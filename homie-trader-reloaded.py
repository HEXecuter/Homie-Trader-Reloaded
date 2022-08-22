from dotenv import load_dotenv
from os import getenv
from nextcord.ext import commands
import nextcord
from datetime import datetime, date, timedelta
from random import randint, choice, uniform
from mysql_db.discordmodels import get_user, User
from mysql_db.mysql_schema import create_schema
import mysql.connector
from homie_assets import movies, degrees, majors
from decimal import Decimal
import finnhub
from asyncio import sleep
from PIL import Image
from io import BytesIO

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

finn = finnhub.Client(getenv("FINN_TOKEN"))

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
                           f"You need to create an account before you can use this command. Use the `/create_account" \
                           f" [pet_name]` command to get started. Make sure to include your pet's name! :grin: "
    response.set_thumbnail("https://i.kym-cdn.com/photos/images/facebook/001/083/714/6f5.jpg")
    await interaction.response.send_message(embed=response)


async def job_not_found_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Apply for a Job First", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"You need to get a job before you can use this command. Use the " \
                           f"`/job apply [job_title] [company_name]` "
    response.set_thumbnail("https://preview.redd.it/4naeoad970351.jpg?auto=webp&s="
                           "8382476bcdc1ff875a65b9650af3915f42f26854")
    await interaction.response.send_message(embed=response)


async def wrong_file_type_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Wrong File Type", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"This is not a supported image type. Supply a `JPG` or `PNG`!"
    response.set_thumbnail("https://i.pinimg.com/564x/96/3b/e6/963be6d5b60feec95a39ced9ea85f907.jpg")
    await interaction.response.send_message(embed=response)


async def paycheck_already_redeemed_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Wait for your Next Paycheck", color=0x00e1ff)
    selected_movie = choice(list(movies.keys()))
    response.description = f"{interaction.user.display_name},\n" \
                           f"You already got paid today. It ain't my fault you're broke! Wait until tomorrow to " \
                           f"receive your next paycheck. In the meantime, you can watch {selected_movie} " \
                           f"{seconds_until_midnight() / movies[selected_movie]['duration']:.4f} times!"
    response.set_image(movies[selected_movie]["image"])
    await interaction.response.send_message(embed=response)


async def no_nft_channel_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="No NFT Text Channel Found", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"There is no NFT channel on this server. Please create " \
                           f"a text channel with the words `nft` and `museum`. " \
                           f"Make sure I have access to the channel. If you " \
                           f"are a peasant without admin rights, get an admin to help."
    response.set_image("https://i.kym-cdn.com/photos/images/original/001/761/805/b8c.jpg")
    await interaction.response.send_message(embed=response)


async def invalid_symbol_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Invalid Stock Symbol Entered", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"That stock symbol does not exist. Use the following website to " \
                           f"search for US based stock symbols. https://stockanalysis.com/stocks/"
    response.set_image("https://i.kym-cdn.com/photos/images/original/000/509/739/490.jpg")
    await interaction.followup.send(embed=response)


def get_nft_channel(interaction: nextcord.Interaction):
    for text_channel in interaction.guild.channels[0].channels:
        if 'nft' in text_channel.name.lower() and 'museum' in text_channel.name.lower():
            return text_channel
    else:
        return None


async def creating_power_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="You Already Made an NFT", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"You already made an NFT for this channel and can not make any more. " \
                           f"If you would like to mint another NFT, that's too bad."
    response.set_image("https://i.pinimg.com/originals/e2/78/13/e27813e577548baadaa53ad737b6a5cd.gif")
    await interaction.followup.send(embed=response)


