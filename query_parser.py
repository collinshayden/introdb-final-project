from pyparsing import *
import sqlite3

# connect to sqlite
con = sqlite3.connect('soccer.db')

# create the cursor
cur = con.cursor()
tables = ['matches', 'player', 'city', 'team', 'venue']
replacement_dictionary = {'goals for': 'goal_for', 'goals against': 'goal_agnst', 'position': 'posi_to_play',
                          'group': 'team_group', 'goal differential': 'goal_diff', 'group position': 'group_position',
                          'venue': 'venue_name', 'city': 'city_name', 'name': 'name', 'players': 'player',
                          'teams': 'team', 'match': 'matches', 'games': 'matches', 'game': 'matches', 'venues': 'venue',
                          'cities': 'city', 'match id': 'match_id', 'venue id': 'venue_id', 'match number': 'match_id',
                          'team group': 'team_group'}


#this executes an sql query and puts all results in a list
def execute_query(query):
    result_list = []
    cur.execute(query)
    result = cur.fetchall()
    for item in result:
        result_list.append(item[0])
    return result_list


# retrieved the column names from a table and adds them to a list
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


# gets the type of every column in all tables and puts it in a dictionary
def get_col_type(table_names):
    col_type_dicts = {}
    for name in table_names:
        # get the type of each column and name
        cols = cur.execute(f'PRAGMA table_info({name})')
        cols = cur.fetchall()
        col_dicts = []
        for index in range(0, len(cols)):
            # get the column name and append it the dictionary
            col_name = cols[index][1]
            col_dicts.append({col_name: cols[index][2]})
        col_type_dicts[name] = col_dicts
    return col_type_dicts


#this processes with queries like "players with age > 20"
def process_with_query(query):
    # get the query information
    query_sub_table = query[0]
    operator = query[3]
    query_column = query[2]
    query_value = query[4]
    # see if the query is a name with two words and concatenate the first and last name
    if len(query) > 5 and query_column == "name":
        query_value = query[4] + ' ' + query[5]

    # see if the query column is in the replacement dictionary and select the correct name variable based on table name
    if query_column in replacement_dictionary:
        query_column = replacement_dictionary[query_column]
        if query_column == "name":
            query_column = query_sub_table + "_name"
    # determine if the subject of the query is in the replacement dictionary (NO TABLES)
    if query_sub_table in replacement_dictionary and query_sub_table not in tables:
        query_sub_table = replacement_dictionary[query_sub_table]
    query_field_table, typ = get_query_type(query_column)
    # validate the type - we dont want > < for validating strings
    if (operator == "<" or operator == ">") and (typ != "INTEGER"):
        return ''
    # if the comparison operator is appropriate for the type of the field return the SQL statement
    else:
        # no need to have a join if these are the same
        if query_field_table == query_sub_table:
            return f'''SELECT "{query_field_table}_name" FROM {query_field_table} where {query_column} {operator} "{query_value}"'''
        else:
            # SQL - SELECT * from query_sub_table join query_field_table where query_column query_operator query_value
            return f'''SELECT "{query_sub_table}_name" FROM {query_sub_table} join {query_field_table} where {query_column} {operator} "{query_value}"'''


# function that gets the table and type of query column
def get_query_type(query_column):
    # get the column type for every column in every table
    cols = get_col_type(tables)
    # find which table and type the field being queried is
    for table, table_cols in cols.items():
        for column_dict in table_cols:
            if query_column == list(column_dict.keys())[0]:
                # get the type and table the query field is in
                typ = column_dict[query_column]
                query_table = table
    return [query_table, typ]


