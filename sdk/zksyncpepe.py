from .claim import main_c_claim
from loguru import logger
import requests
import json
import web3

dict_eligible_wallet = {}


def get_response(response):
    if type(response.content) is bytes:
        return json.loads(response.content.decode())
    else:
        return False


def send_req(address: str):

     with requests.Session() as session:
        try:
            private_key = address
            address = web3.Account.from_key(address).address.lower()

            response = session.get(f'https://www.zksyncpepe.com/resources/amounts/{address}.json')
            proof = requests.get(f'https://www.zksyncpepe.com/resources/proofs/{address}.json').json()
            token = get_response(response)

            return private_key, token, proof

        except Exception as e:
            pass


def get_token_from_eligible_account(wallets: list):

    logger.info(f'Найдено {len(wallets)} кошельков')

    for address in wallets:
        try:
            private_key, token, proof = send_req(address)
            if token[0]:
                logger.info(f'{web3.Account.from_key(address).address.lower()} | BALANCE {token[0]} ZKPEPE')
                dict_eligible_wallet[private_key] = [token, proof]

        except:
            pass
    main_c_claim(dict_eligible_wallet)



def main_claim(wallets: list):
    get_token_from_eligible_account(wallets)
