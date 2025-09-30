import json
import os
import glob
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError


def encode_key(key: str) -> str:
        return key.replace(".", "d")
    
def decode_key(key: str) -> str:
        return key.replace("d", ".")

def get_db_collection():
    database_name = "etching_db"
    collection_name = "merged_etching_data"

    client = MongoClient("mongodb://localhost:27017/")
    db = client[database_name]
    collection = db[collection_name]
    return collection
    
def access_data(collection, profile_key):   
    doc = collection.find_one({encode_key(key): {"$exists": True}})
    return doc[encode_key(key)]

def export_json_to_mongodb(folder_path, db_name, collection_name, mongo_uri="mongodb://localhost:27017/"):
    """
    Reads all JSON files from a specified folder, merges their data, and exports
    the merged data to a MongoDB collection.

    This function assumes a MongoDB instance is running on localhost.

    Args:
        folder_path (str): The path to the folder containing the JSON files.
        db_name (str): The name of the MongoDB database.
        collection_name (str): The name of the collection to export the data to.
        mongo_uri (str): The MongoDB connection string. Defaults to localhost.
    """
    # Initialize an empty list to store all data from the JSON files.
    db_data = {}

    try:
        # Step 1: Find all JSON files in the specified folder.
        # The glob module finds all files matching a pattern.
        json_files = glob.glob(os.path.join(folder_path, "*.json"))

        if not json_files:
            print(f"No JSON files found in the folder: '{folder_path}'")
            return

        print(f"Found {len(json_files)} JSON file(s). Processing...")
                # Step 3: Connect to MongoDB and insert the data.
        print("Connecting to MongoDB...")
        client = MongoClient(mongo_uri)
        client.admin.command('ping')  # Check if the connection is successful.
        db = client[db_name]
        collection = db[collection_name]

        # Step 2: Read and merge the data from each JSON file.
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    for key in file_data.keys():
                        db_data[encode_key(key)] = file_data[key]
                    collection.insert_one(db_data)
                print(f"Successfully loaded data from '{os.path.basename(file_path)}'")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from file '{os.path.basename(file_path)}': {e}")
            except FileNotFoundError:
                print(f"File not found: '{os.path.basename(file_path)}'")
            except Exception as e:
                print(f"An unexpected error occurred while processing '{os.path.basename(file_path)}': {e}")
    
        print("\nConnection successful. Inserting data...")
        # print(f"Successfully inserted {len(result.inserted_ids)} document(s) into '{collection_name}'.")

    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB. Please ensure a MongoDB server is running on '{mongo_uri}'.")
        print(f"Error details: {e}")
    except PyMongoError as e:
        print(f"A MongoDB error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Close the connection to the MongoDB client.
        if 'client' in locals() and client:
            client.close()
            print("MongoDB connection closed.")

if __name__ == "__main__":
    # --- Configuration ---
    json_folder = os.path.join(os.getcwd(), "data_to_load")
    
    # Set the desired database and collection names.
    database_name = "etching_db"
    collection_name = "merged_etching_data"

    # export_json_to_mongodb(json_folder, database_name, collection_name)
    
    client = MongoClient("mongodb://localhost:27017/")
    db = client[database_name]
    collection = db[collection_name]
    
    key = "2_0.5_3_2_2"
    collection = get_db_collection() 
    print(access_data(collection, key))
