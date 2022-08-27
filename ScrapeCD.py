import time
import requests
import csv
import urllib.parse
from selenium.common.exceptions import NoSuchElementException
from SteamData import getSteamPrice, useDriver, getGameList


def ScrapeCD(ID):

    CD_url_start = 'https://www.cdkeys.com/?q='
    CD_url_end = '&platforms=Steam'
    sub1 = "discount_final_price\">"
    sub2 = "</div></div></div>"
    CDPrice = 0.0
    WishlistAvailable = 1
    Titles = ['Name', 'Review Summary', 'Review Score', '# of Reviews',
              'Release Date', 'Type', 'Price']

    data_file = open('CDKeys_Wishlist.csv', 'w', encoding='utf-8')
    csv_writer = csv.writer(data_file)
    csv_writer.writerow(Titles)
    # open data file for writing CDKeys and Steam information

    print("\nWould you like results more or less accurate?\n"
          "Less accurate results may include games that CDKeys does not have,\n"
          "whereas more accurate will use the official Steam price if the exact game is not found.\n")
    accuracy = input("Type 0 for less accurate and 1 for more accurate: ")

    while (len(accuracy) != 1 or not accuracy.isdigit()) and (accuracy != 0 or accuracy != 1):
        accuracy = input("\nYour choice must be a 0 or 1 digit. Please try again: ")

    driver = useDriver()
    # use webdriver bundled with script from SteamData

    response = requests.get('https://store.steampowered.com/wishlist/profiles/' + ID + '/wishlistdata')
    json_response = response.json()

    for game in json_response:
        try:
            game_parsed = urllib.parse.quote(
                    json_response.get(game).get('name').replace('™', '').replace('®', '').replace('&amp;', '&') + " PC")
            URL = CD_url_start + game_parsed + CD_url_end
            driver.get(URL)
            driver.implicitly_wait(3)
        except AttributeError:
            print("Wishlist data could not be found. Double check that your wishlist is public."
                  "\nLink for Steam's wishlist support: "
                  "https://help.steampowered.com/en/faqs/view/0CAD-3B4D-B874-A065#wl-whosee")
            WishlistAvailable = 0
            driver.close()
            break

        # convert Steam name into % URL format for CDKeys
        if WishlistAvailable == 1:
            try:
                exact_name = driver.find_element("xpath", "//h3[contains(@itemprop,'name')]")
            except NoSuchElementException:
                exact_name = 'DNE'
            try:
                result = driver.find_element("xpath", "//div[contains(@class,'price-wrapper')]")
                # if price-wrapper element was found (any result exists)
                if result is not None and WishlistAvailable == 1:
                    # if there is a result on CDKeys for the game
                    prices = result.text.splitlines()
                    # double check if there is a sale price for the game
                    if accuracy == '0':
                        # if user selected lower accuracy (if result on CDKeys exists)
                        gameList = getGameList(json_response, game)

                        # add Steam data to list
                        if not json_response.get(game).get('is_free_game'):
                            try:
                                CDPrice += float(prices[0].replace("$", ''))
                                gameList.append(prices[0])
                                # initially try CDKeys results
                            except IndexError:
                                try:
                                    result = driver.find_elements("xpath", "//div[contains(@itemprop, 'offers')]")
                                    # try second method to find game price
                                    try:
                                        CDPrice += float(result[1].text.split("\n", 1)[0].replace("$", ''))
                                        gameList.append(result[1].text.split("\n", 1)[0])
                                    except ValueError:
                                        CDPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                                    except IndexError:
                                        CDPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                                except NoSuchElementException:
                                    CDPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                        else:
                            # if it is a free game, use that result
                            gameList.append('$0.00')
                        # print results for testing, replace with below
                        csv_writer.writerow(gameList)
                        # req = requests.get(URL)
                    else:
                        # if user selected higher accuracy (only exact matches on CDKeys)
                        gameList = getGameList(json_response, game)

                        # add Steam data to list
                        if not json_response.get(game).get('is_free_game'):
                            # if exact substring was found in the most relevant result
                            if json_response.get(game).get('name').upper().replace('™', '').replace('®', '').replace(
                                    "&amp;", '&') in exact_name.text and exact_name.text != 'DNE':
                                try:
                                    CDPrice += float(prices[0].replace("$", ''))
                                    gameList.append(prices[0])
                                    # initially try CDKeys results
                                except IndexError:
                                    # try second method to find game price
                                    try:
                                        result = driver.find_elements("xpath", "//div[contains(@itemprop, 'offers')]")
                                        try:
                                            CDPrice += float(result[1].text.split("\n", 1)[0].replace("$", ''))
                                            gameList.append(result[1].text.split("\n", 1)[0])
                                        except IndexError:
                                            gameList.append("N/A")
                                    except NoSuchElementException:
                                        CDPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                            else:
                                CDPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                        else:
                            # if it is a free game, use that result
                            gameList.append('$0.00')
                        # print(list)
                        # print results for testing, replace with below
                        csv_writer.writerow(gameList)
                        # req = requests.get(URL)
                else:
                    gameList = getGameList(json_response, game)
                    CDPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                    csv_writer.writerow(gameList)

            except NoSuchElementException:
                # if Selenium fails, notify user that data was not found
                if WishlistAvailable == 1:
                    gameList = getGameList(json_response, game)
                    # add Steam data to list
                    if not json_response.get(game).get('is_free_game'):
                        CDPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                    else:
                        # if it is a free game, use that result
                        gameList.append('$0.00')
                    csv_writer.writerow(gameList)
        else:
            break

    if WishlistAvailable == 1:
        TotalList = ['Total:', '', '', '', '', '', '$' + str("{:.2f}".format(CDPrice))]
        csv_writer.writerow('')
        csv_writer.writerow(TotalList)
        driver.close()
        data_file.close()

        print("\nData from CDKeys was entered in the CDKeys_Wishlist.csv file"
              "\nYour total from CDKeys is: $" + str("{:.2f}".format(CDPrice)))
