import json

import requests
import csv
import time
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def scrapeCD(ID):

    CD_url_start = 'https://www.cdkeys.com/?q='
    CD_url_end = '&platforms=Steam'
    sub1 = "discount_final_price\">"
    sub2 = "</div></div></div>"
    CDPrice = 0
    SteamPrice = 0
    Titles = ['Name', 'Review Summary', 'Review Score', '# of Reviews',
              'Release Date', 'Type', 'Price']

    data_file = open('CDKeys_Wishlist.csv', 'w', encoding='utf-8')
    csv_writer = csv.writer(data_file)
    csv_writer.writerow(Titles)
    # open data file for writing CDKeys and Steam information

    print("\nWould you like results more or less accurate?\n"
          "Less accurate results may include games that CDKeys does not have,\n"
          "whereas more accurate will use the official Steam price if the game is not found.\n")
    accuracy = input("Type 0 for less accurate and 1 for more accurate: ")

    while (len(accuracy) != 1 or not accuracy.isdigit()) and (accuracy != 0 or accuracy != 1):
        accuracy = input("\nYour choice must be a 0 or 1 digit. Please try again: ")

    driver = webdriver.Chrome()
    # use webdriver bundled with script
    response = requests.get('https://store.steampowered.com/wishlist/profiles/' + ID + '/wishlistdata')
    json_response = response.json()

    for game in json_response:

        game_parsed = urllib.parse.quote(json_response.get(game).get('name').replace('™', '') + " PC")
        URL = CD_url_start + game_parsed + CD_url_end
        # convert Steam name into % URL format for CDKeys
        driver.get(URL)
        time.sleep(1)
        # result = driver.find_element("xpath", "//h3[contains(@itemprop,'name')]")
        try:
            result = driver.find_element("xpath", "//div[contains(@class,'price-wrapper')]")
            # if price-wrapper element was found (any result exists)
            if result is not None:
                # if there is a result on CDKeys for the game
                prices = result.text.splitlines()
                # double check if there is a sale price for the game
                if len(prices) > 0:
                    # print("Game: " + json_response.get(game).get('name') +
                    # " Sale Price: " + prices[0] + " Reg Price: " + prices[1])
                    list = [json_response.get(game).get('name').replace('™', ''), json_response.get(game).get('review_desc'),
                            json_response.get(game).get('reviews_percent'),
                            json_response.get(game).get('reviews_total'), json_response.get(game).get('release_string'),
                            json_response.get(game).get('type')]

                    # add Steam data to list

                    if not json_response.get(game).get('is_free_game'):
                        if accuracy == '0':
                            list.append(prices[0])
                            CDPrice += int(float(prices[0].replace("$", '')))
                            # if exact match was not found use the CDKeys top result (less accurate)
                        else:
                            try:
                                print("hello: " + accuracy)
                                # if exact match was not found, use Steam result (more accurate)
                                price = (str(json_response.get(game).get('subs')[0]))
                                idx1 = price.index(sub1)
                                idx2 = price.index(sub2)
                                res = '$'
                                for idx in range(idx1 + len(sub1) + 1, idx2):
                                    res = res + price[idx]
                                list.append(res)
                                CDPrice += int(float(res.replace("$", '')))
                            except IndexError:
                                list.append("N/A")
                    else:
                        # if it is a free game, use that result
                        list.append('$0.00')
                    print(list)
                    # print results for testing, replace with below
                    csv_writer.writerow(list)
                    # req = requests.get(URL)
                else:
                    # if price-wrapper for game has not been found, use Steam values
                    print("Price-wrapper not found")
                    list = [json_response.get(game).get('name').replace('™', ''), json_response.get(game).get('review_desc'),
                            json_response.get(game).get('reviews_percent'),
                            json_response.get(game).get('reviews_total'), json_response.get(game).get('release_string'),
                            json_response.get(game).get('type')]

                    # add Steam data to list

                    if not json_response.get(game).get('is_free_game'):
                        try:
                            price = (str(json_response.get(game).get('subs')[0]))
                            idx1 = price.index(sub1)
                            idx2 = price.index(sub2)
                            res = '$'
                            for idx in range(idx1 + len(sub1) + 1, idx2):
                                res = res + price[idx]
                            list.append(res)
                            CDPrice += int(float(res.replace("$", '')))
                        except IndexError:
                            list.append("N/A")
                    else:
                        # if it is a free game, use that result
                        list.append('$0.00')
                    print(list)
                    # print results for testing, replace with below
                    csv_writer.writerow(list)
                    # req = requests.get(URL)
            else:
                # only used in extreme scenarios where no game at all is found in CDKeys' database
                print("Game not found on CDKeys: " + json_response.get(game).get('name'))

        except NoSuchElementException:
            # if Selenium fails, notify user that data was not found
            print("Data not found for: " + json_response.get(game).get('name'))

    driver.close()
    data_file.close()