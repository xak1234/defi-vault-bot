from http.server import BaseHTTPRequestHandler
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        tokens = {
            'ethena': 'ethena-usde',
            'pendle': 'pendle',
            'gmx': 'gmx',
            'lit': 'litentry',
            'meth': 'mantle-staked-ether'
        }

        prices = {}
        for name, coingecko_id in tokens.items():
            r = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=gbp')
            prices[name] = r.json()[coingecko_id]['gbp']

        stablecoin_value = 5000 * (1 + 0.055)
        heavens_vault_value = 5000 * (1 + 0.09)

        result = {
            "Stablecoin Strategy": f"£{stablecoin_value:.2f}",
            "Heaven's Vault": f"£{heavens_vault_value:.2f}",
            "Prices (GBP)": prices
        }

        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
