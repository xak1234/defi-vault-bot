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
            prices[name] = round(data['
