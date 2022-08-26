import csv
import urllib.parse
import requests
from selenium.common.exceptions import NoSuchElementException
from SteamData import useDriver, getGameList, getSteamPrice


def getID():
    print("Welcome to the Steam Key Wishlist Calculator.\n\nThis program uses "
          "Steam's API and Selenium to scrape for the lowest and safest prices\n"
          "on the games in your Steam wishlist. This program does not obtain any\n"
          "of your personal information, only the data that is public in your wishlist.\n"
          "Therefore it requires your profile / wishlist data to be set to public.\n")
    print("Please enter your Steam ID. It can be found using this link: "
          "https://www.businessinsider.com/how-to-find-steam-id")
    steamID = input("Steam ID: ")

    while len(steamID) != 17 or not steamID.isdigit():
        print("\nYour Steam ID must be 17 characters long. It is entirely "
              "comprised of digits,\nand it can be found using this link: "
              "https://www.businessinsider.com/how-to-find-steam-id")
        steamID = input("Steam ID: ")

    return steamID


def ScrapeCDKeys(CD_url_start, CD_url_end, CDPrice, game_name, driver, priceList):
    CD_URL = CD_url_start + urllib.parse.quote(str(game_name).upper() + " PC") + CD_url_end
    driver.get(CD_URL)
    driver.implicitly_wait(3)
    result = driver.find_element("xpath", "//div[contains(@class,'price-wrapper')]")

    if result is not None:
        prices = result.text.splitlines()
        try:
            CDPrice += float(prices[0].replace("$", ''))
        except IndexError:
            try:
                result = driver.find_elements("xpath", "//div[contains(@itemprop, 'offers')]")
                try:
                    CDPrice += float(result[1].text.split("\n", 1)[0].replace("$", ''))
                except IndexError:
                    CDPrice += -1
                except ValueError:
                    CDPrice += 1
            except NoSuchElementException:
                CDPrice += -1
    else:
        CDPrice += -1

    if CDPrice > 0:
        priceList.append(CDPrice)

    return CDPrice


def ScrapeEneba(Eneba_url_start, EnebaPrice, game_parsed, driver, priceList, numTimes):
    Eneba_URL = Eneba_url_start + game_parsed.upper()
    driver.get(Eneba_URL)
    driver.implicitly_wait(3)

    try:
        if numTimes == '0':
            driver.find_elements("xpath", "//button[contains(@class, 'pr0yIU')]")[1].click()
            # dont cause exception due to clicking US conversion button when scraping wishlist
        result = driver.find_element("xpath", "//span[contains(@class,'L5ErLT')]")
        if result is not None:
            prices = result.text.splitlines()
            try:
                EnebaPrice += float(prices[0].replace("$", ''))
            except IndexError:
                EnebaPrice += -1
        else:
            EnebaPrice += -1
    except NoSuchElementException:
        EnebaPrice += -1

    if EnebaPrice > 0:
        priceList.append(EnebaPrice)
    else:
        print("Eneba: Not Found")

    return EnebaPrice


def ScrapeFanatical(Fan_url_start, Fan_url_end, FanPrice, game_parsed, driver, priceList):
    Fan_URL = Fan_url_start + game_parsed + Fan_url_end
    driver.get(Fan_URL)
    driver.implicitly_wait(3)
    result = driver.find_elements("xpath", "//span[contains(@class,'card-price')]")
    prices = ''

    for x in result:
        if "$" in x.text:
            prices = x.text
            break
    if result is not None:
        try:
            FanPrice += float(prices.replace("$", ''))
        except ValueError:
            FanPrice += -1
    else:
        FanPrice += -1

    if FanPrice > 0:
        priceList.append(FanPrice)
    else:
        print("Fanatical: Not Found")

    return FanPrice


def ScrapeGMG(GMG_url_start, GMG_url_end, game_parsed, driver, GMGPrice, priceList):
    GMG_URL = GMG_url_start + game_parsed + GMG_url_end
    driver.get(GMG_URL)
    driver.implicitly_wait(3)

    try:
        result = driver.find_element("xpath", "//div[contains(@class,'prices')]")
        try:
            if result is not None:
                prices = result.text
                prices = prices.split("\n", 2)[2].replace("$", '')
                if float(prices) > 0.0:
                    GMGPrice += float(prices)
                else:
                    GMGPrice += -1
            else:
                GMGPrice += -1
        except IndexError:
            if not result.text.__contains__("\n") and result.text != '':
                GMGPrice += float(result.text.replace("$", ''))
            else:
                GMGPrice += -1
    except NoSuchElementException:
        GMGPrice += -1

    if GMGPrice > 0:
        priceList.append(GMGPrice)

    return GMGPrice


