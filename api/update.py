from http.server import BaseHTTPRequestHandler
import json
import requests

# Starting capital
STARTING_BALANCE = 5000

# Coin allocations for Heaven's Vault (split evenly)
vault_tokens = {
    'ethena': 'ethena-usde',
    'pendle': 'pendle',
    'gmx': 'gmx',
    'lit': 'litentry',
    'meth': 'mantle-staked-ether'
}

# Initial coin prices (to simulate purchase snapshot)
initial_prices = {
    'ethena': 0.76,
    'pendle': 2.03,
    'gmx': 9.89,
    'lit': 0.38,
    'meth': 1400.00
}

# Lock in how much of each token we “bought” on Day 1 with £5000
equal_split = STARTING_BALANCE / len(initial_prices)
holdings = {
    token: equal_split / price
    for token, price in initial_prices.items()
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            ids = ','.join(vault_tokens.values())
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=gbp'
            res = requests.get(url, timeout=5)
            live_data = res.json()

            prices = {}
            new_vault_value = 0

            for token, coingecko_id in vault_tokens.items():
                live_price = live_data.get(coingecko_id, {}).get('gbp', None)
                prices[token] = round(live_price, 6) if live_price else "Unavailable"

                if isinstance(live_price, (int, float)):
                    new_vault_value += holdings[token] * live_price

            # Stablecoin vault assumed 1:1 until otherwise stated
            stablecoin_value = STARTING_BALANCE

            result = {
                "Stablecoin Strategy": f"£{stablecoin_value:.2f}",
                "Heaven's Vault": f"£{new_vault_value:.2f}",
                "Live Prices (GBP)": prices,
                "Gains": {
                    "stable": 0.0,
                    "heaven": round(((new_vault_value - STARTING_BALANCE) / STARTING_BALANCE) * 100, 2)
                }
            }

            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
