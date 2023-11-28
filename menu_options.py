# functions called from nav

from utils import *


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

    id_col_name = f'{selected_table}_id'
    id = input(f"Enter the {id_col_name} of the row to be removed: ")

    con.execute(f"DELETE FROM {selected_table} WHERE {id_col_name} = ?", (id,))

    con.commit()

    print("Success! Below is the updated table.")
    print_table(con, selected_table)

def modify(con):
    pass


def stats(con):
    print("Below is a list of all numerical columns.")
