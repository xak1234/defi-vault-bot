from http.server import BaseHTTPRequestHandler
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Example: Real DeFi token prices
        prices = {}

        # Tokens you care about
        tokens = {
            'ethena': 'ethena-usde',
            'pendle': 'pendle',
            'gmx': 'gmx',
            'lit': 'litentry',
            'meth': 'mantle-staked-ether'
        }

        for key, coingecko_id in tokens.items():
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=gbp'
            res = requests.get(url)
            prices[key] = res.json()[coingecko_id]['gbp']

        # Example portfolio calc
        stablecoin_value = 5000 * (1 + 0.055)  # 5.5% gain
        heavens_vault_value = 5000 * (1 + 0.09)  # 9% gain

        response = {
            "Stablecoin Strategy": f"£{stablecoin_value:.2f}",
            "Heaven's Vault": f"£{heavens_vault_value:.2f}",
            "Live Prices (GBP)": prices
        }

        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
