"""
Siigo Financial API Adapter.
Infrastructure adapter for consuming Siigo financial APIs.
"""

import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

from src.application.ports.interfaces import (
    SiigoFinancialAPIClient, Logger, APIClient
)


class SiigoFinancialAPIAdapter(SiigoFinancialAPIClient):
    """
    Adaptador para consumir APIs financieras de Siigo.
    Implementa el puerto SiigoFinancialAPIClient.
    """
    
    def __init__(
        self, 
        base_url: str,
        api_client: APIClient,
        logger: Logger,
        timeout: int = 30
    ):
        """
        Inicializar adaptador de Siigo Financial API.
        
        Args:
            base_url: URL base de la API de Siigo
            api_client: Cliente API básico para autenticación
            logger: Logger para registrar operaciones
            timeout: Timeout para requests en segundos
        """
        self._base_url = base_url.rstrip('/')
        self._api_client = api_client
        self._logger = logger
        self._timeout = timeout
        self._session = requests.Session()
        self._auth_token = None
        self._token_expiry = None
    
    def _ensure_authenticated(self) -> bool:
        """Asegurar que la autenticación esté activa."""
        if not self._api_client.is_connected():
            self._logger.error("API client no está conectado")
            return False
        
        # Obtener el token del API client
        if hasattr(self._api_client, '_auth_token') and self._api_client._auth_token:
            self._auth_token = self._api_client._auth_token
            return True
        else:
            self._logger.error("No se pudo obtener el token de autenticación")
            return False
    
    def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """
        Realizar petición HTTP a la API de Siigo.
        
        Args:
            endpoint: Endpoint de la API (sin base_url)
            params: Parámetros de query
            method: Método HTTP
            
        Returns:
            Respuesta JSON de la API
            
        Raises:
            Exception: En caso de error en la petición
        """
        if not self._ensure_authenticated():
            raise Exception("Error de autenticación con API de Siigo")
        
        url = f"{self._base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._auth_token}",
            "Accept": "application/json"
        }
        
        # Agregar Partner-Id si está disponible en el API client
        if (hasattr(self._api_client, '_credentials') and 
            self._api_client._credentials and 
            self._api_client._credentials.partner_id):
            headers["Partner-Id"] = self._api_client._credentials.partner_id
        
        try:
            return self._make_request_with_retry(url, params, headers, method)
                
        except Exception as e:
            error_msg = f"Error en petición a {url}: {str(e)}"
            self._logger.error(error_msg)
            raise Exception(error_msg)
    
    def _make_request_with_retry(
        self,
        url: str,
        params: Optional[Dict[str, Any]],
        headers: Dict[str, str],
        method: str = "GET",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Realizar petición HTTP con lógica de reintento para errores temporales.
        """
        import random
        
        for attempt in range(max_retries + 1):
            try:
                self._logger.debug(f"Petición {method} a {url} (intento {attempt + 1}/{max_retries + 1}) con parámetros: {params}")
                
                if method == "GET":
                    response = self._session.get(url, params=params, headers=headers, timeout=self._timeout)
                elif method == "POST":
                    response = self._session.post(url, json=params, headers=headers, timeout=self._timeout)
                else:
                    raise Exception(f"Método HTTP no soportado: {method}")
                
                response.raise_for_status()
                
                # Verificar si la respuesta tiene contenido JSON
                if response.content:
                    return response.json()
                else:
                    return {"message": "Respuesta vacía", "status": "success"}
                    
            except requests.exceptions.HTTPError as e:
                # Errores temporales que podemos reintentar
                if e.response.status_code in [429, 503, 502, 504] and attempt < max_retries:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)  # Backoff exponencial con jitter
                    self._logger.warning(f"Error temporal {e.response.status_code}, reintentando en {wait_time:.2f} segundos...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
                    
            except requests.exceptions.Timeout as e:
                if attempt < max_retries:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    self._logger.warning(f"Timeout, reintentando en {wait_time:.2f} segundos...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Timeout en petición a {url}")
                    
            except requests.exceptions.RequestException as e:
                # Para otros errores de red, intentar una vez más
                if attempt < max_retries:
                    wait_time = 1 + random.uniform(0, 1)
                    self._logger.warning(f"Error de red, reintentando en {wait_time:.2f} segundos...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise
        
        # Si llegamos aquí, todos los reintentos fallaron
        raise Exception(f"Fallaron todos los reintentos para {url}")
    
    def obtener_facturas_periodo(
        self, 
        fecha_inicio: str, 
        fecha_fin: str,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtener facturas de un período desde la API de Siigo.
        
        Args:
            fecha_inicio: Fecha inicio en formato YYYY-MM-DD
            fecha_fin: Fecha fin en formato YYYY-MM-DD
            page_size: Tamaño de página para paginación
            
        Returns:
            Lista de facturas del período
        """
        self._logger.info(f"Obteniendo facturas del período {fecha_inicio} - {fecha_fin}")
        
        all_invoices = []
        page = 1
        
        try:
            while True:
                params = {
                    "date_start": fecha_inicio,
                    "date_end": fecha_fin,
                    "page": page,
                    "page_size": page_size
                }
                
                response = self._make_request("/v1/invoices", params)
                
                # Verificar estructura de respuesta
                if "results" in response:
                    invoices = response["results"]
                elif isinstance(response, list):
                    invoices = response
                else:
                    self._logger.warning("Estructura de respuesta inesperada para facturas")
                    break
                
                if not invoices:
                    break
                
                all_invoices.extend(invoices)
                
                # Verificar si hay más páginas
                if len(invoices) < page_size:
                    break
                    
                page += 1
                time.sleep(0.1)  # Rate limiting básico
            
            self._logger.info(f"Obtenidas {len(all_invoices)} facturas del período")
            return all_invoices
            
        except Exception as e:
            self._logger.error(f"Error obteniendo facturas: {str(e)}")
            raise
    
    def obtener_notas_credito_periodo(
        self, 
        fecha_inicio: str, 
        fecha_fin: str,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtener notas de crédito de un período desde la API de Siigo.
        
        Args:
            fecha_inicio: Fecha inicio en formato YYYY-MM-DD
            fecha_fin: Fecha fin en formato YYYY-MM-DD
            page_size: Tamaño de página
            
        Returns:
            Lista de notas de crédito del período
        """
        self._logger.info(f"Obteniendo notas de crédito del período {fecha_inicio} - {fecha_fin}")
        
        all_credit_notes = []
        page = 1
        
        try:
            while True:
                params = {
                    "date_start": fecha_inicio,
                    "date_end": fecha_fin,
                    "page": page,
                    "page_size": page_size
                }
                
                response = self._make_request("/v1/credit-notes", params)
                
                # Procesar respuesta similar a facturas
                if "results" in response:
                    credit_notes = response["results"]
                elif isinstance(response, list):
                    credit_notes = response
                else:
                    break
                
                if not credit_notes:
                    break
                
                all_credit_notes.extend(credit_notes)
                
                if len(credit_notes) < page_size:
                    break
                    
                page += 1
                time.sleep(0.1)
            
            self._logger.info(f"Obtenidas {len(all_credit_notes)} notas de crédito del período")
            return all_credit_notes
            
        except Exception as e:
            self._logger.error(f"Error obteniendo notas de crédito: {str(e)}")
            raise
    
    def obtener_compras_periodo(
        self, 
        fecha_inicio: str, 
        fecha_fin: str,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtener compras de un período desde la API de Siigo.
        
        Args:
            fecha_inicio: Fecha inicio en formato YYYY-MM-DD
            fecha_fin: Fecha fin en formato YYYY-MM-DD
            page_size: Tamaño de página
            
        Returns:
            Lista de compras del período
        """
        self._logger.info(f"Obteniendo compras del período {fecha_inicio} - {fecha_fin}")
        
        all_purchases = []
        page = 1
        
        try:
            while True:
                params = {
                    "date_start": fecha_inicio,
                    "date_end": fecha_fin,
                    "page": page,
                    "page_size": page_size
                }
                
                response = self._make_request("/v1/purchases", params)
                
                # Procesar respuesta
                if "results" in response:
                    purchases = response["results"]
                elif isinstance(response, list):
                    purchases = response
                else:
                    break
                
                if not purchases:
                    break
                
                all_purchases.extend(purchases)
                
                if len(purchases) < page_size:
                    break
                    
                page += 1
                # Aumentar el rate limiting para evitar errores 503
                time.sleep(0.5)  # Esperar más tiempo entre páginas
            
            self._logger.info(f"Obtenidas {len(all_purchases)} compras del período")
            return all_purchases
            
        except Exception as e:
            self._logger.error(f"Error obteniendo compras: {str(e)}")
            raise
    
    def obtener_asientos_contables_periodo(
        self, 
        fecha_inicio: str, 
        fecha_fin: str,
        page_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Obtener asientos contables de un período desde la API de Siigo.
        
        Args:
            fecha_inicio: Fecha inicio en formato YYYY-MM-DD
            fecha_fin: Fecha fin en formato YYYY-MM-DD
            page_size: Tamaño de página
            
        Returns:
            Lista de asientos contables del período
        """
        self._logger.info(f"Obteniendo asientos contables del período {fecha_inicio} - {fecha_fin}")
        
        all_journal_entries = []
        page = 1
        
        try:
            while True:
                params = {
                    "date_start": fecha_inicio,
                    "date_end": fecha_fin,
                    "page": page,
                    "page_size": page_size
                }
                
                # Intentar con diferentes endpoints posibles para asientos contables
                endpoints_to_try = ["/v1/journals", "/v1/journal", "/v1/accounting-entries", "/v1/journal-entries"]
                
                response = None
                for endpoint in endpoints_to_try:
                    try:
                        response = self._make_request(endpoint, params)
                        break  # Si funciona, salir del loop
                    except Exception as e:
                        if "404" in str(e) and endpoint != endpoints_to_try[-1]:
                            self._logger.debug(f"Endpoint {endpoint} no disponible, probando siguiente...")
                            continue  # Probar siguiente endpoint
                        elif endpoint == endpoints_to_try[-1]:
                            # Es el último endpoint, registrar error pero continuar con datos parciales
                            self._logger.warning(f"Ningún endpoint de asientos contables disponible: {str(e)}")
                            return []  # Retornar lista vacía en lugar de fallar
                        else:
                            raise e  # Re-lanzar error si no es 404
                
                # Procesar respuesta
                if not response:
                    break
                    
                if "results" in response:
                    journal_entries = response["results"]
                elif isinstance(response, list):
                    journal_entries = response
                else:
                    break
                
                if not journal_entries:
                    break
                
                all_journal_entries.extend(journal_entries)
                
                if len(journal_entries) < page_size:
                    break
                    
                page += 1
                time.sleep(0.1)
            
            self._logger.info(f"Obtenidos {len(all_journal_entries)} asientos contables del período")
            return all_journal_entries
            
        except Exception as e:
            self._logger.error(f"Error obteniendo asientos contables: {str(e)}")
            raise
    
    def obtener_balance_prueba(self, fecha_corte: str) -> Dict[str, Any]:
        """
        Obtener balance de prueba desde la API de Siigo.
        
        Args:
            fecha_corte: Fecha de corte en formato YYYY-MM-DD
            
        Returns:
            Balance de prueba con todas las cuentas y saldos
        """
        self._logger.info(f"Obteniendo balance de prueba para fecha {fecha_corte}")
        
        try:
            params = {
                "date": fecha_corte
            }
            
            response = self._make_request("/v1/trial-balance", params)
            
            # Validar estructura de respuesta
            if not isinstance(response, dict):
                raise Exception("Estructura de respuesta inválida para balance de prueba")
            
            # Asegurar que tenga la estructura esperada
            if "accounts" not in response:
                self._logger.warning("Balance de prueba sin cuentas, creando estructura básica")
                response = {
                    "date": fecha_corte,
                    "accounts": response.get("results", []) if "results" in response else [],
                    "total_debits": 0,
                    "total_credits": 0
                }
            
            self._logger.info(f"Balance de prueba obtenido con {len(response.get('accounts', []))} cuentas")
            return response
            
        except Exception as e:
            self._logger.error(f"Error obteniendo balance de prueba: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """
        Probar conexión con la API de Siigo.
        
        Returns:
            True si la conexión es exitosa
        """
        try:
            self._logger.info("Probando conexión con API de Siigo")
            
            # Intentar obtener información básica
            response = self._make_request("/v1/users/current-user")
            
            if response:
                self._logger.info("Conexión con API de Siigo exitosa")
                return True
            else:
                self._logger.error("Respuesta vacía de API de Siigo")
                return False
                
        except Exception as e:
            self._logger.error(f"Error probando conexión con API de Siigo: {str(e)}")
            return False
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Obtener información de la API y límites de rate.
        
        Returns:
            Información de la API
        """
        return {
            "base_url": self._base_url,
            "timeout": self._timeout,
            "authenticated": self._auth_token is not None,
            "endpoints_supported": [
                "/v1/invoices",
                "/v1/credit-notes", 
                "/v1/purchases",
                "/v1/journal-entries",
                "/v1/trial-balance"
            ]
        }