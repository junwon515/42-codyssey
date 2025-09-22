# crawling_KBS.py
import requests
from bs4 import BeautifulSoup


def get_kbs_headlines():
    url = 'https://news.kbs.co.kr/news/pc/main/main.html'

    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        headline_elements = soup.select('.main-head-line .title')

        news_list = [
            elem.get_text(strip=True)
            for elem in headline_elements
            if elem and elem.get_text(strip=True)
        ]

        if not news_list:
            news_list.append('뉴스 정보를 가져오지 못했습니다.')

        return news_list
    except requests.RequestException as e:
        print(f'Error fetching KBS news: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')


def get_naver_weather():
    url = 'https://search.naver.com/search.naver?query=날씨'

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        weather_info = soup.select_one('.weather_info')

        weather_list = []
        if weather_info:
            temperature_text = weather_info.select_one('.temperature_text')
            summary = weather_info.select_one('.summary')
            summary_list = weather_info.select_one('.summary_list').find_all(
                recursive=False
            )

            if temperature_text:
                weather_list.append(
                    temperature_text.get_text(strip=True, separator=' ')
                )
            if summary:
                weather_list.append(summary.get_text(strip=True, separator=' '))
            for summary_item in summary_list:
                weather_list.append(summary_item.get_text(strip=True, separator=' '))

        if not weather_list:
            weather_list.append('날씨 정보를 가져오지 못했습니다.')

        return weather_list
    except requests.RequestException as e:
        print(f'Error fetching weather information: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')


def main():
    print('=== KBS 뉴스 헤드라인 ===')
    headlines = get_kbs_headlines()
    for idx, headline in enumerate(headlines, 1):
        print(f'{idx}. {headline}')

    print('\n=== 네이버 날씨 정보 ===')
    weather_info = get_naver_weather()
    for info in weather_info:
        print(info)


if __name__ == '__main__':
    main()
