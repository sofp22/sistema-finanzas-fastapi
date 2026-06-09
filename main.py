from fastapi import FastAPI

# Aquí inicializamos tu aplicación
app = FastAPI(
    title="API Finanzas y Préstamos",
    description="Backend para la gestión de liquidez y reglas de negocio"
)

# Este es tu primer "Endpoint" (URL)
@app.get("/")
def verificar_estado():
    return {
        "estado": "Exitoso",
        "mensaje": "¡Hola! Tu backend está encendido y listo para trabajar."
    }