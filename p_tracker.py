from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
import time
from statistics import mean
import requests
import sys
import json

discounts = []

def Price_Tracker(*args):
    for arg in args:
        option = webdriver.ChromeOptions()
        option.add_argument("--incognito") # creates new instance of chrome in incognito mode
        browser = webdriver.Chrome(executable_path=r'C:\Users\bluep\chromedriver.exe', chrome_options=option) # PATH to chrome driver, r allows pc to read unicode
        browser.get(arg)# url
        time.sleep(3.83698792)
        name = browser.find_elements_by_id('productTitle')#gets name of product
        name = name[0].text
        try:
            h = browser.find_elements_by_id('priceblock_saleprice') #finds current_price number
            current_price = h[0].text
        except:
            try:
                h = browser.find_elements_by_id('priceblock_ourprice') #compensates for different html styles
                current_price = h[0].text
            except:
                browser.close()

                continue
        browser.close() # this must come after gettin text from page
        current_price = current_price.strip('$') #takes away $ mark
        current_price = current_price.replace(',','')   #takes care of commas
        current_price = float(current_price) #converts string to float
        price_dict = None
        with open('price_data.txt', 'r+') as file:
            price_dict = json.load(file)
        if name not in price_dict:
            price_dict[name] = [current_price]
            with open('price_data.txt', 'w') as file:
                json.dump(price_dict, file)
            pushbullet_message('Setup Price Tracking for {a}'.format(a=name), 'Successfully setup price tracking for {a}'.format(a=name))
            continue
        else:
            price_dict[name].append(current_price)
            price_list = price_dict[name]
            first = price_list[0]
            last = price_list[-1]
            yesterday = price_list[-2]
            price_list.sort()
            high = price_list[-1]
            low = price_list[0]
            if last < yesterday and last < first:
                discounts.append((first,last,high,low,yesterday,name))
            with open('price_data.txt', 'w') as file:
                json.dump(price_dict, file)


def pushbullet_message(title, body):
    msg = {"type": "note", "title": title, "body": body}
    TOKEN = 'o.CjtuTtCEjYk6bTNADb4bNJR0m0zxQixt'
    resp = requests.post('https://api.pushbullet.com/v2/pushes', 
                         data=json.dumps(msg),
                         headers={'Authorization': 'Bearer ' + TOKEN,
                                  'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Error',resp.status_code)
    else:
        print ('Message sent') 

#Amazon urls are placed in here
Price_Tracker('https://www.amazon.com/ELEGOO-Project-Tutorial-Controller-Projects/dp/B01D8KOZF4/ref=sr_1_3?dchild=1&keywords=arduino+kit&qid=1587334169&sr=8-3','https://www.amazon.com/Dell-XPS-9380-13-3-Notebook/dp/B07R73H8PC/ref=sxin_3_osp44-013b3ba6_cov?ascsubtag=amzn1.osa.013b3ba6-0b2c-4572-817a-d5becaee9c2e.ATVPDKIKX0DER.en_US&creativeASIN=B07R73H8PC&cv_ct_cx=laptop&cv_ct_id=amzn1.osa.013b3ba6-0b2c-4572-817a-d5becaee9c2e.ATVPDKIKX0DER.en_US&cv_ct_pg=search&cv_ct_wn=osp-search&dchild=1&keywords=laptop&linkCode=oas&pd_rd_i=B07R73H8PC&pd_rd_r=699a9623-97b2-4444-a85b-455582f9eb19&pd_rd_w=fWDrj&pd_rd_wg=FwsxN&pf_rd_p=b6bd5224-05d9-4fef-a730-ce19a634e012&pf_rd_r=5RRV4R10XTB0QBGDXBWN&qid=1587697806&sr=1-1-32a32192-7547-4d9b-b4f8-fe31bfe05040&tag=reviewscom07-20','https://www.amazon.com/M-Audio-AIR-192-Studio-Grade-Instruments/dp/B07YYX7K6R/ref=sr_1_35?dchild=1&keywords=audio+interface&qid=1587954760&sr=8-35')

messages = ''

if len(discounts) >0:
    for i in discounts:
        m = ' Today\'s price for {aa} is {a}. This is less than yesterday\'s price of {b}. The high is {c} and the low is {d}'.format(aa = i[5], a = i[1], b = i[4], c  = i[2] , d = i[3])
        messages +=m
    pushbullet_message('Lower Price Alert(s)!', messages)

