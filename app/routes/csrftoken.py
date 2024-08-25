from fastapi import APIRouter, Depends, Response, Request,HTTPException
from fastapi_csrf_protect import CsrfProtect
from app.utils import generate_csrf, load_env_variables    # Asegúrate de importar tu función desde utils.py
from dotenv import load_dotenv
import os
import redis
from datetime import datetime, timedelta


# Cargar variables de entorno
load_env_variables()

redis_host = os.getenv('REDIS_HOST')
# Configura Redis
redis_client = redis.StrictRedis(host=redis_host, port=6379, db=0, decode_responses=True)
# Ahora carga la secret_key desde las variables de entorno
secret_key = os.getenv('SECRET_KEY')

# Asegúrate de que la clave secreta esté disponible
if not secret_key:
    raise ValueError("SECRET_KEY no está configurado en el archivo .env")

# Crear un enrutador específico para las rutas CSRF
router = APIRouter()


def rate_limit_exceeded(ip: str) -> bool:
    """
    Verifica si el límite de tasa ha sido excedido para una IP dada.
    """
    current_time = datetime.utcnow()
    key = f"rate_limit:{ip}"
    requests = redis_client.lrange(key, 0, -1)

    # Elimina solicitudes que están fuera del límite de tiempo de una hora
    valid_requests = [req for req in requests if datetime.strptime(req, '%Y-%m-%d %H:%M:%S.%f') > current_time - timedelta(hours=1)]

    if len(valid_requests) >= 10:
        return True
    else:
        # Solo actualiza Redis si hay un cambio
        if len(valid_requests) < len(requests):
            redis_client.delete(key)
            redis_client.rpush(key, *valid_requests)  # Reemplaza con solicitudes válidas
        return False

def increment_request_count(ip: str):
    """
    Incrementa el contador de solicitudes para una IP dada.
    """
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
    key = f"rate_limit:{ip}"
    redis_client.rpush(key, current_time)
    redis_client.expire(key, 3600)  # Establece la expiración a 1 hora

@router.get("/csrftoken")
def get_csrf_token(request: Request,response: Response, csrf_protect: CsrfProtect = Depends()):

    client_ip = request.client.host  # Obtiene la IP del cliente

    # Verifica si se ha excedido el límite de solicitudes
    if rate_limit_exceeded(client_ip):
        raise HTTPException(status_code=429, detail="Too many requests")

    # Incrementa el conteo de solicitudes
    increment_request_count(client_ip)

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

