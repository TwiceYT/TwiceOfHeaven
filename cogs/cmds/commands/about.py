import nextcord
from nextcord.ext import commands, application_checks

intents = nextcord.Intents.all()


class about(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="about",
        description="Get information about user",
    )
    async def about(self, i: nextcord.Interaction, member: nextcord.Member = nextcord.SlashOption(description="The member to get information about")):
            embed = nextcord.Embed(
            title="User Information",
            description=f"Information about {member.mention}",
            color=nextcord.Color.blurple(),
            )                    
            member_roles = [role for role in member.roles]
            member_roles_str = " ".join([role.mention for role in member_roles])
            embed.add_field(name="Username", value=member.name, inline=False)
            embed.add_field(name="Roles", value=member_roles_str, inline=False)
            embed.add_field(name="Account Created", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
            embed.add_field(name="Joined Server", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
            if member.avatar is not None:
                embed.set_thumbnail(url=member.avatar.url) 
            if i.user.avatar: embed.set_footer(text=f"Requested by {i.user.name}", icon_url=i.user.avatar.url)
            else:
                embed.set_footer(text=f"Requested by {i.user.name}", icon_url=i.user.default_avatar.url)
            
            await i.response.send_message(embed=embed)

def setup(bot: commands.Bot):
    print("About Cog Registered")
    bot.add_cog(about(bot))