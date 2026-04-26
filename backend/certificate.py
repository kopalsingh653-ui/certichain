from web3 import Web3
from config import *

web3 = Web3(Web3.HTTPProvider(RPC_URL))
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

def generate_hash(data):
    return web3.keccak(text=data).hex()

def issue_cert(name, course):
    cert_hash = generate_hash(name + course)

    tx = contract.functions.issueCertificate(
        cert_hash, name, course
    ).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'nonce': web3.eth.get_transaction_count(ACCOUNT_ADDRESS),
        'gas': 2000000,
        'gasPrice': web3.to_wei('20', 'gwei')
    })

    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    return cert_hash, tx_hash.hex()

def verify_cert(cert_hash):
    return contract.functions.verify(cert_hash).call()