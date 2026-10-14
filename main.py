from datetime import date
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
# 1. Importamos AsistenciaController junto a los demas controladores
from views import (
    EstudianteController, MateriaController, MatriculaController, AsistenciaController
)

# Se crea UN solo controlador de cada tipo.
# Inyeccion de dependencias:
# - Estudiantes y Materias se pasan a Matriculas (flujo 1 a 1).
# - Matriculas se pasa a Asistencias (para validar el registro diario).
estudiantes = EstudianteController()
materias = MateriaController()
matriculas = MatriculaController(estudiantes, materias)
asistencias = AsistenciaController(matriculas)  # <--- NUEVO CONTROLADOR


# =====================================================================
# AYUDAS DE PANTALLA
# =====================================================================

def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    """Devuelve un entero o None si el usuario escribio otra cosa."""
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    # Los controladores devuelven la TUPLA (exito, mensaje)
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavia."):
    """Sirve para estudiantes, materias, matriculas y asistencias: cada modelo sabe mostrarse."""
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    # Recorre el DICCIONARIO del objeto: clave y valor a la vez
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


# =====================================================================
# MENU DE ASISTENCIAS (NUEVO)
# =====================================================================

def registrar_asistencia():
    imprimir_titulo("REGISTRAR ASISTENCIA")
    imprimir_info("Matriculas (Inscripciones Activas):")
    mostrar_lista(matriculas.leer(), "No hay alumnos matriculados.")

    fecha_hoy = date.today().isoformat()
    datos = {
        "matricula_id": pedir_entero("\nId de la matricula: "),
        "fecha": input(f"Fecha (ej. {fecha_hoy}) [Enter = hoy]: ").strip(),
        "estado": input("Estado (Presente / Falta / Atraso / Justificado) [Enter = Presente]: ").strip()
    }
    
    if not datos["fecha"]:
        datos["fecha"] = fecha_hoy
    if not datos["estado"]:
        datos["estado"] = "Presente"
        
    if datos["matricula_id"] is None:
        imprimir_error("El ID de la matricula debe ser un numero")
        return pausa()

    mostrar_resultado(*asistencias.crear(datos))
    pausa()


def listar_asistencias():
    imprimir_titulo("HISTORIAL DE ASISTENCIAS")
    mostrar_lista(asistencias.leer(), "Todavia no hay registros de asistencia.")
    pausa()


def buscar_asistencia():
    imprimir_titulo("BUSCAR ASISTENCIA")
    termino = input("Fecha o Estado: ")
    encontradas = asistencias.buscar(termino)
    mostrar_lista(encontradas, f"Ningun registro coincide con '{termino}'.")
    pausa()


def ver_asistencia():
    imprimir_titulo("VER ASISTENCIA POR ID")
    asis = asistencias.obtener(pedir_entero("Id: "))
    if asis is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(asis)
        # Mostrar contexto del alumno y materia
        mat = matriculas.obtener(asis.matricula_id)
        if mat:
            est = estudiantes.obtener(mat.estudiante_id)
            mate = materias.obtener(mat.materia_id)
            n_est = est.nombre_completo() if est else f"Estudiante #{mat.estudiante_id}"
            n_mat = mate.nombre if mate else f"Materia #{mat.materia_id}"
            print(f"\n  Alumno  : {n_est}")
            print(f"  Materia : {n_mat} ({mat.periodo})")
    pausa()


