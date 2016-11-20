#/usr/bin/env python3
# -_- coding: utf-8 -_-


import os
import http.cookiejar
import base64
import json
import argparse

from datetime import datetime
from random import randrange
from getpass import getpass
from sys import argv, exit
from threading import Thread

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print('Package needed: requests, BeautifulSoup')
    # os.system( "python -m pip install requests && python -m pip install beautifulsoup4")
    print('Please execute "python -m pip install requests && python -m pip install beautifulsoup4"')
    exit()


HEADER_INFO = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
    'Host':'www.renren.com',
    'Origin':'http://www.renren.com',
    'Connection':'keep-alive',
    'Content-Type':'application/x-www-form-urlencoded',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, sdch',
    'Accept-Language':'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2,es;q=0.2',
    'X-Requested-With': "XMLHttpRequest",
    }
LOGGED_IN_HEADER_INFO = {
    'Host': 'friend.renren.com',
    'Connection': 'keep-alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36',
    'DNT': '1',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2,es;q=0.2',
}

ROOT_DIRECTORY = os.path.abspath(os.path.join(os.getcwd(), os.pardir))


class InputFormatError(Exception):
    def __init__(self, msg):
        super(InputFormatError, self).__init__(msg)
        

class NoNetworkConnectionError(Exception):
    def __init__(self, msg):
        super(NoNetworkConnectionError, self).__init__(msg)
        



class RenRen:

    photo_patterns = ((''))

    def __init__(self, username, password, rememberme=True, base_dir=None, photo=True):
        super(RenRen, self).__init__()
        self._s = requests.session()
        self._s.cookies = http.cookiejar.LWPCookieJar('renren.cookie')
        try:
            self._s.cookies.load(ignore_discard=True)
        except IOError:
            pass

        self.username = username
        self.password = password
        self.rememberme = rememberme
        self.friends = None
        self.base_dir = base_dir if base_dir else os.getcwd()
        self.download_photo = photo


    def login(self):
        login_info = {'email': self.username,
                      'password': self.password,
                      'domain': 'renren.com',
                      'origURL': r'http%3A%2F%2Fwww.renren.com%2Fhome',
                      'icode': '',
                      'key_id': '1',
                      'autoLogin': 'true',
                      'captcha_type': 'web_login'}
        try:
            r = self._s.post("http://www.renren.com/ajaxLogin/login?1=1&uniqueTimestamp=20151121925391", 
                             data=login_info, headers=HEADER_INFO)
        except requests.exceptions.ConnectionError as e:
            raise NoNetworkConnectionError('No network connection. Please retry later.')

        if r.status_code == 200:
            print(r.url)
            self._s.cookies.save()
            if self.rememberme:
                # choice = input('Do you want to save your username and password? [Y/N]')
                choice = 'n'
                if choice.lower() == 'y':
                    try:
                        f = open('users/'+username, 'w')
                    except IOError:
                        os.mkdir('user/')
                        f = open('users/'+username, 'w')
                    f.write(username+'\n')
                    f.write(base64.b32encode(password))
                    f.close()
            return 'Login Successful!'
        elif r.status_code == 404:
            return 'Timestamp update needed. Please contact the author of this script.'
        else:
            return 'Error: %d' % r.status_code


    def get_friend_list(self):

        friend_page = self._s.get('http://friend.renren.com/managefriends', headers=LOGGED_IN_HEADER_INFO)
        frdata = self._s.get('http://friend.renren.com/groupsdata', headers=LOGGED_IN_HEADER_INFO)
        # friend_soup = BeautifulSoup(frdata.content, 'html.parser')
        # print frd.content
        # print '\n\n\n+++++++====================+++++++++++++++++++++++++\n\n\n\n\n'
        self.friends = json.loads('{'+''.join(frdata.text.split('\n')[7]).strip().rstrip(',')+'}')['friends']
        # print('Find', str(), 'friends: ')
        self.friend_number = len(self.friends)
        return [[people['fid'], people['fname']] for people in self.friends]


    def get_user_history(self, user, name, begin, end):
        target_name = os.path.join(self.base_dir, name)
        if not os.path.exists(target_name):
            os.mkdir(target_name)
        self.target_fhand = open(target_name+'/posts.txt', 'wb')
        self.photo_threads = []
        for year in range(end, begin-1, -1):
            for month in range(12, 0, -1):
                url = 'http://www.renren.com/timelinefeedretrieve.do?ownerid=%d&render=0&begin=0&limit=300&year=%d&month=%d&isAdmin=false' % (user, year, month)
                self.grab_page(url)

        for td in self.photo_threads:
            if td:
                td.join(240)
        self.target_fhand.close()


    def grab_page(self, url):
        all_stats = []
        r = self._s.get(url, headers=HEADER_INFO)
        # print s.get('http://www.renren.com/', headers=header_info).content
        # print r.content
        soup = BeautifulSoup(r.content, 'html.parser')
        list_of_feeds = soup.findAll('section', 'tl-a-feed')
        for new in list_of_feeds:
            string = new.find('input', type='hidden')['value']
            if self.download_photo and new.find('img'):
                ps = Thread(target=self.save_photo, args=(new.find('img').get('src'), string)).start()
                self.photo_threads.append(ps)
                if new.find('div', class_='content-photo'):
                    string += ': ' + new.find('div', class_='content-photo').text
                else:
                    string += ': 分享图片'
            # elif new.find('div', class_='content-main'):
            if new.find('div', class_='content-main'):
                string += ': ' + new.find('div', class_='content-main').text
            if new.find('div', class_='main-text'):
                string += ': ' + new.find('div', class_='main-text').text
            all_stats.append(string)
            self.target_fhand.write(string.encode('utf-8')+b'\n')
            self.target_fhand.write(b'\n=========================\n\n')
            print(string)
        return all_stats



    def save_photo(self, url, time):
        i = self._s.get(url) # headers=header_info)
        naam = self.target_name+'/photos/'+time+str(randrange(100))
        if i.status_code == 200:
            try:
                with open(naam+'.jpg', 'wb') as f:
                    f.write(i.content)
            except IOError:
                if not os.path.exists(self.target_name+'/photos/'):
                    os.mkdir(self.target_name+'/photos/')
                with open(naam+'.jpg', 'wb') as f:
                    f.write(i.content)
            print('Get photo successed.')
        else:
            print(i.status_code)
            print('Get photo', url, 'failed.')


    def close(self):
        self._s.cookies.save()
        self._s.close()
        # self.fhand.close()


