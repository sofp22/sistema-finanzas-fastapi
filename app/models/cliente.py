from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

# Molde para los datos que recibimos desde el celular
class ClienteCreate(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    nivel_confianza: Optional[int] = 3

# Molde para los datos que le respondemos al celular
class ClienteResponse(BaseModel):
    id: UUID
    nombre: str
    telefono: Optional[str]
    nivel_confianza: int
    fecha_registro: datetime