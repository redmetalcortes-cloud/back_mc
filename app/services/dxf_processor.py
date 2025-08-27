import ezdxf
import math
import matplotlib
matplotlib.use("Agg")  # Headless backend for Render
from matplotlib import pyplot as plt
from matplotlib.patches import Arc, Circle
import os
from rectpack import newPacker
import random
import matplotlib.patches as patches
import numpy as np


def generate_dxf_plot(file_path, output_image_path):
    try:
        # Leer el archivo DXF
        doc = ezdxf.readfile(file_path)
        modelspace = doc.modelspace()

        # Crear la figura
        fig, ax = plt.subplots(figsize=(5, 5))

        # Copiar entidades en una lista para evitar problemas de iteración
        entities = list(modelspace)

        # Graficar entidades del DXF
        for entity in entities:
            if entity.dxftype() == "LINE":
                start = entity.dxf.start
                end = entity.dxf.end
                ax.plot([start.x, end.x], [start.y, end.y], color="blue", linewidth=1)
            elif entity.dxftype() == "CIRCLE":
                center = entity.dxf.center
                radius = entity.dxf.radius
                circle = Circle((center.x, center.y), radius, edgecolor="green", fill=False)
                ax.add_patch(circle)
            elif entity.dxftype() == "ARC":
                center = entity.dxf.center
                radius = entity.dxf.radius
                start_angle = entity.dxf.start_angle
                end_angle = entity.dxf.end_angle
                arc = Arc((center.x, center.y), 2*radius, 2*radius, angle=0,
                          theta1=start_angle, theta2=end_angle, edgecolor="orange", linewidth=1)
                ax.add_patch(arc)

            elif entity.dxftype() in ["LWPOLYLINE", "POLYLINE"]:
                segments = entity.explode()
                for segment in segments:
                    if segment.dxftype() == 'LINE':
                        start = segment.dxf.start
                        end = segment.dxf.end
                        ax.plot([start.x, end.x], [start.y, end.y], color="red", linewidth=1)

        # Ajustar los límites del gráfico
        ax.set_aspect('equal', adjustable='datalim')
        ax.autoscale_view()

        # Título y etiquetas
        file_name = os.path.basename(file_path)
        ax.set_title(f"Visualización del archivo {file_name}")

        # Guardar la imagen en la ruta especificada
        plt.savefig(output_image_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return output_image_path
    except Exception as e:
        raise RuntimeError(f"Error al procesar el archivo DXF: {e}")


Metro_perimetro_corte = {
    "CR18": 1000, 
    "CR16": 1500, 
    "CR14": 2500, 
    "HR14": 3000,
    "HR12": 3500, 
    "HR1/8": 4500, 
    "HR3/16": 7500, 
    "HR1/4": 12000,
    "HR5/16": 16000, 
    "HR3/8": 20000, 
    "HR1/2": 25000, 
    "INOX20": 4000,
    "INOX18": 5000, 
    "INOX16": 6000, 
    "INOX14": 8000, 
    "INOX12": 10000, 
    "INOX1/8": 12000, 
    "INOX3/16": 16000,
    "ALUM1": 2000, 
    "ALUM1,5": 2500, 
    "ALUM2,5": 3500,
    "ALUM3": 4000, 
    "ALUM4": 5000, 
    "ALUM5": 7000, 
    "ALUM6": 9000,
    "ACR1": 1000,
    "ACR2": 2000,
    "ACR3": 3000,
    "ACR4": 4000,
    "ACR5": 5000,
    "ACR6": 6000,
    "MDF1": 1000,
    "MDF2": 2000,
    "MDF3": 3000,
    "MDF4": 4000,
    "MDF5": 5000,
    "MDF6": 6000,
    "CARTON1": 1000
}

Valor_lamina_m2 = {
    "CR18": 98500, 
    "CR16": 108500,
    "CR14": 128500, 
    "HR14": 125000,
    "HR12": 145000, 
    "HR1/8": 165000, 
    "HR3/16": 185000, 
    "HR1/4": 205000,
    "HR5/16": 225000, 
    "HR3/8": 245000, 
    "HR1/2": 265000, 
    "INOX20": 300000,
    "INOX18": 350000, 
    "INOX16": 400000, 
    "INOX14": 450000, 
    "INOX12": 500000, 
    "INOX1/8": 600000, 
    "INOX3/16": 700000,
    "ALUM1": 90000,
    "ALUM1,5": 105000,
    "ALUM2,5": 125000,
    "ALUM3": 135000,
    "ALUM4": 160000,
    "ALUM5": 200000, 
    "ALUM6": 250000,
    "ACR1": 50000,
    "ACR2": 60000,
    "ACR3": 70000,
    "ACR4": 80000,
    "ACR5": 90000, 
    "ACR6": 100000,
    "MDF1": 40000,
    "MDF2": 50000,
    "MDF3": 60000,
    "MDF4": 70000,
    "MDF5": 80000,
    "MDF6": 90000,
    "CARTON1": 30000
}

Valor_pliegue_ml = {
    "CR18": 4000,
    "CR16": 4500,
    "CR14": 5000,  # Ejemplo de costo por metro lineal para CR
    "HR14": 6000,  # Ejemplo de costo por metro lineal para HR
    "HR12": 6500,
    "HR1/8": 7000,
    "HR3/16": 8000,
    "HR1/4": 9000,
    "HR5/16": 10000,
    "HR3/8": 11000,
    "HR1/2": 12000,
    "INOX20": 6000,
    "INOX18": 6500,
    "INOX16": 7000,
    "INOX14": 7500,
    "INOX12": 8000,
    "INOX1/8": 9000,
    "INOX3/16": 10000,
    "ALUM1": 3000, 
    "ALUM1,5": 3500, 
    "ALUM2,5": 4000,
    "ALUM3": 4500, 
    "ALUM4": 5000, 
    "ALUM5": 5500, 
    "ALUM6": 6000,
    "ACR1": 1500,
    "ACR2": 2000,
    "ACR3": 2500,
    "ACR4": 3000,
    "ACR5": 3500,
    "ACR6": 4000,
    "MDF1": 1500,
    "MDF2": 2000,
    "MDF3": 2500,
    "MDF4": 3000,
    "MDF5": 3500,
    "MDF6": 4000,
    "CARTON1": 1000
}


def calcular_descuento(cantidad):
    """
    Retorna el porcentaje de descuento según la cantidad de piezas.
    """
    if cantidad >= 500:
        return 40  # 40% de descuento
    elif cantidad >= 250:
        return 30  # 30% de descuento
    elif cantidad >= 100:
        return 25  # 25% de descuento
    elif cantidad >= 50:
        return 20  # 20% de descuento
    elif cantidad >= 10:
        return 15  # 15% de descuento
    elif cantidad >= 5:
        return 10  # 10% de descuento
    elif cantidad >= 2:
        return 5  # 5% de descuento

    else:
        return 0  # Sin descuento para menos de 1 pieza


def process_dxf_file(file_path, material, cantidad):
    try:
        # Validar material
        if material not in Metro_perimetro_corte or material not in Valor_lamina_m2:
            raise ValueError(f"Material '{material}' no encontrado.")

        # Leer el archivo DXF
        doc = ezdxf.readfile(file_path)
        modelspace = doc.modelspace()

        total_perimeter = 0.0
        largest_area = 0.0
        costo_lineas = 0.0  # Costo acumulado de las líneas
        total_entities = 0
        ancho, alto = 0, 0  # Definir valores predeterminados

        # Recorrer entidades
        for entity in modelspace:
            total_entities += 1
            if entity.dxftype() == "LINE":
                start = entity.dxf.start
                end = entity.dxf.end
                total_perimeter += math.dist((start.x, start.y), (end.x, end.y))
                # Costo por pliegue/metro lineal estimado
                costo_lineas += Valor_pliegue_ml.get(material, 0) * (math.dist((start.x, start.y), (end.x, end.y))/1000.0)

            elif entity.dxftype() == "CIRCLE":
                radius = entity.dxf.radius
                total_perimeter += 2 * math.pi * radius

            elif entity.dxftype() == "ARC":
                radius = entity.dxf.radius
                start_angle = math.radians(entity.dxf.start_angle)
                end_angle = math.radians(entity.dxf.end_angle)
                angle_diff = (end_angle - start_angle) % (2 * math.pi)
                total_perimeter += radius * angle_diff

            elif entity.dxftype() in ["LWPOLYLINE", "POLYLINE"]:
                # Perímetro aproximado (suma de segmentos)
                try:
                    points = np.array([ (p[0], p[1]) for p in entity.get_points() ])
                    segs = np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1)).sum()
                    # cerrar si es cerrada
                    if entity.closed:
                        segs += math.dist(tuple(points[-1]), tuple(points[0]))
                    total_perimeter += segs
                    costo_lineas += Valor_pliegue_ml.get(material, 0) * (segs/1000.0)
                except Exception:
                    pass

        # Área y bounding box (mayor entidad cerrada)
        area_bounds = calculate_area_and_bounds(modelspace)
        if area_bounds:
            largest_area = area_bounds["area"]
            bounds = area_bounds["bounds"]
            ancho = abs(bounds["max_x"] - bounds["min_x"])
            alto = abs(bounds["max_y"] - bounds["min_y"])

        # Costos base (Colombia)
        # Perímetro en metros (DXF suele estar en mm; ajustar según tu origen)
        perimetro_m = total_perimeter / 1000.0
        costo_corte = Metro_perimetro_corte[material] * perimetro_m

        # Costo de material (área m2 a partir de ancho x alto, en mm -> m)
        area_m2 = (ancho/1000.0) * (alto/1000.0)
        costo_material = Valor_lamina_m2[material] * max(area_m2, 0.0001)  # piso mínimo

        # Gastos adicionales (heurísticos)
        desperdicio_porcentaje = calcular_desperdicio(ancho, alto)  # porcentaje
        desperdicio_mat = costo_material * (desperdicio_porcentaje/100.0)
        transporte_mat = costo_material * 0.05
        almacenaje_mat = costo_material * 0.03
        alistamiento = 15000

        costo_bruto = (
            costo_corte
            + costo_material
            + costo_lineas
            + desperdicio_mat
            + transporte_mat
            + almacenaje_mat
            + alistamiento
        )

        # Utilidad variable
        utilidad = calcular_utilidad(costo_bruto)
        precio_total = costo_bruto * utilidad  # sin IVA

        # IVA 19% (CO)
        precio_total *= 1.19

        print(f"Entidades procesadas: {total_entities}")
        print(f"Perímetro total: {round(total_perimeter)} mm")
        print(f"Utilidad aplicada: {utilidad}")
        print(f"Costo de corte: {round(costo_corte):,} COP")
        print(f"Costo doblez: {round(costo_lineas):,} COP")
        print(f"Costo de material: {round(costo_material):,} COP")
        print(f"Costo desperdicio: {round(desperdicio_mat):,} COP")
        print(f"Costo de transporte: {round(transporte_mat):,} COP")
        print(f"Costo de almacenaje: {round(almacenaje_mat):,} COP")
        print(f"Costo de alistamiento: {round(alistamiento):,} COP")
        print(f"Costo bruto: {round(costo_bruto):,} COP")
        print(f"Costo total: {round(precio_total):,} COP")

        # Aplicar descuento por cantidad
        descuento_porcentaje = calcular_descuento(cantidad)
        descuento_valor = (precio_total * descuento_porcentaje) / 100
        precio_final = precio_total - descuento_valor
        precio_unitario_descuento = precio_final / cantidad
        precio_unitario_sin_descuento = precio_total / cantidad
        return {
            "status": "success",  # <-- clave para que el router no lance 422
            "precio_unitario_con_descuento": precio_unitario_descuento,
            "precio_unitario_sin_descuento": precio_unitario_sin_descuento,
            "descuento_porcentaje": descuento_porcentaje,
            "descuento_valor": descuento_valor,
            "precio_final": precio_final,
            "costo_bruto": costo_bruto,
            "total_perimeter": total_perimeter,
            "total_entities": total_entities,
            "costo_material": costo_material * cantidad,
            "costo_corte": costo_corte * cantidad,
            "costo_doblez": costo_lineas,
            "costo_transporte": transporte_mat * cantidad,
            "alistamiento": alistamiento * cantidad,
            "costo_almacenamiento": almacenaje_mat * cantidad,
            "ancho" : ancho,
            "alto" : alto,
            "Porcentaje_desperdicio": desperdicio_porcentaje,
            "costo_desperdicio": desperdicio_mat * cantidad
        }

    except Exception as e:
        return {"status": "failed", "error": str(e)}


