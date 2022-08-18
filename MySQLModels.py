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

# TODO: Remove this section when finished testing table schema
DEBUG = getenv("DEBUG_HOMIE")
if DEBUG == "1":
    # Using multi=True returns a generator of cursor objects, this will cause a command out of sync error
    # unless the generator is cleared
    list(cur.execute("DROP TABLE IF EXISTS users;"
                     "DROP TABLE IF EXISTS nfts;"
                     "DROP TABLE IF EXISTS pets;"
                     "DROP TABLE IF EXISTS multipliers;"
                     "DROP TABLE IF EXISTS industries;"
                     "DROP TABLE IF EXISTS portfolio;",
                     multi=True))

# TODO: Add foreign keys
cur.execute("CREATE TABLE IF NOT EXISTS users("
            "user_id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT, "
            "discord_id BIGINT UNSIGNED NOT NULL, "
            "guild_id BIGINT UNSIGNED NOT NULL, "
            "buying_power DECIMAL(20, 2), "
            "paycheck_redeemed DATE, "
            "creating_power TINYINT NOT NULL, "
            "job_title VARCHAR(32), "
            "company_name VARCHAR(32))"
            "")
# Using multi=True returns a generator of cursor objects, this will cause a command out of sync error
# unless the generator is cleared
list(cur.execute("CREATE INDEX users_discord_id_idx ON users(discord_id);"
                 "CREATE INDEX users_guild_id_idx ON users(guild_id);",
                 multi=True))

cur.execute("CREATE TABLE IF NOT EXISTS nfts("
            "nft_id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT, "
            "based_on BIGINT UNSIGNED NOT NULL, "
            "current_owner BIGINT UNSIGNED NOT NULL, "
            "guild_id BIGINT UNSIGNED NOT NULL, "
            "ticker VARCHAR(10) NOT NULL, "
            "image_url VARCHAR(100) NOT NULL, "
            "last_checked BIGINT NOT NULL, "
            "current_value DECIMAL(20, 2) NOT NULL"
            ")")
list(cur.execute("CREATE INDEX nfts_based_on_idx ON nfts(based_on);"
                 "CREATE INDEX nfts_current_owner_idx ON nfts(current_owner);"
                 "CREATE INDEX nfts_guild_id_idx ON nfts(guild_id);",
                 multi=True))

cur.execute("CREATE TABLE IF NOT EXISTS pets("
            "owner_id INTEGER UNSIGNED NOT NULL,"
            "guild_id BIGINT UNSIGNED NOT NULL, "
            "current_owner BIGINT UNSIGNED NOT NULL DEFAULT 920026662974930954,"
            "purchase_price DECIMAL(20, 2) NOT NULL DEFAULT 100000"
            ")")

cur.execute("CREATE TABLE IF NOT EXISTS portfolio("
            "owner_id INTEGER UNSIGNED NOT NULL, "
            "nft_id INTEGER UNSIGNED NOT NULL, "
            "amount_owned BIGINT UNSIGNED NOT NULL"
            ")")
cur.execute("CREATE INDEX portfolio_owner_id_idx ON portfolio(owner_id)")

cur.execute("CREATE TABLE IF NOT EXISTS multipliers("
            "user_id INTEGER UNSIGNED NOT NULL, "
            "stat_multiplier DECIMAL(20, 2) NOT NULL, "
            "degree_type VARCHAR(10) NOT NULL, "
            "industry_id INTEGER UNSIGNED NOT NULL"
            ")")
list(cur.execute("CREATE INDEX multipliers_user_id_idx ON multipliers(user_id);"
                 "CREATE INDEX multipliers_industry_id_idx ON multipliers(industry_id);",
                 multi=True))

cur.execute("CREATE TABLE IF NOT EXISTS industries("
            "industry_id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT, "
            "industry_name VARCHAR(100)"
            ")")
