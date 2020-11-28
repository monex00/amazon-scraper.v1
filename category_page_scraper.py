import datetime
import time
from amazon_product import amazon_product
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from db_connector import mongoatlas_connector

driver = webdriver.Firefox(
    executable_path="/home/gio/PycharmProjects/pythonProject/Scraper/geckodriver/geckodriver")
URL_MONGO_ATALS = "mongodb+srv://singh:K7nhMHqTfUSt7IDN@cluster0.bgnl4.mongodb.net/sconti?retryWrites=true&w=majority"
DOCUMENT_NAME = "sconti"
COLLECTION_NAME = "amazon_deals_pi"


def get_url(url, page):
    template = url.replace('{}', str(page))
    print(" Scraping: " + template)
    return template


def extract_singleCellItem(item, category):
    title = item.find('div', {'class': 'dealTile'})
    try:
        atag = title.find('a', 'a-link-normal')
        url = atag.get('href')
        if len(url) > 2048:
            raise AttributeError
    except AttributeError:
        print("URL MAGGIORE DI 2048")
        raise AttributeError
    try:
        time = title.find('span', {'role': 'timer'}).text
        current_date_and_time = datetime.datetime.now()
        hours_added = datetime.timedelta(hours=get_sec(time))
        time = current_date_and_time + hours_added
    except AttributeError:
        time = datetime.datetime.now()

    try:
        record = get_product_data(url, time, category)
    except AttributeError:
        print("Error LOADING ITEM")
        raise AttributeError
    return record


def main(urlInit, category):
    for page in range(1, 20):
        records = []
        mongodb = mongoatlas_connector.AtlasMongoDb.get_initialize(URL_MONGO_ATALS, DOCUMENT_NAME, COLLECTION_NAME)
        url = get_url(urlInit, page)

        driver.get(url)
        driver.maximize_window()
        time.sleep(0.75)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = soup.find_all('div', {'class': 'singleCell'})
        print(len(results))
        if len(results) == 0:
            results = soup.findAll('div', {'data-component-type': 's-search-result'})
            print(results)
        for item in results:
            record_status = True
            try:
                record = extract_singleCellItem(item, category)
            except AttributeError:
                record_status = False
            if (record_status):
                print(record)
                records.append(record)
        if len(records) != 0:
            mongodb.fill_records_formatted_dict(records)
        else:
            print("0 ELEMENT FOUND")
        time.sleep(3)
    return records


def get_product_data(specificUrl, date, category):
    driver.get(specificUrl)
    driver.maximize_window()
    time.sleep(0.5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    prodct = amazon_product.AmazonProduct(soup, specificUrl, date, category)
    try:
        product = prodct.initialize()
    except AttributeError:
        print("Error during Initialization")
        raise AttributeError
    return product


def runScraping(url_to_scrape, category):
    records = main(url_to_scrape, category)
    return records


def get_sec(time_str):
    """Get Seconds from time."""
    if str(time_str).count(":") == 2:
        h, m, s = time_str.split(':')
    else:
        h, m = time_str.split(':')
        s = "00"
    return int(h) + int(m) / 60 + int(s) / 60 / 60
