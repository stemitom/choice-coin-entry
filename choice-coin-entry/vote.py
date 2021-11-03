from algosdk import account, encoding, mnemonic, transaction
from algosdk.future.transaction import AssetTransferTxn
from algosdk.v2client import algod
from matplotlib import pyplot as plt
import matplotlib
import hashlib
import secrets
import random

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

decision_one = ""
decision_two = ""
corporate_decision_one = ""
corporate_decision_two = ""

def count(address, error="The asset is not in the account information"):
    """
    This function gets the amount of choice coin that is in an account
    """
    message, error = "", ""
    accountInfo = algod_client.account_info(address)
    assets = accountInfo.get("assets")
    for asset in assets:
        if asset["asset-id"] == choice_id:
            amount = asset.get("amount")
            message = amount
            return amount
    return error


def hashing(item):
    """
    This is a string hashing procedure using the SHA-512 cryptography algorithm
    """
    hash_obj = hashlib.sha512(item.encode())
    return hash_obj.hexdigest()

def choiceVote(sender, key, reciever, amount, comment):
    """
    This is the heart of the voting mechanism and it sends the choice coin from a sender to a reciever
    """
    params = algod_client.suggested_params()
    transaction = AssetTransferTxn(sender, params, reciever, amount, choice_id, note=comment)
    signature = transaction.sign(key)
    algod_client.send_transaction(signature)
    final = transaction.get_txid()
    return True, final

def electionVoting(candidate):
    transaction_id = choiceVote(
        candidate.election.escrow_address,
        candidate.election.escrow_key,
        candidate.address,
        100,
        "Basic Voting Procedure using Choice Coin"
    )
    return f"Usual Ballot tabulated. You can validate that your vote was counted correctly at https://testnet.algoexplorer.io/tx/{transaction_id[1]}/"

def corporateVoting(candidate, stake):
    transaction_id = choiceVote(
        candidate.election.stake.escrow_address,
        candidate.election.escrow_key,
        candidate.address,
        100 * stake,
        "Corporate Voting Procedure using Choice Coin"
    )
    return f"Corporate Ballot tabulated. You can validate that your vote was counted correctly at https://testnet.algoexplorer.io/tx/{transaction_id[1]}/"



def countVotes(candidates):
    labels, values = [], []
    for candidate in candidates:
        _, count = count(candidate.address)
        labels.append(candidate.name)
        values.append(_/100)
    candidateScoreMap = zip(labels, values)
    winner = max(candidateScoreMap, key=candidateScoreMap.get)
    if list(candidateScoreMap.values()).count(candidateScoreMap[winner]) > 1:
        winnerList = {k:v for k,v in candidateScoreMap.items() if v == candidateScoreMap.get(winner)}
        winner = random.choice(list(winnerList.keys()))
    print(labels, values)
    print(f"Candidate {winner} recieved the most votes")
    return labels, values, winner


def corporateCountVotes(candidates):
    count_one = count(corporate_decision_one)
    count_two = count(corporate_decision_two)
    if count_one == count_two:
        winner = random.choice(corporate_decision_one, corporate_decision_two)
    else:
        winner = max(count_one, count_two)
    return count_one, count_two, winner