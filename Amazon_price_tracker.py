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
from config import Amazon_urls

discounts = []

def Price_Tracker(urls):
    try:
        for url in urls:
            option = webdriver.ChromeOptions()
            option.add_argument("--incognito") # creates new instance of chrome in incognito mode
            browser = webdriver.Chrome(executable_path=r'C:\Users\bluep\chromedriver.exe', chrome_options=option) # PATH to chrome driver, r allows pc to read unicode
            browser.get(url)# url
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
            with open('price_data.txt', 'r') as file:
                price_dict = json.load(file)
            if name not in price_dict:
                price_dict[name] = [current_price]
                with open('price_data.txt', 'w') as file:
                    json.dump(price_dict, file)
                pushbullet_message('Setup Price Tracking for {item}'.format(item=name), 'Successfully setup price tracking for {item}'.format(item=name))
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
    except:
        pushbullet_message('Error in Amazon Price Tracker', "error in the program")


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
Price_Tracker(Amazon_urls)

messages = ''

if len(discounts) >0:
    for i in discounts:
        m = ' Today\'s price for {item} is {price}. This is less than yesterday\'s price of {yes_price}. The high is {high} and the low is {low}'.format(item = i[5], price = i[1], yes_price = i[4], high  = i[2] , low = i[3])
        messages +=m
    pushbullet_message('Lower Price Alert(s)!', messages)

