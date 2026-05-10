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

# -------------------------------
# Clase base Empleado
# -------------------------------
class Empleado:
    def __init__(self, nombre, identificacion, salario_base):
        # Atributos generales de cualquier empleado
        self.nombre = nombre
        self.identificacion = identificacion
        self.salario_base = salario_base

    def calcular_salario(self):
        """
        Método virtual (polimorfismo).
        Cada tipo de empleado lo implementa diferente.
        """
        raise NotImplementedError("Debe implementarse en la subclase")

    def mostrar_informacion(self, incluir_salario=False, detalle=False):
        """
        Simulación de sobrecarga usando parámetros opcionales:
        - Básico
        - Con salario
        - Con detalles
        """
        info = f"Nombre: {self.nombre} | ID: {self.identificacion}"

        if incluir_salario:
            info += f" | Salario: {self.calcular_salario()}"

        return info


# -------------------------------
# Clase adicional (Mixin)
# -------------------------------
class Bonificable:
    def __init__(self):
        # Lista para guardar bonificaciones
        self.bonificaciones = []

    def agregar_bonificacion(self, monto):
        # Agrega una bonificación
        self.bonificaciones.append(monto)

    def obtener_bonificaciones(self):
        # Retorna el total de bonificaciones
        return sum(self.bonificaciones)


# -------------------------------
# Tipos de empleados
# -------------------------------

# 1. Empleado de tiempo completo
class EmpleadoTiempoCompleto(Empleado):
    def __init__(self, nombre, identificacion, salario_base, bonificacion=0):
        super().__init__(nombre, identificacion, salario_base)
        self.bonificacion = bonificacion

    def calcular_salario(self):
        # Salario fijo + bonificación
        return self.salario_base + self.bonificacion


# 2. Empleado por horas
class EmpleadoPorHoras(Empleado):
    def __init__(self, nombre, identificacion, pago_por_hora, horas_trabajadas):
        super().__init__(nombre, identificacion, pago_por_hora)
        self.horas_trabajadas = horas_trabajadas

    def calcular_salario(self):
        # Salario = pago por hora * horas trabajadas
        return self.salario_base * self.horas_trabajadas


# 3. Empleado por comisión
class EmpleadoComision(Empleado):
    def __init__(self, nombre, identificacion, salario_base, ventas, porcentaje):
        super().__init__(nombre, identificacion, salario_base)
        self.ventas = ventas
        self.porcentaje = porcentaje

    def calcular_salario(self):
        # Salario base + comisión por ventas
        return self.salario_base + (self.ventas * self.porcentaje)


# -------------------------------
# Herencia múltiple
# -------------------------------
class EmpleadoTiempoCompletoBonificado(EmpleadoTiempoCompleto, Bonificable):
    def __init__(self, nombre, identificacion, salario_base, bonificacion=0):
        # Inicializamos ambas clases
        EmpleadoTiempoCompleto.__init__(self, nombre, identificacion, salario_base, bonificacion)
        Bonificable.__init__(self)

    def calcular_salario(self):
        # Salario base + bonificación + bonificaciones extra
        return super().calcular_salario() + self.obtener_bonificaciones()

    def mostrar_informacion(self, incluir_salario=False, detalle=False):
        info = super().mostrar_informacion(incluir_salario=incluir_salario)

        if detalle:
            info += f" | Bonificaciones extra: {self.obtener_bonificaciones()}"

        return info


# -------------------------------
# Sistema de nómina
# -------------------------------
class SistemaNomina:
    def __init__(self):
        self.empleados = []

    def agregar_empleado(self, empleado):
        # Agrega un empleado a la lista
        self.empleados.append(empleado)

    def calcular_nomina(self):
        print("===== NÓMINA MENSUAL =====")
        total = 0

        # Polimorfismo: cada empleado calcula su salario diferente
        for emp in self.empleados:
            salario = emp.calcular_salario()
            print(emp.mostrar_informacion(incluir_salario=True))
            total += salario

        print(f"\nTOTAL A PAGAR: {total}")


# -------------------------------
# Programa principal
# -------------------------------
if __name__ == "__main__":
    sistema = SistemaNomina()

    # Crear empleados
    emp1 = EmpleadoTiempoCompleto("Ana", "001", 2000, 300)
    emp2 = EmpleadoPorHoras("Luis", "002", 20, 80)
    emp3 = EmpleadoComision("Carlos", "003", 1500, 5000, 0.1)

    # Empleado con herencia múltiple
    emp4 = EmpleadoTiempoCompletoBonificado("Sofia", "004", 2500, 200)
    emp4.agregar_bonificacion(150)
    emp4.agregar_bonificacion(100)

    # Agregar al sistema
    sistema.agregar_empleado(emp1)
    sistema.agregar_empleado(emp2)
    sistema.agregar_empleado(emp3)
    sistema.agregar_empleado(emp4)

    # Ejecutar nómina
    sistema.calcular_nomina()