async def nft_exists_response(interaction: nextcord.Interaction, username):
    response = nextcord.Embed(title=f"{username} Already Has an NFT", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"{username} already has an NFT named after them. Find another person to clown on!"
    response.set_image("https://i.pinimg.com/originals/e2/78/13/e27813e577548baadaa53ad737b6a5cd.gif")
    await interaction.followup.send(embed=response)


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
        response.set_thumbnail("https://i.kym-cdn.com/photos/images/facebook/001/749/973/f9e.jpg")
        await interaction.response.send_message(embed=response)
        db.commit()


@bot.slash_command()
async def nft(interaction: nextcord.Interaction):
    """Main command for NFT related sub-commands"""
    pass


@nft.subcommand()
async def mint(interaction: nextcord.Interaction,
               nft_name: str = nextcord.SlashOption(min_length=3, max_length=32),
               based_on: nextcord.Member = nextcord.SlashOption(required=True),
               stock_symbol: str = nextcord.SlashOption(min_length=1, max_length=6),
               image: nextcord.Attachment = nextcord.SlashOption(required=True)):
    """use this command to apply for your ✨first and only job✨

    Parameters
    _____________
    nft_name: str
        The name of your NFT
    based_on: str
        A member of the server nft will be based on
    stock_symbol: str
        The stock symbol the NFT will be based on Ex: TSLA for Tesla Inc.
    image:
        Image that will be your NFT (SQUARE IMAGES WORK BEST)
    """
    await interaction.response.defer()
    stock_symbol = stock_symbol.replace("$", "")
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id)
    if user_obj is None:  # If user does not have an account
        await account_not_found_response(interaction)
        return

    if image.content_type not in ('image/jpeg', 'image/jpg', 'image/png'):
        await wrong_file_type_response(interaction)
        return

    # Check NFT already exist for user
    if user_obj.nft_exists(based_on.id):
        await nft_exists_response(interaction, based_on.display_name)
        return

    if user_obj.creating_power < 1:
        await creating_power_response(interaction)
        return

    nft_channel = get_nft_channel(interaction)  # If there is no dedicated NFT channel
    if nft_channel is None:
        await no_nft_channel_response(interaction)
        return

    image_storage = bot.get_partial_messageable(1011084374126624820)
    await sleep(1)  # I only have 60 API calls per minute :(
    stock_change = finn.quote(stock_symbol.upper())["dp"]
    if stock_change is None:
        await invalid_symbol_response(interaction)
        return
    value = round(uniform(1, 100), 2)
    image_byte = BytesIO(await image.read())
    final_image = BytesIO()
    Image.open(image_byte).resize((500, 500), Image.Resampling.LANCZOS).save(final_image, "PNG")
    final_image.seek(0)
    image_url = await image_storage.send(content=f"Created by: {interaction.user.display_name} \n"
                                                 f"From: {interaction.guild.name}",
                                         file=nextcord.File(fp=final_image, filename=f'{nft_name}.png'))
    image_url = image_url.attachments[0].url
    user_obj.create_nft(nft_name, based_on.id, stock_symbol, image_url, Decimal(value))
    description = f"@here {interaction.user.display_name} has successfully minted a new NFT based on " \
                  f"{based_on.display_name}. ```\nThis NFT is utilizing the ${stock_symbol.upper()} stock symbol " \
                  f"and has its Initial Public Offering set to ${value:,.2f}. \n```You can buy this NFT using \n" \
                  f"`/purchase stock {based_on.display_name} [AMOUNT]`"
    nft_embed = nextcord.Embed(title=f"New NFT {nft_name} has been created!", description=description, color=0x00e1ff)
    nft_embed.add_field(name="Name", value=f"```\n{nft_name}\n```", inline=True)
    nft_embed.add_field(name="IPO Value", value=f"```\n${value:,.2f}\n```", inline=True)
    nft_embed.add_field(name="Stock Symbol", value=f"```\n${stock_symbol}\n```", inline=True)
    nft_embed.add_field(name="Created By", value=f"{interaction.user.mention}", inline=True)
    nft_embed.add_field(name="Based On", value=f"{based_on.mention}", inline=True)
    nft_embed.set_image(url=image_url)
    nft_message = await nft_channel.send(embed=nft_embed)
    db.commit()
    response = nextcord.Embed(title="New NFT Created", color=0x00e1ff)
    response.description = f"`Use the following link to view the NFT`\n" \
                           f"{nft_message.jump_url}"
    response.set_thumbnail("https://i.kym-cdn.com/photos/images/newsfeed/000/191/809/"
                           "me_gusta_mucho_by_megustamuchoplz-d416uqk.png?1319690633")
    await interaction.followup.send(embed=response)


@bot.slash_command()
async def purchase(interaction: nextcord.Interaction):
    """Main command for purchase related subcommands"""
    pass


@purchase.subcommand()
async def degree(interaction: nextcord.Interaction, degree_type: str = nextcord.SlashOption(choices=degrees.keys())):
    pass


@purchase.subcommand()
async def stock(interaction: nextcord.Interaction, user: nextcord.Member):
    pass

bot.run(TOKEN)
