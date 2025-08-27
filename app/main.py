# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routers import files

app = FastAPI(title="DXF Processor API")

# CORS: ajusta tu dominio de Vercel
origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos generados (PNG/PDF)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Rutas de archivos
app.include_router(files.router)

@app.get("/health")
def health():
    return {"status": "ok"}
