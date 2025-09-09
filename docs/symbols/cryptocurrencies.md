# Cryptocurrency Symbols

This page lists all supported cryptocurrency symbols available through our API.

## Supported Cryptocurrencies

Our API supports the following cryptocurrency pairs traded on Binance:

### Major Cryptocurrencies

| Symbol | Name | Description |
|--------|------|-------------|
| `BTCUSDT` | Bitcoin | World's largest cryptocurrency |
| `ETHUSDT` | Ethereum | Smart contract platform |
| `ADAUSDT` | Cardano | Proof-of-stake blockchain |
| `SOLUSDT` | Solana | High-performance blockchain |
| `DOTUSDT` | Polkadot | Interoperability protocol |
| `AVAXUSDT` | Avalanche | Platform for decentralized apps |
| `MATICUSDT` | Polygon | Ethereum scaling solution |
| `LINKUSDT` | Chainlink | Oracle network |
| `UNIUSDT` | Uniswap | Decentralized exchange |
| `BNBUSDT` | Binance Coin | Binance ecosystem token |

### DeFi Tokens

| Symbol | Name | Description |
|--------|------|-------------|
| `AAVEUSDT` | Aave | Decentralized lending protocol |
| `SUSHIUSDT` | SushiSwap | DEX and yield farming |
| `COMPUSDT` | Compound | Lending protocol |
| `MKRUSDT` | Maker | Stablecoin protocol |
| `YFIUSDT` | Yearn Finance | Yield aggregator |
| `BALUSDT` | Balancer | Automated portfolio manager |
| `CRVUSDT` | Curve | Stablecoin exchange |

### Other Popular Tokens

| Symbol | Name | Description |
|--------|------|-------------|
| `XRPUSDT` | Ripple | Payment protocol |
| `LTCUSDT` | Litecoin | Peer-to-peer cryptocurrency |
| `BCHUSDT` | Bitcoin Cash | Bitcoin fork |
| `ETCUSDT` | Ethereum Classic | Ethereum fork |
| `DOGEUSDT` | Dogecoin | Meme cryptocurrency |
| `SHIBUSDT` | Shiba Inu | Meme token |
| `CAKEUSDT` | PancakeSwap | DEX on Binance Smart Chain |
| `SXPUSDT` | Swipe | Payment protocol |
| `ALICEUSDT` | My Neighbor Alice | Gaming metaverse |

## Symbol Format

All cryptocurrency symbols follow the format: `{BASE}{QUOTE}`

- **BASE**: The cryptocurrency (e.g., BTC, ETH, ADA)
- **QUOTE**: The quote currency (always USDT for our API)

!!! example "Examples"
    - `BTCUSDT` = Bitcoin priced in USDT
    - `ETHUSDT` = Ethereum priced in USDT
    - `ADAUSDT` = Cardano priced in USDT

## Available Endpoints

### Price Endpoints

```bash
# Single cryptocurrency price
GET /crypto-price/{symbol}

# Multiple cryptocurrency prices
GET /crypto-multiple?symbols=BTCUSDT,ETHUSDT,ADAUSDT

# 24-hour statistics
GET /crypto-stats/{symbol}

# Historical data
GET /crypto-historical/{symbol}?interval=1d&limit=100
```

### Examples

#### Get Bitcoin Price
```bash
curl "https://fastapi-stock-data.onrender.com/crypto-price/BTCUSDT"
```

#### Get Multiple Prices
```bash
curl "https://fastapi-stock-data.onrender.com/crypto-multiple?symbols=BTCUSDT,ETHUSDT,SOLUSDT"
```

#### Get 24h Statistics
```bash
curl "https://fastapi-stock-data.onrender.com/crypto-stats/BTCUSDT"
```

#### Get Historical Data
```bash
curl "https://fastapi-stock-data.onrender.com/crypto-historical/BTCUSDT?interval=1d&limit=30"
```

## Historical Data Intervals

Supported intervals for historical data:

- `1m` - 1 minute
- `3m` - 3 minutes
- `5m` - 5 minutes
- `15m` - 15 minutes
- `30m` - 30 minutes
- `1h` - 1 hour
- `2h` - 2 hours
- `4h` - 4 hours
- `6h` - 6 hours
- `8h` - 8 hours
- `12h` - 12 hours
- `1d` - 1 day
- `3d` - 3 days
- `1w` - 1 week
- `1M` - 1 month

## Important Notes

### Symbol Availability
- All symbols are subject to Binance's availability
- Some symbols may be delisted or suspended
- Check the API response for current availability

### Rate Limits
- Binance API has rate limits
- Our API may implement additional rate limiting
- Consider implementing caching for frequent requests

### Data Accuracy
- Prices are real-time from Binance
- Historical data may have slight delays
- Always verify critical data from multiple sources

## Real-time Updates

For real-time price updates, consider:

1. **Polling**: Call endpoints every 30 seconds
2. **WebSocket**: Use Binance WebSocket API directly
3. **Caching**: Implement client-side caching

## Mobile Integration

When using in mobile apps:

```javascript
// React Native example
const getCryptoPrice = async (symbol) => {
    try {
        const response = await fetch(
            `https://fastapi-stock-data.onrender.com/crypto-price/${symbol}`
        );
        const data = await response.json();
        return data.price;
    } catch (error) {
        console.error('Error fetching crypto price:', error);
        return null;
    }
};
```

## Troubleshooting

### Common Issues

**404 Not Found**
- Verify the symbol format (e.g., `BTCUSDT`, not `BTC`)
- Check if the symbol is supported

**500 Internal Server Error**
- Binance API may be temporarily unavailable
- Try again in a few minutes

**Empty Response**
- Symbol may not exist or be delisted
- Check Binance website for symbol status

### Getting Help

- Check the [API Reference](../api/crypto.md) for detailed documentation
- Visit the [Interactive Demo](../crypto_demo.html) to test endpoints
- Report issues on [GitHub](https://github.com/OMCHOKSI108/FastAPI-Stock-data-)
