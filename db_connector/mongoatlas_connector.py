import datetime
import json
import time
from pymongo import MongoClient
from bson import ObjectId


# TODO: requests.post('https://caposconti.herokuapp.com/api/addproductsbot/', json={'records':arg, 'category': '"DEAL_OF_THE_DAY"'})
# TODO : find query if exista insert


class AtlasMongoDb:
    __instance = None
    __atlasmongoinstance = None

    @staticmethod
    def get_initialize(connection_url, db_name, collection_name=""):
        if not AtlasMongoDb.__instance and not AtlasMongoDb.__atlasmongoinstance:
            AtlasMongoDb(connection_url, db_name, collection_name)
        return AtlasMongoDb.__atlasmongoinstance

    def __init__(self, connection_url, db_name, collection_name):
        AtlasMongoDb.__instance = MongoClient(connection_url)[db_name]
        self.connection_url = connection_url
        self.db_name = db_name
        self.collection_name = collection_name
        AtlasMongoDb.__atlasmongoinstance = self

    def __str__(self):
        return "Connected at document  " + self.db_name + "  in collection  " + self.collection_name + "  at url" + self.connection_url

    # @staticmethod
    # def fill_records_formatted_dict(records):
    #     print("Loading records at collection: " + AtlasMongoDb.collection_name)
    #     if AtlasMongoDb.collection_name not in AtlasMongoDb.list_database_names():
    #         AtlasMongoDb.create_collection(AtlasMongoDb.collection_name)
    #     AtlasMongoDb[AtlasMongoDb.collection_name].insert_many(records)

    def fill_records_formatted_dict(self, records):
        print("Loading records at collection: " + AtlasMongoDb.__atlasmongoinstance.collection_name)
        if AtlasMongoDb.__atlasmongoinstance.collection_name not in self.__instance.list_collection_names():
            self.__instance.create_collection(AtlasMongoDb.__atlasmongoinstance.collection_name)
        for x in records:
            entered = False
            for itm in self.__instance[AtlasMongoDb.__atlasmongoinstance.collection_name].find({"Title": x["Title"]}):
                document = self.__instance[AtlasMongoDb.__atlasmongoinstance.collection_name].update_one(
                    {'_id': ObjectId(itm.get('_id'))}, {"$set": x}, upsert=True)
                entered = True
            if not entered:
                document = self.__instance[AtlasMongoDb.__atlasmongoinstance.collection_name].insert_one(x)
        return document.acknowledged

    def delete_old_record(self):
        for doc in self.__instance[AtlasMongoDb.__atlasmongoinstance.collection_name].find(
                {"TimeDeal": {"$lt": datetime.datetime.now()}}):
            self.__instance[AtlasMongoDb.__atlasmongoinstance.collection_name].delete_many(doc)
        print("Old Record Deleted")


