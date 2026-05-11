"""
Sistema Integral para Software FJ

UNAD - Fase 4 - Prácticas Simuladas

Nombre de los estudiantes:
    Isabel Cristina Rozo Mercado
    David Leonardo Gomez Castro
    Camilo Andres Hernandez Sogamoso
    Edwin Leonardo Rincon Silva
    Ever Augusto Gomez Rojas

Grupo: 213023_193

Programa: Escuela de Ciencias Básicas, Tecnología e Ingeniería

Código Fuente: Autoría propia

Gestión de: Clientes, Servicios y Reservas
- Reservas de salas
- Alquiler de equipos
- Asesorías especializadas

Persistencia: JSON | Logs: .log
"""

from typing import Optional, List, Dict
import logging
from abc import ABC, abstractmethod
from datetime import datetime

class SoftwareFJException(Exception):
    """Excepción base para el sistema"""
    def __init__(self, mensaje: str, codigo: int = 1000):
        self.mensaje = mensaje
        self.codigo = codigo
        super().__init__(self.mensaje)
    
    def __str__(self):
        return f"[Código {self.codigo}] {self.mensaje}"


class ValidacionException(SoftwareFJException):
    """Excepción para errores de validación"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo=1001)


class ReservaException(SoftwareFJException):
    """Excepción para errores en reservas"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo=1002)


class ServicioException(SoftwareFJException):
    """Excepción para errores de servicio"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo=1003)


class ClienteException(SoftwareFJException):
    """Excepción para errores de cliente"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo=1004)


