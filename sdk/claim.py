import random
import time
from .config import min_delay, max_delay, gwei_limit

import web3
from web3.middleware import geth_poa_middleware
from loguru import logger


url = "https://1rpc.io/zksync2-era"

web3s = web3.Web3(web3.Web3.HTTPProvider(url))
web3s.middleware_onion.inject(geth_poa_middleware, layer=0)

web3_eth = web3.Web3(web3.Web3.HTTPProvider('https://rpc.ankr.com/eth'))

address_contract = '0x95702a335e3349d197036Acb04BECA1b4997A91a'
abi_contract = '[ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "previousOwner", "type": "address" }, { "indexed": true, "internalType": "address", "name": "newOwner", "type": "address" } ], "name": "OwnershipTransferred", "type": "event" }, { "inputs": [], "name": "airDropToken", "outputs": [ { "internalType": "contract IERC20", "name": "", "type": "address" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "internalType": "bytes32[]", "name": "proof", "type": "bytes32[]" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "claim", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [ { "internalType": "address", "name": "", "type": "address" } ], "name": "claimRecord", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "stateMutability": "view", "type": "function" }, { "inputs": [ { "internalType": "address", "name": "to", "type": "address" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "devWithdraw", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [], "name": "merkleRoot", "outputs": [ { "internalType": "bytes32", "name": "", "type": "bytes32" } ], "stateMutability": "view", "type": "function" }, { "inputs": [], "name": "owner", "outputs": [ { "internalType": "address", "name": "", "type": "address" } ], "stateMutability": "view", "type": "function" }, { "inputs": [], "name": "renounceOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [ { "internalType": "address", "name": "tokenAddress", "type": "address" } ], "name": "setClaimTokenAddress", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [ { "internalType": "bytes32", "name": "_merkleRoot", "type": "bytes32" } ], "name": "setMerkleRoot", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [ { "internalType": "address", "name": "newOwner", "type": "address" } ], "name": "transferOwnership", "outputs": [], "stateMutability": "nonpayable", "type": "function" }, { "inputs": [ { "internalType": "bytes32[]", "name": "proof", "type": "bytes32[]" }, { "internalType": "bytes32", "name": "root", "type": "bytes32" }, { "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "vertifyMerkelProof", "outputs": [ { "internalType": "bool", "name": "", "type": "bool" } ], "stateMutability": "view", "type": "function" } ]'
contract = web3s.eth.contract(address=address_contract, abi=abi_contract)


def claim_token(dict_with_info_acc):
    with open('Data/wallets.txt') as apw:
        wallets = [row.strip() for row in apw]

    for private in wallets:
        current_gwei = web3s.from_wei(web3_eth.eth.gas_price, 'gwei')
        while current_gwei > gwei_limit:
            logger.info(f'Current gwei: {round(current_gwei)} | Waiting for {gwei_limit} gwei | Sleep for 10 seconds')
            time.sleep(10)
            current_gwei = web3s.from_wei(web3_eth.eth.gas_price, 'gwei')

        try:
            nonce = web3s.eth.get_transaction_count(web3s.to_checksum_address(web3.Account.from_key(private).address))

            trx = contract.functions.claim(dict_with_info_acc[private][1], dict_with_info_acc[private][0][0] * 10 ** 18).build_transaction({
                "from": web3.Account.from_key(private).address,
                'nonce': nonce,
                'gasPrice': web3s.eth.gas_price,
            })
            sign_txn_claim = web3s.eth.account.sign_transaction(trx, private_key=private)
            transaction_claim = web3s.eth.send_raw_transaction(sign_txn_claim.rawTransaction)

            logger.success(f"Address: {web3.Account.from_key(private).address} PUSH SUCCESS | Transaction Hash: {web3s.to_hex(transaction_claim)} ")

            web3s.eth.wait_for_transaction_receipt(web3s.to_hex(transaction_claim))

            random_sleep = random.randint(min_delay, max_delay)

            logger.success(f"Address: {web3.Account.from_key(private).address} CLAIM TOKEN SUCCESS | Sleep for {random_sleep} seconds")
            time.sleep(random_sleep)


        except Exception as e:
            logger.error(f'{web3.Account.from_key(private).address} | {e}')

def main_c_claim(dicts):
    claim_token(dicts)

