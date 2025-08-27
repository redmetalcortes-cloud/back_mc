# app/routers/files.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from app.services.dxf_processor import process_dxf_file, generate_dxf_plot
from app.schemas import DXFProcessResponse
import os
from fpdf import FPDF

router = APIRouter(prefix="/files", tags=["files"])

STATIC_DIR = "app/static"
os.makedirs(STATIC_DIR, exist_ok=True)


@router.get("/download_pdf/{file_name}")
async def download_pdf(file_name: str):
    file_path = os.path.join(STATIC_DIR, f"{file_name}.pdf")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path, media_type="application/pdf", filename=f"{file_name}.pdf")


@router.post("/upload/", response_model=DXFProcessResponse)
async def upload_file(
    file: UploadFile = File(...),
    material: str = Form(...),
    cantidad: int = Form(...)
):
    if not file.filename.lower().endswith(".dxf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un DXF")

    # Guardar DXF en static
    dxf_path = os.path.join(STATIC_DIR, file.filename)
    with open(dxf_path, "wb") as f:
        f.write(await file.read())

    # Generar preview PNG
    base_name = os.path.splitext(file.filename)[0]
    preview_png_name = f"{base_name}.png"
    preview_png_path = os.path.join(STATIC_DIR, preview_png_name)
    generate_dxf_plot(dxf_path, preview_png_path)

    # Procesar costos/medidas
    result = process_dxf_file(dxf_path, material, cantidad)
    if result.get("status") == "failed":
        raise HTTPException(status_code=422, detail=f"Error: {result.get('error')}")

    # Generar PDF
    pdf_path = generate_pdf(base_name, result)

    print("=== RESULT DXF FILE ===")
    print(result)

    # Mapear al esquema de salida
    resp = DXFProcessResponse(
        status="success",
        material=material,
        cantidad=int(cantidad),
        ancho=float(result["ancho"]),
        alto=float(result["alto"]),
        total_perimeter=float(result["total_perimeter"]),
        total_entities=int(result["total_entities"]),
        precio_unitario_sin_descuento=float(result["precio_unitario_sin_descuento"]),
        precio_unitario_con_descuento=float(result["precio_unitario_con_descuento"]),
        descuento_porcentaje=int(result["descuento_porcentaje"]),
        descuento_valor=float(result["descuento_valor"]),
        precio_final=float(result["precio_final"]),
        costo_bruto=float(result["costo_bruto"]),
        costo_material=float(result["costo_material"]),
        costo_corte=float(result["costo_corte"]),
        costo_doblez=float(result["costo_doblez"]),
        costo_transporte=float(result["costo_transporte"]),
        costo_almacenamiento=float(result["costo_almacenamiento"]),
        alistamiento=float(result["alistamiento"]),
        costo_desperdicio=float(result["costo_desperdicio"]),
        preview_png_url=f"/static/{preview_png_name}",
        pdf_url=f"/files/download_pdf/{base_name}"
    )

    return resp


def generate_pdf(file_name: str, result: dict) -> str:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Resumen de Procesamiento - {file_name}", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Entidades: {int(result['total_entities'])}", ln=True)
    pdf.cell(200, 10, f"Dimensiones: {result['ancho']:.0f} x {result['alto']:.0f} mm", ln=True)
    pdf.cell(200, 10, f"Perímetro total: {result['total_perimeter']:.0f} mm", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Costos detallados:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Costo de corte: {result['costo_corte']:.0f} COP", ln=True)
    pdf.cell(200, 10, f"Costo de material: {result['costo_material']:.0f} COP", ln=True)
    pdf.cell(200, 10, f"Costo desperdicio: {result['costo_desperdicio']:.0f} COP", ln=True)
    pdf.cell(200, 10, f"Costo de transporte: {result['costo_transporte']:.0f} COP", ln=True)
    pdf.cell(200, 10, f"Costo de almacenaje: {result['costo_almacenamiento']:.0f} COP", ln=True)
    pdf.cell(200, 10, f"Costo de alistamiento: {result['alistamiento']:.0f} COP", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, f"Costo bruto: {result['costo_bruto']:.0f} COP", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, f"Descuento aplicado: {result['descuento_porcentaje']}% (-{result['descuento_valor']:.2f} COP)", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, f"Precio Final: {result['precio_final']:.2f} COP", ln=True)

    out_path = os.path.join(STATIC_DIR, f"{file_name}.pdf")
    pdf.output(out_path)
    return out_path