#processes win percentage queries for a player or team - "win percentage of France
def process_wp_query(query):
    players = execute_query("SELECT DISTINCT player_name from player")
    name = query[2]
    if name in players:
        return f'''SELECT (SUM (CASE 
        WHEN matches.team1_id = player.team_id  and matches.team1_result = "W" THEN 1.0
        WHEN matches.team2_id = player.team_id and matches.team2_result = "W" THEN 1.0
        ELSE 0 END) / COUNT(*) * 100) as win_percentage FROM player JOIN matches 
        ON player.team_id = matches.team1_id OR player.team_id = matches.team2_id
        WHERE player.player_name = "{name}" GROUP BY player.player_name '''
    else:
        return f'''SELECT (SUM (CASE 
        WHEN matches.team1_id = team.team_id  and matches.team1_result = "W" THEN 1.0
        WHEN matches.team2_id = team.team_id and matches.team2_result = "W" THEN 1.0
        ELSE 0 END) / COUNT(*) * 100) as win_percentage FROM team JOIN matches 
        ON team.team_id = matches.team1_id OR team.team_id = matches.team2_id
        WHERE team.team_name = "{name}" GROUP BY team.team_name '''

#processes results query - "games lost by France"
def process_res_query(query):
    subject = query[2]
    res = query[1]
    if res == 'won by':
        res = "W"
    elif res == "tied by":
        rse = "D"
    else:
        res = "L"
    teams = execute_query("SELECT team_name FROM team")
    players = execute_query("SELECT player_name FROM player")
    if subject in teams:
        return f'''SELECT matches.* FROM team JOIN matches ON team.team_id = matches.team1_id 
        OR team.team_id = matches.team2_id WHERE team.team_name = "{subject}"
        AND (matches.team1_id = team.team_id AND matches.team1_result = '{res}'
        OR matches.team2_id = team.team_id AND matches.team2_result = '{res}')'''
    else:
        return f''' SELECT matches.* FROM player JOIN matches ON player.team_id = matches.team1_id 
        OR player.team_id = matches.team2_id WHERE player.player_name = "{subject}"
        AND (matches.team1_id = player.team_id AND matches.team1_result = '{res}'
        OR matches.team2_id = player.team_id AND matches.team2_result = '{res}')'''

#processes location queries - "venues in france"
def process_location_query(query):
    # get query info
    query_sub = query[0]
    query_loc = query[2]
    # determine if the subject needs to be replaced - ie if the user input is plural
    if query_sub in replacement_dictionary and query_sub not in tables:
        query_sub = replacement_dictionary[query_sub]
    # determine the table which the user is inquiring
    if query_sub == 'game' or query_sub == 'matches':
        query_table = 'matches'
    else:
        query_table = 'venue'

    # SQL statement will be SELECT * FROM query_table join join_table where join_cond = query_loc
    if query_table == 'matches':
        return f'''select DISTINCT * from (venue join matches on matches.venue_id = venue.venue_id ) join city on venue.city_id = city.city_id where city_name = "{query_loc}" '''
    else:
        # venues
        return f'''SELECT DISTINCT venue_name FROM venue join city on venue.city_id=city.city_id where city.city_name="{query_loc}"; '''

#processes player queries - "players from France"
def process_player_query(query):
    player_name = query[0]
    player_team = query[2]
    sub_table = 'player'
    # determine if the team is a club team or national team
    club_teams = execute_query("SELECT distinct playing_club from player")
    if player_team in club_teams:
        join_table = ''
        col = 'playing_club'
    else:
        join_table = 'team'
        col = 'team_name'
    # SQL:
    # SELECT * from player where col = __________
    # SELECT * from player join team where col = _____________
    return f'''SELECT player_name FROM player join {join_table} where {col} = "{player_team}" '''


