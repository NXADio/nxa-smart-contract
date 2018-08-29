
from nxa.crowdsale import *
from nxa.nep5 import *
from nxa.team import *
from boa.interop.Neo.Runtime import GetTrigger, CheckWitness
from boa.interop.Neo.TriggerType import Application, Verification
from boa.interop.Neo.Storage import *

ctx = GetContext()
NEP5_METHODS = ['name', 'symbol', 'decimals', 'totalSupply', 'balanceOf', 'transfer', 'transferFrom', 'approve', 'allowance']
TEAM_METHODS = ['team_transfer_from', 'team_approve', 'team_allowance','team_reserve','company_transfer_from','company_approve','company_allowance','company_reserve']

def Main(operation, args):
    """

    :param operation: str The name of the operation to perform
    :param args: list A list of arguments along with the operation
    :return:
        bytearray: The result of the operation
    """
    trigger = GetTrigger()

    if trigger == Verification():

        is_owner = CheckWitness(TOKEN_OWNER)

        if is_owner:
            return True

        attachments = get_asset_attachments()
        return can_exchange(ctx, attachments, True)

    elif trigger == Application():

        for op in NEP5_METHODS:
            if operation == op:
                return handle_nep51(ctx, operation, args)

        for op in TEAM_METHODS:
            if operation == op:
                return handle_team_operations(ctx, operation, args)

        if operation == 'deploy':
            return deploy()

        elif operation == 'circulation':
            return get_circulation(ctx)

        # the following are handled by crowdsale
        elif operation == 'mintTokens':
            return perform_exchange(ctx, args)

        elif operation == 'crowdsale_register':
            return kyc_register(ctx, args)

        elif operation == 'crowdsale_status':
            return kyc_status(ctx, args)

        elif operation == 'crowdsale_available':
            return crowdsale_available_amount(ctx)

        return 'unknown operation'


def deploy():
    """

    :param token: Token The token to deploy
    :return:
        bool: Whether the operation was successful
    """
    if not CheckWitness(TOKEN_OWNER):
        print("Must be owner to deploy")
        return False

    if not Get(ctx, 'initialized'):
        # do deploy logic
        Put(ctx, 'initialized', 1)
        Put(ctx, TOKEN_OWNER, TOKEN_INITIAL_AMOUNT)
        Put(ctx, TEAM_RESERVE_KEY, TEAM_RESERVE_INITIAL_AMOUNT)
        Put(ctx, COMPANY_RESERVE_KEY, COMPANY_RESERVE_INITIAL_AMOUNT)
        return add_to_circulation(ctx, TOKEN_INITIAL_AMOUNT)

    return False