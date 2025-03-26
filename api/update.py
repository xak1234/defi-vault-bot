import json
import requests
from datetime import datetime

def handler(event, context):
    # Check if the request method is GET
    if event.get('httpMethod') != 'GET':
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'Method not allowed'})
        }

    try:
        # Define tokens and their CoinGecko IDs
        tokens = {
            'ethena': 'ethena-usde',
            'pendle': 'pendle',
            'gmx': 'gmx',
            'lit': 'litentry'
        }

        # Fetch token prices from CoinGecko
        token_ids = ','.join(tokens.values())
        price_response = requests.get(f'https://api.coingecko.com/api/v3/simple/price?ids={token_ids}&vs_currencies=usd')
        price_response.raise_for_status()
        prices = price_response.json()

        # Define initial investments (hypothetical amounts for testing)
        investments = [
            {
                'platform': 'Ethena',
                'assets': 'USDe',
                'amount': 2500,  # $2,500
                'apy': 15.0  # Hypothetical APY
            },
            {
                'platform': 'Pendle',
                'assets': 'PENDLE',
                'amount': 2500,  # $2,500
                'apy': 20.0  # Hypothetical APY
            },
            {
                'platform': 'GMX',
                'assets': 'GMX',
                'amount': 2500,  # $2,500
                'apy': 25.0  # Hypothetical APY
            },
            {
                'platform': 'LIT',
                'assets': 'LIT',
                'amount': 2500,  # $2,500
                'apy': 18.0  # Hypothetical APY
            }
        ]

        # Calculate current values and hourly returns
        for investment in investments:
            token_id = tokens[investment['platform'].lower()]
            price = prices[token_id]['usd']
            # Assume the investment amount is in USD, and we bought tokens at the current price
            # For simplicity, we're not adjusting for price changes over time
            investment['total_value'] = investment['amount']  # Simplified: no price change
            investment['hourly_return'] = (investment['apy'] / 100 / 365 / 24) * investment['amount']

        # Construct the portfolio data
        portfolio_data = {
            'date': datetime.now().isoformat(),
            'portfolios': [
                {
                    'name': 'TestPortfolio',
                    'investments': investments
                }
            ],
            'total_value': sum(investment['total_value'] for investment in investments)
        }

        # Calculate total invested and total lost
        total_invested = sum(investment['amount'] for investment in investments)
        total_lost = total_invested - portfolio_data['total_value']

        # Add to the response
        portfolio_data['total_invested'] = total_invested
        portfolio_data['total_lost'] = total_lost

        return {
            'statusCode': 200,
            'body': json.dumps(portfolio_data)
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error fetching data'})
        }