class DatosException(SoftwareFJException):
    """Excepción para datos inválidos o faltantes"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo=1005)

class GestorLogs:
    """Gestor centralizado de logs del sistema"""
    
    def __init__(self, archivo_log: str = "software_fj.log"):
        self.archivo_log = archivo_log
        self._configurar_log()
    
    def _configurar_log(self):
        """Configura el sistema de logging"""
        self.logger = logging.getLogger("SoftwareFJ")
        self.logger.setLevel(logging.DEBUG)
        
        # Handler para archivo
        handler = logging.FileHandler(self.archivo_log, encoding='utf-8')
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(handler)
    
    def info(self, mensaje: str):
        """Registra información"""
        self.logger.info(mensaje)
    
    def warning(self, mensaje: str):
        """Registra advertencias"""
        self.logger.warning(mensaje)
    
    def error(self, mensaje: str, excepcion: Optional[Exception] = None):
        """Registra errores"""
        if excepcion:
            self.logger.error(f"{mensaje} | Excepción: {type(excepcion).__name__}: {str(excepcion)}")
        else:
            self.logger.error(mensaje)
    
    def debug(self, mensaje: str):
        """Registra debug"""
        self.logger.debug(mensaje)

gestor_logs = GestorLogs()

class Entidad(ABC):
    """Clase abstracta que representa entidades generales del sistema"""
    
    def __init__(self, id_entidad: int):
        self._id = id_entidad
        self._fecha_creacion = datetime.now()
        self._activo = True
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion
    
    @property
    def activo(self) -> bool:
        return self._activo
    
    @activo.setter
    def activo(self, valor: bool):
        self._activo = valor
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        pass
    
    @abstractmethod
    def validar(self) -> bool:
        """Valida los datos de la entidad"""
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}(id={self._id})"

class Cliente(Entidad):
    """Clase Cliente con validaciones robustas y encapsulación de datos"""
    
    def __init__(self, id_cliente: int, nombre: str, apellido: str, 
                 identificacion: str, telefono: str, email: str):
        super().__init__(id_cliente)
        self._nombre = nombre
        self._apellido = apellido
        self._identificacion = identificacion
        self._telefono = telefono
        self._email = email
        self._reservas: List[int] = []  # IDs de reservas asociadas
        
        # Validar al crear
        self.validar()
        gestor_logs.info(f"Cliente creado: {self.nombre_completo}")
    
    # -------------------------------------------------------------------------
    # Propiedades con encapsulación
    # -------------------------------------------------------------------------
    
    @property
    def nombre(self) -> str:
        return self._nombre
    
    @nombre.setter
    def nombre(self, valor: str):
        if not valor or len(valor.strip()) < 2:
            raise ValidacionException("El nombre debe tener al menos 2 caracteres")
        self._nombre = valor.strip().title()
    
    @property
    def apellido(self) -> str:
        return self._apellido
    
    @apellido.setter
    def apellido(self, valor: str):
        if not valor or len(valor.strip()) < 2:
            raise ValidacionException("El apellido debe tener al menos 2 caracteres")
        self._apellido = valor.strip().title()
    
    @property
    def identificacion(self) -> str:
        return self._identificacion
    
    @identificacion.setter
    def identificacion(self, valor: str):
        if not valor or len(valor.strip()) < 5:
            raise ValidacionException("La identificación debe tener al menos 5 caracteres")
        self._identificacion = valor.strip()
    
    @property
    def telefono(self) -> str:
        return self._telefono
    
    @telefono.setter
    def telefono(self, valor: str):
        # Validar formato de teléfono
        telefono_limpio = valor.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not telefono_limpio.isdigit() or len(telefono_limpio) < 7:
            raise ValidacionException("El teléfono debe tener al menos 7 dígitos")
        self._telefono = valor.strip()
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, valor: str):
        # Validar formato de email
        valor = valor.strip().lower()
        if '@' not in valor or '.' not in valor.split('@')[-1]:
            raise ValidacionException("El email no tiene un formato válido")
        self._email = valor
    
    @property
    def nombre_completo(self) -> str:
        return f"{self._nombre} {self._apellido}"
    
    @property
    def reservas(self) -> List[int]:
        return self._reservas.copy()
    
    # -------------------------------------------------------------------------
    # Métodos
    # -------------------------------------------------------------------------
    
    def agregar_reserva(self, id_reserva: int):
        """Agrega una reserva al cliente"""
        if id_reserva not in self._reservas:
            self._reservas.append(id_reserva)
            gestor_logs.info(f"Reserva {id_reserva} asociada al cliente {self._id}")
    
    def quitar_reserva(self, id_reserva: int):
        """Quita una reserva del cliente"""
        if id_reserva in self._reservas:
            self._reservas.remove(id_reserva)
            gestor_logs.info(f"Reserva {id_reserva} desasociada del cliente {self._id}")
    
    def to_dict(self) -> dict:
        """Convierte el cliente a diccionario"""
        return {
            "id": self._id,
            "nombre": self._nombre,
            "apellido": self._apellido,
            "identificacion": self._identificacion,
            "telefono": self._telefono,
            "email": self._email,
            "reservas": self._reservas,
            "fecha_creacion": self._fecha_creacion.isoformat(),
            "activo": self._activo
        }
    
    @classmethod
    def from_dict(cls, datos: dict) -> 'Cliente':
        """Crea un cliente desde un diccionario"""
        cliente = cls(
            datos["id"],
            datos["nombre"],
            datos["apellido"],
            datos["identificacion"],
            datos["telefono"],
            datos["email"]
        )
        cliente._reservas = datos.get("reservas", [])
        cliente._activo = datos.get("activo", True)
        if "fecha_creacion" in datos:
            cliente._fecha_creacion = datetime.fromisoformat(datos["fecha_creacion"])
        return cliente
    
    def validar(self) -> bool:
        """Valida los datos del cliente"""
        try:
            # Validar nombre
            if not self._nombre or len(self._nombre.strip()) < 2:
                raise ValidacionException("Nombre inválido")
            
            # Validar apellido
            if not self._apellido or len(self._apellido.strip()) < 2:
                raise ValidacionException("Apellido inválido")
            
            # Validar identificación
            if not self._identificacion or len(self._identificacion.strip()) < 5:
                raise ValidacionException("Identificación inválida")
            
            # Validar teléfono
            telefono_limpio = self._telefono.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            if not telefono_limpio.isdigit() or len(telefono_limpio) < 7:
                raise ValidacionException("Teléfono inválido")
            
            # Validar email
            if '@' not in self._email or '.' not in self._email.split('@')[-1]:
                raise ValidacionException("Email inválido")
            
            return True
            
        except ValidacionException as e:
            gestor_logs.error(f"Error de validación en cliente: {e}")
            raise
    
    def __str__(self):
        return f"Cliente: {self._nombre} {self._apellido} ({self._identificacion})"

class Servicio(ABC):
    """Clase abstracta Servicio"""
    
    def __init__(self, id_servicio: int, nombre: str, descripcion: str):
        self._id = id_servicio
        self._nombre = nombre
        self._descripcion = descripcion
        self._activo = True
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def nombre(self) -> str:
        return self._nombre
    
    @property
    def descripcion(self) -> str:
        return self._descripcion
    
    @property
    def activo(self) -> bool:
        return self._activo
    
    @abstractmethod
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        """Calcula el costo del servicio - método sobrescrito"""
        pass
    
    @abstractmethod
    def describir_servicio(self) -> str:
        """Describe el servicio - método sobrescrito"""
        pass
    
    @abstractmethod
    def validar_parametros(self, **kwargs) -> bool:
        """Valida los parámetros del servicio"""
        pass
    
    def to_dict(self) -> dict:
        """Convierte el servicio a diccionario"""
        return {
            "id": self._id,
            "nombre": self._nombre,
            "descripcion": self._descripcion,
            "activo": self._activo,
            "tipo": self.__class__.__name__
        }
    
    def __repr__(self):
        return f"Servicio(id={self._id}, nombre='{self._nombre}')"

class ServicioReservaSala(Servicio):
    """Servicio de reservas de salas"""
    
    TARIFA_POR_HORA = 50000  # Tarifa base por hora
    
    def __init__(self, id_servicio: int, capacidad: int = 10):
        super().__init__(
            id_servicio, 
            "Reserva de Sala", 
            "Alquiler de salas para reuniones, conferencias y eventos"
        )
        self._capacidad = capacidad
        self._salas_disponibles = ["Sala A", "Sala B", "Sala C", "Sala VIP"]
    
    @property
    def capacidad(self) -> int:
        return self._capacidad
    
    @property
    def salas(self) -> List[str]:
        return self._salas_disponibles.copy()
    
    # -------------------------------------------------------------------------
    # Métodos sobrescritos (polimorfismo)
    # -------------------------------------------------------------------------
    
    def calcular_costo(self, duracion: float, sala: str = None, 
                      horas_extras: float = 0, descuento: float = 0) -> float:
        """
        Método sobrecargado para calcular costo de reserva de sala
        
        Variantes:
        - calcular_costo(duracion) -> costo básico
        - calcular_costo(duracion, sala) -> costo con sala específica
        - calcular_costo(duracion, sala, horas_extras, descuento) -> costo completo
        """
        try:
            # Validar duración
            if duracion <= 0:
                raise ServicioException("La duración debe ser mayor a 0")
            
            if duracion > 12:
                raise ServicioException("La duración máxima es de 12 horas")
            
            # Calcular costo base
            costo = duracion * self.TARIFA_POR_HORA
            
            # Aplicar costo por sala específica
            if sala:
                if sala not in self._salas_disponibles:
                    raise ServicioException(f"La sala '{sala}' no está disponible")
                
                # Salas VIP tienen recargo
                if sala == "Sala VIP":
                    costo *= 1.5
                elif sala == "Sala A":
                    costo *= 1.2
            
            # Agregar horas extras
            if horas_extras > 0:
                costo += horas_extras * (self.TARIFA_POR_HORA * 1.25)
            
            # Aplicar descuento
            if descuento > 0:
                if descuento > 50:
                    raise ServicioException("El descuento no puede exceder el 50%")
                costo -= costo * (descuento / 100)
            
            gestor_logs.info(f"Costo calculado para reserva de sala: ${costo:,.2f}")
            return costo
            
        except ServicioException as e:
            gestor_logs.error(f"Error al calcular costo de reserva: {e}")
            raise
        except Exception as e:
            gestor_logs.error("Error inesperado calculando costo", e)
            raise ServicioException(f"Error al calcular costo: {str(e)}")
    
    def describir_servicio(self) -> str:
        """Describe el servicio de reserva de sala"""
        return (f"Reserva de Sala - Capacidad: {self._capacidad} personas\n"
                f"Salas disponibles: {', '.join(self._salas_disponibles)}\n"
                f"Tarifa: ${self.TARIFA_POR_HORA:,}/hora")
    
    def validar_parametros(self, **kwargs) -> bool:
        """Valida los parámetros para reserva de sala"""
        duracion = kwargs.get("duracion")
        sala = kwargs.get("sala")
        
        if duracion and (duracion <= 0 or duracion > 12):
            raise ServicioException("Duración inválida para reserva de sala")
        
        if sala and sala not in self._salas_disponibles:
            raise ServicioException(f"Sala '{sala}' no disponible")
        
        return True
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        datos = super().to_dict()
        datos.update({
            "capacidad": self._capacidad,
            "salas": self._salas_disponibles,
            "tarifa_hora": self.TARIFA_POR_HORA
        })
        return datos

class ServicioAlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos"""    
    def __init__(self, id_servicio: int):
        super().__init__(
            id_servicio,
            "Alquiler de Equipos",
            "Alquiler de equipos tecnológicos para eventos y presentaciones"
        )
        self._equipos_disponibles = list(self.TARIFAS.keys())
    
    @property
    def equipos(self) -> List[str]:
        return self._equipos_disponibles.copy()
    
    def obtener_tarifa(self, equipo: str) -> float:
        """Obtiene la tarifa de un equipo específico"""
        return self.TARIFAS.get(equipo.lower(), 0)
    
    # -------------------------------------------------------------------------
    # Métodos sobrescritos (polimorfismo)
    # -------------------------------------------------------------------------
    
    def calcular_costo(self, duracion: float, equipo: str = None,
                      cantidad: int = 1, seguro: bool = False) -> float:
        """
        Método sobrecargado para calcular costo de alquiler de equipo
        
        Variantes:
        - calcular_costo(duracion) -> costo total de todos los equipos
        - calcular_costo(duracion, equipo) -> costo de equipo específico
        - calcular_costo(duracion, equipo, cantidad, seguro) -> costo completo
        """
        try:
            if duracion <= 0:
                raise ServicioException("La duración debe ser mayor a 0")
            
            costo = 0
            
            if equipo:
                # Costo de equipo específico
                tarifa = self.obtener_tarifa(equipo)
                if tarifa == 0:
                    raise ServicioException(f"Equipo '{equipo}' no disponible")
                
                costo = duracion * tarifa * cantidad
                
                # Agregar costo de seguro (10%)
                if seguro:
                    costo *= 1.10
            else:
                # Costo de todos los equipos
                for eq in self._equipos_disponibles:
                    costo += duracion * self.TARIFAS[eq]
            
            gestor_logs.info(f"Costo calculado para alquiler de equipo: ${costo:,.2f}")
            return costo
            
        except ServicioException as e:
            gestor_logs.error(f"Error al calcular costo de alquiler: {e}")
            raise
        except Exception as e:
            gestor_logs.error("Error inesperado calculando costo", e)
            raise ServicioException(f"Error al calcular costo: {str(e)}")
    
    def describir_servicio(self) -> str:
        """Describe el servicio de alquiler de equipos"""
        equipos_info = "\n".join([f"  - {eq}: ${tar:,}/hora" 
                                   for eq, tar in self.TARIFAS.items()])
        return f"Alquiler de Equipos\n{equipos_info}"
    
    def validar_parametros(self, **kwargs) -> bool:
        """Valida los parámetros para alquiler de equipo"""
        duracion = kwargs.get("duracion")
        equipo = kwargs.get("equipo")
        cantidad = kwargs.get("cantidad", 1)
        
        if duracion and duracion <= 0:
            raise ServicioException("Duración inválida")
        
        if equipo and equipo.lower() not in self._equipos_disponibles:
            raise ServicioException(f"Equipo '{equipo}' no disponible")
        
        if cantidad and cantidad < 1:
            raise ServicioException("La cantidad debe ser al menos 1")
        
        return True
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        datos = super().to_dict()
        datos.update({
            "equipos": self.TARIFAS.copy()
        })
        return datos

