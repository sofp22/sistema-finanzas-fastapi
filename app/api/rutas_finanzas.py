from fastapi import APIRouter, HTTPException
from app.database.conexion import supabase
from app.models.finanzas import TransaccionCreate, TransaccionResponse
from typing import List
from uuid import UUID

router = APIRouter(prefix="/finanzas-personales", tags=["Finanzas Personales"])

# 1. REGISTRAR TRANSACCIÓN PERSONAL (Soporta tarjeta_credito, efectivo, cuenta_bancaria)
@router.post("/", response_model=TransaccionResponse)
def registrar_transaccion_personal(transaccion: TransaccionCreate):
    if transaccion.tipo not in ['ingreso', 'gasto']:
        raise HTTPException(status_code=400, detail="El tipo debe ser 'ingreso' o 'gasto'")
        
    if transaccion.metodo_pago not in ['cuenta_bancaria', 'efectivo', 'tarjeta_credito']:
        raise HTTPException(status_code=400, detail="Método de pago inválido")
        
    datos = transaccion.model_dump()
    datos["estado"] = "activo"
    
    respuesta = supabase.table("transacciones_personales").insert(datos).execute()
    if not respuesta.data:
        raise HTTPException(status_code=400, detail="No se pudo registrar el movimiento")
        
    datos_respuesta = respuesta.data[0]
    if "fecha_transaccion" in datos_respuesta:
        datos_respuesta["fecha"] = datos_respuesta["fecha_transaccion"]
        
    return datos_respuesta

# 2. LISTAR TRANSACCIONES (Oculta las anuladas por defecto para mantener limpia tu vista)
@router.get("/", response_model=List[TransaccionResponse])
def listar_transacciones_personales():
    respuesta = supabase.table("transacciones_personales").select("*").eq("estado", "activo").order("fecha_transaccion", desc=True).execute()
    
    lista_convertida = []
    for item in respuesta.data:
        if "fecha_transaccion" in item:
            item["fecha"] = item["fecha_transaccion"]
        lista_convertida.append(item)
        
    return lista_convertida

# 3. EDITAR TRANSACCIÓN PERSONAL (CRUD)
@router.put("/{transaccion_id}", response_model=TransaccionResponse)
def editar_transaccion_personal(transaccion_id: UUID, transaccion: TransaccionCreate):
    id_str = str(transaccion_id)
    
    if transaccion.tipo not in ['ingreso', 'gasto']:
        raise HTTPException(status_code=400, detail="El tipo debe ser 'ingreso' o 'gasto'")
        
    datos_update = transaccion.model_dump()
    
    respuesta = supabase.table("transacciones_personales").update(datos_update).eq("id", id_str).execute()
    if not respuesta.data:
        raise HTTPException(status_code=404, detail="Movimiento financiero no encontrado")
        
    datos_respuesta = respuesta.data[0]
    if "fecha_transaccion" in datos_respuesta:
        datos_respuesta["fecha"] = datos_respuesta["fecha_transaccion"]
        
    return datos_respuesta

# 4. ELIMINAR TRANSACCIÓN PERSONAL (Borrado suave / Anulación)
@router.delete("/{transaccion_id}", response_model=dict)
def eliminar_transaccion_personal(transaccion_id: UUID):
    id_str = str(transaccion_id)
    
    # Cambiamos estado a 'anulado' para proteger el historial financiero histórico
    respuesta = supabase.table("transacciones_personales").update({"estado": "anulado"}).eq("id", id_str).execute()
    if not respuesta.data:
        raise HTTPException(status_code=404, detail="Movimiento financiero no encontrado")
        
    return {"mensaje": "Movimiento eliminado (anulado) correctamente de tus finanzas personales"}