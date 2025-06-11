import nextcord
from nextcord.ext import commands
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()

intents = nextcord.Intents.all()

#Load env file
load_dotenv(dotenv_path='config\config.env')
#Load custom Prefix
BotID = os.getenv("BotID")

class MinigameLed(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="minigame-led",
        description="Check the minigames leaderboard"
    )
    async def leaderboard(self, i: nextcord.Interaction):
        try:
            result = self.get_leaderboard_data(i)
            if result:
                embed = self.create_leaderboard_embed(result, "Minigames")
                await i.response.send_message(embed=embed)
            else:
                await i.response.send_message(content="There are no users in the leaderboard")
        except Exception as e:
            await i.response.send_message(content=f"An error occurred: {e}")

    def get_leaderboard_data(self, i: nextcord.Interaction):
        cursor.execute("""
        SELECT user, trivia_wins, guessnr_wins, pvp_wins FROM minigames WHERE guild_id = ?
        """, (i.guild.id,))
        result = cursor.fetchall()

        if result:
            # Replace None with 0 for wins
            result = [(user, trivia_wins or 0, guessnr_wins or 0, pvp_wins or 0) for user, trivia_wins, guessnr_wins, pvp_wins in result]
            # Sort the result list based on the sum of trivia, guessing, and PVP wins
            result.sort(key=lambda x: sum(x[1:]), reverse=True)
            # Slice the result list to show only the top 10 users
            result = result[:10]

        return result

    def create_leaderboard_embed(self, result, leaderboard_type):
        embed = nextcord.Embed(title=f"{leaderboard_type} Leaderboard", color=nextcord.Color.red())
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/859111111111111111/859111111111111111/economy.png")

        # Add headers for the leaderboard
        embed.add_field(name="Nr", value="", inline=True)
        embed.add_field(name="User", value="", inline=True)
        embed.add_field(name="Wins", value="", inline=True)

        # Construct the leaderboard text with headers and formatted data
        for rank, user_data in enumerate(result, start=1):
            embed.add_field(name="", value=f"{rank}", inline=True)
            embed.add_field(name="", value=user_data[0], inline=True)
            embed.add_field(name="", value=sum(user_data[1:]), inline=True)

        embed.set_footer(text=f"{leaderboard_type} Leaderboard")
        return embed

    def get_trivia_leaderboard_data(self, guild_id):
        cursor.execute("""
        SELECT user, trivia_wins FROM minigames WHERE guild_id = ?
        """, (guild_id,))
        result = cursor.fetchall()

        if result:
            result = [(user, trivia_wins or 0) for user, trivia_wins in result]
            result.sort(key=lambda x: x[1], reverse=True)
            result = result[:10]

        return result

    def get_guessing_leaderboard_data(self, guild_id):
        cursor.execute("""
        SELECT user, guessnr_wins FROM minigames WHERE guild_id = ?
        """, (guild_id,))
        result = cursor.fetchall()

        if result:
            result = [(user, guessnr_wins or 0) for user, guessnr_wins in result]
            result.sort(key=lambda x: x[1], reverse=True)
            result = result[:10]

        return result

    def get_pvp_leaderboard_data(self, guild_id):
        cursor.execute("""
        SELECT user, pvp_wins FROM minigames WHERE guild_id = ?
        """, (guild_id,))
        result = cursor.fetchall()

        if result:
            result = [(user, pvp_wins or 0) for user, pvp_wins in result]
            result.sort(key=lambda x: x[1], reverse=True)
            result = result[:10]

        return result

    @nextcord.slash_command(
        name="trivia-led",
        description="Check the Trivia leaderboard"   
    )
    async def trivia_leaderboard(self, i: nextcord.Interaction):
        try:
            result = self.get_trivia_leaderboard_data(i.guild.id)
            if result:
                embed = self.create_leaderboard_embed(result, "Trivia")
                await i.response.send_message(embed=embed)
            else:
                await i.response.send_message(content="There are no users in the Trivia leaderboard")
        except Exception as e:
            await i.response.send_message(content=f"An error occurred: {e}")

    @nextcord.slash_command(
        name="guessing-led",
        description="Check the Guessing leaderboard"   
    )
    async def guessing_leaderboard(self, i: nextcord.Interaction):
        try:
            result = self.get_guessing_leaderboard_data(i.guild.id)
            if result:
                embed = self.create_leaderboard_embed(result, "Guessing")
                await i.response.send_message(embed=embed)
            else:
                await i.response.send_message(content="There are no users in the Guessing leaderboard")
        except Exception as e:
            await i.response.send_message(content=f"An error occurred: {e}")

    @nextcord.slash_command(
        name="pvp-led",
        description="Check the PVP leaderboard"  
    )
    async def pvp_leaderboard(self, i: nextcord.Interaction):
        try:
            result = self.get_pvp_leaderboard_data(i.guild.id)
            if result:
                embed = self.create_leaderboard_embed(result, "PVP")
                await i.response.send_message(embed=embed)
            else:
                await i.response.send_message(content="There are no users in the PVP leaderboard")
        except Exception as e:
            await i.response.send_message(content=f"An error occurred: {e}")

def setup(bot: commands.Bot):
    print("MinigamesLed Cog Registered")
    bot.add_cog(MinigameLed(bot))
