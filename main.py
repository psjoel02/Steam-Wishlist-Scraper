import json

import requests
import csv
import time
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def scrapeCD(ID):

    # 76561198967647254
    CD_url_start = 'https://www.cdkeys.com/?q='
    CD_url_end = '&platforms=Steam'
    driver = webdriver.Chrome('C:/Users/Joel/Downloads/chromedriver_win32/chromedriver.exe')

    response = requests.get('https://store.steampowered.com/wishlist/profiles/' + ID + '/wishlistdata')
    json_response = response.json()
    for game in json_response:
        # print(json_response.get(game).get('name').replace('™', ''))

        game_parsed = urllib.parse.quote(json_response.get(game).get('name').replace('™', '') + " PC")
        URL = CD_url_start + game_parsed + CD_url_end

        driver.get(URL)
        time.sleep(0.2)

        try:
            result = driver.find_element("xpath", "//div[contains(@class,'price-wrapper')]")
            if result is not None:
                prices = result.text.splitlines()
                if len(prices) > 1:
                    print("Game: " + json_response.get(game).get('name') +
                          " Sale Price: " + prices[0] + " Reg Price: " + prices[1])
                    # req = requests.get(URL)
            else:
                print("Name: " + json_response.get(game).get('name') + " Sale Price: " + prices[0])
        except NoSuchElementException:
            print("Data not found for: " + json_response.get(game).get('name'))


    driver.close()


    data_file = open('wishlist_data.csv', 'w')
    csv_writer = csv.writer(data_file)

    data_file.close()



def main():

    steamID = ''

    print("Welcome to the Steam Wishlist Calculator. \nThis program uses "
          "Steam's API and Selenium to scrape for the lowest and safest prices\n"
          "on the games in your Steam wishlist.\n")
    print("Please enter your Steam ID. It can be found using this link: "
          "https://www.businessinsider.com/how-to-find-steam-id")
    steamID = input("Steam ID: ")

    while len(steamID) != 17 or not steamID.isdigit():
        print("\nYour Steam ID must be 17 characters long. It is entirely "
              "comprised of digits,\nand it can be found using this link: "
              "https://www.businessinsider.com/how-to-find-steam-id")
        steamID = input("Steam ID: ")

    print("Would you like to scrape from CDKeys or Fanatical")
    scrapeCD(steamID)


if __name__ == "__main__":
    main()
