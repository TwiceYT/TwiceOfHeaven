import nextcord
from nextcord.ext import commands
import api as api
import random

intents = nextcord.Intents.all()

class MemberJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Perform actions when a member joins
        # For example, send a welcome message as an embed to a specific channel
        welcome_channel_id = api.WelcomeID  # Replace with your welcome channel ID
        welcome_channel = member.guild.get_channel(welcome_channel_id)
        rules_channel_mention = f"<#{api.Rules}>"

        if welcome_channel:
            # Create an embed for the welcome message
            embed = nextcord.Embed(
                title=f"Welcome to the server, {member.name}!",
                description=f"We're glad to have you here. Enjoy your stay!",
                color=0x00ff00
            )
            embed.add_field(name="Rules", value=f"Be sure to read the {rules_channel_mention}.")
            embed.add_field(name="Mention", inline=False, value=f"{member.mention}")
            embed.set_thumbnail(url=member.avatar.url)  # Display member's avatar

            # Randomize the role a member gets, a team between A - F, Used for initiate managers
            preset_roles = [api.TeamA, api.TeamB, api.TeamC, api.TeamD, api.TeamE, api.TeamF]
            random.shuffle(preset_roles)
            
            # Assign only one random role to the new member
            role_to_assign = random.choice(preset_roles)
            role = member.guild.get_role(role_to_assign)
            
            if role:
                await member.add_roles(role)
                embed.add_field(name="Assigned Team", value=f"{role.mention}")

            # Send the welcome message as an embed
            await welcome_channel.send(embed=embed)

def setup(bot: commands.Bot):
    print("MemberJoin Cog Registered")
    bot.add_cog(MemberJoin(bot))