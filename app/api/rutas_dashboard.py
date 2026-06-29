from fastapi import APIRouter
from app.database.conexion import supabase

router = APIRouter(prefix="/dashboard", tags=["Dashboard General"])

@router.get("/resumen")
def obtener_resumen_financiero_total():
    # --- 1. SECCIÓN EMPRESA (PRÉSTAMOS Y ABONOS) ---
    res_prestamos = supabase.table("prestamos").select("monto_inicial, saldo_actual").execute()
    res_abonos = supabase.table("abonos").select("monto_total").execute()
    
    total_prestado = sum(float(p["monto_inicial"]) for p in res_prestamos.data)
    capital_en_la_calle = sum(float(p["saldo_actual"]) for p in res_prestamos.data)
    total_recaudado_abonos = sum(float(a["monto_total"]) for a in res_abonos.data)
    

    res_personales = supabase.table("transacciones_personales").select("tipo, monto, metodo_pago").eq("estado", "activo").execute()
    
    total_ingresos_personales = 0.0
    total_gastos_personales = 0.0
    
    for mov in res_personales.data:
        if mov["tipo"] == "ingreso":
            total_ingresos_personales += float(mov["monto"])
        elif mov["tipo"] == "gasto":
            if mov.get("metodo_pago") != "tarjeta_credito":
                total_gastos_personales += float(mov["monto"])
            
    balance_personal_libre = total_ingresos_personales - total_gastos_personales

    return {
        "empresa_prestamos": {
            "total_historico_prestado": total_prestado,
            "dinero_actual_en_la_calle": capital_en_la_calle,
            "total_recuperado_por_cobros": total_recaudado_abonos,
            "mensaje_estado": "Este dinero pertenece al flujo del negocio."
        },
        "finanzas_personales": {
            "mis_ingresos_totales": total_ingresos_personales,
            "mis_gastos_totales": total_gastos_personales,
            "mi_dinero_libre_disponible": balance_personal_libre,
            "mensaje_estado": "Este dinero es tuyo, fuera del negocio."
        }
    }