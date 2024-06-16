import nextcord
from nextcord.ext import commands
import sqlite3
import api as api
from datetime import datetime

def setup():
    with sqlite3.connect('toh.db') as db:
        cursor = db.cursor()

    #Ban database logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bans (
            serverid INTEGER,
            banned_user TEXT,
            ban_reason TEXT,
            banned_by TEXT,
            ban_timestamp TIMESTAMP,
            user_id INTEGER,
            bannedby_id INTEGER,
            PRIMARY KEY (user_id, ban_timestamp)
        )
    """)
    db.commit()


    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS guildinfo (
            guild_id INTEGER PRIMARY KEY,
            guild_name TEXT,
            modlogs INTEGER,
            welcome_channel_id INTEGER,
            Leave_channel_id INTEGER,
            membercoun_tchannel INTEGER,
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
    db.commit()

    #config database logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            token TEXT,
            prefix TEXT
        )
    """)
    db.commit()

