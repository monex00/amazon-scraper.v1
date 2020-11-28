from bs4 import BeautifulSoup
from amazon_product.product_page_constant import *

DOLLAR_CHAR = '€'
# TODO:
#  Data di temine offerta, è prime ? prodotti kindle e il prezzo che prende dai libri
#
class AmazonProduct(object):

    def initialize(self):
        try:
            self._product["Price"] = self.scrape_price()
            self._product["DealPrice"] = self.scrape_dealprice()
            self._product["OffertValue"] = self.scrape_dealoffertvalue()
            self._product["Title"] = self.scrape_titleproduct()
            self._product["Image"] = self.scrape_imageproduct()
            self._product["Rating"] = self.scrape_ratingproduct()
            self._product["NumberOfVote"] = self.scrape_numberofvote()
            # self._product["Asin"] = self.scrape_asin()
            self._product["MerchantInfo"] = self.scrape_merchant_info()
            self._product["PercentageDeals"] = self.set_percentage_deals()
        except AttributeError:
            raise AttributeError
        return self._product

    def __init__(self, soup: BeautifulSoup, specific_url, date, category):
        """as initialized load the data immediately"""
        super(AmazonProduct, self).__init__()
        print("Product url : " + specific_url)
        self._product = {
            "Title": [],
            "Image": [],
            "DealPrice": [],
            "Price": [],
            "OffertValue": [],
            "Rating": [],
            "Url": [],
            "NumberOfVote": [],
            "Asin": [],
            "MerchantInfo": [],
            "TimeDeal": [],
            "Category": [],
            "PercentageDeals": [],
        }
        soup_int = soup
        self.productPage = soup_int
        self._product["Url"] = specific_url
        self._product["TimeDeal"] = date
        self._product["Category"] = category
        #il problema risiede nell'url che viene dato TODO: vedere asin ---> mercoledì fare aggiustare click con selenium, e vedere asin con problema legato al prices
        self._product["Asin"] = self._find_asin(specific_url)

    def scrape_price(self):
        found = False
        sale_price_box = self.productPage
        # try:
        #     sale_price_box = self.productPage.find("div", {'id': PRICE_BOX_ID})
        # except AttributeError:
        #     print("Error loading SalePrice value")
        #     raise AttributeError
        if DOLLAR_CHAR in str(sale_price_box.find('span', {'id': SALE_PRICE_ID_OUR}).text):
            found = True
            price = sale_price_box.find('span', {'id': SALE_PRICE_ID_OUR}).text
        if DOLLAR_CHAR in str(sale_price_box.find('span', {'id': SALE_PRICE_ID_GENERAL}).text):
            found = True
            price = sale_price_box.find('span', {'id': SALE_PRICE_ID_GENERAL}).text
        if DOLLAR_CHAR in str(sale_price_box.find('span', {'class': SALE_PRICE_CLASS_GENERAL}).text):
            found = True
            price = sale_price_box.find('span', {'class': SALE_PRICE_CLASS_GENERAL}).text

        if not found:
            print("Error during SALE PRICE scraping")
            print(sale_price_box.find('span', {'class': SALE_PRICE_CLASS_GENERAL}).text)
            raise AttributeError
        return price

    def scrape_dealprice(self):
        try:
            print("deal price:  "+self.productPage.find('span', {'id': DEAL_PRICE_SPAN}).text)
            deal_price = self.productPage.find('span', {'id': DEAL_PRICE_SPAN}).text
            deal_price = deal_price.strip()
            if '.' in deal_price:
                deal_price = deal_price.remove('.')
            deal_price = deal_price.replace('€', '')
            deal_price = deal_price.replace(',', '.')
            return float(deal_price)
        except AttributeError:
            print("Error loading dealPrice value")
            deal_price = "Deal price not found"
            return deal_price

    def scrape_dealoffertvalue(self):
        try:
            offert_box = self.productPage.find('tr', {'id': DEAL_OFFERT_TR_ID})
            offert_value = offert_box.find('td', DEAL_OFFERT_TD_CLASS).text
        except AttributeError:
            print("Error during DEAL OFFERT VALUE scraping")
            offert_value = 'NOT FOUND'
        return offert_value

    def scrape_titleproduct(self):
        try:
            title = self.productPage.find('span', TITLE_DIRECT_SPAN).text
        except AttributeError:
            print("Error loading title value")
            raise AttributeError
        return title.lower()

    def scrape_imageproduct(self):
        try:
            image_container = self.productPage.find('div', IMAGE_BOX_DIV)
            image_finded = image_container.find('img')
            image_product = image_finded['src']
            if len(image_product) > 2048:
                print("Image product len > 2048")
                raise AttributeError
        except AttributeError:
            print("Error loading Image value")
            raise AttributeError
        return image_product

    def scrape_ratingproduct(self):
        try:
            rating = self.productPage.find('div', {'id': RATING_DIV_ID})
            rating = rating.find('span', RATING_STARS_SPAN).text
        except AttributeError:
            print("Error loading rating")
            rating = "NOT FOUND"
        return rating

    def scrape_numberofvote(self):
        try:
            number_of_vote = self.productPage.find('span', {'id': NUMBEROFVOTE_SPAN_ID}).text
        except AttributeError:
            print("Error loading numberOfVote")
            number_of_vote = "NOTE FOUND"
        return number_of_vote

    def _find_asin(self, url):
        if '/dp/' in url:
            return url.split('/dp/')[1].split('/')[0]
        else:
            print("ASIN NOT FOUND")
    # def scrape_asin(self):
    #     try:
    #         asinbox = self.productPage.find('div', {'id': ASIN_BOX_DIV_ID})
    #         if asinbox is None:
    #             print("Error loading asinbox is NONE")
    #             raise AttributeError
    #         asin = asinbox['data-asin']
    #     except AttributeError:
    #         print("Error during ASIN scraping")
    #         raise AttributeError
    #     return asin

    def scrape_merchant_info(self):
        """Scrape the information of the seller and prepare the string for discord"""
        try:
            mechant_info = self.productPage.find('div', {'id': MERCHANTINFO_DIV_ID})
            seller = mechant_info.find('a', {'id': SELLER_A_ID}).text
            spedition_handler = mechant_info.find('a', {'id': SPEDITIONHANDLER_A_ID}).text
            seller_url = mechant_info.find('a', {'id': SELLER_A_ID})['href']
            string_to_eliminate_first = '/gp/help/seller/at-a-glance.html/ref=dp_merchant_link?ie=UTF8&seller='
            string_to_eliminate_second = '&isAmazonFulfilled=1'
            seller_url = seller_url.replace(string_to_eliminate_first, "")
            seller_url = seller_url.replace(string_to_eliminate_second, "")
            seller_url = 'https://www.amazon.it/sp?_encoding=UTF8&asin=&isAmazonFulfilled=1&isCBA=&marketplaceID=APJ6JRA9NG5V4&orderID=&protocol=current&seller=' + seller_url + '&sshmPath='
            mechant_info_message = 'Venduto da ' + '[' + seller + ']' + '(' + seller_url + ')' + ' e ' + spedition_handler
        except AttributeError:
            print("ErrorLoadingInfo")
            if ('Venduto e spedito da Amazon' in mechant_info.text):
                mechant_info_message = 'Venduto e spedito da Amazon'
            else:
                mechant_info_message = mechant_info.text
        return mechant_info_message

    def set_percentage_deals(self):
        if 'NOT FOUND' not in self._product["OffertValue"]:
            percentage = self._product["OffertValue"]
            percentage.remove('\n')
            percentage = percentage.split(' ')
            print(percentage)
            percentage = percentage[2]
            percentage = percentage.replace('()')
            percentage = percentage.replace('%')
            print(percentage)
            return percentage
        else:
            return "NOT FOUND"
