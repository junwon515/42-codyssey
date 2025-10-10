import csv
import os
import smtplib
from email.message import EmailMessage

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
GOOGLE_SENDER_EMAIL = os.getenv('GOOGLE_SENDER_EMAIL')
GOOGLE_APP_PASSWORD = os.getenv('GOOGLE_APP_PASSWORD')
NAVER_SENDER_EMAIL = os.getenv('NAVER_SENDER_EMAIL')
NAVER_APP_PASSWORD = os.getenv('NAVER_APP_PASSWORD')

SMTP_SERVERS = {
    'gmail': ('smtp.gmail.com', 587),
    'naver': ('smtp.naver.com', 587),
}
RECIPIENT_LIST_CSV = os.path.join(os.path.dirname(__file__), 'mail_target_list.csv')
SMTP_TIMEOUT = 30


def read_recipients_from_csv(file_path):
    recipients = []
    try:
        with open(file_path, encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            if (
                not reader.fieldnames
                or 'name' not in reader.fieldnames
                or 'email' not in reader.fieldnames
            ):
                print("경고: CSV 파일에 'name' 또는 'email' 열이 없습니다.")
                return []
            skipped = 0
            for row in reader:
                name = (row.get('name') or '').strip()
                email = (row.get('email') or '').strip()
                if not name or not email or '@' not in email:
                    skipped += 1
                    continue
                recipients.append({'name': name, 'email': email})
            if skipped:
                print(f'경고: {skipped}개 행을 건너뜀(누락/잘못된 값).')
    except FileNotFoundError:
        print(f"오류: CSV 파일을 찾을 수 없습니다: '{file_path}'")
    except Exception as e:
        print(f'오류: CSV 파일을 읽는 중 문제가 발생했습니다: {e}')
    return recipients


def create_email_message(
    *, sender_email, recipient_email, subject, body, file_path=None
):
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    if '<html' in body.lower() and '</html>' in body.lower():
        msg.set_content('HTML을 지원하지 않는 환경에서는 이 메시지가 표시됩니다.')
        msg.add_alternative(body, subtype='html')
    else:
        msg.set_content(body)

    if file_path:
        try:
            with open(file_path, 'rb') as attachment:
                file_name = os.path.basename(file_path)
                msg.add_attachment(
                    attachment.read(),
                    maintype='application',
                    subtype='octet-stream',
                    filename=file_name,
                )
        except FileNotFoundError:
            print(f"오류: 첨부 파일을 찾을 수 없습니다: '{file_path}'")
            return None
        except Exception as e:
            print(f'오류: 첨부 파일을 처리하는 중 문제가 발생했습니다: {e}')
            return None
    return msg


def send_emails_individually(
    *, smtp_info, sender_email, app_password, recipients, subject, body, file_path=None
):
    server = None
    try:
        server = smtplib.SMTP(smtp_info[0], smtp_info[1], timeout=SMTP_TIMEOUT)
        server.starttls()
        server.login(sender_email, app_password)
        print('SMTP 서버에 성공적으로 로그인했습니다.')

        for recipient in recipients:
            recipient_name = recipient['name']
            recipient_email = recipient['email']
            personalized_body = body.replace('{name}', recipient_name)

            msg = create_email_message(
                sender_email=sender_email,
                recipient_email=recipient_email,
                subject=subject,
                body=personalized_body,
                file_path=file_path,
            )
            if msg is None:
                print(
                    f"오류: '{recipient_email}'님에게 보낼 메시지 생성에 실패하여 건너뜁니다."
                )
                continue

            server.send_message(msg)
            print(
                f"성공: '{recipient_name}'님({recipient_email})에게 이메일을 보냈습니다."
            )

    except smtplib.SMTPAuthenticationError:
        print('인증 오류: 이메일 주소나 앱 비밀번호를 확인하세요.')
        print(
            '네이버/Gmail의 경우, SMTP 사용 설정 및 앱 비밀번호 생성이 필요할 수 있습니다.'
        )
    except smtplib.SMTPConnectError:
        print('SMTP 서버에 연결할 수 없습니다. 주소와 포트를 확인하세요.')
    except Exception as e:
        print(f'이메일 전송 중 오류가 발생했습니다: {e}')
    finally:
        if server:
            server.quit()
            print('SMTP 서버 연결을 종료했습니다.')


def send_email_as_group(
    *,
    smtp_info,
    sender_email,
    app_password,
    to_emails,
    cc_emails=None,
    bcc_emails=None,
    subject,
    body,
    file_path=None,
):
    to_emails = to_emails or []
    cc_emails = cc_emails or []
    bcc_emails = bcc_emails or []

    all_recipients = to_emails + cc_emails + bcc_emails

    msg = create_email_message(
        sender_email=sender_email,
        recipient_email=', '.join(to_emails),
        subject=subject,
        body=body,
        file_path=file_path,
    )
    if msg is None:
        print('오류: 메시지 생성에 실패하여 전송을 중단합니다.')
        return
    if cc_emails:
        msg['Cc'] = ', '.join(cc_emails)

    server = None
    try:
        server = smtplib.SMTP(smtp_info[0], smtp_info[1], timeout=SMTP_TIMEOUT)
        server.starttls()
        server.login(sender_email, app_password)

        server.send_message(msg, from_addr=sender_email, to_addrs=all_recipients)

        print('SMTP 서버에 성공적으로 로그인했으며, 그룹 메일을 발송했습니다.')
        print(f'  - To: {to_emails}')
        print(f'  - CC: {cc_emails}')
        print(f'  - BCC: {len(bcc_emails)} 명')

    except Exception as e:
        print(f'이메일 전송 중 오류가 발생했습니다: {e}')
    finally:
        if server:
            server.quit()
            print('SMTP 서버 연결을 종료했습니다.')


def main():
    smtp_info = None
    for i in range(3, 0, -1):
        mail_service = (
            input("사용할 메일 서비스 ('gmail' 또는 'naver'): ").strip().lower()
        )
        if mail_service in SMTP_SERVERS:
            smtp_info = SMTP_SERVERS[mail_service]
            break
        else:
            print(
                f"오류: 'gmail' 또는 'naver' 중에서 선택해주세요. ({i-1}번 기회 남음)"
            )

    if not smtp_info:
        print('메일 서비스를 선택하지 않아 프로그램을 종료합니다.')
        return

    if smtp_info == SMTP_SERVERS['gmail']:
        sender_email = (GOOGLE_SENDER_EMAIL or input('발신자 Gmail 주소: ')).strip()
        app_password = (GOOGLE_APP_PASSWORD or input('Gmail 앱 비밀번호: ')).strip()
    else:
        sender_email = (NAVER_SENDER_EMAIL or input('발신자 Naver 주소: ')).strip()
        app_password = (NAVER_APP_PASSWORD or input('Naver 앱 비밀번호: ')).strip()

    subject = input('이메일 제목: ').strip()
    html_file_path = input('HTML 본문 파일 경로 (없으면 Enter): ').strip() or None
    if html_file_path:
        try:
            with open(html_file_path, encoding='utf-8') as f:
                body = f.read()
        except FileNotFoundError:
            print(f"오류: HTML 파일을 찾을 수 없습니다: '{html_file_path}'")
            return
        except Exception as e:
            print(f'오류: HTML 파일을 읽는 중 문제가 발생했습니다: {e}')
            return
    else:
        body = input('이메일 본문: ').strip()

    attachment_path = input('첨부 파일 경로 (없으면 Enter): ').strip() or None

    recipients = read_recipients_from_csv(RECIPIENT_LIST_CSV)
    if recipients:
        print(f'총 {len(recipients)}명에게 이메일 발송을 시작합니다.')
        send_emails_individually(
            smtp_info=smtp_info,
            sender_email=sender_email,
            app_password=app_password,
            recipients=recipients,
            subject=subject,
            body=body,
            file_path=attachment_path,
        )

        # send_email_as_group(
        #     smtp_info=smtp_info,
        #     sender_email=sender_email,
        #     app_password=app_password,
        #     to_emails=[],
        #     cc_emails=[],
        #     bcc_emails=[r['email'] for r in recipients],
        #     subject=subject,
        #     body=body,
        #     file_path=attachment_path,
        # )
    else:
        print('보낼 대상이 없거나 CSV 파일을 읽는 데 실패하여 프로그램을 종료합니다.')


if __name__ == '__main__':
    main()
