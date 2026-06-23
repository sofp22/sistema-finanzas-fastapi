from fastapi import APIRouter, HTTPException
from app.database.conexion import supabase
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
        
    # Mapeamos 'fecha_transaccion' a 'fecha' para cumplir con el esquema TransaccionResponse
    datos_respuesta = respuesta.data[0]
    if "fecha_transaccion" in datos_respuesta:
        datos_respuesta["fecha"] = datos_respuesta["fecha_transaccion"]
        
    return datos_respuesta

# 2. Listar todos los movimientos personales
@router.get("/", response_model=List[TransaccionResponse])
def listar_transacciones_personales():
    respuesta = supabase.table("transacciones_personales").select("*").order("fecha_transaccion", desc=True).execute()
    
    # También mapeamos cada elemento de la lista para el GET
    lista_convertida = []
    for item in respuesta.data:
        if "fecha_transaccion" in item:
            item["fecha"] = item["fecha_transaccion"]
        lista_convertida.append(item)
        
    return lista_convertida