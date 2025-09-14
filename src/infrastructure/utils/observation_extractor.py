"""
DataConta - Observation Data Extractor
Utility for extracting business information from invoice observations.
"""

import re
from typing import Tuple, Dict, Any, List
from src.application.ports.interfaces import Logger


class ObservationExtractor:
    """
    Utility class for extracting structured information from invoice observations.
    
    Extracts client type (Persona Natural/Jurídica) and tax regime information
    from observation strings in Spanish.
    """
    
    def __init__(self, logger: Logger):
        """Initialize the extractor with logger."""
        self._logger = logger
        
        # Patterns for client type detection
        self._persona_juridica_patterns = [
            r"persona\s+jur[ií]dica",
            r"p\.?\s*jur[ií]dica",
            r"empresa",
            r"sociedad",
            r"s\.a\.s",
            r"s\.a\.",
            r"ltda",
            r"corporaci[óo]n"
        ]
        
        self._persona_natural_patterns = [
            r"persona\s+natural",
            r"p\.?\s*natural",
            r"individual"
        ]
        
        # Patterns for tax regime detection
        self._regimen_patterns = {
            "Responsable del IVA": [
                r"responsable\s+del\s+impuesto\s+sobre\s+las\s+ventas",
                r"responsable\s+del\s+iva",
                r"responsable\s+iva"
            ],
            "No Responsable del IVA": [
                r"no\s+responsable\s+del\s+iva",
                r"no\s+responsable\s+iva",
                r"exento\s+iva"
            ],
            "Régimen Simplificado": [
                r"r[ée]gimen\s+simplificado",
                r"simplificado"
            ],
            "Gran Contribuyente": [
                r"gran\s+contribuyente",
                r"g\.?\s*contribuyente"
            ]
        }
    
    def extract_client_info(self, observations: str) -> Tuple[str, str]:
        """
        Extract client type and tax regime from observations.
        
        Args:
            observations: Raw observation string from invoice
            
        Returns:
            Tuple of (tipo_cliente, regimen)
        """
        try:
            if not observations or not isinstance(observations, str):
                return "No Especificado", "No Especificado"
            
            # Clean and normalize text
            clean_text = self._clean_text(observations)
            
            # Extract client type
            tipo_cliente = self._extract_client_type(clean_text)
            
            # Extract tax regime
            regimen = self._extract_tax_regime(clean_text)
            
            self._logger.debug(f"Extracted - Type: {tipo_cliente}, Regime: {regimen}")
            
            return tipo_cliente, regimen
        
        except Exception as e:
            self._logger.error(f"Error extracting client info from observations: {e}")
            return "No Especificado", "No Especificado"
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for pattern matching."""
        # Convert to lowercase and remove extra whitespace
        clean = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Remove special characters but keep spaces, letters, and numbers
        clean = re.sub(r'[^\w\s\.\-]', ' ', clean)
        
        # Remove extra spaces again
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def _extract_client_type(self, text: str) -> str:
        """Extract client type from cleaned text."""
        # Check for Persona Jurídica patterns
        for pattern in self._persona_juridica_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "Persona Jurídica"
        
        # Check for Persona Natural patterns
        for pattern in self._persona_natural_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return "Persona Natural"
        
        return "No Especificado"
    
    def _extract_tax_regime(self, text: str) -> str:
        """Extract tax regime from cleaned text."""
        for regime, patterns in self._regimen_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return regime
        
        return "No Especificado"
    
    def extract_payment_category(self, payment_name: str) -> str:
        """
        Extract payment category from payment name.
        
        Args:
            payment_name: Name of the payment method
            
        Returns:
            Payment category (Efectivo, Tarjeta, Transferencia, etc.)
        """
        try:
            if not payment_name or not isinstance(payment_name, str):
                return "No Especificado"
            
            clean_name = payment_name.lower().strip()
            
            # Payment category patterns
            categories = {
                "Efectivo": ["efectivo", "cash", "contado"],
                "Tarjeta de Crédito": ["tarjeta", "credito", "credit", "visa", "mastercard"],
                "Tarjeta de Débito": ["debito", "debit"],
                "Transferencia": ["transferencia", "transfer", "bancaria", "pse"],
                "Cheque": ["cheque", "check"],
                "Consignación": ["consignacion", "deposito"]
            }
            
            for category, patterns in categories.items():
                for pattern in patterns:
                    if pattern in clean_name:
                        return category
            
            return "Otros"
        
        except Exception as e:
            self._logger.error(f"Error extracting payment category: {e}")
            return "No Especificado"
    
    def extract_product_category(self, description: str) -> str:
        """
        Extract product category from product description.
        
        Args:
            description: Product description
            
        Returns:
            Product category
        """
        try:
            if not description or not isinstance(description, str):
                return "General"
            
            clean_desc = description.lower().strip()
            
            # Product category patterns
            categories = {
                "Servicios": ["servicio", "service", "cuidado", "alojamiento", "consultoria"],
                "Productos": ["producto", "articulo", "item", "mercancia"],
                "Software": ["software", "licencia", "aplicacion", "sistema"],
                "Salud": ["medico", "medicina", "salud", "hospital", "clinica"],
                "Educación": ["educacion", "curso", "capacitacion", "entrenamiento"],
                "Transporte": ["transporte", "flete", "envio", "logistica"],
                "Alimentación": ["alimento", "comida", "restaurante", "catering"]
            }
            
            for category, patterns in categories.items():
                for pattern in patterns:
                    if pattern in clean_desc:
                        return category
            
            return "General"
        
        except Exception as e:
            self._logger.error(f"Error extracting product category: {e}")
            return "General"
    
    def analyze_observations_sample(self, observations_list: List[str]) -> Dict[str, Any]:
        """
        Analyze a sample of observations to provide insights.
        
        Args:
            observations_list: List of observation strings
            
        Returns:
            Dictionary with analysis results
        """
        try:
            analysis = {
                "total_observations": len(observations_list),
                "client_types": {},
                "regimes": {},
                "common_patterns": [],
                "empty_observations": 0
            }
            
            for obs in observations_list:
                if not obs or not obs.strip():
                    analysis["empty_observations"] += 1
                    continue
                
                tipo_cliente, regimen = self.extract_client_info(obs)
                
                # Count client types
                analysis["client_types"][tipo_cliente] = analysis["client_types"].get(tipo_cliente, 0) + 1
                
                # Count regimes
                analysis["regimes"][regimen] = analysis["regimes"].get(regimen, 0) + 1
            
            return analysis
        
        except Exception as e:
            self._logger.error(f"Error analyzing observations sample: {e}")
            return {"error": str(e)}