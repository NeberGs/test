from tokenize import String
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
import time
from auth_data import steam_password, login_steam,api_key,user_id
from data_item import data_item
import telegram
import lxml
import random


def get_SteamLoging(driver):
    driver.get('https://steamcommunity.com/market/')
    time.sleep(3)

    login_buton = driver.find_element_by_xpath('//*[@id="global_action_menu"]/a').click()
    time.sleep(3)
    login_input = driver.find_element_by_xpath('//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div/div/div[2]/div/form/div[1]/input')
    
    login_input.clear()
    login_input.send_keys(login_steam)
    time.sleep(0.5)

    password_input = driver.find_element_by_xpath('//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div/div/div[2]/div/form/div[2]/input')
    password_input.clear()
    password_input.send_keys(steam_password)
    time.sleep(0.5)
    sign_in = driver.find_element_by_xpath('//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div/div/div[2]/div/form/div[4]/button').click()
    time.sleep(3)
    # steam_from_email = driver.find_element_by_xpath('//*[@id="authcode"]')
    # steam_from_email.send_keys(str(input()))
    # submit = driver.find_element_by_xpath('//*[@id="auth_buttonset_entercode"]/div[1]').click()
    # steam_guard = driver.find_element_by_xpath('//*[@id="mainBody"]/div[1]/div/div/div/div[2]/form/div/div[2]/div')
    # steam_guard.send_keys(str(input()))
    print('Enter your code')
    code = list(str(input()))
    

    for num in range(1,6):
        col = num-1
        
        steam_guard = driver.find_element_by_xpath(f'//*[@id="responsive_page_template_content"]/div[1]/div[1]/div/div/div/div[2]/form/div/div[2]/div/input[{num}]')
        steam_guard.send_keys(code[col])
        time.sleep(0.5)
    
    
    time.sleep(3)
    
    #submit = driver.find_element_by_xpath('//*[@id="login_twofactorauth_buttonset_entercode"]/div[1]').click()
    time.sleep(3)

def navigate(driver, url,page_no):
    driver.get(url+str(page_no))

def get_data(page_data):
    soup = BeautifulSoup(page_data, 'html.parser')
    items = soup.find('div', id = 'searchResultsRows').find_all('div', class_ ='market_listing_row')
    all_data =[]
    for item in items:

        price = item.find('span', class_='market_listing_price market_listing_price_with_fee').text.strip()[:-1].replace(',','.')
        item_float = item.find('div', class_= 'market_listing_item_name_block').find('div', class_= 'float-div').find('div', class_= 'csgofloat-itemfloat').text[7:]
        seed = item.find('div', class_= 'market_listing_item_name_block').find('div', class_= 'float-div').find('div', class_= 'csgofloat-itemseed').text[12:]
        link = item.get('id')
        data = {
            'price' : price,
            'item_float' : item_float,
            'seed' : seed,
            'link' : link
        }
        all_data.append(data)
    return all_data

def get_seed_patern(data,data_from_item):
    
    for key,value in data_from_item['list_patern'].items():
        if (int(data['seed'])==key):
            if float(data['price'].replace(' ',''))<float(value-((value*40)/100)):
                link = data['link']
                price = data['price']
                data = {
                    'type' : f'seed_patern = {key},costs = {value}',
                    'link' : link,
                    'price' : price
                }
                return data
    
def get_float(data,data_from_item):
    
    if float(data['item_float'].split()[0])<=0.00999999999999:
        if float(data['price'].replace(' ',''))<float(data_from_item['range_price_float']):
            link = data['link']
            price = data['price']
            data = {
                'type' : 'float',
                'link' : link,
                'price' : price
            }
            return data

def data_analyse(sourse_data,data_from_item):
    links =[]
    
    for item_data in sourse_data:
        if item_data['item_float'] == '' or item_data['price'] =='Sold':
            print('data float failer')
            continue
        if data_from_item['type_scraping_weapon'] == 'Float':
            link = get_float(item_data,data_from_item)
            if link != None:
                links.append(link)
        elif data_from_item['type_scraping_weapon'] == 'Patern':
            link = get_seed_patern(item_data,data_from_item)
            if link != None:
                links.append(link)
        elif data_from_item['type_scraping_weapon'] == 'Float_and_Seed': 
            link1 = get_seed_patern(item_data,data_from_item)
            link2 = get_float(item_data,data_from_item)
            if link1 !=None:
                links.append(link1)
            elif link2 !=None:
                links.append(link2)
    return links
def buy_items(driver,link):
    find_elelment = driver.find_element_by_xpath(f'//*[@id="{link}"]/div[2]/div[1]/div/a').click()
    time.sleep(1)
    check_box = driver.find_element_by_xpath('//*[@id="market_buynow_dialog_accept_ssa"]')
    purchaise = driver.find_element_by_xpath('//*[@id="market_buynow_dialog_purchase"]/span')
    close = driver.find_element_by_xpath('//*[@id="market_buynow_dialog_close"]/span')
    if check_box.is_selected() == False:
        check_box.click()
        time.sleep(0.5)
        purchaise.click()
    elif check_box.is_selected() == False:
        purchaise.click()
    else:
        close.click()

        

def range_of_price(sourse_data,range_price):
    count = 0
    if len(sourse_data) < 5:
        return False
    for i in range(-1,3):
        if sourse_data[i]['price'].replace(' ','') == 'Sold':
            print('Some item sold')
            continue
        elif float(sourse_data[i]['price'].replace(' ',''))>float(range_price):
            count+=1
    if count >= 3 :
        return False

def main():
    bot = telegram.Bot(token=api_key)

    chrome_option = ChromeOptions()
    chrome_option.add_extension('csgofloat.crx')
    
    driver = webdriver.Chrome('./chromedriver', options=chrome_option)

    get_SteamLoging(driver)
    data_from_items = data_item
    print(data_item[0]['url'])
    while True:
        for data_from_item in data_from_items:
            url = data_from_item['url']
            try:
                if data_from_item['col']=='min':
                    num = 5
            except KeyError:
                num = 40

            for number in range(num):
                number*=100
                navigate(driver,url,number)
                time.sleep(random.randrange(5, 7))
                data_page = driver.page_source
                try:
                    parse_data = get_data(data_page)
                except AttributeError:
                    print('Pizda zalogalo')
                    time.sleep(15)
                    break
                
                parse_data = get_data(data_page)
                print(url+str(number))
                
                data = data_analyse(parse_data,data_from_item)
                for i in data :
                    link = str(i['link'])
                    price = str(i['price'])
                    type = str(i['type'])
                    messageW = f'{url}\nnumber = {number/100+1}\npriceItem = {price}\n{type}'
                    
                    bot.send_message(chat_id=user_id, text=messageW)
                    
                    buy_items(driver,link)
                    
                if(range_of_price(parse_data,data_from_item['range_price'])==False):
                
                    break
                else:
                    continue 
         

if __name__ == '__main__':
    main()