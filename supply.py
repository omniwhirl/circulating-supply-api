import requests
import json
from flask import Flask, jsonify
import os
import time


API_KEY = os.environ.get('API_KEY', None)
TOKEN_ADDRESS_OLD = "0xfc5a11d0fe8b5ad23b8a643df5eae60b979ce1bf"
TOKEN_ADDRESS_NEW = "0x4f6cbaca3151f7746273004fd7295933a9b70e69"
TOKEN_DECIMAL_ADJUSTMENT = 10**18

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

total_supply_url_old = f"https://api.polygonscan.com/api?module=stats&action=tokensupply&contractaddress={TOKEN_ADDRESS_OLD}&apikey={API_KEY}"
total_supply_url_new = f"https://api.polygonscan.com/api?module=stats&action=tokensupply&contractaddress={TOKEN_ADDRESS_NEW}&apikey={API_KEY}"
wallet_supply_url_old = f"https://api.polygonscan.com/api?module=account&action=tokenbalance&contractaddress={TOKEN_ADDRESS_OLD}&address=wallet_address&tag=latest&apikey={API_KEY}"
wallet_supply_url_new = f"https://api.polygonscan.com/api?module=account&action=tokenbalance&contractaddress={TOKEN_ADDRESS_NEW}&address=wallet_address&tag=latest&apikey={API_KEY}"


def adjust_decimals(num):
    return num / TOKEN_DECIMAL_ADJUSTMENT


def get_supply():
    total_supply_old = int(json.loads(
        requests.get(total_supply_url_old).text)['result'])
    total_supply_new = int(json.loads(
        requests.get(total_supply_url_new).text)['result'])
    total_supply = total_supply_old + total_supply_new
    circulating_supply = total_supply

    community_funds = '0xb55394d9860b781B817B634F9c6C5d5dBA35A934'
    ecosystem_funds = '0xd4C0799903364c745cA28F22dbf26dBd27ac790F'
    team_funds = '0xf0035bdf672067cF2e6Be75dED6F4e008EE9536d'
    otc_funds = '0xc4CdD4C5C730b32faDb4cC38Ec55b4E24ab69CAe'
    vested_funds = '0x5ED75c4FC1Ed359AAe12E142c570F2A8AC492402'
    # for anonymity mining rewards
    temporary_holding = '0x18049311bdf789d9ea80f3a5ffad754fa86d2a8d'
    reward_distributor = '0x70509B8EDa83702AeB783721029e158c64712fD8'

    old_accounts = [team_funds, vested_funds]
    new_accounts = [community_funds, ecosystem_funds,
                    otc_funds, temporary_holding, reward_distributor]

    # Blacklisting for old token
    for account in old_accounts:
        wallet_balance_old = int(json.loads(requests.get(
            wallet_supply_url_old.replace('wallet_address', account)).text)['result'])
        circulating_supply -= wallet_balance_old
    time.sleep(1)
    # Blacklisting for new token
    for account in new_accounts:
        wallet_balance_new = int(json.loads(requests.get(
            wallet_supply_url_new.replace('wallet_address', account)).text)['result'])
        circulating_supply -= wallet_balance_new

    return adjust_decimals(total_supply), adjust_decimals(circulating_supply)


@app.route('/')
def index():
    ts, cs = get_supply()
    return jsonify({
        'total_supply': ts,
        'circulating_supply': cs
    })


@app.route('/total')
def total():
    ts, cs = get_supply()
    return str(ts)


@app.route('/circulating')
def circulating():
    ts, cs = get_supply()
    return str(cs)
