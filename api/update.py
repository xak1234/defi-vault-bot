from http.server import BaseHTTPRequestHandler
import json
import requests
from datetime import datetime

START_AMOUNT = 5000

# Cache last known good prices
last_good_prices = {}


# Working stable tokens with GBP prices
tokens_stable = {
    'usde': 'ethena-usde',
    'rai': 'rai',
    'frax': 'frax',
    'alusd': 'alchemix-usd',
    'lusd': 'liquity-usd'
}

# Heaven vault risky tokens
tokens_heaven = {
    'ethena': 'ethena-usde',
    'pendle': 'pendle',
    'gmx': 'gmx',
    'lit': 'litentry',
    'meth': 'mantle-staked-ether'
}

# Store historical values
price_history = {
    'stable': [],
    'heaven': []
}
import time  # Add at the top if not present

def fetch_live_prices(ids):
    global last_good_prices
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids)}&vs_currencies=gbp"
        res = requests.get(url, timeout=10)
        prices = res.json()

        # Check if we got actual prices
        if not prices or any(prices.get(i) is None for i in ids):
            raise ValueError("Incomplete price data received.")

        last_good_prices = prices  # Update cache
        return prices

    except Exception as e:
        print(f"⚠️ Fetch failed: {e}. Retrying in 2 seconds...")
        time.sleep(2)
        try:
            res = requests.get(url, timeout=10)
            prices = res.json()

            if not prices or any(prices.get(i) is None for i in ids):
                raise ValueError("Still incomplete on retry.")

            last_good_prices = prices  # Update cache
            return prices

        except Exception as e2:
            print(f"🔥 Retry failed: {e2}. Using last known good prices.")
            return last_good_prices.copy()


def allocate(tokens, prices):
    portfolio = {}
    total_value = 0
    split = START_AMOUNT / len(tokens)

    for name, coingecko_id in tokens.items():
        price_data = prices.get(coingecko_id)
        price = price_data.get('gbp') if price_data else None

        if not isinstance(price, (int, float)) or price <= 0:
            print(f"⚠️ Warning: Missing or invalid price for {name} ({coingecko_id}). Skipping.")
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
        print("🚨 No valid prices found — possible API failure.")
    return portfolio, round(total_value, 2)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            all_ids = list(set(tokens_stable.values()) | set(tokens_heaven.values()))
            prices = fetch_live_prices(all_ids)

            stable_holdings, stable_total = allocate(tokens_stable, prices)
            heaven_holdings, heaven_total = allocate(tokens_heaven, prices)

            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            # Save history (limit 30)
            price_history['stable'].append({'time': timestamp, 'value': round(stable_total, 2)})
            price_history['stable'] = price_history['stable'][-30:]
            price_history['heaven'].append({'time': timestamp, 'value': round(heaven_total, 2)})
            price_history['heaven'] = price_history['heaven'][-30:]

            response = {
                "Stablecoin": {
                    "total": f"£{stable_total:.2f}",
                    "tokens": {k: {'price': v['price']} for k, v in stable_holdings.items()},
                    "gain": round(((stable_total - START_AMOUNT) / START_AMOUNT) * 100, 2),
                    "history": price_history['stable']
                },
                "Heaven": {
                    "total": f"£{heaven_total:.2f}",
                    "tokens": {k: {'price': v['price']} for k, v in heaven_holdings.items()},
                    "gain": round(((heaven_total - START_AMOUNT) / START_AMOUNT) * 100, 2),
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
