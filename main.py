from ScrapeCD import ScrapeCD
from ScrapeEneba import ScrapeEneba
from ScrapeFan import ScrapeFan
from ScrapeLowest import ScrapeLowest
from SteamData import SteamData
from ScrapeGMG import ScrapeGMG

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


def getOfficial():
    isOfficial = input("\nWould you like to choose a 3rd party site, and official store, or the lowest price?"
                       "\nType 0 for 3rd party, 1 for official, and 2 for the lowest price: ")
    while (len(isOfficial) != 1 or not isOfficial.isdigit()) and (isOfficial != 0 or isOfficial != 1 or isOfficial != 2):
        isOfficial = input("\nYour choice must be a 0, 1, or 2 digit. Please try again: ")

    return isOfficial


def main():
    Restart = '0'
    while Restart == '0':

        isOfficial = getOfficial()
        # get user's choice of official store, unofficial store, or lowest price
        # get user's steam ID
        # An Edge browser is required to use this application
        if isOfficial == '1':
            steamID = getID()
            Official_Store = input("\nWould you like to get game data from Fanatical, Green Man Gaming, or Steam?"
                                   "\n\nType 0 for Fanatical, 1 for Green Man Gaming, and 2 for Steam: ")

            while (len(Official_Store) != 1 or not Official_Store.isdigit()) and \
                    (Official_Store != 0 or Official_Store != 1 or Official_Store != 2):
                Official_Store = input("\nYour choice must be a 0 or 1 digit. Please try again: ")

            if Official_Store == '0':
                ScrapeFan(steamID)
            elif Official_Store == '1':
                ScrapeGMG(steamID)
            else:
                SteamData(steamID)
            # if user selected official(1), scrape Fanatical, Green Man Gaming, or Steam for Data

        elif isOfficial == '0':
            steamID = getID()
            Unofficial_Store = input("\nWould you like to get game data from CDKeys or Eneba?"
                                     "\nCDKeys is more official but has a smaller selection and a higher price, whereas"
                                     "\nEneba is entirely 3rd-party, but has nearly every game at a lower price."
                                     "\n\nType 0 for CDKeys and 1 for Eneba: ")

            while (len(Unofficial_Store) != 1 or not Unofficial_Store.isdigit()) and \
                    (Unofficial_Store != 0 or Unofficial_Store != 1):
                Unofficial_Store = input("\nYour choice must be a 0 or 1 digit. Please try again: ")

            if Unofficial_Store == '1':
                ScrapeEneba(steamID)
            else:
                ScrapeCD(steamID)
            # if user selected unofficial(0), scrape CDKeys or Eneba for data
            # CDKeys has a smaller offering of games than Eneba, but it is safer

        else:
            ScrapeLowest()
        Restart = input("Would you like to find wishlist data again? Press 0 to continue or anything else to exit: ")


if __name__ == "__main__":
    main()

