import json
from web3 import Web3
from solcx import compile_standard, install_solc

install_solc("0.8.0")

with open("HashStore.sol", "r") as f:
    source = f.read()

compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {"HashStore.sol": {"content": source}},
        "settings": {
            "outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}
        },
    },
    solc_version="0.8.0",
)

abi = compiled["contracts"]["HashStore.sol"]["HashStore"]["abi"]
bytecode = compiled["contracts"]["HashStore.sol"]["HashStore"]["evm"]["bytecode"]["object"]

# connect to Ganache (change the port if yours differs)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
print("Connected to Ganache:", w3.is_connected())

account = w3.eth.accounts[0]
print("Deploying from account:", account)

HashStore = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = HashStore.constructor().transact({"from": account})
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Contract deployed at:", receipt.contractAddress)

with open("contract_info.json", "w") as f:
    json.dump({"address": receipt.contractAddress, "abi": abi}, f)

print("Saved contract_info.json")