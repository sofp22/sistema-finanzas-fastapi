from fastapi import APIRouter, HTTPException
from app.database.conexion import supabase
from app.models.cliente import ClienteCreate, ClienteResponse
from typing import List
from app.models.cliente import ClienteCreate, ClienteResponse, PerfilClienteResponse


router = APIRouter(prefix="/clientes", tags=["Clientes"])

# Crear un cliente
@router.post("/", response_model=ClienteResponse)
def crear_cliente(cliente: ClienteCreate):
    datos_cliente = cliente.model_dump()
    # Usamos "clientes" en minúscula para que Supabase lo entienda
    respuesta = supabase.table("clientes").insert(datos_cliente).execute()
    
    if not respuesta.data:
        raise HTTPException(status_code=400, detail="No se pudo registrar el cliente")
        
    return respuesta.data[0]

#  Ver todos los clientes
@router.get("/", response_model=List[ClienteResponse])
def listar_clientes():
    # Usamos "clientes" en minúscula
    respuesta = supabase.table("clientes").select("*").order("nombre").execute()
    return respuesta.data

#  Buscar un cliente específico por su número de cédula
@router.get("/buscar/{cedula}", response_model=ClienteResponse)
def obtener_cliente_por_cedula(cedula: str):
    # Le decimos a Supabase: "Filtra en la tabla clientes donde la columna cedula sea igual (eq) al parámetro"
    respuesta = supabase.table("clientes").select("*").eq("cedula", cedula).execute()
    
    # Si la lista regresa vacía, significa que esa cédula no existe en el sistema
    if not respuesta.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado con esa cédula")
        
    return respuesta.data[0]

# Obtener la hoja de vida financiera completa del cliente por cédula
@router.get("/perfil-completo/{cedula}", response_model=PerfilClienteResponse)
def obtener_perfil_completo_cliente(cedula: str):
    # 1. Buscamos primero al cliente
    res_cliente = supabase.table("clientes").select("*").eq("cedula", cedula).execute()
    if not res_cliente.data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    cliente_datos = res_cliente.data[0]
    cliente_id = cliente_datos["id"]
    
    # 2. Buscamos todos sus préstamos
    res_prestamos = supabase.table("prestamos").select("*").eq("cliente_id", cliente_id).execute()
    lista_prestamos = res_prestamos.data
    
    # 3. LÓGICA DE NEGOCIO: Calculamos su estado financiero en tiempo real
    total_deuda = 0.0
    tiene_deudas_activas = False
    
    for prestamo in lista_prestamos:
        if prestamo["estado"] == "Activo":
            total_deuda += float(prestamo["saldo_actual"])
            tiene_deudas_activas = True
            
    # Determinamos su situación de pago (Paz y Salvo o Con Deuda)
    estado_paz_y_salvo = "SÍ" if total_deuda == 0 and len(lista_prestamos) > 0 else "NO"
    if len(lista_prestamos) == 0:
        estado_paz_y_salvo = "Sin préstamos registrados"

    # 4. Armamos el paquete definitivo para el Frontend
    return {
        "cliente": cliente_datos,
        "prestamos": lista_prestamos,
        "resumen_financiero": {
            "total_prestamos_solicitados": len(lista_prestamos),
            "saldo_pendiente_total": total_deuda,
            "esta_paz_y_salvo": estado_paz_y_salvo,
            "puede_solicitar_nuevo_prestamo": not tiene_deudas_activas 
        }
    }