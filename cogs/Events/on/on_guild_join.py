import nextcord
from nextcord.ext import commands
import sqlite3
from datetime import datetime

intents = nextcord.Intents.all()

# Database file
DATABASE_FILE = 'toh.db'

# Initialize the bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Function to create or update a guild entry in the database
def create_or_update_guild_entry(guild_id, guild_name, join_date):
    with sqlite3.connect(DATABASE_FILE) as db:
        cursor = db.cursor()
        # Insert or update the guild entry
        cursor.execute('''
            INSERT INTO guildinfo (guild_id, guild_name, join_date)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET 
                guild_name=excluded.guild_name,
                join_date=excluded.join_date
        ''', (guild_id, guild_name, join_date))
        db.commit()

class OnJoinGuild(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Event listener for when the bot joins a new guild
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        join_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        create_or_update_guild_entry(guild.id, guild.name, join_date)
        print(f"Joined new guild: {guild.name}, entry created or updated in the database.")

def setup(bot: commands.Bot):
    print("OnJoinGuild Cog Registered")
    bot.add_cog(OnJoinGuild(bot))

