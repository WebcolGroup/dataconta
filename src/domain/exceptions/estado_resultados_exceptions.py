"""
Excepciones específicas para el módulo de Estado de Resultados.
Manejo de errores siguiendo principios SOLID y arquitectura hexagonal.
"""

from typing import Optional


class EstadoResultadosError(Exception):
    """Excepción base para errores relacionados con Estado de Resultados."""
    
    def __init__(self, message: str, error_code: str = "ER_GENERAL", details: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.error_code}: {self.message} - {self.details}"
        return f"{self.error_code}: {self.message}"


class SiigoAPIError(EstadoResultadosError):
    """Error específico de conexión o datos de Siigo API."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message, 
            "ER_SIIGO_API", 
            details
        )


class DataValidationError(EstadoResultadosError):
    """Error de validación de datos contables."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message, 
            "ER_DATA_VALIDATION", 
            details
        )


class ExcelGenerationError(EstadoResultadosError):
    """Error específico de generación de archivos Excel."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message, 
            "ER_EXCEL_GEN", 
            details
        )


class DateRangeError(EstadoResultadosError):
    """Error relacionado con rangos de fechas inválidos."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message, 
            "ER_DATE_RANGE", 
            details
        )


class CalculationError(EstadoResultadosError):
    """Error en cálculos contables o matemáticos."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message, 
            "ER_CALCULATION", 
            details
        )


class NormativeComplianceError(EstadoResultadosError):
    """Error de cumplimiento de normativa tributaria colombiana."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(
            message, 
            "ER_NORMATIVE", 
            details
        )


# Utility functions para manejo de errores
def handle_siigo_connection_error(original_error: Exception) -> SiigoAPIError:
    """
    Convertir errores de conexión con Siigo API a excepciones específicas.
    
    Args:
        original_error: Error original capturado
        
    Returns:
        SiigoAPIError: Error específico con mensaje apropiado
    """
    error_message = str(original_error).lower()
    
    if "connection" in error_message or "timeout" in error_message:
        return SiigoAPIError(
            "No se pudo establecer conexión con Siigo API",
            f"Error de conexión: {str(original_error)}"
        )
    elif "authentication" in error_message or "unauthorized" in error_message:
        return SiigoAPIError(
            "Credenciales de Siigo API inválidas o expiradas",
            f"Error de autenticación: {str(original_error)}"
        )
    elif "rate limit" in error_message or "429" in error_message:
        return SiigoAPIError(
            "Límite de consultas a Siigo API excedido",
            f"Rate limit: {str(original_error)}"
        )
    else:
        return SiigoAPIError(
            "Error general de Siigo API",
            str(original_error)
        )


def handle_data_processing_error(original_error: Exception, data_type: str = "facturas") -> DataValidationError:
    """
    Convertir errores de procesamiento de datos a excepciones específicas.
    
    Args:
        original_error: Error original capturado
        data_type: Tipo de dato que causó el error
        
    Returns:
        DataValidationError: Error específico con mensaje apropiado
    """
    return DataValidationError(
        f"Error procesando {data_type} para Estado de Resultados",
        f"Detalle del error: {str(original_error)}"
    )


def handle_excel_generation_error(original_error: Exception, file_path: str = "") -> ExcelGenerationError:
    """
    Convertir errores de generación de Excel a excepciones específicas.
    
    Args:
        original_error: Error original capturado
        file_path: Ruta del archivo que se intentaba generar
        
    Returns:
        ExcelGenerationError: Error específico con mensaje apropiado
    """
    error_message = str(original_error).lower()
    
    if "permission" in error_message or "access" in error_message:
        return ExcelGenerationError(
            "Sin permisos para crear archivo Excel en la ubicación especificada",
            f"Archivo: {file_path} - Error: {str(original_error)}"
        )
    elif "disk" in error_message or "space" in error_message:
        return ExcelGenerationError(
            "Espacio insuficiente en disco para generar archivo Excel",
            f"Error de espacio: {str(original_error)}"
        )
    elif "openpyxl" in error_message or "xlsxwriter" in error_message:
        return ExcelGenerationError(
            "Error en librería de generación de Excel",
            f"Error de librería: {str(original_error)}"
        )
    else:
        return ExcelGenerationError(
            "Error general generando archivo Excel",
            str(original_error)
        )


