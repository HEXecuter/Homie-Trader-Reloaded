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
async def create_account(interaction: nextcord.Interaction,
                         pet_name: str = nextcord.SlashOption(min_length=2, max_length=32)):
    """Use this command to get started trading, include your pet's name to stay ✨motivated✨ 🙈 😉

    Parameters
    _____________
    pet_name: str
        The name of your ✨adorable✨ pet 😉
    """

    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id)
    # Check if user already has an account, create one if they do not
    if user_obj is None:
        user_obj = User.create_user(cursor, interaction.user.id, interaction.guild_id, pet_name)
        db.commit()
        response = nextcord.Embed(title="Welcome to Homie Market!", color=0x00e1ff)
        response.add_field(name="Date you joined Discord",
                           value=f"```\n{interaction.user.created_at.strftime('%m/%d/%Y')}\n```", inline=True)
        response.add_field(name="Date you joined Homie Market",
                           value=f"```\n{datetime.now().strftime('%m/%d/%Y')}\n```", inline=True)
        response.add_field(name="Date you will finally ḏ̷̃_̷̲̆ ̸̱̔_̴͇̉ ̴̭͠_̶̦̎ ̵͔̿_̶̪́ ̴̳͝e̵̟͌",
                           value=f"```\n{randint(1, 12):02}/{randint(1, 28):02}/2̶̺̘̈͊0̷̢̎̀?̷̘̅?̸̢͓͘\n```", inline=True)
        response.set_thumbnail(bot.user.avatar.url)
        content = f"```\nHello {interaction.user.display_name}, I am inside your walls. " \
                  f"Since you do not have any money, I have deposited ${user_obj.buying_power:,.2f} into your account" \
                  f", but I have also kidnapped {pet_name}. Pay me back $100,000.00 and you can " \
                  f"have {pet_name} back. Hurry before someone else purchases it from me.\n\n" \
                  f"I recommend you get a job to start earning some money. You can mint NFTs based " \
                  f"on yourself or your friends, but you can only mint one. Each NFT is assigned a " \
                  f"random stock ticker that follows the performance of their real life counterpart.\n```"
    else:
        # Tell user they already have an account
        response = nextcord.Embed(title="Certified Brainlet Moment", color=0x00e1ff)
        content = f"```\n{interaction.user.display_name}, you already have an account. " \
                  f"Get your money up, not your funny up.\n```"
        response.set_thumbnail("https://preview.redd.it/yhb6wfnd0q321.png?auto=webp&s="
                               "27e460a8ee79823a538d730cc5e8b25373375fed")
    response.add_field(name="Account Balance", value=f"```\n${user_obj.buying_power:,.2f}\n```")
    response.add_field(name=f"{user_obj.pet_name} Status",
                       value=f"```\n{user_obj.pet_status}\n```", inline=True)
    await interaction.response.send_message(content=content, embed=response, tts=True)


bot.run(TOKEN)
