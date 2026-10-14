from datetime import date
from typing import Dict, Any


# =====================================================================
# CLASE BASE: lo que los modelos comparten
# =====================================================================
class ModeloBase:
    """Padre de todos los modelos. Guarda el id y define el comportamiento comun."""

    def __init__(self, id_registro: int) -> None:
        """
        Inicializa la entidad base con su identificador unico.

        Args:
            id_registro (int): Identificador numerico unico para el registro.

        Returns:
            None
        """
        self.id = int(id_registro)

    # ---- UNICO METODO DE CLASE DEL PROYECTO ----
    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "ModeloBase":
        """
        Diccionario -> objeto. Escrito UNA vez y usado por todos los modelos.
        cls es la clase que llamo: Estudiante, Materia, Matricula o Asistencia.

        Args:
            datos (Dict[str, Any]): Diccionario con los datos leidos del JSON.

        Returns:
            ModeloBase: Instancia de la clase que hizo la llamada.
        """
        datos_copia = dict(datos)                  # copia, para no tocar el original
        id_registro = datos_copia.pop("id")        # saco el id
        return cls(id_registro, **datos_copia)     # el resto son los campos del modelo

    # ---- METODOS DE INSTANCIA ----
    def a_diccionario(self) -> Dict[str, Any]:
        """
        Objeto -> diccionario. Cada hijo agrega sus campos.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario base conteniendo solo el id.
        """
        return {"id": self.id}

    def etiqueta(self) -> str:
        """
        POLIMORFISMO: cada hijo la reescribe a su manera para listados.

        Args:
            Ninguno

        Returns:
            str: Texto generico con el numero de registro.
        """
        return f"registro {self.id}"

    def __str__(self) -> str:
        """
        Lo que se ve al hacer print(objeto). Llama a etiqueta(),
        asi que cada modelo se imprime distinto sin cambiar esta linea.

        Args:
            Ninguno

        Returns:
            str: Representacion final formateada para la consola.
        """
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================================
# HERENCIA: Persona es la base de Estudiante
# =====================================================================
class Persona(ModeloBase):
    """Todo lo que tiene una persona del sistema."""

    def __init__(self, id_registro: int, nombre: str, apellido: str, email: str) -> None:
        """
        Inicializa una Persona con sus datos civiles basicos.

        Args:
            id_registro (int): Identificador unico numerico.
            nombre (str): Nombre de la persona.
            apellido (str): Apellido de la persona.
            email (str): Correo electronico de contacto.

        Returns:
            None
        """
        super().__init__(id_registro)      # el padre guarda el id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self) -> str:
        """
        Concatena de forma limpia el nombre y el apellido.

        Args:
            Ninguno

        Returns:
            str: Nombre y apellido unidos por un espacio.
        """
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Agrega los atributos de Persona al diccionario del padre.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con id, nombre, apellido y email.
        """
        datos = super().a_diccionario()    # {"id": ...} que arma el padre
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self) -> str:
        """
        Sobrescribe la representacion base para devolver el nombre completo.

        Args:
            Ninguno

        Returns:
            str: Nombre completo.
        """
        return self.nombre_completo()


class Estudiante(Persona):
    """Estudiante ES UNA Persona, con carnet y carrera."""

    def __init__(
        self, id_registro: int, nombre: str, apellido: str, email: str, 
        carnet: str = "", carrera: str = ""
    ) -> None:
        """
        Inicializa un Estudiante integrando sus datos academicos.

        Args:
            id_registro (int): Identificador unico numerico.
            nombre (str): Nombre del estudiante.
            apellido (str): Apellido del estudiante.
            email (str): Correo electronico de contacto.
            carnet (str, opcional): Codigo de identificacion. Por defecto "".
            carrera (str, opcional): Programa academico. Por defecto "".

        Returns:
            None
        """
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
        self.carrera = carrera

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Extiende el diccionario de Persona agregando carnet y carrera.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario completo del Estudiante.
        """
        datos = super().a_diccionario()    # reutiliza lo de Persona
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self) -> str:
        """
        Sobrescribe y EXTIENDE la etiqueta del padre (Persona).

        Args:
            Ninguno

        Returns:
            str: Representacion con nombre, carnet y carrera.
        """
        return f"{super().etiqueta()} · {self.carnet or 'sin carnet'} · {self.carrera}"


