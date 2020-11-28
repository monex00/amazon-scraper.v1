from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db_connector import mongoatlas_connector
from amazon_product import amazon_product
import time
import datetime

# TODO: restituire la lista di categorie oppure caricarla sul db per un facile accesso!
# TODO: sistemare i prodotti non caricati
_DRIVER = webdriver.Firefox(executable_path="/home/gio/PycharmProjects/pythonProject/Scraper/geckodriver/geckodriver")
URL_MONGO_ATALS = "mongodb+srv://singh:K7nhMHqTfUSt7IDN@cluster0.bgnl4.mongodb.net/sconti?retryWrites=true&w=majority"
DOCUMENT_NAME = "sconti"
COLLECTION_NAME = "amazon_deals_pi"


class AmazonScraper:
    def __init__(self, url):
        self.current_url = url
        self.mongodb = mongoatlas_connector.AtlasMongoDb.get_initialize(URL_MONGO_ATALS, DOCUMENT_NAME, COLLECTION_NAME)
        _DRIVER.get(self.current_url)
        _DRIVER.maximize_window()
        try:
            # element = WebDriverWait(_DRIVER, 10).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, "tallCellView"))
            # )
            _DRIVER.implicitly_wait(30)
        finally:
            category_list = lambda: _DRIVER.find_elements_by_class_name("a-checkbox-label")
            deselect_category = lambda: _DRIVER.find_element_by_xpath(
                "//span[@class='a-declarative'][1]/div[@class='a-row a-spacing-mini']/a[@class='a-link-normal']")
            num_categories = len(category_list())
            print("Numero di categorie:" + str(num_categories))
            for i in range(0, num_categories, 1):
                if category_list()[i].text is not None:
                    category = category_list()[i].text
                    print(str(i) + ")" + "Categoria: " + category)
                    ActionChains(_DRIVER).move_to_element(category_list()[i]).click().perform()
                    # scrapa la categoria con tutte le pagine TODO: logica swap pagine
                    # come stoppare se non ci sono più pagine ? --> se trovo 0 elementi nella pagina .---> quitta
                    self.scrape_products_page(category)
                    time.sleep(2)
                    deselect_category().click()
            _DRIVER.quit()

    def scrape_products_page(self, category):
        records = []
        try:
            element = WebDriverWait(_DRIVER, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tallCellView")))
        finally:
            soup = BeautifulSoup(_DRIVER.page_source, 'html.parser')
            results = soup.find_all('div', {'class': 'singleCell'})
            print(_DRIVER.current_url)
            if len(results) == 0:
                results = soup.findAll('div', {'data-component-type': 's-search-result'})
                print(results)
            for item in results:
                record_status = True
                try:
                    record = self.extract_singleCellItem(item, category)
                except AttributeError:
                    record_status = False
                if (record_status):
                    print(record)
                    records.append(record)
            if len(records) != 0:
                self.mongodb.fill_records_formatted_dict(records)
            else:
                print("0 ELEMENT FOUND")
            time.sleep(3)

    def extract_singleCellItem(self, item, category):
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
            hours_added = datetime.timedelta(hours=self.get_sec(time))
            time = current_date_and_time + hours_added
        except AttributeError:
            time = datetime.datetime.now()

        try:
            record = self.get_product_data(url, time, category)
        except AttributeError:
            print("Error LOADING ITEM")
            raise AttributeError
        return record

    def get_sec(self, time_str):
        """Get Seconds from time."""
        if str(time_str).count(":") == 2:
            h, m, s = time_str.split(':')
        else:
            h, m = time_str.split(':')
            s = "00"
        return int(h) + int(m) / 60 + int(s) / 60 / 60

    def get_product_data(self, specificUrl, date, category):
        _DRIVER.get(specificUrl)
        _DRIVER.maximize_window()
        time.sleep(0.5)
        soup = BeautifulSoup(_DRIVER.page_source, 'html.parser')
        prodct = amazon_product.AmazonProduct(soup, specificUrl, date, category)
        try:
            product = prodct.initialize()
        except AttributeError:
            print("Error during Initialization")
            raise AttributeError
        return product

if __name__ == '__main__':
    AmazonScraper("https://www.amazon.it/blackfriday?ref_=nav_cs_td_bf_dt_cr")
