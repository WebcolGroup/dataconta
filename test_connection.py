#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión con Siigo API
"""

import os
import requests
from dotenv import load_dotenv

def test_siigo_connection():
    """Probar la conexión con Siigo API"""
    load_dotenv()
    
    # Obtener credenciales
    api_url = os.getenv('SIIGO_API_URL', 'https://api.siigo.com')
    access_key = os.getenv('SIIGO_ACCESS_KEY')
    partner_id = os.getenv('PARTNER_ID', 'SandboxSiigoAPI')
    user = os.getenv('SIIGO_USER')
    
    print("=== TEST CONEXIÓN SIIGO API ===")
    print(f"API URL: {api_url}")
    print(f"Usuario: {user}")
    print(f"Access Key: {access_key[:20]}..." if access_key else "No encontrado")
    print(f"Partner ID: {partner_id}")
    print()
    
    if not access_key or not user:
        print("❌ ERROR: Credenciales no encontradas en .env")
        return False
    
    try:
        # Headers para autenticación
        auth_headers = {
            'Content-Type': 'application/json',
            'Partner-Id': partner_id
        }
        
        # Payload para obtener token
        auth_payload = {
            'username': user,
            'access_key': access_key
        }
        
        auth_url = f"{api_url}/auth"
        print(f"🔗 Enviando POST a: {auth_url}")
        print(f"📋 Headers: {auth_headers}")
        print(f"📄 Payload: {{'username': '{user}', 'access_key': '[OCULTO]'}}")
        print()
        
        # Realizar autenticación
        response = requests.post(
            auth_url, 
            json=auth_payload, 
            headers=auth_headers, 
            timeout=15
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            auth_data = response.json()
            print(f"✅ Respuesta exitosa: {auth_data}")
            
            access_token = auth_data.get('access_token')
            if access_token:
                print(f"🔑 Token obtenido: {access_token[:50]}...")
                return True
            else:
                print("❌ No se recibió access_token en la respuesta")
                return False
        else:
            print(f"❌ Error en autenticación:")
            print(f"   Status: {response.status_code}")
            print(f"   Texto: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Excepción durante la autenticación: {e}")
        return False

if __name__ == "__main__":
    test_siigo_connection()