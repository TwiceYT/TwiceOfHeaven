import sqlite3

# Function to set up the database connection and create tables
def setup():
    try:
        # Connect to the database
        db_connection = sqlite3.connect('toh.db')
        cursor = db_connection.cursor()

        # Create tables if they do not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guildinfo (
                guild_id INTEGER PRIMARY KEY,
                guild_name TEXT,
                modlogs INTEGER,
                welcome_channel_id INTEGER,
                join_role_id INTEGER,
                leave_channel_id INTEGER,
                membercount_channel INTEGER,
                rolecount_channel INTEGER,
                unverified_channel INTEGER,
                staffrole_id INTEGER,
                ticketsupport_role_id INTEGER,
                birthday_channel_id INTEGER,
                verify_role INTEGER,
                ticketlogs INTEGER,
                serverlogs INTEGER,
                supportcategory INTEGER,
                join_date TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                token TEXT,
                prefix TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bans (
                guild_id INTEGER,
                banned_user TEXT,
                ban_reason TEXT,
                banned_by TEXT,
                ban_timestamp TIMESTAMP,
                user_id INTEGER,
                bannedby_id INTEGER,
                PRIMARY KEY (user_id, ban_timestamp)
            )
        """)


        #Warn database logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                guild_id INTEGER,
                warned_user TEXT,
                warn_reason TEXT,
                warned_by TEXT,
                warn_timestamp TIMESTAMP,
                user_id INTEGER,
                warnedby_id INTEGER,
                warnings INTEGER,
                PRIMARY KEY (user_id, warn_timestamp)
            )
        """)


















        

        # Commit changes and return connection and cursor
        db_connection.commit()
        return db_connection, cursor

    except sqlite3.Error as e:
        print("SQLite error:", e)
        return None, None
    except Exception as e:
        print("Error during database setup:", e)
        return None, None
