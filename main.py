from dotenv import load_dotenv
from os import getenv
from nextcord.ext import commands
import nextcord
from datetime import datetime, date, timedelta
from random import randint, choice, uniform
from mysql_db.discordmodels import get_user, User, Nft
from mysql_db.mysql_schema import create_schema
import mysql.connector
from homie_assets import movies, degrees, majors, slanders
from decimal import Decimal
# TODO: Change Finnhub to aiohttp
import finnhub
from PIL import Image
from io import BytesIO
import logging

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler("homie.log")
formatting = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s")
stream_handler.setFormatter(formatting)
file_handler.setFormatter(formatting)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
load_dotenv()
if getenv("HOMIE_LOG") == "INFO":
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)

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

volatility_multiplier = getenv("VOLATILITY_MULTIPLIER")

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
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def target_not_found_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="User does not Have an Account", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"The user you specified does not have a Homie Trader account."
    response.set_thumbnail("https://i.kym-cdn.com/photos/images/facebook/001/083/714/6f5.jpg")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def pet_not_found_response(interaction: nextcord.Interaction, user_name):
    response = nextcord.Embed(title=f"{user_name} does not Have a Pet to Steal", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"{user_name} does not have a pet we can steal. Convince them to create an account first. " \
                           f"Then we can hire someone to kidnap their dog."
    response.set_thumbnail("https://wojakparadise.net/wojak/13382/img")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def pet_already_owned_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title=f"You Are Already in Possession of this Pet", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"You are already the owner of this. No need to steal from yourself."
    response.set_thumbnail("https://wojakparadise.net/wojak/13382/img")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def job_not_found_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Apply for a Job First", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"You need to get a job before you can use this command. Use the " \
                           f"`/job apply [job_title] [company_name]` "
    response.set_thumbnail("https://preview.redd.it/4naeoad970351.jpg?auto=webp&s="
                           "8382476bcdc1ff875a65b9650af3915f42f26854")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def wrong_file_type_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Wrong File Type", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"This is not a supported image type. Supply a `JPG` or `PNG`!"
    response.set_thumbnail("https://i.pinimg.com/564x/96/3b/e6/963be6d5b60feec95a39ced9ea85f907.jpg")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def symbol_in_use(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="This Stock Symbol is in Use", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"This stock symbol is being used by an existing NFT, select another stock symbol!"
    response.set_thumbnail("https://i.pinimg.com/564x/96/3b/e6/963be6d5b60feec95a39ced9ea85f907.jpg")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def paycheck_already_redeemed_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Wait for your Next Paycheck", color=0x00e1ff)
    selected_movie = choice(list(movies.keys()))
    response.description = f"{interaction.user.display_name},\n" \
                           f"You already got paid today. It ain't my fault you're broke! Wait until tomorrow to " \
                           f"receive your next paycheck. In the meantime, you can watch {selected_movie} " \
                           f"{seconds_until_midnight() / movies[selected_movie]['duration']:.4f} times!"
    response.set_image(movies[selected_movie]["image"])
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def no_nft_channel_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="No NFT Text Channel Found", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"There is no NFT channel on this server. Please create " \
                           f"a text channel with the words `nft` and `museum`. " \
                           f"Make sure I have access to the channel. If you " \
                           f"are a peasant without admin rights, get an admin to help."
    response.set_image("https://i.kym-cdn.com/photos/images/original/001/761/805/b8c.jpg")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def invalid_symbol_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Invalid Stock Symbol Entered", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"That stock symbol does not exist. Use the following website to " \
                           f"search for US based stock symbols. https://stockanalysis.com/stocks/"
    response.set_image("https://i.kym-cdn.com/photos/images/original/000/509/739/490.jpg")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


def get_nft_channel(interaction: nextcord.Interaction):
    for text_channel in interaction.guild.channels:
        if 'nft' in text_channel.name.lower() and 'museum' in text_channel.name.lower() and text_channel.type.name == 'text':
            return text_channel
    else:
        return None


def get_role(interaction: nextcord.Interaction, role_name):
    for role in interaction.guild.roles:
        if role_name == role.name:
            return role
    else:
        return None


async def creating_power_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="You Already Made an NFT", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"You already made an NFT for this channel and can not make any more. " \
                           f"If you would like to mint another NFT, that's too bad."
    response.set_image("https://i.pinimg.com/originals/e2/78/13/e27813e577548baadaa53ad737b6a5cd.gif")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def image_not_square_response(interaction: nextcord.Interaction):
    response = nextcord.Embed(title="Upload a More Square-ish Image", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"This image is not square-ish enough. Crop it to be closer to a square."
    response.set_image("https://i.pinimg.com/originals/e2/78/13/e27813e577548baadaa53ad737b6a5cd.gif")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def nft_exists_response(interaction: nextcord.Interaction, username):
    response = nextcord.Embed(title=f"{username} Already Has an NFT", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"{username} already has an NFT named after them. Find another person to clown on!"
    response.set_image("https://i.pinimg.com/originals/e2/78/13/e27813e577548baadaa53ad737b6a5cd.gif")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def nft_not_exists_response(interaction: nextcord.Interaction, username):
    response = nextcord.Embed(title=f"{username} Does Not Have an NFT", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"{username} does not have an NFT based on them. Create an NFT based on them, or " \
                           f"select a different user."
    response.set_image("https://i.pinimg.com/originals/e2/78/13/e27813e577548baadaa53ad737b6a5cd.gif")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def too_poor_response(interaction: nextcord.Interaction, total_cost):
    response = nextcord.Embed(title=f"{interaction.user.display_name} is Poor!", color=0x00e1ff)
    response.description = f"@here " \
                           f"{interaction.user.mention} just tried to buy something and they could not afford it " \
                           f"because they are poor! Come back when you have `${total_cost:,.2f}`"
    response.set_image("https://i.kym-cdn.com/entries/icons/mobile/000/029/831/spongebobmeme.jpg")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def not_enough_owned_response(interaction: nextcord.Interaction, amount_needed, amount_owned):
    response = nextcord.Embed(title=f"You Don't Own Enough of That NFT!", color=0x00e1ff)
    response.description = f"Sorry {interaction.user.display_name}, I ain't takin' yo' yee-yee ahh credit." \
                           f" Come around my crib again when you a little.. mmm, pimpin'."
    response.add_field(name=f"Amount Owned", value=f"```\n{amount_owned:,}\n```", inline=True)
    response.add_field(name=f"Amount Needed", value=f"```\n{amount_needed:,}\n```", inline=True)
    response.set_image("https://i.kym-cdn.com/photos/images/newsfeed/002/010/016/a14.png")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)


async def too_poor_pet_response(interaction: nextcord.Interaction, total_cost, action):
    response = nextcord.Embed(title=f"{interaction.user.display_name} is Poor!", color=0x00e1ff)
    response.description = f"@here " \
                           f"{interaction.user.mention} just tried to {action} and they could not afford it " \
                           f"because they are poor! Come back when you have `${total_cost:,.2f}`"
    response.set_image("https://i.kym-cdn.com/entries/icons/mobile/000/029/831/spongebobmeme.jpg")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
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
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} is attempting to create an account")
    finn = finnhub.Client(getenv("FINN_TOKEN"))
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id, finn, volatility_multiplier)
    # Check if user already has an account, create one if they do not
    if user_obj is None:
        user_obj = User.create_user(cursor, interaction.user.id, interaction.guild_id, pet_name,
                                    finn, volatility_multiplier)
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
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} successfully created an account")
    else:
        # Tell user they already have an account
        response = nextcord.Embed(title="Certified Brainlet Moment", color=0x00e1ff)
        content = f"```\n{interaction.user.display_name}, you already have an account. " \
                  f"Get your money up, not your funny up.\n```"
        response.set_thumbnail("https://preview.redd.it/yhb6wfnd0q321.png?auto=webp&s="
                               "27e460a8ee79823a538d730cc5e8b25373375fed")
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} already had an account")
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
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} is applying for a job")
    finn = finnhub.Client(getenv("FINN_TOKEN"))
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id, finn, volatility_multiplier)
    # Check if user already has an account, create one if they do not
    if user_obj is None:  # User does not have an account
        await account_not_found_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have an account")
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
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name}"
                     f" is now the {job_title} at {company_name}")


