from fastapi import APIRouter, Depends, Response
from fastapi_csrf_protect import CsrfProtect
from app.utils import generate_csrf, load_env_variables    # Asegúrate de importar tu función desde utils.py
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_env_variables()

# Ahora carga la secret_key desde las variables de entorno
secret_key = os.getenv('SECRET_KEY')

# Asegúrate de que la clave secreta esté disponible
if not secret_key:
    raise ValueError("SECRET_KEY no está configurado en el archivo .env")

# Crear un enrutador específico para las rutas CSRF
router = APIRouter()

@router.get("/csrftoken")
def get_csrf_token(response: Response, csrf_protect: CsrfProtect = Depends()):
    csrf_token = generate_csrf(secret_key)
    print(f"Token CSRF generado: {csrf_token}")
    response.set_cookie(
        key="fastapi-csrf-token", 
        value=csrf_token, 
        httponly=True, 
        secure=True,  # Cambia a True en producción
        samesite='None'  # Cambia a 'None' si necesitas enviar cookies a través de diferentes sitios
    )
    return {"csrf_token": csrf_token}