def actualizar_asistencia():
    imprimir_titulo("ACTUALIZAR ASISTENCIA")
    id_asistencia = pedir_entero("Id: ")
    asis = asistencias.obtener(id_asistencia)
    if asis is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {asis.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    nueva_fecha = input(f"Fecha [{asis.fecha}]: ").strip()
    if nueva_fecha:
        cambios["fecha"] = nueva_fecha
        
    nuevo_estado = input(f"Estado [{asis.estado}]: ").strip()
    if nuevo_estado:
        cambios["estado"] = nuevo_estado

    mostrar_resultado(*asistencias.actualizar(id_asistencia, cambios))
    pausa()


def eliminar_asistencia():
    imprimir_titulo("ELIMINAR ASISTENCIA")
    id_asistencia = pedir_entero("Id: ")
    asis = asistencias.obtener(id_asistencia)
    if asis is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminara: {asis.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*asistencias.eliminar(id_asistencia))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# =====================================================================
# MENU DE ESTUDIANTES (INTACTO)
# =====================================================================

def crear_estudiante():
    imprimir_titulo("CREAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet: "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*estudiantes.crear(datos))
    pausa()


def listar_estudiantes():
    imprimir_titulo("ESTUDIANTES")
    mostrar_lista(estudiantes.leer(), "Todavia no hay estudiantes registrados.")
    pausa()


def buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, apellido, email, carnet o carrera: ")
    encontrados = estudiantes.buscar(termino)
    mostrar_lista(encontrados, f"Ningun estudiante coincide con '{termino}'.")
    pausa()


def ver_estudiante():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    estudiante = estudiantes.obtener(pedir_entero("Id: "))
    if estudiante is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(estudiante)
    pausa()


def actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_estudiante = pedir_entero("Id: ")
    estudiante = estudiantes.obtener(id_estudiante)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {estudiante.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        actual = getattr(estudiante, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*estudiantes.actualizar(id_estudiante, cambios))
    pausa()


def eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_estudiante = pedir_entero("Id: ")
    estudiante = estudiantes.obtener(id_estudiante)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminara: {estudiante.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*estudiantes.eliminar(id_estudiante))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# =====================================================================
# MENU DE MATERIAS (INTACTO)
# =====================================================================

def crear_materia():
    imprimir_titulo("CREAR MATERIA")
    datos = {
        "nombre": input("Nombre: "),
        "codigo": input("Codigo: "),
        "creditos": input("Creditos: "),
        "cupos": input("Cupos iniciales [Enter = 30]: "),
    }
    mostrar_resultado(*materias.crear(datos))
    pausa()


def listar_materias():
    imprimir_titulo("MATERIAS")
    mostrar_lista(materias.leer(), "Todavia no hay materias creadas.")
    pausa()


def buscar_materia():
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Nombre o codigo: ")
    mostrar_lista(materias.buscar(termino), "Sin coincidencias.")
    pausa()


def ver_materia():
    imprimir_titulo("VER MATERIA POR ID")
    materia = materias.obtener(pedir_entero("Id: "))
    if materia is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(materia)
    pausa()


def actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")
    id_materia = pedir_entero("Id: ")
    materia = materias.obtener(id_materia)
    if materia is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {materia.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "codigo", "creditos", "cupos"):
        actual = getattr(materia, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*materias.actualizar(id_materia, cambios))
    pausa()


def eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")
    id_materia = pedir_entero("Id: ")
    materia = materias.obtener(id_materia)
    if materia is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminara: {materia.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*materias.eliminar(id_materia))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


# =====================================================================
# MENU DE MATRICULAS (INTACTO)
# =====================================================================

def registrar_matricula():
    imprimir_titulo("REGISTRAR MATRICULA")
    imprimir_info("Estudiantes:")
    mostrar_lista(estudiantes.leer())
    imprimir_info("Materias:")
    mostrar_lista(materias.leer())

    datos = {
        "estudiante_id": pedir_entero("\nId del estudiante: "),
        "materia_id": pedir_entero("Id de la materia: "),
        "periodo": input("Periodo (ej. 2026-1): "),
    }
    
    if None in (datos["estudiante_id"], datos["materia_id"]):
        imprimir_error("Los IDs deben ser numeros enteros")
        return pausa()

    mostrar_resultado(*matriculas.crear(datos))
    pausa()


def listar_matriculas():
    imprimir_titulo("MATRICULAS ACTIVAS")
    mostrar_lista(matriculas.leer(), "Todavia no hay inscripciones.")
    pausa()


def asentar_calificacion():
    imprimir_titulo("ASENTAR CALIFICACION")
    id_matricula = pedir_entero("Id de la matricula: ")
    if not id_matricula:
        return pausa()
        
    nota = input("Ingrese la nota (0 a 20): ")
    mostrar_resultado(*matriculas.actualizar(id_matricula, {"nota": nota}))
    pausa()


def ver_reporte():
    imprimir_titulo("REPORTE ACADEMICO")
    texto = matriculas.reporte_academico(pedir_entero("Id del estudiante: "))
    if texto is None:
        imprimir_error("El estudiante no existe.")
    else:
        print(texto)
    pausa()


def anular_matricula():
    imprimir_titulo("ANULAR MATRICULA")
    id_matricula = pedir_entero("Id de la matricula: ")
    if id_matricula and confirmar("Se liberara el cupo. ¿Confirma?"):
        mostrar_resultado(*matriculas.eliminar(id_matricula))
    else:
        imprimir_info("Operacion cancelada")
    pausa()


def resumen():
    imprimir_titulo("RESUMEN GENERAL")
    print(f"  Estudiantes : {len(estudiantes.leer())}")
    print(f"  Carreras    : {', '.join(estudiantes.carreras_registradas()) or '-'}")
    print(f"  Materias    : {len(materias.leer())}")
    
    llenas = [m for m in materias.leer() if not m.hay_cupo()]
    print(f"  Sin cupos   : {', '.join(m.codigo for m in llenas) or 'ninguna'}")
    print(f"  Matriculas  : {len(matriculas.leer())}")
    print(f"  Asistencias : {len(asistencias.leer())} registros diarios")
    pausa()


# =====================================================================
# MENUS: DICCIONARIOS tecla -> (texto, funcion)
# =====================================================================

MENU_ASISTENCIAS = {
    "1": ("Registrar asistencia", registrar_asistencia),
    "2": ("Ver historial general", listar_asistencias),
    "3": ("Buscar registro", buscar_asistencia),
    "4": ("Ver detalle por id", ver_asistencia),
    "5": ("Modificar estado/fecha", actualizar_asistencia),
    "6": ("Eliminar registro", eliminar_asistencia),
    "0": ("Volver", None),
}

MENU_ESTUDIANTES = {
    "1": ("Crear estudiante", crear_estudiante),
    "2": ("Ver todos", listar_estudiantes),
    "3": ("Buscar", buscar_estudiante),
    "4": ("Ver por id", ver_estudiante),
    "5": ("Actualizar", actualizar_estudiante),
    "6": ("Eliminar", eliminar_estudiante),
    "0": ("Volver", None),
}

MENU_MATERIAS = {
    "1": ("Crear materia", crear_materia),
    "2": ("Ver todas", listar_materias),
    "3": ("Buscar", buscar_materia),
    "4": ("Ver por id", ver_materia),
    "5": ("Actualizar", actualizar_materia),
    "6": ("Eliminar", eliminar_materia),
    "0": ("Volver", None),
}

MENU_MATRICULAS = {
    "1": ("Inscribir estudiante", registrar_matricula),
    "2": ("Ver todas", listar_matriculas),
    "3": ("Asentar calificacion", asentar_calificacion),
    "4": ("Ver reporte academico", ver_reporte),
    "5": ("Anular matricula", anular_matricula),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    """Un solo bucle para los submenus."""
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()

        tecla = input("Opcion: ").strip()
        if tecla not in opciones:
            imprimir_error("Opcion no valida")
            pausa()
            continue

        _texto, funcion = opciones[tecla]
        if funcion is None:
            break
        funcion()


def main():
    while True:
        imprimir_titulo("SISTEMA ACADEMICO")
        print("  1. Estudiantes")
        print("  2. Materias")
        print("  3. Matriculas")
        print("  4. Control de Asistencia")  # <--- NUEVA OPCION EN EL MENU
        print("  5. Resumen")
        print("  0. Salir\n")

        tecla = input("Opcion: ").strip()
        if tecla == "1":
            ejecutar_menu("GESTION DE ESTUDIANTES", MENU_ESTUDIANTES)
        elif tecla == "2":
            ejecutar_menu("GESTION DE MATERIAS", MENU_MATERIAS)
        elif tecla == "3":
            ejecutar_menu("GESTION DE MATRICULAS", MENU_MATRICULAS)
        elif tecla == "4":
            ejecutar_menu("CONTROL DE ASISTENCIA", MENU_ASISTENCIAS)
        elif tecla == "5":
            resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego! 👋")
            break
        else:
            imprimir_error("Opcion no valida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")