@job.subcommand()
async def paycheck(interaction: nextcord.Interaction):
    """Use this command to ✨get paid✨ daily"""
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} is attempting to get a paycheck")
    finn = finnhub.Client(getenv("FINN_TOKEN"))
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id, finn, volatility_multiplier)
    if user_obj is None:  # If user does not have an account
        await account_not_found_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have an account")
        return
    elif user_obj.job_title is None:  # If user does not have a job
        await job_not_found_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have a job")
        return
    elif user_obj.paycheck_redeemed == date.today():  # If user already got paid
        await paycheck_already_redeemed_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} already got paid")
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
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} successfully got paid")


@bot.slash_command(guild_ids=[868296265564319774])
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
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} is attempting to mint an nft")
    await interaction.response.defer()
    finn = finnhub.Client(getenv("FINN_TOKEN"))
    stock_symbol = stock_symbol.replace("$", "").upper()
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id, finn, volatility_multiplier)
    if user_obj is None:  # If user does not have an account
        await account_not_found_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have an account")
        return

    if user_obj.symbol_exists(stock_symbol):
        await symbol_in_use(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} supplied a duplicate symbol: "
                     f"{stock_symbol}")
        return

    if image.content_type not in ('image/jpeg', 'image/jpg', 'image/png'):
        await wrong_file_type_response(interaction)
        logger.warning(f"{interaction.user.display_name} from {interaction.guild.name} "
                       f"supplied a file of {image.content_type}")
        return

    # TODO: Check for square-ish image
    ratio = image.height / image.width
    if ratio < 0.75 or ratio > 1.25:
        await image_not_square_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not supply a square image")
        return

    # Check NFT already exist for user
    if user_obj.nft_exists(based_on.id):
        await nft_exists_response(interaction, based_on.display_name)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} supplied a duplicate user")
        return

    if user_obj.creating_power < 1:
        await creating_power_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} ran out of creating power:"
                     f" {user_obj.creating_power}")
        return

    nft_channel = get_nft_channel(interaction)  # If there is no dedicated NFT channel
    if nft_channel is None:
        await no_nft_channel_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} failed to have "
                     f"a dedicated NFT channel")
        return

    image_storage = bot.get_partial_messageable(1011084374126624820)
    stock_change = finn.quote(stock_symbol)["dp"]
    if stock_change is None:
        await invalid_symbol_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} supplied an invalid symbol:"
                     f" {stock_symbol}")
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

    role = get_role(interaction, f"${stock_symbol} Homie")
    if role is None:
        role = await interaction.guild.create_role(name=f"${stock_symbol} Homie", color=0x00e1ff, reason="NFT Creation")
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} created role:"
                     f" ${stock_symbol} Homie")
    await based_on.add_roles(role, reason="NFT Creation")

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
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} successfully created nft:"
                 f" {based_on.display_name}")


