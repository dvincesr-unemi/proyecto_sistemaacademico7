from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula, Asistencia
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE (ABSTRACTA)
# =====================================================================
# Solo dice QUE metodos debe tener todo controlador.
# COMO se hace cada uno lo escribe cada controlador, de la forma mas simple.
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# CONTROLADOR DE ASISTENCIAS (NUEVO)
# =====================================================================
class AsistenciaController(CrudBase):

    def __init__(self, matriculas, archivo="datos/asistencias.json"):
        # INYECCION DE DEPENDENCIAS: Necesitamos validar que la matricula exista
        self.matriculas = matriculas
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Asistencia.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for asistencia in self.lista:
            datos.append(asistencia.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """Valida obligatoriedad de la matricula, la fecha y que el estado sea valido."""
        # Al crear (id_actual es None), matricula_id y fecha son obligatorios
        if id_actual is None:
            if str(datos.get("fecha", "")).strip() == "":
                return "La fecha es obligatoria"
            if "matricula_id" not in datos:
                return "Debe especificar el ID de la matricula"

        if "matricula_id" in datos:
            try:
                matricula_id = int(datos["matricula_id"])
                if self.matriculas and self.matriculas.obtener(matricula_id) is None:
                    return f"No existe una matricula con ID {matricula_id}"
            except (TypeError, ValueError):
                return "El ID de la matricula debe ser un numero entero"

        if "estado" in datos:
            estado = str(datos["estado"]).strip().capitalize()
            if not Asistencia.es_estado_valido(estado):
                validos = ", ".join(Asistencia.ESTADOS_VALIDOS)
                return f"Estado no valido. Opciones: {validos}"

        # Validacion logica: Un estudiante no puede tener dos asistencias el mismo dia en la misma matricula
        if "fecha" in datos and "matricula_id" in datos:
            fecha = str(datos["fecha"]).strip()
            matricula_id = int(datos["matricula_id"])
            for otra in self.lista:
                if (otra.fecha == fecha and otra.matricula_id == matricula_id 
                        and otra.id != id_actual):
                    return f"Ya existe un registro de asistencia para esta matricula el dia {fecha}"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_asistencia):
        for asistencia in self.lista:
            if asistencia.id == id_asistencia:
                return asistencia
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for asistencia in self.lista:
            if texto in asistencia.fecha.lower() or texto in asistencia.estado.lower():
                encontrados.append(asistencia)
        return encontrados

    def siguiente(self):
        mayor = 0
        for asistencia in self.lista:
            if asistencia.id > mayor:
                mayor = asistencia.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        estado_input = str(datos.get("estado", "Presente")).strip().capitalize()

        asistencia = Asistencia(
            self.siguiente(),
            int(datos["matricula_id"]),
            str(datos["fecha"]).strip(),
            estado_input
        )
        self.lista.append(asistencia)
        self.guardar()
        return True, f"Asistencia registrada: {asistencia.etiqueta()}"

    def actualizar(self, id_asistencia, datos):
        asistencia = self.obtener(id_asistencia)
        if asistencia is None:
            return False, f"No existe un registro de asistencia con ID {id_asistencia}"
        if not datos:
            return False, "No se indico ningun cambio"

        permitidos = {"matricula_id", "fecha", "estado"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no validos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_asistencia)
        if error:
            return False, error

        if "matricula_id" in datos:
            asistencia.matricula_id = int(datos["matricula_id"])
        if "fecha" in datos:
            asistencia.fecha = str(datos["fecha"]).strip()
        if "estado" in datos:
            asistencia.estado = str(datos["estado"]).strip().capitalize()

        self.guardar()
        return True, f"Registro de asistencia {id_asistencia} actualizado"

    def eliminar(self, id_asistencia):
        asistencia = self.obtener(id_asistencia)
        if asistencia is None:
            return False, f"No existe un registro con ID {id_asistencia}"

        self.lista.remove(asistencia)
        self.guardar()
        return True, f"Asistencia {id_asistencia} eliminada"

    def por_matricula(self, id_matricula):
        """Filtra y devuelve todo el historial de asistencias de una inscripcion."""
        return [a for a in self.lista if a.matricula_id == int(id_matricula)]


