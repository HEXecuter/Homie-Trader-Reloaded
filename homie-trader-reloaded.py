from dotenv import load_dotenv
from os import getenv
from nextcord.ext import commands
import nextcord
from datetime import datetime
from random import randint
from mysql_db.discordmodels import get_user, User
from mysql_db.mysql_schema import create_schema
import mysql.connector


load_dotenv()

# Create database connection and generate schema if it doesn't exist
db = mysql.connector.connect(
        host=getenv("MYSQL_HOST"),
        port=getenv("MYSQL_PORT"),
        user=getenv("MYSQL_USER"),
        password=getenv("MYSQL_PASSWORD"),
        database="discord")
cur = db.cursor()
create_schema(cur)
db.commit()


# Setup Bot and gain access to guild member information
TOKEN = getenv("DISCORD_TOKEN")
intents = nextcord.Intents.default()
intents.members = True
bot = commands.Bot()


# TODO: Change description, add DB, create user object
@bot.slash_command(guild_ids=[868296265564319774])
async def create_account(interaction: nextcord.Interaction, pet_name: str):
    """Use this command to get started trading, include your pet's name to stay motivated 🙈"""
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id)
    if user_obj is None:
        user_obj = User.create_user(cursor, interaction.user.id, interaction.guild_id, pet_name)
        db.commit()
        response = nextcord.Embed(title="Welcome to Homie Market!", color=0x00e1ff)
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
                  f"but I have also kidnapped {pet_name}. Pay me back $100,000 and you can " \
                  f"have {pet_name} back. Hurry before someone else purchases it from me.\n\n" \
                  f"I recommend you get a job to start earning some money. You can mint NFTs based " \
                  f"on yourself or your friends, but you can only mint one. Each NFT is assigned a " \
                  f"random stock ticker that follows the performance of their real life counterpart.\n```"
        await interaction.response.send_message(content=content, embed=response, tts=True)
    else:
        # TODO: Tell user they already have an account
        pass


bot.run(TOKEN)