@nft.subcommand()
async def info(interaction: nextcord.Interaction, based_on: nextcord.Member):
    """Use this command to purchase an NFT

    Parameters
    _____________
    based_on:
        The user the NFT is based on
    """
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} is attempting an info on:"
                 f" {based_on.display_name}")
    await interaction.response.defer()
    finn = finnhub.Client(getenv("FINN_TOKEN"))
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id, finn, volatility_multiplier)
    if user_obj is None:  # If user does not have an account
        await account_not_found_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have an account")
        return
    # Check NFT already exist for user
    if not user_obj.nft_exists(based_on.id):
        await nft_not_exists_response(interaction, based_on.display_name)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} target user did not "
                     f"have an account")
        return

    nft_id = user_obj.get_nft_id(based_on.id)
    nft_obj = Nft(cursor, nft_id)
    nft_price = user_obj.get_nft_cost(nft_id)
    response = nextcord.Embed(title=f"{nft_obj.name}NFT", color=0x00e1ff)
    response.add_field(name=f"Current Value", value=f"```\n{nft_price:,.2f}\n```", inline=True)
    response.add_field(name=f"Percent Change", value=f"```\n{nft_obj.percent_change:,.2%}\n```", inline=True)
    response.add_field(name=f"Based On", value=f"```\n{based_on.display_name}\n```", inline=False)
    response.add_field(name="Name", value=f"```\n{nft_obj.name}\n```", inline=False)
    response.set_image(nft_obj.image)
    await interaction.followup.send(embed=response)
    db.commit()
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} successfully completed an info on:"
                 f" {based_on.display_name}")


