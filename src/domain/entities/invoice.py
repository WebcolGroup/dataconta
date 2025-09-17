"""
Domain entities for the Siigo API application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


# ========================================================================================
# LICENCIA Y TIPOS DE SISTEMA
# ========================================================================================

class LicenseType(Enum):
    """
    Tipos de licencia disponibles en DataConta.
    
    FREE: Funcionalidades básicas, CLI únicamente
    PROFESSIONAL: GUI completa, informes financieros, BI limitado  
    ENTERPRISE: Funcionalidades completas sin límites
    """
    FREE = "FREE"
    PROFESSIONAL = "PROFESSIONAL" 
    ENTERPRISE = "ENTERPRISE"
    
    @property
    def display_name(self) -> str:
        """Nombre legible para mostrar al usuario."""
        names = {
            LicenseType.FREE: "🆓 Gratuita",
            LicenseType.PROFESSIONAL: "💼 Profesional", 
            LicenseType.ENTERPRISE: "🏢 Enterprise"
        }
        return names[self]
    
    @property
    def max_invoices_query(self) -> int:
        """Máximo número de facturas por consulta."""
        limits = {
            LicenseType.FREE: 500,
            LicenseType.PROFESSIONAL: 2000,
            LicenseType.ENTERPRISE: 100000  # Prácticamente ilimitado
        }
        return limits[self]
    
    @property
    def max_invoices_bi(self) -> Optional[int]:
        """Máximo número de facturas para exportación BI. None = sin límite."""
        limits = {
            LicenseType.FREE: 0,  # Sin acceso a BI
            LicenseType.PROFESSIONAL: 2000,
            LicenseType.ENTERPRISE: None  # Sin límite
        }
        return limits[self]
    
    @property
    def has_gui_access(self) -> bool:
        """Si tiene acceso a la interfaz gráfica."""
        return self in [LicenseType.PROFESSIONAL, LicenseType.ENTERPRISE]
    
    @property
    def has_financial_reports(self) -> bool:
        """Si tiene acceso a informes financieros."""
        return self in [LicenseType.PROFESSIONAL, LicenseType.ENTERPRISE]
    
    @property
    def has_bi_export(self) -> bool:
        """Si tiene acceso a exportación de Business Intelligence."""
        return self in [LicenseType.PROFESSIONAL, LicenseType.ENTERPRISE]
    
    @property
    def has_advanced_features(self) -> bool:
        """Si tiene funcionalidades avanzadas (solo Enterprise)."""
        return self == LicenseType.ENTERPRISE


@dataclass
class LicenseLimits:
    """
    Límites específicos por tipo de licencia.
    """
    license_type: LicenseType
    max_invoices_per_query: int
    max_invoices_bi: Optional[int]
    gui_enabled: bool
    financial_reports_enabled: bool
    bi_export_enabled: bool
    advanced_logging: bool
    online_validation: bool
    
    @classmethod
    def from_license_type(cls, license_type: LicenseType) -> 'LicenseLimits':
        """Crear límites basados en el tipo de licencia."""
        return cls(
            license_type=license_type,
            max_invoices_per_query=license_type.max_invoices_query,
            max_invoices_bi=license_type.max_invoices_bi,
            gui_enabled=license_type.has_gui_access,
            financial_reports_enabled=license_type.has_financial_reports,
            bi_export_enabled=license_type.has_bi_export,
            advanced_logging=license_type != LicenseType.FREE,
            online_validation=license_type != LicenseType.FREE
        )


# ========================================================================================
# ENTIDADES PARA BUSINESS INTELLIGENCE (Modelo Estrella)
# ========================================================================================

@dataclass
class FactInvoice:
    """
    Tabla de hechos para facturas (modelo estrella).
    Representa el grano más bajo: cada línea de producto en cada factura con cada pago.
    """
    factura_id: str
    fecha: str
    cliente_id: str
    vendedor_id: str
    producto_codigo: str
    producto_cantidad: float
    producto_precio: float
    producto_descuento: float
    producto_total: float
    pago_id: str
    subtotal: float
    descuento_total: float
    impuestos: float
    total: float
    estado: str
    observaciones: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export with proper number formatting."""
        return {
            "factura_id": self.factura_id,
            "fecha": self.fecha,
            "cliente_id": self.cliente_id,
            "vendedor_id": self.vendedor_id,
            "producto_codigo": self.producto_codigo,
            "producto_cantidad": self._format_quantity(self.producto_cantidad),
            "producto_precio": self._format_currency(self.producto_precio),
            "producto_descuento": self._format_currency(self.producto_descuento),
            "producto_total": self._format_currency(self.producto_total),
            "pago_id": self.pago_id,
            "subtotal": self._format_currency(self.subtotal),
            "descuento_total": self._format_currency(self.descuento_total),
            "impuestos": self._format_currency(self.impuestos),
            "total": self._format_currency(self.total),
            "estado": self.estado,
            "observaciones": self.observaciones
        }
    
    def _format_currency(self, value: float) -> str:
        """Format currency values with comma as decimal separator for Spanish/European locale."""
        if value is None:
            return "0,00"
        return f"{value:.2f}".replace(".", ",")
    
    def _format_quantity(self, value: float) -> str:
        """Format quantity values with comma as decimal separator for Spanish/European locale."""
        if value is None:
            return "0"
        # If it's a whole number, format as integer, otherwise with decimals
        if value == int(value):
            return f"{int(value)}"
        else:
            return f"{value:.2f}".replace(".", ",")
    
    @staticmethod
    def get_csv_headers() -> List[str]:
        """Get CSV headers for fact table."""
        return [
            "factura_id", "fecha", "cliente_id", "vendedor_id", "producto_codigo",
            "producto_cantidad", "producto_precio", "producto_descuento", "producto_total",
            "pago_id", "subtotal", "descuento_total", "impuestos", "total", "estado", "observaciones"
        ]


