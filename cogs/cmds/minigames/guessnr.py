import nextcord
from nextcord.ext import commands
import random
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config/config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()


intents = nextcord.Intents.all()

class Guess(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="guess_nr",
        description="Guess a number game!"
    )
    async def guess(self, i: nextcord.Interaction):
        secret_number = random.randint(1, 100)
        attempts = 0

        await i.response.send_message("I've picked a number between 1 and 100. Try to guess it! You have 5 attempts.")

        while attempts < 5:
            try:
                # Wait for user's guess
                guess_message = await self.bot.wait_for(
                    "message",
                    timeout=30.0,
                    check=lambda m: m.author == i.user and m.channel == i.channel,
                )

                # Parse user's guess
                user_guess = int(guess_message.content)
                attempts += 1

                # Check if the guess is correct
                if user_guess == secret_number:
                    # Update economy table for user
                    cursor.execute("""
                        SELECT user_id, user, bank FROM economy WHERE user_id = ? AND guild_id = ?
                    """, (i.user.id, i.guild.id))
                    result = cursor.fetchone()
                    if result is None:
                        cursor.execute("""
                            INSERT INTO economy(user_id, user, bank, guild_id) VALUES (?, ?, ?, ?)
                        """, (i.user.id, i.user.name, 10, i.guild.id))
                    else:
                        bank = result[2] + 10
                        cursor.execute("""
                            UPDATE economy SET bank = ? WHERE user_id = ? AND guild_id = ?
                        """, (bank, i.user.id, i.guild.id))
                    database.commit()

                    # Update minigames table for user
                    cursor.execute("""
                        SELECT user_id, user, guessnr_wins FROM minigames WHERE user_id = ? AND guild_id = ?
                    """, (i.user.id, i.guild.id))
                    result = cursor.fetchone()
                    if result is None:
                        cursor.execute("""
                            INSERT INTO minigames(user_id, user, guessnr_wins, guild_id) VALUES (?, ?, ?, ?)
                        """, (i.user.id, i.user.name, 1, i.guild.id))
                    else:
                        wins = result[2] if result[2] is not None else 0
                        wins += 1
                        cursor.execute("""
                            UPDATE minigames SET guessnr_wins = ? WHERE user_id = ? AND guild_id = ?
                        """, (wins, i.user.id, i.guild.id))
                    database.commit()

                    await i.followup.send(f"Eyy congratulations {i.user.mention} you guessed the right number!!")
                    break

                elif user_guess > secret_number:
                    await i.followup.send("Sorry, the correct number is lower!")
                else:
                    await i.followup.send("Sorry, the correct number is higher!")

            except ValueError:
                await i.followup.send("Please enter a valid number between 1 and 100.")
            except nextcord.errors.TimeoutError:
                await i.followup.send(f"Time's up! The correct number was {secret_number}. Better luck next time.")
                break

        if attempts >= 5:
            await i.followup.send(f"You've used all your attempts. The correct number was {secret_number}. Try again later.")

def setup(bot: commands.Bot):
    print("Guess Cog Registered")
    bot.add_cog(Guess(bot))
