import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
APP_PASSWORD = os.getenv('APP_PASSWORD')

PORT = 587
RECIPIENT_EMAIL = None
EMAIL_SUBJECT = None
EMAIL_BODY = None
ATTACHMENT_PATH = None


def send_gmail(
    *, sender_email, app_password, recipient_email, subject, body, file_path=None
):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if file_path:
        try:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            file_name = os.path.basename(file_path)
            part.add_header('Content-Disposition', 'attachment', filename=file_name)
            msg.attach(part)
        except FileNotFoundError:
            print(f'파일을 찾을 수 없습니다: {file_path}')
            return
        except Exception as e:
            print(f'첨부 파일을 추가하는 중 오류가 발생했습니다: {e}')
            return

    try:
        server = smtplib.SMTP('smtp.gmail.com', PORT)
        server.starttls()
        server.login(sender_email, app_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        print('이메일을 성공적으로 보냈습니다.')
    except smtplib.SMTPAuthenticationError:
        print('인증 오류: 이메일 주소나 앱 비밀번호를 확인하세요.')
    except smtplib.SMTPConnectError:
        print('SMTP 서버에 연결할 수 없습니다.')
    except Exception as e:
        print(f'이메일 전송 중 오류가 발생했습니다: {e}')
    finally:
        if 'server' in locals() and server.sock:
            server.quit()


def main():
    sender_email = SENDER_EMAIL or None
    app_password = APP_PASSWORD or None
    recipient_email = RECIPIENT_EMAIL or None
    email_subject = EMAIL_SUBJECT or None
    email_body = EMAIL_BODY or None
    attachment_path = ATTACHMENT_PATH or None

    if sender_email is None or app_password is None:
        sender_email = input('발신자 이메일: ').strip()
        app_password = input('앱 비밀번호: ').strip()

    if recipient_email is None:
        recipient_email = input('수신자 이메일: ').strip()

    if email_subject is None:
        email_subject = input('이메일 제목: ').strip()

    if email_body is None:
        email_body = input('이메일 본문: ').strip()

    if attachment_path is None:
        attachment_path = input('첨부 파일 경로 (필요 없으면 Enter): ').strip() or None

    send_gmail(
        sender_email=sender_email,
        app_password=app_password,
        recipient_email=recipient_email,
        subject=email_subject,
        body=email_body,
        file_path=attachment_path,
    )


if __name__ == '__main__':
    main()
