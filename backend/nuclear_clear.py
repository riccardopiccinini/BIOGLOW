import asyncio
from db import supabase
from config import config

async def nuclear_clear():
    print("🚀 AVVIO PULIZIA TOTALE (NUCLEAR CLEAR)...")
    
    try:
        # 1. Svuota Osservazioni
        print("Svuotamento tabella osservazioni...")
        supabase.table("osservazioni").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("✅ Osservazioni rimosse.")

        # 2. Svuota Alert
        print("Svuotamento tabella alert...")
        supabase.table("alerts").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("✅ Alert rimossi.")

        # 3. Svuota Bucket Storage
        bucket_name = config.SUPABASE_STORAGE_BUCKET or "observations"
        print(f"Svuotamento bucket storage '{bucket_name}'...")
        
        # Recupera la lista di tutti i file nel bucket
        files = supabase.storage.from_(bucket_name).list()
        
        if files and len(files) > 0:
            # Prepara la lista dei percorsi da eliminare
            file_paths = [f['name'] for f in files]
            
            # Elimina i file in blocco
            supabase.storage.from_(bucket_name).remove(file_paths)
            print(f"✅ {len(file_paths)} file rimossi dallo storage.")
        else:
            print("Nessun file trovato nello storage.")

        print("\n✨ PULIZIA COMPLETATA! Il sistema è ora totalmente vuoto.")
        
    except Exception as e:
        print(f"\n❌ Errore durante la pulizia nucleare: {e}")

if __name__ == "__main__":
    asyncio.run(nuclear_clear())
