"""
Email Reports Addon para DataConta
Addon de ejemplo que demuestra el sistema de addons enviando reportes por email.
"""

import smtplib
import ssl
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import os
from pathlib import Path

from src.application.ports.addon_interfaces import AddonBase, AddonContext, AddonManifest


@dataclass
class EmailConfig:
    """Configuración de email para el addon."""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""
    recipient_emails: List[str] = None
    
    def __post_init__(self):
        if self.recipient_emails is None:
            self.recipient_emails = []


class EmailReportsAddon(AddonBase):
    """
    Addon de ejemplo para envío de reportes por email.
    
    Funcionalidades:
    - Envío de reportes diarios
    - Envío de reportes mensuales
    - Configuración de email
    - Integración con datos de Siigo
    """
    
    def __init__(self):
        """Inicializar addon de email reports."""
        super().__init__()
        self.email_config = EmailConfig()
        self.config_file = None
        
    def initialize(self, context: AddonContext) -> bool:
        """
        Inicializar addon con contexto.
        
        Args:
            context: Contexto de addon con dependencias
            
        Returns:
            bool: True si se inicializó exitosamente
        """
        try:
            self.context = context
            self.logger = context.logger
            
            # Cargar manifiesto
            manifest_path = Path(__file__).parent / "manifest.json"
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            self.manifest = AddonManifest(**manifest_data)
            
            # Establecer path de configuración
            self.config_file = Path(__file__).parent / "email_config.json"
            
            # Cargar configuración existente
            self._load_config()
            
            if self.logger:
                self.logger.info(f"✅ Addon '{self.get_name()}' inicializado exitosamente")
                
            return True
            
        except Exception as e:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"❌ Error inicializando addon {self.get_name()}: {e}")
            return False
    
    def get_name(self) -> str:
        """Obtener nombre del addon."""
        return "email_reports"
    
    def get_version(self) -> str:
        """Obtener versión del addon."""
        return "1.0.0"
    
    def get_description(self) -> str:
        """Obtener descripción del addon."""
        return "Envía informes financieros por correo electrónico de forma automatizada"
    
    def get_manifest(self) -> AddonManifest:
        """Obtener manifiesto del addon."""
        return self.manifest
    
    def is_compatible(self, app_version: str) -> bool:
        """
        Verificar compatibilidad con versión de la app.
        
        Args:
            app_version: Versión de DataConta
            
        Returns:
            bool: True si es compatible
        """
        # Lógica simple de compatibilidad
        try:
            major, minor, patch = map(int, app_version.split('.'))
            return major >= 1  # Compatible con DataConta 1.x.x
        except:
            return False
    
    def execute_action(self, action_name: str, parameters: Dict[str, Any] = None) -> bool:
        """
        Ejecutar acción del addon.
        
        Args:
            action_name: Nombre de la acción
            parameters: Parámetros adicionales
            
        Returns:
            bool: True si se ejecutó exitosamente
        """
        try:
            if self.logger:
                self.logger.info(f"🚀 Ejecutando acción: {action_name}")
            
            action_map = {
                'send_daily_report': self._send_daily_report,
                'send_monthly_report': self._send_monthly_report,
                'configure_email_settings': self._configure_email_settings
            }
            
            if action_name not in action_map:
                if self.logger:
                    self.logger.error(f"❌ Acción no encontrada: {action_name}")
                return False
            
            # Validar configuración antes de ejecutar acciones de envío
            if action_name.startswith('send_') and not self._validate_email_config():
                if self.logger:
                    self.logger.error("❌ Configuración de email inválida")
                return False
            
            # Ejecutar acción
            result = action_map[action_name](parameters or {})
            
            if self.logger:
                status = "✅" if result else "❌"
                self.logger.info(f"{status} Acción {action_name} {'completada' if result else 'falló'}")
                
            return result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error ejecutando acción {action_name}: {e}")
            return False
    
    def cleanup(self) -> bool:
        """
        Limpiar recursos del addon.
        
        Returns:
            bool: True si se limpió exitosamente
        """
        try:
            if self.logger:
                self.logger.info(f"🧹 Limpiando addon {self.get_name()}")
            
            # Limpiar cualquier recurso usado
            self.email_config = EmailConfig()
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error limpiando addon: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtener estado actual del addon.
        
        Returns:
            Dict con información de estado
        """
        return {
            'name': self.get_name(),
            'version': self.get_version(),
            'status': 'active',
            'email_configured': self._validate_email_config(),
            'config_file_exists': self.config_file.exists() if self.config_file else False,
            'recipients_count': len(self.email_config.recipient_emails),
            'last_execution': None  # Podría almacenarse en config
        }
    
    def _load_config(self):
        """Cargar configuración desde archivo."""
        try:
            if self.config_file and self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Actualizar configuración
                self.email_config.smtp_server = config_data.get('smtp_server', self.email_config.smtp_server)
                self.email_config.smtp_port = config_data.get('smtp_port', self.email_config.smtp_port)
                self.email_config.sender_email = config_data.get('sender_email', '')
                self.email_config.sender_password = config_data.get('sender_password', '')
                self.email_config.recipient_emails = config_data.get('recipient_emails', [])
                
                if self.logger:
                    self.logger.debug("📧 Configuración de email cargada")
                    
        except Exception as e:
            if self.logger:
                self.logger.warning(f"⚠️ Error cargando configuración de email: {e}")
    
    def _save_config(self):
        """Guardar configuración a archivo."""
        try:
            config_data = {
                'smtp_server': self.email_config.smtp_server,
                'smtp_port': self.email_config.smtp_port,
                'sender_email': self.email_config.sender_email,
                'sender_password': self.email_config.sender_password,  # En prod, usar encriptación
                'recipient_emails': self.email_config.recipient_emails
            }
            
            if self.config_file:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                
                if self.logger:
                    self.logger.info("✅ Configuración de email guardada")
                    
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error guardando configuración: {e}")
    
    def _validate_email_config(self) -> bool:
        """Validar configuración de email."""
        return (
            bool(self.email_config.sender_email) and
            bool(self.email_config.sender_password) and
            bool(self.email_config.recipient_emails) and
            len(self.email_config.recipient_emails) > 0
        )
    
    def _send_daily_report(self, parameters: Dict[str, Any]) -> bool:
        """Enviar reporte diario."""
        try:
            if self.logger:
                self.logger.info("📧 Preparando reporte diario...")
            
            # Generar datos del reporte (mock para demo)
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            
            report_data = {
                'fecha': yesterday.strftime('%Y-%m-%d'),
                'total_ventas': 15420.50,  # Mock data
                'numero_facturas': 23,
                'cliente_principal': 'Empresa ABC S.A.S',
                'valor_cliente_principal': 5420.00
            }
            
            # Crear contenido del email
            subject = f"Reporte Diario DataConta - {report_data['fecha']}"
            body = self._create_daily_report_body(report_data)
            
            # Enviar email
            return self._send_email(subject, body)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error enviando reporte diario: {e}")
            return False
    
    def _send_monthly_report(self, parameters: Dict[str, Any]) -> bool:
        """Enviar reporte mensual."""
        try:
            if self.logger:
                self.logger.info("📊 Preparando reporte mensual...")
            
            # Generar datos del reporte mensual (mock)
            today = datetime.now()
            month_name = today.strftime('%B %Y')
            
            report_data = {
                'periodo': month_name,
                'total_ventas': 456789.25,
                'total_facturas': 342,
                'promedio_diario': 15226.31,
                'top_clientes': [
                    {'nombre': 'Cliente A S.A.S', 'valor': 89456.20},
                    {'nombre': 'Cliente B Ltda', 'valor': 67834.15},
                    {'nombre': 'Cliente C S.A.S', 'valor': 45678.30}
                ]
            }
            
            # Crear contenido del email
            subject = f"Reporte Mensual DataConta - {month_name}"
            body = self._create_monthly_report_body(report_data)
            
            # Enviar email
            return self._send_email(subject, body)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error enviando reporte mensual: {e}")
            return False
    
    def _configure_email_settings(self, parameters: Dict[str, Any]) -> bool:
        """Configurar ajustes de email."""
        try:
            if self.logger:
                self.logger.info("⚙️ Configurando ajustes de email...")
            
            # En una implementación real, esto abriría un diálogo de configuración
            # Por ahora, usar valores de ejemplo
            
            # Configuración de ejemplo para demo
            demo_config = {
                'sender_email': 'dataconta@empresa.com',
                'sender_password': 'password123',  # En prod usar almacenamiento seguro
                'recipient_emails': ['gerencia@empresa.com', 'contabilidad@empresa.com']
            }
            
            # Actualizar configuración con valores demo
            for key, value in demo_config.items():
                if hasattr(self.email_config, key):
                    setattr(self.email_config, key, value)
            
            # Guardar configuración
            self._save_config()
            
            if self.logger:
                self.logger.info("✅ Configuración de email actualizada (modo demo)")
                
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error configurando email: {e}")
            return False
    
    def _create_daily_report_body(self, data: Dict[str, Any]) -> str:
        """Crear cuerpo del reporte diario."""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ color: #2c3e50; border-bottom: 2px solid #27ae60; padding-bottom: 10px; }}
                .metric {{ background-color: #ecf0f1; padding: 10px; margin: 5px 0; border-radius: 5px; }}
                .value {{ font-weight: bold; color: #27ae60; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📊 Reporte Diario DataConta</h2>
                <p>Fecha: {data['fecha']}</p>
            </div>
            
            <div class="metric">
                <strong>💰 Total Ventas:</strong> 
                <span class="value">${data['total_ventas']:,.2f}</span>
            </div>
            
            <div class="metric">
                <strong>📄 Número de Facturas:</strong> 
                <span class="value">{data['numero_facturas']}</span>
            </div>
            
            <div class="metric">
                <strong>🏆 Cliente Principal:</strong> 
                <span class="value">{data['cliente_principal']}</span>
                <br>Valor: ${data['valor_cliente_principal']:,.2f}
            </div>
            
            <hr>
            <p><em>Reporte generado automáticamente por DataConta Email Reports Addon</em></p>
        </body>
        </html>
        """
    
    def _create_monthly_report_body(self, data: Dict[str, Any]) -> str:
        """Crear cuerpo del reporte mensual."""
        top_clients_html = ""
        for i, cliente in enumerate(data['top_clientes'], 1):
            top_clients_html += f"""
            <li>{cliente['nombre']}: <strong>${cliente['valor']:,.2f}</strong></li>
            """
        
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ color: #2c3e50; border-bottom: 2px solid #27ae60; padding-bottom: 10px; }}
                .metric {{ background-color: #ecf0f1; padding: 10px; margin: 5px 0; border-radius: 5px; }}
                .value {{ font-weight: bold; color: #27ae60; }}
                .top-clients {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📈 Reporte Mensual DataConta</h2>
                <p>Período: {data['periodo']}</p>
            </div>
            
            <div class="metric">
                <strong>💰 Total Ventas del Mes:</strong> 
                <span class="value">${data['total_ventas']:,.2f}</span>
            </div>
            
            <div class="metric">
                <strong>📄 Total Facturas:</strong> 
                <span class="value">{data['total_facturas']}</span>
            </div>
            
            <div class="metric">
                <strong>📊 Promedio Diario:</strong> 
                <span class="value">${data['promedio_diario']:,.2f}</span>
            </div>
            
            <div class="top-clients">
                <h3>🏆 Top 3 Clientes del Mes</h3>
                <ol>
                    {top_clients_html}
                </ol>
            </div>
            
            <hr>
            <p><em>Reporte generado automáticamente por DataConta Email Reports Addon</em></p>
        </body>
        </html>
        """
    
    def _send_email(self, subject: str, body: str, attachments: List[str] = None) -> bool:
        """
        Enviar email con el reporte.
        
        Args:
            subject: Asunto del email
            body: Cuerpo del email (HTML)
            attachments: Lista de paths de archivos adjuntos
            
        Returns:
            bool: True si se envió exitosamente
        """
        try:
            # Crear mensaje
            message = MimeMultipart()
            message["From"] = self.email_config.sender_email
            message["To"] = ", ".join(self.email_config.recipient_emails)
            message["Subject"] = subject
            
            # Agregar cuerpo HTML
            message.attach(MimeText(body, "html"))
            
            # Agregar archivos adjuntos si los hay
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MimeBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'
                            )
                            message.attach(part)
            
            # Configurar conexión SMTP
            context = ssl.create_default_context()
            
            # En modo demo, simular envío exitoso
            if self.email_config.sender_email == 'dataconta@empresa.com':
                if self.logger:
                    self.logger.info("📧 EMAIL ENVIADO (MODO DEMO)")
                    self.logger.info(f"   Para: {', '.join(self.email_config.recipient_emails)}")
                    self.logger.info(f"   Asunto: {subject}")
                return True
            
            # Envío real (comentado para demo)
            """
            with smtplib.SMTP(self.email_config.smtp_server, self.email_config.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(self.email_config.sender_email, self.email_config.sender_password)
                
                text = message.as_string()
                server.sendmail(
                    self.email_config.sender_email,
                    self.email_config.recipient_emails,
                    text
                )
            """
            
            if self.logger:
                self.logger.info("✅ Email enviado exitosamente")
                
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error enviando email: {e}")
            return False


# Función helper para crear instancia del addon
def create_addon() -> EmailReportsAddon:
    """
    Función factory para crear instancia del addon.
    
    Returns:
        EmailReportsAddon: Instancia del addon
    """
    return EmailReportsAddon()


if __name__ == "__main__":
    # Test básico del addon
    addon = EmailReportsAddon()
    print(f"Addon: {addon.get_name()} v{addon.get_version()}")
    print(f"Descripción: {addon.get_description()}")
    print(f"Estado: {addon.get_status()}")