@dataclass
class DimClient:
    """Dimensión de clientes."""
    cliente_id: str
    identificacion: str
    nombre: str
    email: str
    tipo_cliente: str = "No Especificado"  # Persona Natural / Jurídica
    regimen: str = "No Especificado"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
            "cliente_id": self.cliente_id,
            "identificacion": self.identificacion,
            "nombre": self.nombre,
            "email": self.email,
            "tipo_cliente": self.tipo_cliente,
            "regimen": self.regimen
        }
    
    @staticmethod
    def get_csv_headers() -> List[str]:
        """Get CSV headers for clients dimension."""
        return ["cliente_id", "identificacion", "nombre", "email", "tipo_cliente", "regimen"]


@dataclass
class DimSeller:
    """Dimensión de vendedores."""
    vendedor_id: str
    nombre: str
    zona: str = "No Especificado"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
            "vendedor_id": self.vendedor_id,
            "nombre": self.nombre,
            "zona": self.zona
        }
    
    @staticmethod
    def get_csv_headers() -> List[str]:
        """Get CSV headers for sellers dimension."""
        return ["vendedor_id", "nombre", "zona"]


@dataclass
class DimProduct:
    """Dimensión de productos."""
    producto_codigo: str
    descripcion: str
    categoria: str = "General"
    precio_estandar: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export with proper number formatting."""
        return {
            "producto_codigo": self.producto_codigo,
            "descripcion": self.descripcion,
            "categoria": self.categoria,
            "precio_estandar": self._format_currency(self.precio_estandar)
        }
    
    def _format_currency(self, value: float) -> str:
        """Format currency values with comma as decimal separator for Spanish/European locale."""
        if value is None:
            return "0,00"
        return f"{value:.2f}".replace(".", ",")
    
    @staticmethod
    def get_csv_headers() -> List[str]:
        """Get CSV headers for products dimension."""
        return ["producto_codigo", "descripcion", "categoria", "precio_estandar"]


@dataclass
class DimPayment:
    """Dimensión de pagos."""
    pago_id: str
    nombre: str
    categoria: str = "No Especificado"  # Tarjeta, Efectivo, Transferencia, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
            "pago_id": self.pago_id,
            "nombre": self.nombre,
            "categoria": self.categoria
        }
    
    @staticmethod
    def get_csv_headers() -> List[str]:
        """Get CSV headers for payments dimension."""
        return ["pago_id", "nombre", "categoria"]


@dataclass
class DimDate:
    """Dimensión de fechas."""
    fecha: str
    año: int
    mes: int
    dia: int
    trimestre: int
    nombre_mes: str
    nombre_dia: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV export."""
        return {
            "fecha": self.fecha,
            "año": self.año,
            "mes": self.mes,
            "dia": self.dia,
            "trimestre": self.trimestre,
            "nombre_mes": self.nombre_mes,
            "nombre_dia": self.nombre_dia
        }
    
    @staticmethod
    def get_csv_headers() -> List[str]:
        """Get CSV headers for dates dimension."""
        return ["fecha", "año", "mes", "dia", "trimestre", "nombre_mes", "nombre_dia"]
    
    @classmethod
    def from_date_string(cls, date_str: str) -> 'DimDate':
        """Create DimDate from date string (ISO format)."""
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            # Nombres de meses y días en español
            meses = [
                "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            dias = [
                "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"
            ]
            
            return cls(
                fecha=dt.strftime("%Y-%m-%d"),
                año=dt.year,
                mes=dt.month,
                dia=dt.day,
                trimestre=(dt.month - 1) // 3 + 1,
                nombre_mes=meses[dt.month],
                nombre_dia=dias[dt.weekday()]
            )
        except Exception:
            # Fallback para fechas inválidas
            return cls(
                fecha=date_str,
                año=2000,
                mes=1,
                dia=1,
                trimestre=1,
                nombre_mes="Enero",
                nombre_dia="Lunes"
            )


