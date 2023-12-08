# Intro Databases Final Project
# Hayden Collins & Abbey Knobel
# Created on 2023/11/28

from menu_options import *

con = sqlite3.connect("soccer.db")
cur = con.cursor()


# function to display the nav
def nav():
    print(f"\nWelcome!")
    # user input to choose menu option
    option = ""
    while option not in ["a", "b", "c", "d", "e", "f", "h", "g"]:
        print("Choose an option: ")
        print(" (a) Add")
        print(" (b) Remove")
        print(" (c) Modify")
        print(" (d) Stats")
        print(" (e) Query")
        print(" (f) Visualizations")
        print(" (g) Show a Table")
        print(" (h) Quit")
        option = input(" => ").lower()
        if option not in ["a", "b", "c", "d", "e", "f", "h", "g"]:
            print("Invalid option.")

    # calling menu functions
    if option == "a":
        add(con)
    elif option == "b":
        remove(con)
    elif option == "c":
        modify(con)
    elif option == "d":
        stats(con)
    elif option == "e":
        query(con)
    elif option == "f":
        visualizations(cur)
    elif option == "g":
        show_table(con)
    else:
        print("Quitting program.")
        return

    # prompting user to return to nav or quit
    option = ""
    while option not in ["a", "b"]:
        print("\nChoose an option: ")
        print(" (a) Return to Nav")
        print(" (b) Quit")
        option = input(" => ").lower()
        if option not in ["a", "b"]:
            print("Invalid option.")
    if option == "a":
        nav()
    else:
        print("Quitting program.")
        return


# main function
def main():
    nav()
    con.close()


main()
