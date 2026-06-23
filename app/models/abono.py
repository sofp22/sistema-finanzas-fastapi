from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

# Molde para recibir un pago dividiendo capital de interés desde Flutter
class AbonoCreate(BaseModel):
    prestamo_id: UUID
    monto_capital: float
    monto_interes: float

# Molde para responderle a Flutter con el recibo detallado
class AbonoResponse(BaseModel):
    id: UUID
    prestamo_id: UUID
    monto_total: float
    monto_capital: float
    monto_interes: float
    estado: str  # Guardará 'valido' o 'anulado'
    fecha_abono: datetime