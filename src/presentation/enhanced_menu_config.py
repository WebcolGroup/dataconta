"""
Enhanced Menu Configuration with FREE License Restrictions
Sistema de menús mejorado que incluye opciones bloqueadas para incentivar upgrades.
"""

from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass
from enum import Enum

from src.domain.services.license_manager import LicenseManager


class MenuItemType(Enum):
    """Tipos de items de menú."""
    AVAILABLE = "available"
    BLOCKED = "blocked"
    UPGRADE_PROMPT = "upgrade_prompt"


@dataclass
class EnhancedMenuOption:
    """Opción de menú mejorada con soporte para restricciones de licencia."""
    id: str
    title: str
    description: str
    emoji: str
    action: Optional[Callable] = None
    required_license: str = "FREE"
    item_type: MenuItemType = MenuItemType.AVAILABLE
    upgrade_message: str = ""
    feature_category: str = "basic"


@dataclass
class EnhancedMenuSection:
    """Sección de menú mejorada con opciones de diferentes tipos."""
    id: str
    title: str
    description: str
    emoji: str
    options: List[EnhancedMenuOption]
    min_license_required: str = "FREE"


class FreeMenuConfigManager:
    """
    Gestor de configuración de menús para licencia FREE.
    Crea menús dinámicos con opciones bloqueadas para incentivar upgrades.
    """
    
    def __init__(self, license_manager: LicenseManager):
        self._license_manager = license_manager
        self._menu_sections: Dict[str, EnhancedMenuSection] = {}
        self._setup_menu_sections()
    
    def _setup_menu_sections(self):
        """Configurar todas las secciones de menú con restricciones FREE."""
        
        # ==========================================
        # SECCIÓN: CONSULTAS Y ANÁLISIS BÁSICO
        # ==========================================
        basic_queries_section = EnhancedMenuSection(
            id="basic_queries",
            title="Consultas y Análisis Básico",
            description="Herramientas básicas de consulta disponibles en FREE",
            emoji="📋",
            options=[
                EnhancedMenuOption(
                    id="query_invoices_limited",
                    title="Consultar Facturas",
                    description="Consultar facturas de venta (máximo 100 registros)",
                    emoji="📄",
                    required_license="FREE",
                    item_type=MenuItemType.AVAILABLE,
                    feature_category="query"
                ),
                EnhancedMenuOption(
                    id="basic_statistics",
                    title="Estadísticas Básicas",
                    description="Ver estadísticas simples de facturas (limitado)",
                    emoji="📊",
                    required_license="FREE",
                    item_type=MenuItemType.AVAILABLE,
                    feature_category="stats"
                ),
                EnhancedMenuOption(
                    id="query_invoices_unlimited",
                    title="🔒 Consulta Ilimitada de Facturas",
                    description="Consultar facturas sin límites (requiere PRO/ENTERPRISE)",
                    emoji="🔒",
                    required_license="PRO",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="Actualiza a PRO para consultar facturas sin límite de 100 registros.",
                    feature_category="query"
                ),
                EnhancedMenuOption(
                    id="advanced_analytics",
                    title="🔒 Análisis Avanzado",
                    description="Análisis detallado con gráficos y tendencias (requiere PRO)",
                    emoji="🔒",
                    required_license="PRO",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="Los análisis avanzados con gráficos están disponibles en PRO y ENTERPRISE.",
                    feature_category="analytics"
                )
            ],
            min_license_required="FREE"
        )
        
        # ==========================================
        # SECCIÓN: EXPORTACIÓN DE DATOS
        # ==========================================
        export_section = EnhancedMenuSection(
            id="data_export",
            title="Exportación de Datos",
            description="Opciones de exportación con diferentes niveles de acceso",
            emoji="📤",
            options=[
                EnhancedMenuOption(
                    id="export_json_free",
                    title="Exportar a JSON",
                    description="Exportación básica a formato JSON (hasta 100 registros)",
                    emoji="📄",
                    required_license="FREE",
                    item_type=MenuItemType.AVAILABLE,
                    feature_category="export"
                ),
                EnhancedMenuOption(
                    id="export_csv_blocked",
                    title="🔒 Exportar a CSV Completo",
                    description="Exportación completa a CSV con todos los campos (requiere PRO)",
                    emoji="🔒",
                    required_license="PRO",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="La exportación CSV completa está disponible en PRO. FREE solo incluye JSON básico.",
                    feature_category="export"
                ),
                EnhancedMenuOption(
                    id="export_excel_blocked",
                    title="🔒 Exportar a Excel",
                    description="Exportación a Excel con formato profesional (requiere PRO)",
                    emoji="🔒",
                    required_license="PRO",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="Exportación a Excel disponible en PRO con formato y gráficos incluidos.",
                    feature_category="export"
                ),
                EnhancedMenuOption(
                    id="export_bi_blocked",
                    title="🔒 Exportación BI Completa",
                    description="Modelo completo para Business Intelligence (requiere ENTERPRISE)",
                    emoji="🔒",
                    required_license="ENTERPRISE",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="El módulo BI completo con modelo estrella está disponible solo en ENTERPRISE.",
                    feature_category="bi"
                )
            ],
            min_license_required="FREE"
        )
        
        # ==========================================
        # SECCIÓN: INFORMES Y REPORTES
        # ==========================================
        reports_section = EnhancedMenuSection(
            id="reports",
            title="Informes y Reportes",
            description="Generación de informes con diferentes niveles de detalle",
            emoji="📈",
            options=[
                EnhancedMenuOption(
                    id="basic_summary_report",
                    title="Reporte Básico",
                    description="Resumen simple de facturas disponible en FREE",
                    emoji="📋",
                    required_license="FREE",
                    item_type=MenuItemType.AVAILABLE,
                    feature_category="report"
                ),
                EnhancedMenuOption(
                    id="detailed_report_blocked",
                    title="🔒 Informes Detallados",
                    description="Reportes completos con análisis detallado (requiere PRO)",
                    emoji="🔒",
                    required_license="PRO",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="Los informes detallados con gráficos y análisis están en PRO y ENTERPRISE.",
                    feature_category="report"
                ),
                EnhancedMenuOption(
                    id="pdf_reports_blocked",
                    title="🔒 Reportes PDF Profesionales",
                    description="Informes en PDF con formato empresarial (requiere PRO)",
                    emoji="🔒",
                    required_license="PRO",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="Generación de PDF profesionales disponible en PRO y ENTERPRISE.",
                    feature_category="report"
                ),
                EnhancedMenuOption(
                    id="dashboard_blocked",
                    title="🔒 Dashboard Interactivo",
                    description="Dashboard en tiempo real con métricas dinámicas (requiere ENTERPRISE)",
                    emoji="🔒",
                    required_license="ENTERPRISE",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="Dashboard interactivo con métricas en tiempo real solo en ENTERPRISE.",
                    feature_category="dashboard"
                )
            ],
            min_license_required="FREE"
        )
        
        # ==========================================
        # SECCIÓN: HERRAMIENTAS E INTEGRACIONES
        # ==========================================
        tools_section = EnhancedMenuSection(
            id="tools_integrations",
            title="Herramientas e Integraciones",
            description="Utilidades y conexiones con sistemas externos",
            emoji="🛠️",
            options=[
                EnhancedMenuOption(
                    id="api_status_check",
                    title="Verificar Estado API",
                    description="Comprobar conectividad con Siigo API",
                    emoji="🔍",
                    required_license="FREE",
                    item_type=MenuItemType.AVAILABLE,
                    feature_category="tool"
                ),
                EnhancedMenuOption(
                    id="basic_config",
                    title="Configuración Básica",
                    description="Ajustes básicos del sistema disponibles en FREE",
                    emoji="⚙️",
                    required_license="FREE",
                    item_type=MenuItemType.AVAILABLE,
                    feature_category="config"
                ),
                EnhancedMenuOption(
                    id="ollama_integration_blocked",
                    title="🔒 Integración con Ollama AI",
                    description="Análisis con inteligencia artificial local (requiere PRO)",
                    emoji="🔒",
                    required_license="PRO",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="La integración con Ollama AI está disponible en PRO y ENTERPRISE.",
                    feature_category="ai"
                ),
                EnhancedMenuOption(
                    id="advanced_integrations_blocked",
                    title="🔒 Integraciones Avanzadas",
                    description="API webhooks, conectores ERP (requiere ENTERPRISE)",
                    emoji="🔒",
                    required_license="ENTERPRISE",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="Integraciones avanzadas con ERP y webhooks solo en ENTERPRISE.",
                    feature_category="integration"
                )
            ],
            min_license_required="FREE"
        )
        
        # ==========================================
        # SECCIÓN: FUNCIONES PREMIUM (Solo bloqueadas)
        # ==========================================
        premium_section = EnhancedMenuSection(
            id="premium_features",
            title="Funciones Premium",
            description="Funcionalidades avanzadas disponibles con upgrade",
            emoji="⭐",
            options=[
                EnhancedMenuOption(
                    id="ai_predictions_blocked",
                    title="🔒 Predicciones con IA",
                    description="Análisis predictivo basado en tendencias históricas",
                    emoji="🔒",
                    required_license="ENTERPRISE",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="Análisis predictivo con IA disponible exclusivamente en ENTERPRISE.",
                    feature_category="ai_advanced"
                ),
                EnhancedMenuOption(
                    id="anomaly_detection_blocked",
                    title="🔒 Detección de Anomalías",
                    description="Identificación automática de patrones inusuales",
                    emoji="🔒",
                    required_license="ENTERPRISE",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="Detección automática de anomalías solo en ENTERPRISE con IA avanzada.",
                    feature_category="ai_advanced"
                ),
                EnhancedMenuOption(
                    id="custom_workflows_blocked",
                    title="🔒 Flujos de Trabajo Personalizados",
                    description="Automatización personalizada de procesos empresariales",
                    emoji="🔒",
                    required_license="ENTERPRISE",
                    item_type=MenuItemType.BLOCKED,
                    upgrade_message="Flujos personalizados y automatización avanzada en ENTERPRISE.",
                    feature_category="automation"
                ),
                EnhancedMenuOption(
                    id="upgrade_info",
                    title="⬆️ Ver Planes de Upgrade",
                    description="Información completa sobre planes PRO y ENTERPRISE",
                    emoji="⬆️",
                    required_license="FREE",
                    item_type=MenuItemType.UPGRADE_PROMPT,
                    feature_category="upgrade"
                )
            ],
            min_license_required="FREE"
        )
        
        # Registrar todas las secciones
        self._menu_sections["basic_queries"] = basic_queries_section
        self._menu_sections["data_export"] = export_section
        self._menu_sections["reports"] = reports_section
        self._menu_sections["tools_integrations"] = tools_section
        self._menu_sections["premium_features"] = premium_section
    
    def get_menu_sections_for_license(self) -> Dict[str, EnhancedMenuSection]:
        """
        Obtener secciones de menú filtradas según la licencia actual.
        """
        current_license = self._license_manager.get_license_type()
        filtered_sections = {}
        
        for section_id, section in self._menu_sections.items():
            # Filtrar opciones según licencia
            filtered_options = []
            
            for option in section.options:
                if option.item_type == MenuItemType.AVAILABLE:
                    # Verificar si la opción está permitida para la licencia actual
                    if self._is_option_allowed(option):
                        filtered_options.append(option)
                elif option.item_type == MenuItemType.BLOCKED:
                    # Siempre mostrar opciones bloqueadas para incentivar upgrade
                    filtered_options.append(option)
                elif option.item_type == MenuItemType.UPGRADE_PROMPT:
                    # Mostrar prompts de upgrade solo en licencia FREE
                    if current_license == "FREE":
                        filtered_options.append(option)
            
            if filtered_options:
                filtered_section = EnhancedMenuSection(
                    id=section.id,
                    title=section.title,
                    description=section.description,
                    emoji=section.emoji,
                    options=filtered_options,
                    min_license_required=section.min_license_required
                )
                filtered_sections[section_id] = filtered_section
        
        return filtered_sections
    
    def _is_option_allowed(self, option: EnhancedMenuOption) -> bool:
        """Verificar si una opción está permitida para la licencia actual."""
        current_license = self._license_manager.get_license_type()
        
        # Mapeo de jerarquía de licencias
        license_hierarchy = {
            "FREE": 0,
            "PRO": 1,
            "ENTERPRISE": 2
        }
        
        current_level = license_hierarchy.get(current_license, 0)
        required_level = license_hierarchy.get(option.required_license, 0)
        
        return current_level >= required_level
    
    def get_blocked_feature_message(self, option_id: str) -> str:
        """
        Obtener mensaje de upgrade para una opción bloqueada.
        """
        for section in self._menu_sections.values():
            for option in section.options:
                if option.id == option_id and option.item_type == MenuItemType.BLOCKED:
                    base_message = option.upgrade_message or f"La funcionalidad '{option.title}' requiere una licencia superior."
                    
                    # Agregar información de planes
                    upgrade_info = self._get_upgrade_info_for_feature(option.required_license)
                    
                    return f"{base_message}\n\n{upgrade_info}"
        
        return "Esta funcionalidad requiere una licencia superior. Contacta ventas@dataconta.com"
    
    def _get_upgrade_info_for_feature(self, required_license: str) -> str:
        """Obtener información de upgrade específica para el nivel requerido."""
        
        if required_license == "PRO":
            return """💼 LICENCIA PROFESIONAL:
• Hasta 1,000 facturas por consulta
• Exportación CSV y Excel completa
• Informes detallados con gráficos
• Integración básica con IA
• Soporte por email

💰 Precio: $29/mes
🌐 Más info: www.dataconta.com/pro"""
        
        elif required_license == "ENTERPRISE":
            return """🏢 LICENCIA ENTERPRISE:
• Consultas ilimitadas
• Módulo BI completo
• IA avanzada y predicciones
• Integraciones personalizadas
• Dashboard en tiempo real
• Soporte prioritario 24/7

💰 Precio: $99/mes
🌐 Más info: www.dataconta.com/enterprise"""
        
        return """📞 Contacta con nuestro equipo:
• Email: ventas@dataconta.com
• Web: www.dataconta.com/planes
• Tel: +1-800-DATACONTA"""
    
    def get_free_license_summary(self) -> str:
        """Obtener resumen de funcionalidades disponibles en FREE."""
        available_features = []
        blocked_count = 0
        
        for section in self._menu_sections.values():
            for option in section.options:
                if option.item_type == MenuItemType.AVAILABLE and self._is_option_allowed(option):
                    available_features.append(f"• {option.title}")
                elif option.item_type == MenuItemType.BLOCKED:
                    blocked_count += 1
        
        summary = f"""
🆓 DATACONTA FREE - FUNCIONALIDADES DISPONIBLES:

✅ Funciones incluidas ({len(available_features)}):
""" + "\n".join(available_features) + f"""

🔒 Funciones bloqueadas: {blocked_count}
⬆️  Actualiza para desbloquear todas las funcionalidades

💼 PRO: Perfecto para pequeñas empresas
🏢 ENTERPRISE: Solución completa para grandes organizaciones

📞 Contacto: ventas@dataconta.com
"""
        return summary.strip()
    
    def get_section_by_id(self, section_id: str) -> Optional[EnhancedMenuSection]:
        """Obtener una sección específica por ID."""
        return self._menu_sections.get(section_id)
    
    def get_option_by_id(self, option_id: str) -> Optional[EnhancedMenuOption]:
        """Obtener una opción específica por ID."""
        for section in self._menu_sections.values():
            for option in section.options:
                if option.id == option_id:
                    return option
        return None
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de menús."""
        total_options = 0
        available_options = 0
        blocked_options = 0
        upgrade_prompts = 0
        
        for section in self._menu_sections.values():
            for option in section.options:
                total_options += 1
                if option.item_type == MenuItemType.AVAILABLE:
                    if self._is_option_allowed(option):
                        available_options += 1
                elif option.item_type == MenuItemType.BLOCKED:
                    blocked_options += 1
                elif option.item_type == MenuItemType.UPGRADE_PROMPT:
                    upgrade_prompts += 1
        
        return {
            "total_sections": len(self._menu_sections),
            "total_options": total_options,
            "available_options": available_options,
            "blocked_options": blocked_options,
            "upgrade_prompts": upgrade_prompts,
            "current_license": self._license_manager.get_license_type(),
            "license_display_name": self._license_manager.get_license_display_name()
        }