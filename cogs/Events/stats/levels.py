import nextcord
from nextcord.ext import commands
import sqlite3
import os
import math
import random
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import requests
import io

# Database file
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()

# Define your font file path
FONT_PATH = "arial.ttf"

# Function to create rank card
def create_rank_card(username, avatar_bytes, current_xp, next_level_xp, level, rank):
    # Load avatar image from bytes
    avatar_image = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
    avatar_image = avatar_image.resize((120, 120))

    # Create a blank rank card
    rank_card = Image.new("RGBA", (800, 220), color=(32, 34, 37))
    
    # Draw colored border
    draw = ImageDraw.Draw(rank_card)
    border_color = (0, 255, 255)
    draw.rectangle([(0, 0), (799, 219)], outline=border_color, width=10)
    
    # Paste avatar onto rank card
    rank_card.paste(avatar_image, (30, 50), mask=avatar_image)

    draw = ImageDraw.Draw(rank_card)

    # Load a font
    font = ImageFont.truetype(FONT_PATH, 40)
    small_font = ImageFont.truetype(FONT_PATH, 30)
    tiny_font = ImageFont.truetype(FONT_PATH, 20)

    # Draw username and underline
    username_text = f"{username}"
    draw.text((170, 40), username_text, font=font, fill=(255, 255, 255))
    username_bbox = draw.textbbox((170, 30), username_text, font=font)  # Use 170 as the starting x-coordinate
    username_width = username_bbox[2] - username_bbox[0]
    username_height = username_bbox[3] - username_bbox[1]
    underline_y = 50 + username_height + 5
    draw.line((170, underline_y, 170 + username_width, underline_y), fill=(0, 255, 255), width=3)  # Use 170 instead of 150


    # Draw Level, XP, and Rank text on the same row
    level_text = f"Level: {int(level)}"
    xp_text = f"XP: {current_xp}/{next_level_xp}"
    rank_text = f"Rank: {rank}"
    text_y = underline_y + 25
    draw.text((170, text_y), level_text, font=tiny_font, fill=(255, 255, 255))
    draw.text((340, text_y), xp_text, font=tiny_font, fill=(255, 255, 255))
    draw.text((540, text_y), rank_text, font=tiny_font, fill=(255, 255, 255))

    # Calculate progress bar width
    progress = min(1.0, current_xp / next_level_xp)
    bar_width = 600
    bar_height = 20
    bar_x = 170
    bar_y = text_y + 40

    # Draw background of progress bar
    draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], outline=None, fill=(48, 49, 54))

    # Draw progress of progress bar
    draw.rectangle([bar_x, bar_y, bar_x + int(bar_width * progress), bar_y + bar_height],
                   outline=None, fill=(0, 255, 255))

    return rank_card


class Levels(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return  # Ignore messages sent by bots

        if not message.guild:
            return  # Ignore messages sent in DMs

        cursor.execute(
            "SELECT user_id, user, guild_id, exp, level, last_lvl FROM levels WHERE user_id = ? AND guild_id = ?",
            (message.author.id, message.guild.id)
        )
        result = cursor.fetchone()

        if result is None:
            cursor.execute(
                "INSERT INTO levels(user_id, user, guild_id, exp, level, last_lvl) VALUES (?, ?, ?, ?, ?, ?)",
                (message.author.id, message.author.name, message.guild.id, 0, 0, 0)
            )
            database.commit()
        else:
            exp = result[3]
            lvl = result[4]
            last_lvl = result[5]

            exp_gained = random.randint(1, 5)
            exp += exp_gained
            lvl = 0.15 * (math.sqrt(exp))

            cursor.execute(
                "UPDATE levels SET exp = ?, level = ? WHERE user_id = ? AND guild_id = ?",
                (exp, lvl, message.author.id, message.guild.id)
            )
            database.commit()

            if int(lvl) > last_lvl:
                await message.channel.send(f"{message.author.mention} has leveled up to level {int(lvl)}!")
                cursor.execute(
                    "UPDATE levels SET last_lvl = ? WHERE user_id = ? AND guild_id = ?",
                    (int(lvl), message.author.id, message.guild.id)
                )
                database.commit()

    @nextcord.slash_command(
        name="level",
        description="Check the levels of a user"
    )
    async def levels(self, interaction: nextcord.Interaction, member: nextcord.Member):

        cursor.execute("SELECT exp, level, last_lvl FROM levels WHERE user_id = ? AND guild_id = ?", (member.id, member.guild.id,))
        result_user = cursor.fetchone()

        if result_user:
            exp = result_user[0]
            level = result_user[1]
            next_lvl_xp = ((int(level) + 1) / 0.15) ** 2
            next_lvl_xp = int(next_lvl_xp)

            # Calculate rank (example: fetch from database or calculate based on experience points)
            cursor.execute("SELECT COUNT(*) FROM levels WHERE guild_id = ? AND exp > ?", (member.guild.id, exp))
            rank = cursor.fetchone()[0] + 1

            # Fetch avatar as bytes from URL
            avatar_bytes = requests.get(member.avatar.url).content

            # Create the rank card
            rank_card = create_rank_card(member.name, avatar_bytes, exp, next_lvl_xp, level, rank)

            # Convert the rank card to bytes
            with io.BytesIO() as image_binary:
                rank_card.save(image_binary, 'PNG')
                image_binary.seek(0)
                await interaction.response.send_message(file=nextcord.File(fp=image_binary, filename='rank_card.png'))
        else:
            await interaction.response.send_message("User not found in the database.")


def setup(bot: commands.Bot):
    print("Levels Cog Registered")
    bot.add_cog(Levels(bot))
