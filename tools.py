#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 20:03:00 2022

@author: shuan
"""

import requests,os
import time
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

def scroll(chrome,stop,step,delay=0.5):
    pos=0
    for i in range(0,stop,step):
        pos=i+step
        chrome.execute_script(f'window.scrollTo{i},{pos}')
        time.sleep(delay)

def get_chrome(url,driver_path='/Users/shuan/Desktop/python/webdriver/chromedriver.exe',hide=False):
    try:
        options = webdriver.ChromeOptions()
        if hide:
            options.add_argument('--headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("--start-maximized")
            
        service=Service(driver_path)
        chrome = webdriver.Chrome(service=service, options=options)
        chrome.get(url)
        time.sleep(1)
        
        return chrome
    except Exception as e:
        print(e)
    return None

def find_element(chrome,xpath):
    try:
        return chrome.find_element(By.XPATH,xpath)
    except Exception as e:
        print(e)
    return None

def make_dirs(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            return True
    except Exception as e:
        print('路徑穆綠錯誤！',e)
    return False

def get_date(hms = False):
    if hms:
        now = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    else:
        now = datetime.now().strftime('%Y/%m/%d')
    return now

def get_date2(hms = False,sep='-'):
    if hms:
        now = datetime.now().strftime(f'%Y{sep}%m{sep}%d %H:%M:%S')
    else:
        now = datetime.now().strftime(f'%Y{sep}%m{sep}%d')
    return now

def get_soup(url,post_data= None):
    headers={
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    try:
        if post_data is not None:
            resp=requests.post(url,post_data,headers=headers)
        else:
            resp = requests.get(url,headers=headers)
        resp.encoding='utf-8'
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text,'lxml')
            return soup
        else:
            print('取得網頁失敗',resp.status_code)
    except Exception as e:
        print(e)
    return None

def save_pic(url, file_name='temp.jpg'):
    try:
        resp = requests.get(url)
        status_code = resp.status_code
        if status_code== 200:
            with open(file_name,'wb') as f:
                f.write(resp.content)
            print(f'{file_name}儲存完畢')
    except Exception as e:
        print('圖片路徑錯誤!',e)
        
if __name__ == '__main__':
    print('test!')
    url = 'https://tw.yahoo.com/'
    print(get_date(hms = False))
    