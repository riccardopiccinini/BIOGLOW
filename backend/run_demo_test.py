import asyncio
import sys
import os
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.demo import load_demo_data
from backend.biodiversity import compute_shannon

async def run():
    await load_demo_data()
    index = await compute_shannon()
    print('Shannon index (demo):', index)

if __name__ == '__main__':
    asyncio.run(run())

