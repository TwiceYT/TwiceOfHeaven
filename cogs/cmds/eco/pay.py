import nextcord
from nextcord.ext import commands
import api as api
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()



intents = nextcord.Intents.all()

class Pay(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="pay",
        description="Pay another user money!",
        guild_ids=[api.GuildID]
    )
    async def pay(self, i: nextcord.Interaction, member: nextcord.Member, amount: int = 1):
        cursor.execute("SELECT bank FROM economy WHERE user_id = ? AND guild_id = ?", (i.user.id, i.guild_id,))
        result = cursor.fetchone()

        if result is None:
            await i.response.send_message("You don't have an account.")
            return

        currentamount = result[0]

        if currentamount >= amount:
            new_amountSender = currentamount - amount
            cursor.execute("UPDATE economy SET bank = ? WHERE user_id = ? AND guild_id = ?", (new_amountSender, i.user.id, i.guild_id,))
            database.commit()

            cursor.execute("SELECT bank FROM economy WHERE user_id = ? AND guild_id = ?", (member.id, i.guild_id,))
            result2 = cursor.fetchone()

            if result2 is None:
                currentamountAchiver = 0
                cursor.execute("INSERT INTO economy (user_id, guild_id, bank) VALUES (?, ?, ?)", (member.id, i.guild_id, amount))
                new_amountAchieve = amount
            else:
                currentamountAchiver = result2[0]
                new_amountAchieve = currentamountAchiver + amount
                cursor.execute("UPDATE economy SET bank = ? WHERE user_id = ? AND guild_id = ?", (new_amountAchieve, member.id, i.guild_id,))

            database.commit()

            embed = nextcord.Embed(
                title="Money Transfer",
                description=f"You have sent money to user {member.name}",
            )
            embed.add_field(name="Amount: ", value=amount, inline=True)
            embed.add_field(name="Your New Amount:", value=f"${new_amountSender}", inline=False)
            embed.add_field(name=f"{member.name}'s New Amount:", value=f"${new_amountAchieve}", inline=False)

            await i.send(embed=embed)
        else:
            await i.response.send_message("You don't have enough money to send that amount!")

def setup(bot: commands.Bot):
    print("Pay Cog Registered")
    bot.add_cog(Pay(bot))
