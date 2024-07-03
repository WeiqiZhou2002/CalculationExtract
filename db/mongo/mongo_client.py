#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project    : CalculationExtract 
@File       : mongo_client.py
@IDE        : PyCharm 
@Author     : zychen@cnic.cn
@Date       : 2024/5/30 17:18 
@Description: 
"""
from gridfs import GridFS
from pymongo import MongoClient
import bson


class Mongo:
    def __init__(self, host, port):
        self.client = MongoClient(host=host, port=port)

    def save_one(self, data, db, collection):
        try:
            conn = self.client[db][collection]
            object_id = conn.insert_one(data).inserted_id
            return object_id
        except Exception as e:
            print(f"An error occurred: {e}")

    def save_many(self, data, db, collection):
        conn = self.client[db][collection]
        object_ids = conn.insert_many(data).inserted_ids
        return object_ids

    def save_large(self, data, db):
        fs = GridFS(self.client[db])
        bson_data = bson.BSON.encode(data)
        object_id = fs.put(bson_data)
        return object_id

    def close(self):
        self.client.close()
