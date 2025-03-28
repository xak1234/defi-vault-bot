from http.server import BaseHTTPRequestHandler
import json
import requests

STARTING_BALANCE = 5000

# Tokens and IDs
vault_tokens = {
    'ethena': 'ethena-usde',
    'pendle': 'pendle',
    'gmx': 'gmx',
    'lit': 'litentry',
    'meth': 'mantle-staked-ether'
}

# Initial token prices at 'investment time'
initial_prices = {
    'ethena': 0.76,
    'pendle': 2.03,
    'gmx': 9.89,
    'lit': 0.38,
    'meth': 1400.00
}

# How much of each token we hold in Heaven's Vault
equal_split = STARTING_BALANCE / len(vault_tokens)
holdings = {
    token: equal_split / initial_prices[token]
    for token in vault_tokens
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            ids = ','.join(vault_tokens.values())
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=gbp'
            res = requests.get(url, timeout=5)
            live_data = res.json()

            prices = {}
            heaven_value = 0

            for token, coingecko_id in vault_tokens.items():
                live_price = live_data.get(coingecko_id, {}).get('gbp')
                if live_price:
                    prices[token] = round(live_price, 6)
                    heaven_value += holdings[token] * live_price
                else:
                    prices[token] = "Unavailable"

            stablecoin_value = STARTING_BALANCE  # Assume 1:1 backing, no fluctuation

            result = {
                "Stablecoin Strategy": f"£{stablecoin_value:.2f}",
                "Heaven's Vault": f"£{heaven_value:.2f}",
                "Live Prices (GBP)": prices,
                "Gains": {
                    "stable": 0.00,
                    "heaven": round(((heaven_value - STARTING_BALANCE) / STARTING_BALANCE) * 100, 2)
                }
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
