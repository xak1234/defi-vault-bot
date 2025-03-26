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
        # Fetch ETH lending rate from Compound
        compound_response = requests.get('https://api.compound.finance/api/v2/ctoken')
        compound_response.raise_for_status()
        eth_ctoken = next(token for token in compound_response.json()['cToken'] if token['underlying_symbol'] == 'ETH')
        eth_lending_apy = float(eth_ctoken['supply_rate']['value']) * 100  # Convert to percentage

        # Fetch token prices from CoinGecko (ETH and USDC for Balancer)
        price_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum,usd-coin&vs_currencies=usd')
        price_response.raise_for_status()
        prices = price_response.json()
        eth_price = prices['ethereum']['usd']
        usdc_price = prices['usd-coin']['usd']

        # Calculate Compound position
        compound_initial_usd = 2000  # Your initial investment in USD
        compound_eth_amount = compound_initial_usd / eth_price  # How much ETH you lent initially
        compound_current_value = compound_eth_amount * eth_price  # Current value in USD
        compound_hourly_return = (eth_lending_apy / 100 / 365 / 24) * compound_initial_usd  # Hourly return in USD

        # Fetch Balancer pool data (ETH/USDC 50/50 pool)
        balancer_pool_id = '0x96646936b91d6b9d7d0c47c496afbf3d6ec7b6f00020000000000000000019f'  # Example pool ID
        balancer_query = {
            'query': '''
                query {
                    pools(where: {id: "%s"}) {
                        id
                        totalLiquidity
                        totalSwapFee
                        swaps(first: 1, orderBy: timestamp, orderDirection: desc) {
                            timestamp
                        }
                    }
                }
            ''' % balancer_pool_id
        }
        balancer_response = requests.post('https://api.thegraph.com/subgraphs/name/balancer-labs/balancer-v2', json=balancer_query)
        balancer_response.raise_for_status()
        balancer_pool = balancer_response.json()['data']['pools'][0]

        # Estimate Balancer APY based on swap fees (simplified)
        total_swap_fees = float(balancer_pool['totalSwapFee'])
        total_liquidity = float(balancer_pool['totalLiquidity'])
        last_swap_timestamp = balancer_pool['swaps'][0]['timestamp'] if balancer_pool['swaps'] else 0
        current_timestamp = int(datetime.now().timestamp())
        time_diff_days = (current_timestamp - last_swap_timestamp) / (60 * 60 * 24)  # Time difference in days
        estimated_apy = (total_swap_fees / total_liquidity) * (365 / (time_diff_days or 1)) * 100  # Annualized APY

        # Calculate Balancer position (simplified, assumes 50/50 pool and no impermanent loss for now)
        balancer_initial_usd = 3000  # Your initial investment in USD
        balancer_eth_amount = (balancer_initial_usd / 2) / eth_price  # Half in ETH
        balancer_usdc_amount = (balancer_initial_usd / 2) / usdc_price  # Half in USDC
        balancer_current_value = (balancer_eth_amount * eth_price) + (balancer_usdc_amount * usdc_price)  # Current value in USD
        balancer_hourly_return = (estimated_apy / 100 / 365 / 24) * balancer_initial_usd  # Hourly return in USD

        # Placeholder data for other platforms (to be replaced later)
        uniswap_apy = 20
        uniswap_value = 2005.5457  # From last update
        uniswap_hourly_return = (uniswap_apy / 100 / 365 / 24) * 2000

        pancakeswap_apy = 40
        pancakeswap_value = 3016.5870  # From last update
        pancakeswap_hourly_return = (pancakeswap_apy / 100 / 365 / 24) * 3000

        # Construct the response
        portfolio_data = {
            'date': datetime.now().isoformat(),
            'portfolios': [
                {
                    'name': 'Medium',
                    'investments': [
                        {
                            'platform': 'Compound',
                            'assets': 'ETH',
                            'amount': compound_initial_usd,
                            'apy': eth_lending_apy,
                            'hourly_return': compound_hourly_return,
                            'total_value': compound_current_value
                        },
                        {
                            'platform': 'Balancer',
                            'assets': 'ETH/USDC (50/50)',
                            'amount': balancer_initial_usd,
                            'apy': estimated_apy,
                            'hourly_return': balancer_hourly_return,
                            'total_value': balancer_current_value
                        }
                    ]
                },
                {
                    'name': 'Heaven',
                    'investments': [
                        {
                            'platform': 'Uniswap V3',
                            'assets': 'ETH/WBTC',
                            'amount': 2000,
                            'apy': uniswap_apy,
                            'hourly_return': uniswap_hourly_return,
                            'total_value': uniswap_value
                        },
                        {
                            'platform': 'PancakeSwap',
                            'assets': 'CAKE-BNB LP',
                            'amount': 3000,
                            'apy': pancakeswap_apy,
                            'hourly_return': pancakeswap_hourly_return,
                            'total_value': pancakeswap_value
                        }
                    ]
                }
            ],
            'total_value': compound_current_value + balancer_current_value + uniswap_value + pancakeswap_value
        }

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
