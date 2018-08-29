from boa.interop.Neo.Runtime import CheckWitness, Notify
from boa.interop.Neo.Action import RegisterAction
from boa.interop.Neo.Storage import *
from boa.builtins import concat

from nxa.token import *


OnTransfer = RegisterAction('transfer', 'addr_from', 'addr_to', 'amount')
OnApprove = RegisterAction('approve', 'addr_from', 'addr_to', 'amount')

def handle_nep51(ctx, operation, args):

    if operation == 'name':
        return TOKEN_NAME

    elif operation == 'decimals':
        return TOKEN_DECIMALS

    elif operation == 'symbol':
        return TOKEN_SYMBOL

    elif operation == 'totalSupply':
        return Get(ctx, TOKEN_CIRC_KEY)

    elif operation == 'balanceOf':
        if len(args) == 1:
            return Get(ctx, args[0])

    elif operation == 'transfer':
        if len(args) == 3:
            return do_transfer(ctx, args[0], args[1], args[2])

    elif operation == 'transferFrom':
        if len(args) == 3:
            return do_transfer_from(ctx, args[0], args[1], args[2])

    elif operation == 'approve':
        if len(args) == 3:
            return do_approve(ctx, args[0], args[1], args[2])

    elif operation == 'allowance':
        if len(args) == 2:
            return do_allowance(ctx, args[0], args[1])

    return False


def do_transfer(ctx, t_from, t_to, amount):

    if amount <= 0:
        return False

    if len(t_to) != 20:
        return False

    if CheckWitness(t_from):

        if t_from == t_to:
            print("transfer to self!")
            return True

        from_val = Get(ctx, t_from)

        if CheckWitness(TOKEN_OWNER):
            team_reserve = Get(ctx,TEAM_RESERVE_KEY)
            company_reserve = Get(ctx, COMPANY_RESERVE_KEY)
            from_val = from_val - team_reserve
            from_val = from_val - company_reserve

            if from_val < amount:
                print("insufficient funds")
                return False

            difference = from_val - amount
            difference = difference + company_reserve
            difference = difference + team_reserve

            if difference == 0:
                Delete(ctx, t_from)
            else:
                Put(ctx, t_from, difference)
        else:
            if from_val < amount:
                print("insufficient funds")
                return False
            difference = from_val - amount
            if from_val == amount:
                Delete(ctx, t_from)
            else:
                Put(ctx, t_from, difference)

        to_value = Get(ctx, t_to)

        to_total = to_value + amount

        Put(ctx, t_to, to_total)

        OnTransfer(t_from, t_to, amount)

        return True
    else:
        print("from address is not the tx sender")

    return False


def do_transfer_from(ctx, t_from, t_to, amount):

    if amount <= 0:
        return False

    available_key = concat(t_from, t_to)

    if len(available_key) != 40:
        return False

    available_to_to_addr = Get(ctx, available_key)

    if available_to_to_addr < amount:
        print("Insufficient funds approved")
        return False

    from_balance = Get(ctx, t_from)
    new_from_balance = from_balance - amount

    #Token owner logic to not touch the team funding and the company reserve
    #When making transfers
    if CheckWitness(TOKEN_OWNER):
        team_reserve = Get(ctx,TEAM_RESERVE_KEY)
        company_reserve = Get(ctx, COMPANY_RESERVE_KEY)
        from_balance = from_balance - team_reserve
        from_balance = from_balance - company_reserve

    if from_balance < amount:
            print("Insufficient tokens in from balance")
            return False

    to_balance = Get(ctx, t_to)

    new_to_balance = to_balance + amount

    Put(ctx, t_to, new_to_balance)
    Put(ctx, t_from, new_from_balance)

    print("transfer complete")

    new_allowance = available_to_to_addr - amount

    if new_allowance == 0:
        print("removing all balance")
        Delete(ctx, available_key)
    else:
        print("updating allowance to new allowance")
        Put(ctx, available_key, new_allowance)

    OnTransfer(t_from, t_to, amount)

    return True


def do_approve(ctx, t_owner, t_spender, amount):

    if len(t_spender) != 20:
        return False

    if not CheckWitness(t_owner):
        return False

    if amount < 0:
        return False

    #Token owner logic to not touch the team funding and the company reserve
    #When making transfers
    from_balance = Get(ctx, t_owner)

    if CheckWitness(TOKEN_OWNER):
        team_reserve = Get(ctx,TEAM_RESERVE_KEY)
        company_reserve = Get(ctx, COMPANY_RESERVE_KEY)
        from_balance = from_balance - team_reserve
        from_balance = from_balance - company_reserve


    if from_balance>= amount:

        approval_key = concat(t_owner, t_spender)

        if amount == 0:
            Delete(ctx, approval_key)
        else:
            Put(ctx, approval_key, amount)

        OnApprove(t_owner, t_spender, amount)

        return True

    return False


def do_allowance(ctx, t_owner, t_spender):

    return Get(ctx, concat(t_owner, t_spender))
