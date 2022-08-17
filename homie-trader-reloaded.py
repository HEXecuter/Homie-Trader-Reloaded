from dotenv import load_dotenv
from os import getenv
import discord
from nextcord.ext import commands
import nextcord
from datetime import datetime
from functools import partial
from random import randint


FLUCTUATION_MULTIPLIER = 5.0
DEBUG = 1


load_dotenv()
TOKEN = getenv("DISCORD_TOKEN")
intents = nextcord.Intents.default()
intents.members = True
bot = commands.Bot()


# TODO: Change description, add DB, create user object
@bot.slash_command(guild_ids=[868296265564319774])
async def create_account(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Welcome to Homie Trader!", color=0x00e1ff)
    response.description = f"Hello {interaction.user.display_name},\nI hope you realize what you are getting into."
    response.add_field(name="Date you joined Discord", value="```\n" + interaction.user.created_at.strftime("%m/%d/%Y") + "\n```", inline=True)
    response.add_field(name="Date you joined Homie Market", value="```\n" + datetime.now().strftime("%m/%d/%Y") + "\n```", inline=True)
    response.add_field(name="Date you will be the happiest",
                       value=f"```\n{randint(1, 12):02}/{randint(1, 28):02}/{randint(2023, 2040)}\n```", inline=True)
    response.add_field(name="Date you will finally ḏ̷̃_̷̲̆ ̸̱̔_̴͇̉ ̴̭͠_̶̦̎ ̵͔̿_̶̪́ ̴̳͝e̵̟͌ forever",
                       value=f"```\n{randint(1,12):02}/{randint(1,28):02}/2̶̺̘̈͊0̷̢̎̀?̷̘̅?̸̢͓͘\n```", inline=True)
    response.set_image(bot.user.avatar.url)
    await interaction.response.send_message(embed=response)


bot.run(TOKEN)
