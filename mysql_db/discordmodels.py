from mysql.connector.cursor_cext import CMySQLCursor  # Just for type hinting
from decimal import Decimal
from typing import Union
from datetime import date
import finnhub


class Nft:

    def __init__(self, cur: CMySQLCursor, nft_id):
        self.cur = cur
        self.id = nft_id
        self.cur.execute("SELECT * FROM nfts WHERE nft_id = %s", (self.id,))
        _, self.name, self.based_on, self.current_owner, self.guild_id, self.symbol, self.image, self.last_checked, \
            self.current_value, self.percent_change = self.cur.fetchone()


class User:

    def __init__(self, cur: CMySQLCursor, discord_id: int, guild_id: int, finn: finnhub.Client, change_mul):
        self.change_mul = Decimal(change_mul)
        self.finn = finn
        self.cur = cur
        cur.execute("SELECT * FROM users WHERE discord_id = %s AND guild_id = %s LIMIT 1",
                    (discord_id, guild_id))

        self.user_id, self.discord_id, self.guild_id, _, self.paycheck_redeemed, \
            self.creating_power, self.job_title, self.company_name = cur.fetchone()

        cur.execute("SELECT current_owner, pet_name, purchase_price FROM pets WHERE owner_id = %s", (self.user_id,))
        self.pet_owner, self.pet_name, self.pet_price = cur.fetchone()
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
    def create_user(cls, cur: CMySQLCursor, discord_id: int, guild_id: int, pet_name: str, finn: finnhub.Client,
                    mult: str) -> "User":
        cur.execute("INSERT INTO users(discord_id, guild_id, buying_power, creating_power) "
                    "VALUES(%s, %s, %s, %s)", (discord_id, guild_id, Decimal("1000.00"), 1))
        cur.execute("INSERT INTO pets VALUES("
                    "(SELECT user_id FROM users WHERE discord_id = %s AND guild_id = %s LIMIT 1),"
                    "%s, %s, DEFAULT, DEFAULT)", (discord_id, guild_id, guild_id, pet_name))
        return cls(cur, discord_id, guild_id, finn, mult)

    def nft_exists(self, based_on_id):
        self.cur.execute("SELECT COUNT(*) FROM nfts WHERE based_on = %s AND guild_id = %s",
                         (based_on_id, self.guild_id))
        return self.cur.fetchone()[0]


    def symbol_exists(self, symbol):
        self.cur.execute("SELECT COUNT(*) FROM nfts WHERE symbol = %s AND guild_id = %s",
                         (symbol, self.guild_id))
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

    def get_nft_id(self, based_on_id):
        self.cur.execute("SELECT nft_id FROM nfts WHERE based_on = %s AND guild_id = %s",
                         (based_on_id, self.guild_id))
        return self.cur.fetchone()[0]

    # TODO: If I sell all NFTs I have to delete row
    def nft_owned_amount(self, nft_id):
        self.cur.execute("SELECT IFNULL((SELECT amount_owned FROM portfolio WHERE nft_id = %s AND owner_id = %s), 0)",
                         (nft_id, self.user_id))
        return self.cur.fetchone()[0]

    def get_nft_cost(self, nft_id):
        self.cur.execute("SELECT last_checked, current_value, symbol FROM nfts WHERE nft_id = %s", (nft_id,))
        last_checked, current_value, symbol = self.cur.fetchone()
        today = date.today()
        if last_checked == today:
            return current_value
        else:
            change = self.finn.quote(symbol)["dp"]
            percent_change = (self.change_mul * (Decimal(round(change, 2))/100))
            if percent_change < Decimal("-0.95"):
                percent_change = Decimal("-0.95")
            current_value = current_value * (1 + percent_change)
            self.cur.execute("UPDATE nfts SET "
                             "current_value = %s, percent_change = %s, last_checked = %s WHERE nft_id = %s",
                             (current_value, percent_change, today, nft_id))
            return current_value

    def purchase_nft(self, nft_id, amount):
        if self.nft_owned_amount(nft_id) == 0:
            self.cur.execute("INSERT INTO portfolio VALUES(%s, %s, %s)", (self.user_id, nft_id, amount))
        else:
            self.cur.execute("UPDATE portfolio SET amount_owned = amount_owned + %s WHERE owner_id = %s AND nft_id = %s",
                             (amount, self.user_id, nft_id))

    def sell_nft(self, nft_id, amount_sold, amount_owned):
        if amount_sold == amount_owned:
            self.cur.execute("DELETE FROM portfolio WHERE owner_id = %s AND nft_id = %s", (self.user_id, nft_id))
        else:
            self.cur.execute("UPDATE portfolio SET amount_owned = amount_owned - %s WHERE owner_id = %s AND nft_id = %s",
                             (amount_sold, self.user_id, nft_id))

    def pet_stolen(self, new_owner_disc_id):
        self.cur.execute("UPDATE pets SET current_owner = %s, purchase_price = 200000 WHERE owner_id = %s",
                         (new_owner_disc_id, self.user_id))

    def get_top_stocks(self):
        self.cur.execute("SELECT COUNT(*) FROM portfolio WHERE owner_id = %s", (self.user_id,))
        if self.cur.fetchone()[0] == 0:
            return []
        self.cur.execute("SELECT symbol, amount_owned, current_value, based_on, nft_name FROM portfolio "
                         "JOIN nfts ON portfolio.nft_id = nfts.nft_id WHERE portfolio.owner_id = %s "
                         "ORDER BY (amount_owned * current_value) LIMIT 5", (self.user_id,))
        return self.cur.fetchall()

    def get_portfolio_value(self):
        total = Decimal("0")
        self.cur.execute("SELECT nft_id, amount_owned FROM portfolio WHERE owner_id = %s", (self.user_id,))
        for row in self.cur.fetchall():
            total += self.get_nft_cost(row[0]) * row[1]
        return total

    def change_nft_price(self, new_price, perc_change, nft_id):
        self.cur.execute("UPDATE nfts SET current_value = %s, percent_change = %s WHERE nft_id = %s",
                         (new_price, perc_change, nft_id))


def get_user(cursor: CMySQLCursor, discord_id: int, guild_id: int, finn: finnhub.Client, mult: str) -> Union[None, User]:
    """
    Returns User() object if user is found, else returns None
    :param cursor: MySQL Cursor Object
    :param discord_id: Integer that represents discord user id
    :param guild_id:  Integer that represents guild id
    :param finn: Finnhub Client
    :param mult: String representing volatility multiplier
    :return: Returns User object if user exists, else returns None
    """
    cursor.execute("SELECT COUNT(*) FROM users WHERE  discord_id = %s AND guild_id = %s LIMIT 1",
                   (discord_id, guild_id))
    number_of_users = cursor.fetchone()[0]
    if number_of_users == 1:
        return User(cursor, discord_id, guild_id, finn, mult)
    elif number_of_users == 0:
        return None
    else:
        # TODO: Add logging that there is more than one user detected
        return None
