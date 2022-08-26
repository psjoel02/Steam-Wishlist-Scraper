import time
import requests
import csv
import urllib.parse
from selenium.common.exceptions import NoSuchElementException
from SteamData import getSteamPrice, useDriver, getGameList


def ScrapeEneba(ID):
    Eneba_url_start = 'https://www.eneba.com/us/store?&platforms[]=STEAM&text='
    sub1 = "discount_final_price\">"
    sub2 = "</div></div></div>"
    EnebaPrice = 0.0
    WishlistAvailable = 1
    firstVisit = 0
    Titles = ['Name', 'Review Summary', 'Review Score', '# of Reviews',
              'Release Date', 'Type', 'Price']

    data_file = open('Eneba_Wishlist.csv', 'w', encoding='utf-8')
    csv_writer = csv.writer(data_file)
    csv_writer.writerow(Titles)
    # open data file for writing Eneba and Steam information

    print("\nWould you like results more or less accurate?\n"
          "Less accurate results may include games that Eneba does not have,\n"
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
                    json_response.get(game).get('name').replace('™', '').replace('®', '').replace('&amp;', '&'))
            URL = Eneba_url_start + game_parsed
            driver.get(URL)
            driver.implicitly_wait(3)
            if firstVisit == 0:
                driver.find_elements("xpath", "//button[contains(@class, 'pr0yIU')]")[1].click()
                firstVisit += 1
                # click on US element to change site to $
        except AttributeError:
            print("Wishlist data could not be found. Double check that your wishlist is public."
                  "\nLink for Steam's wishlist support: "
                  "https://help.steampowered.com/en/faqs/view/0CAD-3B4D-B874-A065#wl-whosee")
            WishlistAvailable = 0
            driver.close()
            break

        # convert Steam name into % URL format for Eneba
        if WishlistAvailable == 1:
            try:
                exact_name = driver.find_element("xpath", "//span[contains(@class,'YLosEL')]")
                # name of top result in Eneba
            except NoSuchElementException:
                exact_name = 'DNE'
            try:
                result = driver.find_element("xpath", "//span[contains(@class,'L5ErLT')]")
                # if price element was found (any result exists)
                if result is not None and WishlistAvailable == 1:
                    # if there is a result on Eneba for the game
                    prices = result.text.splitlines()
                    # double check if there is a sale price for the game
                    if accuracy == '0':
                        # if user selected lower accuracy (if result on Eneba exists)
                        gameList = getGameList(json_response, game)

                        # add Steam data to list
                        if not json_response.get(game).get('is_free_game'):
                            try:
                                gameList.append(prices[0])
                                EnebaPrice += float(prices[0].replace("$", ''))
                            except IndexError:
                                EnebaPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                        else:
                            # if it is a free game, use that result
                            gameList.append('$0.00')
                        # print results for testing, replace with below
                        csv_writer.writerow(gameList)
                        # req = requests.get(URL)
                    else:
                        # if user selected higher accuracy (only exact matches on Eneba)
                        gameList = getGameList(json_response, game)

                        # add Steam data to list
                        if not json_response.get(game).get('is_free_game'):
                            # if exact substring was found in the most relevant result
                            if json_response.get(game).get('name').replace('™', '').replace('®', '').replace('&amp;',
                                                                                                             '&') \
                                    in exact_name.text and exact_name.text != 'DNE':
                                try:
                                    gameList.append(prices[0])
                                    EnebaPrice += float(prices[0].replace("$", ''))
                                    # initially try Eneba results
                                except IndexError:
                                    gameList.append("N/A")
                            else:
                                EnebaPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                        else:
                            # if it is a free game, use that result
                            gameList.append('$0.00')
                        # print(list)
                        # print results for testing, replace with below
                        csv_writer.writerow(gameList)
                        # req = requests.get(URL)
                else:
                    gameList = getGameList(json_response, game)
                    EnebaPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                    csv_writer.writerow(gameList)

            except NoSuchElementException:
                # if Selenium fails, notify user that data was not found
                if WishlistAvailable == 1:
                    gameList = getGameList(json_response, game)
                    # add Steam data to list
                    if not json_response.get(game).get('is_free_game'):
                        EnebaPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                    else:
                        # if it is a free game, use that result
                        gameList.append('$0.00')
                    csv_writer.writerow(gameList)
        else:
            break

    if WishlistAvailable == 1:
        TotalList = ['Total:', '', '', '', '', '', '$' + str("{:.2f}".format(EnebaPrice))]
        csv_writer.writerow('')
        csv_writer.writerow(TotalList)
        driver.close()
        data_file.close()

        print("\nData from Eneba was entered in the Eneba_Wishlist.csv file"
              "\nYour total from Eneba is: $" + str("{:.2f}".format(EnebaPrice)))
