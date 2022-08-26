import requests
import csv
import edgedriver_autoinstaller
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.edge.options import Options


def getGameList(json_response, game):
    gameList = [
        json_response.get(game).get('name').replace('™', '').replace('®', '').replace('&amp;', '&').title(),
        json_response.get(game).get('review_desc'),
        str(json_response.get(game).get('reviews_percent')) + "%",
        json_response.get(game).get('reviews_total'),
        json_response.get(game).get('release_string'),
        json_response.get(game).get('type')]

    return gameList


def getSteamPrice(json_response, game, sub1, sub2, gameList):
    scrape_price = 0
    try:
        # if exact match was not found use Steam result (more accurate)
        price = (str(json_response.get(game).get('subs')[0]))
        idx1 = price.index(sub1)
        idx2 = price.index(sub2)
        res = '$'
        for idx in range(idx1 + len(sub1) + 1, idx2):
            res = res + price[idx]
        gameList.append(res)
        scrape_price += float(res.replace("$", ''))
    except IndexError:
        # if no steam price is available it has not been released
        gameList.append("N/A")
    return scrape_price


def useDriver():
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
    Edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    Edge_options.add_argument('log-level=3')
    driver = webdriver.Edge(options=Edge_options)
    driver.get("http://www.python.org")
    assert "Python" in driver.title
    return driver


def SteamData(ID):
    sub1 = "discount_final_price\">"
    sub2 = "</div></div></div>"
    SteamPrice = 0.0
    WishlistAvailable = 1
    Titles = ['Name', 'Review Summary', 'Review Score', '# of Reviews',
              'Release Date', 'Type', 'Price']

    data_file = open('Steam_Wishlist.csv', 'w', encoding='utf-8')
    csv_writer = csv.writer(data_file)
    csv_writer.writerow(Titles)
    # open data file for writing Steam information

    response = requests.get('https://store.steampowered.com/wishlist/profiles/' + ID + '/wishlistdata')
    json_response = response.json()

    for game in json_response:

        try:
            json_response.get(game).get('name')
        except AttributeError:
            print("Wishlist data could not be found. Double check that your wishlist is public."
                  "\nLink for Steam's wishlist support: "
                  "https://help.steampowered.com/en/faqs/view/0CAD-3B4D-B874-A065#wl-whosee")
            WishlistAvailable = 0

        try:
            if WishlistAvailable == 1:

                gameList = getGameList(json_response, game)
                if not json_response.get(game).get('is_free_game'):
                    SteamPrice += getSteamPrice(json_response, game, sub1, sub2, gameList)
                else:
                    # if it is a free game, use that result
                    gameList.append('$0.00')
                # print(list)
                # print results for testing, replace with below
                csv_writer.writerow(gameList)
                # req = requests.get(URL)

        except NoSuchElementException:
            if WishlistAvailable == 1:
                print("Data not found for: " + json_response.get(game).get('name'))

    if WishlistAvailable == 1:
        TotalList = ['Total:', '', '', '', '', '', '$' + str("{:.2f}".format(SteamPrice))]
        csv_writer.writerow('')
        csv_writer.writerow(TotalList)
        data_file.close()

        print("\nData from Steam was entered in the Steam_Wishlist.csv file"
              "\nYour total from Steam is: $" + str("{:.2f}".format(SteamPrice)))