#processes play query - "players play in MF"
def process_play_query(query):
    # pull info from query
    query_sub = query[0]
    playing_pos = query[2]
    if query_sub in replacement_dictionary and query_sub not in tables:
        query_sub = replacement_dictionary[query_sub]
    # get a list of potential positions and cities and venues
    cities = execute_query("SELECT distinct city_name from city")
    positions = execute_query("SELECT distinct posi_to_play from player")
    venues = execute_query("SELECT distinct venue_name from venue")
    # create all possible options
    # if this is a match number
    if playing_pos.isdigit():
        if query_sub == 'player':
            return f'''SELECT player_name FROM player join matches on matches.team1_id = player.team_id or matches.team2_id = player.team_id where match_id = "{playing_pos}"'''
        if query_sub == 'team':
            return f'''SELECT * FROM team join matches on team.team_id = matches.team1_id or team.team_id = matches.team2_id where match_id = "{playing_pos}" '''
    # option 1 - player plays in a position
    # SELECT * FROM player where posi_to_play = playing_pos
    if query_sub == 'player':
        if playing_pos in positions:
            return f'''SELECT * FROM player where posi_to_play = "{playing_pos}"'''
        # option 2 - player plays in a venue
        # select * from (player join match) join venue where venue_name = playing_pos
        if playing_pos in venues:
            return f''' SELECT DISTINCT player_name FROM (player join matches) join venue where venue_name = "{playing_pos}"'''
        # option 3 - a player plays in a city
        # select * from ((player join match) join venue) join city where city_name = playing_pos
        if playing_pos in cities:
            return f'''SELECT DISTINCT player_name from ((player join matches) join venue) join city where city_name = "{playing_pos}"'''
    if query_sub == 'team':
        if playing_pos in venues:
            return f'''SELECT DISTINCT team_name from (team join matches) join venue where venue_name = "{playing_pos}"'''
        if playing_pos in cities:
            return f'''SELECT DISTINCT team_name from ((team join matches) join venue) join city where city_name = "{playing_pos}"'''

#processes position of play  "position of John Doe"
def process_position_query(query):
    name = query[2]
    return f'''SELECT posi_to_play from player where player_name = "{name}" '''

#processes totals - "total audience of France"
def process_total_query(query):
    teams = execute_query("SELECT team_name FROM team")
    players = execute_query("SELECT player_name FROM player")
    venues = execute_query("SELECT venue_name FROM venue")
    cities = execute_query("SELECT city_name FROM city")
    match_nums = execute_query("SELECT match_id FROM matches")
    match_nums = [str(match) for match in match_nums]

    positions = execute_query("SELECT DISTINCT posi_to_play FROM player")
    totaled = query[1]
    subject = query[3]
    if totaled in replacement_dictionary:
        totaled = replacement_dictionary[totaled]
    if subject in replacement_dictionary:
        subject = replacement_dictionary[subject]
    if totaled == 'audience':
        if subject in teams:
            return f'''SELECT sum(audience) FROM team join matches on matches.team1_id = team.team_id 
            or matches.team2_id = team.team_id where team_name = "{query[3]}" '''
        elif subject in players:
            return f'''SELECT sum(audience) FROM player join matches on matches.team1_id = player.team_id 
            or matches.team2_id = player.team_id where player_name = "{query[3]}" '''
        elif subject in venues:
            return f'''SELECT sum(audience) FROM (team join matches on matches.team1_id = team.team_id 
             or matches.team2_id = team.team_id) join venue on venue.venue_id = matches.venue_id
            where venue_name = "{query[3]}"'''
        elif subject in cities:
            return f'''SELECT sum(audience) FROM ((team join matches on matches.team1_id = team.team_id 
            or matches.team2_id = team.team_id) join venue on venue.venue_id = matches.venue_id) 
            join city on city.city_id = venue.city_id   where city_name = "{query[3]}"'''
        elif subject in match_nums:
            return f'''SELECT audience FROM matches where match_id = {query[3]}'''
        else:
            return ''

    elif totaled == "goal_for" or totaled == "goal_agnst":
        if subject in teams:
            return f'''SELECT {totaled} from team where team_name = "{subject}"'''
        if subject in players:
            return f'''SELECT  {totaled} from player join team on player.team_id = team.team_id 
            where player_name = "{subject}"'''

    elif totaled == 'player':
        if subject in teams:
            return f'''SELECT COUNT(player_name) AS player_count FROM player JOIN team 
            ON player.team_id = team.team_id WHERE team.team_name = "{subject}"
            GROUP BY team.team_name'''
        elif subject in positions:
            return f'''SELECT COUNT(player_name) AS player_count FROM player 
            WHERE posi_to_play = "{subject}" GROUP BY posi_to_play'''
        else:
            return ''
    elif totaled == 'matches':
        if subject in teams:
            return f'''SELECT COUNT(match_id) FROM team join matches on matches.team1_id = team.team_id 
            or matches.team2_id = team.team_id where team_name = "{subject}"'''
        elif subject in players:
            return f''' SELECT COUNT(match_id) FROM player join matches on 
            matches.team1_id = player.team_id or matches.team2_id = player.team_id 
            where player_name = "{subject}"'''
        else:
            return ''
    elif totaled == 'wins' or totaled == 'losses' or totaled == 'draws':
        if subject in teams:
            return f'''SELECT SUM({totaled}) AS win_count FROM team WHERE 
            team_name = "{subject}" GROUP BY team_name'''
        elif subject in players:
            return f'''SELECT sum({totaled}) FROM team join player on team.team_id = player.team_id
            WHERE player_name = "{subject}" GROUP BY player_name'''
        else:
            return ''
    else:
        return ''

