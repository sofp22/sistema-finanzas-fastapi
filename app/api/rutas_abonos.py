from fastapi import APIRouter, HTTPException
from app.database.conexion import supabase
from app.models.abono import AbonoCreate, AbonoResponse
from uuid import UUID

router = APIRouter(prefix="/abonos", tags=["Abonos"])

@router.post("/", response_model=AbonoResponse)
def registrar_abono(abono: AbonoCreate):
    # 1. Convertimos el ID a string para evitar errores de serialización JSON
    id_prestamo_str = str(abono.prestamo_id)
    
    # 2. Traer el préstamo actual de Supabase para ver cuánto debe
    res_prestamo = supabase.table("prestamos").select("*").eq("id", id_prestamo_str).execute()
    
    if not res_prestamo.data:
        raise HTTPException(status_code=404, detail="El préstamo especificado no existe")
        
    prestamo_actual = res_prestamo.data[0]
    
    # REGLA: No se pueden hacer abonos a préstamos ya pagados
    if prestamo_actual["estado"] == "Pagado":
        raise HTTPException(status_code=400, detail="Este préstamo ya se encuentra completamente Pagado")
        
    saldo_anterior = float(prestamo_actual["saldo_actual"])
    monto_abono = float(abono.monto)
    
    # REGLA: No abonar más de lo que se debe
    if monto_abono > saldo_anterior:
        raise HTTPException(
            status_code=400, 
            detail=f"El abono (${monto_abono}) supera al saldo pendiente (${saldo_anterior})"
        )
        
    # 3. MATEMÁTICA FINANCIERA: Calcular nuevo saldo y estado
    nuevo_saldo = saldo_anterior - monto_abono
    nuevo_estado = "Pagado" if nuevo_saldo == 0 else "Activo"
    
    # 4. ACTUALIZACIÓN: Guardar el nuevo saldo en la tabla 'prestamos'
    supabase.table("prestamos").update({
        "saldo_actual": nuevo_saldo,
        "estado": nuevo_estado
    }).eq("id", id_prestamo_str).execute()
    
    # 5. REGISTRO: Insertar el recibo del abono en la tabla 'abonos'
    datos_abono = abono.model_dump()
    datos_abono["prestamo_id"] = id_prestamo_str # Forzamos string
    
    res_abono = supabase.table("abonos").insert(datos_abono).execute()
    
    if not res_abono.data:
        raise HTTPException(status_code=400, detail="No se pudo procesar el recibo del abono")
        
    return res_abono.data[0]