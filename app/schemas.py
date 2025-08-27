# app/schemas.py
from pydantic import BaseModel
from typing import Optional

class DXFProcessResponse(BaseModel):
    status: str
    material: str
    cantidad: int
    ancho: float
    alto: float
    total_perimeter: float
    total_entities: int
    precio_unitario_sin_descuento: float
    precio_unitario_con_descuento: float
    descuento_porcentaje: int
    descuento_valor: float
    precio_final: float
    costo_bruto: float
    costo_material: float
    costo_corte: float
    costo_doblez: float
    costo_transporte: float
    costo_almacenamiento: float
    alistamiento: float
    costo_desperdicio: float
    preview_png_url: Optional[str] = None
    pdf_url: Optional[str] = None
