from http.server import BaseHTTPRequestHandler
import json
import requests
from datetime import datetime

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
        changes = {}
        for name, coingecko_id in tokens.items():
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coingecko_id}&vs_currencies=gbp&include_24hr_change=true"
            r = requests.get(url)
            data = r.json()[coingecko_id]
            prices[name] = round(data['gbp'], 4)
            changes[name] = round(data['gbp_24h_change'], 2)

        # Initial amounts
        stablecoin_initial = 5000
        heavens_initial = 5000

        # Simulated current values
        stablecoin_current = 5275.00
        heavens_current = 5450.00

        # Per-fund calculations
        stablecoin_gain = stablecoin_current - stablecoin_initial
        heavens_gain = heavens_current - heavens_initial
        stablecoin_pct = round((stablecoin_gain / stablecoin_initial) * 100, 2)
        heavens_pct = round((heavens_gain / heavens_initial) * 100, 2)

        total_current = stablecoin_current + heavens_current
        total_initial = stablecoin_initial + heavens_initial
        total_gain = total_current - total_initial
        total_gain_pct = round((total_gain / total_initial) * 100, 2)

        result = {
            "Stablecoin Strategy": f"{stablecoin_current:.2f}",
            "Heavens Vault": f"{heavens_current:.2f}",
            "Original Investment": f"{total_initial:.2f}",
            "Total": f"{total_current:.2f}",
            "Total Gain": f"{total_gain:.2f}",
            "Total Gain %": f"{total_gain_pct:.2f}",
            "Stablecoin Gain": f"{stablecoin_gain:.2f}",
            "Stablecoin Gain %": f"{stablecoin_pct:.2f}",
            "Heavens Gain": f"{heavens_gain:.2f}",
            "Heavens Gain %": f"{heavens_pct:.2f}",
            "Prices (GBP)": prices,
            "Price Changes (24h %)": changes,
            "last_updated": datetime.utcnow().isoformat()
        }

        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