#parses user input
def parse(user_input):
    #all of the columns in the db
    total_cols = ['goals for', 'goals against', 'audience', 'points', 'players', 'matches', 'wins', 'draws', 'losses']

    #all of the column namesthat are readable - a user can say "goals against" instead of goal_agnst
    col_names_readable = list(replacement_dictionary.keys())
    # this pulls the column names with some extra non-useful data
    match_cols = retrieve_cols('matches')
    player_cols = retrieve_cols('player')
    team_cols = retrieve_cols('team')
    venue_cols = retrieve_cols('venue')
    city_cols = retrieve_cols('city')
    all_cols = match_cols + player_cols + team_cols + venue_cols + city_cols + col_names_readable

    # create a list of possible locations for the cities or venues
    cities = execute_query("SELECT city_name FROM city")
    venues = execute_query("SELECT venue_name FROM venue")
    players_names = execute_query("SELECT player_name FROM player")
    player_countries = execute_query("SELECT team_name FROM team where team_name not null")
    player_clubs = execute_query("SELECT playing_club FROM player where playing_club NOT null")
    all_player_teams = player_clubs + player_countries
    locations = cities + venues
    results = ['won by', 'lost by', 'tied by']
    plural_table_names = ['teams', 'players', 'match', 'venues', 'cities']
    positions = execute_query("SELECT posi_to_play FROM player")
    match_no = execute_query("SELECT match_id FROM matches")

    # Keywords
    with_operator = CaselessLiteral("with")
    in_operator = CaselessLiteral("in")
    from_operator = CaselessLiteral("from")
    of_operator = CaselessLiteral("of")
    venue_keyword = CaselessLiteral("venues")
    play_keyword = CaselessLiteral("play in")
    wp_keyword = CaselessLiteral("win percentage")
    total_keyword = CaselessLiteral("total")
    position_keyword = CaselessLiteral("position")
    word = Word(alphas)
    ints = Word(nums)

    # define parser variables
    player_keyword = oneOf(['player', 'players'], caseless=True)
    match_keyword = oneOf(['match', 'matches', 'game', 'games'], caseless=True)
    team_keyword = oneOf(['team', 'teams'], caseless=True)
    results = oneOf(results, caseless=True)
    player_names = oneOf(players_names, caseless=True)
    match_col = oneOf(match_cols, caseless=True)
    player_col = oneOf(player_cols, caseless=True)
    team_col = oneOf(team_cols, caseless=True)
    venue_col = oneOf(venue_cols, caseless=True)
    city_col = oneOf(city_cols, caseless=True)
    location = oneOf(locations, caseless=True)
    all_player_teams = oneOf(all_player_teams, caseless=True)
    all_tables = oneOf(tables, caseless=True)
    all_cols = oneOf(all_cols, caseless=True)
    positions = oneOf(positions, caseless=True)
    total_cols = oneOf(total_cols, caseless=True)
    play_in = oneOf(['plays in', 'play in'], caseless=True)
    plural_table_names = oneOf(plural_table_names, caseless=True)
    match_no = oneOf([str(match) for match in match_no])

    # define operators in grammar
    equals_operator = Literal("=")
    greater_operator = Literal(">")
    less_operator = Literal("<")
    and_operator = CaselessLiteral("and")
    of_operator = CaselessLiteral("of")
    or_operator = CaselessLiteral("or")
    comparison_operator = (greater_operator | less_operator | equals_operator)

    # create potential query expressions
    loc_exp = ((match_keyword | venue_keyword) + in_operator + location)("loc_exp")
    player_team_exp = (player_keyword + from_operator + all_player_teams)("player_team_exp")
    with_exp = ((plural_table_names | all_tables) + with_operator + (all_cols) + comparison_operator + (word | ints))(
        "with_exp")
    play_exp = ((player_keyword | team_keyword) + play_in + (location | positions | match_no))("play_exp")
    wp_exp = (wp_keyword + of_operator + (all_player_teams | player_names))("wp_exp")
    position_exp = (position_keyword + of_operator + player_names)("position_exp")
    total_exp = (total_keyword + total_cols + of_operator + (
            location | player_names | match_no | positions | all_player_teams))("total_exp")
    res_exp = ((match_keyword) + results + (all_player_teams | player_names))
    expression = Forward()

    # expression definition (for grammar)
    expression << (loc_exp | player_team_exp | with_exp | play_exp | wp_exp | total_exp | position_exp | res_exp)

    # accepts strings in language and returns the parsed input if not accepted returns zero
    try:
        result = list(expression.parseString(user_input))
        if (user_input.lower() == "help"):
            return 1
        else:
            return result
    except Exception as e:
        return 0


