import sys, requests, bs4, os, time, shelve, shutil, datetime, json, selenium,pprint,math
import logging
import pandas as pd
from threading import Thread
from pymongo import MongoClient
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.INFO)

client = MongoClient('localhost', 27017)
db = client['DM']
noomo=db.noomo


cursors = noomo.find({})
for art in cursors:
    for i in art["noOmonimi"]:
        print(i["Nome"], i['Cognome'])
        print('https://dblp.org/search/author?q='+i["Nome"]+'+'+i['Cognome'])
