import hashlib
from algosdk import account, mnemonic
from algosdk.future import transaction
from algosdk.future.transaction import AssetTransferTxn, PaymentTxn
from algosdk.v2client import algod
from decouple import config


algod_address = config('ALGOD_ADDRESS')
algod_token = config("ALGOD_TOKEN")
headers = {
    "X-API-Key": algod_token,
}
algod_client = algod.AlgodClient(algod_token, algod_address, headers)

escrowAddr = config('escrowAddr')
escrowPhrase = config('escrowPhrase')
escrowKey = mnemonic.to_private_key(escrowPhrase)
fundAddr = config('fundAddr')
fundPhrase = config('fundPhrase')
fundKey = mnemonic.to_private_key(fundPhrase)
choice_id = 21364625
# choice_id = 1726141

def hashing(item) -> str:
    hash_obj = hashlib.sha512(item.encode())
    return hash_obj.hexdigest()

def containChoiceCoin(address) -> bool:
    account = algod_client.account_info(address)
    contains_choice = False
    for asset in account["assets"]:
        if asset["asset-id"] == choice_id:
            contains_choice = True
            break
    return contains_choice

def getWalletBalance(address: str) -> int:
    account = algod_client.account_info(address)
    return account["amount"]

def waitForTransactionConfirmation(transaction_id: str):
    """Wait until the transaction is confirmed or rejected, or until timeout snumber of rounds have passed."""

    TIMEOUT = 4
    start_round = algod_client.status()["last-round"] + 1
    current_round = start_round

    while current_round < start_round + TIMEOUT:
        try:
            pending_txn = algod_client.pending_transaction_info(transaction_id)
        except Exception:
            return
        if pending_txn.get("confirmed-round", 0) > 0:
            return pending_txn
        elif pending_txn["pool-error"]:
            raise Exception("pool error: {}".format(pending_txn["pool-error"]))

        algod_client.status_after_block(current_round)
        current_round += 1
    raise Exception("pending tx not found in TIMEOUT rounds, TIMEOUT value = : {}".format(TIMEOUT))


    return True

def generate_algo_acc():
    key, addr = account.generate_account()
    phrase = mnemonic.from_private_key(key)
    return key, phrase, addr


def sendInitialAlgo(sender, key, recepient, amount):
    params = algod_client.suggested_params()
    transaction = PaymentTxn(
        sender,
        params,
        recepient,
        amount,
        note="Initial funding for candidate address"
    )
    transaction = transaction.sign(key)
    algod_client.send_transaction(transaction)
    return True

def choiceCoinOptIn(address, privateKey, choice_id=choice_id) -> None:
    params = algod_client.suggested_params()
    transaction = AssetTransferTxn(
        address,
        params,
        address,
        0,
        choice_id
    )
    signature = transaction.sign(privateKey)
    algod_client.send_transaction(signature)
    return True

def createAccount():
    key, phrase, addr = generate_algo_acc()
    try:
        sendInitialAlgo(fundAddr, fundKey, addr, 200000)
    except:
        raise Exception("Funding is not successful. Please try to confirm balance")
    try:
        choiceCoinOptIn(addr, key)
    except:
        raise Exception("Failed to opt in for choice asset. Please try again")
    return addr, phrase, key

# def sendChoice(candidate_address, amount=1) -> None:
#     params = algod_client.suggested_params()
#     transaction = AssetTransferTxn(
#         escrow_address,
#         params,
#         candidate_address,
#         amount,
#         "Send choice coins for votes (via the choice coin)"
#     )
#     signature = transaction.sign(escrow_key)
#     algod_client.send_transaction(signature)
#     return True


# def choiceVote(sender, key, receiver,amount,comment):
#     params = algod_client.suggested_params() # Sets suggested parameters
#     transaction = AssetTransferTxn(
#         sender, 
#         params, 
#         receiver, 
#         amount, 
#         choice_id, 
#         note=comment
#     )
#     signature = transaction.sign(key)
#     algod_client.send_transaction(signature)
#     final = transaction.get_txid()
#     return True, final

# def voteProject(candidate_address):
#     TX_ID = choiceVote(escrow_address, escrow_key, candidate_address, 1, "Tabulated using Choice Coin") 
#     message = "Vote counted. \n You can validate that your vote was counted correctly at https://testnet.algoexplorer.io/tx/" + TX_ID[1] + "."    
#     return message