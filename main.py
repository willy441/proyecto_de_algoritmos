from datetime import datetime
from operaciones import (
    LIMITE_STOCK,
    buscar_producto,
    cargar_inventario,
    eliminar_repuesto,
    guardar_inventario,
    obtener_categorias,
    ordenar_inventario,
    reducir_stock_repuesto,
    registrar_bitacora,
    validar_codigo,
)

registro_ventas_dia = []


def menu_agregar_producto(inventario: list[dict]) -> None:
    print("\n--- AGREGAR NUEVO REPUESTO ---")
    codigo = input("Ingrese codigo (ej. REP011): ").strip().upper()

    if not validar_codigo(codigo):
        print(">> Error: Formato invalido. Deben ser 3 letras y 3 numeros.")
        return

    for item in inventario:
        if item["codigo"] == codigo:
            print(">> Error: Ya existe un repuesto con ese codigo.")
            return

    nombre = input("Nombre del repuesto: ").strip().title()
    categoria = input("Categoria: ").strip().capitalize()

    try:
        precio = float(input("Precio unitario (Q): "))
        stock = int(input("Stock inicial: "))
        if precio <= 0 or stock < 0:
            print(">> Error: Precio y stock no pueden ser negativos.")
            return
    except ValueError:
        print(">> Error: Ingrese valores numericos validos.")
        return

    nuevo = {
        "codigo": codigo,
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": stock,
    }
    inventario.append(nuevo)
    registrar_bitacora(f"Producto agregado: {codigo} - {nombre}")
    print(f">> Repuesto '{nombre}' agregado exitosamente.")


def menu_buscar_producto(inventario: list[dict]) -> None:
    print("\n--- BUSCAR REPUESTO ---")
    texto = input("Ingrese codigo o nombre a buscar: ")
    resultados = buscar_producto(inventario, texto)

    if not resultados:
        print(">> No se encontraron repuestos.")
        return

    print("\nResultados encontrados:")
    print(f"{'CODIGO':<8} {'NOMBRE':<28} {'CATEGORIA':<15} {'PRECIO':<10} {'STOCK':<6}")
    print("-" * 70)
    for p in resultados:
        print(f"{p['codigo']:<8} {p['nombre']:<28} {p['categoria']:<15} Q{p['precio']:<9.2f} {p['stock']:<6}")


def menu_registrar_venta(inventario: list[dict]) -> None:
    print("\n--- REGISTRAR VENTA ---")
    codigo = input("Codigo del repuesto: ").strip().upper()

    encontrado = None
    for item in inventario:
        if item["codigo"] == codigo:
            encontrado = item
            break

    if not encontrado:
        print(">> Error: Codigo no encontrado.")
        return

    try:
        cantidad = int(input(f"Cantidad a vender (Disponibles: {encontrado['stock']}): "))
    except ValueError:
        print(">> Error: Debe ingresar un numero entero.")
        return

    if cantidad <= 0:
        print(">> Error: La cantidad debe ser mayor a 0.")
        return

    if cantidad > encontrado["stock"]:
        print(f">> Error: Stock insuficiente. Solo hay {encontrado['stock']} disponibles.")
        return

    encontrado["stock"] -= cantidad
    total = cantidad * encontrado["precio"]
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    registro_ventas_dia.append((fecha, codigo, cantidad, total))
    registrar_bitacora(f"Venta: {cantidad}x {codigo} - Total: Q{total:.2f}")

    print(f">> Venta completada. Total cobrado: Q{total:.2f}")
    if encontrado["stock"] <= LIMITE_STOCK:
        print(f"ALERTA: Quedan solo {encontrado['stock']} unidades de '{encontrado['nombre']}'.")


def menu_mostrar_inventario(inventario: list[dict]) -> None:
    print("\n--- INVENTARIO DEL TALLER ---")
    print("Ordenar por: [1] Nombre | [2] Precio")
    opc = input("Seleccione criterio (1 o 2): ").strip()

    criterio = "precio" if opc == "2" else "nombre"
    lista = ordenar_inventario(inventario, criterio)

    cats = ", ".join(obtener_categorias(inventario))
    print(f"\nCategorias registradas: {cats}")
    print(f"{'CODIGO':<8} {'NOMBRE':<28} {'CATEGORIA':<15} {'PRECIO':<10} {'STOCK':<8} {'ESTADO'}")
    print("-" * 80)
    for p in lista:
        estado = "Stock bajo" if p["stock"] <= LIMITE_STOCK else "OK"
        print(f"{p['codigo']:<8} {p['nombre']:<28} {p['categoria']:<15} Q{p['precio']:<9.2f} {p['stock']:<8} {estado}")


def menu_reporte_ventas() -> None:
    print("\n--- REPORTE DE VENTAS DEL DIA ---")
    if not registro_ventas_dia:
        print("No hay ventas registradas en esta sesion.")
        return

    print(f"{'FECHA':<18} {'CODIGO':<10} {'CANTIDAD':<10} {'TOTAL':<10}")
    print("-" * 50)
    total_general = 0.0
    for fecha, cod, cant, subtotal in registro_ventas_dia:
        print(f"{fecha:<18} {cod:<10} {cant:<10} Q{subtotal:<9.2f}")
        total_general += subtotal

    print("-" * 50)
    print(f"TOTAL DEL DIA: Q{total_general:.2f}")


def menu_quitar_o_reducir(inventario: list[dict]) -> None:
    print("\n--- BAJA O REDUCCION DE STOCK ---")
    print("1. Reducir unidades (dano, merma, garantia)")
    print("2. Eliminar repuesto del catalogo")
    opc = input("Opcion (1 o 2): ").strip()
    codigo = input("Codigo del repuesto: ").strip().upper()

    if opc == "1":
        try:
            cant = int(input("Cantidad a descontar: "))
        except ValueError:
            print(">> Error: Ingrese un numero entero.")
            return
        exito, msg = reducir_stock_repuesto(inventario, codigo, cant)
        print(f">> {msg}")
    elif opc == "2":
        confirmar = input(f"Seguro que desea eliminar el repuesto {codigo}? (s/n): ").strip().lower()
        if confirmar == "s":
            exito, msg = eliminar_repuesto(inventario, codigo)
            print(f">> {msg}")
        else:
            print(">> Cancelado.")
    else:
        print(">> Opcion invalida.")


def main():
    inventario = cargar_inventario()

    while True:
        print("\n======================================")
        print("  SISTEMA DE TALLER - MENU PRINCIPAL  ")
        print("======================================")
        print("1. Agregar nuevo producto")
        print("2. Buscar producto")
        print("3. Registrar venta")
        print("4. Mostrar inventario")
        print("5. Reporte de ventas del dia")
        print("6. Quitar stock o eliminar producto")
        print("7. Salir y guardar cambios")
        print("======================================")

        opcion = input("Seleccione opcion (1-7): ").strip()

        if opcion == "1":
            menu_agregar_producto(inventario)
        elif opcion == "2":
            menu_buscar_producto(inventario)
        elif opcion == "3":
            menu_registrar_venta(inventario)
        elif opcion == "4":
            menu_mostrar_inventario(inventario)
        elif opcion == "5":
            menu_reporte_ventas()
        elif opcion == "6":
            menu_quitar_o_reducir(inventario)
        elif opcion == "7":
            guardar_inventario(inventario)
            registrar_bitacora("Salida del sistema y datos guardados")
            print(">> Cambios guardados. Saliendo del sistema...")
            break
        else:
            print(">> Opcion invalida, intente de nuevo.")


if __name__ == "__main__":
    main()
