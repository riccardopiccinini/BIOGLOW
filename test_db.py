import asyncio
from db import supabase

async def test():
    try:
        res = supabase.table("stations").select("*").execute()
        print(f"Stations found: {len(res.data) if res.data else 0}")
        for s in res.data:
            print(s)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
