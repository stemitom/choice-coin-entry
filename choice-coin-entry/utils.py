import hashlib
from algosdk import account, mnemonic
from algosdk.future.transaction import AssetTransferTxn, PaymentTxn
from algosdk.v2client import algod
from vote import algod_client, choice_id

algod_address = "https://testnet-algorand.api.purestake.io/ps2"  # Put Algod Client address here
algod_token = "fi0QdbiBVl8hsVMCA2SUg6jnQdvAzxY48Zy2G6Yc"  # Put Algod Token here
headers = {
    "X-API-Key": algod_token,
}
algod_client = algod.AlgodClient(algod_token, algod_address, headers)

escrow_address = "3JTSHP4IT2JAHDN3PXY64E2DU6GCVPTLPXHLOK5JDSFGKH3WIV2GCFU6QY"
escrow_mnemonic = "leopard gain lunch soccer slush supply engage gather pill page fence update scissors later brave image depart media indicate senior ready stand again absent worry"
escrow_key = mnemonic.to_private_key(escrow_mnemonic)
choice_id = 21364625

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

def generate_algorand_keypair():
    private_key, address = account.generate_account()
    phrase = mnemonic.from_private_key(private_key)
    return address, phrase, private_key

def wait_for_transaction_confirmation(transaction_id: str):
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


def send_initial_algorand(escrow_address: str, escrow_private_key: str, recipient_address: str,) -> None:
    """Send algorand to candidate address."""

    AMOUNT = 210000
    suggested_params = algod_client.suggested_params()
    unsigned_transaction = PaymentTxn(
        escrow_address,
        suggested_params,
        recipient_address,
        AMOUNT,
        note="Initial Funding for Candidate Creation",
    )
    signed_transaction = unsigned_transaction.sign(escrow_private_key)

    try:
        transaction_id = algod_client.send_transaction(signed_transaction)
        wait_for_transaction_confirmation(transaction_id)
    except Exception as err:
        print(err)
        return True
    return False

def choiceCoinOptIn(address, private_key):
    """Opt into Choice Coin."""
    is_failed = send_initial_algorand(
                escrow_address, escrow_key, address
    )
    suggested_params = algod_client.suggested_params()
    transaction = AssetTransferTxn(address, suggested_params, address, 0, choice_id)
    signature = transaction.sign(private_key)
    try:
        transaction_id = algod_client.send_transaction(signature)
    except Exception as e:
        print(e)
    wait_for_transaction_confirmation(transaction_id)

def sendChoice(candidate_address, amount=1) -> None:
    params = algod_client.suggested_params()
    transaction = AssetTransferTxn(
        escrow_address,
        params,
        candidate_address,
        amount,
        "Send choice coins for votes (via the choice coin)"
    )
    signature = transaction.sign(escrow_key)
    algod_client.send_transaction(signature)

def returnChoice(candidate_address, candidate_mnemonic, amount=1):
    params = algod_client.suggested_params()
    transaction = AssetTransferTxn(
        candidate_address,
        params,
        escrow_address,
        amount,
        "Returning choice coins (via the choice coin)"
    )
    signature = transaction.sign(mnemonic.to_private_key(candidate_mnemonic))
    algod_client.send_transaction(signature)
