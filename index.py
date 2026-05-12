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

from typing import Optional, List, Dict  # importa los módulos necesarios de tipado
from abc import ABC, abstractmethod  # importa los módulos necesarios para manejar abtraccion
from datetime import datetime  # importa los módulos necesarios para manejar fechas y horas
import json, os, logging # importa los módulos necesarios para manejar archivos, json y logging
import tkinter as tk  # importa los módulos necesarios para manejar interfaces gráficas
from tkinter import ttk, messagebox  # importa los módulos necesarios para manejar interfaces gráficas

class SoftwareFJException(Exception):
    """Excepción base para el sistema"""
    def __init__(self, mensaje: str, codigo: int = 1000):
        """Función o método __init__."""
        self.mensaje = mensaje  # asigna un atributo del objeto
        self.codigo = codigo  # asigna un atributo del objeto
        super().__init__(self.mensaje)  # realiza la instrucción
    
    def __str__(self):
        """Función o método __str__."""
        return f"[Código {self.codigo}] {self.mensaje}"  # devuelve el valor al llamador


class ValidacionException(SoftwareFJException):
    """Excepción para errores de validación"""
    def __init__(self, mensaje: str):
        """Función o método __init__."""
        super().__init__(mensaje, codigo=1001)  # asigna un valor a una variable o atributo


class ReservaException(SoftwareFJException):
    """Excepción para errores en reservas"""
    def __init__(self, mensaje: str):
        """Función o método __init__."""
        super().__init__(mensaje, codigo=1002)  # asigna un valor a una variable o atributo


class ServicioException(SoftwareFJException):
    """Excepción para errores de servicio"""
    def __init__(self, mensaje: str):
        """Función o método __init__."""
        super().__init__(mensaje, codigo=1003)  # asigna un valor a una variable o atributo


class ClienteException(SoftwareFJException):
    """Excepción para errores de cliente"""
    def __init__(self, mensaje: str):
        """Función o método __init__."""
        super().__init__(mensaje, codigo=1004)  # asigna un valor a una variable o atributo


class DatosException(SoftwareFJException):
    """Excepción para datos inválidos o faltantes"""
    def __init__(self, mensaje: str):
        """Función o método __init__."""
        super().__init__(mensaje, codigo=1005)  # asigna un valor a una variable o atributo

class GestorLogs:
    """Gestor centralizado de logs del sistema"""
    
    def __init__(self, archivo_log: str = "software_fj.log"):
        """Función o método __init__."""
        self.archivo_log = archivo_log  # asigna un atributo del objeto
        self._configurar_log()  # realiza la instrucción
    
    def _configurar_log(self):
        """Configura el sistema de logging"""
        self.logger = logging.getLogger("SoftwareFJ")  # registra información en el log
        self.logger.setLevel(logging.DEBUG)  # registra información en el log
        
        # Handler para archivo
        handler = logging.FileHandler(self.archivo_log, encoding='utf-8')  # asigna un atributo del objeto
        formatter = logging.Formatter(  # asigna un valor a una variable o atributo
            '%(asctime)s | %(levelname)-8s | %(funcName)s | %(message)s',  # realiza la instrucción
            datefmt='%Y-%m-%d %H:%M:%S'  # asigna un valor a una variable o atributo
        )  # realiza la instrucción
        handler.setFormatter(formatter)  # realiza la instrucción
        
        if not self.logger.handlers:  # evalúa una condición
            self.logger.addHandler(handler)  # registra información en el log
    
    def info(self, mensaje: str):
        """Registra información"""
        self.logger.info(mensaje)  # registra información en el log
    
    def warning(self, mensaje: str):
        """Registra advertencias"""
        self.logger.warning(mensaje)  # registra información en el log
    
    def error(self, mensaje: str, excepcion: Optional[Exception] = None):
        """Registra errores"""
        if excepcion:  # evalúa una condición
            self.logger.error(f"{mensaje} | Excepción: {type(excepcion).__name__}: {str(excepcion)}")  # registra información en el log
        else:  # ejecuta el bloque alternativo si la condición anterior no se cumple
            self.logger.error(mensaje)  # registra información en el log
    
    def debug(self, mensaje: str):
        """Registra debug"""
        self.logger.debug(mensaje)  # registra información en el log

gestor_logs = GestorLogs()  # registra información en el log

class Entidad(ABC):
    """Clase abstracta que representa entidades generales del sistema"""
    
    def __init__(self, id_entidad: int):
        """Función o método __init__."""
        self._id = id_entidad  # asigna un atributo del objeto
        self._fecha_creacion = datetime.now()  # asigna un atributo del objeto
        self._activo = True  # asigna un atributo del objeto
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def id(self) -> int:
        """Función o método id."""
        return self._id  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def fecha_creacion(self) -> datetime:
        """Función o método fecha_creacion."""
        return self._fecha_creacion  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def activo(self) -> bool:
        """Función o método activo."""
        return self._activo  # devuelve el valor al llamador
    
    @activo.setter  # aplica un decorador sobre la función o clase siguiente
    def activo(self, valor: bool):
        """Función o método activo."""
        self._activo = valor  # asigna un atributo del objeto
    
    @abstractmethod  # aplica un decorador sobre la función o clase siguiente
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        pass  # no realiza ninguna acción
    
    @abstractmethod  # aplica un decorador sobre la función o clase siguiente
    def validar(self) -> bool:
        """Valida los datos de la entidad"""
        pass  # no realiza ninguna acción
    
    def __repr__(self):
        """Función o método __repr__."""
        return f"{self.__class__.__name__}(id={self._id})"  # devuelve el valor al llamador

class Cliente(Entidad):
    """Clase Cliente con validaciones robustas y encapsulación de datos"""
    
    def __init__(self, id_cliente: int, nombre: str, apellido: str, 
                 identificacion: str, telefono: str, email: str):
        """Función o método __init__."""
        super().__init__(id_cliente)  # realiza la instrucción
        self._nombre = nombre  # asigna un atributo del objeto
        self._apellido = apellido  # asigna un atributo del objeto
        self._identificacion = identificacion  # asigna un atributo del objeto
        self._telefono = telefono  # asigna un atributo del objeto
        self._email = email  # asigna un atributo del objeto
        self._reservas: List[int] = []  # IDs de reservas asociadas
        
        # Validar al crear
        self.validar()  # realiza la instrucción
        gestor_logs.info(f"Cliente creado: {self.nombre_completo}")  # registra información en el log
    
    # -------------------------------------------------------------------------
    # Propiedades con encapsulación
    # -------------------------------------------------------------------------
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def nombre(self) -> str:
        """Función o método nombre."""
        return self._nombre  # devuelve el valor al llamador
    
    @nombre.setter  # aplica un decorador sobre la función o clase siguiente
    def nombre(self, valor: str):
        """Función o método nombre."""
        if not valor or len(valor.strip()) < 2:  # evalúa una condición
            raise ValidacionException("El nombre debe tener al menos 2 caracteres")  # lanza una excepción cuando ocurre un error
        self._nombre = valor.strip().title()  # asigna un atributo del objeto
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def apellido(self) -> str:
        """Función o método apellido."""
        return self._apellido  # devuelve el valor al llamador
    
    @apellido.setter  # aplica un decorador sobre la función o clase siguiente
    def apellido(self, valor: str):
        """Función o método apellido."""
        if not valor or len(valor.strip()) < 2:  # evalúa una condición
            raise ValidacionException("El apellido debe tener al menos 2 caracteres")  # lanza una excepción cuando ocurre un error
        self._apellido = valor.strip().title()  # asigna un atributo del objeto
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def identificacion(self) -> str:
        """Función o método identificacion."""
        return self._identificacion  # devuelve el valor al llamador
    
    @identificacion.setter  # aplica un decorador sobre la función o clase siguiente
    def identificacion(self, valor: str):
        """Función o método identificacion."""
        if not valor or len(valor.strip()) < 5:  # evalúa una condición
            raise ValidacionException("La identificación debe tener al menos 5 caracteres")  # lanza una excepción cuando ocurre un error
        self._identificacion = valor.strip()  # asigna un atributo del objeto
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def telefono(self) -> str:
        """Función o método telefono."""
        return self._telefono  # devuelve el valor al llamador
    
    @telefono.setter  # aplica un decorador sobre la función o clase siguiente
    def telefono(self, valor: str):
        """Función o método telefono."""
        # Validar formato de teléfono
        telefono_limpio = valor.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")  # asigna un valor a una variable o atributo
        if not telefono_limpio.isdigit() or len(telefono_limpio) < 7:  # evalúa una condición
            raise ValidacionException("El teléfono debe tener al menos 7 dígitos")  # lanza una excepción cuando ocurre un error
        self._telefono = valor.strip()  # asigna un atributo del objeto
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def email(self) -> str:
        """Función o método email."""
        return self._email  # devuelve el valor al llamador
    
    @email.setter  # aplica un decorador sobre la función o clase siguiente
    def email(self, valor: str):
        """Función o método email."""
        # Validar formato de email
        valor = valor.strip().lower()  # asigna un valor a una variable o atributo
        if '@' not in valor or '.' not in valor.split('@')[-1]:  # evalúa una condición
            raise ValidacionException("El email no tiene un formato válido")  # lanza una excepción cuando ocurre un error
        self._email = valor  # asigna un atributo del objeto
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def nombre_completo(self) -> str:
        """Función o método nombre_completo."""
        return f"{self._nombre} {self._apellido}"  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def reservas(self) -> List[int]:
        """Función o método reservas."""
        return self._reservas.copy()  # devuelve el valor al llamador
    
    # -------------------------------------------------------------------------
    # Métodos
    # -------------------------------------------------------------------------
    
    def agregar_reserva(self, id_reserva: int):
        """Agrega una reserva al cliente"""
        if id_reserva not in self._reservas:  # evalúa una condición
            self._reservas.append(id_reserva)  # realiza la instrucción
            gestor_logs.info(f"Reserva {id_reserva} asociada al cliente {self._id}")  # registra información en el log
    
    def quitar_reserva(self, id_reserva: int):
        """Quita una reserva del cliente"""
        if id_reserva in self._reservas:  # evalúa una condición
            self._reservas.remove(id_reserva)  # realiza la instrucción
            gestor_logs.info(f"Reserva {id_reserva} desasociada del cliente {self._id}")  # registra información en el log
    
    def to_dict(self) -> dict:
        """Convierte el cliente a diccionario"""
        return {  # devuelve el valor al llamador
            "id": self._id,  # realiza la instrucción
            "nombre": self._nombre,  # realiza la instrucción
            "apellido": self._apellido,  # realiza la instrucción
            "identificacion": self._identificacion,  # realiza la instrucción
            "telefono": self._telefono,  # realiza la instrucción
            "email": self._email,  # realiza la instrucción
            "reservas": self._reservas,  # realiza la instrucción
            "fecha_creacion": self._fecha_creacion.isoformat(),  # realiza la instrucción
            "activo": self._activo  # realiza la instrucción
        }  # realiza la instrucción
    
    @classmethod  # aplica un decorador sobre la función o clase siguiente
    def from_dict(cls, datos: dict) -> 'Cliente':
        """Crea un cliente desde un diccionario"""
        cliente = cls(  # asigna un valor a una variable o atributo
            datos["id"],  # realiza la instrucción
            datos["nombre"],  # realiza la instrucción
            datos["apellido"],  # realiza la instrucción
            datos["identificacion"],  # realiza la instrucción
            datos["telefono"],  # realiza la instrucción
            datos["email"]  # realiza la instrucción
        )  # realiza la instrucción
        cliente._reservas = datos.get("reservas", [])  # asigna un valor a una variable o atributo
        cliente._activo = datos.get("activo", True)  # asigna un valor a una variable o atributo
        if "fecha_creacion" in datos:  # evalúa una condición
            cliente._fecha_creacion = datetime.fromisoformat(datos["fecha_creacion"])  # asigna un valor a una variable o atributo
        return cliente  # devuelve el valor al llamador
    
    def validar(self) -> bool:
        """Valida los datos del cliente"""
        try:  # inicia un bloque de manejo de excepciones
            # Validar nombre
            if not self._nombre or len(self._nombre.strip()) < 2:  # evalúa una condición
                raise ValidacionException("Nombre inválido")  # lanza una excepción cuando ocurre un error
            
            # Validar apellido
            if not self._apellido or len(self._apellido.strip()) < 2:  # evalúa una condición
                raise ValidacionException("Apellido inválido")  # lanza una excepción cuando ocurre un error
            
            # Validar identificación
            if not self._identificacion or len(self._identificacion.strip()) < 5:  # evalúa una condición
                raise ValidacionException("Identificación inválida")  # lanza una excepción cuando ocurre un error
            
            # Validar teléfono
            telefono_limpio = self._telefono.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")  # asigna un atributo del objeto
            if not telefono_limpio.isdigit() or len(telefono_limpio) < 7:  # evalúa una condición
                raise ValidacionException("Teléfono inválido")  # lanza una excepción cuando ocurre un error
            
            # Validar email
            if '@' not in self._email or '.' not in self._email.split('@')[-1]:  # evalúa una condición
                raise ValidacionException("Email inválido")  # lanza una excepción cuando ocurre un error
            
            return True  # devuelve el valor al llamador
            
        except ValidacionException as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error de validación en cliente: {e}")  # registra información en el log
            raise  # realiza la instrucción
    
    def __str__(self):
        """Función o método __str__."""
        return f"Cliente: {self._nombre} {self._apellido} ({self._identificacion})"  # devuelve el valor al llamador

