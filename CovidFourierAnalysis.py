# Analysis of the frequencies present in the Covid-19 curve

import requests
import re
from bs4 import BeautifulSoup
import json
import js2xml


def get_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text)
    return soup


def get_links(url):
    soup = get_page(url)
    links = soup.find_all('a', class_="mt_a")
    country_links = [a.get('href') for a in links]
    return country_links


# Get data from Worldometers.info???
def get_covid_data():
    url = "https://www.worldometers.info/coronavirus/"
    all_country_links = get_links(url)
    dict_info = get_info(url + all_country_links[0])
    get_line_graph(url + all_country_links[0])
    return dict_info


def get_info(country_url):
    country_soup = get_page(country_url)
    info = country_soup.find_all('div', class_="maincounter-number")
    total_number = info[0].text.strip()
    deaths = info[1].text.strip()
    recovered = info[2].text.strip()
    name = country_soup.find_all('h1')
    country = name[0].text.strip()

    dict_info = {
        "Country / District": country,
        "Number of total confirmed cases": total_number,
        "Number of deaths": deaths,
        "Number of recovered": recovered
    }

    return dict_info


def get_line_graph(country_url):
    country_soup = get_page(country_url)
    script = country_soup.findAll("script")
    # print(len(script))
    # print(script[23])      # 23 - Total Cases; 24 - Daily Cases; 25 - Active Cases
    print(script[24])
    out = json.loads(script)
    print(out)
    # parsed = js2xml.parse(script[24])
    # print(js2xml.pretty_print(parsed))
    # chart = country_soup.find_all('g', class_="highcharts-series-group")
    # print(chart)


if __name__ == "__main__":
    us_data = get_covid_data()
    # print(us_data)

    # Fourier transform
    # Plot


