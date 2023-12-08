# functions called from nav

from utils import *
from query_parser import *
from query_parser import get_query
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np


def add(con):
    selected_table, table_names = select_table(con)

    print(f"You selected to add to '{selected_table}'")
    if selected_table == "city":
        city_id = input("Enter the city id: ")
        city_name = input("Enter the city name: ")
        con.execute("INSERT INTO city ('city_id', 'city_name') VALUES (?, ?)", (city_id, city_name))

    elif selected_table == "venue":
        venue_id = input("Enter the venue id: ")
        venue_name = input("Enter the venue name: ")
        city_id = input("Enter the city id: ")
        con.execute("INSERT INTO venue ('venue_id', 'venue_name', 'city_id') VALUES (?, ?, ?)",
                    (venue_id, venue_name, city_id))

    elif selected_table == "team":
        team_id = input("Enter the team_id: ")
        team_name = input("Enter the team name: ")
        team_group = input("Enter the team group: ")
        won = input("Enter # of games won: ")
        lost = input("Enter # of games lost: ")
        draw = input("Enter # of games drawn: ")
        goal_for = input("Enter # of goals scored by the team: ")
        goal_agnst = input("Enter # of goals scored against the team: ")
        goal_diff = input("Enter the goal differential for the team: ")
        points = input("Enter the # of points: ")

        con.execute("INSERT INTO team "
                    "('team_id', 'team_name', 'team_group', 'won', 'lost', 'draw', 'goal_for', 'goal_agnst', 'goal_diff', 'points') "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (team_id, team_name, team_group, won, lost, draw, goal_for, goal_agnst, goal_diff, points))

    elif selected_table == "match":
        match_id = input("Enter the match number: ")
        play_stage = input("Enter the play stage: ")
        play_date = input("Enter the date of the match: ")
        venue_id = input("Enter the venue_id: ")
        audience = input("Enter the audience size: ")
        team1_id = input("Enter the the first team id: ")
        team2_id = input("Enter the the second team id: ")
        team1_goals = input("Enter the the first team's goal #: ")
        team2_goals = input("Enter the the second team's goal #: ")
        team1_result = input("Enter the the first team's result: ")
        team2_result = input("Enter the the second team's result: ")

        con.execute("INSERT INTO match "
                    "('match_id', 'play_stage', 'play_date', 'venue_id', 'audience', 'team1_id', 'team2_id', "
                    "'team1_goals', 'team2_goals', 'team1_result', 'team2_result') "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                        match_id, play_stage, play_date, venue_id, audience, team1_id, team2_id, team1_goals,
                        team2_goals, team1_result, team2_result))

    elif selected_table == "player":
        player_id = input("Enter the player id: ")
        team_id = input("Enter the team id: ")
        player_name = input("Enter the player's name: ")
        posi_to_play = input("Enter the player's position: ")
        age = input("Enter the player's age: ")
        playing_club = input("Enter the player's club: ")

        con.execute("INSERT INTO player "
                    "('player_id', 'team_id', 'player_name', 'posi_to_play', 'age', 'playing_club') "
                    "VALUES (?, ?, ?, ?, ?, ?)", (player_id, team_id, player_name, posi_to_play, age, playing_club))

    con.commit()  # saving the changes to the db file

    print("Success! Below is the updated table.")
    print_table(con, selected_table)


def remove(con):
    selected_table, table_names = select_table(con)
    print(f"You selected to remove from '{selected_table}'")
    print(f"\nThese are the current entries in the {selected_table} table: \n")
    print_table(con, selected_table)

    primary_key = f'{selected_table}_id'
    id = input(f"Enter the {primary_key} of the row to be removed: ")

    con.execute(f"DELETE FROM {selected_table} WHERE {primary_key} = ?", (id,))

    con.commit()

    print("Success! Below is the updated table.")
    print_table(con, selected_table)