def calcular_utilidad(costo_bruto):
    """
    Calcula la utilidad en función del costo bruto.
    Si el costo es de $1, la utilidad es del 60% (1.6).
    Si el costo es de $500,000 o más, la utilidad es del 20% (1.2).
    """
    if costo_bruto < 100000:
        # Utilidad decreciente linealmente desde 1.6 a 1.2 entre $1 y $500,000
        utilidad = 1.6 - ((1.6 - 1.2) * (costo_bruto - 1) / (100000 - 1))
    else:
        utilidad = 1.2
    return utilidad


def calculate_perimeter(entity):
    # Implementación original aquí (perímetros de LINE, CIRCLE, ARC, LWPOLYLINE/POLYLINE)
    # Si tu implementación previa ya funcionaba, consérvala.
    # Este placeholder evita romper dependencias si el módulo importaba esta función.
    if hasattr(entity, "dxftype"):
        t = entity.dxftype()
        if t == "LINE":
            s, e = entity.dxf.start, entity.dxf.end
            return math.dist((s.x, s.y), (e.x, e.y))
        elif t == "CIRCLE":
            r = entity.dxf.radius
            return 2 * math.pi * r
        elif t == "ARC":
            r = entity.dxf.radius
            a0 = math.radians(entity.dxf.start_angle)
            a1 = math.radians(entity.dxf.end_angle)
            return r * ((a1 - a0) % (2*math.pi))
    return 0.0


