import requests
import json
from flask import Flask, jsonify
import os


API_KEY = os.environ.get('API_KEY', None)
TOKEN_ADDRESS = "0xfc5a11d0fe8b5ad23b8a643df5eae60b979ce1bf"
TOKEN_DECIMAL_ADJUSTMENT = 10**18

app = Flask(__name__)

total_supply_url = f"https://api.polygonscan.com/api?module=stats&action=tokensupply&contractaddress={TOKEN_ADDRESS}&apikey={API_KEY}"
wallet_supply_url = f"https://api.polygonscan.com/api?module=account&action=tokenbalance&contractaddress={TOKEN_ADDRESS}&address=wallet_address&tag=latest&apikey={API_KEY}"


def adjust_decimals(num):
    return num / TOKEN_DECIMAL_ADJUSTMENT


def get_supply():
    total_supply = int(json.loads(
        requests.get(total_supply_url).text)['result'])
    circulating_supply = total_supply

    community_funds = '0xb55394d9860b781B817B634F9c6C5d5dBA35A934'
    ecosystem_funds = '0xd4C0799903364c745cA28F22dbf26dBd27ac790F'
    team_funds = '0xf0035bdf672067cF2e6Be75dED6F4e008EE9536d'
    otc_funds = '0xc4CdD4C5C730b32faDb4cC38Ec55b4E24ab69CAe'

    accounts = [community_funds, ecosystem_funds, team_funds, otc_funds]

    for account in accounts:
        wallet_balance = int(json.loads(requests.get(
            wallet_supply_url.replace('wallet_address', account)).text)['result'])
        circulating_supply -= wallet_balance

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