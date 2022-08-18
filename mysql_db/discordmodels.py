import mysql.connector
from mysql.connector.cursor_cext import CMySQLCursor  # Just for type hinting
from os import getenv
from dotenv import load_dotenv
from decimal import Decimal
from typing import Union


class User:

    def __init__(self, cur: CMySQLCursor, discord_id: int, guild_id: int):
        self.cur = cur
        cur.execute("SELECT * FROM users WHERE discord_id = %s AND guild_id = %s LIMIT 1",
                    (discord_id, guild_id))
        self.user_id, self.discord_id, self.guild_id, self.buying_power, self.paycheck_redeemed, \
            self.creating_power, self.job_title, self.company_name = cur.fetchone()

    @classmethod
    def create_user(cls, cur: CMySQLCursor, discord_id: int, guild_id: int, pet_name: str) -> "User":
        cur.execute("INSERT INTO users(discord_id, guild_id, buying_power, creating_power) "
                    "VALUES(%s, %s, %s, %s)", (discord_id, guild_id, Decimal("1000.00"), 1))
        cur.execute("INSERT INTO pets VALUES("
                    "(SELECT user_id FROM users WHERE discord_id = %s AND guild_id = %s LIMIT 1),"
                    "%s, %s, DEFAULT, DEFAULT)", (discord_id, guild_id, guild_id, pet_name))
        return cls(cur, discord_id, guild_id)


def get_user(cursor: CMySQLCursor, discord_id: int, guild_id: int) -> Union[None, User]:
    """
    Returns User() object if user is found, else returns None
    :param cursor: MySQL Cursor Object
    :param discord_id: Integer that represents discord user id
    :param guild_id:  Integer that represents guild id
    :return: Returns User object if user exists, else returns None
    """
    cursor.execute("SELECT COUNT(*) FROM users WHERE  discord_id = %s AND guild_id = %s LIMIT 1",
                   (discord_id, guild_id))
    number_of_users = cursor.fetchone()[0]
    if number_of_users == 1:
        return User(cursor, discord_id, guild_id)
    elif number_of_users == 0:
        return None
    else:
        # TODO: Add logging that there is more than one user detected
        return None


if __name__ == "__main__":
    load_dotenv()
    db = mysql.connector.connect(
        host=getenv("MYSQL_HOST"),
        port=getenv("MYSQL_PORT"),
        user=getenv("MYSQL_USER"),
        password=getenv("MYSQL_PASSWORD"),
        database="discord")

    cursor = db.cursor()
