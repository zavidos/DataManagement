import sys, requests, bs4, os, time, shelve, shutil, datetime, smtplib, ssl, selenium, pprint, sys, inspect, logging
from pypac import PACSession, get_pac
import pypac


#importing credentials from external file
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import credentials
user = credentials.username
pwd = credentials.password
apikey = credentials.APIkey

#using proxy and auth separately in requests
auth = requests.auth.HTTPProxyAuth(user,pwd)
proxies = {
  "http": "http://proxy.polimi.it:8080",
  "https": "http://proxy.polimi.it:8080"}

#to be used with only proxy specification in requests, credentials are in proxy address
proxies2 = {
  "http": f"http://{user}:{pwd}@proxy.polimi.it:8080",
  "https": f"http://{user}:{pwd}@proxy.polimi.it:8080"}


urlscopus = f"https://api.elsevier.com/content/search/author?query=authlast(weng)%20and%20authfirst(wei)&apiKey={apikey}"
urlpoli='https://verify.proxy.polimi.it'

user_agent = 'Mozilla/5.0'
headers = {'User-Agent': user_agent}

def provaProxy(ind,nome='name not specified'):
    print(f"risultato usando {nome}:")
    try:
        scaricata=requests.get(ind,proxies=proxies,auth=auth,headers=headers)
    except Exception as e:
        if apikey in str(e):
            pos = str(e).find(apikey)
            print("..."+str(e)[pos+len(apikey):])
        else:
            print(str(e)[:len(str(e))//2])
            print(str(e)[len(str(e))//2:])
    print()

provaProxy(urlscopus,'scopus')
provaProxy(urlpoli, 'verifica politecnico')
