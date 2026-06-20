from fastapi import FastAPI
from app.database.conexion import supabase
from app.api.rutas_clientes import router as clientes_router
# 1. Importamos las nuevas rutas de préstamos
from app.api.rutas_prestamos import router as prestamos_router

app = FastAPI(
    title="API Finanzas y Préstamos",
    description="Backend para la gestión de liquidez y reglas de negocio"
)

# Registramos los dos grupos de rutas
app.include_router(clientes_router)
app.include_router(prestamos_router) # 2. Registramos préstamos

@app.get("/")
def verificar_estado():
    return {
        "estado": "Exitoso",
        "mensaje": "¡Hola! Tu backend está encendido y listo para trabajar."
    }

@app.get("/probar-conexion")
def probar_conexion_supabase():
    try:
        respuesta = supabase.table("configuracion_app").select("*").execute()
        return {
            "estado_conexion": "Exitosa 🚀",
            "datos_recuperados": respuesta.data
        }
    except Exception as error:
        return {"estado_conexion": "Fallida ❌", "detalles_error": str(error)}