# ========================================================================================
# ENTIDADES EXISTENTES
# ========================================================================================

@dataclass
class InvoiceExportDTO:
    """
    Data Transfer Object for invoice export operations.
    Defines the expected structure for invoice data to be exported to CSV.
    """
    
    # Invoice basic info
    invoice_id: str
    invoice_number: str
    invoice_date: str
    
    # Financial data
    discount: Decimal = Decimal('0.00')
    tax_amount: Decimal = Decimal('0.00')
    net_amount: Decimal = Decimal('0.00')
    total_amount: Decimal = Decimal('0.00')
    
    # Status and method
    status: str = "Pending"
    payment_method: str = "Cash"
    
    # Business classification
    segment: str = "General"
    category: str = "Sales"
    vendor: str = ""
    channel: str = "Direct"
    
    # Location
    currency: str = "COP"
    country: str = "Colombia"
    
    # Customer info
    customer_id: str = ""
    customer_name: str = ""
    
    # Additional fields
    cost_center: Optional[str] = None
    seller: Optional[str] = None
    observations: Optional[str] = None
    
    def validate_structure(self) -> tuple[bool, List[str]]:
        """
        Validate that the DTO has the required structure.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields validation
        required_fields = {
            'invoice_id': self.invoice_id,
            'invoice_number': self.invoice_number,
            'invoice_date': self.invoice_date
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value or (isinstance(field_value, str) and not field_value.strip()):
                errors.append(f"Required field '{field_name}' is missing or empty")
        
        # Numeric fields validation
        numeric_fields = {
            'discount': self.discount,
            'tax_amount': self.tax_amount,
            'net_amount': self.net_amount,
            'total_amount': self.total_amount
        }
        
        for field_name, field_value in numeric_fields.items():
            if not isinstance(field_value, Decimal):
                try:
                    setattr(self, field_name, Decimal(str(field_value)))
                except:
                    errors.append(f"Field '{field_name}' must be a valid number")
        
        return len(errors) == 0, errors
    
    def to_csv_headers(self) -> List[str]:
        """Get CSV headers for export."""
        return [
            "InvoiceID", "InvoiceNumber", "InvoiceDate", "Discount", "TaxAmount",
            "NetAmount", "TotalAmount", "Status", "PaymentMethod", "Segment",
            "Category", "Vendor", "Channel", "Currency", "Country",
            "CustomerID", "CustomerName", "CostCenter", "Seller", "Observations"
        ]
    
    def to_csv_row(self) -> List[str]:
        """Convert DTO to CSV row data."""
        return [
            str(self.invoice_id),
            str(self.invoice_number),
            str(self.invoice_date),
            str(self.discount),
            str(self.tax_amount),
            str(self.net_amount),
            str(self.total_amount),
            str(self.status),
            str(self.payment_method),
            str(self.segment),
            str(self.category),
            str(self.vendor),
            str(self.channel),
            str(self.currency),
            str(self.country),
            str(self.customer_id),
            str(self.customer_name),
            str(self.cost_center or ""),
            str(self.seller or ""),
            str(self.observations or "")
        ]


@dataclass
class Invoice:
    """Invoice entity representing a Siigo invoice."""
    
    id: str
    document_id: str
    number: int
    name: str
    date: datetime
    customer: 'Customer'
    items: List['InvoiceItem']
    payments: List['Payment']
    cost_center: Optional[int] = None
    seller: Optional[int] = None
    observations: Optional[str] = None
    additional_fields: Optional[Dict[str, Any]] = None
    total: Optional[Decimal] = None
    
    def calculate_total(self) -> Decimal:
        """Calculate invoice total from items."""
        if not self.items:
            return Decimal('0.00')
        return sum(item.calculate_total() for item in self.items)
    
    def is_valid(self) -> bool:
        """Validate invoice business rules."""
        return (
            bool(self.document_id) and
            bool(self.customer) and
            len(self.items) > 0 and
            all(item.is_valid() for item in self.items)
        )


@dataclass
class Customer:
    """Customer entity."""
    
    identification: str
    branch_office: int = 0
    check_digit: Optional[str] = None
    name: Optional[List[str]] = None
    commercial_name: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    phones: Optional[List[Dict[str, Any]]] = None
    contacts: Optional[List[Dict[str, Any]]] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.name is None:
            self.name = []
        if self.phones is None:
            self.phones = []
        if self.contacts is None:
            self.contacts = []


@dataclass
class InvoiceItem:
    """Invoice item entity."""
    
    code: str
    description: str
    quantity: Decimal
    price: Decimal
    discount: Decimal = Decimal('0.00')
    taxes: Optional[List[Dict[str, Any]]] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.taxes is None:
            self.taxes = []
    
    def calculate_subtotal(self) -> Decimal:
        """Calculate subtotal before taxes."""
        return (self.quantity * self.price) - self.discount
    
    def calculate_tax_amount(self) -> Decimal:
        """Calculate total tax amount."""
        if not self.taxes:
            return Decimal('0.00')
        
        subtotal = self.calculate_subtotal()
        total_tax = Decimal('0.00')
        
        for tax in self.taxes:
            tax_rate = Decimal(str(tax.get('percentage', 0))) / 100
            total_tax += subtotal * tax_rate
        
        return total_tax
    
    def calculate_total(self) -> Decimal:
        """Calculate total including taxes."""
        return self.calculate_subtotal() + self.calculate_tax_amount()
    
    def is_valid(self) -> bool:
        """Validate item business rules."""
        return (
            bool(self.code) and
            bool(self.description) and
            self.quantity > 0 and
            self.price >= 0
        )


@dataclass
class Payment:
    """Payment entity."""
    
    id: int
    value: Decimal
    due_date: datetime
    
    def is_valid(self) -> bool:
        """Validate payment business rules."""
        return self.value > 0


@dataclass
class License:
    """License entity for application licensing with tiered support."""
    
    key: str
    license_type: LicenseType
    status: str
    expires_at: Optional[datetime] = None
    features: Optional[List[str]] = None
    limits: Optional[LicenseLimits] = None
    
    def __post_init__(self):
        """Initialize default values and limits."""
        if self.features is None:
            self.features = []
        
        # Crear límites automáticamente basados en el tipo de licencia
        if self.limits is None:
            self.limits = LicenseLimits.from_license_type(self.license_type)
    
    def is_valid(self) -> bool:
        """Check if license is valid."""
        if self.status != 'active':
            return False
        
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        
        return True
    
    def has_feature(self, feature: str) -> bool:
        """Check if license includes a specific feature."""
        return feature in self.features
    
    def can_access_gui(self) -> bool:
        """Check if license allows GUI access."""
        return self.limits.gui_enabled if self.limits else False
    
    def can_generate_financial_reports(self) -> bool:
        """Check if license allows financial reports generation."""
        return self.limits.financial_reports_enabled if self.limits else False
    
    def can_export_bi(self) -> bool:
        """Check if license allows BI export."""
        return self.limits.bi_export_enabled if self.limits else False
    
    def get_max_invoices_query(self) -> int:
        """Get maximum invoices per query for this license."""
        return self.limits.max_invoices_per_query if self.limits else 100
    
    def get_max_invoices_bi(self) -> Optional[int]:
        """Get maximum invoices for BI export. None = unlimited."""
        return self.limits.max_invoices_bi if self.limits else 0
    
    def validate_invoice_count(self, count: int, operation: str = "query") -> bool:
        """Validate if the requested invoice count is within license limits."""
        if operation == "query":
            return count <= self.get_max_invoices_query()
        elif operation == "bi_export":
            max_bi = self.get_max_invoices_bi()
            if max_bi is None:  # Unlimited
                return True
            if max_bi == 0:  # No access
                return False
            return count <= max_bi
        return False


@dataclass
class APICredentials:
    """API credentials entity."""
    
    username: str
    access_key: str
    api_url: str
    partner_id: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Validate credentials format."""
        return (
            bool(self.username) and
            bool(self.access_key) and
            bool(self.api_url) and
            self.api_url.startswith(('http://', 'https://'))
        )


