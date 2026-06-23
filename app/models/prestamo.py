from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

# Molde para cuando nos pidan crear un préstamo desde el celular
class PrestamoCreate(BaseModel):
    cliente_id: UUID
    monto_inicial: float
    tasa_interes: float  # Ej: 0.05 para un 5%

# Molde para cuando le respondamos al celular con los datos guardados
class PrestamoResponse(BaseModel):
    id: UUID
    cliente_id: UUID
    monto_inicial: float
    saldo_actual: float  
    tasa_interes: float
    estado: str
    fecha_creacion: datetime