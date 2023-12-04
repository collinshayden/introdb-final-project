# Intro Databases Final Project
# Hayden Collins & Abbey Knobel
# Created on 2023/11/28

import sqlite3
from menu_options import *
import query_parser

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
        print(" (e) Query")
        print(" (f) Visualizations")
        print(" (h) Quit")
        option = input(" => ").lower()
        if option not in ["a", "b", "c", "d", "e", "f", "h"]:
            print("Invalid option.")

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
        visualizations(con)
    else:
        print("Quitting program.")
        return

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


def main():
    nav()
    con.close()


main()
