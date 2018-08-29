from boa.interop.Neo.Storage import *
from boa.interop.Neo.Runtime import CheckWitness, Notify
from boa.interop.Neo.Blockchain import GetHeight
from nxa.token import *
from boa.interop.Neo.Action import RegisterAction


MONTH_KEY = "month"

first_year_key = "1year"

second_year_key = "2year"

deposit_key = "deposit_height"

OnTransfer = RegisterAction('transfer', 'addr_from', 'addr_to', 'amount')
OnApprove = RegisterAction('approve', 'addr_from', 'addr_to', 'amount')

def handle_team_operations(ctx, operation, args):
    if operation == 'team_transfer_from':
        if len(args) == 4:
            return team_transfer_from(ctx, args[0], args[1], args[2],args[3])

    elif operation == 'team_approve':
        if len(args) == 3:
            return team_approve(ctx, args[0], args[1], args[2])

    elif operation == 'team_allowance':
        if len(args) == 3:
            return team_allowance(ctx, args[0], args[1], args[2])

    elif operation == 'team_reserve':
        return team_reserve(ctx)

    if operation == 'company_transfer_from':
        if len(args) == 2:
            return company_transfer_from(ctx, args[0], args[1])

    elif operation == 'company_approve':
        if len(args) == 2:
            return company_approve(ctx, args[0], args[1])

    elif operation == 'company_allowance':
        if len(args) == 2:
            return company_allowance(ctx, args[0], args[1])

    elif operation == 'company_reserve':
        return company_reserve(ctx)

    return 'unknown operation'


def team_transfer_from(ctx, t_from, t_to, amount, month):
    if amount <= 0:
        return False

    first_part = concat(t_from, t_to)
    available_key = concat(first_part, month)
    if len(available_key) <= 40:
        return False

    available_to_to_addr = Get(ctx, available_key)

    if available_to_to_addr < amount:
        print("Insufficient funds approved")
        return False


    from_balance = Get(ctx, t_from)

    deposit_address_key = concat(available_key, deposit_key)

    deposit_height = Get(ctx, deposit_address_key)

    current_height = GetHeight()

    if((current_height - deposit_height) < YEAR):
        print("At least 1 year must pass to withdraw funds")
        return False

    first_year_address_key = concat(available_key, first_year_key)

    first_year_transfer = Get(ctx, first_year_address_key)
    available_amount = Get(ctx, available_key)

    if not first_year_transfer:
        first_year_amount = (15 * available_amount) / 100
        Put(ctx, first_year_address_key, True)
        return perform_transfer(ctx, t_to, t_from, from_balance, available_to_to_addr, available_key, first_year_amount)


    if((current_height - deposit_height) < 2*YEAR):
        print("At least 2 years must pass to withdraw funds")
        return False


    second_year_address_key = concat(available_key, second_year_key)
    second_year_transfer = Get(ctx, second_year_address_key)

    if not second_year_transfer:
        second_year_amount = (30 * available_amount )/ 100
        Put(ctx, second_year_address_key, True)

        return perform_transfer(ctx, t_to, t_from, from_balance, available_to_to_addr, available_key, second_year_amount)


    if((current_height - deposit_height) < 3 *YEAR):
        print("At least 3 year must pass to withdraw the whole funds")
        return False

    return perform_transfer(ctx, t_to, t_from, from_balance, available_to_to_addr, available_key, amount)

def team_approve(ctx, t_owner, t_spender, amount):

    if len(t_spender) != 20:
        return False

    if not CheckWitness(t_owner):
        return False

    if amount < 0:
        return False

    height = GetHeight()
    employee_month = concat(t_spender,NEXT_MONTH_SALARY)
    month = Get(ctx,employee_month)
    if month == b'':
        month = 1
    else:
        month = month + 1

    if Get(ctx, t_owner) >= amount:

        firstPart = concat(t_owner, t_spender)
        approval_key = concat(firstPart, month)
        first_year_address_key = concat(approval_key, "1year")
        second_year_address_key = concat(approval_key, "2year")
        deposit_address_key = concat(approval_key, "deposit_height")
        team_amount = Get(ctx, TEAM_RESERVE_KEY)

        if amount == 0:
            Delete(ctx, approval_key)
        elif (team_amount < amount):
            print("Not enough funds remain from team reserve")
            return False
        else:
            Put(ctx, approval_key, amount)
            Put(ctx, first_year_address_key, False)
            Put(ctx, second_year_address_key, False)
            Put(ctx, deposit_address_key, height)
            Put(ctx, employee_month, month)
            Put(ctx, TEAM_RESERVE_KEY, team_amount - amount)
        OnApprove(t_owner, t_spender, amount)

        return True

    return False


