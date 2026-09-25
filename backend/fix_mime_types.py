import asyncio
from db import supabase
from config import config
from pathlib import Path

MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
}

async def process_folder(folder_path=""):
    bucket_name = config.SUPABASE_STORAGE_BUCKET
    
    try:
        # List entries in the current folder
        entries = supabase.storage.from_(bucket_name).list(folder_path)
        
        if not entries:
            return

        for entry in entries:
            name = entry.get('name')
            if not name: continue
            
            full_path = f"{folder_path}/{name}" if folder_path else name
            
            # Check if it's a folder (id is None or name ends with /)
            if entry.get('id') is None:
                await process_folder(full_path)
                continue
                
            ext = Path(name).suffix.lower()
            correct_mime = MIME_TYPES.get(ext)
            
            if not correct_mime:
                continue

            print(f"Correzione {full_path} -> {correct_mime}...")
            
            try:
                # Download
                file_data = supabase.storage.from_(bucket_name).download(full_path)
                
                # Upload with correct MIME and upsert
                supabase.storage.from_(bucket_name).upload(
                    path=full_path,
                    file=file_data,
                    file_options={"content-type": correct_mime, "upsert": "true"}
                )
            except Exception as e:
                print(f"Errore con file {full_path}: {e}")

    except Exception as e:
        print(f"Errore durante la scansione di {folder_path}: {e}")

async def main():
    if not config.SUPABASE_STORAGE_BUCKET:
        print("Errore: SUPABASE_STORAGE_BUCKET non configurato.")
        return

    print(f"Avvio correzione ricorsiva MIME types nel bucket: {config.SUPABASE_STORAGE_BUCKET}...")
    await process_folder()
    print("\nOperazione completata!")

if __name__ == "__main__":
    asyncio.run(main())
