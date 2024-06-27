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


    #level database logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS levels (
            guild_id INTEGER,
            user_id INTEGER,
            user TEXT,
            exp INTEGER,
            level INTEGER,
            last_lvl INTEGER
        )
        """)

        #MessageStats Database
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS msgstats (
            guild_id INTEGER,
            user_id INTEGER,
            user TEXT,
            msg INTEGER,
            last_message_timestamp DATETIME
        )
        """)

        #Economy Database
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS economy (
            guild_id INTEGER,
            user_id INTEGER,
            user TEXT,
            bank INTEGER
        )
        """)

        #Minigames
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS minigames (
            guild_id INTEGER,
            user_id INTEGER,
            user TEXT,
            trivia_wins INTEGER,
            guessnr_wins INTEGER,
            pvp_wins INTEGER
        )
        """)

        #Voice Channel Stats
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS voicestat (
            guild_id INTEGER,
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            last_joined TEXT,
            total INTEGER
        )
        """);

        #Birthdays
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS birthdays (
            guild_id INTEGER,
            user_id INTEGER,
            user TEXT,
            birthdate INTEGER
        )
        """);
    #
    ##
    ### LOGS
    ##
    #
    
        #Editlog
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS editlog (
            guild_id INTEGER,
            user_id INTEGER,
            user TEXT,
            old_content TEXT,
            new_content INTEGER,
            message_id INTEGER,
            edit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """);

            #DelMsgLog
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS delmsglog (
            guild_id INTEGER,
            user_id INTEGER,
            user TEXT,
            content TEXT,
            message_id INTEGER,
            del_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """);

            #ChanneLogs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Channellog (
                guild_id INTEGER,
                user_id INTEGER,
                user TEXT,
                action TEXT,
                channel_name TEXT,
                channel_id INTEGER,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
