from fastapi import APIRouter, HTTPException
from app.database.conexion import supabase
from app.models.prestamo import PrestamoCreate, PrestamoResponse
from typing import List
from uuid import UUID

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])

# 1. Ruta para crear un préstamo nuevo
@router.post("/", response_model=PrestamoResponse)
def crear_prestamo(prestamo: PrestamoCreate):
    datos_prestamo = prestamo.model_dump()
    
    # LÓGICA REGLA DE NEGOCIO: Al crear el préstamo, el saldo actual es igual al monto inicial
    datos_prestamo["cliente_id"] = str(datos_prestamo["cliente_id"])
    datos_prestamo["saldo_actual"] = float(prestamo.monto_inicial)
    datos_prestamo["estado"] = "Activo"
    
    
    respuesta = supabase.table("prestamos").insert(datos_prestamo).execute()
    
    if not respuesta.data:
        raise HTTPException(status_code=400, detail="No se pudo registrar el préstamo. Verifica que el cliente_id sea correcto.")
        
    return respuesta.data[0]

# 2. Ruta para ver todos los préstamos activos de un cliente específico
@router.get("/cliente/{cliente_id}", response_model=List[PrestamoResponse])
def listar_prestamos_por_cliente(cliente_id: UUID):
    respuesta = supabase.table("prestamos")\
        .select("*")\
        .eq("cliente_id", str(cliente_id))\
        .execute()
        
    return respuesta.data