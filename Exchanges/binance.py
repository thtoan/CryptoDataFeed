import asyncio
import time
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)-15s : %(levelname)s : %(message)s')

class BinanceData:

    BASE = 'wss://stream.binance.com:9443'
    def __init__(self, symbol):
        self.symbol = symbol
        self.trade_stream = None
        self.candle = None
        self.patial_book = None

    async def get_trade_stream(self):
        """The trade streams push raw trade information."""
        uri = f'{self.BASE}/ws/{self.symbol}@trade'
        async with websockets.connect(uri) as trade:
            while True:
                await asyncio.sleep(0.001)
                resp = await trade.recv()  # return response.
                data = json.loads(resp)
                self.trade_stream = {'last_price': float(data['p']), 'quantity': float(data['q'])}

    async def get_candlestick_stream(self, interval):
        """The candle stream push updates to the current candlestick every second."""
        uri = f'{self.BASE}/ws/{self.symbol}@kline_{interval}'
        async with websockets.connect(uri) as candle:
            # await self.candle.put(None)
            while True:
                await asyncio.sleep(0.005)
                resp = await candle.recv()  # return response.
                data = json.loads(resp)['k']
                self.candle = {'interval': data['i'], 'open': data['o'], 'close': data['c'],
                               'high': data['h'], 'low': data['l'], 'volume': data['v']}

    async def get_partial_book_stream(self, level):
        """Top <level> bids and asks, pushed every second. Valid <levels> are 5, 10 and 20."""
        if level in {5, 10, 20}:
            uri = f'{self.BASE}/ws/{self.symbol}@depth{level}'
            async with websockets.connect(uri) as patial_book:
                while True:
                    await asyncio.sleep(0.005)
                    resp = await patial_book.recv()  # return response.
                    data = json.loads(resp)
                    self.patial_book = data
        else:
            logging.info("The level should 5, 10 or 20.")

    async def get_full_orderbook_stream(self):
        pass


async def main():
    client = BinanceData('ethusdt')
    task1 = asyncio.create_task(client.get_trade_stream())
    while True:
        await asyncio.sleep(0.001)
        logging.info(client.trade_stream)


if __name__ == '__main__':
    asyncio.run(main())
