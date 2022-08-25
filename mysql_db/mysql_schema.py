import mysql.connector
from mysql.connector.cursor_cext import CMySQLCursor  # Just for type hinting
from os import getenv
from dotenv import load_dotenv
import logging
from time import sleep

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler("homie.log")
formatting = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s")
stream_handler.setFormatter(formatting)
file_handler.setFormatter(formatting)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
if getenv("HOMIE_LOG") == "INFO":
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)

def create_schema(cur: CMySQLCursor):
    # TODO: Remove this section when finished testing table schema
    DEBUG = getenv("RESTART_HOMIE")
    if DEBUG == "1":
        # Using multi=True returns a generator of cursor objects, this will cause a command out of sync error
        # unless the generator is cleared before the next execute
        logger.warning("Attempting to drop all tables")
        sleep(5)
        list(cur.execute("DROP TABLE IF EXISTS portfolio;"
                         "DROP TABLE IF EXISTS nfts;"
                         "DROP TABLE IF EXISTS pets;"
                         "DROP TABLE IF EXISTS multipliers;"
                         "DROP TABLE IF EXISTS industries;"
                         "DROP TABLE IF EXISTS users;",
                         multi=True))
        logger.warning("All tables where dropped")

    logger.info("Attempting to create users table")
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

    logger.info("Attempting to create NFTs table")
    cur.execute("CREATE TABLE IF NOT EXISTS nfts("
                "nft_id INTEGER UNSIGNED PRIMARY KEY AUTO_INCREMENT, "
                "nft_name VARCHAR(32) NOT NULL,"
                "based_on BIGINT UNSIGNED NOT NULL, "
                "current_owner INTEGER UNSIGNED NOT NULL, "
                "guild_id BIGINT UNSIGNED NOT NULL, "
                "symbol VARCHAR(10) NOT NULL, "
                "image_url VARCHAR(150) NOT NULL, "
                "last_checked DATE NOT NULL DEFAULT (CURRENT_DATE), "
                "current_value DECIMAL(20, 2) NOT NULL,"
                "percent_change DECIMAL(20, 2) DEFAULT 0.0,"
                "FOREIGN KEY(current_owner) REFERENCES users(user_id)"
                ")")

    logger.info("Attempting to create pets table")
    cur.execute("CREATE TABLE IF NOT EXISTS pets("
                "owner_id INTEGER UNSIGNED NOT NULL,"
                "guild_id BIGINT UNSIGNED NOT NULL, "
                "pet_name VARCHAR(32) NOT NULL,"
                "current_owner BIGINT UNSIGNED NOT NULL DEFAULT 920026662974930954,"
                "purchase_price DECIMAL(20, 2) NOT NULL DEFAULT 100000,"
                "FOREIGN KEY (owner_id) REFERENCES users(user_id)"
                ")")

    logger.info("Attempting to create portfolio table")
    cur.execute("CREATE TABLE IF NOT EXISTS portfolio("
                "owner_id INTEGER UNSIGNED NOT NULL, "
                "nft_id INTEGER UNSIGNED NOT NULL, "
                "amount_owned BIGINT UNSIGNED NOT NULL,"
                "FOREIGN KEY (owner_id) REFERENCES users(user_id),"
                "FOREIGN KEY (nft_id) REFERENCES nfts(nft_id)"
                ")")

    logger.info("Attempting to create multipliers table")
    cur.execute("CREATE TABLE IF NOT EXISTS multipliers("
                "owner_id INTEGER UNSIGNED NOT NULL, "
                "stat_multiplier DECIMAL(20, 2) NOT NULL, "
                "amount INTEGER NOT NULL DEFAULT 0, "
                "degree_type VARCHAR(32) NOT NULL, "
                "industry_index INTEGER UNSIGNED NOT NULL,"
                "FOREIGN KEY (owner_id) REFERENCES users(user_id)"
                ")")

    logger.info("Checking if indexes exists")
    cur.execute("SELECT COUNT(*) FROM information_schema.statistics WHERE "
                "table_schema = DATABASE() AND index_name = \"users_discord_id_idx\"")
    if cur.fetchone()[0] == 0:
        # Using multi=True returns a generator of cursor objects, this will cause a command out of sync error
        # unless the generator is cleared before the next execute
        list(cur.execute("CREATE INDEX users_discord_id_idx ON users(discord_id);"
                         "CREATE INDEX users_guild_id_idx ON users(guild_id);",
                         multi=True))
        list(cur.execute("CREATE INDEX nfts_based_on_idx ON nfts(based_on);"
                         "CREATE INDEX nfts_guild_id_idx ON nfts(guild_id);",
                         multi=True))
        logger.info("Indexes where created")

    cur.close()


if __name__ == "__main__":
    load_dotenv()
    db = mysql.connector.connect(
        host=getenv("MYSQL_HOST"),
        port=getenv("MYSQL_PORT"),
        user=getenv("MYSQL_USER"),
        password=getenv("MYSQL_PASSWORD"),
        database="discord")

    cursor = db.cursor()
    create_schema(cursor)