class Servicio(ABC):
    """Clase abstracta Servicio"""
    
    def __init__(self, id: int, nombre: str, descripcion: str, capacidad: int, precio: int, activo: bool, tipo: str):
        """Función o método __init__."""
        self._id = id  # asigna un atributo del objeto
        self._nombre = nombre  # asigna un atributo del objeto
        self._descripcion = descripcion  # asigna un atributo del objeto
        self._activo = activo  # asigna un atributo del objeto
        self._tipo = tipo  # asigna un atributo del objeto
        self._capacidad = capacidad  # asigna un atributo del objeto
        self._precio = precio  # asigna un atributo del objeto
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def id(self) -> int:
        """Función o método id."""
        return self._id  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def nombre(self) -> str:
        """Función o método nombre."""
        return self._nombre  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def descripcion(self) -> str:
        """Función o método descripcion."""
        return self._descripcion  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def activo(self) -> bool:
        """Función o método activo."""
        return self._activo  # devuelve el valor al llamador
    
    @abstractmethod  # aplica un decorador sobre la función o clase siguiente
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        """Calcula el costo del servicio - método sobrescrito"""
        pass  # no realiza ninguna acción
    
    @abstractmethod  # aplica un decorador sobre la función o clase siguiente
    def describir_servicio(self) -> str:
        """Describe el servicio - método sobrescrito"""
        pass  # no realiza ninguna acción
    
    @abstractmethod  # aplica un decorador sobre la función o clase siguiente
    def validar_parametros(self, **kwargs) -> bool:
        """Valida los parámetros del servicio"""
        pass  # no realiza ninguna acción
    
    def to_dict(self) -> dict:
        """Convierte el servicio a diccionario"""
        return {  # devuelve el valor al llamador
            "id": self._id,  # realiza la instrucción
            "nombre": self._nombre,  # realiza la instrucción
            "descripcion": self._descripcion,  # realiza la instrucción
            "capacidad": self._capacidad,  # realiza la instrucción
            "precio": self._precio,  # realiza la instrucción
            "activo": self._activo,  # realiza la instrucción
            "tipo": self.__class__.__name__  # realiza la instrucción
        }  # realiza la instrucción
    
    def __repr__(self):
        """Función o método __repr__."""
        return f"Servicio(id={self._id}, nombre='{self._nombre}')"  # devuelve el valor al llamador

class ServicioReservaSala(Servicio):
    """Servicio de reservas de salas"""
    
    TARIFA_POR_HORA = 50000  # Tarifa base por hora
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def capacidad(self) -> int:
        """Función o método capacidad."""
        return self._capacidad  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def salas(self) -> List[str]:
        """Función o método salas."""
        return self._salas_disponibles.copy()  # devuelve el valor al llamador
    
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
        try:  # inicia un bloque de manejo de excepciones
            # Validar duración
            if duracion <= 0:  # evalúa una condición
                raise ServicioException("La duración debe ser mayor a 0")  # lanza una excepción cuando ocurre un error
            
            if duracion > 12:  # evalúa una condición
                raise ServicioException("La duración máxima es de 12 horas")  # lanza una excepción cuando ocurre un error
            
            # Calcular costo base
            costo = duracion * self.TARIFA_POR_HORA  # asigna un atributo del objeto
            
            # Aplicar costo por sala específica
            if sala:  # evalúa una condición
                if sala not in self._salas_disponibles:  # evalúa una condición
                    raise ServicioException(f"La sala '{sala}' no está disponible")  # lanza una excepción cuando ocurre un error
                
                # Salas VIP tienen recargo
                if sala == "Sala VIP":  # evalúa una condición
                    costo *= 1.5  # asigna un valor a una variable o atributo
                elif sala == "Sala A":  # evalúa una condición
                    costo *= 1.2  # asigna un valor a una variable o atributo
            
            # Agregar horas extras
            if horas_extras > 0:  # evalúa una condición
                costo += horas_extras * (self.TARIFA_POR_HORA * 1.25)  # asigna un atributo del objeto
            
            # Aplicar descuento
            if descuento > 0:  # evalúa una condición
                if descuento > 50:  # evalúa una condición
                    raise ServicioException("El descuento no puede exceder el 50%")  # lanza una excepción cuando ocurre un error
                costo -= costo * (descuento / 100)  # asigna un valor a una variable o atributo
            
            gestor_logs.info(f"Costo calculado para reserva de sala: ${costo:,.2f}")  # registra información en el log
            return costo  # devuelve el valor al llamador
            
        except ServicioException as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error al calcular costo de reserva: {e}")  # registra información en el log
            raise  # realiza la instrucción
        except Exception as e:  # captura la excepción producida en el bloque try
            gestor_logs.error("Error inesperado calculando costo", e)  # registra información en el log
            raise ServicioException(f"Error al calcular costo: {str(e)}")  # lanza una excepción cuando ocurre un error
    
    def describir_servicio(self) -> str:
        """Describe el servicio de reserva de sala"""
        return (f"Reserva de Sala - Capacidad: {self._capacidad} personas\n"  # devuelve el valor al llamador
                f"Salas disponibles: {', '.join(self._salas_disponibles)}\n"  # realiza la instrucción
                f"Tarifa: ${self.TARIFA_POR_HORA:,}/hora")  # realiza la instrucción
    
    def validar_parametros(self, **kwargs) -> bool:
        """Valida los parámetros para reserva de sala"""
        duracion = kwargs.get("duracion")  # asigna un valor a una variable o atributo
        sala = kwargs.get("sala")  # asigna un valor a una variable o atributo
        
        if duracion and (duracion <= 0 or duracion > 12):  # evalúa una condición
            raise ServicioException("Duración inválida para reserva de sala")  # lanza una excepción cuando ocurre un error
        
        if sala and sala not in self._salas_disponibles:  # evalúa una condición
            raise ServicioException(f"Sala '{sala}' no disponible")  # lanza una excepción cuando ocurre un error
        
        return True  # devuelve el valor al llamador
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        datos = super().to_dict()  # asigna un valor a una variable o atributo
        return datos  # devuelve el valor al llamador

class ServicioAlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos"""
    @property  # aplica un decorador sobre la función o clase siguiente
    def equipos(self) -> List[str]:
        """Función o método equipos."""
        return self._equipos_disponibles.copy()  # devuelve el valor al llamador
    
    def obtener_tarifa(self, equipo: str) -> float:
        """Obtiene la tarifa de un equipo específico"""
        return self.TARIFAS.get(equipo.lower(), 0)  # devuelve el valor al llamador
    
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
        try:  # inicia un bloque de manejo de excepciones
            if duracion <= 0:  # evalúa una condición
                raise ServicioException("La duración debe ser mayor a 0")  # lanza una excepción cuando ocurre un error
            
            costo = 0  # asigna un valor a una variable o atributo
            
            if equipo:  # evalúa una condición
                # Costo de equipo específico
                tarifa = self.obtener_tarifa(equipo)  # asigna un atributo del objeto
                if tarifa == 0:  # evalúa una condición
                    raise ServicioException(f"Equipo '{equipo}' no disponible")  # lanza una excepción cuando ocurre un error
                
                costo = duracion * tarifa * cantidad  # asigna un valor a una variable o atributo
                
                # Agregar costo de seguro (10%)
                if seguro:  # evalúa una condición
                    costo *= 1.10  # asigna un valor a una variable o atributo
            else:  # ejecuta el bloque alternativo si la condición anterior no se cumple
                # Costo de todos los equipos
                costo += duracion * self._precio  # asigna un atributo del objeto
            
            gestor_logs.info(f"Costo calculado para alquiler de equipo: ${costo:,.2f}")  # registra información en el log
            return costo  # devuelve el valor al llamador
            
        except ServicioException as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error al calcular costo de alquiler: {e}")  # registra información en el log
            raise  # realiza la instrucción
        except Exception as e:  # captura la excepción producida en el bloque try
            gestor_logs.error("Error inesperado calculando costo", e)  # registra información en el log
            raise ServicioException(f"Error al calcular costo: {str(e)}")  # lanza una excepción cuando ocurre un error
    
    def describir_servicio(self) -> str:
        """Describe el servicio de alquiler de equipos"""
        equipos_info = "\n".join([f"  - {eq}: ${tar:,}/hora"   # asigna un valor a una variable o atributo
                                   for eq, tar in self.TARIFAS.items()])  # inicia un bucle para repetir instrucciones
        return f"Alquiler de Equipos\n{equipos_info}"  # devuelve el valor al llamador
    
    def validar_parametros(self, **kwargs) -> bool:
        """Valida los parámetros para alquiler de equipo"""
        duracion = kwargs.get("duracion")  # asigna un valor a una variable o atributo
        equipo = kwargs.get("equipo")  # asigna un valor a una variable o atributo
        cantidad = kwargs.get("cantidad", 1)  # asigna un valor a una variable o atributo
        
        if duracion and duracion <= 0:  # evalúa una condición
            raise ServicioException("Duración inválida")  # lanza una excepción cuando ocurre un error
        
        if cantidad and cantidad < 1:  # evalúa una condición
            raise ServicioException("La cantidad debe ser al menos 1")  # lanza una excepción cuando ocurre un error
        
        return True  # devuelve el valor al llamador
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        datos = super().to_dict()  # asigna un valor a una variable o atributo
        return datos  # devuelve el valor al llamador

class ServicioAsesoria(Servicio):
    """Servicio de asesorías especializadas"""    
    @property  # aplica un decorador sobre la función o clase siguiente
    def tipos(self) -> List[str]:
        """Función o método tipos."""
        return self._tipos_asesoria.copy()  # devuelve el valor al llamador
    
    def obtener_tarifa(self, tipo: str) -> float:
        """Obtiene la tarifa de un tipo de asesoría"""
        return self._precio  # devuelve el valor al llamador
    
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
        try:  # inicia un bloque de manejo de excepciones
            if duracion <= 0:  # evalúa una condición
                raise ServicioException("La duración debe ser mayor a 0")  # lanza una excepción cuando ocurre un error
            
            if duracion > 8:  # evalúa una condición
                raise ServicioException("La duración máxima es de 8 horas")  # lanza una excepción cuando ocurre un error
            
            costo = 0  # asigna un valor a una variable o atributo
            
            if tipo:  # evalúa una condición
                # Costo de tipo específico
                tarifa = self.obtener_tarifa(tipo)  # asigna un atributo del objeto
                if tarifa == 0:  # evalúa una condición
                    raise ServicioException(f"Tipo de asesoría '{tipo}' no disponible")  # lanza una excepción cuando ocurre un error
                
                costo = duracion * tarifa  # asigna un valor a una variable o atributo
                
                # Aplicar nivel (recargo)
                if nivel == "intermedio":  # evalúa una condición
                    costo *= 1.25  # asigna un valor a una variable o atributo
                elif nivel == "avanzado":  # evalúa una condición
                    costo *= 1.50  # asigna un valor a una variable o atributo
            else:  # ejecuta el bloque alternativo si la condición anterior no se cumple
                # Costo promedio
                tarifa_promedio = self._precio  # asigna un atributo del objeto
                costo = duracion * tarifa_promedio  # asigna un valor a una variable o atributo
            
            # Agregar impuestos (19% IVA)
            if impuestos:  # evalúa una condición
                costo *= 1.19  # asigna un valor a una variable o atributo
            
            gestor_logs.info(f"Costo calculado para asesoría: ${costo:,.2f}")  # registra información en el log
            return costo  # devuelve el valor al llamador
            
        except ServicioException as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error al calcular costo de asesoría: {e}")  # registra información en el log
            raise  # realiza la instrucción
        except Exception as e:  # captura la excepción producida en el bloque try
            gestor_logs.error("Error inesperado calculando costo", e)  # registra información en el log
            raise ServicioException(f"Error al calcular costo: {str(e)}")  # lanza una excepción cuando ocurre un error
    
    def describir_servicio(self) -> str:
        """Describe el servicio de asesorías"""
        tipos_info = "\n".join([f"  - {tipo}: ${tar:,}/hora"   # asigna un valor a una variable o atributo
                                for tipo, tar in self.TARIFAS_POR_TIPO.items()])  # inicia un bucle para repetir instrucciones
        return f"Asesorías Especializadas\n{tipos_info}\nNiveles: Básico, Intermedio, Avanzado"  # devuelve el valor al llamador
    
    def validar_parametros(self, **kwargs) -> bool:
        """Valida los parámetros para asesoría"""
        duracion = kwargs.get("duracion")  # asigna un valor a una variable o atributo
        tipo = kwargs.get("tipo")  # asigna un valor a una variable o atributo
        nivel = kwargs.get("nivel", "basico")  # asigna un valor a una variable o atributo
        
        if duracion and (duracion <= 0 or duracion > 8):  # evalúa una condición
            raise ServicioException("Duración inválida para asesoría")  # lanza una excepción cuando ocurre un error
        
        if tipo and tipo.lower() not in self._tipos_asesoria:  # evalúa una condición
            raise ServicioException(f"Tipo de asesoría '{tipo}' no disponible")  # lanza una excepción cuando ocurre un error
        
        if nivel not in ["basico", "intermedio", "avanzado"]:  # evalúa una condición
            raise ServicioException("Nivel inválido")  # lanza una excepción cuando ocurre un error
        
        return True  # devuelve el valor al llamador
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        datos = super().to_dict()  # asigna un valor a una variable o atributo
        return datos  # devuelve el valor al llamador

entidades = {  # asigna un valor a una variable o atributo
    'ServicioReservaSala': ServicioReservaSala,  # realiza la instrucción
    'ServicioAlquilerEquipo': ServicioAlquilerEquipo,  # realiza la instrucción
    'ServicioAsesoria': ServicioAsesoria,  # realiza la instrucción
}  # realiza la instrucción

class Reserva:
    """Clase Reserva que integra cliente, servicio, duración y estado"""
    
    ESTADOS = ["pendiente", "confirmada", "cancelada", "completada"]  # asigna un valor a una variable o atributo
    
    def __init__(self, id_reserva: int, cliente: Cliente, servicio: Servicio,
                 duracion: float, descripcion: str = ""):
        """Función o método __init__."""
        self._id = id_reserva  # asigna un atributo del objeto
        self._cliente = cliente  # asigna un atributo del objeto
        self._servicio = servicio  # asigna un atributo del objeto
        self._duracion = duracion  # asigna un atributo del objeto
        self._descripcion = descripcion  # asigna un atributo del objeto
        self._estado = "pendiente"  # asigna un atributo del objeto
        self._costo_total = 0.0  # asigna un atributo del objeto
        self._fecha_creacion = datetime.now()  # asigna un atributo del objeto
        self._fecha_confirmacion: Optional[datetime] = None  # asigna un atributo del objeto
        
        # Validar parámetros
        self._validar()  # realiza la instrucción
        
        # Asociar reserva al cliente
        cliente.agregar_reserva(id_reserva)  # realiza la instrucción
        
        gestor_logs.info(f"Reserva creada: {id_reserva} - Cliente: {cliente.id}")  # registra información en el log
    
    # -------------------------------------------------------------------------
    # Propiedades
    # -------------------------------------------------------------------------
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def id(self) -> int:
        """Función o método id."""
        return self._id  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def cliente(self) -> Cliente:
        """Función o método cliente."""
        return self._cliente  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def servicio(self) -> Servicio:
        """Función o método servicio."""
        return self._servicio  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def duracion(self) -> float:
        """Función o método duracion."""
        return self._duracion  # devuelve el valor al llamador
    
    @duracion.setter  # aplica un decorador sobre la función o clase siguiente
    def duracion(self, valor: float):
        """Función o método duracion."""
        if valor <= 0:  # evalúa una condición
            raise ReservaException("La duración debe ser mayor a 0")  # lanza una excepción cuando ocurre un error
        self._duracion = valor  # asigna un atributo del objeto
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def descripcion(self) -> str:
        """Función o método descripcion."""
        return self._descripcion  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def estado(self) -> str:
        """Función o método estado."""
        return self._estado  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def costo_total(self) -> float:
        """Función o método costo_total."""
        return self._costo_total  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def fecha_creacion(self) -> datetime:
        """Función o método fecha_creacion."""
        return self._fecha_creacion  # devuelve el valor al llamador
    
    @property  # aplica un decorador sobre la función o clase siguiente
    def fecha_confirmacion(self) -> Optional[datetime]:
        """Función o método fecha_confirmacion."""
        return self._fecha_confirmacion  # devuelve el valor al llamador
    
    # -------------------------------------------------------------------------
    # Métodos de procesamiento
    # -------------------------------------------------------------------------
    
    def _validar(self):
        """Valida los datos de la reserva"""
        try:  # inicia un bloque de manejo de excepciones
            if not self._cliente:  # evalúa una condición
                raise ReservaException("El cliente es obligatorio")  # lanza una excepción cuando ocurre un error
            
            if not self._servicio:  # evalúa una condición
                raise ReservaException("El servicio es obligatorio")  # lanza una excepción cuando ocurre un error
            
            if self._duracion <= 0:  # evalúa una condición
                raise ReservaException("La duración debe ser mayor a 0")  # lanza una excepción cuando ocurre un error
            
            # Validar según tipo de servicio
            if isinstance(self._servicio, ServicioReservaSala):  # evalúa una condición
                self._servicio.validar_parametros(duracion=self._duracion)  # asigna un atributo del objeto
            elif isinstance(self._servicio, ServicioAlquilerEquipo):  # evalúa una condición
                self._servicio.validar_parametros(duracion=self._duracion)  # asigna un atributo del objeto
            elif isinstance(self._servicio, ServicioAsesoria):  # evalúa una condición
                self._servicio.validar_parametros(duracion=self._duracion)  # asigna un atributo del objeto
            
            return True  # devuelve el valor al llamador
            
        except ReservaException as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error de validación en reserva: {e}")  # registra información en el log
            raise  # realiza la instrucción
    
    def procesar(self, **kwargs) -> float:
        """
        Procesa la reserva calculando el costo total
        Manejo de excepciones con try/except/else/finally
        """
        costo = 0.0  # asigna un valor a una variable o atributo
        
        try:  # inicia un bloque de manejo de excepciones
            # Calcular según tipo de servicio
            if isinstance(self._servicio, ServicioReservaSala):  # evalúa una condición
                sala = kwargs.get("sala")  # asigna un valor a una variable o atributo
                horas_extras = kwargs.get("horas_extras", 0)  # asigna un valor a una variable o atributo
                descuento = kwargs.get("descuento", 0)  # asigna un valor a una variable o atributo
                costo = self._servicio.calcular_costo(  # asigna un atributo del objeto
                    self._duracion, sala, horas_extras, descuento  # realiza la instrucción
                )  # realiza la instrucción
                
            elif isinstance(self._servicio, ServicioAlquilerEquipo):  # evalúa una condición
                equipo = kwargs.get("equipo")  # asigna un valor a una variable o atributo
                cantidad = kwargs.get("cantidad", 1)  # asigna un valor a una variable o atributo
                seguro = kwargs.get("seguro", False)  # asigna un valor a una variable o atributo
                costo = self._servicio.calcular_costo(  # asigna un atributo del objeto
                    self._duracion, equipo, cantidad, seguro  # realiza la instrucción
                )  # realiza la instrucción
                
            elif isinstance(self._servicio, ServicioAsesoria):  # evalúa una condición
                tipo = kwargs.get("tipo")  # asigna un valor a una variable o atributo
                nivel = kwargs.get("nivel", "basico")  # asigna un valor a una variable o atributo
                impuestos = kwargs.get("impuestos", True)  # asigna un valor a una variable o atributo
                costo = self._servicio.calcular_costo(  # asigna un atributo del objeto
                    self._duracion, tipo, nivel, impuestos  # realiza la instrucción
                )  # realiza la instrucción
            
            self._costo_total = costo  # asigna un atributo del objeto
            
        except ServicioException as e:  # captura la excepción producida en el bloque try
            # Encadenamiento de excepciones
            gestor_logs.error(f"Error procesando reserva: {e}")  # registra información en el log
            raise ReservaException(f"Error al procesar reserva: {str(e)}") from e  # lanza una excepción cuando ocurre un error
            
        except Exception as e:  # captura la excepción producida en el bloque try
            gestor_logs.error("Error inesperado procesando reserva", e)  # registra información en el log
            raise ReservaException(f"Error inesperado: {str(e)}") from e  # lanza una excepción cuando ocurre un error
            
        else:  # ejecuta el bloque alternativo si la condición anterior no se cumple
            gestor_logs.info(f"Reserva {self._id} procesada exitosamente - Costo: ${costo:,.2f}")  # registra información en el log
            
        finally:  # ejecuta siempre este bloque aunque haya excepción
            # Siempre se ejecuta
            pass  # no realiza ninguna acción
        
        return costo  # devuelve el valor al llamador
    
    def confirmar(self) -> bool:
        """
        Confirma la reserva
        Uso de try/except/finally
        """
        try:  # inicia un bloque de manejo de excepciones
            if self._estado != "pendiente":  # evalúa una condición
                raise ReservaException(f"No se puede confirmar una reserva en estado '{self._estado}'")  # lanza una excepción cuando ocurre un error
            
            if self._costo_total == 0:  # evalúa una condición
                raise ReservaException("La reserva debe ser procesada antes de confirmarse")  # lanza una excepción cuando ocurre un error
            
            self._estado = "confirmada"  # asigna un atributo del objeto
            self._fecha_confirmacion = datetime.now()  # asigna un atributo del objeto
            
            gestor_logs.info(f"Reserva {self._id} confirmada")  # registra información en el log
            return True  # devuelve el valor al llamador
            
        except ReservaException as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error al confirmar reserva: {e}")  # registra información en el log
            raise  # realiza la instrucción
        except Exception as e:  # captura la excepción producida en el bloque try
            gestor_logs.error("Error inesperado confirmando reserva", e)  # registra información en el log
            raise ReservaException(f"Error al confirmar: {str(e)}") from e  # lanza una excepción cuando ocurre un error
        finally:  # ejecuta siempre este bloque aunque haya excepción
            # Limpieza si es necesario
            pass  # no realiza ninguna acción
    
    def cancelar(self) -> bool:
        """
        Cancela la reserva
        """
        try:  # inicia un bloque de manejo de excepciones
            if self._estado == "cancelada":  # evalúa una condición
                raise ReservaException("La reserva ya está cancelada")  # lanza una excepción cuando ocurre un error
            
            if self._estado == "completada":  # evalúa una condición
                raise ReservaException("No se puede cancelar una reserva completada")  # lanza una excepción cuando ocurre un error
            
            self._estado = "cancelada"  # asigna un atributo del objeto
            
            # Desasociar del cliente
            self._cliente.quitar_reserva(self._id)  # realiza la instrucción
            
            gestor_logs.info(f"Reserva {self._id} cancelada")  # registra información en el log
            return True  # devuelve el valor al llamador
            
        except ReservaException as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error al cancelar reserva: {e}")  # registra información en el log
            raise  # realiza la instrucción
        except Exception as e:  # captura la excepción producida en el bloque try
            gestor_logs.error("Error inesperado cancelando reserva", e)  # registra información en el log
            raise ReservaException(f"Error al cancelar: {str(e)}") from e  # lanza una excepción cuando ocurre un error
    
    def completar(self) -> bool:
        """
        Marca la reserva como completada
        """
        try:  # inicia un bloque de manejo de excepciones
            if self._estado != "confirmada":  # evalúa una condición
                raise ReservaException("Solo se pueden completar reservas confirmadas")  # lanza una excepción cuando ocurre un error
            
            self._estado = "completada"  # asigna un atributo del objeto
            gestor_logs.info(f"Reserva {self._id} completada")  # registra información en el log
            return True  # devuelve el valor al llamador
            
        except ReservaException as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error al completar reserva: {e}")  # registra información en el log
            raise  # realiza la instrucción
    
    def to_dict(self) -> dict:
        """Convierte la reserva a diccionario"""
        return {  # devuelve el valor al llamador
            "id": self._id,  # realiza la instrucción
            "cliente_id": self._cliente.id,  # realiza la instrucción
            "servicio_id": self._servicio.id,  # realiza la instrucción
            "duracion": self._duracion,  # realiza la instrucción
            "descripcion": self._descripcion,  # realiza la instrucción
            "estado": self._estado,  # realiza la instrucción
            "costo_total": self._costo_total,  # realiza la instrucción
            "fecha_creacion": self._fecha_creacion.isoformat(),  # realiza la instrucción
            "fecha_confirmacion": self._fecha_confirmacion.isoformat() if self._fecha_confirmacion else None  # realiza la instrucción
        }  # realiza la instrucción
    
    def __str__(self):
        """Función o método __str__."""
        return (f"Reserva #{self._id} | Cliente: {self._cliente.nombre} {self._cliente.apellido} | "
                f"Servicio: {self._servicio.nombre} | Estado: {self._estado} | "  # realiza la instrucción
                f"Costo: ${self._costo_total:,.2f}")  # realiza la instrucción

class SistemaSoftwareFJ:
    """Sistema principal que gestiona clientes, servicios y reservas"""
    
    def __init__(self):
        """Función o método __init__."""
        self._clientes: Dict[int, Cliente] = {}  # asigna un atributo del objeto
        self._servicios: Dict[int, Servicio] = {}  # asigna un atributo del objeto
        self._reservas: Dict[int, Reserva] = {}  # asigna un atributo del objeto
        self._next_id_cliente = 1  # asigna un atributo del objeto
        self._next_id_servicio = 1  # asigna un atributo del objeto
        self._next_id_reserva = 1  # asigna un atributo del objeto
        
        # Inicializar servicios disponibles
        self._inicializar_servicios()  # realiza la instrucción
        
        gestor_logs.info("Sistema SoftwareFJ inicializado")  # registra información en el log
    
    def _inicializar_servicios(self):
        """Inicializa los servicios del sistema"""
        try:              # inicia un bloque de manejo de excepciones
            self._next_id_servicio = 4  # asigna un atributo del objeto
            
            gestor_logs.info("Servicios inicializados correctamente")  # registra información en el log
            
        except Exception as e:  # captura la excepción producida en el bloque try
            gestor_logs.error("Error inicializando servicios", e)  # registra información en el log
            raise  # realiza la instrucción
    
    def crear_cliente(self, nombre: str, apellido: str, identificacion: str,
                     telefono: str, email: str) -> Cliente:
        """Crea un nuevo cliente"""
        try:  # inicia un bloque de manejo de excepciones
            # Verificar identificación única
            for cliente in self._clientes.values():  # inicia un bucle para repetir instrucciones
                if cliente.identificacion == identificacion:  # evalúa una condición
                    raise ClienteException(f"Ya existe un cliente con identificación '{identificacion}'")  # lanza una excepción cuando ocurre un error
            
            cliente = Cliente(  # asigna un valor a una variable o atributo
                self._next_id_cliente,  # realiza la instrucción
                nombre, apellido, identificacion, telefono, email  # realiza la instrucción
            )  # realiza la instrucción
            
            self._clientes[self._next_id_cliente] = cliente  # asigna un atributo del objeto
            self._next_id_cliente += 1  # asigna un atributo del objeto
            
            return cliente  # devuelve el valor al llamador
            
        except (ValidacionException, ClienteException) as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error creando cliente: {e}")  # registra información en el log
            raise  # realiza la instrucción
        except Exception as e:  # captura la excepción producida en el bloque try
            gestor_logs.error("Error inesperado creando cliente", e)  # registra información en el log
            raise ClienteException(f"Error al crear cliente: {str(e)}") from e  # lanza una excepción cuando ocurre un error
    
    def obtener_cliente(self, id_cliente: int) -> Optional[Cliente]:
        """Obtiene un cliente por su ID"""
        return self._clientes.get(id_cliente)  # devuelve el valor al llamador
    
    def listar_clientes(self) -> List[Cliente]:
        """Lista todos los clientes"""
        return list(self._clientes.values())  # devuelve el valor al llamador
    
    def actualizar_cliente(self, id_cliente: int, **kwargs) -> Cliente:
        """Actualiza los datos de un cliente"""
        try:  # inicia un bloque de manejo de excepciones
            cliente = self.obtener_cliente(id_cliente)  # asigna un atributo del objeto
            if not cliente:  # evalúa una condición
                raise ClienteException(f"No existe cliente con ID {id_cliente}")  # lanza una excepción cuando ocurre un error
            
            # Actualizar campos proporcionados
            if "nombre" in kwargs:  # evalúa una condición
                cliente.nombre = kwargs["nombre"]  # asigna un valor a una variable o atributo
            if "apellido" in kwargs:  # evalúa una condición
                cliente.apellido = kwargs["apellido"]  # asigna un valor a una variable o atributo
            if "telefono" in kwargs:  # evalúa una condición
                cliente.telefono = kwargs["telefono"]  # asigna un valor a una variable o atributo
            if "email" in kwargs:  # evalúa una condición
                cliente.email = kwargs["email"]  # asigna un valor a una variable o atributo
            
            gestor_logs.info(f"Cliente {id_cliente} actualizado")  # registra información en el log
            return cliente  # devuelve el valor al llamador
            
        except (ValidacionException, ClienteException) as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error actualizando cliente: {e}")  # registra información en el log
            raise  # realiza la instrucción
    
    def eliminar_cliente(self, id_cliente: int) -> bool:
        """Elimina (desactiva) un cliente"""
        try:  # inicia un bloque de manejo de excepciones
            cliente = self.obtener_cliente(id_cliente)  # asigna un atributo del objeto
            if not cliente:  # evalúa una condición
                raise ClienteException(f"No existe cliente con ID {id_cliente}")  # lanza una excepción cuando ocurre un error
            
            # Verificar que no tenga reservas
            if cliente.reservas:  # evalúa una condición
                raise ClienteException("No se puede eliminar un cliente con reservas.")  # lanza una excepción cuando ocurre un error
            
            cliente.activo = False  # asigna un valor a una variable o atributo
            gestor_logs.info(f"Cliente {id_cliente} eliminado")  # registra información en el log
            return True  # devuelve el valor al llamador
            
        except ClienteException as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error eliminando cliente: {e}")  # registra información en el log
            raise  # realiza la instrucción
    
    def obtener_servicio(self, id_servicio: int) -> Optional[Servicio]:
        """Obtiene un servicio por su ID"""
        return self._servicios.get(id_servicio)  # devuelve el valor al llamador
    
    def listar_servicios(self) -> List[Servicio]:
        """Lista todos los servicios"""
        return list(self._servicios.values())  # devuelve el valor al llamador
    
    def crear_reserva(self, id_cliente: int, id_servicio: int,
                     duracion: float, descripcion: str = "", **kwargs) -> Reserva:
        """Crea una nueva reserva"""
        try:  # inicia un bloque de manejo de excepciones
            # Obtener cliente
            cliente = self.obtener_cliente(id_cliente)  # asigna un atributo del objeto
            if not cliente:  # evalúa una condición
                raise ReservaException(f"No existe cliente con ID {id_cliente}")  # lanza una excepción cuando ocurre un error
            
            if not cliente.activo:  # evalúa una condición
                raise ReservaException("El cliente está inactivo")  # lanza una excepción cuando ocurre un error
            
            # Obtener servicio
            servicio = self.obtener_servicio(id_servicio)  # asigna un atributo del objeto
            if not servicio:  # evalúa una condición
                raise ReservaException(f"No existe servicio con ID {id_servicio}")  # lanza una excepción cuando ocurre un error
            
            if not servicio.activo:  # evalúa una condición
                raise ReservaException("El servicio está inactivo")  # lanza una excepción cuando ocurre un error
            
            # Crear reserva
            reserva = Reserva(  # asigna un valor a una variable o atributo
                self._next_id_reserva,  # realiza la instrucción
                cliente, servicio, duracion, descripcion  # realiza la instrucción
            )  # realiza la instrucción
            
            # Procesar reserva con parámetros adicionales
            reserva.procesar(**kwargs)  # realiza la instrucción
            
            self._reservas[self._next_id_reserva] = reserva  # asigna un atributo del objeto
            self._next_id_reserva += 1  # asigna un atributo del objeto
            
            return reserva  # devuelve el valor al llamador
            
        except (ReservaException, ServicioException) as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error creando reserva: {e}")  # registra información en el log
            raise  # realiza la instrucción
        except Exception as e:  # captura la excepción producida en el bloque try
            gestor_logs.error("Error inesperado creando reserva", e)  # registra información en el log
            raise ReservaException(f"Error al crear reserva: {str(e)}") from e  # lanza una excepción cuando ocurre un error
    
    def obtener_reserva(self, id_reserva: int) -> Optional[Reserva]:
        """Obtiene una reserva por su ID"""
        return self._reservas.get(id_reserva)  # devuelve el valor al llamador
    
    def listar_reservas(self) -> List[Reserva]:
        """Lista todas las reservas"""
        return list(self._reservas.values())  # devuelve el valor al llamador
    
    def confirmar_reserva(self, id_reserva: int) -> bool:
        """Confirma una reserva"""
        try:  # inicia un bloque de manejo de excepciones
            reserva = self.obtener_reserva(id_reserva)  # asigna un atributo del objeto
            if not reserva:  # evalúa una condición
                raise ReservaException(f"No existe reserva con ID {id_reserva}")  # lanza una excepción cuando ocurre un error
            
            return reserva.confirmar()  # devuelve el valor al llamador
            
        except ReservaException as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error confirmando reserva: {e}")  # registra información en el log
            raise  # realiza la instrucción
    
    def cancelar_reserva(self, id_reserva: int) -> bool:
        """Cancela una reserva"""
        try:  # inicia un bloque de manejo de excepciones
            reserva = self.obtener_reserva(id_reserva)  # asigna un atributo del objeto
            if not reserva:  # evalúa una condición
                raise ReservaException(f"No existe reserva con ID {id_reserva}")  # lanza una excepción cuando ocurre un error
            
            return reserva.cancelar()  # devuelve el valor al llamador
            
        except ReservaException as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error cancelando reserva: {e}")  # registra información en el log
            raise  # realiza la instrucción
    
    def completar_reserva(self, id_reserva: int) -> bool:
        """Completa una reserva"""
        try:  # inicia un bloque de manejo de excepciones
            reserva = self.obtener_reserva(id_reserva)  # asigna un atributo del objeto
            if not reserva:  # evalúa una condición
                raise ReservaException(f"No existe reserva con ID {id_reserva}")  # lanza una excepción cuando ocurre un error
            
            return reserva.completar()  # devuelve el valor al llamador
            
        except ReservaException as e:  # captura la excepción producida en el bloque try
            gestor_logs.error(f"Error completando reserva: {e}")  # registra información en el log
            raise  # realiza la instrucción
    
    def guardar_datos(self, archivo: str = "software_fj_data.json"):
        """Guarda todos los datos en un archivo JSON"""
        try:  # inicia un bloque de manejo de excepciones
            self._next_id_cliente = max(self._next_id_cliente, max(self._clientes.keys(), default=0) + 1)  # asigna un atributo del objeto
            self._next_id_servicio = max(self._next_id_servicio, max(self._servicios.keys(), default=0) + 1)  # asigna un atributo del objeto
            self._next_id_reserva = max(self._next_id_reserva, max(self._reservas.keys(), default=0) + 1)  # asigna un atributo del objeto

            datos = {  # asigna un valor a una variable o atributo
                "clientes": [c.to_dict() for c in self._clientes.values()],  # realiza la instrucción
                "servicios": [s.to_dict() for s in self._servicios.values()],  # realiza la instrucción
                "reservas": [r.to_dict() for r in self._reservas.values()],  # realiza la instrucción
                "next_ids": {  # realiza la instrucción
                    "cliente": self._next_id_cliente,  # realiza la instrucción
                    "servicio": self._next_id_servicio,  # realiza la instrucción
                    "reserva": self._next_id_reserva  # realiza la instrucción
                }  # realiza la instrucción
            }  # realiza la instrucción
            
            with open(archivo, 'w', encoding='utf-8') as f:  # abre un contexto gestionado automáticamente
                json.dump(datos, f, indent=2, ensure_ascii=False)  # asigna un valor a una variable o atributo
            
            gestor_logs.info(f"Datos guardados en {archivo}")  # registra información en el log
            return True  # devuelve el valor al llamador
            
        except Exception as e:  # captura la excepción producida en el bloque try
            gestor_logs.error("Error guardando datos", e)  # registra información en el log
            raise DatosException(f"Error al guardar datos: {str(e)}") from e  # lanza una excepción cuando ocurre un error
    
    def cargar_datos(self, archivo: str = "software_fj_data.json"):
        """Carga los datos desde un archivo JSON"""
        try:  # inicia un bloque de manejo de excepciones
            if not os.path.exists(archivo):  # evalúa una condición
                gestor_logs.info(f"El archivo {archivo} no existe, se creará uno nuevo")  # registra información en el log
                return False  # devuelve el valor al llamador
            
            with open(archivo, 'r', encoding='utf-8') as f:  # abre un contexto gestionado automáticamente
                datos = json.load(f)  # asigna un valor a una variable o atributo
            
            # Cargar clientes
            self._clientes = {}  # asigna un atributo del objeto
            for c in datos.get("clientes", []):  # inicia un bucle para repetir instrucciones
                cliente = Cliente.from_dict(c)  # asigna un valor a una variable o atributo
                self._clientes[cliente.id] = cliente  # asigna un atributo del objeto
            
            self._servicios = {}  # asigna un atributo del objeto
            servicios_data = datos.get("servicios", [])  # asigna un valor a una variable o atributo
            if isinstance(servicios_data, dict):  # evalúa una condición
                servicios_data = list(servicios_data.values())  # asigna un valor a una variable o atributo
            servicios_data = servicios_data if len(servicios_data) else [  # asigna un valor a una variable o atributo
                {  # realiza la instrucción
                    "id": 1,  # realiza la instrucción
                    "nombre": "Sala A",  # realiza la instrucción
                    "descripcion": "Sala de reuniones con capacidad para 20 personas",  # realiza la instrucción
                    "capacidad": 20,  # realiza la instrucción
                    "precio": 50000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioReservaSala",  # realiza la instrucción
                },  # realiza la instrucción
                {  # realiza la instrucción
                    "id": 2,  # realiza la instrucción
                    "nombre": "Sala B",  # realiza la instrucción
                    "descripcion": "Sala de reuniones con capacidad para 20 personas",  # realiza la instrucción
                    "capacidad": 20,  # realiza la instrucción
                    "precio": 50000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioReservaSala",  # realiza la instrucción
                },  # realiza la instrucción
                {  # realiza la instrucción
                    "id": 3,  # realiza la instrucción
                    "nombre": "Sala C",  # realiza la instrucción
                    "descripcion": "Sala de reuniones con capacidad para 20 personas",  # realiza la instrucción
                    "capacidad": 20,  # realiza la instrucción
                    "precio": 50000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioReservaSala",  # realiza la instrucción
                },  # realiza la instrucción
                {  # realiza la instrucción
                    "id": 4,  # realiza la instrucción
                    "nombre": "Sala VIP",  # realiza la instrucción
                    "descripcion": "Sala VIP",  # realiza la instrucción
                    "capacidad": 10,  # realiza la instrucción
                    "precio": 250000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioReservaSala",  # realiza la instrucción
                },  # realiza la instrucción
                {  # realiza la instrucción
                    "id": 5,  # realiza la instrucción
                    "nombre": "PC GAMING",  # realiza la instrucción
                    "descripcion": "24 nucleos, 128GB RAM, RTX 4090",  # realiza la instrucción
                    "capacidad": 0,  # realiza la instrucción
                    "precio": 150000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioAlquilerEquipo",  # realiza la instrucción
                },  # realiza la instrucción
                # Nuevos equipos
                {  # realiza la instrucción
                    "id": 6,  # realiza la instrucción
                    "nombre": "Workstation Diseño",  # realiza la instrucción
                    "descripcion": "Intel Xeon, 64GB RAM, Quadro RTX",  # realiza la instrucción
                    "capacidad": 0,  # realiza la instrucción
                    "precio": 120000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioAlquilerEquipo",  # realiza la instrucción
                },  # realiza la instrucción
                {  # realiza la instrucción
                    "id": 7,  # realiza la instrucción
                    "nombre": "Servidor Virtual",  # realiza la instrucción
                    "descripcion": "Servidor dedicado con 32 cores y 256GB RAM",  # realiza la instrucción
                    "capacidad": 0,  # realiza la instrucción
                    "precio": 200000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioAlquilerEquipo",  # realiza la instrucción
                },  # realiza la instrucción
                {  # realiza la instrucción
                    "id": 8,  # realiza la instrucción
                    "nombre": "Laptop Ultrabook",  # realiza la instrucción
                    "descripcion": "Core i7, 16GB RAM, SSD 1TB",  # realiza la instrucción
                    "capacidad": 0,  # realiza la instrucción
                    "precio": 80000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioAlquilerEquipo",  # realiza la instrucción
                },  # realiza la instrucción
                {  # realiza la instrucción
                    "id": 9,  # realiza la instrucción
                    "nombre": "Equipo VR",  # realiza la instrucción
                    "descripcion": "Set completo Oculus Quest Pro",  # realiza la instrucción
                    "capacidad": 0,  # realiza la instrucción
                    "precio": 100000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioAlquilerEquipo",  # realiza la instrucción
                },  # realiza la instrucción
                {  # realiza la instrucción
                    "id": 10,  # realiza la instrucción
                    "nombre": "Impresora 3D",  # realiza la instrucción
                    "descripcion": "Impresora 3D industrial para prototipado",  # realiza la instrucción
                    "capacidad": 0,  # realiza la instrucción
                    "precio": 130000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioAlquilerEquipo",  # realiza la instrucción
                },  # realiza la instrucción
                {  # realiza la instrucción
                    "id": 11,  # realiza la instrucción
                    "nombre": "Asesoria Legal",  # realiza la instrucción
                    "descripcion": "Consultoría legal especializada",  # realiza la instrucción
                    "capacidad": 5,  # realiza la instrucción
                    "precio": 120000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioAsesoria",  # realiza la instrucción
                },  # realiza la instrucción
                {  # realiza la instrucción
                    "id": 12,  # realiza la instrucción
                    "nombre": "Asesoria Contable",  # realiza la instrucción
                    "descripcion": "Consultoría en gestión contable y tributaria",  # realiza la instrucción
                    "capacidad": 5,  # realiza la instrucción
                    "precio": 100000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioAsesoria",  # realiza la instrucción
                },  # realiza la instrucción
                {  # realiza la instrucción
                    "id": 13,  # realiza la instrucción
                    "nombre": "Asesoria en Recursos Humanos",  # realiza la instrucción
                    "descripcion": "Consultoría en gestión de talento humano",  # realiza la instrucción
                    "capacidad": 5,  # realiza la instrucción
                    "precio": 90000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioAsesoria",  # realiza la instrucción
                },  # realiza la instrucción
                {  # realiza la instrucción
                    "id": 14,  # realiza la instrucción
                    "nombre": "Asesoria en Marketing",  # realiza la instrucción
                    "descripcion": "Consultoría en estrategias de marketing digital",  # realiza la instrucción
                    "capacidad": 5,  # realiza la instrucción
                    "precio": 85000,  # realiza la instrucción
                    "activo": True,  # realiza la instrucción
                    "tipo": "ServicioAsesoria",  # realiza la instrucción
                },  # realiza la instrucción
            ]  # realiza la instrucción
            for s in servicios_data:  # inicia un bucle para repetir instrucciones
                constructor = entidades.get(s.get("tipo"))  # asigna un valor a una variable o atributo
                if not constructor:  # evalúa una condición
                    continue  # realiza la instrucción
                servicio = constructor(**s)  # asigna un valor a una variable o atributo
                self._servicios[servicio.id] = servicio  # asigna un atributo del objeto
            print(f"Servicios: {self._servicios}")  # muestra información en pantalla

            # Cargar reservas (requiere reconstruir referencias)
            self._reservas = {}  # asigna un atributo del objeto
            for r in datos.get("reservas", []):  # inicia un bucle para repetir instrucciones
                cliente = self.obtener_cliente(r["cliente_id"])  # asigna un atributo del objeto
                servicio = self.obtener_servicio(r["servicio_id"])  # asigna un atributo del objeto
                
                if cliente and servicio:  # evalúa una condición
                    reserva = Reserva(  # asigna un valor a una variable o atributo
                        r["id"], cliente, servicio,  # realiza la instrucción
                        r["duracion"], r.get("descripcion", "")  # realiza la instrucción
                    )  # realiza la instrucción
                    reserva._estado = r.get("estado", "pendiente")  # asigna un valor a una variable o atributo
                    reserva._costo_total = r.get("costo_total", 0)  # asigna un valor a una variable o atributo
                    self._reservas[r["id"]] = reserva  # asigna un atributo del objeto
            
            # Restaurar IDs
            ids = datos.get("next_ids", {})  # asigna un valor a una variable o atributo
            self._next_id_cliente = max(max(self._clientes.keys(), default=0) + 1,  # asigna un atributo del objeto
                                        ids.get("cliente", 1))  # realiza la instrucción
            self._next_id_servicio = max(max(self._servicios.keys(), default=0) + 1,  # asigna un atributo del objeto
                                         ids.get("servicio", 1))  # realiza la instrucción
            self._next_id_reserva = max(max(self._reservas.keys(), default=0) + 1,  # asigna un atributo del objeto
                                        ids.get("reserva", 1))  # realiza la instrucción
            
            gestor_logs.info(f"Datos cargados desde {archivo}")  # registra información en el log
            return True  # devuelve el valor al llamador
            
        except Exception as e:  # captura la excepción producida en el bloque try
            gestor_logs.error("Error cargando datos", e)  # registra información en el log
            raise DatosException(f"Error al cargar datos: {str(e)}") from e  # lanza una excepción cuando ocurre un error

class InterfazSoftwareFJ:
    """Interfaz gráfica del sistema usando Tkinter"""
    
    def __init__(self, root):
        """Función o método __init__."""
        self.root = root  # asigna un atributo del objeto
        self.root.title("Software FJ - Sistema de Gestión")  # realiza la instrucción
        self.root.geometry("1000x700")  # realiza la instrucción
        
        # Sistema backend
        self.sistema = SistemaSoftwareFJ()  # asigna un atributo del objeto
        
        # Cargar datos existentes
        try:  # inicia un bloque de manejo de excepciones
            self.sistema.cargar_datos()  # realiza la instrucción
        except:  # realiza la instrucción
            pass  # no realiza ninguna acción
        
        # Configurar interfaz
        self.configurar_interfaz()  # realiza la instrucción
        
        # Cargar datos iniciales
        self.actualizar_vistas()  # realiza la instrucción
    
    def configurar_interfaz(self):
        """
        Configura los elementos de la interfaz
        """
        
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding="10")  # asigna un atributo del objeto
        self.main_frame.pack(fill=tk.BOTH, expand=True)  # asigna un atributo del objeto
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame)  # asigna un atributo del objeto
        self.notebook.pack(fill=tk.BOTH, expand=True)  # asigna un atributo del objeto
        
        # Pestañas
        self.crear_pestana_clientes()  # realiza la instrucción
        self.crear_pestana_servicios()  # realiza la instrucción
        self.crear_pestana_reservas()  # realiza la instrucción
        
        # Barra de estado
        self.estado = ttk.Label(self.root, text="Sistema listo", relief=tk.SUNKEN, anchor=tk.W)  # asigna un atributo del objeto
        self.estado.pack(fill=tk.X)  # asigna un atributo del objeto
    
    def crear_pestana_clientes(self):
        """Crea la pestaña de clientes"""
        frame = ttk.Frame(self.notebook)  # asigna un atributo del objeto
        self.notebook.add(frame, text="Clientes")  # asigna un atributo del objeto
        
        # Frame de formulario
        form_frame = ttk.LabelFrame(frame, text="Datos del Cliente", padding="10")  # asigna un valor a una variable o atributo
        form_frame.pack(fill=tk.X, padx=5, pady=5)  # asigna un valor a una variable o atributo
        
        # Campos
        ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=2)  # asigna un valor a una variable o atributo
        self.entry_nombre = ttk.Entry(form_frame, width=30)  # asigna un atributo del objeto
        self.entry_nombre.grid(row=0, column=1, pady=2, padx=5)  # asigna un atributo del objeto
        
        ttk.Label(form_frame, text="Apellido:").grid(row=1, column=0, sticky=tk.W, pady=2)  # asigna un valor a una variable o atributo
        self.entry_apellido = ttk.Entry(form_frame, width=30)  # asigna un atributo del objeto
        self.entry_apellido.grid(row=1, column=1, pady=2, padx=5)  # asigna un atributo del objeto
        
        ttk.Label(form_frame, text="Identificación:").grid(row=2, column=0, sticky=tk.W, pady=2)  # asigna un valor a una variable o atributo
        self.entry_identificacion = ttk.Entry(form_frame, width=30)  # asigna un atributo del objeto
        self.entry_identificacion.grid(row=2, column=1, pady=2, padx=5)  # asigna un atributo del objeto
        
        ttk.Label(form_frame, text="Teléfono:").grid(row=3, column=0, sticky=tk.W, pady=2)  # asigna un valor a una variable o atributo
        self.entry_telefono = ttk.Entry(form_frame, width=30)  # asigna un atributo del objeto
        self.entry_telefono.grid(row=3, column=1, pady=2, padx=5)  # asigna un atributo del objeto
        
        ttk.Label(form_frame, text="Email:").grid(row=4, column=0, sticky=tk.W, pady=2)  # asigna un valor a una variable o atributo
        self.entry_email = ttk.Entry(form_frame, width=30)  # asigna un atributo del objeto
        self.entry_email.grid(row=4, column=1, pady=2, padx=5)  # asigna un atributo del objeto
        
        # Botones
        btn_frame = ttk.Frame(form_frame)  # asigna un valor a una variable o atributo
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)  # asigna un valor a una variable o atributo
        ttk.Button(btn_frame, text="Agregar Cliente", command=self.agregar_cliente).pack(side=tk.LEFT, padx=5)  # asigna un atributo del objeto
        ttk.Button(btn_frame, text="Editar", command=self.editar_cliente).pack(side=tk.LEFT, padx=5)  # asigna un atributo del objeto
        ttk.Button(btn_frame, text="Eliminar", command=self.eliminar_cliente).pack(side=tk.LEFT, padx=5)  # asigna un atributo del objeto
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_formulario_cliente).pack(side=tk.LEFT, padx=5)  # asigna un atributo del objeto
        
        # Treeview
        tree_frame = ttk.Frame(frame)  # asigna un valor a una variable o atributo
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  # asigna un valor a una variable o atributo
        
        self.tree_clientes = ttk.Treeview(tree_frame, columns=("ID", "Nombre", "Apellido", "Identificación", "Teléfono", "Email"), show="headings")  # asigna un atributo del objeto
        for col in ("ID", "Nombre", "Apellido", "Identificación", "Teléfono", "Email"):  # inicia un bucle para repetir instrucciones
            self.tree_clientes.heading(col, text=col)  # asigna un atributo del objeto
            self.tree_clientes.column(col, width=100)  # asigna un atributo del objeto
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_clientes.yview)  # asigna un atributo del objeto
        self.tree_clientes.configure(yscrollcommand=scrollbar.set)  # asigna un atributo del objeto
        self.tree_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # asigna un atributo del objeto
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # asigna un valor a una variable o atributo
    
    def crear_pestana_servicios(self):
        """Crea la pestaña de servicios"""
        frame = ttk.Frame(self.notebook)  # asigna un atributo del objeto
        self.notebook.add(frame, text="Servicios")  # asigna un atributo del objeto

        # Frame de tabla de servicios
        table_frame = ttk.LabelFrame(frame, text="Elementos de Servicios", padding="10")  # asigna un valor a una variable o atributo
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  # asigna un valor a una variable o atributo

        # Treeview para mostrar servicios en tabla
        self.tree_servicios = ttk.Treeview(table_frame, columns=("Tipo", "Elemento", "Precio/Hora"), show="headings")  # asigna un atributo del objeto
        self.tree_servicios.heading("Tipo", text="Tipo de Servicio")  # asigna un atributo del objeto
        self.tree_servicios.heading("Elemento", text="Elemento")  # asigna un atributo del objeto
        self.tree_servicios.heading("Precio/Hora", text="Precio/Hora")  # asigna un atributo del objeto
        
        self.tree_servicios.column("Tipo", width=200)  # asigna un atributo del objeto
        self.tree_servicios.column("Elemento", width=150)  # asigna un atributo del objeto
        self.tree_servicios.column("Precio/Hora", width=120)  # asigna un atributo del objeto

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree_servicios.yview)  # asigna un atributo del objeto
        self.tree_servicios.configure(yscrollcommand=scrollbar.set)  # asigna un atributo del objeto
        self.tree_servicios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # asigna un atributo del objeto
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # asigna un valor a una variable o atributo

        # Botones de acción
        btn_frame = ttk.Frame(frame)  # asigna un valor a una variable o atributo
        btn_frame.pack(fill=tk.X, padx=5, pady=5)  # asigna un valor a una variable o atributo
        ttk.Button(btn_frame, text="Editar", command=self.editar_servicio).pack(side=tk.LEFT, padx=5)  # asigna un atributo del objeto
        ttk.Button(btn_frame, text="Eliminar", command=self.eliminar_servicio).pack(side=tk.LEFT, padx=5)  # asigna un atributo del objeto
        ttk.Button(btn_frame, text="Actualizar", command=self.actualizar_vista_servicios).pack(side=tk.LEFT, padx=5)  # asigna un atributo del objeto
    
    def crear_pestana_reservas(self):
        """Crea la pestaña de reservas"""
        frame = ttk.Frame(self.notebook)  # asigna un atributo del objeto
        self.notebook.add(frame, text="Reservas")  # asigna un atributo del objeto
        
        # Frame de formulario
        form_frame = ttk.LabelFrame(frame, text="Nueva Reserva", padding="10")  # asigna un valor a una variable o atributo
        form_frame.pack(fill=tk.X, padx=5, pady=5)  # asigna un valor a una variable o atributo
        
        # Cliente
        ttk.Label(form_frame, text="Cliente:").grid(row=0, column=0, sticky=tk.W, pady=2)  # asigna un valor a una variable o atributo
        self.combo_cliente = ttk.Combobox(form_frame, width=28)  # asigna un atributo del objeto
        self.combo_cliente.grid(row=0, column=1, pady=2, padx=5)  # asigna un atributo del objeto
        
        # Servicio
        ttk.Label(form_frame, text="Servicio:").grid(row=1, column=0, sticky=tk.W, pady=2)  # asigna un valor a una variable o atributo
        self.combo_servicio = ttk.Combobox(form_frame, width=28)  # asigna un atributo del objeto
        self.combo_servicio.grid(row=1, column=1, pady=2, padx=5)  # asigna un atributo del objeto
        
        # Duración
        ttk.Label(form_frame, text="Duración (horas):").grid(row=2, column=0, sticky=tk.W, pady=2)  # asigna un valor a una variable o atributo
        self.entry_duracion = ttk.Entry(form_frame, width=30)  # asigna un atributo del objeto
        self.entry_duracion.grid(row=2, column=1, pady=2, padx=5)  # asigna un atributo del objeto
        
        # Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=3, column=0, sticky=tk.W, pady=2)  # asigna un valor a una variable o atributo
        self.entry_descripcion = ttk.Entry(form_frame, width=30)  # asigna un atributo del objeto
        self.entry_descripcion.grid(row=3, column=1, pady=2, padx=5)  # asigna un atributo del objeto
        
        # Botones
        btn_frame = ttk.Frame(form_frame)  # asigna un valor a una variable o atributo
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)  # asigna un valor a una variable o atributo
        ttk.Button(btn_frame, text="Crear Reserva", command=self.crear_reserva).pack(side=tk.LEFT, padx=5)  # asigna un atributo del objeto
        ttk.Button(btn_frame, text="Confirmar", command=self.confirmar_reserva).pack(side=tk.LEFT, padx=5)  # asigna un atributo del objeto
        ttk.Button(btn_frame, text="Cancelar", command=self.cancelar_reserva).pack(side=tk.LEFT, padx=5)  # asigna un atributo del objeto
        ttk.Button(btn_frame, text="Completar", command=self.completar_reserva).pack(side=tk.LEFT, padx=5)  # asigna un atributo del objeto
        ttk.Button(btn_frame, text="Editar", command=self.editar_reserva).pack(side=tk.LEFT, padx=5)  # asigna un atributo del objeto
        
        # Treeview
        tree_frame = ttk.Frame(frame)  # asigna un valor a una variable o atributo
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)  # asigna un valor a una variable o atributo
        
        self.tree_reservas = ttk.Treeview(tree_frame, columns=("ID", "Cliente", "Servicio", "Duración", "Estado", "Costo"), show="headings")  # asigna un atributo del objeto
        for col in ("ID", "Cliente", "Servicio", "Duración", "Estado", "Costo"):  # inicia un bucle para repetir instrucciones
            self.tree_reservas.heading(col, text=col)  # asigna un atributo del objeto
            self.tree_reservas.column(col, width=100)  # asigna un atributo del objeto
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_reservas.yview)  # asigna un atributo del objeto
        self.tree_reservas.configure(yscrollcommand=scrollbar.set)  # asigna un atributo del objeto
        self.tree_reservas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # asigna un atributo del objeto
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # asigna un valor a una variable o atributo
    
    # -------------------------------------------------------------------------
    # Métodos de acción
    # -------------------------------------------------------------------------
    
    def agregar_cliente(self):
        """Agrega un nuevo cliente"""
        try:  # inicia un bloque de manejo de excepciones
            cliente = self.sistema.crear_cliente(  # asigna un atributo del objeto
                self.entry_nombre.get(),  # realiza la instrucción
                self.entry_apellido.get(),  # realiza la instrucción
                self.entry_identificacion.get(),  # realiza la instrucción
                self.entry_telefono.get(),  # realiza la instrucción
                self.entry_email.get()  # realiza la instrucción
            )  # realiza la instrucción
            self.actualizar_vistas()  # realiza la instrucción
            self.limpiar_formulario_cliente()  # realiza la instrucción
            self.guardar_datos()  # Guardar automáticamente en JSON
            self.actualizar_estado(f"Cliente '{cliente.nombre} {cliente.apellido}' creado exitosamente")  # realiza la instrucción
            messagebox.showinfo("Éxito", f"Cliente creado con ID: {cliente.id}")  # realiza la instrucción
            
        except (ValidacionException, ClienteException) as e:  # captura la excepción producida en el bloque try
            messagebox.showerror("Error", str(e))  # realiza la instrucción
            self.actualizar_estado(f"Error: {str(e)}")  # realiza la instrucción
    
    def limpiar_formulario_cliente(self):
        """Limpia el formulario de cliente"""
        self.entry_nombre.delete(0, tk.END)  # realiza la instrucción
        self.entry_apellido.delete(0, tk.END)  # realiza la instrucción
        self.entry_identificacion.delete(0, tk.END)  # realiza la instrucción
        self.entry_telefono.delete(0, tk.END)  # realiza la instrucción
        self.entry_email.delete(0, tk.END)  # realiza la instrucción
    
    def editar_cliente(self):
        """Edita el cliente seleccionado"""
        try:  # inicia un bloque de manejo de excepciones
            seleccion = self.tree_clientes.selection()  # asigna un atributo del objeto
            if not seleccion:  # evalúa una condición
                raise ClienteException("Seleccione un cliente")  # lanza una excepción cuando ocurre un error
            
            item = self.tree_clientes.item(seleccion[0])  # asigna un atributo del objeto
            id_cliente = int(item["values"][0])  # asigna un valor a una variable o atributo
            
            cliente = self.sistema.obtener_cliente(id_cliente)  # asigna un atributo del objeto
            if not cliente:  # evalúa una condición
                raise ClienteException("Cliente no encontrado")  # lanza una excepción cuando ocurre un error
            
            # Crear diálogo para editar
            dialog = tk.Toplevel(self.root)  # asigna un atributo del objeto
            dialog.title("Editar Cliente")  # realiza la instrucción
            dialog.geometry("400x350")  # realiza la instrucción
            dialog.transient(self.root)  # realiza la instrucción
            dialog.grab_set()  # realiza la instrucción
            
            # Frame del formulario
            form_frame = ttk.Frame(dialog, padding="20")  # asigna un valor a una variable o atributo
            form_frame.pack(fill=tk.BOTH, expand=True)  # asigna un valor a una variable o atributo
            
            ttk.Label(form_frame, text="Nombre:").grid(row=0, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            entry_nombre = ttk.Entry(form_frame, width=25)  # asigna un valor a una variable o atributo
            entry_nombre.grid(row=0, column=1, pady=5, padx=5)  # asigna un valor a una variable o atributo
            entry_nombre.insert(0, cliente.nombre)  # realiza la instrucción
            
            ttk.Label(form_frame, text="Apellido:").grid(row=1, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            entry_apellido = ttk.Entry(form_frame, width=25)  # asigna un valor a una variable o atributo
            entry_apellido.grid(row=1, column=1, pady=5, padx=5)  # asigna un valor a una variable o atributo
            entry_apellido.insert(0, cliente.apellido)  # realiza la instrucción
            
            ttk.Label(form_frame, text="Teléfono:").grid(row=2, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            entry_telefono = ttk.Entry(form_frame, width=25)  # asigna un valor a una variable o atributo
            entry_telefono.grid(row=2, column=1, pady=5, padx=5)  # asigna un valor a una variable o atributo
            entry_telefono.insert(0, cliente.telefono)  # realiza la instrucción
            
            ttk.Label(form_frame, text="Email:").grid(row=3, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            entry_email = ttk.Entry(form_frame, width=25)  # asigna un valor a una variable o atributo
            entry_email.grid(row=3, column=1, pady=5, padx=5)  # asigna un valor a una variable o atributo
            entry_email.insert(0, cliente.email)  # realiza la instrucción
            
            ttk.Label(form_frame, text="Identificación:").grid(row=4, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            ttk.Label(form_frame, text=cliente.identificacion).grid(row=4, column=1, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            
            def guardar_cambio():
                """Función o método guardar_cambio."""
                try:  # inicia un bloque de manejo de excepciones
                    self.sistema.actualizar_cliente(  # realiza la instrucción
                        id_cliente,  # realiza la instrucción
                        nombre=entry_nombre.get(),  # asigna un valor a una variable o atributo
                        apellido=entry_apellido.get(),  # asigna un valor a una variable o atributo
                        telefono=entry_telefono.get(),  # asigna un valor a una variable o atributo
                        email=entry_email.get()  # asigna un valor a una variable o atributo
                    )  # realiza la instrucción
                    self.actualizar_vista_clientes()  # realiza la instrucción
                    self.guardar_datos()  # Guardar automáticamente en JSON
                    self.actualizar_estado(f"Cliente {id_cliente} actualizado")  # realiza la instrucción
                    messagebox.showinfo("Éxito", "Cliente actualizado correctamente")  # realiza la instrucción
                    dialog.destroy()  # realiza la instrucción
                    
                except (ValidacionException, ClienteException) as e:  # captura la excepción producida en el bloque try
                    messagebox.showerror("Error", str(e))  # realiza la instrucción
            
            btn_frame = ttk.Frame(form_frame)  # asigna un valor a una variable o atributo
            btn_frame.grid(row=5, column=0, columnspan=2, pady=20)  # asigna un valor a una variable o atributo
            ttk.Button(btn_frame, text="Guardar", command=guardar_cambio).pack(side=tk.LEFT, padx=5)  # asigna un valor a una variable o atributo
            ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)  # asigna un valor a una variable o atributo
            
        except ClienteException as e:  # captura la excepción producida en el bloque try
            messagebox.showerror("Error", str(e))  # realiza la instrucción
    
    def eliminar_cliente(self):
        """Elimina el cliente seleccionado"""
        try:  # inicia un bloque de manejo de excepciones
            seleccion = self.tree_clientes.selection()  # asigna un atributo del objeto
            if not seleccion:  # evalúa una condición
                raise ClienteException("Seleccione un cliente")  # lanza una excepción cuando ocurre un error
            
            item = self.tree_clientes.item(seleccion[0])  # asigna un atributo del objeto
            id_cliente = int(item["values"][0])  # asigna un valor a una variable o atributo
            nombre = item["values"][1]  # asigna un valor a una variable o atributo
            apellido = item["values"][2]  # asigna un valor a una variable o atributo
            
            respuesta = messagebox.askyesno(  # asigna un valor a una variable o atributo
                "Confirmar eliminación",  # realiza la instrucción
                f"¿Está seguro de eliminar al cliente {nombre} {apellido}?"  # realiza la instrucción
            )  # realiza la instrucción
            
            if respuesta:  # evalúa una condición
                self.sistema.eliminar_cliente(id_cliente)  # realiza la instrucción
                self.actualizar_vista_clientes()  # realiza la instrucción
                self.guardar_datos()  # Guardar automáticamente en JSON
                self.actualizar_estado(f"Cliente {id_cliente} eliminado")  # realiza la instrucción
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")  # realiza la instrucción
                
        except ClienteException as e:  # captura la excepción producida en el bloque try
            messagebox.showerror("Error", str(e))  # realiza la instrucción
    
    def crear_reserva(self):
        """Crea una nueva reserva"""
        try:  # inicia un bloque de manejo de excepciones
            # Obtener IDs seleccionados
            cliente_texto = self.combo_cliente.get()  # asigna un atributo del objeto
            servicio_texto = self.combo_servicio.get()  # asigna un atributo del objeto
            
            if not cliente_texto or not servicio_texto:  # evalúa una condición
                raise ReservaException("Debe seleccionar cliente y servicio")  # lanza una excepción cuando ocurre un error
            
            id_cliente = int(cliente_texto.split("-")[0].strip())  # asigna un valor a una variable o atributo
            id_servicio = int(servicio_texto.split("-")[0].strip())  # asigna un valor a una variable o atributo
            duracion = float(self.entry_duracion.get())  # asigna un atributo del objeto
            descripcion = self.entry_descripcion.get()  # asigna un atributo del objeto
            
            reserva = self.sistema.crear_reserva(  # asigna un atributo del objeto
                id_cliente, id_servicio, duracion, descripcion  # realiza la instrucción
            )  # realiza la instrucción
            
            self.actualizar_vistas()  # realiza la instrucción
            self.guardar_datos()  # Guardar automáticamente en JSON
            self.actualizar_estado(f"Reserva #{reserva.id} creada - Costo: ${reserva.costo_total:,.2f}")
            messagebox.showinfo("Éxito", f"Reserva creada con ID: {reserva.id}\nCosto: ${reserva.costo_total:,.2f}")  # realiza la instrucción
            
        except (ReservaException, ValueError) as e:  # captura la excepción producida en el bloque try
            messagebox.showerror("Error", str(e))  # realiza la instrucción
            self.actualizar_estado(f"Error: {str(e)}")  # realiza la instrucción
    
    def confirmar_reserva(self):
        """Confirma la reserva seleccionada"""
        try:  # inicia un bloque de manejo de excepciones
            seleccion = self.tree_reservas.selection()  # asigna un atributo del objeto
            if not seleccion:  # evalúa una condición
                raise ReservaException("Seleccione una reserva")  # lanza una excepción cuando ocurre un error
            
            item = self.tree_reservas.item(seleccion[0])  # asigna un atributo del objeto
            id_reserva = int(item["values"][0])  # asigna un valor a una variable o atributo
            
            self.sistema.confirmar_reserva(id_reserva)  # realiza la instrucción
            self.actualizar_vistas()  # realiza la instrucción
            self.guardar_datos()  # Guardar automáticamente en JSON
            self.actualizar_estado(f"Reserva #{id_reserva} confirmada")
            messagebox.showinfo("Éxito", "Reserva confirmada")  # realiza la instrucción
            
        except ReservaException as e:  # captura la excepción producida en el bloque try
            messagebox.showerror("Error", str(e))  # realiza la instrucción
    
    def cancelar_reserva(self):
        """Cancela la reserva seleccionada"""
        try:  # inicia un bloque de manejo de excepciones
            seleccion = self.tree_reservas.selection()  # asigna un atributo del objeto
            if not seleccion:  # evalúa una condición
                raise ReservaException("Seleccione una reserva")  # lanza una excepción cuando ocurre un error
            
            item = self.tree_reservas.item(seleccion[0])  # asigna un atributo del objeto
            id_reserva = int(item["values"][0])  # asigna un valor a una variable o atributo
            
            self.sistema.cancelar_reserva(id_reserva)  # realiza la instrucción
            self.actualizar_vistas()  # realiza la instrucción
            self.guardar_datos()  # Guardar automáticamente en JSON
            self.actualizar_estado(f"Reserva #{id_reserva} cancelada")
            messagebox.showinfo("Éxito", "Reserva cancelada")  # realiza la instrucción
            
        except ReservaException as e:  # captura la excepción producida en el bloque try
            messagebox.showerror("Error", str(e))  # realiza la instrucción
    
    def completar_reserva(self):
        """Completa la reserva seleccionada"""
        try:  # inicia un bloque de manejo de excepciones
            seleccion = self.tree_reservas.selection()  # asigna un atributo del objeto
            if not seleccion:  # evalúa una condición
                raise ReservaException("Seleccione una reserva")  # lanza una excepción cuando ocurre un error
            
            item = self.tree_reservas.item(seleccion[0])  # asigna un atributo del objeto
            id_reserva = int(item["values"][0])  # asigna un valor a una variable o atributo
            
            self.sistema.completar_reserva(id_reserva)  # realiza la instrucción
            self.actualizar_vistas()  # realiza la instrucción
            self.guardar_datos()  # Guardar automáticamente en JSON
            self.actualizar_estado(f"Reserva #{id_reserva} completada")
            messagebox.showinfo("Éxito", "Reserva completada")  # realiza la instrucción
            
        except ReservaException as e:  # captura la excepción producida en el bloque try
            messagebox.showerror("Error", str(e))  # realiza la instrucción
    
    def editar_reserva(self):
        """Edita la reserva seleccionada"""
        try:  # inicia un bloque de manejo de excepciones
            seleccion = self.tree_reservas.selection()  # asigna un atributo del objeto
            if not seleccion:  # evalúa una condición
                raise ReservaException("Seleccione una reserva")  # lanza una excepción cuando ocurre un error
            
            item = self.tree_reservas.item(seleccion[0])  # asigna un atributo del objeto
            id_reserva = int(item["values"][0])  # asigna un valor a una variable o atributo
            
            reserva = self.sistema.obtener_reserva(id_reserva)  # asigna un atributo del objeto
            if not reserva:  # evalúa una condición
                raise ReservaException("Reserva no encontrada")  # lanza una excepción cuando ocurre un error
            
            # Crear diálogo para editar
            dialog = tk.Toplevel(self.root)  # asigna un atributo del objeto
            dialog.title("Editar Reserva")  # realiza la instrucción
            dialog.geometry("400x300")  # realiza la instrucción
            dialog.transient(self.root)  # realiza la instrucción
            dialog.grab_set()  # realiza la instrucción
            
            # Frame del formulario
            form_frame = ttk.Frame(dialog, padding="20")  # asigna un valor a una variable o atributo
            form_frame.pack(fill=tk.BOTH, expand=True)  # asigna un valor a una variable o atributo
            
            ttk.Label(form_frame, text="Cliente:").grid(row=0, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            ttk.Label(form_frame, text=f"{reserva.cliente.nombre} {reserva.cliente.apellido}").grid(row=0, column=1, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            
            ttk.Label(form_frame, text="Servicio:").grid(row=1, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            ttk.Label(form_frame, text=reserva.servicio.nombre).grid(row=1, column=1, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            
            ttk.Label(form_frame, text="Duración (horas):").grid(row=2, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            entry_duracion = ttk.Entry(form_frame, width=25)  # asigna un valor a una variable o atributo
            entry_duracion.grid(row=2, column=1, pady=5, padx=5)  # asigna un valor a una variable o atributo
            entry_duracion.insert(0, str(reserva.duracion))  # realiza la instrucción
            
            ttk.Label(form_frame, text="Descripción:").grid(row=3, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            entry_descripcion = ttk.Entry(form_frame, width=25)  # asigna un valor a una variable o atributo
            entry_descripcion.grid(row=3, column=1, pady=5, padx=5)  # asigna un valor a una variable o atributo
            entry_descripcion.insert(0, reserva.descripcion)  # realiza la instrucción
            
            ttk.Label(form_frame, text="Estado actual:").grid(row=4, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            ttk.Label(form_frame, text=reserva.estado).grid(row=4, column=1, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            
            def guardar_cambio():
                """Función o método guardar_cambio."""
                try:  # inicia un bloque de manejo de excepciones
                    reserva.duracion = float(entry_duracion.get())  # asigna un valor a una variable o atributo
                    reserva._descripcion = entry_descripcion.get()  # asigna un valor a una variable o atributo
                    # Reprocesar el costo
                    reserva.procesar()  # realiza la instrucción
                    self.actualizar_vista_reservas()  # realiza la instrucción
                    self.guardar_datos()  # Guardar automáticamente en JSON
                    self.actualizar_estado(f"Reserva {id_reserva} actualizada")  # realiza la instrucción
                    messagebox.showinfo("Éxito", "Reserva actualizada correctamente")  # realiza la instrucción
                    dialog.destroy()  # realiza la instrucción
                    
                except (ReservaException, ValueError) as e:  # captura la excepción producida en el bloque try
                    messagebox.showerror("Error", str(e))  # realiza la instrucción
            
            btn_frame = ttk.Frame(form_frame)  # asigna un valor a una variable o atributo
            btn_frame.grid(row=5, column=0, columnspan=2, pady=20)  # asigna un valor a una variable o atributo
            ttk.Button(btn_frame, text="Guardar", command=guardar_cambio).pack(side=tk.LEFT, padx=5)  # asigna un valor a una variable o atributo
            ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)  # asigna un valor a una variable o atributo
            
        except ReservaException as e:  # captura la excepción producida en el bloque try
            messagebox.showerror("Error", str(e))  # realiza la instrucción
    
    def guardar_datos(self, mostrar_mensaje: bool = False):
        """Guarda los datos en JSON"""
        try:  # inicia un bloque de manejo de excepciones
            self.sistema.guardar_datos()  # realiza la instrucción
            if mostrar_mensaje:  # evalúa una condición
                self.actualizar_estado("Datos guardados exitosamente")  # realiza la instrucción
                messagebox.showinfo("Éxito", "Datos guardados en software_fj_data.json")  # realiza la instrucción
        except DatosException as e:  # captura la excepción producida en el bloque try
            if mostrar_mensaje:  # evalúa una condición
                messagebox.showerror("Error", str(e))  # realiza la instrucción
    
    def actualizar_vistas(self):
        """Actualiza todas las vistas"""
        self.actualizar_vista_clientes()  # realiza la instrucción
        self.actualizar_vista_servicios()  # realiza la instrucción
        self.actualizar_vista_reservas()  # realiza la instrucción
    
    def actualizar_vista_clientes(self):
        """Actualiza la vista de clientes"""
        for item in self.tree_clientes.get_children():  # inicia un bucle para repetir instrucciones
            self.tree_clientes.delete(item)  # realiza la instrucción
        
        for cliente in self.sistema.listar_clientes():  # inicia un bucle para repetir instrucciones
            if cliente.activo:  # evalúa una condición
                self.tree_clientes.insert("", tk.END, values=(  # asigna un atributo del objeto
                    cliente.id,  # realiza la instrucción
                    cliente.nombre,  # realiza la instrucción
                    cliente.apellido,  # realiza la instrucción
                    cliente.identificacion,  # realiza la instrucción
                    cliente.telefono,  # realiza la instrucción
                    cliente.email  # realiza la instrucción
                ))  # realiza la instrucción
        
        # Actualizar combobox
        clientes = [f"{c.id} - {c.nombre} {c.apellido}" for c in self.sistema.listar_clientes() if c.activo]  # asigna un atributo del objeto
        self.combo_cliente["values"] = clientes  # asigna un atributo del objeto
    
    def actualizar_vista_servicios(self):
        """Actualiza la vista de servicios con tabla organizada por tipo y precio"""
        # Limpiar tabla
        for item in self.tree_servicios.get_children():  # inicia un bucle para repetir instrucciones
            self.tree_servicios.delete(item)  # realiza la instrucción
        
        
        # Recolectar todos los elementos de servicios
        elementos = []  # asigna un valor a una variable o atributo
        
        for servicio in self.sistema.listar_servicios():  # inicia un bucle para repetir instrucciones
            s = servicio.to_dict()  # asigna un valor a una variable o atributo
            s['elemento'] = s.pop('nombre')  # Para mostrar el nombre del servicio como elemento
            elementos.append(s)  # realiza la instrucción
        # Ordenar por tipo y luego por precio
        elementos.sort(key=lambda x: (x["tipo"], x["precio"]))  # asigna un valor a una variable o atributo
        
        # Insertar en la tabla (solo los no eliminados)
        for elem in elementos:  # inicia un bucle para repetir instrucciones
            if elem["precio"] > 0:  # No mostrar elementos eliminados
                self.tree_servicios.insert("", tk.END, values=(  # asigna un atributo del objeto
                    elem["tipo"],  # realiza la instrucción
                    elem["elemento"],  # realiza la instrucción
                    f"${elem['precio']:,.0f}"  # realiza la instrucción
                ))  # realiza la instrucción
        
        # Actualizar combobox de servicios para reservas
        servicios = [f"{s.id} - {s.nombre}" for s in self.sistema.listar_servicios() if s.activo]  # asigna un atributo del objeto
        self.combo_servicio["values"] = servicios  # asigna un atributo del objeto
    
    def editar_servicio(self):
        """Edita el servicio seleccionado"""
        try:  # inicia un bloque de manejo de excepciones
            seleccion = self.tree_servicios.selection()  # asigna un atributo del objeto
            if not seleccion:  # evalúa una condición
                raise ReservaException("Seleccione un elemento de servicio")  # lanza una excepción cuando ocurre un error
            
            item = self.tree_servicios.item(seleccion[0])  # asigna un atributo del objeto
            tipo = item["values"][0]  # asigna un valor a una variable o atributo
            elemento = item["values"][1]  # asigna un valor a una variable o atributo
            precio_actual = item["values"][2]  # asigna un valor a una variable o atributo
            
            # Crear diálogo para editar
            dialog = tk.Toplevel(self.root)  # asigna un atributo del objeto
            dialog.title("Editar Servicio")  # realiza la instrucción
            dialog.geometry("400x250")  # realiza la instrucción
            dialog.transient(self.root)  # realiza la instrucción
            dialog.grab_set()  # realiza la instrucción
            
            # Frame del formulario
            form_frame = ttk.Frame(dialog, padding="20")  # asigna un valor a una variable o atributo
            form_frame.pack(fill=tk.BOTH, expand=True)  # asigna un valor a una variable o atributo
            
            ttk.Label(form_frame, text="Tipo:").grid(row=0, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            ttk.Label(form_frame, text=tipo).grid(row=0, column=1, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            
            ttk.Label(form_frame, text="Elemento:").grid(row=1, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            ttk.Label(form_frame, text=elemento).grid(row=1, column=1, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            
            ttk.Label(form_frame, text="Nuevo Precio:").grid(row=2, column=0, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            entry_precio = ttk.Entry(form_frame, width=20)  # asigna un valor a una variable o atributo
            entry_precio.grid(row=2, column=1, sticky=tk.W, pady=5)  # asigna un valor a una variable o atributo
            entry_precio.insert(0, precio_actual.replace("$", "").replace(",", ""))  # realiza la instrucción
            
            def guardar_cambio():
                """Función o método guardar_cambio."""
                try:  # inicia un bloque de manejo de excepciones
                    nuevo_precio = float(entry_precio.get())  # asigna un valor a una variable o atributo
                    
                    # Actualizar según el tipo
                    for servicio in self.sistema.listar_servicios():  # inicia un bucle para repetir instrucciones
                        if tipo == "Reserva de Sala":  # evalúa una condición
                            if isinstance(servicio, ServicioReservaSala):  # evalúa una condición
                                if elemento == "Sala A":  # evalúa una condición
                                    servicio.TARIFA_POR_HORA = int(nuevo_precio / 1.2)  # asigna un valor a una variable o atributo
                                elif elemento == "Sala VIP":  # evalúa una condición
                                    servicio.TARIFA_POR_HORA = int(nuevo_precio / 1.5)  # asigna un valor a una variable o atributo
                                else:  # ejecuta el bloque alternativo si la condición anterior no se cumple
                                    servicio.TARIFA_POR_HORA = int(nuevo_precio)  # asigna un valor a una variable o atributo
                        elif tipo == "Alquiler de Equipos":  # evalúa una condición
                            if isinstance(servicio, ServicioAlquilerEquipo):  # evalúa una condición
                                clave = elemento.lower().replace(" ", "_")  # asigna un valor a una variable o atributo
                                servicio.TARIFAS[clave] = nuevo_precio  # asigna un valor a una variable o atributo
                        elif tipo == "Asesorías Especializadas":  # evalúa una condición
                            if isinstance(servicio, ServicioAsesoria):  # evalúa una condición
                                clave = elemento.lower().replace(" ", "_")  # asigna un valor a una variable o atributo
                                servicio._precio = nuevo_precio  # asigna un valor a una variable o atributo
                    
                    self.actualizar_vista_servicios()  # realiza la instrucción
                    self.guardar_datos()  # Guardar automáticamente en JSON
                    self.actualizar_estado(f"Precio de {elemento} actualizado a ${nuevo_precio:,.0f}")  # realiza la instrucción
                    messagebox.showinfo("Éxito", "Precio actualizado correctamente")  # realiza la instrucción
                    dialog.destroy()  # realiza la instrucción
                    
                except ValueError:  # captura la excepción producida en el bloque try
                    messagebox.showerror("Error", "Ingrese un precio válido")  # realiza la instrucción
            
            btn_frame = ttk.Frame(form_frame)  # asigna un valor a una variable o atributo
            btn_frame.grid(row=3, column=0, columnspan=2, pady=20)  # asigna un valor a una variable o atributo
            ttk.Button(btn_frame, text="Guardar", command=guardar_cambio).pack(side=tk.LEFT, padx=5)  # asigna un valor a una variable o atributo
            ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)  # asigna un valor a una variable o atributo
            
        except ReservaException as e:  # captura la excepción producida en el bloque try
            messagebox.showerror("Error", str(e))  # realiza la instrucción
    
    def eliminar_servicio(self):
        """Elimina (desactiva) el servicio seleccionado"""
        try:  # inicia un bloque de manejo de excepciones
            seleccion = self.tree_servicios.selection()  # asigna un atributo del objeto
            if not seleccion:  # evalúa una condición
                raise ReservaException("Seleccione un elemento de servicio")  # lanza una excepción cuando ocurre un error
            
            item = self.tree_servicios.item(seleccion[0])  # asigna un atributo del objeto
            tipo = item["values"][0]  # asigna un valor a una variable o atributo
            elemento = item["values"][1]  # asigna un valor a una variable o atributo
            
            respuesta = messagebox.askyesno(  # asigna un valor a una variable o atributo
                "Confirmar eliminación",  # realiza la instrucción
                f"¿Está seguro de eliminar '{elemento}' del tipo '{tipo}'?"  # realiza la instrucción
            )  # realiza la instrucción
            
            if respuesta:  # evalúa una condición
                # Desactivar el elemento según el tipo
                for servicio in self.sistema.listar_servicios():  # inicia un bucle para repetir instrucciones
                    if tipo == "Reserva de Sala":  # evalúa una condición
                        if isinstance(servicio, ServicioReservaSala):  # evalúa una condición
                            if elemento in servicio._salas_disponibles:  # evalúa una condición
                                servicio._salas_disponibles.remove(elemento)  # realiza la instrucción
                    elif tipo == "Alquiler de Equipos":  # evalúa una condición
                        if isinstance(servicio, ServicioAlquilerEquipo):  # evalúa una condición
                            clave = elemento.lower().replace(" ", "_")  # asigna un valor a una variable o atributo
                            if clave in servicio.TARIFAS:  # evalúa una condición
                                servicio.TARIFAS[clave] = 0  # Marcar como eliminado
                    elif tipo == "Asesorías Especializadas":  # evalúa una condición
                        if isinstance(servicio, ServicioAsesoria):  # evalúa una condición
                            clave = elemento.lower().replace(" ", "_")  # asigna un valor a una variable o atributo
                            if clave in servicio.TARIFAS_POR_TIPO:  # evalúa una condición
                                servicio.TARIFAS_POR_TIPO[clave] = 0  # Marcar como eliminado
                
                self.actualizar_vista_servicios()  # realiza la instrucción
                self.guardar_datos()  # Guardar automáticamente en JSON
                self.actualizar_estado(f"Elemento '{elemento}' eliminado")  # realiza la instrucción
                messagebox.showinfo("Éxito", f"Elemento '{elemento}' eliminado")  # realiza la instrucción
                
        except ReservaException as e:  # captura la excepción producida en el bloque try
            messagebox.showerror("Error", str(e))  # realiza la instrucción
    
    def actualizar_vista_reservas(self):
        """Actualiza la vista de reservas"""
        for item in self.tree_reservas.get_children():  # inicia un bucle para repetir instrucciones
            self.tree_reservas.delete(item)  # realiza la instrucción
        
        for reserva in self.sistema.listar_reservas():  # inicia un bucle para repetir instrucciones
            self.tree_reservas.insert("", tk.END, values=(  # asigna un atributo del objeto
                reserva.id,  # realiza la instrucción
                f"{reserva.cliente.nombre} {reserva.cliente.apellido}",  # realiza la instrucción
                reserva.servicio.nombre,  # realiza la instrucción
                reserva.duracion,  # realiza la instrucción
                reserva.estado,  # realiza la instrucción
                f"${reserva.costo_total:,.2f}"  # realiza la instrucción
            ))  # realiza la instrucción
    
    def actualizar_estado(self, mensaje: str):
        """Actualiza la barra de estado"""
        self.estado.config(text=mensaje)  # asigna un atributo del objeto
    
    def mostrar_clientes(self):
        """Muestra la pestaña de clientes"""
        self.notebook.select(0)  # realiza la instrucción
    
    def mostrar_servicios(self):
        """Muestra la pestaña de servicios"""
        self.notebook.select(1)  # realiza la instrucción
    
    def mostrar_reservas(self):
        """Muestra la pestaña de reservas"""
        self.notebook.select(2)  # realiza la instrucción

def main():
    """Función principal"""
    root = tk.Tk()  # asigna un valor a una variable o atributo
    InterfazSoftwareFJ(root)  # realiza la instrucción
    root.mainloop()  # realiza la instrucción


if __name__ == "__main__":  # evalúa una condición
    main()  # realiza la instrucción
