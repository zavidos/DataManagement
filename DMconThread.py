import sys, requests, bs4, os, time, shelve, shutil, datetime, json, selenium,pprint
import logging
import pandas as pd
from selenium import webdriver
from threading import Thread
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.INFO)

start = time.time()

def scaricapagina(indirizzo):
    url = indirizzo
    user_agent = 'Mozilla/5.0'
    headers = {'User-Agent': user_agent}
    scaricata = requests.get(url, allow_redirects=True, headers=headers)
    scaricata.raise_for_status()
    logging.info(scaricata.status_code)
    return scaricata

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

def salva_articoli(pagautore):
    pag_autore=scaricapagina(pagautore)
    zuppa_aut=bs4.BeautifulSoup(pag_autore.text, 'lxml')
    risultati_pub=zuppa_aut.find("ul", attrs={"class": "publ-list"})
    pub_lista = []
    curr_year = 0
    for figlio in risultati_pub.children:
        pub_data = dati_auth(figlio)
        if type(pub_data) == int:
            curr_year = pub_data
        else:
            pub_data['Year'] = curr_year
            pub_lista.append(pub_data)
    return pub_lista

diz_dblp={}


cognomi = ["Wang", "Li", "Chang", "Liu", "Chen", "Yang", "Huang", "Chao", "Wu", "Chou", "Hsu", "Sun", "Ma", "Chu", "Hu", "Kuo", "He", "Ho", "Lin", "Kao", "Zhang"]
nomi = ["Yichen", "Yuxuan", "Haoyu", "Yuchen", "Zimo", "Yuhang", "Haoran", "Zihao", "Wei", "Qiang", "Wang", "Yan", "Nushi", "Wei", "Yan", "Hui", "Ying", "Zihan", "Xinyi", "Yinuo"]
listanomi = []
for cognome in cognomi:
    for nome in nomi:
        final = [nome,cognome]
        listanomi.append(final)
listanomi=listanomi[0:15]
print(listanomi)

#listanomi=[['yichen','wang'],['ju','zhang'],['lei','guo'],['wei','chen'],['feng','liu']]
lista_tot=[]
listathr=[]
for i in listanomi:
    try:
        indirizzo='https://dblp.org/search/author?q='+i[0]+'+'+i[1]
        scaricata=scaricapagina(indirizzo)
        lavorapagina(scaricata,i[0],i[1])
    except:
        print(i[0],i[1],"non ha omonimi")

def thr(i):
    lista_tot.append(dict(_id=i,Name=diz_dblp[i]['name'],Surname=diz_dblp[i]['surname'],Publications=salva_articoli(diz_dblp[i]['link'])))

for i in diz_dblp:
    threadObject=Thread(target=thr,args=[i])
    listathr.append(threadObject)

for x in listathr:
    x.start()

for x in listathr:
    x.join()

with open('datathr.json', 'w', encoding='utf-8') as f:
  f.write(json.dumps(lista_tot, ensure_ascii=False, indent=2))

end = time.time()
print(f'It took {round(end - start,1)} seconds for {len(lista_tot)} records for a total of {round((end - start)/len(lista_tot),3)} sec per record')
