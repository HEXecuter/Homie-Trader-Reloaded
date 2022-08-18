import mysql.connector
from os import getenv
from dotenv import load_dotenv


load_dotenv()
db = mysql.connector.connect(
    host=getenv("MYSQL_HOST"),
    port=getenv("MYSQL_PORT"),
    user=getenv("MYSQL_USER"),
    password=getenv("MYSQL_PASSWORD"),
    database="discord")

cur = db.cursor()

DEBUG = getenv("DEBUG_HOMIE")
if DEBUG == 1:
    pass

# TODO: Add indexes and foreign keys
cur.execute("CREATE TABLE IF NOT EXISTS users("
            "user_id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT, "
            "discord_id BIGINT UNSIGNED NOT NULL, "
            "guild_id BIGINT UNSIGNED NOT NULL, "
            "buying_power DECIMAL(20, 2), "
            "paycheck_redeemed DATE, "
            "creating_power TINYINT NOT NULL, "
            "job_title VARCHAR(32), "
            "company_name VARCHAR(32)"
            ")")

cur.execute("CREATE TABLE IF NOT EXISTS nfts("
            "nft_id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT, "
            "based_on BIGINT UNSIGNED NOT NULL, "
            "current_owner_id BIGINT UNSIGNED NOT NULL, "
            "ticker VARCHAR(10) NOT NULL, "
            "image_url VARCHAR(100) NOT NULL, "
            "last_checked BIGINT NOT NULL, "
            "current_value DECIMAL(20, 2) NOT NULL"
            ")")

cur.execute("CREATE TABLE IF NOT EXISTS pets("
            "owner_id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT,"
            "current_owner BIGINT UNSIGNED NOT NULL DEFAULT 920026662974930954,"
            "purchase_price DECIMAL(20, 2) NOT NULL DEFAULT 100000"
            ")")

cur.execute("CREATE TABLE IF NOT EXISTS portfolio("
            "owner_id INTEGER UNSIGNED NOT NULL, "
            "nft_id INTEGER UNSIGNED NOT NULL, "
            "amount_owned BIGINT UNSIGNED NOT NULL"
            ")")

cur.execute("CREATE TABLE IF NOT EXISTS multipliers("
            "user_id INTEGER UNSIGNED NOT NULL, "
            "stat_multiplier DECIMAL(20, 2) NOT NULL, "
            "degree_type VARCHAR(10) NOT NULL, "
            "industry_id INTEGER UNSIGNED NOT NULL"
            ")")

cur.execute("CREATE TABLE IF NOT EXISTS industries("
            "industry_id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT, "
            "industry_name VARCHAR(100)"
            ")")