def team_allowance(ctx, t_owner, t_spender,month):
    first_part = concat(t_owner, t_spender)
    approval_key = concat(first_part, month)
    return Get(ctx, approval_key)


def perform_transfer(ctx, t_to, t_from, from_balance, available_to_to_addr, available_key, amount):
    if from_balance < amount:
        print("Insufficient tokens in from balance")
        return False

    to_balance = Get(ctx, t_to)

    new_from_balance = from_balance - amount

    new_to_balance = to_balance + amount

    Put(ctx, t_to, new_to_balance)
    Put(ctx, t_from, new_from_balance)

    new_allowance = available_to_to_addr - amount

    if new_allowance == 0:
        print("removing all balance")
        Delete(ctx, available_key)
    else:
        print("updating allowance to new allowance")
        Put(ctx, available_key, new_allowance)

    OnTransfer(t_from, t_to, amount)

    return True

def team_reserve(ctx):
    return Get(ctx, TEAM_RESERVE_KEY)

#####

def company_transfer_from(ctx, t_from, t_to):

    if not CheckWitness(TOKEN_OWNER):
        return False

    available_fist_part = concat(t_from, t_to)
    available_key = concat(available_fist_part, MONTH_KEY)

    if len(available_key) < 40:
        return False

    available_to_to_addr = Get(ctx, available_key)

    if available_to_to_addr < MONTHLY_ALLOWANCE:
        print("Insufficient funds approved")
        return False

    deposit_address_key = concat(available_key, deposit_key)
    height = Get(ctx,deposit_address_key)
    current_height =GetHeight()

    if (current_height - height < MONTH):
        print("A month must pass to send the funds")
        return False

    from_balance = Get(ctx, t_from)

    if from_balance < MONTHLY_ALLOWANCE:
        print("Insufficient tokens in from balance")
        return False

    company_reserve = Get(ctx, COMPANY_RESERVE_KEY)

    if company_reserve < MONTHLY_ALLOWANCE:
        print("Insufficient tokens in from balance")
        return False

    to_balance = Get(ctx, t_to)
    new_from_balance = from_balance - MONTHLY_ALLOWANCE
    new_to_balance = to_balance + MONTHLY_ALLOWANCE
    new_company_reserve = company_reserve - MONTHLY_ALLOWANCE

    Put(ctx, t_to, new_to_balance)
    Put(ctx, t_from, new_from_balance)
    Put(ctx, COMPANY_RESERVE_KEY, new_company_reserve)
    Put(ctx, deposit_address_key, current_height)


    print("transfer complete")
    OnTransfer(t_from, t_to, MONTHLY_ALLOWANCE)

    return True


def company_approve(ctx, t_owner, t_spender):

    if not CheckWitness(TOKEN_OWNER):
        print("Must be token owner to approve funds")
        return False

    if len(t_spender) != 20:
        return False

    if not CheckWitness(t_owner):
        return False

    company_reserv_amount = Get(ctx, COMPANY_RESERVE_KEY)

    if company_reserv_amount <= 0:
        return False

    if Get(ctx, t_owner) >= amount:
        approval_first_part = concat(t_owner, t_spender)
        approval_key = concat(approval_first_part, MONTH_KEY)
        height = GetHeight()
        deposit_address_key = concat(approval_key, deposit_key)
        Put(ctx, deposit_address_key, height)
        Put(ctx, approval_key, MONTHLY_ALLOWANCE)
        OnApprove(t_owner, t_spender, MONTHLY_ALLOWANCE)

        return True

    return False


def company_allowance(ctx, t_owner, t_spender):
    approval_first_part = concat(t_owner, t_spender)
    approval_key = concat(approval_first_part, MONTH_KEY)

    return Get(ctx, approval_key)

def company_reserve(ctx):
    return Get(ctx, COMPANY_RESERVE_KEY)
