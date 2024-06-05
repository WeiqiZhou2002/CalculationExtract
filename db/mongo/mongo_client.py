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
from pymongo import MongoClient


class Mongo:
    def __init__(self, host, port):
        self.client = MongoClient(host=host, port=port)



    def save_one(self, data, db, collection):
        conn = self.client[db][collection]
        object_id = conn.insert_one(data).inserted_id
        return object_id

    def save_many(self, data, db, collection):
        conn = self.client[db][collection]
        object_ids = conn.insert_many(data).inserted_ids
        return object_ids

    def close(self):
        self.client.close()