def modify(con):
    selected_table, table_names = select_table(con)
    print(f"You selected to modify a row from '{selected_table}'")
    print(f"\nThese are the current entries in the {selected_table} table: \n")
    print_table(con, selected_table)

    primary_key = f'{selected_table}_id'
    valid_key = False

    while not valid_key:
        id = input(f"Enter the {primary_key} of the row to be modified: ")

        cursor = con.cursor()
        cursor.execute(f"SELECT * FROM {selected_table} WHERE {primary_key} = ?", (id,))
        row = cursor.fetchone()  # Fetch a single row
        if row:
            print(row)
            valid_key = True
        else:
            print("No matching row found, please try again")

    print("Here is a list of columns names:")
    columns = get_column_names(con, selected_table)
    print(columns)
    selected_column = ""
    while selected_column not in columns:
        selected_column = input("Enter the column name that you would like to modify: ").lower()
        if selected_column not in columns:
            print("Invalid selection.")

    new_value = input("Enter the new value you would like to set: ")
    con.execute(f"UPDATE {selected_table} SET {selected_column} = ? WHERE {primary_key} = ?", (new_value, id))
    con.commit()

    print("Success! Below is the updated table.")
    print_table(con, selected_table)


def stats(con):
    operations = ["min", "max", "std", "median", "avg"]
    print("Below is a list of all numerical columns paired with their respective tables.")
    column_table_pairs = get_numeric_columns(con)
    print("\nTable Name - Column Name")
    for column, table in column_table_pairs.items():
        print(f"{table} - {column}")

    selected_column = ""
    while selected_column not in column_table_pairs.keys():
        selected_column = input("Enter a column name: ").lower()
        if selected_column not in column_table_pairs.keys():
            print("Invalid selection.")
    selected_table = column_table_pairs[selected_column]

    print(f"You selected {selected_column}.")
    print("Below are available the operations:")
    print(operations)
    selected_operation = ""
    while selected_operation not in operations:
        selected_operation = input("Choose an operation to perform: ").lower()
        if selected_operation not in operations:
            print("Invalid selection.")

    if selected_operation == "min":
        cursor = con.cursor()
        cursor.execute(f"SELECT MIN({selected_column}) FROM {selected_table}")
        min_value = cursor.fetchone()[0]
        print(f"The minimum value in {selected_column} is {min_value}")
    elif selected_operation == "max":
        cursor = con.cursor()
        cursor.execute(f"SELECT MAX({selected_column}) FROM {selected_table}")
        max_value = cursor.fetchone()[0]
        print(f"The maximum value in {selected_column} is {max_value}")
    elif selected_operation == "std":
        std = calculate_stats(con, selected_column, selected_table, selected_operation)
        print(f"The standard deviation of {selected_column} is {std:.2f}")
    elif selected_operation == "median":
        median = calculate_stats(con, selected_column, selected_table, selected_operation)
        print(f"The mean {selected_column} is {median:.2f}")
    elif selected_operation == "avg":
        mean = calculate_stats(con, selected_column, selected_table, selected_operation)
        print(f"The mean {selected_column} is {mean:.2f}")


def query_help():
    print("This program allows you to make various queries to our database which contains information about soccer "
          "games. Some example queries are listed below: ")
    print("1. games won by [player_name/team_name]\n"
          "2. position of [player_name]\n"
          "3. total players of [team_name]\n"
          "4. total [audience/goals for/matches/wins/losses] of [player_name/team_name]\n"
          "5. win percentage of [team_name]\n"
          "6. players from [team_name]\n"
          "7. players with age < 20\n"
          "8. players with position = [position]\n"
          "9. players play in [position]\n"
          "10. teams with [wins/losses] > [n]\n"
          "11. players with [wins/losses] > [n]\n"
          "12. [players/teams] play in [city]\n"
          "13. [players/teams] play in [venue]\n"
          "14. venues in [city]\n"
          "15. matches in [city/venue]\n"
          "16. players play in [match_id]\n"
          "17. teams with points > [n]\n")


def query(con):
    query_help()
    try:
        query_statement = get_query()
        print_query(con, query_statement)
    except Exception as e:
        print("Invalid query, try again: ")
        query_statement = get_query()
        print_query(con, query_statement)

def show_table(con):
    table, table_names = select_table(con)
    print_table(con, table)
