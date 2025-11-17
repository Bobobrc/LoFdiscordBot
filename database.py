import sqlite3
from sqlite3 import Error


def create_connection(db_file):
  conn = None
  try:
    conn = sqlite3.connect(db_file)
    return conn
  except Error as e:
    print(e)
    
conn = create_connection('discordBOT.db')

# Create tables for players and leaderboard

def create_players_table(conn):
  try:
      cur = conn.cursor()
      cur.execute("""CREATE TABLE IF NOT EXISTS players(
                player_name TEXT PRIMARY KEY,
                last_match TEXT
                );""")
  except Error as e:
      print(e)
  cur.close()

def create_leaderboard_table(conn):
  try:
      cur = conn.cursor()
      cur.execute("""CREATE TABLE IF NOT EXISTS leaderboard(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                tier TEXT,
                rank TEXT,
                lp INT
                );""")
  except Error as e:
      print(e)
  cur.close()
  
#create_players_table(conn)
#create_leaderboard_table(conn)  

# Select leaderboard

def select_leaderboard(conn):
    c = """SELECT * FROM leaderboard"""
    cur = conn.cursor()
    cur.execute(c)

    leaderboard = cur.fetchall()
    
    cur.close()
    return leaderboard

# Get all the players

def get_players(conn):
    c = """SELECT player_name FROM leaderboard"""
    cur = conn.cursor()
    cur.execute(c)

    leaderboard = cur.fetchall()
 
    cur.close()
    return leaderboard

def get_players_count(conn):
    query = "SELECT COUNT(*) FROM leaderboard"
    cur = conn.cursor()
    cur.execute(query)
    count = cur.fetchone()[0]
    cur.close()
    return count
  
# Get a player from leaderboard

def select_player_by_name(conn, player_name):
    c = """SELECT * FROM leaderboard WHERE player_name = ?"""
    cur = conn.cursor()
    cur.execute(c, (player_name,))

    player_info = cur.fetchone()
 
    cur.close()
    return player_info
  
def select_player_by_id(conn, id):
    c = """SELECT * FROM leaderboard WHERE id = ?"""
    cur = conn.cursor()
    cur.execute(c, (id,))

    player_info = cur.fetchone()
 
    cur.close()
    return player_info
  
# Get the last match id

def get_last_match(conn, player_name):
    c = """SELECT last_match FROM players WHERE player_name = ?"""
    cur = conn.cursor()
    cur.execute(c, (player_name,))
    last_game = cur.fetchall()
    cur.close()
    return last_game[0][0]
  
# Update the last match id

def update_last_match(conn, player_name):
  c = '''UPDATE players
          SET last_match = ?
          WHERE player_name = ?'''
  cur = conn.cursor()
  cur.execute(c, player_name)
  conn.commit()
  cur.close
  
# Update leaderboard

def update_leaderboard(conn, x):
    c = ''' UPDATE leaderboard
              SET player_name = ?,
                  tier = ?,
                  rank = ?,
                  lp = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(c, x)
    conn.commit()
    cur.close()
  
# Reset tables to default info

def reset_leaderboard_table(conn, player_name):
    c = ''' UPDATE leaderboard
              SET player_name = ?,
                  tier = ?,
                  rank = ?,
                  lp = ?
              WHERE player_name = ?'''
    cur = conn.cursor()
    cur.execute(c, (player_name, 'UNRANKED', 'UNRANKED', 0, player_name))
    conn.commit()
    cur.close()
  
# Add player to tables
    
def add_player_to_players(conn, player):
    c = '''INSERT OR IGNORE INTO players(player_name, last_match)
            VALUES(?,?)'''
    cur = conn.cursor()
    cur.execute(c, player)
    conn.commit()
    cur.close()

def add_player_to_leaderboard(conn, player):
    c = ''' INSERT OR IGNORE INTO leaderboard(player_name, tier, rank, lp)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(c, player)
    conn.commit()
    cur.close()
    
# Remove player from tables

def remove_player_from_players(conn, player):
    c = '''DELETE FROM players WHERE player_name = ?'''
    cur = conn.cursor()
    cur.execute(c, (player,))
    conn.commit()
    cur.close()

def remove_player_from_leaderboard(conn, player):
    c = '''DELETE FROM leaderboard WHERE player_name = ?'''
    cur = conn.cursor()
    cur.execute(c, (player,))
    conn.commit()
    cur.close()

# Every time you delete an user    
# Move data from leaderboard table to temp table, reset auto increment and move the data back

import sqlite3

def reorder_leaderboard(conn, table_name='leaderboard'):
    # Connect to the SQLite database
    cursor = conn.cursor()

    try:
        # Start a transaction
        cursor.execute("BEGIN;")

        # Step 1: Create a temporary table with the same structure, but without AUTOINCREMENT
        cursor.execute(f"""
            CREATE TABLE temp_table (
                ID INTEGER PRIMARY KEY,
                PLAYER_NAME TEXT,
                TIER TEXT,
                RANK INTEGER,
                LP INTEGER
            );
        """)

        # Step 2: Insert data into the temporary table with new sequential IDs
        cursor.execute(f"""
            INSERT INTO temp_table (PLAYER_NAME, TIER, RANK, LP)
            SELECT PLAYER_NAME, TIER, RANK, LP
            FROM {table_name}
            ORDER BY ID;
        """)

        # Step 3: Drop the original table
        cursor.execute(f"DROP TABLE {table_name};")

        # Step 4: Rename the temporary table to the original table name
        cursor.execute(f"ALTER TABLE temp_table RENAME TO {table_name};")

        # Step 5: Reset the AUTOINCREMENT counter
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")

        # Commit the transaction
        conn.commit()
        print("Auto-increment IDs reset successfully.")

    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"An error occurred: {e}")
