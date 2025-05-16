from pyheaven import *
from selenium import webdriver
from bs4 import BeautifulSoup
import time

ROOT_PATH = "./data/SEC/"
NOW_YEAR = 2024
NOW_QUARTER = 3

# SEC limits automated access, so we need to use selenium to call a browser to download the file
def download(url, download_directory, sleep_interval=1):
    def is_download_finished(download_directory):
        for filename in ListFiles(download_directory):
            if filename.endswith(".crdownload"):
                return False
        return True
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(sleep_interval)
    while not is_download_finished(download_directory):
        time.sleep(sleep_interval)
    time.sleep(sleep_interval)
    driver.quit()

def save_webpage(url, path, sleep_interval=1):
    if not ExistFile(path):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "safebrowsing.enabled": True
        })
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(sleep_interval)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        time.sleep(sleep_interval)
        driver.quit()

def save_pdf(url, download_directory, sleep_interval=1):
    def is_download_finished(download_directory):
        for filename in ListFiles(download_directory):
            if filename.endswith(".crdownload"):
                return False
        return True
    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True
    })
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(sleep_interval)
    while not is_download_finished(download_directory):
        time.sleep(sleep_interval)
    time.sleep(sleep_interval)
    driver.quit()

def extract_links(html, file_format='pdf'):
    with open(html, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        pdf_links = []
        for link in soup.find_all('a', href=True):
            if link['href'].endswith(f'.{file_format}'):
                pdf_links.append(link['href'])
        return pdf_links

def enumerate_years(start_year=1994, end_year=2024):
    return [year for year in range(start_year, end_year+1)]

def enumerate_quarters(start_year=1994, start_quarter=3, end_year=2024, end_quarter=3):
    return [(year, quarter) for year in range(start_year, end_year+1) for quarter in range(1, 5)
            if (year > start_year or quarter >= start_quarter) and (year < end_year or quarter <= end_quarter)]

def enumerate_months(start_year=1994, start_month=1, end_year=2024, end_month=12):
    return [(year, month) for year in range(start_year, end_year+1) for month in range(1, 13)
            if (year > start_year or month >= start_month) and (year < end_year or month <= end_month)]
