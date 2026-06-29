from fastapi import APIRouter, HTTPException
from app.database.conexion import supabase
from app.models.abono import AbonoCreate, AbonoResponse
from uuid import UUID
from typing import List
from datetime import datetime

router = APIRouter(prefix="/abonos", tags=["Abonos"])

# 1. REGISTRAR ABONO (CON EFECTO CASCADA PARA LOS INTERESES)
@router.post("/", response_model=AbonoResponse)
def registrar_abono(abono: AbonoCreate):
    id_prestamo_str = str(abono.prestamo_id)
    
    # Validar que el préstamo exista y extraer el cliente_id
    res_prestamo = supabase.table("prestamos").select("*").eq("id", id_prestamo_str).execute()
    if not res_prestamo.data:
        raise HTTPException(status_code=404, detail="El préstamo especificado no existe")
        
    prestamo_actual = res_prestamo.data[0]
    cliente_id = prestamo_actual["cliente_id"]
    
    if prestamo_actual["estado"] == "Pagado":
        raise HTTPException(status_code=400, detail="Este préstamo ya se encuentra completamente Pagado")
        
    saldo_anterior = float(prestamo_actual["saldo_actual"])
    
    if abono.monto_capital > saldo_anterior:
        raise HTTPException(
            status_code=400, 
            detail=f"El abono a capital (${abono.monto_capital}) supera al saldo pendiente (${saldo_anterior})"
        )
        
    # Matemática: Solo el capital resta la deuda
    nuevo_saldo = max(0.0, saldo_anterior - abono.monto_capital)
    nuevo_estado = "Pagado" if nuevo_saldo == 0 else "Activo"
    activo_flag = False if nuevo_saldo == 0 else True
    
    # Actualizar Préstamo
    supabase.table("prestamos").update({
        "saldo_actual": nuevo_saldo,
        "estado": nuevo_estado,
        "activo": activo_flag
    }).eq("id", id_prestamo_str).execute()
    
    # Guardar Abono Detallado
    monto_total = abono.monto_capital + abono.monto_interes
    datos_abono = {
        "prestamo_id": id_prestamo_str,
        "monto_total": monto_total,
        "monto_capital": abono.monto_capital,
        "monto_interes": abono.monto_interes,
        "estado": "valido"
    }
    
    res_abono = supabase.table("abonos").insert(datos_abono).execute()
    if not res_abono.data:
        raise HTTPException(status_code=400, detail="No se pudo procesar el recibo del abono")

    # Inicializar o recuperar cuenta de ahorros del cliente
    res_ahorro = supabase.table("ahorros").select("*").eq("cliente_id", cliente_id).execute()
    if not res_ahorro.data:
        res_nueva_cuenta = supabase.table("ahorros").insert({"cliente_id": cliente_id, "saldo_ahorro": 0.0}).execute()
        cuenta_ahorro = res_nueva_cuenta.data[0]
    else:
        cuenta_ahorro = res_ahorro.data[0]
        
    total_a_ahorrar = 0.0
    
    # REGLA 1: El 15% de lo pagado a capital se destina a la bolsa de ahorros
    if abono.monto_capital > 0:
        monto_15_capital = abono.monto_capital * 0.15
        total_a_ahorrar += monto_15_capital
        supabase.table("movimientos_ahorro").insert({
            "ahorro_id": cuenta_ahorro["id"],
            "tipo": "15_Capital",
            "monto": monto_15_capital
        }).execute()

    # REGLA 2: DISTRIBUCIÓN EN CASCADA DEL INTERÉS
    if abono.monto_interes > 0:
        interes_disponible = abono.monto_interes
        mes_actual = datetime.now().month
        
        # Obtener todas las metas/obligaciones mensuales de la base de datos
        res_obligaciones = supabase.table("obligaciones_mensuales").select("*").execute()
        obligaciones = res_obligaciones.data if res_obligaciones.data else []
        
        # Paso A: Control de ciclo de meses (Resetear si cambió el mes en el calendario)
        for ob in obligaciones:
            if ob["ultimo_mes_pago"] != mes_actual:
                ob["monto_pagado_mes"] = 0.0
                supabase.table("obligaciones_mensuales").update({
                    "monto_pagado_mes": 0.0, 
                    "ultimo_mes_pago": mes_actual
                }).eq("id", ob["id"]).execute()
        
        # Paso B: Efecto derrame en cascada para obligaciones incompletas
        for ob in obligaciones:
            if interes_disponible <= 0:
                break  # Si nos quedamos sin interés, detenemos la distribución
                
            meta = float(ob["monto_meta"])
            pagado_actual = float(ob["monto_pagado_mes"])
            falta_por_pagar = max(0.0, meta - pagado_actual)
            
            # Si a esta obligación le falta dinero para llegar al 100%, la apoyamos
            if falta_por_pagar > 0:
                abono_a_obligacion = min(interes_disponible, falta_por_pagar)
                interes_disponible -= abono_a_obligacion
                nuevo_pago_acumulado = pagado_actual + abono_a_obligacion
                
                # Actualizamos el progreso de esta meta específica en Supabase
                supabase.table("obligaciones_mensuales").update({
                    "monto_pagado_mes": nuevo_pago_acumulado
                }).eq("id", ob["id"]).execute()
                
        # Paso C: Si TODAS las obligaciones ya están llenas (100%) y sobró dinero, va a ahorros
        if interes_disponible > 0:
            total_a_ahorrar += interes_disponible
            supabase.table("movimientos_ahorro").insert({
                "ahorro_id": cuenta_ahorro["id"],
                "tipo": "Excedente_Interes",
                "monto": interes_disponible
            }).execute()

    # Consolidar saldo definitivo en la cuenta de ahorros si hubo movimientos (Regla 1 o Regla 2)
    if total_a_ahorrar > 0:
        nuevo_saldo_ahorro = float(cuenta_ahorro["saldo_ahorro"]) + total_a_ahorrar
        supabase.table("ahorros").update({"saldo_ahorro": nuevo_saldo_ahorro}).eq("id", cuenta_ahorro["id"]).execute()
    
    return res_abono.data[0]


