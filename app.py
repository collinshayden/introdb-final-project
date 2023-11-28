# Intro Databases Final Project
# Hayden Collins & Abbey Knobel
# Created on 2023/11/28

import sqlite3
from menu_options import *
import parser

con = sqlite3.connect("soccer.db")


def nav():
    print(f"\nWelcome!")
    option = ""
    while option not in ["a", "b", "c", "d", "e"]:
        print("Choose an option: ")
        print(" (a) Add")
        print(" (b) Remove")
        print(" (c) Modify")
        print(" (d) Stats")
        print(" (e) Quit")
        option = input(" => ").lower()
        if option not in ["a", "b", "c", "d", "e"]:
            print("Invalid option.")

    if option == "a":
        add(con)
    elif option == "b":
        remove()
    elif option == "c":
        modify()
    elif option == "d":
        stats()
    else:
        "Quitting program."


def main():
    nav()


main()
