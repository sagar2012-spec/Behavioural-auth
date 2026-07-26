import json
import os
from web3 import Web3

# work out the path to contract_info.json regardless of where we run from
HERE = os.path.dirname(os.path.abspath(__file__))
INFO_PATH = os.path.join(HERE, "..", "blockchain", "contract_info.json")

with open(INFO_PATH, "r") as f:
    info = json.load(f)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
contract = w3.eth.contract(address=info["address"], abi=info["abi"])
account = w3.eth.accounts[0]


def store_hash(pattern_id, hash_value):
    """Write a hash to the blockchain. Costs gas, creates a transaction."""
    tx = contract.functions.storeHash(pattern_id, hash_value).transact({"from": account})
    w3.eth.wait_for_transaction_receipt(tx)
    return True


def get_hash(pattern_id):
    """Read a hash back. Free, no transaction."""
    return contract.functions.getHash(pattern_id).call()


def is_connected():
    return w3.is_connected()