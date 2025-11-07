from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json

load_dotenv('C:\\Users\\vknan\\Desktop\\Python_Projects\\Langchain-SQL-Agent\\.env')

client = MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
# If the database doesn't exist, MongoDB creates it upon the first write operation.
db = client[os.getenv("MONGO_DB_NAME")]
collection = db[os.getenv("MONGO_COLLECTION_NAME")]

def find_documents(query: dict):
    try:
        # --- CRITICAL FIX START ---
        if isinstance(query, str):
            try:
                # Safely parse the string representation of the dictionary
                query_dict = json.loads(query)
            except json.JSONDecodeError as e:
                return f"Error: The query string could not be parsed into a dictionary. Received: {query}"
        elif isinstance(query, dict):
            query_dict = query
        else:
            # Should not happen based on the error, but good for robustness
            return f"Error: Unexpected query type received: {type(query)}"
        # --- CRITICAL FIX END ---
        print(f"incoming query:{query_dict}")
        return list(collection.find(query_dict))
    except Exception as e:
        return f"Error: {str(e)}"

def insert_document(document: dict):
    collection.insert_one(document)

def update_document(query: dict, update_values: dict):
    collection.update_one(query, {'$set': update_values})

def delete_document(query: dict):
    collection.delete_one(query)

def count_documents(query: dict):
    return collection.count_documents(query)

def close_connection():
    client.close()