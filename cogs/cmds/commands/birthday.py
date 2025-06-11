import nextcord
from nextcord.ext import commands, tasks
import sqlite3
import datetime
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()



intents = nextcord.Intents.all()


class Birthday(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_birthday_task.start()  # Initialize the task loop here

    def get_birthday_channel(self, guild_id):
        cursor = self.bot.db_cursor
        cursor.execute('SELECT birthday_channel_id FROM guildinfo WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    @nextcord.slash_command(
        name="birthday-set",
        description="Set your own birthday and get pinged in the server on your B-Day"
    )
    async def set_birthday(self, i: nextcord.Interaction, birthday: str):
        try:
            date_obj = datetime.datetime.strptime(birthday, "%d %B").date()
            formatted_date = date_obj.strftime("%Y-%m-%d")  # Store in YYYY-MM-DD format
        except ValueError:
            return await i.response.send_message("Invalid date format. Please use dd month (e.g., 15 January).")

        cursor = self.bot.db_cursor
        # Check if the user already has a birthday entry for the guild
        cursor.execute("SELECT * FROM birthdays WHERE user_id=? AND guild_id=?", (i.user.id, i.guild.id))
        existing_entry = cursor.fetchone()

        if existing_entry:
            # Update the existing entry with the new birthdate
            cursor.execute("UPDATE birthdays SET birthdate=? WHERE user_id=? AND guild_id=?", (formatted_date, i.user.id, i.guild.id))
        else:
            # Insert a new entry for the guild
            cursor.execute("INSERT INTO birthdays (user_id, user, birthdate, guild_id) VALUES (?, ?, ?, ?)", (i.user.id, str(i.user), formatted_date, i.guild.id))

        self.bot.db_connection.commit()

        await i.response.send_message(f"Your birthday ({birthday}) has been successfully stored!")



        ###     ###     ###     ###
##     Sending birthday messages        ###
        ###     ###     ###     ###

    async def send_birthday_messages(self, guild):
        today = datetime.date.today()
        cursor = self.bot.db_cursor

        cursor.execute("SELECT * FROM birthdays WHERE guild_id=?", (guild.id,))
        birthdays = cursor.fetchall()

        for entry in birthdays:
            guild_id, user_id, user, birthdate_str = entry

            try:
                birthdate = datetime.datetime.strptime(birthdate_str, "%Y-%m-%d").date()  # Convert string to date
            except ValueError:
                print(f"Skipping invalid birthdate for user {user_id} in guild {guild_id}: {birthdate_str}")
                continue

            # Check if today is the user's birthday
            if birthdate.month == today.month and birthdate.day == today.day:
                member = guild.get_member(user_id)
                if member:
                    birthday_channel = self.get_birthday_channel(guild.id)
                    if birthday_channel:
                        channel = guild.get_channel(birthday_channel)
                        if channel:
                            await channel.send(f"Happy birthday, {member.mention}!")

    @tasks.loop(hours=24)
    async def check_birthday_task(self):
        print("Sending birthday messages...")
        for guild in self.bot.guilds:
            await self.send_birthday_messages(guild)
            print("Birthday message sent!")

    @check_birthday_task.before_loop
    async def before_check_birthday_task(self):
        await self.bot.wait_until_ready()

    @nextcord.slash_command(
        name="birthday-near",
        description="Get a list of upcoming birthdays in the next few months"
    )
    async def upcoming_birthdays(self, i: nextcord.Interaction, months: int = 3):
        today = datetime.date.today()
        future_date = today + datetime.timedelta(days=months * 30)  # Roughly get the future date

        cursor = self.bot.db_cursor
        cursor.execute("SELECT user, birthdate FROM birthdays WHERE guild_id=?", (i.guild.id,))
        birthdays = cursor.fetchall()

        upcoming_birthdays = []
        for user, birthdate_str in birthdays:
            try:
                birthdate = datetime.datetime.strptime(birthdate_str, "%Y-%m-%d").date()
            except ValueError:
                print(f"Skipping invalid birthdate for user {user} in guild {i.guild.id}: {birthdate_str}")
                continue

            # Adjust birthdate to the current year for comparison
            adjusted_birthdate = birthdate.replace(year=today.year)

            if today <= adjusted_birthdate <= future_date:
                upcoming_birthdays.append((user, adjusted_birthdate))

        # Sort the upcoming birthdays by date
        upcoming_birthdays.sort(key=lambda x: x[1])

        if not upcoming_birthdays:
            await i.response.send_message("No upcoming birthdays in the next few months.")
            return

        embed = nextcord.Embed(
            title="Upcoming Birthdays",
            description=f"Here are the birthdays in the next {months} month(s):",
            color=nextcord.Color.blue()
        )

        for user, birthdate in upcoming_birthdays:
            embed.add_field(name=user, value=birthdate.strftime("%d %B"), inline=False)

        await i.response.send_message(embed=embed)

def setup(bot: commands.Bot):
    print("Birthday Cog Registered")
    bot.add_cog(Birthday(bot))