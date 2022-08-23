from mysql.connector.cursor_cext import CMySQLCursor  # Just for type hinting
from decimal import Decimal
from typing import Union
from datetime import date


class User:

    def __init__(self, cur: CMySQLCursor, discord_id: int, guild_id: int):
        self.cur = cur
        cur.execute("SELECT * FROM users WHERE discord_id = %s AND guild_id = %s LIMIT 1",
                    (discord_id, guild_id))

        self.user_id, self.discord_id, self.guild_id, _, self.paycheck_redeemed, \
            self.creating_power, self.job_title, self.company_name = cur.fetchone()

        cur.execute("SELECT current_owner, pet_name FROM pets WHERE owner_id = %s", (self.user_id,))
        self.pet_owner, self.pet_name = cur.fetchone()
        self.pet_status = "Safe for now" if self.pet_owner == self.discord_id else "Kidnapped"

    def new_job(self, job_title: str, company_name: str):
        if self.job_title is None:  # If first job, make sure they can get paycheck today
            self.cur.execute("UPDATE users SET paycheck_redeemed = '2018-12-31' WHERE user_id = %s", (self.user_id,))
        self.cur.execute("UPDATE users SET job_title = %s, company_name = %s WHERE user_id = %s",
                         (job_title, company_name, self.user_id))
        self.job_title = job_title
        self.company_name = company_name

    def get_multipliers(self) -> Decimal:
        self.cur.execute("SELECT IFNULL(SUM(stat_multiplier), 0) FROM multipliers WHERE owner_id = %s", (self.user_id,))
        return self.cur.fetchone()[0]

    def get_paycheck(self):
        if self.paycheck_redeemed == date.today():
            return None  # TODO: Log that some how command bypassed initial check
        paycheck_amount = Decimal("100") * (Decimal("1") + self.get_multipliers())
        self.cur.execute("UPDATE users SET buying_power = buying_power + %s WHERE user_id = %s", (paycheck_amount,
                                                                                                  self.user_id))
        self.cur.execute("UPDATE users SET paycheck_redeemed = %s WHERE user_id = %s", (date.today(), self.user_id))
        return paycheck_amount

    @property
    def buying_power(self):
        self.cur.execute("SELECT buying_power FROM users WHERE user_id = %s", (self.user_id,))
        return self.cur.fetchone()[0]

    @classmethod
    def create_user(cls, cur: CMySQLCursor, discord_id: int, guild_id: int, pet_name: str) -> "User":
        cur.execute("INSERT INTO users(discord_id, guild_id, buying_power, creating_power) "
                    "VALUES(%s, %s, %s, %s)", (discord_id, guild_id, Decimal("1000.00"), 1))
        cur.execute("INSERT INTO pets VALUES("
                    "(SELECT user_id FROM users WHERE discord_id = %s AND guild_id = %s LIMIT 1),"
                    "%s, %s, DEFAULT, DEFAULT)", (discord_id, guild_id, guild_id, pet_name))
        return cls(cur, discord_id, guild_id)

    def nft_exists(self, based_on_id):
        self.cur.execute("SELECT COUNT(*) FROM nfts WHERE based_on = %s AND guild_id = %s",
                         (based_on_id, self.guild_id))
        return self.cur.fetchone()[0]

    def create_nft(self, nft_name, based_on, symbol, url, value):
        self.cur.execute("INSERT INTO nfts(nft_name, based_on, current_owner, guild_id, symbol,"
                         "image_url, last_checked, current_value) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                         (nft_name, based_on, self.user_id, self.guild_id, symbol.upper(), url, date.today(), value))
        self.cur.execute("UPDATE users SET creating_power = creating_power - 1 WHERE user_id = %s", (self.user_id,))

    def add_modifier(self, final_multiplier, amount, degree_type, industry_index):
        self.cur.execute("INSERT INTO multipliers(owner_id, stat_multiplier, amount, degree_type, industry_index) "
                         "VALUES(%s, %s, %s, %s, %s)",
                         (self.user_id, final_multiplier, amount, degree_type, industry_index))

    def charge_user(self, amount):
        self.cur.execute("UPDATE users SET buying_power = buying_power - %s WHERE user_id = %s", (amount, self.user_id))


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
