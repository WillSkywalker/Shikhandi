#/usr/bin/env python
# -_- coding: utf-8 -_-


import os
import requests
import cookielib
from bs4 import BeautifulSoup
from login import header_info

s = requests.session()
s.cookies = cookielib.LWPCookieJar('renren.cookie')
try:
    s.cookies.load(ignore_discard=True)
except:
    print "You haven't logged in yet!"
    print "run `python auth.py` to log in."


def a_thousands_times_over(user):
    for year in [2015, 2014, 2013]:
        for month in xrange(1, 13):
            url = 'http://www.renren.com/timelinefeedretrieve.do?ownerid=%d&render=0&begin=0&limit=300&year=%d&month=%d&isAdmin=false' % (user, year, month)
            grab(url)


def grab(url):
    all_stats = []
    r = s.get(url, headers=header_info)
    soup = BeautifulSoup(r.content, 'html.parser')
    list_of_feeds = soup.findAll('section', 'tl-a-feed')
    for new in list_of_feeds:
        string = '-'.join(stamp.text for stamp in new.findAll('span')[2::-1]).replace(u'月', '')
        if new.find('div', class_='content-image'):
            save_photo(new.find('img').get('src'), string)
            string += ': ' + new.find('div', class_='content-image').text
        elif new.find('div', class_='content-main'):
            string += ': ' + new.find('div', class_='content-main').text
        all_stats.append(string)
        print string
    return all_stats




def save_photo(url, time):
    i = s.get(url, header_info)
    if i.status_code == 200:
        try:
            open('photos/'+time, 'wb').write(i.content)
        except IOError:
            os.mkdir('photos/')
            open('photos/'+time, 'wb').write(i.content)
        print 'Get photo successed.'
    else:
        print 'Get photo', url, 'failed.'



if __name__ == '__main__':
    print grab('http://www.renren.com/timelinefeedretrieve.do?ownerid=********&render=0&begin=0&limit=30&year=2014&month=11&isAdmin=false')
