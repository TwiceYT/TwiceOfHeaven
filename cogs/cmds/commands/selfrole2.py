import nextcord
from nextcord.ext import commands, application_checks
import os
import sqlite3
from dotenv import load_dotenv
import api

# Load environment variables from the .env file
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


class ReactionRoleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.role_message_id = 0  # This will store the message ID
        self.emoji_to_role = {}  # This will map emojis to role IDs

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        if payload.message_id != self.role_message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            return

        role = guild.get_role(role_id)
        if role is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        try:
            await member.add_roles(role)
        except nextcord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: nextcord.RawReactionActionEvent):
        if payload.message_id != self.role_message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            return

        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            return

        role = guild.get_role(role_id)
        if role is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        try:
            await member.remove_roles(role)
        except nextcord.HTTPException:
            pass

    @nextcord.slash_command(
        name="selfrole",
        description="Setup a role reaction pair",
        guild_ids=[api.GuildID]  # Add your guild ID(s) here
    )
    async def setup_role_reaction(
        self,
        interaction: nextcord.Interaction,
        message_id: str,
        emoji: str,
        role: nextcord.Role
    ):
        try:
            channel = interaction.channel
            message = await channel.fetch_message(message_id)
        except nextcord.NotFound:
            await interaction.response.send_message("Message not found.", ephemeral=True)
            return
        except ValueError:
            await interaction.response.send_message("Invalid message ID format.", ephemeral=True)
            return
        print(emoji)
        if emoji.startswith("<:") and emoji.endswith(">"):
            try:
                name, emoji_id = emoji.strip("<:>").split(":")
                partial_emoji = nextcord.PartialEmoji(name=name, id=int(emoji_id))
            except ValueError:
                await interaction.response.send_message("Invalid custom emoji format.", ephemeral=True)
                return
        else:
            partial_emoji = nextcord.PartialEmoji(name=emoji)

        self.emoji_to_role[partial_emoji] = role.id
        self.role_message_id = message.id

        try:
            await message.add_reaction(partial_emoji)
        except nextcord.HTTPException as e:
            await interaction.response.send_message(f"Failed to add reaction: {e}", ephemeral=True)
            return

        await interaction.response.send_message(f"Reaction role setup complete! React with {emoji} to get the {role.name} role.", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(ReactionRoleCog(bot))