# 2. ELIMINAR / ANULAR ABONO (Devuelve el dinero a la deuda automáticamente)
@router.delete("/{abono_id}", response_model=dict)
def anular_abono(abono_id: UUID):
    id_abono_str = str(abono_id)
    
    res_abono = supabase.table("abonos").select("*").eq("id", id_abono_str).execute()
    if not res_abono.data:
        raise HTTPException(status_code=404, detail="El abono no existe")
        
    abono_actual = res_abono.data[0]
    if abono_actual["estado"] == "anulado":
        raise HTTPException(status_code=400, detail="Este abono ya se encontraba anulado")
        
    id_prestamo_str = str(abono_actual["prestamo_id"])
    capital_a_revertir = float(abono_actual["monto_capital"])
    
    # Recuperar el préstamo para sumarle la deuda cancelada por error
    res_prestamo = supabase.table("prestamos").select("*").eq("id", id_prestamo_str).execute()
    if not res_prestamo.data:
        raise HTTPException(status_code=404, detail="El préstamo asociado ya no existe")
        
    prestamo_actual = res_prestamo.data[0]
    nuevo_saldo = float(prestamo_actual["saldo_actual"]) + capital_a_revertir
    
    # Regresa el préstamo a estado Activo
    supabase.table("prestamos").update({
        "saldo_actual": nuevo_saldo,
        "estado": "Activo",
        "activo": True
    }).eq("id", id_prestamo_str).execute()
    
    # Cambiar estado del abono a anulado
    supabase.table("abonos").update({"estado": "anulado"}).eq("id", id_abono_str).execute()
    
    return {"mensaje": "Abono anulado con éxito. La deuda del cliente ha sido restaurada."}


# 3. EDITAR ABONO (Corrige montos mal digitados y recalcula la deuda limpia)
@router.put("/{abono_id}", response_model=AbonoResponse)
def editar_abono(abono_id: UUID, nuevo_abono: AbonoCreate):
    id_abono_str = str(abono_id)
    
    res_abono = supabase.table("abonos").select("*").eq("id", id_abono_str).execute()
    if not res_abono.data:
        raise HTTPException(status_code=404, detail="El abono no existe")
        
    abono_viejo = res_abono.data[0]
    if abono_viejo["estado"] == "anulado":
        raise HTTPException(status_code=400, detail="No se puede editar un abono anulado")
        
    id_prestamo_str = str(abono_viejo["prestamo_id"])
    capital_viejo = float(abono_viejo["monto_capital"])
    
    res_prestamo = supabase.table("prestamos").select("*").eq("id", id_prestamo_str).execute()
    if not res_prestamo.data:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        
    prestamo = res_prestamo.data[0]
    
    # Reversión virtual del capital viejo para conocer el saldo base real
    saldo_base = float(prestamo["saldo_actual"]) + capital_viejo
    
    if nuevo_abono.monto_capital > saldo_base:
        raise HTTPException(status_code=400, detail="El nuevo capital ingresado supera el saldo de la deuda")
        
    # Nuevo cálculo
    nuevo_saldo = max(0.0, saldo_base - nuevo_abono.monto_capital)
    nuevo_estado = "Pagado" if nuevo_saldo == 0 else "Activo"
    activo_flag = False if nuevo_saldo == 0 else True
    
    # Guardar cambios en préstamo
    supabase.table("prestamos").update({
        "saldo_actual": nuevo_saldo,
        "estado": nuevo_estado,
        "activo": activo_flag
    }).eq("id", id_prestamo_str).execute()
    
    # Modificar el recibo del abono
    monto_total = nuevo_abono.monto_capital + nuevo_abono.monto_interes
    res_update = supabase.table("abonos").update({
        "monto_total": monto_total,
        "monto_capital": nuevo_abono.monto_capital,
        "monto_interes": nuevo_abono.monto_interes
    }).eq("id", id_abono_str).execute()
    
    return res_update.data[0]


# 4. OBTENER HISTORIAL DE ABONOS DE UN PRÉSTAMO
@router.get("/prestamo/{prestamo_id}", response_model=List[AbonoResponse])
def obtener_abonos_por_prestamo(prestamo_id: UUID):
    respuesta = supabase.table("abonos").select("*").eq("prestamo_id", str(prestamo_id)).execute()
    return respuesta.data