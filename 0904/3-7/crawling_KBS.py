import getpass

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

NAVER_ID = ''
NAVER_PW = ''
DRIVER_PATH = ''

KBS_NEWS_URL = 'https://news.kbs.co.kr/news/pc/main/main.html'
NAVER_WEATHER_URL = 'https://search.naver.com/search.naver?query=날씨'
NAVER_LOGIN_URL = 'https://nid.naver.com/nidlogin.login'
NAVER_MAIL_URL = 'https://mail.naver.com'
REQUEST_TIMEOUT = 10

DEFAULT_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

# 세션 재사용으로 효율 향상
SESSION = requests.Session()
SESSION.headers.update(DEFAULT_HEADERS)


def get_kbs_headlines():
    news_list = []
    try:
        response = SESSION.get(
            KBS_NEWS_URL, allow_redirects=True, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        headline_elements = soup.select('.main-head-line .title') or soup.select(
            '.headline, .headline a, .title'
        )

        news_list = [
            elem.get_text(strip=True)
            for elem in headline_elements
            if elem and elem.get_text(strip=True)
        ]

        print(f'✅ 총 {len(news_list)}개의 KBS 뉴스 헤드라인을 수집했습니다.')

    except requests.RequestException as e:
        print(f'❌ KBS 뉴스 헤드라인을 가져오는 중 오류 발생: {e}')
    except Exception as e:
        print(f'❌ KBS 뉴스 헤드라인을 가져오는 중 알 수 없는 오류 발생: {e}')

    return news_list


def get_naver_weather():
    weather_list = []
    try:
        response = SESSION.get(NAVER_WEATHER_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        weather_info = soup.select_one('.weather_info')

        if not weather_info:
            print(
                '❌ 네이버 날씨 정보 섹션을 찾을 수 없습니다. 페이지 구조가 변경되었을 수 있습니다.'
            )
            return weather_list

        temp = weather_info.select_one('.temperature_text')
        if temp:
            weather_list.append(temp.get_text(strip=True, separator=' '))

        summary = weather_info.select_one('.summary')
        if summary:
            weather_list.append(summary.get_text(strip=True, separator=' '))

        summary_list_container = weather_info.select_one('.summary_list')
        if summary_list_container:
            for item in summary_list_container.find_all(recursive=False):
                text = item.get_text(strip=True, separator=' ')
                if text:
                    weather_list.append(text)

        print('✅ 네이버 날씨 정보를 성공적으로 수집했습니다.')

    except requests.RequestException as e:
        print(f'❌ 네이버 날씨 정보를 가져오는 중 오류 발생: {e}')
    except Exception as e:
        print(f'❌ 네이버 날씨 정보를 가져오는 중 알 수 없는 오류 발생: {e}')

    return weather_list


def setup_driver(use_manager=True, driver_path=None):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--log-level=3')
    options.add_experimental_option(
        'excludeSwitches', ['enable-logging', 'enable-automation']
    )
    options.add_argument(f"user-agent={DEFAULT_HEADERS['User-Agent']}")

    try:
        if use_manager:
            print('✅ webdriver-manager를 사용하여 드라이버를 설정합니다.')
            service = Service(ChromeDriverManager().install())
        else:
            if not driver_path:
                raise ValueError(
                    '❌ 수동 설정을 위해 드라이버 경로(driver_path)가 필요합니다.'
                )
            print(f'✅ 수동 경로({driver_path})를 사용하여 드라이버를 설정합니다.')
            service = Service(executable_path=driver_path)

        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f'❌ 드라이버 설정 중 오류 발생: {e}')
        return None


def login_naver(driver, user_id, user_pw):
    driver.get(NAVER_LOGIN_URL)

    try:
        wait = WebDriverWait(driver, 10)
        id_el = wait.until(EC.presence_of_element_located((By.ID, 'id')))
        pw_el = wait.until(EC.presence_of_element_located((By.ID, 'pw')))

        driver.execute_script('arguments[0].value = arguments[1];', id_el, user_id)
        driver.execute_script('arguments[0].value = arguments[1];', pw_el, user_pw)

        try:
            driver.find_element(By.ID, 'log.login').click()
        except Exception:
            try:
                driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            except Exception:
                print('⚠️ 로그인 버튼을 찾지 못했습니다.')
                return False

        print('\n--- ⚠️ 사용자 확인 필요 ---')
        input(
            '2단계 인증(2FA)이 설정된 경우, 브라우저에서 인증을 완료한 후 터미널에서 Enter를 누르세요.\n'
            '2단계 인증이 없다면 바로 Enter를 누르세요...'
        )
        print('--------------------------\n')

        if 'nid.naver.com' in driver.current_url:
            print(
                '⚠️ 로그인 페이지에 머물러 있습니다. 아이디/비밀번호를 확인하거나 CAPTCHA를 해결해주세요.'
            )
            return False

        print('✅ 로그인이 성공적으로 처리되었습니다.')
        return True

    except TimeoutException:
        print('❌ 로그인 필드 로딩 시간 초과')
        return False
    except Exception as e:
        print(f'❌ 로그인 중 오류 발생: {e}')
        return False


def crawl_email_titles(driver):
    driver.get(NAVER_MAIL_URL)

    titles = []
    try:
        wait = WebDriverWait(driver, 15)
        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.mail_title .text'))
        )
        elements = driver.find_elements(By.CSS_SELECTOR, '.mail_title .text')
        for el in elements:
            text = el.text.strip()
            if text:
                titles.append(text)

        print(f'✅ 총 {len(titles)}개의 메일 제목을 수집했습니다.')

    except TimeoutException:
        print(
            '❌ 메일 목록을 시간 내에 불러오지 못했습니다. 로그인 실패 또는 페이지 구조 변경 가능성이 있습니다.'
        )
    except Exception as e:
        print(f'❌ 메일 제목 수집 중 오류 발생: {e}')

    return titles


def main() -> None:
    headlines = get_kbs_headlines()
    if headlines:
        print('\n--- KBS 뉴스 헤드라인 ---')
        for idx, headline in enumerate(headlines, 1):
            print(f'{idx}. {headline}')
        print('-----------------------\n')

    weather_info = get_naver_weather()
    if weather_info:
        print('\n--- 네이버 날씨 정보 ---')
        for info in weather_info:
            print(info)
        print('-----------------------\n')

    driver = (
        setup_driver(use_manager=True)
        if not DRIVER_PATH
        else setup_driver(use_manager=False, driver_path=DRIVER_PATH)
    )
    if not driver:
        return

    naver_id = NAVER_ID or None
    naver_pw = NAVER_PW or None
    if not naver_id or not naver_pw:
        print('⚠️ 네이버 아이디/비밀번호가 설정되지 않았습니다. 입력을 요청합니다.')
        naver_id = naver_id or input('네이버 아이디: ')
        naver_pw = naver_pw or getpass.getpass('네이버 비밀번호: ')

    try:
        if login_naver(driver, naver_id, naver_pw):
            titles = crawl_email_titles(driver)
            if titles:
                print('\n--- 네이버 메일 제목 ---')
                for i, title in enumerate(titles, 1):
                    print(f'{i}. {title}')
                print('-----------------------\n')
    finally:
        print('🎉 모든 작업이 완료되었습니다. 브라우저를 종료합니다.')
        driver.quit()


if __name__ == '__main__':
    main()
