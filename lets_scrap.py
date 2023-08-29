import time
import xlsxwriter
import requests
from bs4 import BeautifulSoup
from time import sleep
import json
import fake_useragent

headers = {'User-Agent': 'Mozilla/5.0 (iPod touch; CPU iPhone 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (HTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1'}

# Функция для получения ссылок на вакансии
def get_links(text):
    user_agent = fake_useragent.UserAgent()
    data = requests.get(url=f'https://hh.ru/search/vacancy?text={text}&area=113&page=1',
                        headers=headers)
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, 'lxml')
    try:
        page_count = int(soup.select('div.pager span a span')[-1].text)
    except:
        return
    for page in range(1, page_count + 1):
        try:
            data = requests.get(url=f'https://hh.ru/search/vacancy?text={text}&area=113&page={page}',
                                headers=headers)
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, 'lxml')
            for a in soup.find_all('a', attrs={'class': 'serp-item__title'}):
                yield f"{a.attrs['href'].split('?')[0]}"
        except Exception as e:
            print(f'{e}')

# Функция для получения данных о вакансии
def get_resume(link):
    user_agent = fake_useragent.UserAgent()
    data = requests.get(url=link, headers=headers)
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, 'lxml')
    try:
        name = soup.find(attrs={'class': 'vacancy-title'}).text
    except:
        name = ''
    try:
        salary = soup.find(attrs={'class': 'bloko-header-section-2 bloko-header-section-2_lite'}).text.replace('\\xa','')
    except:
        salary = ''
    try:
        vacancy_description = soup.find(attrs={'class': 'g-user-content'}).text
    except:
        vacancy_description = ''
    try:
        skills = [skill.text for skill in soup.find(attrs={'class': 'bloko-tag-list'}).find_all(attrs={'class': 'bloko-tag__section_text'})]
    except:
        skills = []
    resume = {'name': name,
              'salary': salary,
              'vacancy_description': vacancy_description,
              'skills': skills,
              'adr': link
              }

    return resume

if __name__ == '__main__':
    data = []
    for a in get_links('python'):
        data.append(get_resume(a))
        time.sleep(1)
        # Сохраняем данные в JSON-файл
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
