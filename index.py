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
import json, os
import tkinter as tk
from tkinter import ttk, messagebox

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
    
    def __init__(self, id: int, nombre: str, descripcion: str, capacidad: int, precio: int, activo: bool, tipo: str):
        self._id = id
        self._nombre = nombre
        self._descripcion = descripcion
        self._activo = activo
        self._tipo = tipo
        self._capacidad = capacidad
        self._precio = precio
    
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
            "capacidad": self._capacidad,
            "precio": self._precio,
            "activo": self._activo,
            "tipo": self.__class__.__name__
        }
    
    def __repr__(self):
        return f"Servicio(id={self._id}, nombre='{self._nombre}')"

class ServicioReservaSala(Servicio):
    """Servicio de reservas de salas"""
    
    TARIFA_POR_HORA = 50000  # Tarifa base por hora
    
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
        return datos

class ServicioAlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos"""
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
        return datos

class ServicioAsesoria(Servicio):
    """Servicio de asesorías especializadas"""    
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

class SistemaSoftwareFJ:
    """Sistema principal que gestiona clientes, servicios y reservas"""
    
    def __init__(self):
        self._clientes: Dict[int, Cliente] = {}
        self._servicios: Dict[int, Servicio] = {}
        self._reservas: Dict[int, Reserva] = {}
        self._next_id_cliente = 1
        self._next_id_servicio = 1
        self._next_id_reserva = 1
        
        # Inicializar servicios disponibles
        self._inicializar_servicios()
        
        gestor_logs.info("Sistema SoftwareFJ inicializado")
    
    def _inicializar_servicios(self):
        """Inicializa los servicios del sistema"""
        try:            
            self._next_id_servicio = 4
            
            gestor_logs.info("Servicios inicializados correctamente")
            
        except Exception as e:
            gestor_logs.error("Error inicializando servicios", e)
            raise
    
    def crear_cliente(self, nombre: str, apellido: str, identificacion: str,
                     telefono: str, email: str) -> Cliente:
        """Crea un nuevo cliente"""
        try:
            # Verificar identificación única
            for cliente in self._clientes.values():
                if cliente.identificacion == identificacion:
                    raise ClienteException(f"Ya existe un cliente con identificación '{identificacion}'")
            
            cliente = Cliente(
                self._next_id_cliente,
                nombre, apellido, identificacion, telefono, email
            )
            
            self._clientes[self._next_id_cliente] = cliente
            self._next_id_cliente += 1
            
            return cliente
            
        except (ValidacionException, ClienteException) as e:
            gestor_logs.error(f"Error creando cliente: {e}")
            raise
        except Exception as e:
            gestor_logs.error("Error inesperado creando cliente", e)
            raise ClienteException(f"Error al crear cliente: {str(e)}") from e
    
    def obtener_cliente(self, id_cliente: int) -> Optional[Cliente]:
        """Obtiene un cliente por su ID"""
        return self._clientes.get(id_cliente)
    
    def listar_clientes(self) -> List[Cliente]:
        """Lista todos los clientes"""
        return list(self._clientes.values())
    
    def actualizar_cliente(self, id_cliente: int, **kwargs) -> Cliente:
        """Actualiza los datos de un cliente"""
        try:
            cliente = self.obtener_cliente(id_cliente)
            if not cliente:
                raise ClienteException(f"No existe cliente con ID {id_cliente}")
            
            # Actualizar campos proporcionados
            if "nombre" in kwargs:
                cliente.nombre = kwargs["nombre"]
            if "apellido" in kwargs:
                cliente.apellido = kwargs["apellido"]
            if "telefono" in kwargs:
                cliente.telefono = kwargs["telefono"]
            if "email" in kwargs:
                cliente.email = kwargs["email"]
            
            gestor_logs.info(f"Cliente {id_cliente} actualizado")
            return cliente
            
        except (ValidacionException, ClienteException) as e:
            gestor_logs.error(f"Error actualizando cliente: {e}")
            raise
    
    def eliminar_cliente(self, id_cliente: int) -> bool:
        """Elimina (desactiva) un cliente"""
        try:
            cliente = self.obtener_cliente(id_cliente)
            if not cliente:
                raise ClienteException(f"No existe cliente con ID {id_cliente}")
            
            # Verificar que no tenga reservas
            if cliente.reservas:
                raise ClienteException("No se puede eliminar un cliente con reservas.")
            
            cliente.activo = False
            gestor_logs.info(f"Cliente {id_cliente} eliminado")
            return True
            
        except ClienteException as e:
            gestor_logs.error(f"Error eliminando cliente: {e}")
            raise
    
    def obtener_servicio(self, id_servicio: int) -> Optional[Servicio]:
        """Obtiene un servicio por su ID"""
        return self._servicios.get(id_servicio)
    
    def listar_servicios(self) -> List[Servicio]:
        """Lista todos los servicios"""
        return list(self._servicios.values())
    
    def crear_reserva(self, id_cliente: int, id_servicio: int,
                     duracion: float, descripcion: str = "", **kwargs) -> Reserva:
        """Crea una nueva reserva"""
        try:
            # Obtener cliente
            cliente = self.obtener_cliente(id_cliente)
            if not cliente:
                raise ReservaException(f"No existe cliente con ID {id_cliente}")
            
            if not cliente.activo:
                raise ReservaException("El cliente está inactivo")
            
            # Obtener servicio
            servicio = self.obtener_servicio(id_servicio)
            if not servicio:
                raise ReservaException(f"No existe servicio con ID {id_servicio}")
            
            if not servicio.activo:
                raise ReservaException("El servicio está inactivo")
            
            # Crear reserva
            reserva = Reserva(
                self._next_id_reserva,
                cliente, servicio, duracion, descripcion
            )
            
            # Procesar reserva con parámetros adicionales
            reserva.procesar(**kwargs)
            
            self._reservas[self._next_id_reserva] = reserva
            self._next_id_reserva += 1
            
            return reserva
            
        except (ReservaException, ServicioException) as e:
            gestor_logs.error(f"Error creando reserva: {e}")
            raise
        except Exception as e:
            gestor_logs.error("Error inesperado creando reserva", e)
            raise ReservaException(f"Error al crear reserva: {str(e)}") from e
    
    def obtener_reserva(self, id_reserva: int) -> Optional[Reserva]:
        """Obtiene una reserva por su ID"""
        return self._reservas.get(id_reserva)
    
    def listar_reservas(self) -> List[Reserva]:
        """Lista todas las reservas"""
        return list(self._reservas.values())
    
    def confirmar_reserva(self, id_reserva: int) -> bool:
        """Confirma una reserva"""
        try:
            reserva = self.obtener_reserva(id_reserva)
            if not reserva:
                raise ReservaException(f"No existe reserva con ID {id_reserva}")
            
            return reserva.confirmar()
            
        except ReservaException as e:
            gestor_logs.error(f"Error confirmando reserva: {e}")
            raise
    
    def cancelar_reserva(self, id_reserva: int) -> bool:
        """Cancela una reserva"""
        try:
            reserva = self.obtener_reserva(id_reserva)
            if not reserva:
                raise ReservaException(f"No existe reserva con ID {id_reserva}")
            
            return reserva.cancelar()
            
        except ReservaException as e:
            gestor_logs.error(f"Error cancelando reserva: {e}")
            raise
    
    def completar_reserva(self, id_reserva: int) -> bool:
        """Completa una reserva"""
        try:
            reserva = self.obtener_reserva(id_reserva)
            if not reserva:
                raise ReservaException(f"No existe reserva con ID {id_reserva}")
            
            return reserva.completar()
            
        except ReservaException as e:
            gestor_logs.error(f"Error completando reserva: {e}")
            raise
    
    def guardar_datos(self, archivo: str = "software_fj_data.json"):
        """Guarda todos los datos en un archivo JSON"""
        try:
            self._next_id_cliente = max(self._next_id_cliente, max(self._clientes.keys(), default=0) + 1)
            self._next_id_servicio = max(self._next_id_servicio, max(self._servicios.keys(), default=0) + 1)
            self._next_id_reserva = max(self._next_id_reserva, max(self._reservas.keys(), default=0) + 1)

            datos = {
                "clientes": [c.to_dict() for c in self._clientes.values()],
                "servicios": [s.to_dict() for s in self._servicios.values()],
                "reservas": [r.to_dict() for r in self._reservas.values()],
                "next_ids": {
                    "cliente": self._next_id_cliente,
                    "servicio": self._next_id_servicio,
                    "reserva": self._next_id_reserva
                }
            }
            
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            
            gestor_logs.info(f"Datos guardados en {archivo}")
            return True
            
        except Exception as e:
            gestor_logs.error("Error guardando datos", e)
            raise DatosException(f"Error al guardar datos: {str(e)}") from e
    
    def cargar_datos(self, archivo: str = "software_fj_data.json"):
        """Carga los datos desde un archivo JSON"""
        try:
            if not os.path.exists(archivo):
                gestor_logs.info(f"El archivo {archivo} no existe, se creará uno nuevo")
                return False
            
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Cargar clientes
            self._clientes = {}
            for c in datos.get("clientes", []):
                cliente = Cliente.from_dict(c)
                self._clientes[cliente.id] = cliente
            
            self._servicios = {}
            servicios_data = datos.get("servicios", [])
            if isinstance(servicios_data, dict):
                servicios_data = list(servicios_data.values())
            servicios_data = servicios_data if len(servicios_data) else [
                {
                    "id": 1,
                    "nombre": "Sala A",
                    "descripcion": "Sala de reuniones con capacidad para 20 personas",
                    "capacidad": 20,
                    "precio": 50000,
                    "activo": True,
                    "tipo": "ServicioReservaSala",
                },
                {
                    "id": 2,
                    "nombre": "Sala B",
                    "descripcion": "Sala de reuniones con capacidad para 20 personas",
                    "capacidad": 20,
                    "precio": 50000,
                    "activo": True,
                    "tipo": "ServicioReservaSala",
                },
                {
                    "id": 3,
                    "nombre": "Sala C",
                    "descripcion": "Sala de reuniones con capacidad para 20 personas",
                    "capacidad": 20,
                    "precio": 50000,
                    "activo": True,
                    "tipo": "ServicioReservaSala",
                },
                {
                    "id": 4,
                    "nombre": "PC GAMING",
                    "descripcion": "24 nucleos, 128GB RAM, RTX 4090",
                    "capacidad": 0,
                    "precio": 150000,
                    "activo": True,
                    "tipo": "ServicioAlquilerEquipo",
                },
                {
                    "id": 5,
                    "nombre": "Asesoria Tecnologica",
                    "descripcion": "Asesoria tecnologica",
                    "capacidad": 10,
                    "precio": 150000,
                    "activo": True,
                    "tipo": "ServicioAsesoria",
                },
                # Nuevos equipos
                {
                    "id": 6,
                    "nombre": "Workstation Diseño",
                    "descripcion": "Intel Xeon, 64GB RAM, Quadro RTX",
                    "capacidad": 0,
                    "precio": 120000,
                    "activo": True,
                    "tipo": "ServicioAlquilerEquipo",
                },
                {
                    "id": 7,
                    "nombre": "Servidor Virtual",
                    "descripcion": "Servidor dedicado con 32 cores y 256GB RAM",
                    "capacidad": 0,
                    "precio": 200000,
                    "activo": True,
                    "tipo": "ServicioAlquilerEquipo",
                },
                {
                    "id": 8,
                    "nombre": "Laptop Ultrabook",
                    "descripcion": "Core i7, 16GB RAM, SSD 1TB",
                    "capacidad": 0,
                    "precio": 80000,
                    "activo": True,
                    "tipo": "ServicioAlquilerEquipo",
                },
                {
                    "id": 9,
                    "nombre": "Equipo VR",
                    "descripcion": "Set completo Oculus Quest Pro",
                    "capacidad": 0,
                    "precio": 100000,
                    "activo": True,
                    "tipo": "ServicioAlquilerEquipo",
                },
                {
                    "id": 10,
                    "nombre": "Impresora 3D",
                    "descripcion": "Impresora 3D industrial para prototipado",
                    "capacidad": 0,
                    "precio": 130000,
                    "activo": True,
                    "tipo": "ServicioAlquilerEquipo",
                },
                # Asesorías adicionales según TARIFAS_POR_TIPO
                {
                    "id": 11,
                    "nombre": "Asesoria Legal",
                    "descripcion": "Consultoría legal especializada",
                    "capacidad": 5,
                    "precio": 120000,
                    "activo": True,
                    "tipo": "ServicioAsesoria",
                },
                {
                    "id": 12,
                    "nombre": "Asesoria Contable",
                    "descripcion": "Consultoría en gestión contable y tributaria",
                    "capacidad": 5,
                    "precio": 100000,
                    "activo": True,
                    "tipo": "ServicioAsesoria",
                },
                {
                    "id": 13,
                    "nombre": "Asesoria en Recursos Humanos",
                    "descripcion": "Consultoría en gestión de talento humano",
                    "capacidad": 5,
                    "precio": 90000,
                    "activo": True,
                    "tipo": "ServicioAsesoria",
                },
                {
                    "id": 14,
                    "nombre": "Asesoria en Marketing",
                    "descripcion": "Consultoría en estrategias de marketing digital",
                    "capacidad": 5,
                    "precio": 85000,
                    "activo": True,
                    "tipo": "ServicioAsesoria",
                },
            ]
            for s in servicios_data:
                constructor = entidades.get(s.get("tipo"))
                if not constructor:
                    continue
                servicio = constructor(**s)
                self._servicios[servicio.id] = servicio
            print(f"Servicios: {self._servicios}")

            # Cargar reservas (requiere reconstruir referencias)
            self._reservas = {}
            for r in datos.get("reservas", []):
                cliente = self.obtener_cliente(r["cliente_id"])
                servicio = self.obtener_servicio(r["servicio_id"])
                
                if cliente and servicio:
                    reserva = Reserva(
                        r["id"], cliente, servicio,
                        r["duracion"], r.get("descripcion", "")
                    )
                    reserva._estado = r.get("estado", "pendiente")
                    reserva._costo_total = r.get("costo_total", 0)
                    self._reservas[r["id"]] = reserva
            
            # Restaurar IDs
            ids = datos.get("next_ids", {})
            self._next_id_cliente = max(max(self._clientes.keys(), default=0) + 1,
                                        ids.get("cliente", 1))
            self._next_id_servicio = max(max(self._servicios.keys(), default=0) + 1,
                                         ids.get("servicio", 1))
            self._next_id_reserva = max(max(self._reservas.keys(), default=0) + 1,
                                        ids.get("reserva", 1))
            
            gestor_logs.info(f"Datos cargados desde {archivo}")
            return True
            
        except Exception as e:
            gestor_logs.error("Error cargando datos", e)
            raise DatosException(f"Error al cargar datos: {str(e)}") from e

class InterfazSoftwareFJ:
    """Interfaz gráfica del sistema usando Tkinter"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Sistema de Gestión")
        self.root.geometry("1000x700")
        
        # Sistema backend
        self.sistema = SistemaSoftwareFJ()
        
        # Cargar datos existentes
        try:
            self.sistema.cargar_datos()
        except:
            pass
        
        # Configurar interfaz
        self.configurar_interfaz()
        
        # Cargar datos iniciales
        self.actualizar_vistas()
    
    def configurar_interfaz(self):
        """
        Configura los elementos de la interfaz
        """
        
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestañas
        self.crear_pestana_clientes()
        self.crear_pestana_servicios()
        self.crear_pestana_reservas()
        
        # Barra de estado
        self.estado = ttk.Label(self.root, text="Sistema listo", relief=tk.SUNKEN, anchor=tk.W)
        self.estado.pack(fill=tk.X)
    
    def crear_pestana_clientes(self):
        """Crea la pestaña de clientes"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Clientes")
        
        # Frame de formulario
        form_frame = ttk.LabelFrame(frame, text="Datos del Cliente", padding="10")
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Campos
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_nombre = ttk.Entry(form_frame, width=30)
        self.entry_nombre.grid(row=0, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Apellido:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_apellido = ttk.Entry(form_frame, width=30)
        self.entry_apellido.grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Identificación:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_identificacion = ttk.Entry(form_frame, width=30)
        self.entry_identificacion.grid(row=2, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Teléfono:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.entry_telefono = ttk.Entry(form_frame, width=30)
        self.entry_telefono.grid(row=3, column=1, pady=2, padx=5)
        
        ttk.Label(form_frame, text="Email:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.entry_email = ttk.Entry(form_frame, width=30)
        self.entry_email.grid(row=4, column=1, pady=2, padx=5)
        
        # Botones
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Agregar Cliente", command=self.agregar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.editar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.eliminar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario_cliente).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree_clientes = ttk.Treeview(tree_frame, columns=("ID", "Nombre", "Apellido", "Identificación", "Teléfono", "Email"), show="headings")
        for col in ("ID", "Nombre", "Apellido", "Identificación", "Teléfono", "Email"):
            self.tree_clientes.heading(col, text=col)
            self.tree_clientes.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscrollcommand=scrollbar.set)
        self.tree_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def crear_pestana_servicios(self):
        """Crea la pestaña de servicios"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Servicios")

        # Frame de tabla de servicios
        table_frame = ttk.LabelFrame(frame, text="Elementos de Servicios", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview para mostrar servicios en tabla
        self.tree_servicios = ttk.Treeview(table_frame, columns=("Tipo", "Elemento", "Precio/Hora"), show="headings")
        self.tree_servicios.heading("Tipo", text="Tipo de Servicio")
        self.tree_servicios.heading("Elemento", text="Elemento")
        self.tree_servicios.heading("Precio/Hora", text="Precio/Hora")
        
        self.tree_servicios.column("Tipo", width=200)
        self.tree_servicios.column("Elemento", width=150)
        self.tree_servicios.column("Precio/Hora", width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_servicios.yview)
        self.tree_servicios.configure(yscrollcommand=scrollbar.set)
        self.tree_servicios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botones de acción
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_frame, text="Editar", command=self.editar_servicio).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar", command=self.eliminar_servicio).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Actualizar", command=self.actualizar_vista_servicios).pack(side=tk.LEFT, padx=5)
    
    def crear_pestana_reservas(self):
        """Crea la pestaña de reservas"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Reservas")
        
        # Frame de formulario
        form_frame = ttk.LabelFrame(frame, text="Nueva Reserva", padding="10")
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Cliente
        ttk.Label(form_frame, text="Cliente:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.combo_cliente = ttk.Combobox(form_frame, width=28)
        self.combo_cliente.grid(row=0, column=1, pady=2, padx=5)
        
        # Servicio
        ttk.Label(form_frame, text="Servicio:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.combo_servicio = ttk.Combobox(form_frame, width=28)
        self.combo_servicio.grid(row=1, column=1, pady=2, padx=5)
        
        # Duración
        ttk.Label(form_frame, text="Duración (horas):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_duracion = ttk.Entry(form_frame, width=30)
        self.entry_duracion.grid(row=2, column=1, pady=2, padx=5)
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.entry_descripcion = ttk.Entry(form_frame, width=30)
        self.entry_descripcion.grid(row=3, column=1, pady=2, padx=5)
        
        # Botones
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Crear Reserva", command=self.crear_reserva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Confirmar", command=self.confirmar_reserva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar_reserva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Completar", command=self.completar_reserva).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Editar", command=self.editar_reserva).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree_reservas = ttk.Treeview(tree_frame, columns=("ID", "Cliente", "Servicio", "Duración", "Estado", "Costo"), show="headings")
        for col in ("ID", "Cliente", "Servicio", "Duración", "Estado", "Costo"):
            self.tree_reservas.heading(col, text=col)
            self.tree_reservas.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_reservas.yview)
        self.tree_reservas.configure(yscrollcommand=scrollbar.set)
        self.tree_reservas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # -------------------------------------------------------------------------
    # Métodos de acción
    # -------------------------------------------------------------------------
    
    def agregar_cliente(self):
        """Agrega un nuevo cliente"""
        try:
            cliente = self.sistema.crear_cliente(
                self.entry_nombre.get(),
                self.entry_apellido.get(),
                self.entry_identificacion.get(),
                self.entry_telefono.get(),
                self.entry_email.get()
            )
            self.actualizar_vistas()
            self.limpiar_formulario_cliente()
            self.guardar_datos()  # Guardar automáticamente en JSON
            self.actualizar_estado(f"Cliente '{cliente.nombre} {cliente.apellido}' creado exitosamente")
            messagebox.showinfo("Éxito", f"Cliente creado con ID: {cliente.id}")
            
        except (ValidacionException, ClienteException) as e:
            messagebox.showerror("Error", str(e))
            self.actualizar_estado(f"Error: {str(e)}")
    
    def limpiar_formulario_cliente(self):
        """Limpia el formulario de cliente"""
        self.entry_nombre.delete(0, tk.END)
        self.entry_apellido.delete(0, tk.END)
        self.entry_identificacion.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
    
    def editar_cliente(self):
        """Edita el cliente seleccionado"""
        try:
            seleccion = self.tree_clientes.selection()
            if not seleccion:
                raise ClienteException("Seleccione un cliente")
            
            item = self.tree_clientes.item(seleccion[0])
            id_cliente = int(item["values"][0])
            
            cliente = self.sistema.obtener_cliente(id_cliente)
            if not cliente:
                raise ClienteException("Cliente no encontrado")
            
            # Crear diálogo para editar
            dialog = tk.Toplevel(self.root)
            dialog.title("Editar Cliente")
            dialog.geometry("400x350")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Frame del formulario
            form_frame = ttk.Frame(dialog, padding="20")
            form_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=5)
            entry_nombre = ttk.Entry(form_frame, width=25)
            entry_nombre.grid(row=0, column=1, pady=5, padx=5)
            entry_nombre.insert(0, cliente.nombre)
            
            ttk.Label(form_frame, text="Apellido:").grid(row=1, column=0, sticky=tk.W, pady=5)
            entry_apellido = ttk.Entry(form_frame, width=25)
            entry_apellido.grid(row=1, column=1, pady=5, padx=5)
            entry_apellido.insert(0, cliente.apellido)
            
            ttk.Label(form_frame, text="Teléfono:").grid(row=2, column=0, sticky=tk.W, pady=5)
            entry_telefono = ttk.Entry(form_frame, width=25)
            entry_telefono.grid(row=2, column=1, pady=5, padx=5)
            entry_telefono.insert(0, cliente.telefono)
            
            ttk.Label(form_frame, text="Email:").grid(row=3, column=0, sticky=tk.W, pady=5)
            entry_email = ttk.Entry(form_frame, width=25)
            entry_email.grid(row=3, column=1, pady=5, padx=5)
            entry_email.insert(0, cliente.email)
            
            ttk.Label(form_frame, text="Identificación:").grid(row=4, column=0, sticky=tk.W, pady=5)
            ttk.Label(form_frame, text=cliente.identificacion).grid(row=4, column=1, sticky=tk.W, pady=5)
            
            def guardar_cambio():
                try:
                    self.sistema.actualizar_cliente(
                        id_cliente,
                        nombre=entry_nombre.get(),
                        apellido=entry_apellido.get(),
                        telefono=entry_telefono.get(),
                        email=entry_email.get()
                    )
                    self.actualizar_vista_clientes()
                    self.guardar_datos()  # Guardar automáticamente en JSON
                    self.actualizar_estado(f"Cliente {id_cliente} actualizado")
                    messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
                    dialog.destroy()
                    
                except (ValidacionException, ClienteException) as e:
                    messagebox.showerror("Error", str(e))
            
            btn_frame = ttk.Frame(form_frame)
            btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
            ttk.Button(btn_frame, text="Guardar", command=guardar_cambio).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
        except ClienteException as e:
            messagebox.showerror("Error", str(e))
    
    def eliminar_cliente(self):
        """Elimina el cliente seleccionado"""
        try:
            seleccion = self.tree_clientes.selection()
            if not seleccion:
                raise ClienteException("Seleccione un cliente")
            
            item = self.tree_clientes.item(seleccion[0])
            id_cliente = int(item["values"][0])
            nombre = item["values"][1]
            apellido = item["values"][2]
            
            respuesta = messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Está seguro de eliminar al cliente {nombre} {apellido}?"
            )
            
            if respuesta:
                self.sistema.eliminar_cliente(id_cliente)
                self.actualizar_vista_clientes()
                self.guardar_datos()  # Guardar automáticamente en JSON
                self.actualizar_estado(f"Cliente {id_cliente} eliminado")
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                
        except ClienteException as e:
            messagebox.showerror("Error", str(e))
    
    def crear_reserva(self):
        """Crea una nueva reserva"""
        try:
            # Obtener IDs seleccionados
            cliente_texto = self.combo_cliente.get()
            servicio_texto = self.combo_servicio.get()
            
            if not cliente_texto or not servicio_texto:
                raise ReservaException("Debe seleccionar cliente y servicio")
            
            id_cliente = int(cliente_texto.split("-")[0].strip())
            id_servicio = int(servicio_texto.split("-")[0].strip())
            duracion = float(self.entry_duracion.get())
            descripcion = self.entry_descripcion.get()
            
            reserva = self.sistema.crear_reserva(
                id_cliente, id_servicio, duracion, descripcion
            )
            
            self.actualizar_vistas()
            self.guardar_datos()  # Guardar automáticamente en JSON
            self.actualizar_estado(f"Reserva #{reserva.id} creada - Costo: ${reserva.costo_total:,.2f}")
            messagebox.showinfo("Éxito", f"Reserva creada con ID: {reserva.id}\nCosto: ${reserva.costo_total:,.2f}")
            
        except (ReservaException, ValueError) as e:
            messagebox.showerror("Error", str(e))
            self.actualizar_estado(f"Error: {str(e)}")
    
    def confirmar_reserva(self):
        """Confirma la reserva seleccionada"""
        try:
            seleccion = self.tree_reservas.selection()
            if not seleccion:
                raise ReservaException("Seleccione una reserva")
            
            item = self.tree_reservas.item(seleccion[0])
            id_reserva = int(item["values"][0])
            
            self.sistema.confirmar_reserva(id_reserva)
            self.actualizar_vistas()
            self.guardar_datos()  # Guardar automáticamente en JSON
            self.actualizar_estado(f"Reserva #{id_reserva} confirmada")
            messagebox.showinfo("Éxito", "Reserva confirmada")
            
        except ReservaException as e:
            messagebox.showerror("Error", str(e))
    
    def cancelar_reserva(self):
        """Cancela la reserva seleccionada"""
        try:
            seleccion = self.tree_reservas.selection()
            if not seleccion:
                raise ReservaException("Seleccione una reserva")
            
            item = self.tree_reservas.item(seleccion[0])
            id_reserva = int(item["values"][0])
            
            self.sistema.cancelar_reserva(id_reserva)
            self.actualizar_vistas()
            self.guardar_datos()  # Guardar automáticamente en JSON
            self.actualizar_estado(f"Reserva #{id_reserva} cancelada")
            messagebox.showinfo("Éxito", "Reserva cancelada")
            
        except ReservaException as e:
            messagebox.showerror("Error", str(e))
    
    def completar_reserva(self):
        """Completa la reserva seleccionada"""
        try:
            seleccion = self.tree_reservas.selection()
            if not seleccion:
                raise ReservaException("Seleccione una reserva")
            
            item = self.tree_reservas.item(seleccion[0])
            id_reserva = int(item["values"][0])
            
            self.sistema.completar_reserva(id_reserva)
            self.actualizar_vistas()
            self.guardar_datos()  # Guardar automáticamente en JSON
            self.actualizar_estado(f"Reserva #{id_reserva} completada")
            messagebox.showinfo("Éxito", "Reserva completada")
            
        except ReservaException as e:
            messagebox.showerror("Error", str(e))
    
    def editar_reserva(self):
        """Edita la reserva seleccionada"""
        try:
            seleccion = self.tree_reservas.selection()
            if not seleccion:
                raise ReservaException("Seleccione una reserva")
            
            item = self.tree_reservas.item(seleccion[0])
            id_reserva = int(item["values"][0])
            
            reserva = self.sistema.obtener_reserva(id_reserva)
            if not reserva:
                raise ReservaException("Reserva no encontrada")
            
            # Crear diálogo para editar
            dialog = tk.Toplevel(self.root)
            dialog.title("Editar Reserva")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Frame del formulario
            form_frame = ttk.Frame(dialog, padding="20")
            form_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(form_frame, text="Cliente:").grid(row=0, column=0, sticky=tk.W, pady=5)
            ttk.Label(form_frame, text=f"{reserva.cliente.nombre} {reserva.cliente.apellido}").grid(row=0, column=1, sticky=tk.W, pady=5)
            
            ttk.Label(form_frame, text="Servicio:").grid(row=1, column=0, sticky=tk.W, pady=5)
            ttk.Label(form_frame, text=reserva.servicio.nombre).grid(row=1, column=1, sticky=tk.W, pady=5)
            
            ttk.Label(form_frame, text="Duración (horas):").grid(row=2, column=0, sticky=tk.W, pady=5)
            entry_duracion = ttk.Entry(form_frame, width=25)
            entry_duracion.grid(row=2, column=1, pady=5, padx=5)
            entry_duracion.insert(0, str(reserva.duracion))
            
            ttk.Label(form_frame, text="Descripción:").grid(row=3, column=0, sticky=tk.W, pady=5)
            entry_descripcion = ttk.Entry(form_frame, width=25)
            entry_descripcion.grid(row=3, column=1, pady=5, padx=5)
            entry_descripcion.insert(0, reserva.descripcion)
            
            ttk.Label(form_frame, text="Estado actual:").grid(row=4, column=0, sticky=tk.W, pady=5)
            ttk.Label(form_frame, text=reserva.estado).grid(row=4, column=1, sticky=tk.W, pady=5)
            
            def guardar_cambio():
                try:
                    reserva.duracion = float(entry_duracion.get())
                    reserva._descripcion = entry_descripcion.get()
                    # Reprocesar el costo
                    reserva.procesar()
                    self.actualizar_vista_reservas()
                    self.guardar_datos()  # Guardar automáticamente en JSON
                    self.actualizar_estado(f"Reserva {id_reserva} actualizada")
                    messagebox.showinfo("Éxito", "Reserva actualizada correctamente")
                    dialog.destroy()
                    
                except (ReservaException, ValueError) as e:
                    messagebox.showerror("Error", str(e))
            
            btn_frame = ttk.Frame(form_frame)
            btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
            ttk.Button(btn_frame, text="Guardar", command=guardar_cambio).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
        except ReservaException as e:
            messagebox.showerror("Error", str(e))
    
    def guardar_datos(self, mostrar_mensaje: bool = False):
        """Guarda los datos en JSON"""
        try:
            self.sistema.guardar_datos()
            if mostrar_mensaje:
                self.actualizar_estado("Datos guardados exitosamente")
                messagebox.showinfo("Éxito", "Datos guardados en software_fj_data.json")
        except DatosException as e:
            if mostrar_mensaje:
                messagebox.showerror("Error", str(e))
    
    def actualizar_vistas(self):
        """Actualiza todas las vistas"""
        self.actualizar_vista_clientes()
        self.actualizar_vista_servicios()
        self.actualizar_vista_reservas()
    
    def actualizar_vista_clientes(self):
        """Actualiza la vista de clientes"""
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        for cliente in self.sistema.listar_clientes():
            if cliente.activo:
                self.tree_clientes.insert("", tk.END, values=(
                    cliente.id,
                    cliente.nombre,
                    cliente.apellido,
                    cliente.identificacion,
                    cliente.telefono,
                    cliente.email
                ))
        
        # Actualizar combobox
        clientes = [f"{c.id} - {c.nombre} {c.apellido}" for c in self.sistema.listar_clientes() if c.activo]
        self.combo_cliente["values"] = clientes
    
    def actualizar_vista_servicios(self):
        """Actualiza la vista de servicios con tabla organizada por tipo y precio"""
        # Limpiar tabla
        for item in self.tree_servicios.get_children():
            self.tree_servicios.delete(item)
        
        
        # Recolectar todos los elementos de servicios
        elementos = []
        
        for servicio in self.sistema.listar_servicios():
            s = servicio.to_dict()
            s['elemento'] = s.pop('nombre')  # Para mostrar el nombre del servicio como elemento
            elementos.append(s)
        # Ordenar por tipo y luego por precio
        elementos.sort(key=lambda x: (x["tipo"], x["precio"]))
        
        # Insertar en la tabla (solo los no eliminados)
        for elem in elementos:
            if elem["precio"] > 0:  # No mostrar elementos eliminados
                self.tree_servicios.insert("", tk.END, values=(
                    elem["tipo"],
                    elem["elemento"],
                    f"${elem['precio']:,.0f}"
                ))
        
        # Actualizar combobox de servicios para reservas
        servicios = [f"{s.id} - {s.nombre}" for s in self.sistema.listar_servicios() if s.activo]
        self.combo_servicio["values"] = servicios
    
    def editar_servicio(self):
        """Edita el servicio seleccionado"""
        try:
            seleccion = self.tree_servicios.selection()
            if not seleccion:
                raise ReservaException("Seleccione un elemento de servicio")
            
            item = self.tree_servicios.item(seleccion[0])
            tipo = item["values"][0]
            elemento = item["values"][1]
            precio_actual = item["values"][2]
            
            # Crear diálogo para editar
            dialog = tk.Toplevel(self.root)
            dialog.title("Editar Servicio")
            dialog.geometry("400x250")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Frame del formulario
            form_frame = ttk.Frame(dialog, padding="20")
            form_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(form_frame, text="Tipo:").grid(row=0, column=0, sticky=tk.W, pady=5)
            ttk.Label(form_frame, text=tipo).grid(row=0, column=1, sticky=tk.W, pady=5)
            
            ttk.Label(form_frame, text="Elemento:").grid(row=1, column=0, sticky=tk.W, pady=5)
            ttk.Label(form_frame, text=elemento).grid(row=1, column=1, sticky=tk.W, pady=5)
            
            ttk.Label(form_frame, text="Nuevo Precio:").grid(row=2, column=0, sticky=tk.W, pady=5)
            entry_precio = ttk.Entry(form_frame, width=20)
            entry_precio.grid(row=2, column=1, sticky=tk.W, pady=5)
            entry_precio.insert(0, precio_actual.replace("$", "").replace(",", ""))
            
            def guardar_cambio():
                try:
                    nuevo_precio = float(entry_precio.get())
                    
                    # Actualizar según el tipo
                    for servicio in self.sistema.listar_servicios():
                        if tipo == "Reserva de Sala":
                            if isinstance(servicio, ServicioReservaSala):
                                if elemento == "Sala A":
                                    servicio.TARIFA_POR_HORA = int(nuevo_precio / 1.2)
                                elif elemento == "Sala VIP":
                                    servicio.TARIFA_POR_HORA = int(nuevo_precio / 1.5)
                                else:
                                    servicio.TARIFA_POR_HORA = int(nuevo_precio)
                        elif tipo == "Alquiler de Equipos":
                            if isinstance(servicio, ServicioAlquilerEquipo):
                                clave = elemento.lower().replace(" ", "_")
                                servicio.TARIFAS[clave] = nuevo_precio
                        elif tipo == "Asesorías Especializadas":
                            if isinstance(servicio, ServicioAsesoria):
                                clave = elemento.lower().replace(" ", "_")
                                servicio.TARIFAS_POR_TIPO[clave] = nuevo_precio
                    
                    self.actualizar_vista_servicios()
                    self.guardar_datos()  # Guardar automáticamente en JSON
                    self.actualizar_estado(f"Precio de {elemento} actualizado a ${nuevo_precio:,.0f}")
                    messagebox.showinfo("Éxito", "Precio actualizado correctamente")
                    dialog.destroy()
                    
                except ValueError:
                    messagebox.showerror("Error", "Ingrese un precio válido")
            
            btn_frame = ttk.Frame(form_frame)
            btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
            ttk.Button(btn_frame, text="Guardar", command=guardar_cambio).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
            
        except ReservaException as e:
            messagebox.showerror("Error", str(e))
    
    def eliminar_servicio(self):
        """Elimina (desactiva) el servicio seleccionado"""
        try:
            seleccion = self.tree_servicios.selection()
            if not seleccion:
                raise ReservaException("Seleccione un elemento de servicio")
            
            item = self.tree_servicios.item(seleccion[0])
            tipo = item["values"][0]
            elemento = item["values"][1]
            
            respuesta = messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Está seguro de eliminar '{elemento}' del tipo '{tipo}'?"
            )
            
            if respuesta:
                # Desactivar el elemento según el tipo
                for servicio in self.sistema.listar_servicios():
                    if tipo == "Reserva de Sala":
                        if isinstance(servicio, ServicioReservaSala):
                            if elemento in servicio._salas_disponibles:
                                servicio._salas_disponibles.remove(elemento)
                    elif tipo == "Alquiler de Equipos":
                        if isinstance(servicio, ServicioAlquilerEquipo):
                            clave = elemento.lower().replace(" ", "_")
                            if clave in servicio.TARIFAS:
                                servicio.TARIFAS[clave] = 0  # Marcar como eliminado
                    elif tipo == "Asesorías Especializadas":
                        if isinstance(servicio, ServicioAsesoria):
                            clave = elemento.lower().replace(" ", "_")
                            if clave in servicio.TARIFAS_POR_TIPO:
                                servicio.TARIFAS_POR_TIPO[clave] = 0  # Marcar como eliminado
                
                self.actualizar_vista_servicios()
                self.guardar_datos()  # Guardar automáticamente en JSON
                self.actualizar_estado(f"Elemento '{elemento}' eliminado")
                messagebox.showinfo("Éxito", f"Elemento '{elemento}' eliminado")
                
        except ReservaException as e:
            messagebox.showerror("Error", str(e))
    
    def actualizar_vista_reservas(self):
        """Actualiza la vista de reservas"""
        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)
        
        for reserva in self.sistema.listar_reservas():
            self.tree_reservas.insert("", tk.END, values=(
                reserva.id,
                f"{reserva.cliente.nombre} {reserva.cliente.apellido}",
                reserva.servicio.nombre,
                reserva.duracion,
                reserva.estado,
                f"${reserva.costo_total:,.2f}"
            ))
    
    def actualizar_estado(self, mensaje: str):
        """Actualiza la barra de estado"""
        self.estado.config(text=mensaje)
    
    def mostrar_clientes(self):
        """Muestra la pestaña de clientes"""
        self.notebook.select(0)
    
    def mostrar_servicios(self):
        """Muestra la pestaña de servicios"""
        self.notebook.select(1)
    
    def mostrar_reservas(self):
        """Muestra la pestaña de reservas"""
        self.notebook.select(2)

def main():
    """Función principal"""
    root = tk.Tk()
    InterfazSoftwareFJ(root)
    root.mainloop()


if __name__ == "__main__":
    main()