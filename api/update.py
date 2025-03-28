import json
import os
import requests
from datetime import datetime
from http.server import BaseHTTPRequestHandler

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "xak1234/defi-vault-bot"
STATE_FILE = "vault-data/state.json"

STABLECOINS = {
    'usde': 'ethena-usde',
    'rai': 'rai',
    'frax': 'frax',
    'alusd': 'alchemix-usd',
    'lusd': 'liquity-usd'
}

HEAVENS = {
    'ethena': 'ethena-usde',
    'pendle': 'pendle',
    'gmx': 'gmx',
    'lit': 'litentry',
    'meth': 'mantle-staked-ether'
}

def fetch_prices(coin_dict):
    ids = ','.join(coin_dict.values())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=gbp"
    r = requests.get(url)
    return r.json()

def calculate_value(prices, mapping, allocations):
    values = {}
    total = 0
    for key, coingecko_id in mapping.items():
        price = prices.get(coingecko_id, {}).get('gbp', 0)
        amount = allocations.get(key, 0)
        values[key] = {"price": round(price, 6), "value": round(price * amount, 2)}
        total += price * amount
    return round(total, 2), values

def load_state():
    url = f"https://raw.githubusercontent.com/{REPO}/main/{STATE_FILE}"
    r = requests.get(url)
    return r.json()

def save_state(state):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    get_url = f"https://api.github.com/repos/{REPO}/contents/{STATE_FILE}"
    get_resp = requests.get(get_url, headers=headers)
    sha = get_resp.json().get("sha")

    put_data = {
        "message": "Update vault state",
        "content": base64_encode(json.dumps(state, indent=2)),
        "sha": sha
    }
    r = requests.put(get_url, headers=headers, json=put_data)
    return r.json()

def base64_encode(s):
    from base64 import b64encode
    return b64encode(s.encode()).decode()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        state = load_state()

        stable_prices = fetch_prices(STABLECOINS)
        heaven_prices = fetch_prices(HEAVENS)

        stable_total, stable_values = calculate_value(stable_prices, STABLECOINS, state["Stablecoin"]["allocations"])
        heaven_total, heaven_values = calculate_value(heaven_prices, HEAVENS, state["Heaven"]["allocations"])

        stable_gain = round(((stable_total - state["Stablecoin"]["initial"])/state["Stablecoin"]["initial"])*100, 2)
        heaven_gain = round(((heaven_total - state["Heaven"]["initial"])/state["Heaven"]["initial"])*100, 2)

        result = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "Stablecoin": {
                "total": f"\u00a3{stable_total:.2f}",
                "gain": f"{stable_gain}%",
                "tokens": stable_values
            },
            "Heaven": {
                "total": f"\u00a3{heaven_total:.2f}",
                "gain": f"{heaven_gain}%",
                "tokens": heaven_values
            }
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
