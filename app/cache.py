import asyncio
from typing import Dict

class InMemoryCache:
    def __init__(self):
        self.store: Dict[str, dict] = {}
        self._lock = asyncio.Lock()

    async def set(self, symbol: str, quote: dict):
        async with self._lock:
            self.store[symbol.upper()] = quote

    async def get(self, symbol: str):
        async with self._lock:
            return self.store.get(symbol.upper())

    async def get_all(self):
        async with self._lock:
            return dict(self.store)
