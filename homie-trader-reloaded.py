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
    response = nextcord.Embed(title="Welcome to Homie Market!", color=0x00e1ff)
    # response.description = f"Hello {interaction.user.display_name},\nI hope you realize what you are getting into."
    response.add_field(name="Date you joined Discord",
                       value="```\n" + interaction.user.created_at.strftime("%m/%d/%Y") + "\n```", inline=True)
    response.add_field(name="Date you joined Homie Market",
                       value="```\n" + datetime.now().strftime("%m/%d/%Y") + "\n```", inline=True)
    response.add_field(name="Date you will finally ḏ̷̃_̷̲̆ ̸̱̔_̴͇̉ ̴̭͠_̶̦̎ ̵͔̿_̶̪́ ̴̳͝e̵̟͌",
                       value=f"```\n{randint(1, 12):02}/{randint(1, 28):02}/2̶̺̘̈͊0̷̢̎̀?̷̘̅?̸̢͓͘\n```", inline=True)
    response.add_field(name="Account Balance", value="```\n$1,000\n```")
    response.set_thumbnail(bot.user.avatar.url)
    content = f"```\nHello {interaction.user.display_name}, I am inside your walls. " \
              f"Since you do not have any money, I have deposited $1,000 into your account, " \
              f"but I have also kidnapped your dog. Pay me back $100,000 and you can " \
              f"have your dog back. Hurry before someone else purchases her from me.\n\n" \
              f"I recommend you get a job to start earning some money. You can mint NFTs based " \
              f"on yourself or your friends, but you can only mint one. Each NFT is assigned a " \
              f"random stock ticker that follows the performance of their real life counterpart.\n```"
    await interaction.response.send_message(content=content, embed=response, tts=True)


bot.run(TOKEN)
