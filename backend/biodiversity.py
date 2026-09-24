import math
import traceback
from collections import defaultdict
from datetime import datetime, timedelta

# Import supabase inside function to catch import errors
def get_supabase():
    from db import supabase
    return supabase

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

def _group_observations(interval="month", filters=None):
    """Internal: group observations by week/month and return dict {date_key: [obs,...]}."""
    supabase = get_supabase()
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
        if not dt_str:
            continue

        try:
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            if interval == "week":
                start_of_week = dt - timedelta(days=dt.weekday())
                key = start_of_week.strftime("%Y-%m-%d")
            else:  # month
                key = dt.strftime("%Y-%m-01")
            grouped[key].append(obs)
        except (ValueError, AttributeError) as e:
            print(f"Date parse error for {dt_str}: {e}")
            continue

    return grouped

async def compute_shannon_time_series(interval="month", filters=None):
    """Return list of {'date': date_key, 'value': shannon_index} for frontend compatibility."""
    try:
        grouped = _group_observations(interval=interval, filters=filters)
        time_series = []
        for date_key in sorted(grouped.keys()):
            val = shannon_index(grouped[date_key])
            time_series.append({"date": date_key, "value": val})
        return time_series
    except Exception as e:
        print(f"compute_shannon_time_series error: {e}")
        print(traceback.format_exc())
        raise

async def compute_shannon_time_series_detail(interval="month", filters=None):
    """Return detailed per-group info: date, value (Shannon), species_count, total_obs, species_list (top 5)."""
    try:
        grouped = _group_observations(interval=interval, filters=filters)
        detailed = []
        for date_key in sorted(grouped.keys()):
            obs_list = grouped[date_key]
            total = len(obs_list)
            # species counts
            counts = {}
            for obs in obs_list:
                sp = obs.get('species')
                if sp:
                    counts[sp] = counts.get(sp, 0) + 1
            species_count = len(counts)
            # Shannon index
            h_val = shannon_index(obs_list)
            # top 5 species by frequency
            top_species = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
            top_species_list = [sp for sp, _ in top_species]
            detailed.append({
                "date": date_key,
                "shannon": h_val,
                "species_count": species_count,
                "total_observations": total,
                "top_species": top_species_list
            })
        return detailed
    except Exception as e:
        print(f"compute_shannon_time_series_detail error: {e}")
        print(traceback.format_exc())
        raise