def visualizations(cur):
    #prompt user
    user_choice = input("Please select one of the following statistics to visualize.\n"
                        "a. All goals scored for/against every team\n"
                        "b. Number of total players in each position\n"
                        "c. Win percentage of each team\n"
                        "d. Audience of each game played by a team\n"
                        "e. Number of wins for each team\n")

    while user_choice not in ['a', 'b', 'c', 'd', "e"]:
        user_choice = input("Invalid selection please select a letter a-e: ")  # get a list of teams
    teams = execute_query("SELECT team_name FROM team")

    if user_choice == 'a':
        # get all of the teams goals for and against
        goals = cur.execute("SELECT team_name, goal_for, goal_agnst FROM team")
        goals = cur.fetchall()
        # pull the data and put it into lists for plotting
        team_names = []
        goals_for = []
        goals_against = []
        for team in goals:
            team_names.append(team[0][:4])
            goals_for.append(team[1])
            goals_against.append(team[2])
        x_axis = np.arange(0, len(team_names))
        plt.bar(x_axis - 0.2, goals_for, 0.4, label = "Goals For" )
        plt.bar(x_axis +0.2, goals_against, 0.4, label = "Goals Against" )
        plt.xticks(x_axis, team_names)
        plt.xlabel("Team")
        plt.ylabel("Number of Goals")
        plt.title("Number of Goals Score For/Against Each Team")
        plt.legend()

    elif user_choice == 'b':
        cur.execute("SELECT posi_to_play, count(*) as position_count from player group by posi_to_play")
        positions = cur.fetchall()
        pos = []
        nums = []
        for position in positions:
            pos.append(position[0])
            nums.append(position[1])
        x_axis = np.arange(0, len(positions))
        plt.bar(x_axis, nums, 0.6)
        plt.xticks(x_axis, pos)
        plt.xlabel("Position")
        plt.ylabel("Number of Players")
        plt.title("Total Number of Players in Each Position")

    elif user_choice == 'c':
        win_percentages = []
        names = []
        for team_name in teams:
            wp = cur.execute(f'''SELECT (SUM (CASE 
            WHEN matches.team1_id = team.team_id  and matches.team1_result = "W" THEN 1.0
            WHEN matches.team2_id = team.team_id and matches.team2_result = "W" THEN 1.0
            ELSE 0 END) / COUNT(*) * 100) as win_percentage FROM team JOIN matches 
            ON team.team_id = matches.team1_id OR team.team_id = matches.team2_id
            WHERE team.team_name = "{team_name}" GROUP BY team.team_name''')
            wp = cur.fetchall()
            win_percentages.append(wp[0][0])
            names.append(team_name[:3])
        x_axis = np.arange(0, len(win_percentages))
        plt.bar(x_axis, win_percentages, 0.8)
        plt.xticks(x_axis, names)
        plt.xlabel("Team")
        plt.ylabel("Win Percentage")
        plt.title("Win Percentage for Each Team")

    elif user_choice == "d":
        total_aud = []
        names = []
        for team_name in teams:
            aud = cur.execute(f'''SELECT sum(audience) FROM team join matches on matches.team1_id = team.team_id 
            or matches.team2_id = team.team_id where team_name = "{team_name}" ''')
            names.append(team_name[:3])
            aud = cur.fetchall()
            total_aud.append(aud[0][0])
        x_axis = np.arange(0, len(total_aud))
        plt.bar(x_axis, total_aud, 0.8)
        plt.xticks(x_axis, names)
        plt.xlabel("Team")
        plt.ylabel("Total Audience")
        plt.title("Total Audience of Each Team")
    elif user_choice == "e":
        cur.execute(f'''SELECT wins as "# wins", count(wins)  as "# teams" FROM team group by wins''')
        res = cur.fetchall()
        team_with_scores = [row[1] for row in res]
        colors = plt.get_cmap('Blues')(np.linspace(0.2, 0.7, len(team_with_scores)))
        fig, ax = plt.subplots()
        ax.pie(team_with_scores, colors=colors, radius=3, center=(4, 4),
               wedgeprops={"linewidth": 1, "edgecolor": "white"}, frame=True, )
        plt.legend(title='# of wins / # of teams', labels=res, loc='upper right')
        plt.title("Teams grouped by # of wins")
    plt.tight_layout()
    plt.show(block=False)
