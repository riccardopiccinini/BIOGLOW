import asyncio
from db import supabase

async def clear_data():
    print("Pulizia database in corso...")
    try:
        # Cancella osservazioni (attenuazione: questo cancella TUTTO)
        # In Supabase, per cancellare tutto serve una condizione o l'uso di un comando specifico
        # Usiamo un filtro che è sempre vero per svuotare la tabella
        res_obs = supabase.table("osservazioni").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print(f"Osservazioni rimosse.")

        # Cancella alert
        res_alerts = supabase.table("alerts").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print(f"Alert rimossi.")
        
        print("\nDatabase pulito con successo! Ora puoi rilanciare la simulazione.")
    except Exception as e:
        print(f"Errore durante la pulizia: {e}")

if __name__ == "__main__":
    asyncio.run(clear_data())
