from http.server import BaseHTTPRequestHandler
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        prices = {}

        tokens = {
            'ethena': 'ethena-usde',
            'pendle': 'pendle',
            'gmx': 'gmx',
            'lit': 'litentry',
            'meth': 'mantle-staked-ether'
        }

        for key, coingecko_id in tokens.items():
            try:
                url = f'https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=gbp'
                res = requests.get(url, timeout=5)
                data = res.json()
                if coingecko_id in data and 'gbp' in data[coingecko_id]:
                    prices[key] = data[coingecko_id]['gbp']
                else:
                    prices[key] = 'Unavailable'
            except Exception as e:
                prices[key] = f"Error: {str(e)}"

        # Simulated values
        stablecoin_value = 5000 * (1 + 0.055)
        heavens_vault_value = 5000 * (1 + 0.09)

        response = {
            "Stablecoin Strategy": f"£{stablecoin_value:.2f}",
            "Heaven's Vault": f"£{heavens_vault_value:.2f}",
            "Live Prices (GBP)": prices
        }

        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
