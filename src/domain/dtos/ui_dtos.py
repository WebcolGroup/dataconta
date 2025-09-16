"""
DTOs para la capa de UI
Objetos de transferencia de datos específicos para la comunicación entre 
la interfaz de usuario y la capa de aplicación.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ReportFormat(Enum):
    """Formatos disponibles para reportes"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"


class ExportStatus(Enum):
    """Estados de exportación"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class UINotificationType(Enum):
    """Tipos de notificación de UI"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    QUESTION = "question"


@dataclass
class UIProgressInfo:
    """Información de progreso para operaciones largas"""
    title: str
    message: str
    current: int
    maximum: int
    is_indeterminate: bool = False


@dataclass
class UINotification:
    """Notificación para mostrar al usuario"""
    title: str
    message: str
    notification_type: UINotificationType
    details: Optional[str] = None
    """Estados de una operación de exportación"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class UIInvoiceRequestDTO:
    """Request para consultar facturas desde la UI"""
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    customer_id: Optional[str] = None
    page_size: int = 100
    export_format: ReportFormat = ReportFormat.JSON
    save_to_file: bool = True
    include_details: bool = True


@dataclass
class UIInvoiceResponseDTO:
    """Response con información de facturas para la UI"""
    success: bool
    total_invoices: int
    invoices: List[Dict[str, Any]]
    file_path: Optional[str] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class UIExportRequestDTO:
    """Request general para exportaciones desde la UI"""
    export_type: str  # "invoices", "bi", "financial_report"
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    format: ReportFormat = ReportFormat.CSV
    output_path: Optional[str] = None
    include_details: bool = True
    filters: Dict[str, Any] = None


@dataclass
class UIExportResponseDTO:
    """Response para operaciones de exportación"""
    success: bool
    status: ExportStatus
    file_path: Optional[str] = None
    records_exported: int = 0
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
    warnings: List[str] = None


@dataclass
class UIBIExportRequestDTO:
    """Request específico para exportar datos de BI"""
    date_start: Optional[str] = None
    date_end: Optional[str] = None
    include_fact_tables: bool = True
    include_dimension_tables: bool = True
    output_directory: Optional[str] = None
    generate_relationships: bool = True


@dataclass
class UIBIExportResponseDTO:
    """Response para exportación de BI"""
    success: bool
    fact_tables_created: List[str] = None
    dimension_tables_created: List[str] = None
    relationships_file: Optional[str] = None
    total_records: int = 0
    execution_time: Optional[float] = None
    output_directory: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class UIFinancialReportRequestDTO:
    """Request para generar reportes financieros"""
    report_type: str  # "estado_resultados", "balance_general", "flujo_caja"
    period_start: str
    period_end: str
    format: ReportFormat = ReportFormat.CSV
    include_kpis: bool = True
    include_charts: bool = False
    output_path: Optional[str] = None
    currency: str = "COP"


@dataclass
class UIFinancialReportResponseDTO:
    """Response para reportes financieros"""
    success: bool
    report_type: str
    period_start: str
    period_end: str
    file_path: Optional[str] = None
    summary_data: Dict[str, Any] = None
    execution_time: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class UISystemStatusDTO:
    """Estado del sistema para mostrar en la UI"""
    api_connected: bool
    license_valid: bool
    license_type: str
    last_sync: Optional[datetime] = None
    pending_operations: int = 0
    system_health: str = "healthy"  # healthy, warning, error
    messages: List[str] = None


@dataclass
class UIMenuSectionDTO:
    """Sección de menú para la UI"""
    id: str
    title: str
    emoji: str
    description: str
    license_required: str
    enabled: bool = True
    options: List['UIMenuOptionDTO'] = None


@dataclass
class UIMenuOptionDTO:
    """Opción individual de menú para la UI"""
    id: str
    title: str
    description: str
    emoji: str
    enabled: bool = True
    shortcut: Optional[str] = None
    tooltip: Optional[str] = None
    requires_confirmation: bool = False
    estimated_duration: Optional[str] = None  # "< 1 min", "1-5 min", etc.


@dataclass
class UIOperationProgressDTO:
    """Información de progreso para operaciones largas"""
    operation_id: str
    operation_name: str
    current_step: str
    progress_percentage: float
    estimated_remaining: Optional[str] = None
    can_cancel: bool = True
    details: Optional[str] = None


@dataclass
class UIFileInfoDTO:
    """Información sobre archivos generados"""
    file_path: str
    file_name: str
    file_size: int  # En bytes
    creation_date: datetime
    file_type: str
    description: Optional[str] = None
    can_open: bool = True
    can_export: bool = True


@dataclass
class UIValidationResultDTO:
    """Resultado de validación para la UI"""
    is_valid: bool
    error_message: Optional[str] = None
    warnings: List[str] = None
    field_errors: Dict[str, str] = None
    suggestions: List[str] = None


@dataclass
class UILicenseInfoDTO:
    """Información de licencia para mostrar en la UI"""
    license_type: str
    is_valid: bool
    expiry_date: Optional[datetime] = None
    features_available: List[str] = None
    features_restricted: List[str] = None
    usage_limits: Dict[str, Any] = None


@dataclass
class UIDateRangeDTO:
    """Rango de fechas seleccionado por el usuario"""
    start_date: str  # YYYY-MM-DD format
    end_date: str    # YYYY-MM-DD format
    preset_name: Optional[str] = None  # "this_month", "last_quarter", etc.
    is_custom: bool = True


@dataclass
class UIFilterCriteriaDTO:
    """Criterios de filtro para consultas"""
    date_range: Optional[UIDateRangeDTO] = None
    customer_ids: List[str] = None
    product_codes: List[str] = None
    amount_range: Optional[Dict[str, float]] = None  # {"min": 0, "max": 1000000}
    status_filter: List[str] = None
    text_search: Optional[str] = None


@dataclass
class UIApplicationStateDTO:
    """Estado completo de la aplicación para la UI"""
    system_status: UISystemStatusDTO
    license_info: UILicenseInfoDTO
    current_user: Optional[str] = None
    active_operations: List[UIOperationProgressDTO] = None
    recent_files: List[UIFileInfoDTO] = None
    notifications: List[str] = None