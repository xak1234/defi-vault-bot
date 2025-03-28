from http.server import BaseHTTPRequestHandler
import json
import requests

START_AMOUNT = 5000

stable_tokens = {
    'usde': 'ethena-usde',
    'sdai': 'superstate-sdai',
    'mimatic': 'mimatic',
    'musd': 'mstable-usd',
    'gdai': 'gdai'
}

heaven_tokens = {
    'ethena': 'ethena-usde',
    'pendle': 'pendle',
    'gmx': 'gmx',
    'lit': 'litentry',
    'meth': 'mantle-staked-ether'
}

# Initial prices at the time of investment (manually set)
stable_initial = {
    'usde': 0.76,
    'sdai': 0.78,
    'mimatic': 0.79,
    'musd': 0.82,
    'gdai': 0.81
}

heaven_initial = {
    'ethena': 0.76,
    'pendle': 2.03,
    'gmx': 9.89,
    'lit': 0.38,
    'meth': 1400.00
}

def calculate_portfolio(tokens, initial_prices, live_data):
    portfolio = {
        'total': 0,
        'tokens': {}
    }
    split = START_AMOUNT / len(tokens)

    for token, coingecko_id in tokens.items():
        live_price = live_data.get(coingecko_id, {}).get('gbp', 0)
        initial_price = initial_prices[token]
        quantity = split / initial_price
        value_now = quantity * live_price
        portfolio['tokens'][token] = {
            'price': round(live_price, 6),
            'quantity': round(quantity, 6),
            'value': round(value_now, 2)
        }
        portfolio['total'] += value_now

    portfolio['total'] = f"£{portfolio['total']:.2f}"
    gain = ((float(portfolio['total'][1:]) - START_AMOUNT) / START_AMOUNT) * 100
    portfolio['gain'] = round(gain, 2)
    return portfolio

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            ids = ','.join(set(list(stable_tokens.values()) + list(heaven_tokens.values())))
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=gbp"
            r = requests.get(url, timeout=5)
            live_data = r.json()

            response = {
                "Stablecoin": calculate_portfolio(stable_tokens, stable_initial, live_data),
                "Heaven": calculate_portfolio(heaven_tokens, heaven_initial, live_data)
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
