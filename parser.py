from pyparsing import *
import sqlite3

# connect to sqlite
con = sqlite3.connect('soccer.db')

# create the cursor
cur = con.cursor()


def execute_query(query):
    result_list = []
    cur.execute(query)
    result = cur.fetchall()
    for item in result:
        result_list.append(item[0])
    return result_list


def retrieve_cols(table_name):
    name_list = []
    cols = cur.execute(f'PRAGMA table_info({table_name})')
    cols = cur.fetchall()
    for index in range(0, len(cols)):
        # pull the column names
        col_name = cols[index][1]
        # add the column names to the list
        name_list.append(col_name)
    return name_list


def check_where_query():
    pass


def parse(user_input):
    location_words = ['matches', 'games']
    all_tables = ['matches', 'games', 'player', 'team', 'venue', 'city']
    # this pulls the column names with some extra non-useful data
    match_cols = retrieve_cols('matches')
    player_cols = retrieve_cols('player')
    team_cols = retrieve_cols('team')
    venue_cols = retrieve_cols('venue')
    city_cols = retrieve_cols('city')
    all_cols = match_cols + player_cols + team_cols + venue_cols + city_cols
    # create a list of possible locations for the cities or venues
    cities = execute_query("SELECT city FROM city")
    venues = execute_query("SELECT venue_name FROM venue")

    player_countries = execute_query("SELECT name FROM team where name not null")
    player_clubs = execute_query("SELECT playing_club FROM player where playing_club NOT null")
    all_player_teams = player_clubs + player_countries
    locations = cities + venues
    positions = execute_query("SELECT posi_to_play FROM player")
    match_no = execute_query("SELECT match_no FROM matches")

    # Keywords
    where_operator = CaselessLiteral("where")
    in_operator = CaselessLiteral("in")
    from_operator = CaselessLiteral("from")
    of_operator = CaselessLiteral("of")
    match_keyword = CaselessLiteral("matches")
    game_keyword = CaselessLiteral("games")
    venue_keyword = CaselessLiteral("venues")
    player_keyword = CaselessLiteral("players")
    team_keyword = CaselessLiteral("teams")
    play_keyword = CaselessLiteral("play in")
    word = Word(alphas)

    # define parser variables
    match_col = oneOf(match_cols, caseless=True)
    player_col = oneOf(player_cols, caseless=True)
    team_col = oneOf(team_cols, caseless=True)
    venue_col = oneOf(venue_cols, caseless=True)
    city_col = oneOf(city_cols, caseless=True)
    location = oneOf(locations, caseless=True)
    all_player_teams = oneOf(all_player_teams, caseless=True)
    all_tables = oneOf(all_tables, caseless=True)
    all_cols = oneOf(all_cols, caseless=True)
    positions = oneOf(positions, caseless=True)
    match_no = oneOf([str(match) for match in match_no])

    # define operators in grammar
    equals_operator = Literal("==")
    greater_operator = Literal(">")
    less_operator = Literal("<")
    and_operator = CaselessLiteral("and")
    of_operator = CaselessLiteral("of")
    or_operator = CaselessLiteral("or")
    comparison_operator = (greater_operator | less_operator | equals_operator)

    # create potential query expressions
    loc_exp = ((match_keyword | game_keyword | venue_keyword) + in_operator + location)("game_loc_exp")
    player_team_exp = (player_keyword + from_operator + all_player_teams)("player_team_exp")
    where_exp = (all_tables + where_operator + all_cols + comparison_operator + word)("where_exp")
    play_exp = ((player_keyword | team_keyword) + play_keyword + (location | positions | match_no))("play_exp")

    # create and_expr
    # expressions_list = [res_exp, sum_exp, pt_exp, loc_exp, snow_exp, typ_exp, diff_exp]
    # and_exp = (Or(expressions_list) + and_operator + Or(expressions_list))
    # or_exp = (Or(expressions_list) + or_operator + Or(expressions_list))

    expression = Forward()

    # expression definition (for grammar)
    expression << (loc_exp | player_team_exp | where_exp | play_exp)

    # accepts strings in language and returns the parsed input
    try:
        result = list(expression.parseString(user_input))
        if (user_input.lower() == "help"):
            return 1
        else:
            return result
    except Exception as e:
        return 0


res = parse('players play in GK')  # main program to call parser function and firestorm function
# def main():
#     intro = '''Dear beloved user,
#         I was built in order to help provide information on all ski resorts on the Ikon pass.
# Please excuse me if my information is not completely up to date; The data is a few years old.
# Regardless, I am overjoyed to provide my assistance. Please follow all of the syntax specifications provided below as I am very picky!
# HAPPY SEARCHING!\n'''
#
#     help_string = '''List of top level collection fields you may use in query:
#     - Location: returns all resorts in specified location
#     - Snowfall: returns all resorts with average seasonal snowfalls as specified (must be in a number in range 0-500 incrementing by 50)
#     - Resort:   returns all top level collection information on specified resort
#     - Summit:   returns all resorts with summit height as specified (must be in a number in range 1000-14000 incrementing by 100)
#
#
# List of sub collection fields you may use in query:
#     - Popular Trails of [resort]: returns the popular trails for a given resort if the sub collection
#                                   exists
#     - Type:                      returns top level collection information of resorts that contain
#                                   popular trails of specified trail type
#                                   (types include “Chute”, “Glades”, “Bumps”, and “Groomer”)
#     - Difficulties:              returns top level collection information of resorts with popular
#                                  trails of specified level of difficulty
#                                  (difficulties include “Beginner”, “Intermediate”, “Advanced”,
#                                   and “Expert”)
#
#
# - help (returns this menu of rules)
#
#
# List of operators available to use:
# ==, >, <, and, or
#
# Important Information:
#     - Commands must follow the following structure:
#       Field operator argument where argument can only be one of the specified words for each field. User
#       can also perform compound commands by combining commands defined above with ‘or’ or ‘and’.
#     - If the user asks for information about sub collection fields but does not include “Popular Trails”
#       in the command, it will return top level info with those types of trails
#     - Snowfall and Summit must be used with the greater than or less than operators. Popular Trails must
#       be used with ‘of’ along with a resort, while the remaining fields must be used with ==.
#
# Example searches could be:
#     - location == vermont and snowfall > 400
#     - type == chute
#     - Popular trails of Alta and difficulty == advanced
#     - Snowfall > 400 and Summit > 8000'''
#     print(intro)
#     print(help_string)
#     user_input = input("\nPlease enter your command: \n")
#
#     while user_input.lower() != 'quit':
#         parsed_input = parser(user_input)
#         if parsed_input == 1:
#             print(help_string)
#             user_input = input("\nPlease enter your command: \n")
#         elif parsed_input == 0:
#             print("Invalid input")
#             user_input = input("\nPlease enter your command: \n")
#         else:
#
#             # call the query program to filter parsed input and print the results
#             output = process_input(parsed_input)
#             output_list = []
#             # determine if th e output is a list or a stream of query results
#             if isinstance(output, list):
#                 output_list = output
#             else:
#                 for doc in output:
#                     output_list.append(doc.to_dict())
#             # add space between user input and output
#             print("\n")
#             # determine if the list is empty
#             if len(output_list) == 0:
#                 print("No information available")
#             # iterate through the output list
#             for dictionary in output_list:
#                 # iterate through the list to print the output
#                 for key, value in dictionary.items():
#                     print(f"{key}: {value}")
#                 print("---------------------------")
#
#             user_input = input("Please enter your command: \n")
#
#     print('Thank you!')
#
#
# main()