@bot.slash_command(guild_ids=[868296265564319774])
async def purchase(interaction: nextcord.Interaction):
    """Main command for purchase related subcommands"""
    pass


@purchase.subcommand()
async def degree(interaction: nextcord.Interaction, degree_type: str = nextcord.SlashOption(choices=degrees.keys()),
                 amount: int = nextcord.SlashOption(min_value=1, max_value=100)):
    """Use this command to ✨bribe✨ a school official into giving you a degree

    Parameters
    _____________
    degree_type:
        Choose from the list of options, more expensive degrees provide better returns
    amount:
        The amount of degrees you want to purchase
    """
    logger.debug(
        f"{interaction.user.display_name} from {interaction.guild.name} is attempting to buy a degree of type: "
        f"{degree_type}")
    finn = finnhub.Client(getenv("FINN_TOKEN"))
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id, finn, volatility_multiplier)
    if user_obj is None:  # If user does not have an account
        await account_not_found_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have an account")
        return

    total_cost = degrees[degree_type]["price"] * amount
    if user_obj.buying_power < total_cost:
        await too_poor_response(interaction, total_cost)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have enough funds")
        return

    multiplier = degrees[degree_type]["stat"] * amount
    friendly_name = degrees[degree_type]["friendly_name"]
    industry = choice(range(len(majors)))

    user_obj.charge_user(total_cost)
    user_obj.add_modifier(multiplier, amount, degree_type, industry)

    response = nextcord.Embed(title="New Modifiers Purchased!", color=0x00e1ff)
    response.description = f"Congratulations on all the hard work it took to get {amount} {friendly_name}! " \
                           f"Your paycheck has now gone up!"
    response.add_field(name=f"Total Cost", value=f"```\n${total_cost:,.2f}\n```", inline=True)
    response.add_field(name=f"Account Balance", value=f"```\n${user_obj.buying_power:,.2f}\n```", inline=True)
    response.add_field(name=f"Degree Major", value=f"```\n{majors[industry]}\n```", inline=False)
    response.set_thumbnail(bot.user.avatar.url)
    await interaction.response.send_message(embed=response)
    db.commit()
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} successfully bought a degree of type:"
                 f" {degree_type}")


