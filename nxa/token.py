"""
Basic settings for an NEP5 Token and crowdsale
"""

from boa.interop.Neo.Storage import *

TOKEN_NAME = 'NXAD'

TOKEN_SYMBOL = 'NXA'

TOKEN_DECIMALS = 8

TOKEN_OWNER = b'\xa8\x15\x95\x90\xe2!\xf0#td\xb8\xf5N\x1c\\m\xacNe('

TOKEN_CIRC_KEY = b'in_circulation'

TOKEN_TOTAL_SUPPLY = 2600000000 * 100000000  # 2600m total supply * 10^8 ( decimals)

TOKEN_INITIAL_AMOUNT = 1040000000 * 100000000  # 1560m to owners * 10^8

MAX_EXCHANGE_LIMITED_ROUND = 1560000000 * 100000000

BLOCK_SALE_START = 1809861

LIMITED_ROUND_END = 1809861 + 388800

KYC_KEY = b'kyc_ok'

LIMITED_ROUND_KEY = b'r1'

YEAR = 1576800

MONTH = 129600

NEXT_MONTH_SALARY = "NEXT_MONTH_SALARY"

TEAM_RESERVE_KEY = "TEAM_RESERVE"

TEAM_RESERVE_INITIAL_AMOUNT = 286000000 * 100000000

COMPANY_RESERVE_KEY = "COMPANY_RESERVE"

COMPANY_RESERVE_INITIAL_AMOUNT = 364000000 * 100000000

MONTHLY_ALLOWANCE = 10111110 * 100000000 + 11111111


def crowdsale_available_amount(ctx):
    """

    :return: int The amount of tokens left for sale in the crowdsale
    """

    in_circ = Get(ctx, TOKEN_CIRC_KEY)

    available = TOKEN_TOTAL_SUPPLY - in_circ

    return available


def add_to_circulation(ctx, amount):
    """
    Adds an amount of token to circlulation

    :param amount: int the amount to add to circulation
    """
    current_supply = Get(ctx, TOKEN_CIRC_KEY)

    current_supply += amount
    Put(ctx, TOKEN_CIRC_KEY, current_supply)
    return True


def get_circulation(ctx):
    """
    Get the total amount of tokens in circulation

    :return:
        int: Total amount in circulation
    """
    return Get(ctx, TOKEN_CIRC_KEY)
