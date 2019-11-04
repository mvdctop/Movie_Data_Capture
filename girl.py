# coding=utf-8
import csv
import re
from lxml import etree
import json
from bs4 import BeautifulSoup
from ADC_function import *
import os
import datetime

def getActorURL(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = html.xpath('//*[@id="waterfall"]/div/a/@href')
    return result1
# =====
def getName(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result1 = str(html.xpath('//*[@id="waterfall"]/div[1]/div/div[2]/span/text()')).strip(" ['']")
    return result1
def getActorPhotoURL(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result1 = str(html.xpath('//*[@id="waterfall"]/div[1]/div/div[1]/img/@src')).strip(" ['']")
    return result1
def getBirthday(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result1 = str(html.xpath('//p[contains(text(),"生日: ")]/text()')).strip(" ['']")
    return result1
def getAge(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result1 = str(html.xpath('//p[contains(text(),"年齡: ")]/text()')).strip(" ['']")
    return result1
def getHigh(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result1 = str(html.xpath('//p[contains(text(),"身高: ")]/text()')).strip(" ['']")
    return result1
def getCup(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result1 = str(html.xpath('//p[contains(text(),"罩杯: ")]/text()')).strip(" ['']")
    return result1
def getInfo(htmlcode,xpath):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result1 = str(html.xpath(xpath)).strip(" ['']")
    return result1

# =====

filename = '2.csv'

def create_csv():
    path = filename
    with open(path, 'w') as f:
        print("名称,头像URL,个人URL,生日,年龄,身高,罩杯", file=f, )


def write_csv(htmlcode, url):
    path = filename
    with open(path, 'a+') as f:
        print(getName(htmlcode), end=',', file=f)
        print(getActorPhotoURL(htmlcode), end=',', file=f)
        print(url, end=',', file=f)
        print(getBirthday(htmlcode).strip('生日: '), end=',', file=f)
        print(getAge(htmlcode).strip('年齡: '), end=',', file=f)
        print(getHigh(htmlcode).strip('身高: ').strip('cm'), end=',', file=f)
        print(getCup(htmlcode).strip('罩杯: '), file=f)

def main(url):
    actor_list = getActorURL(get_html(url))
    b = 0
    c = len(actor_list)
    for i in actor_list:
        try:
            htmlcode = get_html(i)
            write_csv(htmlcode, i)
            b = b + 1
            print('[' + str(b) + '/' + str(c) + ']', 'writed', getName(htmlcode))
        except:
            print('error')
            b = b + 1
            continue

if os.path.exists(filename) == False:
    print('create file')
    create_csv()

a = 198
while a <= 202:
    print('page:', a)
    main('https://www.javbus.com/actresses/' + str(a))
    print(datetime.datetime.now().strftime("%Y.%m.%d-%H:%M:%S"))
    a = a + 1