# =====================================================================
# UNICA CLASE CON ATRIBUTOS Y METODOS ESTATICOS
# =====================================================================
class Materia(ModeloBase):
    """Materia ES UN ModeloBase. Aqui viven los ejemplos de lo estatico para el sistema."""

    # ATRIBUTOS ESTATICOS (de clase): existen una sola vez, no por objeto
    CUPOS_MAXIMOS = 30           # regla del negocio, igual para todas las materias
    NOTA_APROBACION = 14         # calificacion minima para aprobar
    total_creadas = 0            # contador compartido

    def __init__(
        self, id_registro: int, nombre: str, codigo: str, 
        creditos: int = 0, cupos: int = 30
    ) -> None:
        """
        Inicializa una asignatura academica.

        Args:
            id_registro (int): Identificador unico numerico.
            nombre (str): Nombre de la asignatura.
            codigo (str): Codigo institucional de la asignatura.
            creditos (int, opcional): Valor en creditos academicos. Por defecto 0.
            cupos (int, opcional): Plazas disponibles. Por defecto 30.

        Returns:
            None
        """
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = int(creditos)
        self.cupos = int(cupos)
        Materia.total_creadas += 1         # se modifica en la CLASE, no en self

    # METODOS ESTATICOS: reglas que no necesitan ninguna materia concreta
    @staticmethod
    def es_nota_valida(valor: Any) -> bool:
        """
        Valida que un ingreso numerico este dentro del rango permitido (0 a 20).

        Args:
            valor (Any): Valor a evaluar, usualmente string o numerico.

        Returns:
            bool: True si es valido, False si hay error de tipo o rango.
        """
        try:
            nota = float(valor)
            return 0 <= nota <= 20
        except (TypeError, ValueError):
            return False

    # METODOS DE INSTANCIA: necesitan los datos de ESTA materia
    def hay_cupo(self) -> bool:
        """
        Verifica si la materia aun cuenta con plazas disponibles.

        Args:
            Ninguno

        Returns:
            bool: True si hay cupos restantes.
        """
        return self.cupos > 0

    def ocupar_cupo(self) -> None:
        """
        Resta 1 a la disponibilidad si es que todavia hay cupos.

        Args:
            Ninguno

        Returns:
            None
        """
        if self.hay_cupo():
            self.cupos -= 1

    def liberar_cupo(self) -> None:
        """
        Suma 1 a la disponibilidad, sin exceder el maximo configurado en la clase.

        Args:
            Ninguno

        Returns:
            None
        """
        if self.cupos < Materia.CUPOS_MAXIMOS:
            self.cupos += 1

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Objeto -> diccionario agregando los datos de la asignatura.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Datos para el JSON.
        """
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["codigo"] = self.codigo
        datos["creditos"] = self.creditos
        datos["cupos"] = self.cupos
        return datos

    def etiqueta(self) -> str:
        """
        Genera el formato de lectura para la asignatura y alerta si esta llena.

        Args:
            Ninguno

        Returns:
            str: Texto con codigo, nombre y cupos restantes.
        """
        alerta = " ⚠ LLENA" if not self.hay_cupo() else ""
        return f"[{self.codigo}] {self.nombre} ({self.creditos} Cr) · cupos {self.cupos}/{Materia.CUPOS_MAXIMOS}{alerta}"


# =====================================================================
# MATRICULA: Relacion transaccional 1 a 1 intacta
# =====================================================================
class Matricula(ModeloBase):
    """Matricula simple: une a un estudiante con una materia en un periodo especifico."""

    def __init__(
        self, id_registro: int, estudiante_id: int, materia_id: int, 
        periodo: str, nota: float = 0.0, fecha: str = ""
    ) -> None:
        """
        Inicializa la relacion transaccional entre estudiante y materia.

        Args:
            id_registro (int): Identificador de la matricula.
            estudiante_id (int): ID de la entidad Estudiante.
            materia_id (int): ID de la entidad Materia.
            periodo (str): Ciclo lectivo o semestre.
            nota (float, opcional): Calificacion. Por defecto 0.0.
            fecha (str, opcional): Fecha de registro. Por defecto se usa la de hoy.

        Returns:
            None
        """
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = periodo
        self.nota = float(nota)
        self.fecha = fecha or date.today().isoformat()

    def esta_aprobada(self) -> bool:
        """
        Consulta la regla estatica de Materia para saber si la nota es aprobatoria.
        Se calcula cada vez para no quedar desactualizado si la nota cambia.

        Args:
            Ninguno

        Returns:
            bool: True si es mayor o igual a la NOTA_APROBACION.
        """
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self) -> str:
        """
        Convierte la validacion de aprobacion en un estado legible.

        Args:
            Ninguno

        Returns:
            str: 'Aprobada' o 'Reprobada'.
        """
        return "Aprobada" if self.esta_aprobada() else "Reprobada"

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Devuelve el diccionario que se persistira en la transaccion.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con referencias y calificacion.
        """
        datos = super().a_diccionario()
        datos["estudiante_id"] = self.estudiante_id
        datos["materia_id"] = self.materia_id
        datos["periodo"] = self.periodo
        datos["nota"] = self.nota
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self) -> str:
        """
        Formato de lectura que resume la situacion academica de la inscripcion.

        Args:
            Ninguno

        Returns:
            str: Historial formateado.
        """
        return (f"{self.fecha} · estudiante {self.estudiante_id} · "
                f"materia {self.materia_id} ({self.periodo}) "
                f"-> Nota: {self.nota} [{self.estado()}]")