# TODO: Check if symbol is already in use
@purchase.subcommand()
async def stock(interaction: nextcord.Interaction, based_on: nextcord.Member,
                amount: int = nextcord.SlashOption(min_value=1, max_value=100)):
    """Use this command to purchase an NFT

        Parameters
        _____________
        based_on:
            The user the NFT is based on
        amount:
            The amount of NFTs you want to purchase
        """
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} is attempting to buy {amount} "
                 f"NFTs of type: {based_on.display_name}")
    await interaction.response.defer()
    finn = finnhub.Client(getenv("FINN_TOKEN"))
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id, finn, volatility_multiplier)
    if user_obj is None:  # If user does not have an account
        await account_not_found_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have an account")
        return
    # Check NFT already exist for user
    if not user_obj.nft_exists(based_on.id):
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} target user did not have an "
                     f"account")
        await nft_not_exists_response(interaction, based_on.display_name)
        return

    nft_id = user_obj.get_nft_id(based_on.id)
    nft_price = user_obj.get_nft_cost(nft_id)
    total_cost = nft_price * amount
    if user_obj.buying_power < total_cost:
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have enough funds")
        await too_poor_response(interaction, total_cost)
        return
    user_obj.purchase_nft(nft_id, amount)
    user_obj.charge_user(total_cost)
    nft_obj = Nft(cursor, nft_id)
    response = nextcord.Embed(title=f"Purchased {nft_obj.name} Stonks", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"`You have successfully purchased the NFT based on {based_on.display_name}`"
    response.add_field(name=f"Amount Purchased", value=f"```\n{amount:,}\n```", inline=True)
    response.add_field(name=f"Price per Unit", value=f"```\n${nft_price:,.2f}\n```", inline=True)
    response.add_field(name=f"NFT Name", value=f"```\n{nft_obj.name}\n```", inline=False)
    response.add_field(name=f"Account Balance", value=f"```\n${user_obj.buying_power:,.2f}\n```", inline=False)
    response.add_field(name=f"NFT Symbol", value=f"```\n${nft_obj.symbol}\n```", inline=False)
    response.set_thumbnail("https://i.kym-cdn.com/entries/icons/mobile/000/029/959/"
                           "Screen_Shot_2019-06-05_at_1.26.32_PM.jpg")
    await interaction.followup.send(embed=response)
    db.commit()
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} successfully bought an NFT based on:"
                 f" {based_on.display_name}")


@purchase.subcommand()
async def kidnap_pet(interaction: nextcord.Interaction, pet_owner: nextcord.Member):
    """Use this command to hire a team of bandits to indefinitely borrow a pet

    Parameters
    _____________
    pet_owner:
        The owner who's pet you want to borrow
    """
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} is attempting to buy a kidnapping")
    finn = finnhub.Client(getenv("FINN_TOKEN"))
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id, finn, volatility_multiplier)
    target_obj = get_user(cursor, pet_owner.id, pet_owner.guild.id, finn, volatility_multiplier)
    if user_obj is None:  # If user does not have an account
        await account_not_found_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have an account")
        return
    if target_obj is None:
        await pet_not_found_response(interaction, pet_owner.display_name)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} target did not have a pet:"
                     f" {pet_owner.display_name}")
        return

    if interaction.user.id == target_obj.pet_owner:
        await pet_already_owned_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} already owns the target's pet:"
                     f" {pet_owner.display_name}")
        return

    if user_obj.user_id == target_obj.user_id:
        total_price = target_obj.pet_price
        if user_obj.buying_power < total_price:
            await too_poor_pet_response(interaction, total_price, f"rescue their own pet {user_obj.pet_name},")
            logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} couldn't afford their own pet")
            return
    else:
        total_price = Decimal("200000")
        if user_obj.buying_power < total_price:
            await too_poor_pet_response(interaction, total_price, f"kidnap {pet_owner.mention} pet "
                                                                  f"{target_obj.pet_name},")
            logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} couldn't afford target's pet:"
                         f" {pet_owner.display_name}")
            return
    user_obj.charge_user(total_price)
    target_obj.pet_stolen(user_obj.discord_id)
    response = nextcord.Embed(title=f"{target_obj.pet_name} Successfully Kidnapped", color=0x00e1ff)
    response.description = f"The operation to kidnap {pet_owner.display_name}'s pet was a " \
                           f"success. Stay vigilant to ensure they do not retaliate."
    response.add_field(name=f"Kidnap Cost", value=f"```\n${total_price:,.2f}\n```", inline=True)
    response.add_field(name=f"Account Balance", value=f"```\n${user_obj.buying_power:,.2f}\n```", inline=True)
    response.set_thumbnail("https://wojakparadise.net/wojak/13382/img")
    await interaction.response.send_message(embed=response)
    db.commit()
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} successfully kidnapped pet:"
                 f" {pet_owner.display_name}")


