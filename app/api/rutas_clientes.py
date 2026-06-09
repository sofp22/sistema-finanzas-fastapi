from fastapi import APIRouter, HTTPException
from app.database.conexion import supabase
from app.models.cliente import ClienteCreate, ClienteResponse
from typing import List

router = APIRouter(prefix="/clientes", tags=["Clientes"])

# 1. Crear un cliente
@router.post("/", response_model=ClienteResponse)
def crear_cliente(cliente: ClienteCreate):
    datos_cliente = cliente.model_dump()
    # Usamos "clientes" en minúscula para que Supabase lo entienda
    respuesta = supabase.table("clientes").insert(datos_cliente).execute()
    
    if not respuesta.data:
        raise HTTPException(status_code=400, detail="No se pudo registrar el cliente")
        
    return respuesta.data[0]

# 2. Ver todos los clientes
@router.get("/", response_model=List[ClienteResponse])
def listar_clientes():
    # Usamos "clientes" en minúscula
    respuesta = supabase.table("clientes").select("*").order("nombre").execute()
    return respuesta.data