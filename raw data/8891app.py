#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 00:15:14 2023

@author: shuan
"""


import tkinter as tk
from tkinter import ttk
from tools import get_chrome,find_element,make_dirs
from bs4 import BeautifulSoup
import time
import pandas as pd
from datetime import datetime 
import tkinter.messagebox as tkmessage
from queue import Queue
from threading import Thread
import matplotlib.pyplot as plt
from PIL import ImageTk, Image
import seaborn as sns


font1 = ("微軟正黑體", 12)
font2 = ("標楷體", 42)
font3 = ("標楷體", 16)
font4 = ("微軟正黑體", 24)
font5 = ("標楷體", 20)

def get_car_data(url):
    global chrome
    chrome = None
    try:
        chrome=get_chrome(url,hide=True)
        soup =BeautifulSoup(chrome.page_source,'lxml')
        cars = soup.find( id ='search-result').find_all('a')
        print(len(cars))
        datas=[]
        for i,car in enumerate(cars):
            area = car.find('div',class_='ib-info-im').find('span').text.strip()
            image = car.find('img').get('data-src')
            title = car.find('img').get('title')
            link = 'https://www.8891.com.tw'+car.get('href')
            price,year,km = car.find('div',class_='ib-row ib-extra').text.strip().split()
            #print(f'{i+1}.{title}',link,price,year,km,image,sep='\n')
            datas.append([title,link,area,price,year,km,image])
            #print('-----------------------------------------------------------------')
        q.put(datas)
        return datas
    except Exception as e:
        print(e)
    finally:
        if chrome is not None:
            chrome.quit()
    return None


def find_car():
    global datas,key
    try:
        if entry0.get() == '':
            datas = None
            labelstart.config(text='未輸入欲查找車種!',fg = 'red')
            return
        labelstart.config(text='查詢中....請稍候',fg = '#b0e0e6')
        url = 'https://auto.8891.com.tw'
        chrome = get_chrome(url,hide=True)
        time.sleep(1)
        find_element(chrome,'/html/body/div[5]/div/div[6]/div[2]/div/div[7]/div[4]').click()
        time.sleep(1)
        input_el =find_element(chrome,'/html/body/div[5]/div/div[4]/div/div[1]/div[2]/form/div[1]/input')
        time.sleep(1)
        input_el.click()
        time.sleep(0.5)
        input_el.clear()
        time.sleep(0.5)
        key = entry0.get()
        time.sleep(1)
        input_el.send_keys(f'{key}\n')
        time.sleep(1)
        soup = BeautifulSoup(chrome.page_source,'lxml')
        pages = eval(soup.find('div',class_='_pages_1skvm_295').find_all('button')[-1].text.strip())
        chrome.quit()
        threads=[]
        datas=[]
        max_count =10
        count=10
        if tkmessage.askquestion(title = '警告', message = f'{key}:{pages}頁(確定執行？(yes/no):)') == 'yes':
            start=datetime.now()
            for i in range(pages):
                api_url=f'https://auto.8891.com.tw?page={i+1}&key={key}'
                print(api_url)
                threads.append(Thread(target=(get_car_data),args=(api_url,)))
                count+=1
                if count%max_count==0:
                    for t in threads:
                        t.start()
                    for t in threads:
                        t.join()
                    threads=[]
                    count=0         
            for t in threads:
                t.start()
            for t in threads:
                t.join()
        for i in range(q.qsize()):
            datas += q.get()
        labelstart.config(text = f'爬找完畢共{len(datas)}筆資料. 共花費:{datetime.now()-start}', fg = '#32cd32')
        list_var.set(datas)

    except Exception as e:
        print(e)
        labelstart.config(text='請重新查詢！！')

def clear_find():
    global datas
    if datas == None or datas== []:
        labelstart.config(text='未查尋資料!',fg = 'red')
        return
    entry0.delete(0,'end')
    labelstart.config(text='清除查尋資料!',fg = 'green')
    datas=[]
    list_var.set(datas)
        
def select_car():
    global data,df,df1
    try:
        year=box1.get()
        price=box2.get()
        df=pd.DataFrame(datas,columns=columns)
        df['year']=df['year'].apply(lambda x : eval(x.replace('年','')))
        df=df.drop(df[(df['price']=='電洽') | (df['price']=='暫停出售')  | (df['price']=='代標車') ].index)
        df['price']=df['price'].apply(lambda x:eval(x.replace('萬','')))*10000
        if datas == None or datas== []:
            labelstart.config(text='未查尋資料!',fg = 'red')
            return
        elif year =='' and price== '':
            labelstart.config(text = '未篩選年份及價格...')
            list_var.set(datas)
            return
        elif year == '':
            if price == price_list[0]:
                df1 = df.sort_values(['price'],ascending = False)
            elif price == price_list[1]:
                df1 = df.sort_values(['price'])
            elif price ==price_list[2]:
                df1= df[df['price']<= 100000]
            elif price == price_list[3]:
                df1= df[df['price']<= 500000]
            elif price ==price_list[4]:
                df1= df[df['price']<= 1000000]
            elif price == price_list[5]:
                df1= df[df['price']<= 1500000]
            elif price ==price_list[6]:
                df1= df[df['price']<= 2000000]
            elif price == price_list[7]:
                df1= df[df['price']<= 3000000]
            elif price == price_list[8]:
                df1= df[df['price']> 3000000]
            data=df1.values.tolist()
            list_var.set(data)
            labelstart.config(text=f'已篩選{len(data)}筆資料!',fg = '#00ffff')
        elif price == '':
            if year == year_list[0]:
                df1 = df[df['year']<=2000]
            for i,y in enumerate(year_list[1:]):
                if year == year_list[1:][i]:
                    df1 = df[df['year']==eval(y)]
            data=df1.values.tolist()
            list_var.set(data)
            labelstart.config(text=f'已篩選{len(data)}筆資料!',fg = '#00ffff')
        elif year != '' and price != '':
            if price == price_list[0] and year == year_list[0]:
                df1 = df[df['year']<=2000].sort_values(['price'],ascending = False)
            elif price == price_list[1] and year == year_list[0]:
                df1 = df[df['year']<=2000].sort_values(['price'])
            elif price == price_list[0]:
                df1 = df[df['year']==eval(year)].sort_values(['price'],ascending = False)
            elif price == price_list[1]:
                df1 = df[df['year']==eval(year)].sort_values(['price'])
            elif price == price_list[2] and year == year_list[0]:
                df1= df[(df['year']<=2000) & (df['price']<= 100000)]
            elif price == price_list[2]:
                df1= df[(df['year']==eval(year)) & (df['price']<= 100000)]
            elif price == price_list[3] and year == year_list[0]:
                df1= df[(df['year']<=2000) & (df['price']<= 500000)]                
            elif price == price_list[3]:
                df1= df[(df['year']==eval(year)) & (df['price']<= 500000)]
            elif price == price_list[4] and year == year_list[0]:
                df1= df[(df['year']<=2000) & (df['price']<= 1000000)]                
            elif price == price_list[4]:
                df1= df[(df['year']==eval(year)) & (df['price']<= 1000000)]
            elif price == price_list[5] and year == year_list[0]:
                df1= df[(df['year']<=2000) & (df['price']<= 1500000)]                
            elif price == price_list[5]:
                df1= df[(df['year']==eval(year)) & (df['price']<= 1500000)]
            elif price == price_list[6] and year == year_list[0]:
                df1= df[(df['year']<=2000) & (df['price']<= 2000000)]                
            elif price == price_list[6]:
                df1= df[(df['year']==eval(year)) & (df['price']<= 2000000)]
            elif price == price_list[7] and year == year_list[0]:
                df1= df[(df['year']<=2000) & (df['price']<= 3000000)]                
            elif price == price_list[7]:
                df1= df[(df['year']==eval(year)) & (df['price']<= 3000000)]
            elif price == price_list[8] and year == year_list[0]:
                df1= df[(df['year']<=2000) & (df['price']> 3000000)]                
            elif price == price_list[8]:
                df1= df[(df['year']==eval(year)) & (df['price']> 3000000)]
            data=df1.values.tolist()
            list_var.set(data)
            labelstart.config(text=f'已篩選{len(data)}筆資料!',fg = '#00ffff')
    except Exception as e:
        labelstart.config(text=e)
    

def clear_select():
    global datas
    if datas == None or datas== []:
        labelstart.config(text='未查尋資料!',fg = 'red')
        box1.set('')
        box2.set('')
        return
    box1.set('')
    box2.set('')
    labelstart.config(text='清除篩選!',fg = '#ff4500')
    list_var.set(datas)

def to_csv():
    global datas
    if datas == None or datas== []:
        labelstart.config(text='未查尋資料!',fg = 'red')
        return
    make_dirs(path)
    if tkmessage.askquestion(title = '警告', message = '是否要另外儲存已篩選資料？') == 'yes':
        if len(data) != 0:
            df=pd.DataFrame(datas,columns=columns)
            df.to_csv(f'{path}{key}_8891.csv',encoding='utf-8-sig')
            df1=pd.DataFrame(data,columns=columns)
            df1.to_csv(f'{path}{key}_篩選資料.csv',encoding='utf-8-sig')
        else:
            tk.messagebox.showinfo(title='提示', message='未有篩選資料，已儲存所有資料...')
            df=pd.DataFrame(datas,columns=columns)
            df.to_csv(f'{path}{key}_8891.csv',encoding='utf-8-sig')
        labelstart.config(text = '存檔完畢.',fg= '#ba55d3')
    else:
        df=pd.DataFrame(datas,columns=columns)
        df.to_csv(f'{path}{key}_8891.csv',encoding='utf-8-sig')
        labelstart.config(text = '存檔完畢.',fg= '#ba55d3')
        
        
def to_png():
    global new_win,new_win2
    try:
        if datas == None or datas== []:
            labelstart.config(text='未查尋資料!',fg = 'red')
            return
        df = pd.read_csv(f'{path}{key}_8891.csv',encoding='utf-8',index_col=0)
        df['year']=df['year'].apply(lambda x : eval(x.replace('年','')))
        df=df.drop(df[(df['price']=='電洽') | (df['price']=='暫停出售')  | (df['price']=='代標車') ].index)
        df['price']=df['price'].apply(lambda x:eval(x.replace('萬','')))*10000
        df['km']=df['km'].apply(lambda x : eval(x.replace('萬','').replace('km',''))*10000 if '萬' in x else eval(x.replace('km','')))
        
        sns.jointplot(x='year',y='price',hue='km',data=df)
        plt.savefig(f'{path}{key}.png',bbox_inches='tight')
        sns.pairplot(df)
        plt.savefig(f'{path}{key}(1).png',bbox_inches='tight')
        plt.close()
        labelstart.config(text = '存圖完畢.',fg= '#6a5acd')
        if new_win is not None:
            new_win.destroy()
        new_win= tk.Toplevel(win)
        image= ImageTk.PhotoImage(Image.open(f'{path}{key}.png'))
        tk.Label(new_win, image=image).pack(anchor='center')
        if new_win2 is not None:
            new_win2.destroy()
        new_win2 = tk.Toplevel(win)
        image2=ImageTk.PhotoImage(Image.open(f'{path}{key}(1).png'))
        tk.Label(new_win2, image=image2).pack(anchor='center')
        new_win.mainloop()
        new_win2.mainloop()
    except Exception as e:
        print(e)
        tk.messagebox.showinfo(title='提示', message='請先存csv檔')

def close():
    win.destroy()

q= Queue()
columns = ['title','link','area','price','year','km','image']
data=[]
datas = []
path='res/8891_data/'
win = tk.Tk()
win.title('8891二手車查詢系統')
win.geometry('480x540')
win.resizable(False,False)
new_win=None
new_win2=None
list_var = tk.StringVar()
list_var.set([])
price_list=['由高至低↓','由低至高↑','10萬↓','50萬↓','100萬↓','150萬↓','200萬↓','300萬↓','300萬↑']
year_list=['2000年↓']
for i in range(2000,datetime.now().year):
    year_list.append(str(i+1))
                        




frame0 = tk.Frame(win, bg='#ffc0cb')
frame0.pack(fill="x")
frame1 = tk.Frame(win, bg='#add8e6')
frame1.pack(fill="y")
frame2 = tk.Frame(win)
frame2.pack(fill="y")
frame3 = tk.Frame(win, bg='#ffc0cb')
frame3.pack(fill="y")
frame4 = tk.Frame(win, bg='#add8e6')
frame4.pack(fill="y")
frame5 = tk.Frame(win)
frame5.pack(fill="x")
scrollbar_y = tk.Scrollbar(frame5)
scrollbar_y.pack(side='right', fill='y')

labelstart = tk.Label(frame0, text="歡迎使用8891中古車查詢系統:", font=font1, bg="black", fg="white", anchor="w")
labelstart.pack(fill="x")

label0 = tk.Label(frame0, text="想找什麼車呢？", font=font5)
label0.pack(padx=10, pady=10)
entry0 = tk.Entry(frame0, bg="lightyellow", fg="black", font=font3, borderwidth=3)
entry0.pack(padx=10, pady=10)

button0 = tk.Button(frame1, text="查詢", font=font5,fg = 'black',command = find_car)
button0.grid(row=0, column=0,padx=5, pady=5,columnspan=2,sticky='news')
button1 = tk.Button(frame1, text="清除查詢", font=font5,fg = 'black',command = clear_find)
button1.grid(row=0, column=2,padx=5, pady=5,columnspan=2,sticky='news')

label1 = tk.Label(frame2, text="年份:", font=font3)
label1.grid(row=1, column=0)
box1 = ttk.Combobox(frame2,text='',width = 15,values=year_list)
box1.grid(row=1, column=1, pady=5)
label2 = tk.Label(frame2, text="價格:", font=font3)
label2.grid(row=1, column=2)
box2 = ttk.Combobox(frame2,text = '',width=15,values=price_list)
box2.grid(row=1, column=3, pady=5)

button2 = tk.Button(frame3, text="篩選", font=font5,fg = 'black',command = select_car)
button2.grid(row=0, column=0,padx=5, pady=5,columnspan=2,sticky='news')
button3 = tk.Button(frame3, text="清除篩選", font=font5,fg = 'black',command = clear_select)
button3.grid(row=0, column=2,padx=5, pady=5,columnspan=2,sticky='news')



button4 = tk.Button(frame4, text="轉csv", font=font3,command=to_csv)
button4.grid(row=0, column=0, padx=10, pady=10)
button5 = tk.Button(frame4, text="輸出圖表\n每年平均價格\n(篩選數據不適用)", font=font3,command=to_png)
button5.grid(row=0, column=1, padx=10, pady=10)
button6 = tk.Button(frame4, text="關閉", font=font3,command = close)
button6.grid(row=0, column=2, padx=10, pady=10)


listbox = tk.Listbox(frame5, listvariable=list_var, font=font1, bg="aliceblue", fg="black",yscrollcommand=scrollbar_y.set)
listbox.pack(fill="both",expand =1)

scrollbar_y.config(command = listbox.yview)

win.mainloop()