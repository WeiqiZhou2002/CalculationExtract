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
    def __init__(self, host, port, db, collection):
        self.conn = MongoClient(host=host, port=port)
        self.db = self.conn[db]
        self.collection = self.db[collection]


    def save_one(self, data):
        object_id = self.collection.insert_one(data).inserted_id
        self.conn.close()
        return object_id

    def save_many(self, data):
        object_ids = self.collection.insert_many(data).inserted_ids
        self.conn.close()
        return object_ids

