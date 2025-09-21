"""
Configuración de pytest para DataConta FREE
Contiene fixtures y configuración global para las pruebas.
"""

import pytest
import os
import sys
from datetime import datetime, date
from typing import Dict, List, Any
from unittest.mock import Mock, MagicMock

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.application.services.kpi_service import KPIService, KPIData
from src.application.services.export_service import ExportService
from src.domain.entities.invoice import Invoice, InvoiceFilter


@pytest.fixture
def sample_invoice_data():
    """Fixture con datos de facturas de ejemplo para pruebas."""
    return [
        {
            'id': 'INV001',
            'number': 'F001',
            'date': '2025-01-15',
            'customer': {
                'identification': '12345678',
                'name': 'Cliente Test 1',
                'branch_office': 0
            },
            'total': 1000000,
            'subtotal': 840336,
            'total_tax': 159664,
            'status': 'active',
            'items': [
                {
                    'code': 'PROD001',
                    'description': 'Producto Test 1',
                    'quantity': 2,
                    'price': 420168,
                    'total': 840336
                }
            ]
        },
        {
            'id': 'INV002',
            'number': 'F002',
            'date': '2025-01-16',
            'customer': {
                'identification': '87654321',
                'name': 'Cliente Test 2',
                'branch_office': 0
            },
            'total': 500000,
            'subtotal': 420168,
            'total_tax': 79832,
            'status': 'active',
            'items': [
                {
                    'code': 'PROD002',
                    'description': 'Producto Test 2',
                    'quantity': 1,
                    'price': 420168,
                    'total': 420168
                }
            ]
        },
        {
            'id': 'INV003',
            'number': 'F003',
            'date': '2025-01-17',
            'customer': {
                'identification': '12345678',
                'name': 'Cliente Test 1',
                'branch_office': 0
            },
            'total': 2000000,
            'subtotal': 1680672,
            'total_tax': 319328,
            'status': 'active',
            'items': [
                {
                    'code': 'PROD001',
                    'description': 'Producto Test 1',
                    'quantity': 4,
                    'price': 420168,
                    'total': 1680672
                }
            ]
        }
    ]


@pytest.fixture
def mock_invoice_repository():
    """Mock del repositorio de facturas."""
    mock_repo = Mock()
    mock_repo.get_invoices.return_value = []
    mock_repo.get_invoice_states.return_value = [
        {'id': 'open', 'name': 'Abierta'},
        {'id': 'closed', 'name': 'Cerrada'},
        {'id': 'cancelled', 'name': 'Anulada'}
    ]
    return mock_repo


@pytest.fixture
def mock_file_storage():
    """Mock del almacenamiento de archivos."""
    mock_storage = Mock()
    mock_storage.save_data.return_value = True
    mock_storage.load_data.return_value = {}
    mock_storage.file_exists.return_value = False
    return mock_storage


@pytest.fixture
def mock_logger():
    """Mock del logger."""
    mock_logger = Mock()
    return mock_logger


@pytest.fixture
def kpi_service(mock_invoice_repository, mock_file_storage, mock_logger):
    """Instancia del servicio KPI con mocks."""
    return KPIService(
        invoice_repository=mock_invoice_repository,
        file_storage=mock_file_storage,
        logger=mock_logger
    )


@pytest.fixture
def export_service(mock_invoice_repository, mock_file_storage, mock_logger):
    """Instancia del servicio de exportación con mocks."""
    return ExportService(
        invoice_repository=mock_invoice_repository,
        file_storage=mock_file_storage,
        logger=mock_logger
    )


@pytest.fixture
def temp_output_dir(tmp_path):
    """Directorio temporal para archivos de salida."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    return str(output_dir)
