import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Le decimos a Python que lea el archivo .env oculto
load_dotenv()

# 2. Traemos las variables que guardaste en el .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 3. Una pequeña validación de seguridad por si olvidaste llenar el .env
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("ERROR: Falta configurar las variables en tu archivo .env")

# 4. Creamos la conexión oficial
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)