# =====================================================================
# ASISTENCIA: Control de presencia a clases vinculado a la matricula
# =====================================================================
class Asistencia(ModeloBase):
    """Registro de asistencia diaria o por clase para una matricula especifica."""

    ESTADOS_VALIDOS = {"Presente", "Falta", "Atraso", "Justificado"}

    def __init__(
        self, id_registro: int, matricula_id: int, fecha: str, estado: str = "Presente"
    ) -> None:
        """
        Inicializa un registro de asistencia en el aula.

        Args:
            id_registro (int): Identificador numerico unico.
            matricula_id (int): ID de la inscripcion (que vincula estudiante y materia).
            fecha (str): Fecha de la clase (ej: '2026-10-14').
            estado (str, opcional): Condicion de asistencia. Por defecto 'Presente'.

        Returns:
            None
        """
        super().__init__(id_registro)
        self.matricula_id = int(matricula_id)
        self.fecha = fecha
        
        # Validación de estado: Si no es uno de los permitidos, por defecto asigna 'Falta'
        estado_formateado = str(estado).strip().capitalize()
        self.estado = estado_formateado if estado_formateado in self.ESTADOS_VALIDOS else "Falta"

    @staticmethod
    def es_estado_valido(estado: str) -> bool:
        """
        Verifica si el texto de estado corresponde a los permitidos por el sistema.

        Args:
            estado (str): Texto a validar.

        Returns:
            bool: True si es valido, False si no existe en ESTADOS_VALIDOS.
        """
        return str(estado).strip().capitalize() in Asistencia.ESTADOS_VALIDOS

    def a_diccionario(self) -> Dict[str, Any]:
        """
        Serializa los campos del registro de asistencia.

        Args:
            Ninguno

        Returns:
            Dict[str, Any]: Diccionario con la informacion transaccional diaria.
        """
        datos = super().a_diccionario()
        datos["matricula_id"] = self.matricula_id
        datos["fecha"] = self.fecha
        datos["estado"] = self.estado
        return datos

    def etiqueta(self) -> str:
        """
        Representacion resumida del registro diario.

        Args:
            Ninguno

        Returns:
            str: Fecha, ID de matricula y Estado.
        """
        return f"{self.fecha} · Matricula #{self.matricula_id} -> {self.estado}"