class ServicioAsesoria(Servicio):
    """Servicio de asesorías especializadas"""
    
    TARIFAS_POR_TIPO = {
        "tecnologica": 80000,
        "legal": 120000,
        "contable": 100000,
        "recursos_humanos": 90000,
        "marketing": 85000
    }
    
    def __init__(self, id_servicio: int):
        super().__init__(
            id_servicio,
            "Asesorías Especializadas",
            "Asesorías profesionales en diferentes áreas"
        )
        self._tipos_asesoria = list(self.TARIFAS_POR_TIPO.keys())
    
    @property
    def tipos(self) -> List[str]:
        return self._tipos_asesoria.copy()
    
    def obtener_tarifa(self, tipo: str) -> float:
        """Obtiene la tarifa de un tipo de asesoría"""
        return self.TARIFAS_POR_TIPO.get(tipo.lower(), 0)
    
    # -------------------------------------------------------------------------
    # Métodos sobrescritos (polimorfismo)
    # -------------------------------------------------------------------------
    
    def calcular_costo(self, duracion: float, tipo: str = None,
                      nivel: str = "basico", impuestos: bool = True) -> float:
        """
        Método sobrecargado para calcular costo de asesoría
        
        Variantes:
        - calcular_costo(duracion) -> costo básico
        - calcular_costo(duracion, tipo) -> costo con tipo específico
        - calcular_costo(duracion, tipo, nivel, impuestos) -> costo completo
        """
        try:
            if duracion <= 0:
                raise ServicioException("La duración debe ser mayor a 0")
            
            if duracion > 8:
                raise ServicioException("La duración máxima es de 8 horas")
            
            costo = 0
            
            if tipo:
                # Costo de tipo específico
                tarifa = self.obtener_tarifa(tipo)
                if tarifa == 0:
                    raise ServicioException(f"Tipo de asesoría '{tipo}' no disponible")
                
                costo = duracion * tarifa
                
                # Aplicar nivel (recargo)
                if nivel == "intermedio":
                    costo *= 1.25
                elif nivel == "avanzado":
                    costo *= 1.50
            else:
                # Costo promedio
                tarifa_promedio = sum(self.TARIFAS_POR_TIPO.values()) / len(self.TARIFAS_POR_TIPO)
                costo = duracion * tarifa_promedio
            
            # Agregar impuestos (19% IVA)
            if impuestos:
                costo *= 1.19
            
            gestor_logs.info(f"Costo calculado para asesoría: ${costo:,.2f}")
            return costo
            
        except ServicioException as e:
            gestor_logs.error(f"Error al calcular costo de asesoría: {e}")
            raise
        except Exception as e:
            gestor_logs.error("Error inesperado calculando costo", e)
            raise ServicioException(f"Error al calcular costo: {str(e)}")
    
    def describir_servicio(self) -> str:
        """Describe el servicio de asesorías"""
        tipos_info = "\n".join([f"  - {tipo}: ${tar:,}/hora" 
                                for tipo, tar in self.TARIFAS_POR_TIPO.items()])
        return f"Asesorías Especializadas\n{tipos_info}\nNiveles: Básico, Intermedio, Avanzado"
    
    def validar_parametros(self, **kwargs) -> bool:
        """Valida los parámetros para asesoría"""
        duracion = kwargs.get("duracion")
        tipo = kwargs.get("tipo")
        nivel = kwargs.get("nivel", "basico")
        
        if duracion and (duracion <= 0 or duracion > 8):
            raise ServicioException("Duración inválida para asesoría")
        
        if tipo and tipo.lower() not in self._tipos_asesoria:
            raise ServicioException(f"Tipo de asesoría '{tipo}' no disponible")
        
        if nivel not in ["basico", "intermedio", "avanzado"]:
            raise ServicioException("Nivel inválido")
        
        return True
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        datos = super().to_dict()
        datos.update({
            "tipos": self.TARIFAS_POR_TIPO.copy()
        })
        return datos