def ScrapeSteam(Steam_url_start, chars, game_parsed, driver, SteamPrice, priceList):
    game_name = ''.join(filter(chars.__contains__, game_parsed)).replace('2', ' ')
    Steam_URL = Steam_url_start + game_name
    driver.get(Steam_URL)
    driver.implicitly_wait(3)

    try:
        result = driver.find_element("xpath", "//div[contains(@class, 'col search_price  responsive_secondrow')]")
        if result is not None:
            try:
                SteamPrice += float(result.text.replace("$", ''))
            except ValueError:
                SteamPrice += -1
        else:
            SteamPrice += -1
    except NoSuchElementException:
        SteamPrice += -1

    if SteamPrice > 0:
        priceList.append(SteamPrice)
    else:
        print("Steam: Not Found")

    return SteamPrice


def ScrapeLowest():
    numTimes = '0'
    priceList = []
    chars = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789')

    CD_url_start = 'https://www.cdkeys.com/?q='
    CD_url_end = '&platforms=Steam'
    CDPrice = 0.0

    Eneba_url_start = 'https://www.eneba.com/us/store?&platforms[]=STEAM&text='
    EnebaPrice = 0.0

    Fan_url_start = 'https://www.fanatical.com/en/search?search='
    Fan_url_end = '&drm=steam'
    FanPrice = 0.0

    GMG_url_start = 'https://www.greenmangaming.com/search?query='
    GMG_url_end = '&drm=Steam'
    GMGPrice = 0.0

    Steam_url_start = 'https://store.steampowered.com/search/?term='
    SteamPrice = 0.0

    print("\nWould you like to scrape for the lowest price for one game across"
          "\nCDKeys, Eneba, Fanatical, GMG, and Steam, or your entire wishlist?\n")
    selection = input("Type 0 for one game and 1 for your wishlist: ")

    while (len(selection) != 1 or not selection.isdigit()) and (selection != 0 or selection != 1):
        selection = input("\nYour choice must be a 0 or 1 digit. Please try again: ")

    # use webdriver bundled with script from SteamData
    if selection == '0':

        game_name = input("\nPlease enter the name of your game here: ")
        game_parsed = urllib.parse.quote(str(game_name).replace('™', '').replace('®', '').replace('&amp;', '&'))

        driver = useDriver()

        CDPrice = ScrapeCDKeys(CD_url_start, CD_url_end, CDPrice, game_name, driver, priceList)
        if CDPrice > 0:
            print("\nCDKeys: $" + "{:.2f}".format(CDPrice))
        else:
            print("\nCDKeys: Not Found")

        EnebaPrice = ScrapeEneba(Eneba_url_start, EnebaPrice, game_parsed, driver, priceList, numTimes)
        if EnebaPrice > 0:
            print("Eneba: $" + "{:.2f}".format(EnebaPrice))
        else:
            print("Eneba: Not Found")

        FanPrice = ScrapeFanatical(Fan_url_start, Fan_url_end, FanPrice, game_parsed, driver, priceList)
        if FanPrice > 0:
            print("Fanatical: $" + "{:.2f}".format(FanPrice))
        else:
            print("Fanatical: Not Found")

        GMGPrice = ScrapeGMG(GMG_url_start, GMG_url_end, game_parsed, driver, GMGPrice, priceList)
        if GMGPrice > 0:
            print("Green Man Gaming: $" + "{:.2f}".format(GMGPrice))
        else:
            print("Green Man Gaming: Not Found")

        SteamPrice = ScrapeSteam(Steam_url_start, chars, game_parsed, driver, SteamPrice, priceList)
        if SteamPrice > 0:
            print("Steam: $" + "{:.2f}".format(SteamPrice))
        else:
            print("Steam: Not Found")

        numTimes = '1'
        lowest = min(priceList)

        if float(lowest) == float(CDPrice):
            print("\nCDKeys has the lowest price for " + game_name + " at $" + "{:.2f}".format(lowest))
        elif float(lowest) == float(EnebaPrice):
            print("\nEneba has the lowest price for " + game_name + " at $" + "{:.2f}".format(lowest))
        elif float(lowest) == float(FanPrice):
            print("\nFanatical has the lowest price for " + game_name + " at $" + "{:.2f}".format(lowest))
        elif float(lowest) == float(GMGPrice):
            print("\nGreen Man Gaming has the lowest price for " + game_name + " at $" + "{:.2f}".format(lowest))
        elif float(lowest) == float(SteamPrice):
            print("\nSteam has the lowest price for " + game_name + " at $" + "{:.2f}".format(lowest))
        else:
            print("\nError, no lowest value found.")
        # no switch in Python
    else:
        ScrapeAll(CD_url_start, CD_url_end, Eneba_url_start, Fan_url_start, Fan_url_end, GMG_url_start,
                  GMG_url_end, numTimes)


