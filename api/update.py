import os
import json
import requests
from datetime import datetime
from http.server import BaseHTTPRequestHandler

# GitHub settings
github_repo = "xak1234/defi-vault-bot"  # change to your repo
state_file_path = "vault-data/state.json"  # relative path in your repo
github_token = os.environ.get("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {github_token}",
    "Accept": "application/vnd.github+json"
}

def get_github_state():
    url = f"https://api.github.com/repos/{github_repo}/contents/{state_file_path}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        content = res.json()
        sha = content['sha']
        decoded = json.loads(requests.get(content['download_url']).text)
        return decoded, sha
    return {}, None

def update_github_state(data, sha):
    url = f"https://api.github.com/repos/{github_repo}/contents/{state_file_path}"
    encoded = json.dumps(data, indent=2)
    payload = {
        "message": "Update vault state",
        "content": encoded.encode("utf-8").decode("utf-8"),
        "sha": sha,
        "branch": "main"
    }
    return requests.put(url, headers=headers, data=json.dumps(payload))

def fetch_price(token_id):
    r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={token_id}&vs_currencies=gbp")
    return round(r.json()[token_id]['gbp'], 6)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            state, sha = get_github_state()

            if not state:
                state = {
                    "Stablecoin": {
                        "tokens": {
                            "usde": {"id": "ethena-usde", "amount": 3238.55},
                            "rai": {"id": "rai", "amount": 842.67},
                            "frax": {"id": "frax", "amount": 325.91},
                            "alusd": {"id": "alchemix-usd", "amount": 593.8},
                            "lusd": {"id": "liquity-usd", "amount": 584.07}
                        },
                        "starting_value": 5000
                    },
                    "Heaven": {
                        "tokens": {
                            "ethena": {"id": "ethena-usde", "amount": 3238.55},
                            "pendle": {"id": "pendle", "amount": 842.67},
                            "gmx": {"id": "gmx", "amount": 325.91},
                            "lit": {"id": "litentry", "amount": 593.8},
                            "meth": {"id": "mantle-staked-ether", "amount": 584.07}
                        },
                        "starting_value": 5000
                    }
                }

            def calculate_portfolio(portfolio):
                total = 0
                for k, v in portfolio['tokens'].items():
                    price = fetch_price(v['id'])
                    v['price'] = price
                    v['value'] = round(price * v['amount'], 2)
                    total += v['value']
                portfolio['total'] = round(total, 2)
                portfolio['gain'] = round(((total - portfolio['starting_value']) / portfolio['starting_value']) * 100, 2)
                return portfolio

            stable = calculate_portfolio(state['Stablecoin'])
            heaven = calculate_portfolio(state['Heaven'])

            # Save new state
            update_github_state(state, sha)

            # Respond with portfolio data
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                "Stablecoin": stable,
                "Heaven": heaven
            }).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
