#目的:主要是抓出當日跟昨日ptt beauty中推數>10的文章，並取得img連結送到tg
#使用方法:請在telegram_bot_sendtext函式中輸入你的tg bot token跟group id

import datetime
import json
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

def open_beauty_json():
    try:
        with open("pttbe.json", "r", encoding="utf-8") as f:
            bejson = json.loads(f.read())
        return bejson
    except Exception as e:
        print(e)
        return None

def get_text_webpage(url):
    payload={'cookies':{'over18': '1'}}
    resp = requests.get(url=url,cookies={'over18': '1'})
    if resp.status_code != 200:
        print('error url')
        sys.exit()
    else:
        return resp.text

def get_web_url(doc,date):
    soup=BeautifulSoup(doc,'html.parser')
    all_push=soup.find_all('div','r-ent')
    resouces=list()
    for blocks in all_push:
        resource = dict()
        date_incolumn=blocks.find('div', 'date')
        push_count = blocks.find('div', 'nrec')
        if date_incolumn:
            if date_incolumn.text.strip() == date:
                if push_count:
                    try:
                        if int(push_count.text.strip()) > 10:
                            print(push_count.text.strip())
                            a_url=blocks.find('div','title').a['href'] if blocks.find('div','title').a['href'] else ''
                            a_title=blocks.find('div', 'title').text.strip()
                            print(a_title)
                            print(a_url)
                            print(date)
                            resource['a_url'] = 'https://www.ptt.cc' + a_url
                            resource['a_title'] = a_title
                            resource['date'] = date
                            resouces.append(resource)
                    except Exception:
                        if push_count.text.strip()== '爆':
                            a_url=blocks.find('div','title').a['href'] if blocks.find('div','title') else ''
                            a_title=blocks.find('div', 'title').text.strip()
                            print(a_title)
                            print(a_url)
                            print(date)
                            resource['a_title'] = a_title
                            resource['a_url'] = 'https://www.ptt.cc' + a_url
                            resource['date'] = date
                            resouces.append(resource)
                        elif push_count.text.startswith('X'):
                            continue
    return resouces

def get_img_url(url):
    docs = get_text_webpage(url)
    soup = BeautifulSoup(docs, 'html.parser')
    all_a=soup.find_all('a')
    img_source=list()
    for a in all_a:
        if a['href']:
            match_img=re.compile(r'https://.*jpg$')
            match_gif=re.compile(r'https://.*imgur.com')
            if match_img.search(a['href']):
                img_source.append(a['href'])
            elif match_gif.search(a['href']):
                img_source.append(a['href'])

    for a in img_source:
        print(a)
    return img_source

def telegram_bot_sendtext(bot_message):
    bot_token = ''
    bot_chatID = ''
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    print(send_text)
    requests.packages.urllib3.disable_warnings()
    respnose=requests.get(send_text, verify=False, timeout=(3.05, 27))
    return respnose.json()

def main(date):
    beautu_json=open_beauty_json()
    url='https://www.ptt.cc/bbs/Beauty/index.html'
    docs=get_text_webpage(url)
    all_pages_info=list()
    info=get_web_url(docs,date)
    all_pages_info +=info
    if not info:
        soup = BeautifulSoup(docs, 'html.parser')
        pre_page_url = 'https://www.ptt.cc/' + soup.find('div', 'btn-group btn-group-paging').find_all('a')[1]['href']
        print(pre_page_url)
        docs = get_text_webpage(pre_page_url)
        info = get_web_url(docs,date)
        all_pages_info +=info
    while info:
        soup = BeautifulSoup(docs, 'html.parser')
        pre_page_url = 'https://www.ptt.cc/' + soup.find('div', 'btn-group btn-group-paging').find_all('a')[1]['href']
        docs = get_text_webpage(pre_page_url)
        info = get_web_url(docs,date)
        if info:
            all_pages_info +=info
    save_all_pages_info=list()
    save_all_pages_info +=all_pages_info
    if beautu_json:
        for a in save_all_pages_info:
            for items in [jsonform.values() for jsonform in beautu_json]:
                if a.get('a_url') in items:
                    all_pages_info.remove(a)
                    break
    if all_pages_info:
        for a in all_pages_info:
            try:
                josn_gotg_info = json.dumps(a, ensure_ascii=False, indent=2)
                print(josn_gotg_info)
                telegram_bot_sendtext(josn_gotg_info)
                nice_urls=get_img_url(a['a_url'])

                for good in nice_urls:
                    time.sleep(3)
                    print(good)
                    telegram_bot_sendtext(good)
            except Exception as e:
                print(e)
    if beautu_json:
        beautu_json += all_pages_info
        with open('pttbe.json', 'w', encoding='utf-8') as f:
            json.dump(beautu_json, f, indent=2, ensure_ascii=False)
    else:
    # print(bejson)
        with open('pttbe.json', 'w', encoding='utf-8') as f:
            json.dump(all_pages_info, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    today = datetime.datetime.now()
    today_form=today.strftime('%m/%d').lstrip('0')
    print(today_form)
    main(today_form)
    yesterday = today - datetime.timedelta(days=1)
    yesterday_form=yesterday.strftime('%m/%d').lstrip('0')
    print(yesterday_form)
    main(yesterday_form)



