from ScrapeCD import scrapeCD


def getID():
    print("Welcome to the Steam Wishlist Calculator.\n\nThis program uses "
          "Steam's API and Selenium to scrape for the lowest and safest prices\n"
          "on the games in your Steam wishlist. This program does not obtain any\n"
          "of your personal information, only the data that is public in your wishlist.\n")
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

    # add Eneba and Green Man Gaming options
    if isOfficial == 1:
        print("Exiting script...")
        # if user selected unofficial(0), scrape CDKeys or Eneba for data
        # CDKeys has a smaller offering of games than Eneba, but it is safer...
    else:
        scrapeCD(steamID)
        # if user selected official(1), scrape Fanatical or Green Man Gaming for Data


if __name__ == "__main__":
    main()
