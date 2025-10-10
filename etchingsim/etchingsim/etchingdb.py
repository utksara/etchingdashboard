from pymongo import MongoClient
import re

def encode_key(key: str) -> str:
        return key.replace(".", "d")
    
def decode_key(key: str) -> str:
        return key.replace("d", ".")

def extract_params(key: str):
        number_pattern = r'\d+(?:\.\d+)?'
        numbers = re.findall(number_pattern, key)
        float_numbers = [float(n) for n in numbers]
        return float_numbers

def get_db_collection():
    database_name = "etching_db"
    collection_name = "merged_etching_data"

    client = MongoClient("mongodb://localhost:27017/")
    db = client[database_name]
    collection = db[collection_name]
    return collection

def get_all_keys(collection):
        pipeline = [
                {"$project": {"keys": {"$objectToArray": "$$ROOT"}}},
                {"$unwind": "$keys"},
                {"$group": {"_id": None, "allKeys": {"$addToSet": "$keys.k"}}}
        ]
        all_keys = list(collection.aggregate(pipeline))
        return all_keys[0]["allKeys"]
    
def get_data(collection, profile_key):  
    doc = collection.find_one({encode_key(profile_key): {"$exists": True}})
    return doc[encode_key(profile_key)]