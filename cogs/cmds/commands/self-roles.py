import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
from nextcord.utils import get
import api

intents = nextcord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

class SelfRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @nextcord.slash_command(name="selfroles", description="Set up a self-role reaction")
    async def selfroles(
        self,
        interaction: Interaction,
        channel_id: str = SlashOption(description="Channel ID where the message is located"),
        message_id: str = SlashOption(description="Message ID to add the reaction"),
        emoji: str = SlashOption(description="Emoji to use for the reaction"),
        role: nextcord.Role = SlashOption(description="Role to assign on reaction")
    ):
        try:
            channel = await self.bot.fetch_channel(int(channel_id))
            message = await channel.fetch_message(int(message_id))
        except nextcord.NotFound:
            await interaction.response.send_message("Message or channel not found.", ephemeral=True)
            return
        except nextcord.Forbidden:
            await interaction.response.send_message("Insufficient permissions to access the message or channel.", ephemeral=True)
            return

        # Check if the emoji is a custom emoji or a Unicode emoji
        if emoji.startswith("<:") and emoji.endswith(">"):
            # Custom emoji (e.g., <:emoji_name:emoji_id>)
            emoji_obj = emoji
        else:
            # Unicode emoji, no further processing needed
            emoji_obj = emoji

        # Add the reaction
        try:
            await message.add_reaction(emoji_obj)
        except nextcord.HTTPException as e:
            await interaction.response.send_message(f"Failed to add reaction: {e}", ephemeral=True)
            return

        # Save the reaction-role pair in a dictionary (or database for persistence)
        if not hasattr(self.bot, 'reaction_roles'):
            self.bot.reaction_roles = {}
        self.bot.reaction_roles[(message.id, str(emoji_obj))] = role.id

        await interaction.response.send_message(f"Reaction {emoji} added to message ID {message_id} in channel {channel.name} for role {role.name}", ephemeral=True)

        

    @nextcord.slash_command(name="list_emojis", description="List all accessible emojis", guild_ids=[api.GuildID])
    async def list_emojis(self, interaction: Interaction):
        # Check if the bot has access to the server and its emojis
        guild = interaction.guild
        if guild:
            emojis = [str(emoji) for emoji in guild.emojis]
            if emojis:
                await interaction.response.send_message("Available emojis: " + ", ".join(emojis))
            else:
                await interaction.response.send_message("No accessible custom emojis found in this server.")
        else:
            await interaction.response.send_message("Bot is not in this server or unable to access it.")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not hasattr(self.bot, 'reaction_roles'):
            return

        message_id = payload.message_id
        emoji = str(payload.emoji)

        if (message_id, emoji) in self.bot.reaction_roles:
            guild = self.bot.get_guild(payload.guild_id)
            role_id = self.bot.reaction_roles[(message_id, emoji)]
            role = get(guild.roles, id=role_id)

            if role:
                member = guild.get_member(payload.user_id)
                if member:
                    await member.add_roles(role)
                    print(f"Added {role.name} to {member.name}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not hasattr(self.bot, 'reaction_roles'):
            return

        message_id = payload.message_id
        emoji = str(payload.emoji)

        if (message_id, emoji) in self.bot.reaction_roles:
            guild = self.bot.get_guild(payload.guild_id)
            role_id = self.bot.reaction_roles[(message_id, emoji)]
            role = get(guild.roles, id=role_id)

            if role:
                member = guild.get_member(payload.user_id)
                if member:
                    await member.remove_roles(role)
                    print(f"Removed {role.name} from {member.name}")

def setup(bot: commands.Bot):
    print("SelfRoles Cog Registered")
    bot.add_cog(SelfRoles(bot))
