from pyparsing import *
import sqlite3

#connect to sqlite
con = sqlite3.connect('soccer.db')

#create the cursor 
cur = con.cursor() 

replacement_dictionary = {'goals for': 'goal_for', 'goals against':'goal_agnst',
                          'points':'pts','position':'posi_to_play', 'group':'team_group' , 
                          'goal differential': 'goal_diff', 'group position':'group_position',
                          'venue' : 'venue_name' , 'city': 'city_name', 'name': 'name', 
                          'players': 'player', 'teams':'team', 'matches' : 'match',
                          'games': 'match', 'game' : 'match', 'venues': 'venue',
                          'cities': 'city', 'match id': 'match_id', 'venue id': 'venue_id',
                          }
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
    cols= cur.fetchall()
    for index in range(0,len(cols)):
        #pull the column names
        col_name = cols[index][1]
        #add the column names to the list
        name_list.append(col_name)
    return name_list

def get_col_type(table_names):
    col_type_dicts = {}
    for name in table_names:
        #get the type of each column
        cols = cur.execute(f'PRAGMA table_info({name})')
        cols= cur.fetchall()
        col_dicts = []
        for index in range(0, len(cols)):
            col_name = cols[index][1]
            col_dicts.append({col_name: cols[index][2]})
        col_type_dicts[name] = col_dicts
    return col_type_dicts

def with_query(query):
    #get the column name from the query
    query_sub = query[0]
    operator = query[3]
    query_column = query[2]
    query_value = query[4]
    if len(query) > 4 and query_column == "name":
        query_value = query[4] + ' ' + query[5]
    query_table = '' 
    
    if query_column in replacement_dictionary:
        query_column = replacement_dictionary[query_column]
        if query_column == "name":
            if query_sub in replacement_dictionary:
                query_column = replacement_dictionary[query_sub] + '_name'
                query_sub = replacement_dictionary[query_sub]
            else:
                query_column = query_sub + "_name"
    #get the column type for every column in every table
    cols = get_col_type(['match', 'player','city','team','venue'])
    #determine the value of the column the query is asking for 
    for table, table_cols in cols.items():
        for column_dict in table_cols:
            if query_column in list(column_dict.keys())[0]:
                typ = column_dict[query_column]
                query_table = table
                if (operator == "<"  or operator == ">") and (typ != "INTEGER"):
                    return []
                else:
                    return [query_sub, query_column, operator, query_value, query_table]
                
          
            



