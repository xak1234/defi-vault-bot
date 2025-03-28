import json
import os
import requests
from datetime import datetime

STATE_FILE = "/tmp/vault_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "Stablecoin": {"initial": 5000, "tokens": {}, "gain": 0},
        "Heaven": {"initial": 5000, "tokens": {}, "gain": 0}
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

class handler:
    def __init__(self, *args, **kwargs):
        pass

    def do_GET(self):
        state = load_state()

        stable_tokens = {
            'usde': 'ethena-usde',
            'rai': 'rai',
            'frax': 'frax',
            'alusd': 'alchemix-usd',
            'lusd': 'liquity-usd'
        }

        heaven_tokens = {
            'ethena': 'ethena-usde',
            'pendle': 'pendle',
            'gmx': 'gmx',
            'lit': 'litentry',
            'meth': 'mantle-staked-ether'
        }

        def fetch_prices(token_map):
            prices = {}
            for sym, cid in token_map.items():
                url = f'https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=gbp'
                r = requests.get(url).json()
                prices[sym] = round(r[cid]['gbp'], 6)
            return prices

        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        stable_prices = fetch_prices(stable_tokens)
        heaven_prices = fetch_prices(heaven_tokens)

        # Equal allocation
        per_stable = state['Stablecoin']['initial'] / len(stable_tokens)
        per_heaven = state['Heaven']['initial'] / len(heaven_tokens)

        stable_value = 0
        for sym, price in stable_prices.items():
            amount = per_stable / price
            val = amount * price
            state['Stablecoin']['tokens'][sym] = {'price': price, 'amount': round(amount, 6)}
            stable_value += val

        heaven_value = 0
        for sym, price in heaven_prices.items():
            amount = per_heaven / price
            val = amount * price
            state['Heaven']['tokens'][sym] = {'price': price, 'amount': round(amount, 6)}
            heaven_value += val

        state['Stablecoin']['gain'] = round((stable_value - state['Stablecoin']['initial']) / state['Stablecoin']['initial'] * 100, 2)
        state['Heaven']['gain'] = round((heaven_value - state['Heaven']['initial']) / state['Heaven']['initial'] * 100, 2)

        response = {
            "timestamp": now,
            "Stablecoin": {
                "total": f"£{stable_value:.2f}",
                "gain": state['Stablecoin']['gain'],
                "tokens": {sym: {"price": f"{v['price']:.6f}"} for sym, v in state['Stablecoin']['tokens'].items()}
            },
            "Heaven": {
                "total": f"£{heaven_value:.2f}",
                "gain": state['Heaven']['gain'],
                "tokens": {sym: {"price": f"{v['price']:.6f}"} for sym, v in state['Heaven']['tokens'].items()}
            }
        }

        save_state(state)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(response)
        }

    def __call__(self, environ, start_response):
        result = self.do_GET()
        start_response(f"{result['statusCode']} OK", list(result['headers'].items()))
        return [result['body'].encode('utf-8')]
