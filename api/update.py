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

        # Simulated current values
        stablecoin_current = 5275.00
        heavens_current = 5450.00
        total_current = stablecoin_current + heavens_current
        original_total = 10000.00
        gain = total_current - original_total
        gain_pct = round((gain / original_total) * 100, 2)

        result = {
            "Stablecoin Strategy": f"{stablecoin_current:.2f}",
            "Heavens Vault": f"{heavens_current:.2f}",
            "Original Investment": f"{original_total:.2f}",
            "Total": f"{total_current:.2f}",
            "Total Gain": f"{gain:.2f}",
            "Total Gain %": f"{gain_pct:.2f}",
            "Prices (GBP)": prices,
            "Price Changes (24h %)": changes,
            "last_updated": datetime.utcnow().isoformat()
        }

        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
