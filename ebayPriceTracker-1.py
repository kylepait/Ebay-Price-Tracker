
from bs4 import BeautifulSoup
import requests 
import numpy as np
import csv
from datetime import datetime

from twilio.rest import Client

LINK = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=p4432023.m570.l1312&_nkw=pokemon+black+2+CIB&_sacat=0"


def get_prices_by_link(link):
    # get source
    r = requests.get(link)
    # parse source
    page_parse = BeautifulSoup(r.text, 'html.parser')
    # find all list items from search results
    search_results = page_parse.find("ul",{"class":"srp-results"}).find_all("li",{"class":"s-item"})

    item_prices = []

    for result in search_results:
        price_as_text = result.find("span",{"class":"s-item__price"}).text
        if "to" in price_as_text:
            continue
        price = float(price_as_text[1:].replace(",",""))
        item_prices.append(price)
    return item_prices

def remove_outliers(prices, m=2):
    data = np.array(prices)
    return data[abs(data - np.mean(data)) < m * np.std(data)]

def get_average(prices):
    return np.mean(prices)

def save_to_file(prices):
    fields=[datetime.today().strftime("%B-%D-%Y"),np.around(get_average(prices),2)]
    with open('prices.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fields)
    
    send_text_message(f'New entry added:\nTimestamp: {datetime.today()}\nAverage Price: {get_average(prices)}')


def send_text_message(message):
    # Replace these values with your Twilio account SID, auth token, Twilio phone number, and your phone number
    account_sid = 'ACdcfcbe5482cb9aa111341a21f25bd4df'
    auth_token = 'ae051fd1e696b90db34b3cfea7c56bef'
    from_phone_number = '+18555030489'
    to_phone_number = '+17576513018'

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_=from_phone_number,
        to=to_phone_number
    )

    print(f"Text message sent with SID: {message.sid}")

if __name__ == "__main__":
    prices = get_prices_by_link(LINK)
    prices_without_outliers = remove_outliers(prices)
    print(get_average(prices_without_outliers))
    save_to_file(prices_without_outliers)