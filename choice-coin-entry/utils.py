from algosdk.v2client import algod
from vote import algod_client, choice_id

def contain_choice_coin(address):
    account = algod_client.account_info(address)
    contains_choice = False
    for asset in account["assets"]:
        if asset["asset-id"] == choice_id:
            contains_choice = True
            break
    return contains_choice

def get_wallet_balance(address: str) -> int:
    account = algod_client.account_info(address)
    return account["amount"]

