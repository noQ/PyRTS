'''
Created on Jun 11, 2012

@author: Adrian Costia
'''

from pyrts.datastore.store import DataStore
from pyrts.datastore.models import * #@UnusedWildImport
import os
import json

db = DataStore("controller").connect()
json_file = open("white_list.json","r")
data = json.load(json_file)

for itm in data["whitelist"]:
    dbToken = AccessWhiteList(address = itm['address']).save()
