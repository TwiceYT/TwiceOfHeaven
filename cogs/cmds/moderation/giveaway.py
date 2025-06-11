import nextcord
from nextcord.ext import commands, application_checks
import sqlite3
import asyncio
import random
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()


def get_staffrole(i: nextcord.Interaction):
    with sqlite3.connect('toh.db') as database:
        cursor = database.cursor()
        cursor.execute('SELECT staffrole_id FROM guildinfo WHERE guild_id = ?', (i.guild.id,))
        staffrole = cursor.fetchone()
        if staffrole:
            return staffrole[0]
        else:
            i.response.send_message("You need to set up your kick logs using /setup", ephemeral=True)
            return None

def is_staff_or_admin():
    async def predicate(i: nextcord.Interaction):
        if i.user.guild_permissions.administrator:
            return True
        
        staff_role_id = get_staffrole(i)
        if staff_role_id is None:
            return False
        
        staff_role = i.guild.get_role(staff_role_id)
        if staff_role in i.user.roles:
            return True
        
        await i.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return False
    
    return application_checks.check(predicate)


class Giveaway(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @is_staff_or_admin()
    @nextcord.slash_command(
        name="giveaway",
        description="Create your own giveaway"
    )
    async def giveaway(self, interaction: nextcord.Interaction, duration: int, prize: str, requirements: str):
        # Convert duration from hours to seconds
        duration_seconds = duration * 3600

        # Calculate initial time remaining
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Create the giveaway embed
        embed = nextcord.Embed(
            title="🎉 Giveaway 🎉",
            description=f"React with 🎉 to enter the giveaway!\nPrize: {prize}\nRequirements: {requirements}",
            color=nextcord.Color.gold()
        )
        embed.add_field(name="Time Remaining", value=f"{hours}h {minutes}m {seconds}s", inline=False)
        
        # Send the embed and add the reaction
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_message()
        await msg.add_reaction("🎉")
        
        # Update the time remaining periodically
        while duration_seconds > 0:
            await asyncio.sleep(1)
            duration_seconds -= 1
            hours, remainder = divmod(duration_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            embed.set_field_at(0, name="Time Remaining", value=f"{hours}h {minutes}m {seconds}s", inline=False)
            await msg.edit(embed=embed)
        
        # Fetch the message again to get updated reactions
        msg = await interaction.channel.fetch_message(msg.id)
        reactions = msg.reactions
        
        # Initialize a list to store participants
        participants = []
        
        # Iterate through reactions and add users who reacted with 🎉 to the participants list
        for reaction in reactions:
            if str(reaction.emoji) == "🎉":
                async for user in reaction.users():
                    if user != self.bot.user:  # Ensure the bot itself is not included
                        participants.append(user)
        
        # Announce the participants
        if participants:
            winner = random.choice(participants)
            await interaction.followup.send(f"Congratulations {winner.mention}, you have won the giveaway!")
        else:
            await interaction.followup.send("No participants in the giveaway.")

def setup(bot: commands.Bot):
    print("Giveaway Cog Registered")
    bot.add_cog(Giveaway(bot))

