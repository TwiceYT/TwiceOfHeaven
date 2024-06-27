import nextcord
from nextcord.ext import commands, tasks
import api
import sqlite3
import datetime

intents = nextcord.Intents.all()

database = sqlite3.connect('toh.db')
cursor = database.cursor()

class Poll(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        self.polls = {}  # Dictionary to store active polls with their end times

        # Start the background task to update polls
        self.update_poll_task.start()

    def cog_unload(self):
        self.update_poll_task.cancel()

    @nextcord.slash_command(
        name="poll",
        description="Make a poll on the server.",
        guild_ids=[api.GuildID]
    )
    async def create_poll(self, i: nextcord.Interaction, time: int, question: str, options: str, thumbnail: str):

        options_list = [option.strip() for option in options.split(',')]

        if len(options_list) > 10 or len(options_list) < 2:
            await i.response.send_message(":no_entry: Please provide at least 2 options and a maximum of 10")
            return
        elif time <= 1:
            await i.response.send_message(":no_entry: Please provide a poll end time longer than 1h")
            return

        end_time = datetime.datetime.utcnow() + datetime.timedelta(hours=time)

        embed = nextcord.Embed(
            title="Twice Polls",
            description="",
            color=nextcord.Color.gold()
        )
        embed.add_field(name=question, value="", inline=False)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        elif i.guild.icon:
            embed.set_thumbnail(url=i.guild.icon)

        for idx, option in enumerate(options_list):
            # Add field to embed for each option
            emoji = self.emojis[idx]
            embed.add_field(name=f"{emoji} {option}", value="", inline=False)

        await i.response.send_message(embed=embed)
        message = await i.original_message()

        # Store poll information with end time, channel ID, and message ID
        self.polls[message.id] = {
            'end_time': end_time, 
            'channel_id': message.channel.id, 
            'message_id': message.id,
            'options': options_list
        }

        # Map options to emojis
        option_emoji_mapping = dict(zip(options_list, self.emojis[:len(options_list)]))

        # Add reactions to the message
        for option in options_list:
            await message.add_reaction(option_emoji_mapping[option])

    @tasks.loop(seconds=1)
    async def update_poll_task(self):
        current_time = datetime.datetime.utcnow()
        for poll_id, poll_info in list(self.polls.items()):
            channel = self.bot.get_channel(poll_info['channel_id'])
            if channel:
                try:
                    message = await channel.fetch_message(poll_info['message_id'])
                    if current_time >= poll_info['end_time']:
                        # Poll has ended, find the winning option
                        max_votes = 0
                        winning_option = None

                        for reaction in message.reactions:
                            if reaction.count > max_votes:
                                max_votes = reaction.count
                                winning_option = reaction.emoji

                        if winning_option is not None:
                            option_index = self.emojis.index(winning_option)
                            winning_option_text = poll_info['options'][option_index]
                            await channel.send(f"**{winning_option_text}** is the winning option!!")

                        # Clean up
                        embed = message.embeds[0]
                        embed.set_footer(text="Poll has ended.")
                        await message.edit(embed=embed)
                        del self.polls[poll_id]
                    else:
                        # Update the time in the embed
                        remaining_time_seconds = (poll_info['end_time'] - current_time).total_seconds()
                        remaining_days = remaining_time_seconds // 86400
                        remaining_hours = (remaining_time_seconds % 86400) // 3600
                        remaining_minutes = (remaining_time_seconds % 3600) // 60
                        remaining_seconds = remaining_time_seconds % 60

                        if remaining_days > 0:
                            time_str = f"Poll ends in {int(remaining_days)} Days, {int(remaining_hours)} Hours"
                        elif remaining_hours > 0:
                            time_str = f"Poll ends in {int(remaining_hours)} Hours, {int(remaining_minutes)} Minutes"
                        elif remaining_minutes > 0:
                            time_str = f"Poll ends in {int(remaining_minutes)} Minutes"
                        else:
                            time_str = f"Poll ends in {int(remaining_seconds)} Seconds"

                        embed = message.embeds[0]
                        embed.set_footer(text=time_str)
                        await message.edit(embed=embed)
                except nextcord.errors.NotFound:
                    # Message not found (possibly deleted), clean up
                    del self.polls[poll_id]

def setup(bot: commands.Bot):
    print("Poll Cog Registered")
    bot.add_cog(Poll(bot))
