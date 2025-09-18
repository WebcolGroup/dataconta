"""
Test suite simplificado para validar funcionalidades FREE de DataConta.
Pruebas enfocadas en las funcionalidades implementadas para la versión gratuita.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from decimal import Decimal

from src.domain.services.license_manager import LicenseManager
from src.application.services.BasicStatisticsService import BasicStatisticsService, BasicStatisticsRequest
from src.infrastructure.adapters.simple_txt_logger_adapter import SimpleTxtLogger
from src.presentation.enhanced_menu_config import FreeMenuConfigManager, MenuItemType


class TestFreeLicenseCore(unittest.TestCase):
    """Test core FREE license functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.license_manager = LicenseManager("FREE_TEST_LICENSE")
        self.license_manager._license_type = "FREE"
        self.license_manager._is_valid = True
        
        # Mock repository
        self.invoice_repository = Mock()
        self.invoice_repository.get_invoices.return_value = []


class TestLicenseManagerFREE(TestFreeLicenseCore):
    """Test License Manager enhancements for FREE version."""

    def test_free_license_type(self):
        """Test that license type is correctly set to FREE."""
        self.assertEqual(self.license_manager.get_license_type(), "FREE")
        self.assertTrue(self.license_manager.is_license_valid())

    def test_can_access_gui_lite(self):
        """Test GUI Lite access for FREE license."""
        self.assertTrue(self.license_manager.can_access_gui_lite())

    def test_is_gui_lite_mode(self):
        """Test GUI Lite mode detection."""
        self.assertTrue(self.license_manager.is_gui_lite_mode())

    def test_query_limits_free(self):
        """Test query limits for FREE license."""
        max_query = self.license_manager.get_max_invoices_for_query()
        self.assertEqual(max_query, 100, "FREE license should limit queries to 100 invoices")

    def test_blocked_feature_message(self):
        """Test blocked feature messaging."""
        message = self.license_manager.get_blocked_feature_message("BI Export")
        self.assertIn("característica", message.lower())
        self.assertIn("profesional", message.lower())

    def test_free_features_summary(self):
        """Test FREE features summary."""
        summary = self.license_manager.get_free_features_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("license_type", summary)
        self.assertEqual(summary["license_type"], "FREE")


class TestBasicStatisticsServiceCore(TestFreeLicenseCore):
    """Test Basic Statistics Service for FREE license."""

    def setUp(self):
        """Set up statistics service test fixtures."""
        super().setUp()
        self.stats_service = BasicStatisticsService(
            self.invoice_repository,
            self.license_manager
        )

    def test_statistics_service_initialization(self):
        """Test that statistics service initializes correctly."""
        self.assertIsNotNone(self.stats_service)
        self.assertEqual(self.stats_service._license_manager.get_license_type(), "FREE")

    def test_statistics_request_creation(self):
        """Test that statistics request can be created."""
        request = BasicStatisticsRequest(max_records=50)
        self.assertEqual(request.max_records, 50)
        
        # Test default values
        request_default = BasicStatisticsRequest()
        self.assertEqual(request_default.max_records, 100)

    @patch('src.application.services.BasicStatisticsService.BasicStatisticsService._validate_license_limits')
    def test_basic_statistics_with_mocked_validation(self, mock_validation):
        """Test basic statistics calculation with mocked validation."""
        mock_validation.return_value = (True, "")
        
        # Mock some invoices
        mock_invoices = [
            Mock(total=Decimal('100.00')),
            Mock(total=Decimal('200.00')),
            Mock(total=Decimal('150.00'))
        ]
        self.invoice_repository.get_invoices.return_value = mock_invoices
        
        request = BasicStatisticsRequest(max_records=50)
        response = self.stats_service.calculate_basic_statistics(request)
        
        # With mocked validation, this should succeed
        self.assertTrue(response.success)
        self.assertIsNotNone(response.statistics)


class TestSimpleTxtLoggerCore(TestFreeLicenseCore):
    """Test Simple TXT Logger for FREE license."""

    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    def test_logger_initialization(self, mock_exists, mock_mkdir):
        """Test that logger initializes correctly."""
        mock_exists.return_value = True
        
        with patch('builtins.open', create=True):
            logger = SimpleTxtLogger(self.license_manager, "test_logs")
            self.assertIsNotNone(logger)

    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    @patch('builtins.open', create=True)
    def test_license_validation_logging(self, mock_open, mock_exists, mock_mkdir):
        """Test license validation logging."""
        mock_exists.return_value = True
        
        logger = SimpleTxtLogger(self.license_manager, "test_logs")
        
        # This should not raise an exception
        logger.log_license_validation("FREE", True, "Valid license")
        
        # Verify open was called (for file operations)
        self.assertTrue(mock_open.called)


class TestEnhancedMenuConfigCore(TestFreeLicenseCore):
    """Test Enhanced Menu Config for FREE license."""

    def setUp(self):
        """Set up enhanced menu config test fixtures."""
        super().setUp()
        self.menu_config = FreeMenuConfigManager(self.license_manager)

    def test_menu_config_initialization(self):
        """Test menu configuration initialization."""
        self.assertIsNotNone(self.menu_config)
        self.assertEqual(self.menu_config._license_manager.get_license_type(), "FREE")

    def test_get_menu_sections(self):
        """Test getting menu sections for FREE license."""
        sections = self.menu_config.get_menu_sections()
        self.assertIsInstance(sections, list)
        self.assertGreater(len(sections), 0)

    def test_blocked_feature_message(self):
        """Test blocked feature messaging."""
        message = self.menu_config.get_blocked_feature_message("Advanced Reports")
        self.assertIn("disponible", message)

    def test_free_license_summary(self):
        """Test FREE license summary in menu."""
        summary = self.menu_config.get_free_license_summary()
        self.assertIn("GRATUITA", summary)
        self.assertIn("100", summary)  # Should mention the 100 invoice limit


class TestFREEIntegration(TestFreeLicenseCore):
    """Test overall integration of FREE license features."""

    def test_free_license_complete_workflow(self):
        """Test complete FREE license workflow."""
        # 1. Verify license type and validity
        self.assertEqual(self.license_manager.get_license_type(), "FREE")
        self.assertTrue(self.license_manager.is_license_valid())

        # 2. Verify GUI Lite access
        self.assertTrue(self.license_manager.can_access_gui_lite())
        self.assertTrue(self.license_manager.is_gui_lite_mode())

        # 3. Verify limits
        max_query = self.license_manager.get_max_invoices_for_query()
        self.assertEqual(max_query, 100)

        # 4. Create services
        stats_service = BasicStatisticsService(self.invoice_repository, self.license_manager)
        self.assertIsNotNone(stats_service)

        # 5. Create menu config
        menu_config = FreeMenuConfigManager(self.license_manager)
        sections = menu_config.get_menu_sections()
        self.assertGreater(len(sections), 0)

    def test_free_features_availability(self):
        """Test that FREE features are properly available."""
        # Test GUI Lite
        self.assertTrue(self.license_manager.can_access_gui_lite())
        
        # Test basic statistics
        stats_service = BasicStatisticsService(self.invoice_repository, self.license_manager)
        self.assertIsNotNone(stats_service)
        
        # Test menu configuration
        menu_config = FreeMenuConfigManager(self.license_manager)
        summary = menu_config.get_free_license_summary()
        self.assertIn("100", summary)  # Should show invoice limit
        
        # Test blocked feature messaging
        blocked_msg = self.license_manager.get_blocked_feature_message("Advanced BI")
        self.assertIn("PRO", blocked_msg.upper())


if __name__ == '__main__':
    unittest.main()