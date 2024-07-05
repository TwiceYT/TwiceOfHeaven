import nextcord
from nextcord.ext import commands
import api
import sqlite3
import sympy as sp

intents = nextcord.Intents.all()

database = sqlite3.connect('toh.db')
cursor = database.cursor()

def calculate(expression):
    try:
        # Parse the expression using sympy
        result = sp.sympify(expression)
        # Evaluate the expression to get the numeric result
        evaluated_result = result.evalf()
        return evaluated_result, str(result)
    except Exception as e:
        return f"Error: {str(e)}", expression

class Calc(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="calc",
        description="Calculate your math with TwiceOfHeaven",
        guild_ids=[api.GuildID]
    )
    async def calculations(self, ctx: nextcord.Interaction, expression: str):
        result, expr = calculate(expression)
        embed = nextcord.Embed(
            title="Calculation Result:",
            description=f"{expr} = {result}",
        )
        embed.set_footer(text="The procedure might look diff, but shall be right answer!")
        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    print("Calc Cog Registered")
    bot.add_cog(Calc(bot))
