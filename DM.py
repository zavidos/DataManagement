import sys, requests, bs4, os, time, shelve, shutil, datetime, smtplib, ssl, selenium,pprint
import logging
import pandas as pd
from selenium import webdriver
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)

diz_dblp={}
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
            diz_dblp[nome+cognome+numero_omonimo]=ris.a.get('href')
        except:
            pass

def dati_auth(pub):
    ptype = 'nothing'
    link = 'nothing'
    authors = []
    title = 'nothing'
    where = 'nothing'

    if 'year' in pub.get('class'):
        # year is not always scrapable, except for this case. Might be done more elegantly
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

    return {'Type': ptype,
            'Link': link,
            'Authors': authors,
            'Title': title,
            'Where': where}
art=[]
def salva_articoli(pagautore):
    pag_autore=scaricapagina(pagautore)
    zuppa_aut=bs4.BeautifulSoup(pag_autore.text, 'lxml')
    """risultati_title=zuppa_aut.find_all("span", attrs={"class":"title"})
    for title in risultati_title:
        print(title.text)"""
    risultati_pub=zuppa_aut.find("ul", attrs={"class": "publ-list"})
    pub_list_data = []
    curr_year = 0
    for figlio in risultati_pub.children:
        pub_data = dati_auth(figlio)
        if type(pub_data) == int:
            curr_year = pub_data
        else:
            pub_data['Year'] = curr_year
            pub_list_data.append(pub_data)
    return pub_list_data
listanomi=[['wei','wang'],['yichen','wang']]

for i in listanomi:
    indirizzo='https://dblp.org/search/author?q='+i[0]+'+'+i[1]
    scaricata=scaricapagina(indirizzo)
    lavorapagina(scaricata,i[0],i[1])

art=salva_articoli("https://dblp.org/pid/74/8792-1.html")
#pprint.pprint(diz_dblp)
#for i,j in diz_dblp.items():
    #print(i,j)
    #salva_articoli(j)

art
