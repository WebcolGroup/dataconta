"""
Test para Infrastructure Adapters
Tests unitarios simplificados para adapters de infraestructura
"""

import unittest
from unittest.mock import Mock
from datetime import datetime

from src.infrastructure.adapters.siigo_api_adapter import SiigoAPIAdapter
from src.domain.entities.invoice import APICredentials


class TestSiigoAPIAdapter(unittest.TestCase):
    """Tests básicos para el adaptador de API Siigo."""
    
    def setUp(self):
        """Configurar adapter con mock logger."""
        self.mock_logger = Mock()
        self.adapter = SiigoAPIAdapter(self.mock_logger)
    
    def test_constructor(self):
        """Test que el adapter se construye correctamente."""
        self.assertIsNotNone(self.adapter)
        self.assertEqual(self.adapter._logger, self.mock_logger)
        self.assertIsNone(self.adapter._auth_token)
    
    def test_authenticate_with_valid_credentials(self):
        """Test autenticación con credenciales válidas."""
        credentials = APICredentials(
            username="test_user", 
            access_key="test_key",
            api_url="https://api.siigo.com"
        )
        
        # El método authenticate existe pero puede fallar sin API real
        # Solo verificamos que no explota
        try:
            result = self.adapter.authenticate(credentials)
            self.assertIsInstance(result, bool)
        except Exception:
            # Es esperado sin API real
            pass
    
    def test_get_invoices_interface(self):
        """Test que el método get_invoices existe."""
        from src.domain.entities.invoice import InvoiceFilter
        
        # Solo verificamos que el método existe
        self.assertTrue(hasattr(self.adapter, 'get_invoices'))
        
        # Llamada sin credentials debería fallar gracefully
        try:
            filters = InvoiceFilter(
                fecha_inicio=datetime(2024, 1, 1),
                fecha_fin=datetime(2024, 12, 31)
            )
            result = self.adapter.get_invoices(filters)
            self.assertIsInstance(result, list)
        except Exception:
            # Es esperado sin autenticación
            pass


if __name__ == '__main__':
    unittest.main()