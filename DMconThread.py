import sys, requests, bs4, os, time, shelve, shutil, datetime, json, selenium,pprint,math
import logging
import pandas as pd
from selenium import webdriver
from threading import Thread
from pymongo import MongoClient
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.INFO)

start = time.time()

# Download and return webpage from URL
def scaricapagina(indirizzo):
    url = indirizzo
    user_agent = 'Mozilla/5.0'
    headers = {'User-Agent': user_agent}
    scaricata = requests.get(url, allow_redirects=True, headers=headers)
    scaricata.raise_for_status()
    logging.info(scaricata.status_code)
    return scaricata

# Parse webpage with BeautifulSoup and search for people, the use of [0] in result return only the part of DBLP where exact name matches are
def lavorapagina(scaricata,nome,cognome):
    zuppa = bs4.BeautifulSoup(scaricata.text, 'lxml')
    risultati_ul = zuppa.find_all("ul", attrs={"class":"result-list"})[0]
    risultati_li = risultati_ul.find_all("li", attrs={"itemtype":"http://schema.org/Person"})
    for ris in risultati_li:
        try:
            numero_omonimo=ris.a.span.next_sibling.next_sibling.text
            diz_dblp[nome+cognome+numero_omonimo]={'name':nome,'surname':cognome,'link':ris.a.get('href')}
        except:
            pass

#Save articles information, if Year is encoutered update year, else parse article type, link, authors list, title and location
def dati_auth(pub):
    ptype = 'nothing'
    link = 'nothing'
    authors = []
    title = 'nothing'
    where = 'nothing'
    if 'year' in pub.get('class'):
        return int(pub.contents[0])
    else:
        ptype = pub.attrs.get('class')[1]
        for content_item in pub.contents:
            class_of_content_item = content_item.attrs.get('class', [0])
            if 'data' in class_of_content_item:
                for author in content_item.findAll('span', attrs={"itemprop": "author"}):
                    authors.append(author.text)
                title = content_item.find('span', attrs={"class": "title"}).text
                for where_data in content_item.findAll('span', attrs={"itemprop": "isPartOf"}):
                    found_where = where_data.find('span', attrs={"itemprop": "name"})
                    if found_where:
                        where = found_where.text
            elif 'publ' in class_of_content_item:
                link = content_item.contents[0].find('a').attrs.get('href', "nothing")
    return {'Type': ptype, 'Link': link, 'Authors': authors, 'Title': title, 'Where': where}

#for each author download articles info cycling for article section in DBLP (divided by year) and then cycling through articles and running dati_auth function
def salva_articoli(pagautore):
    pag_autore=scaricapagina(pagautore)
    zuppa_aut=bs4.BeautifulSoup(pag_autore.text, 'lxml')
    risultati_pub=zuppa_aut.findAll("ul", attrs={"class": "publ-list"})
    pub_lista = []
    curr_year = 0
    for ri in risultati_pub:
        for figlio in ri.children:
            pub_data = dati_auth(figlio)
            if type(pub_data) == int:
                curr_year = pub_data
            else:
                pub_data['Year'] = curr_year
                pub_lista.append(pub_data)
    return pub_lista

diz_dblp={}
cognomi = ['Cao', 'Cui', 'Yang', 'Feng', 'Yao', 'Chen', 'Gao', 'Yu', 'Hsu', 'Ho', 'Ma', 'Zhu', 'He', 'Zhao', 'Liang', 'Zeng', 'Ding', 'Chu', 'Wu', 'Kao', 'Zhou', 'Zheng', 'Han', 'Tian', 'Wei', 'Xie', 'Shen', 'Chao', 'Xu', 'Liu', 'Chou', 'Zhang', 'Du', 'Lin', 'Chang', 'Dong', 'Li', 'Ren', 'Deng', 'Guo', 'Hu', 'Cheng', 'Tang', 'Wang', 'Cai', 'Jiang', 'Pan', 'Yuan', 'Kuo', 'Zhong', 'Song', 'Peng', 'Fan', 'Lu', 'Ye', 'Tan', 'Su', 'Sun', 'Luo', 'Huang', 'Xiao']
nomi = ['Jun', 'Zimo', 'Gang', 'Yang', 'Jie', 'Xiuying', 'Lei', 'Xinyi', 'Yan', 'Chao', 'Wei', 'Xia', 'Jing', 'Ping', 'Haoyu', 'Yong', 'Zihao', 'Ying', 'Min', 'Yichen', 'Yinuo', 'Na', 'Li', 'Xiulan', 'Wang', 'Yuhang', 'Zihan', 'Haoran', 'Hui', 'Tao', 'Fang', 'Guiying', 'Yuchen', 'Juan', 'Ming', 'Nushi', 'Yuxuan', 'Qiang']

listanomi = []
for cognome in cognomi:
    for nome in nomi:
        final = [nome,cognome]
        listanomi.append(final)
print(f'lunghezza della lista nomi = {len(listanomi)}')
#listanomi=listanomi[:4]
print(listanomi)

#connection to local MongoDB server
client = MongoClient('localhost', 27017)
db = client['DM']
coll=db.dblptutti


listaNoOmonimi=[]
lista_tot=[]
listathr=[]
for i in listanomi:
    try:
        indirizzo='https://dblp.org/search/author?q='+i[0]+'+'+i[1]
        scaricata=scaricapagina(indirizzo)
        lavorapagina(scaricata,i[0],i[1])
    except Exception as e:
        print(e)
        print(i[0],i[1],"non ha omonimi")
        listaNoOmonimi.append({"Nome":i[0],"Cognome":i[1]})
    time.sleep(1)

def thr(i):
    lista_tot.append(dict(_id=i,Name=diz_dblp[i]['name'],Surname=diz_dblp[i]['surname'],Publications=salva_articoli(diz_dblp[i]['link'])))

for i in diz_dblp:
    threadObject=Thread(target=thr,args=[i])
    listathr.append(threadObject)
print("listathr è lunga:",len(listathr))
listasplit=[listathr[10*i:10*i+10] for i in range(0,math.ceil(len(listathr)/10))]


"""for x in listathr:
    x.start()

for x in listathr:
    x.join()

coll.insert_many(lista_tot)"""

for l in listasplit:
    lista_tot=[]
    for x in l:
        x.start()
    for x in l:
        x.join()
    if lista_tot:
        coll.insert_many(lista_tot)
    else:
        print(l)
    time.sleep(8)

"""
with open('datathr2.json', 'w', encoding='utf-8') as f:
  f.write(json.dumps(lista_tot, ensure_ascii=False, indent=2))"""

#Save list of author with no homonyms 
db.noomo.insert_one({"noOmonimi":listaNoOmonimi})
end = time.time()
#print(f'It took {round(end - start,1)} seconds')
print(f'It took {round(end - start,1)} seconds for {len(listathr)} records for a total of {round((end - start)/len(listathr),3)} sec per record')
