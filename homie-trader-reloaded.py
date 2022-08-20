from dotenv import load_dotenv
from os import getenv
from nextcord.ext import commands
import nextcord
from datetime import datetime, date, timedelta
from random import randint, choice
from mysql_db.discordmodels import get_user, User
from mysql_db.mysql_schema import create_schema
import mysql.connector
from homie_assets import movies
from decimal import Decimal

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


def seconds_until_midnight():
    return ((datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) -
            datetime.now()).seconds


async def account_not_found_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Create an Account First", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
        f"You need to create an account before you can use this command. Use the `/create_account [pet_name]` " \
        f"command to get started. Make sure to include your pet's name! :grin: "
    response.set_thumbnail("https://i.kym-cdn.com/photos/images/facebook/001/083/714/6f5.jpg")
    await interaction.response.send_message(embed=response)


async def job_not_found_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Apply for a Job First", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
        f"You need to get a job before you can use this command. Use the `/job apply [job_title] [company_name]` "
    response.set_thumbnail("https://preview.redd.it/4naeoad970351.jpg?auto=webp&s="
                           "8382476bcdc1ff875a65b9650af3915f42f26854")
    await interaction.response.send_message(embed=response)


async def paycheck_already_redeemed_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Wait for your Next Paycheck", color=0x00e1ff)
    selected_movie = choice(list(movies.keys()))
    response.description = f"{interaction.user.display_name},\n" \
                           f"You already got paid today. It ain't my fault you're broke! Wait until tomorrow to " \
                           f"receive your next paycheck. In the meantime, you can watch {selected_movie} " \
                           f"{seconds_until_midnight()/ movies[selected_movie]['duration']:.4f} times!"
    response.set_image(movies[selected_movie]["image"])
    await interaction.response.send_message(embed=response)


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
    response.add_field(name="Account Balance", value=f"```\n${user_obj.buying_power:,.2f}\n```", inline=True)
    response.add_field(name=f"{user_obj.pet_name} Status",
                       value=f"```\n{user_obj.pet_status}\n```", inline=True)
    await interaction.response.send_message(content=content, embed=response, tts=True)


@bot.slash_command(guild_ids=[868296265564319774])
async def job(interaction: nextcord.Interaction):
    """
    Main command for job related subcommands
    """
    pass


@job.subcommand()
async def apply(interaction: nextcord.Interaction, job_title: str = nextcord.SlashOption(min_length=5, max_length=32),
                company_name: str = nextcord.SlashOption(min_length=5, max_length=32)):
    """use this command to apply for your ✨first and only job✨

    Parameters
    _____________
    job_title: str
        Your desired job title Ex: Professional Pizza Maker
    company_name: str
        The name of the company you want to apply to
    """
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id)
    # Check if user already has an account, create one if they do not
    if user_obj is None:  # User does not have an account
        await account_not_found_response(interaction)
        return
    else:
        # Users are allowed to change job, underlying method ensures they do not game the paycheck system
        user_obj.new_job(job_title, company_name)
        db.commit()
        response = nextcord.Embed(title="Congratulations on the New Job!", color=0x00e1ff)
        content = f"```\nCongratulations {interaction.user.display_name},\n" \
                  f"The hiring manager got confused and hired the wrong person! " \
                  f"Thanks to their mistake, you are now the {user_obj.job_title} at {user_obj.company_name}. Don't " \
                  f"forget to get your paycheck! You can also \"study hard\" and pay " \
                  f"for certifications and degrees that increase your salary.\n```"
        response.add_field(name=f"Job Title", value=f"```\n{user_obj.job_title}\n```", inline=False)
        response.add_field(name=f"Company Name", value=f"```\n{user_obj.company_name}\n```", inline=False)
        response.set_thumbnail("https://i.kym-cdn.com/photos/images/newsfeed/001/716/052/bda.png")
        await interaction.response.send_message(content=content, embed=response)


@job.subcommand()
async def paycheck(interaction: nextcord.Interaction):
    """Use this command to ✨get paid✨ daily"""
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id)
    if user_obj is None:  # If user does not have an account
        await account_not_found_response(interaction)
        return
    elif user_obj.job_title is None:  # If user does not have a job
        await job_not_found_response(interaction)
        return
    elif user_obj.paycheck_redeemed == date.today():  # If user already got paid
        await paycheck_already_redeemed_response(interaction)
        return
    else:
        pay_amount = user_obj.get_paycheck()
        response = nextcord.Embed(title="You Have Received Your Paycheck!")
        response.add_field(name=f"Total Comp", value=f"```\n${pay_amount:,.2f}\n```", inline=True)
        response.add_field(name=f"Multipliers", value=f"```\n{Decimal('1') + user_obj.get_multipliers():,.2f}\n```",
                           inline=True)
        response.add_field(name="Account Balance", value=f"```\n${user_obj.buying_power:,.2f}\n```", inline=False)
        response.add_field(name=f"Job Title", value=f"```\n{user_obj.job_title}\n```", inline=False)
        response.add_field(name=f"Company Name", value=f"```\n{user_obj.company_name}\n```", inline=False)
        await interaction.response.send_message(embed=response)

bot.run(TOKEN)
