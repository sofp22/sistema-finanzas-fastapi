from fastapi import FastAPI
from app.database.conexion import supabase
from fastapi.middleware.cors import CORSMiddleware
from app.api.rutas_clientes import router as clientes_router
from app.api.rutas_prestamos import router as prestamos_router
from app.api.rutas_abonos import router as abonos_router
from app.api.rutas_finanzas import router as finanzas_router
from app.api.rutas_dashboard import router as dashboard_router

app = FastAPI(
    title="API Finanzas y Préstamos",
    description="Backend para la gestión de liquidez y reglas de negocio"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Registramos los dos grupos de rutas
app.include_router(clientes_router)
app.include_router(prestamos_router) # 2. Registramos préstamos
app.include_router(abonos_router) # 3. Registramos abonos
app.include_router(finanzas_router)   # 2. Activamos finanzas personales
app.include_router(dashboard_router)

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