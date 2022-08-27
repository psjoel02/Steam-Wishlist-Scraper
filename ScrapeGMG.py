import time
import requests
import csv
import urllib.parse
from selenium.common.exceptions import NoSuchElementException
from SteamData import getSteamPrice, useDriver, getGameList


def ScrapeGMG(ID):
    GMG_url_start = 'https://www.greenmangaming.com/search?query='
    GMG_url_end = '&drm=Steam'
    sub1 = "discount_final_price\">"
    sub2 = "</div></div></div>"
    GMGPrice = 0.0
    WishlistAvailable = 1
    exact_name = ''
    Titles = ['Name', 'Review Summary', 'Review Score', '# of Reviews',
              'Release Date', 'Type', 'Price']

    data_file = open('GreenManGaming_Wishlist.csv', 'w', encoding='utf-8')
    csv_writer = csv.writer(data_file)
    csv_writer.writerow(Titles)
    # open data file for writing Green Man Gaming and Steam information

    print("\nWould you like results more or less accurate?\n"
          "Less accurate results may include games that Green Man Gaming does not have,\n"
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
            URL = GMG_url_start + game_parsed + GMG_url_end
            driver.get(URL)
            time.sleep(3)
            # time sleep required over implicitly wait because GMG is heavy and takes time to load
        except AttributeError:
            print("Wishlist data could not be found. Double check that your wishlist is public."
                  "\nLink for Steam's wishlist support: "
                  "https://help.steampowered.com/en/faqs/view/0CAD-3B4D-B874-A065#wl-whosee")
            WishlistAvailable = 0
            driver.close()
            break

        # convert Steam name into % URL format for Green Man Gaming
        if WishlistAvailable == 1:
            try:
                gameFound = driver.find_element("xpath", "//span[contains(@class,'ais-RefinementList-count')]").text
                gameFound = int(gameFound)
                if gameFound > 9000:
                    exact_name = 'DNE'
                    # no results found
                else:
                    exact_name = driver.find_element("xpath", "//p[contains(@class,'prod-name')]")
            except NoSuchElementException:
                exact_name = 'DNE'
            except IndexError:
                exact_name = 'DNE'
            except ValueError:
                exact_name = 'DNE'
            try:
                result = driver.find_element("xpath", "//div[contains(@class,'prices')]")
                # if current-price element was found (any result exists)
                if result is not None and WishlistAvailable == 1 and exact_name != 'DNE':
                    # if there is a result on Green Man Gaming for the game
                    # double check if there is a sale price for the game
                    if accuracy == '0':
                        # if user selected lower accuracy (if result on Green Man Gaming exists)
                        gameList = getGameList(json_response, game)
                        # add Steam data to list
                        if not json_response.get(game).get('is_free_game'):
                            try:
                                prices = result.text
                                prices = prices.split("\n", 2)[2].replace("$", '')
                                GMGPrice += float(prices.replace("$", ''))
                                gameList.append(prices)
                            except IndexError:
                                if result.text.__contains__("\n") and result.text != '':
                                    GMGPrice += float(result.text.replace("$", ''))
                                    gameList.append(result.text)
                                else:
                                    GMGPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)

                        else:
                            # if it is a free game, use that result
                            gameList.append('$0.00')
                        # print results for testing, replace with below
                        csv_writer.writerow(gameList)
                        # req = requests.get(URL)
                    else:
                        # if user selected higher accuracy (only exact matches on Green Man Gaming)
                        gameList = getGameList(json_response, game)

                        # add Steam data to list
                        if not json_response.get(game).get('is_free_game'):
                            # if exact substring was found in the most relevant result
                            if json_response.get(game).get('name').upper().replace('™', '').replace('®', '') \
                                    .replace("&amp;", '&') in exact_name.text and exact_name.text != 'DNE':
                                try:
                                    prices = result.text
                                    prices = prices.split("\n", 2)[2].replace("$", '')
                                    GMGPrice += float(prices.replace("$", ''))
                                    gameList.append(prices)
                                except IndexError:
                                    if result.text.__contains__("\n") and result.text != '':
                                        GMGPrice += float(result.text.replace("$", ''))
                                        gameList.append(result.text)
                                    else:
                                        GMGPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                            else:
                                GMGPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                        else:
                            # if it is a free game, use that result
                            gameList.append('$0.00')
                        # print(list)
                        # print results for testing, replace with below
                        csv_writer.writerow(gameList)
                        # req = requests.get(URL)
                else:
                    # if game has not been found in GreenManGaming
                    gameList = getGameList(json_response, game)
                    GMGPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                    csv_writer.writerow(gameList)

            except NoSuchElementException:
                # if Selenium fails, notify user that data was not found
                if WishlistAvailable == 1:
                    gameList = getGameList(json_response, game)
                    # add Steam data to list
                    if not json_response.get(game).get('is_free_game'):
                        GMGPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                    else:
                        # if it is a free game, use that result
                        gameList.append('$0.00')
                    csv_writer.writerow(gameList)
        else:
            break

    if WishlistAvailable == 1:
        TotalList = ['Total:', '', '', '', '', '', '$' + str("{:.2f}".format(GMGPrice))]
        csv_writer.writerow('')
        csv_writer.writerow(TotalList)
        driver.close()
        data_file.close()

        print("\nData from Green Man Gaming was entered in the GreenManGaming_Wishlist.csv file"
              "\nYour total from Green Man Gaming is: $" + str("{:.2f}".format(GMGPrice)))
