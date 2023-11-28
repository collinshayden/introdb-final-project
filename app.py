# Hayden Collins & Abbey Knobel
# Created on 2023/11/28

import sqlite3
import parser


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
        add()
    elif option == "b":
        remove()
    elif option == "c":
        modify()
    elif option == "d":
        stats()
    else:
        "Quitting program."


def add():
    pass


def remove():
    pass


def modify():
    pass


def stats():
    print("Below is a list of all numerical columns.")