@purchase.subcommand()
async def slander(interaction: nextcord.Interaction, based_on: nextcord.Member):
    """Use this command to purchase an NFT

        Parameters
        _____________
        based_on:
            The user the NFT is based on
        """
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} is attempting to slander:"
                 f" {based_on.display_name}")
    await interaction.response.defer()
    finn = finnhub.Client(getenv("FINN_TOKEN"))
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id, finn, volatility_multiplier)
    if user_obj is None:  # If user does not have an account
        await account_not_found_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have an account")
        return
    # Check NFT already exist for user
    if not user_obj.nft_exists(based_on.id):
        await nft_not_exists_response(interaction, based_on.display_name)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} target did not have an account")
        return

    nft_id = user_obj.get_nft_id(based_on.id)
    nft_obj = Nft(cursor, nft_id)
    nft_price = user_obj.get_nft_cost(nft_id)
    if user_obj.buying_power < Decimal("50000"):
        await too_poor_response(interaction, Decimal("50000"))
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have enough funds")
        return
    change = Decimal(-round(uniform(0.05, 0.3), 2))
    new_value = nft_price * (Decimal("1") + change)
    user_obj.charge_user(Decimal(50000))
    user_obj.change_nft_price(new_value, change, nft_id)
    response = nextcord.Embed(title=f"Journalist has Written a Slanderous Article on an NFT", color=0x00e1ff)
    response.description = f"@here {interaction.user.display_name} has commissioned a journalist to write a " \
                           f"slanderous article on the NFT based on {based_on.mention}. The article alleges that " \
                           f"{choice(slanders)} This article has resulted in the NFT's price going down by " \
                           f"{change:,.2%}."
    response.add_field(name=f"New Price", value=f"```\n{new_value:,.2f}\n```", inline=True)
    response.add_field(name=f"Percent Change", value=f"```\n{change:,.2%}\n```", inline=True)
    response.add_field(name=f"NFT Name", value=f"```\n{nft_obj.name}\n```", inline=False)
    response.set_thumbnail("https://wojakparadise.net/wojak/6196/img")
    await interaction.followup.send(embed=response)
    db.commit()
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} successfully slandered:"
                 f" {based_on.display_name} by {change:,.2%}")


@bot.slash_command(guild_ids=[868296265564319774])
async def sell_stock(interaction: nextcord.Interaction, based_on: nextcord.Member,
                     amount: int = nextcord.SlashOption(min_value=1, max_value=100)):
    """Use this command to sell an NFT

        Parameters
        _____________
        based_on:
            The user the NFT is based on
        amount:
            The amount of NFTs you want to purchase
        """
    logger.debug(
        f"{interaction.user.display_name} from {interaction.guild.name} is attempting to sell {amount} of type:"
        f" {based_on.display_name}")
    await interaction.response.defer()
    finn = finnhub.Client(getenv("FINN_TOKEN"))
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id, finn, volatility_multiplier)
    if user_obj is None:  # If user does not have an account
        await account_not_found_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have an account")
        return
    if not user_obj.nft_exists(based_on.id):
        await nft_not_exists_response(interaction, based_on.display_name)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} target NFT did not exist")
        return

    nft_id = user_obj.get_nft_id(based_on.id)
    nft_price = user_obj.get_nft_cost(nft_id)
    total_cost = nft_price * amount
    nft_amount_owned = user_obj.nft_owned_amount(nft_id)
    if nft_amount_owned < amount:
        await not_enough_owned_response(interaction, amount, nft_amount_owned)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not own {amount} NFTs")
        return
    user_obj.sell_nft(nft_id, amount, nft_amount_owned)
    user_obj.charge_user(-total_cost)
    nft_obj = Nft(cursor, nft_id)
    response = nextcord.Embed(title=f"Panic Sold {nft_obj.name} Stonks", color=0x00e1ff)
    response.description = f"{interaction.user.display_name},\n" \
                           f"`You have successfully panic sold the NFT based on {based_on.display_name}`"
    response.add_field(name=f"Amount Sold", value=f"```\n{amount:,}\n```", inline=True)
    response.add_field(name=f"Price per Unit", value=f"```\n${nft_price:,.2f}\n```", inline=True)
    response.add_field(name=f"NFT Name", value=f"```\n{nft_obj.name}\n```", inline=False)
    response.add_field(name=f"Account Balance", value=f"```\n${user_obj.buying_power:,.2f}\n```", inline=False)
    response.add_field(name=f"NFT Symbol", value=f"```\n${nft_obj.symbol}\n```", inline=False)
    response.set_thumbnail("https://i.kym-cdn.com/entries/icons/mobile/000/022/017/thumb.jpg")
    await interaction.followup.send(embed=response)
    db.commit()
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} successfully sold {amount} of type:"
                 f" {based_on.display_name}")