def parse(user_input):
    
    all_tables = ['matches', 'games', 'player','team','venue','city']
    total_cols = ['goals for', 'goals against', 'audience','points','players','matches','wins', 'draws', 'losses'] 
    
    col_names_readable = list(replacement_dictionary.keys())
    
    #this pulls the column names with some extra non-useful data 
    match_cols = retrieve_cols('matches')
    player_cols = retrieve_cols('player')
    team_cols = retrieve_cols('team')
    venue_cols = retrieve_cols('venue')
    city_cols = retrieve_cols('city')
    all_cols = match_cols + player_cols + team_cols + venue_cols + city_cols + col_names_readable
    
    #create a list of possible locations for the cities or venues 
    cities = execute_query("SELECT city_name FROM city")
    venues = execute_query("SELECT venue_name FROM venue")
    players_names = execute_query("SELECT player_name FROM player")
    player_countries = execute_query("SELECT team_name FROM team where team_name not null")
    player_clubs = execute_query("SELECT playing_club FROM player where playing_club NOT null")
    all_player_teams = player_clubs + player_countries
    locations = cities + venues
    plural_table_names = ['teams', 'players', 'matches', 'venues', 'cities' ]
    positions = execute_query("SELECT posi_to_play FROM player")
    match_no = execute_query("SELECT match_id FROM match")

    # Keywords
    with_operator = CaselessLiteral("with")
    in_operator = CaselessLiteral("in")
    from_operator = CaselessLiteral("from")
    of_operator = CaselessLiteral("of")
    match_keyword = CaselessLiteral("matches")
    game_keyword = CaselessLiteral("games")
    venue_keyword = CaselessLiteral("venues")
    player_keyword = CaselessLiteral("players")
    team_keyword = CaselessLiteral("teams")
    play_keyword = CaselessLiteral("play in")
    wp_keyword = CaselessLiteral("win percentage")
    total_keyword = CaselessLiteral("total")
    position_keyword = CaselessLiteral("position")
    word = Word(alphas)
    ints = Word(nums)
    
    

    # define parser variables
    player_names = oneOf(players_names, caseless = True)
    match_col = oneOf(match_cols, caseless = True)
    player_col = oneOf(player_cols, caseless = True)
    team_col = oneOf(team_cols, caseless = True)
    venue_col = oneOf(venue_cols, caseless = True)
    city_col = oneOf(city_cols, caseless = True)
    location = oneOf(locations, caseless=True)
    all_player_teams = oneOf(all_player_teams, caseless = True)
    all_tables = oneOf(all_tables, caseless = True)
    all_cols = oneOf(all_cols, caseless =  True)
    positions = oneOf(positions, caseless = True)
    total_cols = oneOf(total_cols, caseless = True)
    plural_table_names = oneOf(plural_table_names, caseless = True)
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
    loc_exp = ((match_keyword|game_keyword|venue_keyword) + in_operator + location)("loc_exp")
    player_team_exp = (player_keyword + from_operator + all_player_teams)("player_team_exp")
    with_exp = ((plural_table_names|all_tables) + with_operator + (all_cols) + comparison_operator + (word|ints))("with_exp") 
    play_exp = ((player_keyword|team_keyword) + play_keyword + (location|positions| match_no))("play_exp")
    wp_exp = (wp_keyword + of_operator + (all_player_teams|player_names))("wp_exp")
    position_exp =  (position_keyword + of_operator + player_names)("position_exp")
    total_exp = (total_keyword + total_cols + of_operator + (location|player_names|match_no|positions|all_player_teams))("total_exp")
    of_exp = (all_cols + of_operator + (all_tables|game_keyword))("of_exp")
    expression = Forward()

    # expression definition (for grammar)
    expression << (loc_exp | player_team_exp | with_exp | play_exp | wp_exp | total_exp | position_exp)

    # accepts strings in language and returns the parsed input
    try:
        result = list(expression.parseString(user_input))
        if (user_input.lower() == "help"):
            return 1
        else:
            return result
    except Exception as e:
        return 0


# print("LOCATION TESTING: ")
# print(parse('matches in Paris'))
# print(parse('games in Bordeaux'))
# print(parse('matches in US'))

# print("PLAYER TESTING: ")
# print(parse("players from USA"))
# print(parse("players from West Ham"))

# print("WITH TESTING")
# print(parse('games with goals for > 5'))
# print(parse("player WITH posi_to_play == GK"))
# print(parse("team with goal_agnst > 5"))
# print(parse("team with goals for > 5"))

# print("PLAY TESTING: ")
# print(parse("players play in Paris"))
# print(parse("teams play in 2"))
# print(parse("players play in GK"))

# print("WP TESTING: ")
# print(parse("win percentage of United States"))
# print(parse("win percentage of Lyon"))
# print(parse("win percentage of Aaron Hughes"))

# print("TOTAL TESTING: ")
# print(parse("total goals for of Lyon"))
# print(parse("total players of GK"))
# print(parse("total audience of Paris"))
# print(parse("total wins of Aaron Hughes"))
# print(parse("total hash of Argentina"))


def main():
    user_input = input("Please enter your query as described by the structure above: ")
    while parse(user_input) == 0:
        user_input = input("Invalid query. Please enter a query that matches the above instructions: ")
    parsed_input = parse(user_input)
    #difference in user input length and the parsed input length
    input_length_difference = len(user_input.split(' ')) - len(parsed_input)
    if input_length_difference > 0:
        parsed_input = parsed_input + user_input.split(' ')[-input_length_difference: ]
    if parsed_input[1] == 'with': 
        query_info = with_query(parsed_input)
        while(query_info == []):
            user_input = input("That is not a valid query for that information. Make sure you are using the correct operators. For queries about text columns be sure to use the == operator. Please enter another query: ")
            query_info = with_query(user_input)
    else: 
        query_info = user_input
    print(query_info)
main()
        
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
