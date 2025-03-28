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
        try:
            ids = ','.join(tokens.values())
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=gbp'
            r = requests.get(url, timeout=5)
            data = r.json()

            for name, coingecko_id in tokens.items():
                prices[name] = data.get(coingecko_id, {}).get('gbp', 'Unavailable')

        except Exception as e:
            prices = {k: f"Error: {str(e)}" for k in tokens}

        stablecoin_value = 5000 * (1 + 0.055)
        heavens_vault_value = 5000 * (1 + 0.09)

        result = {
            "Stablecoin Strategy": f"£{stablecoin_value:.2f}",
            "Heaven's Vault": f"£{heavens_vault_value:.2f}",
            "Live Prices (GBP)": prices
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