# validates the user input based on the response of the parser
def validate_input(user_input):
    while parse(user_input) == 0:
        user_input = input("Invalid query. Please enter a query that matches the above instructions: ")
    return parse(user_input)


# compares the user input length to the response of the parser b/c parser can sometimes crop the input
def compare_input_length(parsed_input, user_input):
    # difference in user input length and the parsed input length
    input_length_difference = len(user_input.split(' ')) - len(parsed_input)
    # grab the rest of the string that could have been missed by the parser
    if input_length_difference > 0:
        parsed_input = parsed_input + user_input.split(' ')[-input_length_difference:]
    return parsed_input


def get_query():
    print("Please enter your query as described by the structure above: ")
    user_input = input(" => ")
    parsed_input = validate_input(user_input)
    parsed_input = compare_input_length(parsed_input, user_input)
    #used for results query
    if parsed_input[1] == 'won by' or parsed_input[1] == 'lost by' or parsed_input[1] == 'tied by':
        query_info = process_res_query(parsed_input)
    #used for play queries
    elif parsed_input[1] == 'plays in' or parsed_input[1] == 'play in':
        query_info = process_play_query(parsed_input)
    #used for position queries
    elif parsed_input[0] == 'position':
        query_info = process_position_query(parsed_input)
    #used for total queries
    elif parsed_input[0] == "total":
        query_info = process_total_query(parsed_input)
    #used for win percent queries
    elif parsed_input[0] == 'win percentage':
        query_info = process_wp_query(parsed_input)
    # used for player origin queries
    elif parsed_input[1] == 'from':
        query_info = process_player_query(parsed_input)
    # used for location queries
    elif parsed_input[1] == 'in':
        query_info = process_location_query(parsed_input)
    # used for with statements
    elif parsed_input[1] == 'with':
        query_info = process_with_query(parsed_input)
        while query_info == '':
            print("That is not a valid query for that information. Make sure you are using the correct operators. For "
                  "queries about text columns be sure to use the == operator. Please enter another query: ")
            user_input = input(" => ")

            parsed_input = validate_input(user_input)
            parsed_input = compare_input_length(parsed_input, user_input)
            query_info = process_with_query(parsed_input)

    else:
        query_info = user_input
    return query_info