class RenRenInterface:

    def __init__(self, arg):
        super(ClassName, self).__init__()
        self.arg = arg
        


def get_informs(maxlen=1000):
    target_user = int(input('Input a number of your friend: ')) - 1
    start = int(input('Start from year: '))
    end = int(input('Until year: '))
    if target_user > maxlen:
        raise InputFormatError('User doesn\'t exist!')
    elif start > end or start < 2006 or end > datetime.now().year:
        raise InputFormatError('You can only choose between year %d-%d' % (2006, datetime.now().year))
    return target_user, start, end



def main():
    parser = argparse.ArgumentParser(description='Keep your memory. From renren.com and Tieba.')
    parser.add_argument('-u', '--username-and-password', nargs=2, 
        metavar=('USER', 'PASSWORD'), help='Your username and password on RenRen')
    parser.add_argument('-P', '--photos', action='store_true')
    args = vars(parser.parse_args())

    if len(argv) == 1:
        user = RenRen(input('Username: '), getpass('Password: '), photo=args['photos'])
    else:
        user = RenRen(args['username_and_password'][0], 
                      args['username_and_password'][1], photo=args['photos'])

    try:
        user.login()
    except NoNetworkConnectionError as e:
        print('No network connection!')
        print(e)
        exit()

    # user.tell_me_what_you_see()
    friend_list = user.get_friend_list()
    for friend in enumerate(friend_list, start=1):
        print(friend[0], friend[1][1])

    while True:
        try:
            target, begin, end = get_informs(len(friend_list))
            break
        except (ValueError, InputFormatError) as e:
            print(e)
            print("Please input again...")

    user.get_user_history(friend_list[target][0],friend_list[target][1], begin, end)
    input('\nFinished!')
    user.close()





if __name__ == '__main__':
    main()
