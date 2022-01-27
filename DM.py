import sys, requests, bs4, os, time, shelve, shutil, datetime, json, selenium,pprint
import logging
import pandas as pd
from selenium import webdriver
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
diz_tot={}
lista_tot=[]
listanomi=[['yichen','wang'],['ju','zhang'],['lei','guo'],['wei','chen'],['feng','liu']]

for i in listanomi:
    indirizzo='https://dblp.org/search/author?q='+i[0]+'+'+i[1]
    scaricata=scaricapagina(indirizzo)
    lavorapagina(scaricata,i[0],i[1])

#pprint.pprint(diz_dblp)
for i,j in diz_dblp.items():
    lista_tot.append(dict(_id=i,Name=j['name'],Surname=j['surname'],Publications=salva_articoli(j['link'])))
    #diz_tot[i]=dict(Name=j['name'],Surname=j['surname'],Publications=salva_articoli(j['link']))

"""with open("DM.json", "w") as outfile:
    json.dump(diz_tot, outfile, indent=2)"""

with open('data.json', 'w', encoding='utf-8') as f:
  f.write(json.dumps(lista_tot, ensure_ascii=False, indent=2))

end = time.time()
print(f'It took {round(end - start,1)} seconds for {len(lista_tot)} records for a total of {round((end - start)/len(lista_tot),3)} sec per record')
