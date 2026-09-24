import math
from collections import defaultdict
from datetime import datetime, timedelta
from db import supabase

def shannon_index(observations):
    total = len(observations)
    if total == 0:
        return 0.0
    
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

async def compute_shannon_time_series(interval="month", filters=None):
    query = supabase.table("osservazioni").select("species, date_time")
    
    if filters:
        if filters.get("station_id"):
            query = query.eq("station_id", filters["station_id"])
        if filters.get("method"):
            query = query.eq("method", filters["method"])
        if filters.get("start"):
            query = query.gte("date_time", filters["start"])
        if filters.get("end"):
            query = query.lte("date_time", filters["end"])
            
    res = query.execute()
    observations = res.data if res.data else []
    
    grouped = defaultdict(list)
    for obs in observations:
        dt_str = obs.get("date_time")
        if not dt_str: continue
        
        try:
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            if interval == "week":
                start_of_week = dt - timedelta(days=dt.weekday())
                key = start_of_week.strftime("%Y-%m-%d")
            else: # month
                key = dt.strftime("%Y-%m-01")
            grouped[key].append(obs)
        except ValueError:
            continue
            
    time_series = []
    for date_key in sorted(grouped.keys()):
        val = shannon_index(grouped[date_key])
        time_series.append({"date": date_key, "value": val})
        
    return time_series
