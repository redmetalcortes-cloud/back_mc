# app/routers/files.py
from app.services.dxf_processor import process_dxf_file, generate_dxf_plot
import os
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fpdf import FPDF


STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)

router = APIRouter()

def generate_pdf(file_name: str, result: dict) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # ==== Header ====
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, "EAZY DXF Processor", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "I", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "Reporte de Cotización", ln=True, align="C")
    pdf.ln(10)

    # ==== Card-like box ====
    pdf.set_draw_color(200, 200, 200)  # borde gris claro
    pdf.set_fill_color(245, 245, 245)  # fondo gris claro
    pdf.rect(10, pdf.get_y(), 190, 90, "DF")  # x, y, ancho, alto, Draw+Fill

    pdf.set_xy(15, pdf.get_y() + 5)
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "Resultado de Cotización", ln=True)

    pdf.set_font("Arial", "", 12)

    # Columna izquierda
    x_start = 15
    y_start = pdf.get_y()
    pdf.set_xy(x_start, y_start)
    pdf.multi_cell(90, 8,
        f"Material: {result.get('material','N/A')}\n"
        f"Cantidad: {result.get('cantidad',1)}\n"
        f"Dimensiones: {result['ancho']:.0f} x {result['alto']:.0f} mm\n"
        f"Perímetro: {result['total_perimeter']:.0f} mm"
    )

    # Columna derecha
    x_right = 110
    pdf.set_xy(x_right, y_start)
    pdf.multi_cell(90, 8,
        f"Costo Bruto: {result['costo_bruto']:.0f} COP\n"
        f"Costo Material: {result['costo_material']:.0f} COP\n"
        f"Costo Corte: {result['costo_corte']:.0f} COP\n"
        f"Costo Doblez: {result['costo_doblez']:.0f} COP"
    )

    pdf.ln(5)

    # ==== Precio final destacado ====
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 150, 0)  # verde
    pdf.cell(0, 10, f"Precio Final: {result['precio_final']:.0f} COP", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # ==== Preview ====
    if "preview" in result:
        preview_path = os.path.join("static", result["preview"])
        if os.path.exists(preview_path):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Vista previa de la pieza:", ln=True)
            pdf.image(preview_path, x=25, w=160)  # ancho ajustado

    # Guardar PDF
    out_path = os.path.join("static", f"{file_name}.pdf")
    pdf.output(out_path)
    return out_path

@router.post("/files/upload/")
async def upload_file(file: UploadFile = File(...), material: str = "CR18", cantidad: int = 1):
    file_name = os.path.splitext(file.filename)[0]
    file_path = os.path.join(STATIC_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Procesar DXF
    result = process_dxf_file(file_path, material, cantidad)

    # Añadir referencia al preview
    result["preview"] = f"{file_name}.png"

    # Generar PDF
    generate_pdf(file_name, result)

    return JSONResponse(content=result)


@router.get("/files/download_pdf/{filename}")
async def download_pdf(filename: str):
    pdf_path = os.path.join(STATIC_DIR, f"{filename}.pdf")
    if not os.path.exists(pdf_path):
        return JSONResponse(content={"error": "Archivo no encontrado"}, status_code=404)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"{filename}.pdf")