def calculate_area_and_bounds(modelspace):
    """
    Busca una entidad cerrada para estimar área y bounding box. Si no encuentra,
    intenta con una envolvente a partir de las entidades presentes.
    """
    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")
    area = 0.0

    for e in modelspace:
        try:
            if e.dxftype() == "CIRCLE":
                c = e.dxf.center
                r = e.dxf.radius
                min_x = min(min_x, c.x - r)
                min_y = min(min_y, c.y - r)
                max_x = max(max_x, c.x + r)
                max_y = max(max_y, c.y + r)
                area = max(area, math.pi * r * r)
            elif e.dxftype() == "LWPOLYLINE" and e.closed:
                pts = np.array([(p[0], p[1]) for p in e.get_points()])
                min_x = min(min_x, float(np.min(pts[:, 0])))
                min_y = min(min_y, float(np.min(pts[:, 1])))
                max_x = max(max_x, float(np.max(pts[:, 0])))
                max_y = max(max_y, float(np.max(pts[:, 1])))
                # Área por fórmula del polígono
                x = pts[:, 0]
                y = pts[:, 1]
                poly_area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
                area = max(area, float(poly_area))
        except Exception:
            continue

    if min_x == float("inf"):
        return None  # Si no es polilínea cerrada ni círculo, retornar None

    return {
        "area": area,
        "bounds": {
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y
        }
    }


