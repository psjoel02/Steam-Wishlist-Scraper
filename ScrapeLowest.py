import time
import urllib.parse
import edgedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import NoSuchElementException


def ScrapeCDKeys(CD_url_start, CD_url_end, CDPrice, game_name, driver, priceList):

    CD_URL = CD_url_start + urllib.parse.quote(str(game_name).upper() + " PC") + CD_url_end
    driver.get(CD_URL)
    time.sleep(3)
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
        print("\nCDKeys: $" + str(CDPrice))
        priceList.append(CDPrice)
    else:
        print("\nCDKeys: Not Found")

    return CDPrice


def ScrapeEneba(Eneba_url_start, EnebaPrice, game_parsed, driver, priceList):

    Eneba_URL = Eneba_url_start + game_parsed.upper()
    driver.get(Eneba_URL)
    time.sleep(3)

    try:
        driver.find_elements("xpath", "//button[contains(@class, 'pr0yIU')]")[1].click()
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
        print("Eneba: $" + str(EnebaPrice))
        priceList.append(EnebaPrice)
    else:
        print("Eneba: Not Found")

    return EnebaPrice


def ScrapeFanatical(Fan_url_start, Fan_url_end, FanPrice, game_parsed, driver, priceList):

    Fan_URL = Fan_url_start + game_parsed + Fan_url_end
    driver.get(Fan_URL)
    time.sleep(3)
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
        print("Fanatical: $" + str(FanPrice))
        priceList.append(FanPrice)
    else:
        print("Fanatical: Not Found")

    return FanPrice


def ScrapeGMG(GMG_url_start, GMG_url_end, game_parsed, driver, GMGPrice, priceList):

    GMG_URL = GMG_url_start + game_parsed + GMG_url_end
    driver.get(GMG_URL)
    time.sleep(3)
    result = None

    try:
        result = driver.find_element("xpath", "//div[contains(@class,'prices')]")
    except NoSuchElementException:
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
            GMGPrice += -1

    if GMGPrice > 0:
        print("Green Man Gaming: $" + str(GMGPrice))
        priceList.append(GMGPrice)
    else:
        print("Green Man Gaming: Not Found")

    return GMGPrice


def ScrapeSteam(Steam_url_start, chars, game_parsed, driver, SteamPrice, priceList):

    game_name = ''.join(filter(chars.__contains__, game_parsed)).replace('2', ' ')
    Steam_URL = Steam_url_start + game_name
    driver.get(Steam_URL)
    time.sleep(3)

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
        print("Steam: $" + str(SteamPrice))
        priceList.append(SteamPrice)
    else:
        print("Steam: Not Found")

    return SteamPrice


def ScrapeLowest():
    priceList = []

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

    edgedriver_autoinstaller.install()
    Edge_options = Options()
    Edge_options.add_argument("--window-size=1920,1080")
    Edge_options.add_argument("--disable-extensions")
    Edge_options.add_argument("--proxy-server='direct://'")
    Edge_options.add_argument("--proxy-bypass-list=*")
    Edge_options.add_argument("--start-maximized")
    Edge_options.add_argument('--headless')
    Edge_options.add_argument('--disable-gpu')
    Edge_options.add_argument('--disable-dev-shm-usage')
    Edge_options.add_argument('--no-sandbox')
    Edge_options.add_argument('--ignore-certificate-errors')
    Edge_options.add_argument('log-level=3')
    driver = webdriver.Edge(options=Edge_options)
    driver.get("http://www.python.org")
    assert "Python" in driver.title
    # use webdriver bundled with script

    chars = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789')
    game_name = input("Please enter the name of your game here: ")
    game_parsed = urllib.parse.quote(str(game_name).replace('™', '').replace('®', '').replace('&amp;', '&'))

    CDPrice = ScrapeCDKeys(CD_url_start, CD_url_end, CDPrice, game_name, driver, priceList)

    EnebaPrice = ScrapeEneba(Eneba_url_start, EnebaPrice, game_parsed, driver, priceList)

    FanPrice = ScrapeFanatical(Fan_url_start, Fan_url_end, FanPrice, game_parsed, driver, priceList)

    GMGPrice = ScrapeGMG(GMG_url_start, GMG_url_end, game_parsed, driver, GMGPrice, priceList)

    SteamPrice = ScrapeSteam(Steam_url_start, chars, game_parsed, driver, SteamPrice, priceList)

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

    driver.close()
