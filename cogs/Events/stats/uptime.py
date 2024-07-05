import nextcord
from nextcord.ext import commands, application_checks
import sqlite3
import api as api
import datetime

intents = nextcord.Intents.all()


class UpTime(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    start_time = datetime.datetime.utcnow()

    @commands.Cog.listener()
    async def on_ready(self):
        global start_time
        start_time = datetime.datetime.utcnow()

    @nextcord.slash_command(
        name="uptime",
        description="Show how long the bot has been online",
        guild_ids=[api.GuildID]
    )
    async def uptime(self, i: nextcord.Interaction):
        uptime_delta = datetime.datetime.utcnow() - start_time
        uptime_string = str(uptime_delta).split('.')[0]  # Remove microseconds

        embed = nextcord.Embed(
            title="Uptime Stats",
            description=f"The bot has been online for: {uptime_string}",
            color=nextcord.Color.gold()
        )
        embed.set_footer(text=f"Requested by {i.user.name}", icon_url=i.user.avatar.url)
        await i.response.send_message(embed=embed)


def setup(bot: commands.Bot):
    print("Up-Time Cog Registered")
    bot.add_cog(UpTime(bot))