# =====================================================================
# CONTROLADOR DE ESTUDIANTES (ORIGINAL INTACTO)
# =====================================================================
class EstudianteController(CrudBase):

    def __init__(self, archivo="datos/estudiantes.json"):
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for estudiante in self.lista:
            datos.append(estudiante.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "apellido", "email"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email invalido: '{email}'"
            usados = {e.email for e in self.lista if e.id != id_actual}
            if email in usados:
                return "Ese email ya esta registrado en otro estudiante"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        for estudiante in self.lista:
            if estudiante.id == id_estudiante:
                return estudiante
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for estudiante in self.lista:
            if (texto in estudiante.nombre.lower()
                    or texto in estudiante.apellido.lower()
                    or texto in estudiante.email
                    or texto in estudiante.carnet.lower()
                    or texto in estudiante.carrera.lower()):
                encontrados.append(estudiante)
        return encontrados

    def siguiente(self):
        mayor = 0
        for estudiante in self.lista:
            if estudiante.id > mayor:
                mayor = estudiante.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        estudiante = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos.get("carnet", "")).strip().upper(),
            str(datos.get("carrera", "")).strip().title()
        )
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indico ningun cambio"

        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no validos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_estudiante)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(estudiante, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    def carreras_registradas(self):
        return sorted({e.carrera for e in self.lista if e.carrera != ""})


# =====================================================================
# CONTROLADOR DE MATERIAS (ORIGINAL INTACTO)
# =====================================================================
class MateriaController(CrudBase):

    def __init__(self, archivo="datos/materias.json"):
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for materia in self.lista:
            datos.append(materia.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "codigo"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        creditos = str(datos.get("creditos", "")).strip()
        if creditos != "" and not creditos.isdigit():
            return "Los creditos deben ser un numero entero"

        cupos = str(datos.get("cupos", "")).strip()
        if cupos != "" and not cupos.isdigit():
            return "Los cupos deben ser un numero entero positivo"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            for otra in self.lista:
                if otra.codigo == codigo and otra.id != id_actual:
                    return f"Ya existe una materia con el codigo {codigo}"
        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        for materia in self.lista:
            if materia.id == id_materia:
                return materia
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for materia in self.lista:
            if texto in materia.nombre.lower() or texto in materia.codigo.lower():
                encontrados.append(materia)
        return encontrados

    def siguiente(self):
        mayor = 0
        for materia in self.lista:
            if materia.id > mayor:
                mayor = materia.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        creditos = str(datos.get("creditos", "")).strip()
        cupos = str(datos.get("cupos", "")).strip()

        materia = Materia(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["codigo"]).strip().upper(),
            int(creditos) if creditos != "" else 0,
            int(cupos) if cupos != "" else Materia.CUPOS_MAXIMOS
        )

        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"
        if not datos:
            return False, "No se indico ningun cambio"

        desconocidos = set(datos) - {"nombre", "codigo", "creditos", "cupos"}
        if desconocidos:
            return False, f"Campos no validos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            materia.codigo = str(datos["codigo"]).strip().upper()
        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])
        if "cupos" in datos:
            materia.cupos = int(datos["cupos"])

        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe una materia con id {id_materia}"

        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"


# =====================================================================
# CONTROLADOR DE MATRICULAS (ORIGINAL INTACTO)
# =====================================================================
class MatriculaController(CrudBase):

    def __init__(self, estudiantes, materias, archivo="datos/matriculas.json"):
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for matricula in self.lista:
            datos.append(matricula.a_diccionario())
        self.gestor.guardar(datos)

    def validar_creacion(self, datos):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser numeros enteros"

        if self.estudiantes.obtener(estudiante_id) is None:
            return f"No existe un estudiante con id {estudiante_id}"

        materia = self.materias.obtener(materia_id)
        if materia is None:
            return f"No existe una materia con id {materia_id}"

        if not materia.hay_cupo():
            return f"La materia {materia.codigo} ya no tiene cupos disponibles"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        for matricula in self.lista:
            if matricula.id == id_matricula:
                return matricula
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontradas = []
        if texto == "":
            return encontradas

        for matricula in self.lista:
            if texto in matricula.periodo.lower() or texto in matricula.fecha:
                encontradas.append(matricula)
        return encontradas

    def siguiente(self):
        mayor = 0
        for matricula in self.lista:
            if matricula.id > mayor:
                mayor = matricula.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar_creacion(datos)
        if error:
            return False, error

        materia = self.materias.obtener(int(datos["materia_id"]))

        matricula = Matricula(
            self.siguiente(),
            int(datos["estudiante_id"]),
            materia.id,
            str(datos.get("periodo", "Actual")).strip().upper()
        )

        materia.ocupar_cupo()
        self.materias.guardar()

        self.lista.append(matricula)
        self.guardar()

        return True, f"Inscripcion registrada exitosamente. Cupos restantes: {materia.cupos}"

    def actualizar(self, id_matricula, datos):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matricula {id_matricula}"

        if "nota" not in datos:
            return False, "Solo se puede actualizar la nota de una matricula"

        if not Materia.es_nota_valida(datos["nota"]):
            return False, "La nota no es valida. Debe ser un numero entre 0 y 20"

        matricula.nota = float(datos["nota"])
        self.guardar()

        estado_final = matricula.estado()
        return True, f"Calificacion guardada. Estado academico: {estado_final}"

    def eliminar(self, id_matricula):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matricula {id_matricula}"

        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matricula {id_matricula} anulada y cupo liberado"

    def reporte_academico(self, id_estudiante):
        estudiante = self.estudiantes.obtener(id_estudiante)
        if estudiante is None:
            return None

        texto = f"BOLETIN ACADEMICO - {estudiante.nombre_completo()}\n"
        texto += f"Carrera: {estudiante.carrera}\n"
        texto += "-" * 50 + "\n"

        inscripciones = [m for m in self.lista if m.estudiante_id == id_estudiante]
        if not inscripciones:
            texto += "El estudiante no tiene materias registradas.\n"
            return texto

        for mat in inscripciones:
            materia = self.materias.obtener(mat.materia_id)
            nombre_mat = materia.nombre if materia else "Materia eliminada"
            texto += f"{mat.periodo} | {nombre_mat} -> Nota: {mat.nota} [{mat.estado()}]\n"

        texto += "-" * 50
        return texto