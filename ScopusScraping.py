import sys, requests, bs4, os, time, shelve, shutil, datetime, smtplib, ssl, selenium, pprint, sys, inspect, logging

from pypac import PACSession
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
proxystring=f"http://{user}:{pwd}@proxy.polimi.it:8080"
proxies2 = {
  "http": proxystring,
  "https": proxystring}

urlscopus = f"https://api.elsevier.com/content/search/author?query=authlast(weng)%20and%20authfirst(wei)&apiKey={apikey}"
urlpoli='https://verify.proxy.polimi.it'
urlpolisenza='http://verify.proxy.polimi.it'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
headers = {'User-Agent': user_agent}

def provaProxy(ind,nome='name not specified',verify=True):
    print(f"risultato usando {nome} e imponento Verify = {verify}:")
    try:
        sessione = requests.Session()
        sessione.trust_env=False
        sessione.proxies = proxies2
        sessione.verify = verify
        sessione.auth = requests.auth.HTTPProxyAuth(user,pwd)
        scaricata = sessione.get(ind)
        #scaricata=requests.get(ind,proxies=proxies2,auth=auth,headers=headers,verify=verify)
        print('It works')
    except Exception as e:
        if apikey in str(e):
            pos = str(e).find(apikey)
            print("..."+str(e)[pos+len(apikey):])
        else:
            print(str(e)[:len(str(e))//2])
            print(str(e)[len(str(e))//2:])
    print()

def provaWpad(ind,nome='name not specified',verify=True):
    print(f"risultato usando {nome} e imponento Verify = {verify}:")
    try:
        pac = pypac.get_pac(url='http://wpad.polimi.it/wpad.dat',allowed_content_types=['text/plain'])
        session = PACSession(pac)
        session.proxy_auth = requests.auth.HTTPProxyAuth(user, pwd)
        session.headers = headers
        resp=session.get(ind,verify=verify)
        zuppa=bs4.BeautifulSoup(resp.text,"lxml")
        if "polimi" in ind:
            print(zuppa.select("h1")[0].text,"\n")
        else:
            print(zuppa.text,"\n")
    except Exception as e:
        if apikey in str(e):
            pos = str(e).find(apikey)
            print("..."+str(e)[pos+len(apikey):],"\n")
        else:
            print(str(e)[:len(str(e))//2])
            print(str(e)[len(str(e))//2:],"\n")

provaWpad(urlpoli,'verificapoli con HTTPS')
provaWpad(urlpolisenza,'verificapoli senza HTTPS')
provaWpad(urlpoli,'verificapoli con HTTPS',verify=False)
provaWpad('https://www.google.it','google con HTTPS')
provaWpad(urlscopus,'scopus')


# provaProxy(urlscopus,'scopus')
# provaProxy(urlscopus,'scopus',False)
# provaProxy(urlpoli, 'verifica politecnico')
# provaProxy(urlpoli, 'verifica politecnico',False)
# provaProxy('https://www.google.it','google HTTPS')
# provaProxy('https://www.google.it','google HTTPS',False)
# provaProxy('http://www.google.it','google HTTP')
