import hashlib
from algosdk import account, mnemonic
from algosdk.future.transaction import AssetTransferTxn, PaymentTxn
from algosdk.v2client import algod

algod_address = "https://testnet-algorand.api.purestake.io/ps2"  # Put Algod Client address here
algod_token = "fi0QdbiBVl8hsVMCA2SUg6jnQdvAzxY48Zy2G6Yc"  # Put Algod Token here
headers = {
    "X-API-Key": algod_token,
}
algod_client = algod.AlgodClient(algod_token, algod_address, headers)

escrowAddr = "3JTSHP4IT2JAHDN3PXY64E2DU6GCVPTLPXHLOK5JDSFGKH3WIV2GCFU6QY"
escrowPhrase = "leopard gain lunch soccer slush supply engage gather pill page fence update scissors later brave image depart media indicate senior ready stand again absent worry"
escrowKey = mnemonic.to_private_key(escrowPhrase)
choice_id = 21364625

fundAddr = "WHNTB5KQTGKBQSZAJ5VX745SGYJTCKSQ2PX7KA3MVCXV7FNAEGLIGOKOZE"
fundPhrase = "foam fault power empty bulb usage round guard evoke city wish screen logic express assume extra copper kind prize table math wheat bargain absorb like"
fundKey = mnemonic.to_private_key(fundPhrase)
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


def sendInitialAlgorand(senderAddress, senderPhrase, recipientAddress,) -> None:
    """Send algorand to candidate address."""

    AMOUNT = 100500
    params = algod_client.suggested_params()
    transaction = PaymentTxn(
        senderAddress,
        params,
        recipientAddress,
        AMOUNT,
        note="Initial Funding for Candidate Creation",
    )
    transaction = transaction.sign(mnemonic.to_private_key(senderPhrase))

    algod_client.send_transaction(transaction)
    return True
  
def choiceCoinOptIn(address, privateKey, choice_id=choice_id) -> None:
    sendInitialAlgorand(
                fundAddr, fundPhrase, address
    )
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

def createNewAccount(fund=False) -> None:
    privateKey, address = account.generate_account()
    passphrase = mnemonic.from_private_key(privateKey)
    if fund: sendInitialAlgorand(fundAddr, fundPhrase, address)
    choiceCoinOptIn(address, privateKey)
    return address, passphrase, privateKey

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

# def returnChoice(candidate_address, candidate_mnemonic, amount=1):
#     params = algod_client.suggested_params()
#     transaction = AssetTransferTxn(
#         candidate_address,
#         params,
#         escrow_address,
#         amount,
#         "Returning choice coins (via the choice coin)"
#     )
#     signature = transaction.sign(mnemonic.to_private_key(candidate_mnemonic))
#     algod_client.send_transaction(signature)



def choiceVote(sender, key, receiver,amount,comment):
    params = algod_client.suggested_params() # Sets suggested parameters
    transaction = AssetTransferTxn(
        sender, 
        params, 
        receiver, 
        amount, 
        choice_id, 
        note=comment
    )
    signature = transaction.sign(key)
    algod_client.send_transaction(signature)
    final = transaction.get_txid()
    return True, final

def voteProject(candidate_address):
    TX_ID = choiceVote(escrow_address, escrow_key, candidate_address, 1, "Tabulated using Choice Coin") 
    message = "Vote counted. \n You can validate that your vote was counted correctly at https://testnet.algoexplorer.io/tx/" + TX_ID[1] + "."    
    return message