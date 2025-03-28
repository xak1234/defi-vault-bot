import json
import os
import base64
import requests
from datetime import datetime

# GitHub storage
GH_REPO = "xak1234/defi-vault-bot"
GH_FILE = "vault-data/state.json"
GH_TOKEN = os.getenv("GH_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GH_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def read_state():
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{GH_FILE}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        content = base64.b64decode(r.json()['content']).decode()
        return json.loads(content)
    return None

def write_state(data):
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{GH_FILE}"
    get = requests.get(url, headers=HEADERS)
    sha = get.json()['sha']
    content = base64.b64encode(json.dumps(data).encode()).decode()

    payload = {
        "message": "Update vault state",
        "content": content,
        "sha": sha
    }
    r = requests.put(url, headers=HEADERS, data=json.dumps(payload))
    return r.status_code == 200 or r.status_code == 201

def get_prices(ids):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=gbp"
    r = requests.get(url)
    return r.json()

def handler(event, context):
    # Token lists
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

    try:
        state = read_state() or {
            "stable": {k: {"amount": 1000} for k in stable_tokens},
            "heaven": {k: {"amount": 1000} for k in heaven_tokens}
        }

        all_ids = list(set(stable_tokens.values()) | set(heaven_tokens.values()))
        prices = get_prices(all_ids)

        def calculate_total(portfolio, tokens):
            total = 0
            token_data = {}
            for key, token_id in tokens.items():
                price = prices[token_id]['gbp']
                amount = state[portfolio][key]['amount']
                value = amount * price
                token_data[key] = {
                    "amount": round(amount, 2),
                    "price": round(price, 6),
                    "value": round(value, 2)
                }
                total += value
            return round(total, 2), token_data

        stable_total, stable_data = calculate_total("stable", stable_tokens)
        heaven_total, heaven_data = calculate_total("heaven", heaven_tokens)

        state["last_updated"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        write_state(state)

        return {
            "statusCode": 200,
            "headers": { "Content-Type": "application/json" },
            "body": json.dumps({
                "timestamp": state["last_updated"],
                "Stablecoin": {
                    "total": f"£{stable_total}",
                    "gain": "0%",
                    "tokens": stable_data
                },
                "Heaven": {
                    "total": f"£{heaven_total}",
                    "gain": "0%",
                    "tokens": heaven_data
                }
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
