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
