import os
from datetime import datetime

ARCHIVO_DATOS = "inventario_taller.csv"
ARCHIVO_LOG = "bitacora.log"
LIMITE_STOCK = 3


def registrar_bitacora(mensaje: str) -> None:
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as archivo:
            archivo.write(f"[{fecha}] {mensaje}\n")
    except OSError as e:
        print(f"Error al escribir bitácora: {e}")


def validar_codigo(codigo: str) -> bool:
    texto = codigo.strip().upper()
    if len(texto) != 6:
        return False
    letras = texto[:3]
    numeros = texto[3:]
    return letras.isalpha() and numeros.isdigit()


def cargar_inventario() -> list[dict]:
    inventario = []
    if not os.path.exists(ARCHIVO_DATOS):
        datos_base = [
            "codigo,nombre,categoria,precio,stock\n",
            "REP001,Filtro de Aceite,Filtros,65.00,12\n",
            "REP002,Filtro de Aire,Filtros,85.00,8\n",
            "REP003,Pastillas Delanteras,Frenos,250.00,5\n",
            "REP004,Liquido DOT4,Frenos,45.00,2\n",
            "REP005,Bujias Iridio,Encendido,320.00,6\n",
            "REP006,Aceite 10W-30,Lubricantes,185.00,10\n",
            "REP007,Aceite 20W-50,Lubricantes,160.00,3\n",
            "REP008,Amortiguador Delantero,Suspension,750.00,4\n",
            "REP009,Bateria 12V,Electrico,650.00,2\n",
            "REP010,Faja de Tiempo,Motor,140.00,7\n",
        ]
        try:
            with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
                archivo.writelines(datos_base)
            registrar_bitacora("Archivo creado con productos iniciales")
        except OSError as e:
            print(f"Error al crear archivo: {e}")
            return []

    try:
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
            filas = archivo.readlines()
            for linea in filas[1:]:
                partes = linea.strip().split(",")
                if len(partes) == 5:
                    repuesto = {
                        "codigo": partes[0],
                        "nombre": partes[1],
                        "categoria": partes[2],
                        "precio": float(partes[3]),
                        "stock": int(partes[4]),
                    }
                    inventario.append(repuesto)
    except (OSError, ValueError) as e:
        print(f"Error al leer archivo: {e}")

    return inventario


def guardar_inventario(inventario: list[dict]) -> None:
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
            archivo.write("codigo,nombre,categoria,precio,stock\n")
            for item in inventario:
                linea = f"{item['codigo']},{item['nombre']},{item['categoria']},{item['precio']:.2f},{item['stock']}\n"
                archivo.write(linea)
    except OSError as e:
        print(f"Error al guardar archivo: {e}")


def obtener_categorias(inventario: list[dict]) -> set:
    return {item["categoria"] for item in inventario}


def buscar_producto(inventario: list[dict], texto: str) -> list[dict]:
    termino = texto.strip().lower()
    coincidencias = []
    for item in inventario:
        if termino == item["codigo"].lower() or termino in item["nombre"].lower():
            coincidencias.append(item)
    return coincidencias


def ordenar_inventario(inventario: list[dict], criterio: str) -> list[dict]:
    if criterio == "precio":
        return sorted(inventario, key=lambda x: x["precio"])
    return sorted(inventario, key=lambda x: x["nombre"].lower())


def reducir_stock_repuesto(inventario: list[dict], codigo: str, cantidad: int) -> tuple[bool, str]:
    cod = codigo.strip().upper()
    for item in inventario:
        if item["codigo"] == cod:
            if cantidad <= 0:
                return False, "La cantidad debe ser mayor a 0."
            if cantidad > item["stock"]:
                return False, f"Stock insuficiente. Solo quedan {item['stock']}."
            item["stock"] -= cantidad
            registrar_bitacora(f"Reduccion de stock: {cod} - {cantidad} unidades")
            return True, f"Stock actualizado. Quedan {item['stock']} unidades."
    return False, "Producto no encontrado."


def eliminar_repuesto(inventario: list[dict], codigo: str) -> tuple[bool, str]:
    cod = codigo.strip().upper()
    for i, item in enumerate(inventario):
        if item["codigo"] == cod:
            nombre = item["nombre"]
            inventario.pop(i)
            registrar_bitacora(f"Producto eliminado: {cod} - {nombre}")
            return True, f"Repuesto '{nombre}' eliminado correctamente."
    return False, "Producto no encontrado."
