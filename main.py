import time
import category_page_scraper
from db_connector import mongoatlas_connector

# IT SCRAPE ITALIAN AMAZON SITE TODO: requests.post('https://caposconti.herokuapp.com/api/addproductsbot/', testare merchant info e finire con categorie ecc,,
#  json={'records':arg, 'category': '"DEAL_OF_THE_DAY"'})
URL_TO_SCRAPE = {
    # "daily_deals": "https://www.amazon.it/events/blackfriday/{}/ref=gbps_ftr___page_{}?gb_f_GB-SUPPLE=enforcedCategories:425916031,dealTypes:DEAL_OF_THE_DAY%252CLIGHTNING_DEAL%252CBEST_DEAL,page:{},sortOrder:BY_SCORE,dealsPerPage:50&gb_ttl_GB-SUPPLE=Offerte%2520in%2520Informatica%2520e%2520accessori&ie=UTF8",
    "computers_accessories": "https://www.amazon.it/blackfriday/{}/ref=gbps_ftr___page_{}?gb_f_GB-SUPPLE=enforcedCategories:425916031,dealTypes:DEAL_OF_THE_DAY%252CLIGHTNING_DEAL%252CBEST_DEAL,page:{},sortOrder:BY_SCORE,dealsPerPage:60&gb_ttl_GB-SUPPLE=Offerte%2520in%2520Informatica%2520e%2520accessori&ie=UTF8",
    "electronics": "https://www.amazon.it/blackfriday/{}/ref=gbps_ftr___wht_41260903?gb_f_GB-SUPPLE=dealTypes:DEAL_OF_THE_DAY%252CLIGHTNING_DEAL%252CBEST_DEAL,sortOrder:BY_SCORE,enforcedCategories:412609031&gb_ttl_GB-SUPPLE=Offerte%2520in%2520Informatica%2520e%2520accessori&ie=UTF8",
    "headphones": "https://www.amazon.it/blackfriday/{}/ref=gbps_fcr___wht_41260903?gb_f_GB-SUPPLE=dealTypes:DEAL_OF_THE_DAY%252CLIGHTNING_DEAL%252CBEST_DEAL,sortOrder:BY_SCORE,enforcedCategories:473365031&gb_ttl_GB-SUPPLE=Offerte%2520in%2520Informatica%2520e%2520accessori&ie=UTF8",
}
URL_MONGO_ATALS = "mongodb+srv://singh:K7nhMHqTfUSt7IDN@cluster0.bgnl4.mongodb.net/sconti?retryWrites=true&w=majority"
DOCUMENT_NAME = "sconti"
COLLECTION_NAME = "amazon_deals_pi"


def main():
    while (True):
        # delete_old_record()
        for category in URL_TO_SCRAPE.keys():
            records = category_page_scraper.runScraping(URL_TO_SCRAPE.get(category), category)
            isScraping = lambda: records is None
            while isScraping():
                records = category_page_scraper.runScraping(URL_TO_SCRAPE.get(category), category)
        time.sleep(60 * 60)


def delete_old_record():
    mongodb = mongoatlas_connector.AtlasMongoDb.get_initialize(URL_MONGO_ATALS, DOCUMENT_NAME, COLLECTION_NAME)
    mongodb.delete_old_record()


if __name__ == '__main__':
    main()