entidades = {
    'ServicioReservaSala': ServicioReservaSala,
    'ServicioAlquilerEquipo': ServicioAlquilerEquipo,
    'ServicioAsesoria': ServicioAsesoria,
}

class Reserva:
    """Clase Reserva que integra cliente, servicio, duración y estado"""
    
    ESTADOS = ["pendiente", "confirmada", "cancelada", "completada"]
    
    def __init__(self, id_reserva: int, cliente: Cliente, servicio: Servicio,
                 duracion: float, descripcion: str = ""):
        self._id = id_reserva
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._descripcion = descripcion
        self._estado = "pendiente"
        self._costo_total = 0.0
        self._fecha_creacion = datetime.now()
        self._fecha_confirmacion: Optional[datetime] = None
        
        # Validar parámetros
        self._validar()
        
        # Asociar reserva al cliente
        cliente.agregar_reserva(id_reserva)
        
        gestor_logs.info(f"Reserva creada: {id_reserva} - Cliente: {cliente.id}")
    
    # -------------------------------------------------------------------------
    # Propiedades
    # -------------------------------------------------------------------------
    
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def cliente(self) -> Cliente:
        return self._cliente
    
    @property
    def servicio(self) -> Servicio:
        return self._servicio
    
    @property
    def duracion(self) -> float:
        return self._duracion
    
    @duracion.setter
    def duracion(self, valor: float):
        if valor <= 0:
            raise ReservaException("La duración debe ser mayor a 0")
        self._duracion = valor
    
    @property
    def descripcion(self) -> str:
        return self._descripcion
    
    @property
    def estado(self) -> str:
        return self._estado
    
    @property
    def costo_total(self) -> float:
        return self._costo_total
    
    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion
    
    @property
    def fecha_confirmacion(self) -> Optional[datetime]:
        return self._fecha_confirmacion
    
    # -------------------------------------------------------------------------
    # Métodos de procesamiento
    # -------------------------------------------------------------------------
    
    def _validar(self):
        """Valida los datos de la reserva"""
        try:
            if not self._cliente:
                raise ReservaException("El cliente es obligatorio")
            
            if not self._servicio:
                raise ReservaException("El servicio es obligatorio")
            
            if self._duracion <= 0:
                raise ReservaException("La duración debe ser mayor a 0")
            
            # Validar según tipo de servicio
            if isinstance(self._servicio, ServicioReservaSala):
                self._servicio.validar_parametros(duracion=self._duracion)
            elif isinstance(self._servicio, ServicioAlquilerEquipo):
                self._servicio.validar_parametros(duracion=self._duracion)
            elif isinstance(self._servicio, ServicioAsesoria):
                self._servicio.validar_parametros(duracion=self._duracion)
            
            return True
            
        except ReservaException as e:
            gestor_logs.error(f"Error de validación en reserva: {e}")
            raise
    
    def procesar(self, **kwargs) -> float:
        """
        Procesa la reserva calculando el costo total
        Manejo de excepciones con try/except/else/finally
        """
        costo = 0.0
        
        try:
            # Calcular según tipo de servicio
            if isinstance(self._servicio, ServicioReservaSala):
                sala = kwargs.get("sala")
                horas_extras = kwargs.get("horas_extras", 0)
                descuento = kwargs.get("descuento", 0)
                costo = self._servicio.calcular_costo(
                    self._duracion, sala, horas_extras, descuento
                )
                
            elif isinstance(self._servicio, ServicioAlquilerEquipo):
                equipo = kwargs.get("equipo")
                cantidad = kwargs.get("cantidad", 1)
                seguro = kwargs.get("seguro", False)
                costo = self._servicio.calcular_costo(
                    self._duracion, equipo, cantidad, seguro
                )
                
            elif isinstance(self._servicio, ServicioAsesoria):
                tipo = kwargs.get("tipo")
                nivel = kwargs.get("nivel", "basico")
                impuestos = kwargs.get("impuestos", True)
                costo = self._servicio.calcular_costo(
                    self._duracion, tipo, nivel, impuestos
                )
            
            self._costo_total = costo
            
        except ServicioException as e:
            # Encadenamiento de excepciones
            gestor_logs.error(f"Error procesando reserva: {e}")
            raise ReservaException(f"Error al procesar reserva: {str(e)}") from e
            
        except Exception as e:
            gestor_logs.error("Error inesperado procesando reserva", e)
            raise ReservaException(f"Error inesperado: {str(e)}") from e
            
        else:
            gestor_logs.info(f"Reserva {self._id} procesada exitosamente - Costo: ${costo:,.2f}")
            
        finally:
            # Siempre se ejecuta
            pass
        
        return costo
    
    def confirmar(self) -> bool:
        """
        Confirma la reserva
        Uso de try/except/finally
        """
        try:
            if self._estado != "pendiente":
                raise ReservaException(f"No se puede confirmar una reserva en estado '{self._estado}'")
            
            if self._costo_total == 0:
                raise ReservaException("La reserva debe ser procesada antes de confirmarse")
            
            self._estado = "confirmada"
            self._fecha_confirmacion = datetime.now()
            
            gestor_logs.info(f"Reserva {self._id} confirmada")
            return True
            
        except ReservaException as e:
            gestor_logs.error(f"Error al confirmar reserva: {e}")
            raise
        except Exception as e:
            gestor_logs.error("Error inesperado confirmando reserva", e)
            raise ReservaException(f"Error al confirmar: {str(e)}") from e
        finally:
            # Limpieza si es necesario
            pass
    
    def cancelar(self) -> bool:
        """
        Cancela la reserva
        """
        try:
            if self._estado == "cancelada":
                raise ReservaException("La reserva ya está cancelada")
            
            if self._estado == "completada":
                raise ReservaException("No se puede cancelar una reserva completada")
            
            self._estado = "cancelada"
            
            # Desasociar del cliente
            self._cliente.quitar_reserva(self._id)
            
            gestor_logs.info(f"Reserva {self._id} cancelada")
            return True
            
        except ReservaException as e:
            gestor_logs.error(f"Error al cancelar reserva: {e}")
            raise
        except Exception as e:
            gestor_logs.error("Error inesperado cancelando reserva", e)
            raise ReservaException(f"Error al cancelar: {str(e)}") from e
    
    def completar(self) -> bool:
        """
        Marca la reserva como completada
        """
        try:
            if self._estado != "confirmada":
                raise ReservaException("Solo se pueden completar reservas confirmadas")
            
            self._estado = "completada"
            gestor_logs.info(f"Reserva {self._id} completada")
            return True
            
        except ReservaException as e:
            gestor_logs.error(f"Error al completar reserva: {e}")
            raise
    
    def to_dict(self) -> dict:
        """Convierte la reserva a diccionario"""
        return {
            "id": self._id,
            "cliente_id": self._cliente.id,
            "servicio_id": self._servicio.id,
            "duracion": self._duracion,
            "descripcion": self._descripcion,
            "estado": self._estado,
            "costo_total": self._costo_total,
            "fecha_creacion": self._fecha_creacion.isoformat(),
            "fecha_confirmacion": self._fecha_confirmacion.isoformat() if self._fecha_confirmacion else None
        }
    
    def __str__(self):
        return (f"Reserva #{self._id} | Cliente: {self._cliente.nombre} {self._cliente.apellido} | "
                f"Servicio: {self._servicio.nombre} | Estado: {self._estado} | "
                f"Costo: ${self._costo_total:,.2f}")