def calcular_desperdicio(ancho, alto, save_best_png_path: str | None = None):
   
    # Dimensiones de la lámina
    sheet_width = 2440
    sheet_height = 1220
    total_area = sheet_width * sheet_height
    rect_area = (ancho) * (alto)  

    # Si la figura es más grande que la lámina, no cabe ninguna y el desperdicio es la lámina completa.
    if rect_area > total_area:
        return total_area

    # Cota superior teórica: máximo número de figuras que caben por área
    max_possible = int(total_area // rect_area)
    low, high = 0, max_possible
    best = 0
    best_packing = None  # Aquí guardaremos la mejor configuración
    rects_to_pack = []

    # Búsqueda binaria sobre cuántas figuras intentar empacar
    while low <= high:
        mid = (low + high) // 2

        # Re-inicializamos el packer para cada intento
        packer = newPacker(rotation=False)  # Permitir rotación si no es prohibido por material

        # Intentamos empacar 'mid' rectángulos
        rects_to_pack = [(ancho, alto, i + 1) for i in range(mid)]
        for w, h, rid in rects_to_pack:
            packer.add_rect(w, h, rid)

        packer.add_bin(sheet_width, sheet_height)  # Una sola lámina

        # Ejecutamos el packing
        packer.pack()

        # Obtenemos resultado
        all_rects = packer[0].rect_list() if len(packer) else []

        # Verificamos si se pudieron empacar todos los rectángulos
        packed_ids = set(r[5] for r in all_rects)  # r = (x, y, w, h, rid?, id)
        if len(packed_ids) == mid:
            # Actualizamos el mejor resultado encontrado
            best = mid
            best_packing = all_rects.copy()  # Guardamos la configuración actual
            low = mid + 1
        else:
            # Si no se pudieron empaquetar todos, reducimos el número a probar
            high = mid - 1

    # Calculamos el área utilizada y el desperdicio (en porcentaje)
    used_area = best * rect_area
    desperdicio = (1 - used_area / total_area) * 100

    print("Máximo teórico de piezas (por área):", max_possible)
    print("Rectángulos empaquetados:", best)

    # Generar imagen con matplotlib de la configuración empacada
    if best_packing:
        fig, ax = plt.subplots(figsize=(10, 5))

        # Dibujar la lámina
        sheet = patches.Rectangle((0, 0), sheet_width, sheet_height, edgecolor='black', facecolor='lightgrey', alpha=0.3)
        ax.add_patch(sheet)

        # Dibujar cada rectángulo
        colors = ['blue', 'red', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow']  # Colores diferentes para cada rectángulo
        for i, r in enumerate(best_packing):
            x, y, w, h, _, rid = r  # x, y, width, height, rid?, id
            # Dibujar un rectángulo con un color de borde y una cara transparente
            color = colors[i % len(colors)]
            rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor=color, facecolor='none')
            ax.add_patch(rect)
            # Añadir el ID del rectángulo dentro
            ax.text(x + w/2, y + h/2, str(rid), color='white', ha='center', va='center', fontsize=8)
        
        ax.set_xlim(0, sheet_width)
        ax.set_ylim(0, sheet_height)
        ax.set_aspect('equal')
        plt.title("Anidado de rectángulos")
        plt.xlabel("X")
        plt.ylabel("Y")
        if save_best_png_path:
            plt.tight_layout()
            plt.gcf().savefig(save_best_png_path, dpi=150, bbox_inches="tight")
        plt.close()

    return desperdicio
