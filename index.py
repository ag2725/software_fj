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

