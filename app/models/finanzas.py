from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

# Este molde valida el método de pago elegido en tus finanzas personales
class TransaccionCreate(BaseModel):
    tipo: str  # Debe ser estrictamente 'ingreso' o 'gasto'
    monto: float
    categoria: str # Ej: 'Tarjeta de Crédito', 'Cuota Préstamo Personal', 'Comida', etc.
    descripcion: Optional[str] = None
    metodo_pago: str = "cuenta_bancaria" # Opciones: 'cuenta_bancaria', 'efectivo', 'tarjeta_credito'

# Moldes de respuesta incluyendo la metadata de control
class TransaccionResponse(BaseModel):
    id: UUID
    tipo: str
    monto: float
    categoria: str
    descripcion: Optional[str]
    metodo_pago: str
    estado: str # 'activo' o 'anulado'
    fecha: datetime