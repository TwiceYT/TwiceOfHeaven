import nextcord
from nextcord.ext import commands
import sqlite3
import random
import time
import os
from dotenv import load_dotenv, dotenv_values

# Database file
load_dotenv(dotenv_path='config\config.env')
DBFile = os.getenv("DATABASE_FILE")
database = sqlite3.connect(DBFile)
cursor = database.cursor()



intents = nextcord.Intents.all()


class Player:
    def __init__(self, user):
        self.user = user
        self.health = 100

    def take_damage(self, damage):
        self.health -= damage

class PvP(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players = {}
        self.attack_cooldown = {}

    def add_player(self, player):
        self.players[player.user.id] = player

    def remove_player(self, player):
        del self.players[player.user.id]

    def get_player(self, user):
        return self.players.get(user.id) if hasattr(user, 'id') else None

    def attack(self, attacker, target):
        damage = random.randint(5, 20)
        target.take_damage(damage)

    def can_attack(self, user_id):
        last_attack_time = self.attack_cooldown.get(user_id, 0)
        current_time = time.time()

        # Set your desired cooldown time (in seconds)
        cooldown_time = 5

        return current_time - last_attack_time > cooldown_time

    def update_attack_cooldown(self, user_id):
        self.attack_cooldown[user_id] = time.time()

    @nextcord.slash_command(
        name="pvpjoin",
        description="Join a pvp game!"
    )
    async def join(self, i: nextcord.Interaction):
        player_instance = Player(i.user)
        self.add_player(player_instance)  # Use 'self' to reference the instance of the class
        await i.response.send_message(f"{i.user.name} has joined the PvP Game!!")

    @nextcord.slash_command(
        name="pvpleave",
        description="Leave the pvp arena!"
    )
    async def leave(self, i: nextcord.Interaction):
        player_instance = self.get_player(i.user)  # Use 'self' to reference the instance of the class
        if player_instance:
            self.remove_player(player_instance)
            await i.response.send_message(f"{i.user.name} has left the PvP Game!")
        else:
            await i.response.send_message(f"{i.user.name}, you are not in a PvP arena...")

    @nextcord.slash_command(
        name="pvp_attack",
        description="Attack another member that is in the arena!"
    )
    async def attack(self, i: nextcord.Interaction, target: nextcord.Member):
        attacker = self.get_player(i.user)
        target_player = self.get_player(target)
        player_instance = self.get_player(i.user)

        if attacker and target_player:
            if not self.can_attack(i.user.id):
                await i.response.send_message("You must wait before attacking again.", ephemeral=True)
                return

            damage = random.randint(5, 60)
            target_player.take_damage(damage)

            if target_player.health <= 0:
                # Economy System:
                cursor.execute("SELECT user_id, user, bank FROM economy WHERE user_id = ? AND guild_id = ?", (i.user.id, i.guild_id,))
                result = cursor.fetchone()
                if result is None:
                    cursor.execute("INSERT INTO economy(user_id, user, bank) VALUES (?, ?, ?) WHERE guild_id = ?", (i.user.id, i.user.name, 20, i.guild_id,))
                    database.commit()
                else:
                    bank = result[2] if result[2] is not None else 0
                    bank += 20
                    cursor.execute("UPDATE economy SET bank = ? WHERE user_id = ? AND guild_id = ?", (bank, i.user.id, i.guild_id,))
                    database.commit()

                # Minigames Wins:
                cursor.execute("SELECT user_id, user, pvp_wins FROM minigames WHERE user_id = ? AND guild_id = ?", (i.user.id, i.guild_id,))
                result = cursor.fetchone()
                if result is None:
                    cursor.execute("INSERT INTO minigames(user_id, user, pvp_wins) VALUES (?, ?, ?) WHERE guild_id = ?", (i.user.id, i.user.name, 1))
                    database.commit()
                else:
                    wins = result[2] if result[2] is not None else 0
                    wins += 1
                    cursor.execute("UPDATE minigames SET pvp_wins = ? WHERE user_id = ? AND guild_id = ?", (wins, i.user.id, i.guild_id,))
                    database.commit()

                result = f'{target_player.user.name} has been defeated and is out of the game!'
                self.remove_player(target_player)

            else:
                result = f'{attacker.user.name} attacked {target_player.user.name}! Health Remaining {target_player.health}'

            self.update_attack_cooldown(i.user.id)
        else:
            result = "Invalid target"

        await i.response.send_message(result)

def setup(bot: commands.Bot):
    print("Economy Cog Registered")
    bot.add_cog(PvP(bot))
