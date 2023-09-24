import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import re
import json

HOST = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
headers = Headers(browser='chrome', os='win').generate()

with requests.Session() as s:
    s.headers.update(headers)

    try:
        html = s.get(HOST).text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while executing the request: {e}")
        exit()

    soup = BeautifulSoup(html, features='lxml')

    vacancy_card = soup.find_all(class_='vacancy-serp-item__layout')

    json_list =[]

    for vacancy in vacancy_card:
        try:
            link_tag = vacancy.find('a', class_='serp-item__title')
            link = link_tag['href']
            salary_tag = vacancy.find('span', class_='bloko-header-section-3')
            salary = salary_tag.text if salary_tag else "Salary is not specified"
            company_name_tag = vacancy.find('a', class_='bloko-link bloko-link_kind-tertiary')
            company_name = company_name_tag.text
            city_tag = vacancy.find('div', class_="vacancy-serp-item__info")
            city_tag1 = city_tag.find_all('div', class_="bloko-text")
            city = re.findall(r'(^\w+-?\w+)(,?.+)?', (city_tag1[1].text))[0][0]

            try:
                vacancy_html = s.get(link).text
                vacancy_soup = BeautifulSoup(vacancy_html, features='lxml')
                vacancy_desc_tag = vacancy_soup.find('div', class_ = 'bloko-columns-row')
                vacancy_desc = vacancy_desc_tag.text
            except requests.exceptions.RequestException as e:
                print(f"An error occurred while receiving the job description: {e}")
                continue

            if 'Flask' in vacancy_desc and 'Django' in vacancy_desc:
                vacancy_dic = {'link': link, 'salary': salary, 'company_name': company_name, 'city': city}
                json_list.append(vacancy_dic)
        except AttributeError as e:
            print(f"An error occurred during the analysis HTML: {e}")
            continue

try:
    with open("vacancy.json", "w", encoding="utf-8") as file:
        json.dump(json_list, file, indent=4)
except IOError as e:
    print(f"An error occurred while writing to the file: {e}")

print(json_list)