def ScrapeAll(CD_url_start, CD_url_end, Eneba_url_start, Fan_url_start, Fan_url_end, GMG_url_start,
              GMG_url_end, numTimes):
    sub1 = "discount_final_price\">"
    sub2 = "</div></div></div>"
    WishlistAvailable = 1
    Titles = ['Name', 'Review Summary', 'Review Score', '# of Reviews',
              'Release Date', 'Type', 'Price', 'Store']

    data_file = open('Lowest_Wishlist.csv', 'w', encoding='utf-8')
    csv_writer = csv.writer(data_file)
    csv_writer.writerow(Titles)
    # open data file for writing Steam information
    TotalPrice = 0.0
    lowest = 0.0
    driver = useDriver()
    # use webdriver bundled with script from SteamData

    print("Please enter your Steam ID. It can be found using this link: "
          "https://www.businessinsider.com/how-to-find-steam-id")
    steamID = input("Steam ID: ")

    while len(steamID) != 17 or not steamID.isdigit():
        print("\nYour Steam ID must be 17 characters long. It is entirely "
              "comprised of digits,\nand it can be found using this link: "
              "https://www.businessinsider.com/how-to-find-steam-id")
        steamID = input("Steam ID: ")

    response = requests.get('https://store.steampowered.com/wishlist/profiles/' + steamID + '/wishlistdata')
    json_response = response.json()

    for game in json_response:

        CDPrice = 0.0
        EnebaPrice = 0.0
        FanPrice = 0.0
        GMGPrice = 0.0
        SteamPrice = 0.0

        try:
            json_response.get(game).get('name')
        except AttributeError:
            print("Wishlist data could not be found. Double check that your wishlist is public."
                  "\nLink for Steam's wishlist support: "
                  "https://help.steampowered.com/en/faqs/view/0CAD-3B4D-B874-A065#wl-whosee")
            driver.close()
            WishlistAvailable = 0
            break

        if WishlistAvailable == 1:
            priceList = []
            game_parsed = \
                urllib.parse.quote(
                    str(json_response.get(game).get('name')).replace('™', '').replace('®', '').replace('&amp;', '&'))
            game_name = str(json_response.get(game).get('name')).replace('™', '').replace('®', '').replace('&amp;', '&')

            gameList = getGameList(json_response, game)

            CDPrice = ScrapeCDKeys(CD_url_start, CD_url_end, CDPrice, game_name, driver, priceList)
            EnebaPrice = ScrapeEneba(Eneba_url_start, EnebaPrice, game_parsed, driver, priceList, numTimes)
            FanPrice = ScrapeFanatical(Fan_url_start, Fan_url_end, FanPrice, game_parsed, driver, priceList)
            GMGPrice = ScrapeGMG(GMG_url_start, GMG_url_end, game_parsed, driver, GMGPrice, priceList)
            SteamPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)

            numTimes = '2'
            lowest = min(priceList)

            if float(lowest) == float(CDPrice):
                gameList.append(CDPrice)
                TotalPrice += float(str(CDPrice).replace("$", ''))

            elif float(lowest) == float(EnebaPrice):
                gameList.append(EnebaPrice)
                TotalPrice += float(str(EnebaPrice).replace("$", ''))

            elif float(lowest) == float(FanPrice):
                gameList.append(FanPrice)
                TotalPrice += float(str(FanPrice).replace("$", ''))

            elif float(lowest) == float(GMGPrice):
                gameList.append(GMGPrice)
                TotalPrice += float(str(GMGPrice).replace("$", ''))

            elif float(lowest) == float(SteamPrice):
                gameList.append(SteamPrice)
                TotalPrice += float(str(SteamPrice).replace("$", ''))

            else:
                print("\nError, no lowest value found.")
                gameList.append("N/A")

            csv_writer.writerow(gameList)

    if WishlistAvailable == 1:
        TotalList = ['Total:', '', '', '', '', '', '$' + str("{:.2f}".format(TotalPrice))]
        csv_writer.writerow('')
        csv_writer.writerow(TotalList)
        driver.close()
        data_file.close()

        print("\nLowest data from all five sites was entered in the Lowest_Wishlist.csv file"
              "\nYour total from every site is: $" + str("{:.2f}".format(TotalPrice)))
