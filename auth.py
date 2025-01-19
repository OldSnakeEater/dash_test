from pymongo import MongoClient
from dotenv import load_dotenv

import os

load_dotenv()

class Auth:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def check_credentials(self):
        client = MongoClient(os.getenv("mongo_url"))
        db = client["dash_test"]
        collection = db.get_collection("user")
        result = collection.find_one({"user": self.login, "password": self.password})
        if result:
            return True
        else:
            return False