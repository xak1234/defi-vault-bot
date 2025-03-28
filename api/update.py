import json
import os
import requests
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from base64 import b64encode

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
    ids = ','.join(set(list(STABLECOINS.values()) + list(HEAVENS.values())))
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=gbp"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        expected = list(set(STABLECOINS.values()) | set(HEAVENS.values()))
        for token in expected:
            if token not in data or 'gbp' not in data[token]:
                raise ValueError(f"Missing price for {token}")
        return data
    except Exception as e:
        print(f"[Error] Price fetch failed: {e}")
        return {}

def load_state():
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{REPO}/contents/{STATE_FILE}"
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        raw = r.json()
        content = json.loads(b64decode(raw['content']).decode())
        sha = raw['sha']
        return content, sha
    except Exception as e:
        print(f"[Error] Failed to load state: {e}")
        return {}, None

def save_state(state, sha):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/repos/{REPO}/contents/{STATE_FILE}"
    body = {
        "message": "Update vault state",
        "content": b64encode(json.dumps(state, indent=2).encode()).decode(),
        "sha": sha
    }
    try:
        res = requests.put(url, headers=headers, json=body)
        print("[INFO] State saved to GitHub.")
    except Exception as e:
        print(f"[Error] Failed to save state: {e}")

def calculate_value(prices, mapping, allocations):
    total = 0
    token_data = {}
    for key, coingecko_id in mapping.items():
        price = float(prices.get(coingecko_id, {}).get('gbp', 0))
        amount = float(allocations.get(key, 0))
        value = price * amount
        token_data[key] = {
            "price": round(price, 6),
            "value": round(value, 2)
        }
        total += value
    return round(total, 2), token_data

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            state, sha = load_state()
            prices = fetch_prices()

            if not state or not sha or not prices:
                raise Exception("Missing state or price data")

            stable_total, stable_tokens = calculate_value(prices, STABLECOINS, state["Stablecoin"]["allocations"])
            heaven_total, heaven_tokens = calculate_value(prices, HEAVENS, state["Heaven"]["allocations"])

            # Sanity check
            if stable_total < 100 or heaven_total < 100:
                raise Exception("Sanity check failed: totals too low")

            stable_gain = round(((stable_total - state["Stablecoin"]["initial"]) / state["Stablecoin"]["initial"]) * 100, 2)
            heaven_gain = round(((heaven_total - state["Heaven"]["initial"]) / state["Heaven"]["initial"]) * 100, 2)

            result = {
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "Stablecoin": {
                    "total": f"£{stable_total:.2f}",
                    "gain": f"{stable_gain}%",
                    "tokens": stable_tokens
                },
                "Heaven": {
                    "total": f"£{heaven_total:.2f}",
                    "gain": f"{heaven_gain}%",
                    "tokens": heaven_tokens
                }
            }

            save_state(state, sha)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            print(f"[Fatal] API handler failed: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
