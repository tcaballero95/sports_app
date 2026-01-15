from supabase import create_client, Client
import os

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
if not url or not key:
	raise ValueError("Debes definir las variables de entorno SUPABASE_URL y SUPABASE_KEY")
supabase: Client = create_client(url, key)