@bot.slash_command(guild_ids=[868296265564319774])
async def portfolio(interaction: nextcord.Interaction, user: nextcord.Member):
    """Use this command to get information on someone's account

    Parameters
    _____________
    user:
        User who's portfolio you want to see

    """
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} is attempting to run a portfolio on:"
                 f" {user.display_name}")
    await interaction.response.defer()
    finn = finnhub.Client(getenv("FINN_TOKEN"))
    cursor = db.cursor()
    user_obj = get_user(cursor, interaction.user.id, interaction.guild_id, finn, volatility_multiplier)
    target_obj = get_user(cursor, user.id, user.guild.id, finn, volatility_multiplier)
    if user_obj is None:  # If user does not have an account
        await account_not_found_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} did not have an account")
        return
    if target_obj is None:
        await target_not_found_response(interaction)
        logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} target did not exists")
        return
    response = nextcord.Embed(title=f"{user.display_name} Portfolio", color=0x00e1ff)
    portfolio_value = user_obj.get_portfolio_value()
    response.add_field(name=f"{target_obj.pet_name} Status", value=f"```\n{target_obj.pet_status}\n```", inline=True)
    response.add_field(name=f"{target_obj.pet_name} Owner", value=f"<@{target_obj.pet_owner}>", inline=True)
    if target_obj.job_title is None:
        response.add_field(name=f"Job Title", value=f"```\nUnemployed\n```", inline=False)
        response.add_field(name=f"Company Name", value=f"```\nUnemployed\n```", inline=False)
    else:
        response.add_field(name=f"Job Title", value=f"```\n{target_obj.job_title}\n```", inline=False)
        response.add_field(name=f"Company Name", value=f"```\n{target_obj.company_name}\n```", inline=False)
    for row in target_obj.get_top_stocks():
        response.add_field(name=f"Symbol", value=f"```\n${row[0]}\n```", inline=True)
        response.add_field(name=f"Total Value", value=f"```\n${row[1] * row[2]:,.2f}\n```", inline=True)
        response.add_field(name=f"Based On", value=f"<@{row[3]}>", inline=True)
        response.add_field(name=f"NFT Name", value=f"```\n{row[4]}\n```", inline=False)
    response.add_field(name=f"Account Balance", value=f"```\n${target_obj.buying_power:,.2f}\n```", inline=False)
    response.add_field(name=f"Portfolio Balance", value=f"```\n${portfolio_value:,.2f}\n```", inline=False)
    await interaction.followup.send(embed=response)
    db.commit()
    logger.debug(f"{interaction.user.display_name} from {interaction.guild.name} successfully ran a portfolio on:"
                 f" {user.display_name}")


@bot.event
async def on_application_command_error(interaction: nextcord.Interaction, error: nextcord.ApplicationInvokeError):
    response = nextcord.Embed(title="Uh Oh Big Stinky", color=0x00e1ff)
    response.description = "Homie Trader just made a big stinky, make sure you are using the command correctly."
    response.set_thumbnail("https://i.ytimg.com/vi/FveF-we6lcE/maxresdefault.jpg")
    if interaction.response.is_done():
        await interaction.followup.send(embed=response)
    else:
        await interaction.response.send_message(embed=response)
    try:
        raise error
    except:  # I know this isn't recommended but I want to log all errors
        logger.exception(f"An error occurred from {interaction.user.display_name} in "
                         f"{interaction.guild.name}")


bot.run(TOKEN)
