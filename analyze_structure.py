"""
Análisis temporal de estructura de facturas Siigo - DataConta
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.infrastructure.adapters.siigo_api_adapter import SiigoAPIAdapter
from src.infrastructure.adapters.logger_adapter import LoggerAdapter
from src.infrastructure.config.environment_config import EnvironmentConfigurationProvider
from src.domain.entities.invoice import InvoiceFilter


def analyze_siigo_structure():
    """Analizar estructura completa de facturas Siigo."""
    
    # Setup
    config = EnvironmentConfigurationProvider()
    logger = LoggerAdapter(__name__)
    siigo_adapter = SiigoAPIAdapter(logger)
    
    try:
        # Configurar credenciales
        credentials = config.get_siigo_credentials()
        siigo_adapter.configure(credentials)
        
        # Autenticar
        if not siigo_adapter.authenticate(credentials):
            print("❌ Error de autenticación")
            return
            
        print("✅ Autenticación exitosa")
        
        # Obtener facturas RAW (sin filtros para obtener máximo detalle)
        filters = InvoiceFilter()
        raw_invoices = siigo_adapter.get_invoices_raw(filters)
        
        print(f"📊 Obtenidas {len(raw_invoices)} facturas")
        
        if raw_invoices:
            # Analizar primera factura para estructura completa
            first_invoice = raw_invoices[0]
            
            print("\n🔍 ESTRUCTURA COMPLETA DE FACTURA SIIGO:")
            print("=" * 60)
            
            # Guardar estructura completa
            with open("siigo_invoice_structure.json", "w", encoding="utf-8") as f:
                json.dump(first_invoice, f, indent=2, ensure_ascii=False, default=str)
            
            print("📄 Estructura guardada en: siigo_invoice_structure.json")
            
            # Mostrar campos principales
            print("\n📋 CAMPOS DISPONIBLES:")
            print("-" * 30)
            
            def analyze_fields(data, prefix=""):
                """Analizar campos recursivamente."""
                fields = []
                if isinstance(data, dict):
                    for key, value in data.items():
                        current_field = f"{prefix}.{key}" if prefix else key
                        fields.append(current_field)
                        
                        if isinstance(value, dict) and value:
                            fields.extend(analyze_fields(value, current_field))
                        elif isinstance(value, list) and value and isinstance(value[0], dict):
                            fields.extend(analyze_fields(value[0], f"{current_field}[0]"))
                            
                return fields
            
            all_fields = analyze_fields(first_invoice)
            
            # Campos requeridos según la especificación
            required_fields = [
                "Discount", "TaxAmount", "NetAmount", "Status", "PaymentMethod", 
                "Segment", "Category", "Vendor", "Channel", "Currency", "Country"
            ]
            
            print(f"🔍 Total campos encontrados: {len(all_fields)}")
            print("\n📊 COMPARACIÓN CON CAMPOS REQUERIDOS:")
            print("-" * 50)
            
            for req_field in required_fields:
                # Buscar coincidencias (case insensitive y parciales)
                matches = [field for field in all_fields if req_field.lower() in field.lower()]
                
                if matches:
                    print(f"✅ {req_field}: {matches}")
                else:
                    print(f"❌ {req_field}: NO ENCONTRADO")
            
            print(f"\n📝 TODOS LOS CAMPOS DISPONIBLES:")
            print("-" * 40)
            for field in sorted(all_fields):
                print(f"  • {field}")
                
        else:
            print("⚠️ No se obtuvieron facturas")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    analyze_siigo_structure()