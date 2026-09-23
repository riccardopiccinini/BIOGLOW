import math
from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def shannon_index(observations):
    # observations: list of dicts with 'species'
    total = len(observations)
    if total == 0:
        return 0.0
    # count per species
    counts = {}
    for obs in observations:
        sp = obs.get('species')
        if sp:
            counts[sp] = counts.get(sp, 0) + 1
    h = 0.0
    for cnt in counts.values():
        p = cnt / total
        h -= p * math.log(p)
    return h

async def compute_shannon():
    # fetch observations from Supabase (you may filter by date range later)
    res = supabase.table("osservazioni").select("species").execute()
    observations = res.data if res.data else []
    return shannon_index(observations)
