from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.prestamo import PrestamoResponse

class ClienteCreate(BaseModel):
    cedula: str
    nombre: str
    telefono: Optional[str] = None
    nivel_confianza: Optional[int] = 3

class ClienteResponse(BaseModel):
    id: UUID
    cedula: str
    nombre: str
    telefono: Optional[str]
    nivel_confianza: int
    fecha_registro: datetime

# une al cliente con todo su historial financiero
class PerfilClienteResponse(BaseModel):
    cliente: ClienteResponse
    prestamos: List[PrestamoResponse]
    resumen_financiero: dict  # Aquí calcularemos en tiempo real si está a paz y salvo, cuánto debe en total, etc.