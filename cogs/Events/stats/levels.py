import nextcord
from nextcord.ext import commands, application_checks
import sqlite3
import api as api
import vacefron
import math
import random
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()


intents = nextcord.Intents.all()


class levels(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return  # Ignore messages sent by the bot itself

        if message.guild is None:
            return  # Ignore messages sent in DMs
        
        cursor.execute(f"SELECT user_id, user, guild_id, exp, level, last_lvl FROM levels WHERE user_id = ? AND user = ? AND guild_id = ?", (message.author.id, message.author.name, message.guild.id))
        result = cursor.fetchone()
        if result is None:
            
            cursor.execute("""
                INSERT INTO levels(user_id, user, guild_id, exp, level, last_lvl) VALUES (?, ?, ?, ?, ?, ?)
            """, (message.author.id, message.author.name, message.guild.id, 0, 0, 0))
            database.commit()

        else:
            exp = result[3]
            lvl = result[4]
            last_lvl = result[5]

            exp_gained = random.randint(1,5)
            exp += exp_gained
            lvl = 0.15*(math.sqrt(exp))

            cursor.execute(f"UPDATE levels SET exp = {exp}, level = {lvl} WHERE user_id = {message.author.id} AND guild_id = {message.guild.id}")
            database.commit()

            if int(lvl) > last_lvl:
                await message.channel.send(f"{message.author.mention} has leveled up to level {int(lvl)}!")
                cursor.execute(f"UPDATE levels SET last_lvl = {int(lvl)} WHERE user_id = {message.author.id} AND guild_id = {message.guild.id}")
                database.commit()

    @nextcord.slash_command(
        name="level",
        description="Check the levels of a user",
        guild_ids=[api.GuildID]
    )
    async def levels(self, i: nextcord.Interaction, member: nextcord.Member):

        rank = 1

        descending = "SELECT * FROM levels WHERE guild_id = ? ORDER BY exp DESC"
        cursor.execute(descending, (i.guild.id,))
        result_all = cursor.fetchall()

        user_found = False

        for ind in range(len(result_all)):

            if result_all[ind][0] == member.id:
                user_found = True
                break
            else:
                rank += 1

        if user_found:
            cursor.execute(f"SELECT exp, level, last_lvl FROM levels WHERE user_id = ? AND guild_id = ?", (member.id, i.guild.id))
            result_user = cursor.fetchone()

            if result_user is not None:
                exp = result_user[0]
                level = result_user[1]
                last_lvl = result_user[2]

                next_lvl_xp = ((int(level) + 1) / 0.15) ** 2
                next_lvl_xp = int(next_lvl_xp)

                rank_card = vacefron.Rankcard(
                    username= member.name,
                    avatar_url= member.avatar.url,
                    current_xp=exp,
                    next_level_xp=next_lvl_xp,
                    previous_level_xp=0,
                    level=int(level),
                    rank=rank,
                )
                card = await vacefron.Client().rank_card(rank_card)
                await i.response.send_message(card.url)
        else:
            await i.response.send_message("User not found in the database.")

def setup(bot: commands.Bot):
    print("Levels Cog Registered")
    bot.add_cog(levels(bot))