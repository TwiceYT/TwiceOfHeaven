import nextcord
from nextcord.ext import commands
import aiohttp
import html
import random
import asyncio
import sqlite3
import api
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()



intents = nextcord.Intents.default()
intents.members = True


class TriviaButton(nextcord.ui.Button):
    def __init__(self, label, style, callback):
        super().__init__(label=label, style=style)
        self.callback = callback

    async def callback(self, interaction: nextcord.Interaction):
        await self.callback(interaction)

class Trivia(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.correct_answer = None
        self.correct_index = None
        self.answer_given = False  # Flag to track if the correct answer has been given
        self.current_user = None  # Track the user who initiated the trivia command

    async def get_trivia_question(self):
        url = "https://opentdb.com/api.php?amount=1&type=multiple"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                question_data = data['results'][0]
                self.correct_answer = html.unescape(question_data['correct_answer'])
                incorrect_answers = [html.unescape(ans) for ans in question_data['incorrect_answers']]
                answers = [self.correct_answer] + incorrect_answers
                random.shuffle(answers)
                self.correct_index = answers.index(self.correct_answer) + 1
                return question_data, answers

    @nextcord.slash_command(
        name="trivia",
        description="Have fun with some Trivia!!",
        guild_ids=[api.GuildID]
    )
    async def trivia(self, i: nextcord.Interaction):
        self.answer_given = False  # Reset the flag for a new trivia question
        self.current_user = i.user  # Set the current user who initiated the command

        question_data, answers = await self.get_trivia_question()

        question = html.unescape(question_data['question'])

        options = ""
        for idx, answer in enumerate(answers, start=1):
            options += f"{idx}. {answer}\n"

        await i.response.send_message(f"**Question:**\n{question}\n\n**Options:**\n{options}")

        try:
            guess_message = await self.bot.wait_for(
                "message",
                timeout=30.0,
                check=lambda m: m.author == i.user and m.channel == i.channel,
            )

            choice = int(guess_message.content)
            if 1 <= choice <= 4:
                await self.check_answer(guess_message, choice)
        except asyncio.TimeoutError:
            if not self.answer_given:  # Check if the answer hasn't been given already
                await i.followup.send("Time is up!")

    async def check_answer(self, message, choice):
        if self.answer_given:
            return  # Prevent processing if the answer has already been given

        self.answer_given = True  # Set the flag to indicate that the correct answer has been given

        if choice == self.correct_index:
            cursor.execute("""
                SELECT user_id, user, bank FROM economy WHERE user_id = ? AND guild_id = ?
            """, (message.author.id, message.guild.id))
            result = cursor.fetchone()
            if result is None:
                cursor.execute("""
                    INSERT INTO economy(user_id, user, bank, guild_id) VALUES (?, ?, ?, ?)
                """, (message.author.id, message.author.name, 50, message.guild.id))
            else:
                bank = result[2] + 50
                cursor.execute("""
                    UPDATE economy SET bank = ? WHERE user_id = ? AND guild_id = ?
                """, (bank, message.author.id, message.guild.id))
            database.commit()

            cursor.execute("""
                SELECT user_id, user, trivia_wins FROM minigames WHERE user_id = ? AND guild_id = ?
            """, (message.author.id, message.guild.id))
            result = cursor.fetchone()
            if result is None:
                cursor.execute("""
                    INSERT INTO minigames(user_id, user, trivia_wins, guild_id) VALUES (?, ?, ?, ?)
                """, (message.author.id, message.author.name, 1, message.guild.id))
            else:
                wins = result[2] if result[2] is not None else 0
                wins += 1
                cursor.execute("""
                    UPDATE minigames SET trivia_wins = ? WHERE user_id = ? AND guild_id = ?
                """, (wins, message.author.id, message.guild.id))
            database.commit()

            await message.channel.send(f"Correct answer, {message.author.mention}!")
        else:
            await message.channel.send(f"Wrong answer, {message.author.mention}. The correct answer was {self.correct_answer}.")

        # Create and send a persistent "Continue" button
        view = nextcord.ui.View()
        continue_button = TriviaButton(label="Continue", style=nextcord.ButtonStyle.primary, callback=self.continue_trivia)
        view.add_item(continue_button)
        await message.channel.send("Would you like to continue?", view=view)

        self.current_user = None  # Reset the current user

    async def continue_trivia(self, interaction: nextcord.Interaction):
        await self.trivia(interaction)  # Restart the trivia command

def setup(bot: commands.Bot):
    print("Trivia Cog Registered")
    bot.add_cog(Trivia(bot))
