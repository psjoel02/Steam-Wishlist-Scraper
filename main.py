from ScrapeCD import scrapeCD


def getID():
    print("Welcome to the Steam Wishlist Calculator.\n\nThis program uses "
          "Steam's API and Selenium to scrape for the lowest and safest prices\n"
          "on the games in your Steam wishlist. This program does not obtain any\n"
          "of your personal information, only the data that is public in your wishlist.\n"
          "Therefore it requires your profile / wishlist data to be public.\n")
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
    isOfficial = input("\nWould you like to choose a 3rd party site or an official store?"
                       "\nType 0 for 3rd party and 1 for official: ")
    while (len(isOfficial) != 1 or not isOfficial.isdigit()) and (isOfficial != 0 or isOfficial != 1):
        isOfficial = input("\nYour choice must be a 0 or 1 digit. Please try again: ")

    return isOfficial


def main():
    # 76561198967647254

    steamID = getID()
    # get user's steam ID
    isOfficial = getOfficial()
    # get user's choice of official or unofficial store
    # A Chrome browser is required to use this application
    # add Eneba and Green Man Gaming options
    if isOfficial == 1:
        Official_Store = input("\nWould you like to get game data from Fanatical, Green Man Gaming, or Steam?"
                               "\n\nType 0 for Fanatical, 1 for Green Man Gaming, and 2 for Steam: ")

        while (len(Official_Store) != 1 or not Official_Store.isdigit()) and \
                (Official_Store != 0 or Official_Store != 1 or Official_Store != 2):
            Official_Store = input("\nYour choice must be a 0 or 1 digit. Please try again: ")

        if Official_Store == 1:
            print("Green Man Gaming")
        elif Official_Store == 2:
            print("Fanatical")
        else:
            print("Steam")
        # if user selected official(1), scrape Fanatical or Green Man Gaming for Data

    else:
        Unofficial_Store = input("\nWould you like to get game data from CDKeys or Eneba?"
                                 "\nCDKeys is more official but has a smaller selection and a higher price, whereas"
                                 "\nEneba is entirely 3rd-party, but has nearly every game at a lower price."
                                 "\n\nType 0 for CDKeys and 1 for Eneba: ")

        while (len(Unofficial_Store) != 1 or not Unofficial_Store.isdigit()) and \
                (Unofficial_Store != 0 or Unofficial_Store != 1):
            Unofficial_Store = input("\nYour choice must be a 0 or 1 digit. Please try again: ")

        if Unofficial_Store == 1:
            print("Eneba here")
        else:
            scrapeCD(steamID)
        # if user selected unofficial(0), scrape CDKeys or Eneba for data
        # CDKeys has a smaller offering of games than Eneba, but it is safer...


if __name__ == "__main__":
    main()
