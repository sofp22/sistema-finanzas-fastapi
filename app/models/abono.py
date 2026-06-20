from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

# Molde para recibir un pago desde el celular
class AbonoCreate(BaseModel):
    prestamo_id: UUID
    monto: float

# Molde para responderle al celular con el recibo del pago
class AbonoResponse(BaseModel):
    id: UUID
    prestamo_id: UUID
    monto: float
    fecha_abono: datetime