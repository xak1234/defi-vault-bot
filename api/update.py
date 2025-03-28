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

def fetch_prices():
    try:
        combined = {**STABLECOINS, **HEAVENS}
        ids = ','.join(set(combined.values()))
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=gbp"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        prices = r.json()

        if not prices or any(value == {} for value in prices.values()):
            raise ValueError("Received empty or partial prices from CoinGecko")

        return prices
    except Exception as e:
        print(f"[Error] Failed to fetch prices: {e}")
        return {}

def calculate_value(prices, mapping, allocations):
    values = {}
    total = 0
    for key, coingecko_id in mapping.items():
        try:
            price = float(prices.get(coingecko_id, {}).get('gbp', 0))
            amount = float(allocations.get(key, 0))
            if price == 0:
                raise ValueError(f"Missing price for {key}")
            values[key] = {"price": round(price, 6), "value": round(price * amount, 2)}
            total += price * amount
        except Exception as e:
            print(f"[Warning] Failed to calculate value for {key}: {e}")
            values[key] = {"price": 0, "value": 0}
    return round(total, 2), values

def load_state():
    try:
        url = f"https://raw.githubusercontent.com/{REPO}/main/{STATE_FILE}"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[Error] Failed to load state.json: {e}")
        return {
            "stablecoin": {
                "initial": 5000,
                "allocations": {
                    "usde": 1293.03,
                    "rai": 210.97,
                    "frax": 1293.03,
                    "alusd": 1050.00,
                    "lusd": 1152.97
                }
            },
            "Heaven": {
                "initial": 5000,
                "allocations": {
                    "ethena": 3242.92,
                    "pendle": 143.29,
                    "gmx": 99.29,
                    "lit": 2200.44,
                    "meth": 3.23
                }
            }
        }

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
        try:
            state = load_state()
            prices = fetch_prices()

            if not prices:
                raise ValueError("Skipping update due to missing prices")

            stable_total, stable_values = calculate_value(prices, STABLECOINS, state["stablecoin"].get("allocations", {}))
            heaven_total, heaven_values = calculate_value(prices, HEAVENS, state["Heaven"].get("allocations", {}))

            if stable_total < 100 or heaven_total < 100:
                raise ValueError("Sanity check failed: values too low, likely fetch failure")

            stable_gain = round(((stable_total - state["stablecoin"]["initial"])/state["stablecoin"]["initial"])*100, 2)
            heaven_gain = round(((heaven_total - state["Heaven"]["initial"])/state["Heaven"]["initial"])*100, 2)

            result = {
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "stablecoin": {
                    "total": f"£{stable_total:.2f}",
                    "gain": f"{stable_gain}%",
                    "tokens": stable_values
                },
                "Heaven": {
                    "total": f"£{heaven_total:.2f}",
                    "gain": f"{heaven_gain}%",
                    "tokens": heaven_values
                }
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            print(f"[Fatal] API handler failed: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Internal server error"}).encode())
