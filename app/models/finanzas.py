from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

# Este molde valida lo que envías desde el celular al registrar un gasto/ingreso
class TransaccionCreate(BaseModel):
    tipo: str  # Debe ser estrictamente 'ingreso' o 'gasto'
    monto: float
    categoria: str # Ej: 'Arriendo', 'Comida', 'Salario'
    descripcion: Optional[str] = None

# Este molde define cómo te responde el backend con los datos ya guardados
class TransaccionResponse(BaseModel):
    id: UUID
    tipo: str
    monto: float
    categoria: str
    descripcion: Optional[str]
    fecha: datetime