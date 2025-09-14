"""
Siigo API adapter - Implementation of InvoiceRepository port.
"""

import json
import requests
from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
from urllib.parse import urljoin

from src.application.ports.interfaces import InvoiceRepository, APIClient, Logger
from src.domain.entities.invoice import (
    Invoice, InvoiceFilter, Customer, InvoiceItem, Payment, APICredentials
)


class SiigoAPIAdapter(InvoiceRepository, APIClient):
    """Adapter for Siigo API integration."""
    
    def __init__(self, logger: Logger):
        self._logger = logger
        self._session = requests.Session()
        self._auth_token: Optional[str] = None
        self._credentials: Optional[APICredentials] = None
        self._session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def authenticate(self, credentials: APICredentials) -> bool:
        """Authenticate with the Siigo API."""
        try:
            if not credentials.is_valid():
                self._logger.error("Invalid API credentials provided")
                return False
            
            self._credentials = credentials
            
            # Set Partner-Id header if provided
            if credentials.partner_id:
                self._session.headers['Partner-Id'] = credentials.partner_id
            
            auth_url = urljoin(credentials.api_url, '/auth')
            auth_data = {
                'username': credentials.username,
                'access_key': credentials.access_key
            }
            
            self._logger.info("Attempting authentication with Siigo API")
            
            auth_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            if credentials.partner_id:
                auth_headers['Partner-Id'] = credentials.partner_id
            
            response = requests.post(auth_url, json=auth_data, headers=auth_headers, timeout=30)
            
            if response.status_code == 200:
                auth_response = response.json()
                self._auth_token = auth_response.get('access_token')
                
                if self._auth_token:
                    self._session.headers['Authorization'] = f'Bearer {self._auth_token}'
                    self._logger.info("Authentication successful")
                    return True
                else:
                    self._logger.error("No access token received in response")
                    return False
            else:
                self._logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Authentication request failed: {e}")
            return False
        except Exception as e:
            self._logger.error(f"Unexpected error during authentication: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if API connection is active."""
        return self._auth_token is not None
    
    def get_invoices(self, filters: InvoiceFilter) -> List[Invoice]:
        """Retrieve invoices from Siigo API."""
        try:
            if not self._ensure_authenticated():
                raise Exception("Authentication failed")
            
            # Prepare query parameters
            params = filters.to_dict()
            params['type'] = 'FV'  # Factura de Venta
            
            # Make API request
            api_url = urljoin(self._credentials.api_url, '/v1/invoices')
            response = self._session.get(api_url, params=params, timeout=30)
            
            if response.status_code == 401:
                # Token expired, re-authenticate
                self._logger.warning("Token expired, re-authenticating")
                self._auth_token = None
                if self.authenticate(self._credentials):
                    response = self._session.get(api_url, params=params, timeout=30)
                else:
                    raise Exception("Re-authentication failed")
            
            if response.status_code == 200:
                data = response.json()
                invoices = self._parse_invoices(data.get('results', []))
                self._logger.info(f"Successfully retrieved {len(invoices)} invoices")
                return invoices
            else:
                self._logger.error(f"API request failed: {response.status_code} - {response.text}")
                raise Exception(f"API request failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Request failed: {e}")
            raise Exception(f"Network error: {e}")
        except Exception as e:
            self._logger.error(f"Error retrieving invoices: {e}")
            raise
    
    def get_invoices_raw(self, filters: InvoiceFilter) -> List[Dict[str, Any]]:
        """Get raw invoice data from API (implementation of APIClient)."""
        try:
            if not self._ensure_authenticated():
                raise Exception("Authentication failed")
            
            params = filters.to_dict()
            params['type'] = 'FV'
            
            api_url = urljoin(self._credentials.api_url, '/v1/invoices')
            response = self._session.get(api_url, params=params, timeout=30)
            
            if response.status_code == 401:
                self._logger.warning("Token expired, re-authenticating")
                self._auth_token = None
                if self.authenticate(self._credentials):
                    response = self._session.get(api_url, params=params, timeout=30)
                else:
                    raise Exception("Re-authentication failed")
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                raise Exception(f"API request failed: {response.status_code}")
                
        except Exception as e:
            self._logger.error(f"Error retrieving raw invoices: {e}")
            raise
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[Invoice]:
        """Get a specific invoice by ID."""
        try:
            if not self._ensure_authenticated():
                return None
            
            api_url = urljoin(self._credentials.api_url, f'/v1/invoices/{invoice_id}')
            response = self._session.get(api_url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                invoices = self._parse_invoices([data])
                return invoices[0] if invoices else None
            else:
                self._logger.error(f"Failed to get invoice {invoice_id}: {response.status_code}")
                return None
                
        except Exception as e:
            self._logger.error(f"Error getting invoice {invoice_id}: {e}")
            return None
    
    def _ensure_authenticated(self) -> bool:
        """Ensure we have valid authentication."""
        if not self._auth_token and self._credentials:
            return self.authenticate(self._credentials)
        return self._auth_token is not None
    
    def _parse_invoices(self, invoice_data: List[Dict[str, Any]]) -> List[Invoice]:
        """Parse API response data into Invoice entities."""
        invoices = []
        
        for data in invoice_data:
            try:
                # Parse customer
                customer_data = data.get('customer', {})
                customer = Customer(
                    identification=customer_data.get('identification', ''),
                    branch_office=customer_data.get('branch_office', 0),
                    check_digit=customer_data.get('check_digit'),
                    name=customer_data.get('name', []),
                    commercial_name=customer_data.get('commercial_name'),
                    address=customer_data.get('address'),
                    phones=customer_data.get('phones', []),
                    contacts=customer_data.get('contacts', [])
                )
                
                # Parse items
                items = []
                for item_data in data.get('items', []):
                    item = InvoiceItem(
                        code=item_data.get('code', ''),
                        description=item_data.get('description', ''),
                        quantity=Decimal(str(item_data.get('quantity', 0))),
                        price=Decimal(str(item_data.get('price', 0))),
                        discount=Decimal(str(item_data.get('discount', 0))),
                        taxes=item_data.get('taxes', [])
                    )
                    items.append(item)
                
                # Parse payments
                payments = []
                for payment_data in data.get('payments', []):
                    payment = Payment(
                        id=payment_data.get('id', 0),
                        value=Decimal(str(payment_data.get('value', 0))),
                        due_date=datetime.fromisoformat(payment_data.get('due_date', datetime.now().isoformat()))
                    )
                    payments.append(payment)
                
                # Create invoice
                invoice = Invoice(
                    id=str(data.get('id', '')),
                    document_id=str(data.get('document', {}).get('id', '')),
                    number=data.get('number', 0),
                    name=data.get('name', ''),
                    date=datetime.fromisoformat(data.get('date', datetime.now().isoformat())),
                    customer=customer,
                    items=items,
                    payments=payments,
                    cost_center=data.get('cost_center'),
                    seller=data.get('seller'),
                    observations=data.get('observations'),
                    additional_fields=data.get('additional_fields'),
                    total=Decimal(str(data.get('total', 0))) if data.get('total') else None
                )
                
                invoices.append(invoice)
                
            except Exception as e:
                self._logger.error(f"Error parsing invoice data: {e}")
                continue
        
        return invoices