def validate_date_range(fecha_inicio: str, fecha_fin: str) -> None:
    """
    Validar rango de fechas para Estado de Resultados.
    
    Args:
        fecha_inicio: Fecha de inicio en formato YYYY-MM-DD
        fecha_fin: Fecha de fin en formato YYYY-MM-DD
        
    Raises:
        DateRangeError: Si el rango de fechas es inválido
    """
    try:
        from datetime import datetime
        
        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
        
        if inicio >= fin:
            raise DateRangeError(
                "La fecha de inicio debe ser anterior a la fecha de fin",
                f"Inicio: {fecha_inicio}, Fin: {fecha_fin}"
            )
        
        # Validar que no sea un rango muy extenso (más de 2 años)
        diferencia_dias = (fin - inicio).days
        if diferencia_dias > 730:  # Aproximadamente 2 años
            raise DateRangeError(
                "El rango de fechas es demasiado extenso (máximo 2 años)",
                f"Rango actual: {diferencia_dias} días"
            )
        
        # Validar que no sean fechas futuras muy lejanas
        hoy = datetime.now()
        if fin > hoy:
            dias_futuro = (fin - hoy).days
            if dias_futuro > 30:  # Máximo 30 días en el futuro
                raise DateRangeError(
                    "La fecha de fin no puede estar muy lejana en el futuro",
                    f"Días en el futuro: {dias_futuro}"
                )
                
    except ValueError as e:
        raise DateRangeError(
            "Formato de fecha inválido (debe ser YYYY-MM-DD)",
            str(e)
        )


def validate_calculation_inputs(ingresos: float, costos: float, gastos: float) -> None:
    """
    Validar inputs para cálculos contables.
    
    Args:
        ingresos: Total de ingresos
        costos: Total de costos
        gastos: Total de gastos
        
    Raises:
        CalculationError: Si los inputs son inválidos
    """
    if ingresos < 0:
        raise CalculationError(
            "Los ingresos no pueden ser negativos",
            f"Valor recibido: {ingresos}"
        )
    
    if costos < 0:
        raise CalculationError(
            "Los costos no pueden ser negativos", 
            f"Valor recibido: {costos}"
        )
    
    if gastos < 0:
        raise CalculationError(
            "Los gastos no pueden ser negativos",
            f"Valor recibido: {gastos}"
        )
    
    # Validar que los costos + gastos no excedan significativamente los ingresos
    # (puede ser válido en casos de pérdidas, pero alertar si es extremo)
    if ingresos > 0 and (costos + gastos) > (ingresos * 3):
        raise CalculationError(
            "Los costos y gastos exceden significativamente los ingresos",
            f"Ingresos: {ingresos}, Costos+Gastos: {costos + gastos}"
        )


def check_normative_compliance(cuenta_codigo: str) -> None:
    """
    Verificar que el código de cuenta cumple con PUC colombiano.
    
    Args:
        cuenta_codigo: Código de cuenta contable
        
    Raises:
        NormativeComplianceError: Si no cumple con normativa
    """
    if not cuenta_codigo or len(cuenta_codigo) < 2:
        raise NormativeComplianceError(
            "Código de cuenta inválido según Plan Único de Cuentas",
            f"Código recibido: {cuenta_codigo}"
        )
    
    # Validar códigos principales del PUC
    primer_digito = cuenta_codigo[0]
    
    cuentas_validas = {
        '1': 'Activo',
        '2': 'Pasivo', 
        '3': 'Patrimonio',
        '4': 'Ingresos',
        '5': 'Gastos',
        '6': 'Costos',
        '7': 'Costos de Producción',
        '8': 'Cuentas de Orden Deudoras',
        '9': 'Cuentas de Orden Acreedoras'
    }
    
    if primer_digito not in cuentas_validas:
        raise NormativeComplianceError(
            f"Código de cuenta no válido según PUC colombiano",
            f"Código: {cuenta_codigo} - Primer dígito: {primer_digito}"
        )