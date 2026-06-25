from fastapi import APIRouter, HTTPException
from app.database.conexion import supabase
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/balance", tags=["Balance Administrador"])

class ObligacionCreate(BaseModel):
    concepto: str
    monto_meta: float
    
@router.get("/resumen")
def obtener_resumen_panel_privado():
    try:
        mes_actual = datetime.now().month
        
        # 1. Traer tus obligaciones fijas mensuales
        res_obligaciones = supabase.table("obligaciones_mensuales").select("*").execute()
        obligaciones = res_obligaciones.data if res_obligaciones.data else []
        
        # Formatear y verificar si cambió el mes en alguna obligación por si acaso
        for ob in obligaciones:
            if ob["ultimo_mes_pago"] != mes_actual:
                ob["monto_pagado_mes"] = 0.0
                # Sincronizamos en la base de datos si detectamos cambio de mes al consultar
                supabase.table("obligaciones_mensuales").update({
                    "monto_pagado_mes": 0.0, 
                    "ultimo_mes_pago": mes_actual
                }).eq("id", ob["id"]).execute()

        # 2. Calcular cuánto tienes en ahorro total sumando todas las bolsas de ahorro
        res_ahorros = supabase.table("ahorros").select("saldo_ahorro").execute()
        ahorro_total = sum(float(fila["saldo_ahorro"]) for fila in res_ahorros.data) if res_ahorros.data else 0.0
        
        # 3. Traer los últimos movimientos globales de tu dinero para el historial privado
        res_movimientos = supabase.table("movimientos_ahorro").select("*").order("fecha", desc=True).limit(20).execute()
        historial_movimientos = res_movimientos.data if res_movimientos.data else []
        
        return {
            "ahorro_total": ahorro_total,
            "obligaciones": obligaciones,
            "historial_fondos": historial_movimientos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular el balance: {str(e)}")
    
    # ENDPOINT NUEVO: Guardar una nueva obligación fija desde la App
@router.post("/obligaciones")
def crear_obligacion_mensual(obligacion: ObligacionCreate):
    try:
        mes_actual = datetime.now().month
        
        datos = {
            "concepto": obligacion.concepto,
            "monto_meta": obligacion.monto_meta,
            "monto_pagado_mes": 0.0,
            "ultimo_mes_pago": mes_actual
        }
        
        resultado = supabase.table("obligaciones_mensuales").insert(datos).execute()
        if not resultado.data:
            raise HTTPException(status_code=400, detail="No se pudo registrar la obligación")
            
        return {"mensaje": "Obligación registrada con éxito", "data": resultado.data[0]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))