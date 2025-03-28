from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
from datetime import datetime
import time

# Starting amounts
START_AMOUNT_STABLE = 5000
START_AMOUNT_HEAVEN = 5000

# Cache last known good prices
last_good_prices = {}

# Stable tokens
tokens_stable = {
    'usde': 'ethena-usde',
    'rai': 'rai',
    'frax': 'frax',
    'alusd': 'alchemix-usd',
    'lusd': 'liquity-usd'
}

# Risky tokens
tokens_heaven = {
    'ethena': 'ethena-usde',
    'pendle': 'pendle',
    'gmx': 'gmx',
    'lit': 'litentry',
    'meth': 'mantle-staked-ether'
}

# History tracking
price_history = {
    'stable': [],
    'heaven': []
}

def fetch_live_prices(ids):
    global last_good_prices
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=gbp"
        res = requests.get(url, timeout=10)
        prices = res.json()
        if not prices or any(prices.get(i) is None for i in ids):
            raise ValueError("Incomplete price data.")
        last_good_prices = prices
        return prices
    except Exception as e:
        print(f"⚠️ Fetch failed: {e}. Retrying...")
        time.sleep(2)
        try:
            res = requests.get(url, timeout=10)
            prices = res.json()
            if not prices or any(prices.get(i) is None for i in ids):
                raise ValueError("Still incomplete.")
            last_good_prices = prices
            return prices
        except Exception as e2:
            print(f"🔥 Retry failed: {e2}. Using cached prices.")
            return last_good_prices.copy()

def allocate(tokens, prices, start_amount):
    portfolio = {}
    total_value = 0
    split = start_amount / len(tokens)
    for name, coingecko_id in tokens.items():
        price_data = prices.get(coingecko_id)
        price = price_data.get('gbp') if price_data else None
        if not isinstance(price, (int, float)) or price <= 0:
            print(f"⚠️ Missing or invalid price for {name}. Skipping.")
            continue
        qty = split / price
        value_now = qty * price
        portfolio[name] = {
            'price': round(price, 6),
            'quantity': round(qty, 4),
            'value': round(value_now, 2)
        }
        total_value += value_now
    if total_value == 0:
        print("🚨 Total value zero. Possible API failure.")
    return portfolio, round(total_value, 2)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            all_ids = list(set(tokens_stable.values()) | set(tokens_heaven.values()))
            prices = fetch_live_prices(all_ids)

            stable_holdings, stable_total = allocate(tokens_stable, prices, START_AMOUNT_STABLE)
            heaven_holdings, heaven_total = allocate(tokens_heaven, prices, START_AMOUNT_HEAVEN)

            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            # History (last 30)
            price_history['stable'].append({'time': timestamp, 'value': stable_total})
            price_history['stable'] = price_history['stable'][-30:]
            price_history['heaven'].append({'time': timestamp, 'value': heaven_total})
            price_history['heaven'] = price_history['heaven'][-30:]

            response = {
                "Stablecoin": {
                    "initial_investment": f"£{START_AMOUNT_STABLE:.2f}",
                    "current_value": f"£{stable_total:.2f}",
                    "gain_amount": round(stable_total - START_AMOUNT_STABLE, 2),
                    "gain_percent": round(((stable_total - START_AMOUNT_STABLE) / START_AMOUNT_STABLE) * 100, 2),
                    "tokens": {k: {'price': v['price']} for k, v in stable_holdings.items()},
                    "history": price_history['stable']
                },
                "Heaven": {
                    "initial_investment": f"£{START_AMOUNT_HEAVEN:.2f}",
                    "current_value": f"£{heaven_total:.2f}",
                    "gain_amount": round(heaven_total - START_AMOUNT_HEAVEN, 2),
                    "gain_percent": round(((heaven_total - START_AMOUNT_HEAVEN) / START_AMOUNT_HEAVEN) * 100, 2),
                    "tokens": {k: {'price': v['price']} for k, v in heaven_holdings.items()},
                    "history": price_history['heaven']
                },
                "timestamp": timestamp
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

# Run the server
if __name__ == "__main__":
    print("🚀 Daddy's DeFi Vault server is live at http://localhost:8000")
    server = HTTPServer(('', 8000), handler)
    server.serve_forever()
