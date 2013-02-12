'''
Created on Jun 11, 2012

@author: Adrian Costia
'''

from pyrts.datastore.store import DataStore
from pyrts.datastore.models import * #@UnusedWildImport
import os
import json

db = DataStore("controller").connect()
json_file = open("tokens.json","r")
data = json.load(json_file)

for itm in data["tokens"]:
    dbToken = AccessToken(
                        token = itm['token'],
                        address='10.100.9.8',
                        expire_at=1365949560,
                       )
    dbToken.save()