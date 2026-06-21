from fastapi import APIRouter, HTTPException
from app.database.conexion import supabase
from app.models.finanzas import TransaccionCreate
from app.models.finanzas import TransaccionCreate, TransaccionResponse
from typing import List

router = APIRouter(prefix="/finanzas-personales", tags=["Finanzas Personales"])

# 1. Registrar un ingreso o gasto personal
@router.post("/", response_model=TransaccionResponse)
def registrar_transaccion_personal(transaccion: TransaccionCreate):
    if transaccion.tipo not in ['ingreso', 'gasto']:
        raise HTTPException(status_code=400, detail="El tipo debe ser 'ingreso' o 'gasto'")
        
    datos = transaccion.model_dump()
    respuesta = supabase.table("transacciones_personales").insert(datos).execute()
    
    if not respuesta.data:
        raise HTTPException(status_code=400, detail="No se pudo registrar el movimiento")
        
    return respuesta.data[0]

# 2. Listar todos los movimientos personales
@router.get("/", response_model=List[TransaccionResponse])
def listar_transacciones_personales():
    respuesta = supabase.table("transacciones_personales").select("*").order("fecha_transaccion", desc=True).execute()
    return respuesta.data