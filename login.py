#/usr/bin/env python
# -_- coding: utf-8 -_-


import os
import requests
import cookielib
import base64
from sys import argv
from bs4 import BeautifulSoup


header_info = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.1581.2 Safari/537.36',
    'Host':'www.renren.com',
    'Origin':'http://www.renren.com',
    'Connection':'keep-alive',
    'Content-Type':'application/x-www-form-urlencoded',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2,es;q=0.2',
    'Cache-Control':'max-age=0',
    'X-Requested-With': "XMLHttpRequest",
    }
s = requests.session()
s.cookies = cookielib.LWPCookieJar('renren.cookie')


def login_renren(username, password, rememberme=True):


    s.post("http://www.renren.com/ajax/ShowCaptcha",data={'email': username})
    # soup = BeautifulSoup(r.content, "html.parser")

    login_info = {'email': username,
                  'password': password,
                  'domain': 'renren.com',
                  'icode': ''}
    r = s.post("http://www.renren.com/ajaxLogin/login?1=1&uniqueTimestamp=20151041528531", data=login_info, headers=header_info)

    if r.status_code == 200:
        print 'Login Successful!'
        s.cookies.save()
        if rememberme:
            choice = raw_input('Do you want to save your username and password? [Y/N]')
            if choice.lower() == 'y':
                try:
                    f = open('users/'+username, 'w')
                except IOError:
                    os.mkdir('user/')
                    f = open('users/'+username, 'w')
                f.write(username+'\n')
                f.write(base64.b32encode(password))
                f.close()
    elif r.status_code == 404:
        print 'Timestamp update needed'
    else:
        print r.status_code

    print r.json



def grab(url):
    s = requests.session()
    s.cookies = cookielib.LWPCookieJar('renren.cookie')
    all_stats = []
    # print s.get('http://www.renren.com/')
    r = s.get(url, headers=header_info)
    # print r.content
    soup = BeautifulSoup(r.content, 'html.parser')
    list_of_feeds = soup.findAll('section', 'tl-a-feed')
    for new in list_of_feeds:
        string = '-'.join(stamp.text for stamp in new.findAll('span')[2::-1]).replace(u'月', '')
        if new.find('div', class_='content-image'):
            save_photo(new.find('img').get('src'), string)
            string += ': ' + new.find('div', class_='content-image').text
        elif new.find('div', class_='content-main'):
            string += ': ' + new.find('div', class_='content-main').find('div').text
        all_stats.append(string)
        print string
    return all_stats





def main():
    if len(argv) == 1:
        login_renren(raw_input('Username: '), raw_input('Password: '))
    elif argv[1] == '-f':
        with open('users/'+argv[2]) as fhand:
            l = fhand.readlines()
            login_renren(l[0], base64.b32decode(l[1]), rememberme=False)
    elif argv > 1:
        print 'Usage: python login.py [-f username]'




if __name__ == '__main__':
    main()