@dataclass
class InvoiceFilter:
    """Filter entity for invoice queries."""
    
    document_id: Optional[str] = None
    created_start: Optional[datetime] = None
    created_end: Optional[datetime] = None
    page_size: int = 100
    page: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert filter to dictionary for API requests."""
        result = {
            'page_size': self.page_size,
            'page': self.page
        }
        
        if self.document_id:
            result['document_id'] = self.document_id
        
        if self.created_start:
            result['created_start'] = self.created_start.isoformat()
        
        if self.created_end:
            result['created_end'] = self.created_end.isoformat()
        
        return result


# ========================================================================================
# NUEVAS ENTIDADES PARA EXPORTACIÓN DE FACTURAS (DataConta Export Service)
# ========================================================================================

@dataclass
class InvoiceExportDocument:
    """Document information for export invoice."""
    id: int
    name: str
    prefix: str
    number: int


@dataclass 
class InvoiceExportCustomer:
    """Customer information for export invoice."""
    id: int
    identification: str
    name: str
    email: str


@dataclass
class InvoiceExportSeller:
    """Seller information for export invoice."""
    id: int
    name: str


@dataclass
class InvoiceExportItem:
    """Item information for export invoice."""
    code: str
    description: str
    quantity: int
    price: Decimal
    discount: Decimal
    total: Decimal
    
    def __post_init__(self):
        """Convert values to Decimal for proper calculation."""
        if not isinstance(self.price, Decimal):
            self.price = Decimal(str(self.price))
        if not isinstance(self.discount, Decimal):
            self.discount = Decimal(str(self.discount))
        if not isinstance(self.total, Decimal):
            self.total = Decimal(str(self.total))


@dataclass
class InvoiceExportPayment:
    """Payment information for export invoice."""
    id: int
    name: str
    value: Decimal
    
    def __post_init__(self):
        """Convert value to Decimal."""
        if not isinstance(self.value, Decimal):
            self.value = Decimal(str(self.value))


@dataclass
class InvoiceExportTotals:
    """Totals information for export invoice."""
    subtotal: Decimal
    discount: Decimal
    taxes: Decimal
    total: Decimal
    
    def __post_init__(self):
        """Convert values to Decimal."""
        if not isinstance(self.subtotal, Decimal):
            self.subtotal = Decimal(str(self.subtotal))
        if not isinstance(self.discount, Decimal):
            self.discount = Decimal(str(self.discount))
        if not isinstance(self.taxes, Decimal):
            self.taxes = Decimal(str(self.taxes))
        if not isinstance(self.total, Decimal):
            self.total = Decimal(str(self.total))


@dataclass
class InvoiceExport:
    """
    Invoice entity for export processing.
    Represents the structure of invoices that will be processed and exported to CSV.
    """
    id: int
    document: InvoiceExportDocument
    date: str
    customer: InvoiceExportCustomer
    seller: InvoiceExportSeller
    items: List[InvoiceExportItem]
    payments: List[InvoiceExportPayment]
    totals: InvoiceExportTotals
    status: str
    observations: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InvoiceExport':
        """Create InvoiceExport from dictionary/JSON data."""
        return cls(
            id=data['id'],
            document=InvoiceExportDocument(**data['document']),
            date=data['date'],
            customer=InvoiceExportCustomer(**data['customer']),
            seller=InvoiceExportSeller(**data['seller']),
            items=[InvoiceExportItem(**item) for item in data['items']],
            payments=[InvoiceExportPayment(**payment) for payment in data['payments']],
            totals=InvoiceExportTotals(**data['totals']),
            status=data['status'],
            observations=data.get('observations')
        )
    
    def get_invoice_number(self) -> str:
        """Get formatted invoice number."""
        return f"{self.document.prefix}-{self.document.number}"
    
    def is_valid(self) -> bool:
        """Validate export invoice business rules."""
        return (
            bool(self.id) and
            bool(self.document) and
            bool(self.customer) and
            bool(self.seller) and
            len(self.items) > 0 and
            len(self.payments) > 0 and
            bool(self.totals) and
            bool(self.status)
        )


@dataclass
class InvoiceExportRow:
    """
    Represents a single row in the CSV export.
    Each row contains flattened invoice data with one item and one payment per row.
    """
    factura_id: int
    fecha: str
    cliente_id: int
    cliente_identificacion: str
    cliente_nombre: str
    cliente_email: str
    vendedor_id: int
    vendedor_nombre: str
    producto_codigo: str
    producto_descripcion: str
    producto_cantidad: int
    producto_precio: Decimal
    producto_descuento: Decimal
    producto_total: Decimal
    pago_metodo: str
    pago_valor: Decimal
    subtotal: Decimal
    descuento_total: Decimal
    impuestos: Decimal
    total: Decimal
    estado: str
    observaciones: Optional[str] = None
    
    def to_csv_row(self) -> List[str]:
        """Convert to CSV row format with proper number formatting."""
        return [
            str(self.factura_id),
            self.fecha,
            str(self.cliente_id),
            self.cliente_identificacion,
            self.cliente_nombre,
            self.cliente_email,
            str(self.vendedor_id),
            self.vendedor_nombre,
            self.producto_codigo,
            self.producto_descripcion,
            self._format_number_with_thousands_separator(self.producto_cantidad),
            self._format_currency(self.producto_precio),
            self._format_currency(self.producto_descuento),
            self._format_currency(self.producto_total),
            self.pago_metodo,
            self._format_currency(self.pago_valor),
            self._format_currency(self.subtotal),
            self._format_currency(self.descuento_total),
            self._format_currency(self.impuestos),
            self._format_currency(self.total),
            self.estado,
            self.observaciones or ""
        ]
    
    def _format_currency(self, value: Decimal) -> str:
        """Format currency values with comma as decimal separator for Spanish/European locale."""
        if value is None:
            return "0,00"
        # Convert to float for formatting, then replace decimal separator
        return f"{float(value):.2f}".replace(".", ",")
    
    def _format_number_with_thousands_separator(self, value: int) -> str:
        """Format integer values as plain numbers for Power BI compatibility."""
        if value is None:
            return "0"
        return f"{value}"
    
    @staticmethod
    def get_csv_headers() -> List[str]:
        """Get CSV headers."""
        return [
            "factura_id", "fecha", "cliente_id", "cliente_identificacion", 
            "cliente_nombre", "cliente_email", "vendedor_id", "vendedor_nombre",
            "producto_codigo", "producto_descripcion", "producto_cantidad",
            "producto_precio", "producto_descuento", "producto_total",
            "pago_metodo", "pago_valor", "subtotal", "descuento_total",
            "impuestos", "total", "estado", "observaciones"
        ]