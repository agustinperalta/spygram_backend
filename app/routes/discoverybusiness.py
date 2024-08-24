from datetime import datetime
from fastapi_csrf_protect import CsrfProtect
from app.utils import makeApiCall, getCreds, load_env_variables
from fastapi import APIRouter, HTTPException, Query,Depends,Request
from typing import List, Optional
from app.models import DiscoveryAccountRequest
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_env_variables()

# Ahora carga la secret_key desde las variables de entorno
secret_key = os.getenv('SECRET_KEY')

# Asegúrate de que la clave secreta esté disponible
if not secret_key:
    raise ValueError("SECRET_KEY no está configurado en el archivo .env")

router = APIRouter()

async def find_last_page(params):
    """
    Find the last page of media posts for an Instagram business account since a given date.
    """
    after = None
    endpointParams = {
        'access_token': params['access_token'],
        'fields': f'business_discovery.username({params["user_name"]}){{followers_count,media{{id,timestamp}}}}'
    }
    url = f"{params['endpoint_base']}/{params['instagram_business_account']}"
    response = await makeApiCall(url, endpointParams, params.get('debug', 'yes'))

     # Manejo de errores
    if 'error' in response['json_data']:
        error_message = response['json_data']['error'].get('error_user_msg', 'An unexpected error occurred.')
        raise HTTPException(status_code=400, detail=error_message)

    # Convert since_date to date if it's a datetime
    since_date = params['since_date']
    if isinstance(since_date, datetime):
        since_date = since_date.date()

    print(response)
    while True:
        media_data = response['json_data']['business_discovery']['media']['data']
        last_post_date = datetime.strptime(media_data[-1]['timestamp'], '%Y-%m-%dT%H:%M:%S%z').date()

        if last_post_date < since_date  or 'after' not in response['json_data']['business_discovery']['media']['paging']['cursors']:
            break

        after = response['json_data']['business_discovery']['media']['paging']['cursors']['after']
        endpointParams['fields'] = f'business_discovery.username({params["user_name"]}){{followers_count,media.after({after}){{timestamp}}}}'
        response = await makeApiCall(url, endpointParams, params.get('debug', 'no'))

    return after

async def get_competition_data(params):
    """
    Get Competition Data from https://graph.facebook.com/{graph-api-version}/{instagram_business_account}?access_token={your-access-token}&fields=business_discovery.username({user_name}){{account_metrics},media{{media_metrics}}
    Returns:
        JSON object: data from the endpoint
    """
    all_data = []  # To accumulate data from all pages

    # Obtain the last page cursor using find_last_page
    after = await find_last_page(params)
    before = None
    # Convert since_date to date if it's a datetime
    since_date = params['since_date']
    if isinstance(since_date, datetime):
        since_date = since_date.date()
    while True:
        endpointParams = dict()
        endpointParams['access_token'] = params['access_token']
        user_name = params['user_name']
        account_metrics = ','.join(params['account_metrics'])
        media_metrics = ','.join(params['media_metrics'])

        if before:
            endpointParams['fields'] = f'business_discovery.username({user_name}){{{account_metrics},media.before({before}){{{media_metrics}}}}}'
        elif after == None:
            endpointParams['fields'] = f'business_discovery.username({user_name}){{{account_metrics},media{{{media_metrics}}}}}'
        else:
            endpointParams['fields'] = f'business_discovery.username({user_name}){{{account_metrics},media.after({after}){{{media_metrics}}}}}'

        url = params['endpoint_base'] + '/' + params['instagram_business_account']
        response = await makeApiCall(url, endpointParams, params.get('debug', 'no'))
        
        # Manejo de errores
        if 'error' in response['json_data']:
            error_message = response['json_data']['error'].get('error_user_msg', 'An unexpected error occurred.')
            raise HTTPException(status_code=400, detail=error_message)


        business_discovery = response['json_data']['business_discovery']
        media_data = [
            media for media in business_discovery['media']['data']
            if datetime.strptime(media['timestamp'], '%Y-%m-%dT%H:%M:%S%z').date() >= since_date
        ]
        # If all_data is empty, add the initial data structure
        if not all_data:
            all_data.append({
                "followers_count": business_discovery.get("followers_count"),
                "biography": business_discovery.get("biography"),
                "media_count": business_discovery.get("media_count"),
                "media": media_data
            })
        else:
            # Append only media data in subsequent iterations
            all_data[0]['media'].extend(media_data)

        if 'before' not in business_discovery['media']['paging']['cursors']:
            break

        before = business_discovery['media']['paging']['cursors']['before']

    return all_data[0]

def setMetrics(account_metrics: list, media_metrics: list):
    # Default values for account_metrics and media_metrics
    default_account_metrics = ["id", "followers_count", "biography", "website", "media_count"]
    default_media_metrics = ["comments_count", "like_count", "media_url", "media_product_type", "media_type", "owner", "permalink", "timestamp", "username", "caption"]

    # Use provided values or defaults if not provided
    if account_metrics is None or len(account_metrics) == 0:
        account_metrics = default_account_metrics
    if media_metrics is None or len(media_metrics) == 0:
        media_metrics = default_media_metrics

    return account_metrics, media_metrics

async def getDiscoveryAccount(params, user_name, since_date, account_metrics=None, media_metrics=None):
    params['account_metrics'], params['media_metrics'] = setMetrics(account_metrics, media_metrics)
    params['debug'] = 'no'
    # Convert since_date to date if it's a datetime
    if isinstance(since_date, datetime):
        since_date = since_date.date()
    params['since_date'] = since_date
    params['user_name'] = user_name
    params['instagram_business_account'] = '17841401977170277'

    discovery_response = await get_competition_data(params)

    return discovery_response

@router.get("/discoveryaccount/")
async def discovery_account(
    user_name: str,
    fecha_desde: str,
    request: Request,
    account_metrics: Optional[List[str]] = Query(None),
    media_metrics: Optional[List[str]] = Query(None),
    csrf_protect: CsrfProtect = Depends(),
):
    # Verifica si el encabezado 'X-CSRF-Token' está presente en la solicitud
    if 'X-CSRF-Token' not in request.headers:
        raise HTTPException(status_code=400, detail="Missing CSRF token in headers")
    # Obtener el token CSRF desde los encabezados de la solicitud
    csrf_token = csrf_protect.get_csrf_from_headers(request.headers)
    print(f"Token CSRF recibido desde el frontend: {csrf_token}")

    # Crear un objeto URLSafeTimedSerializer para validar el token
    serializer = URLSafeTimedSerializer(secret_key)

    try:
        # Validar el token CSRF
        serializer.loads(csrf_token, max_age=60)
    except (BadSignature, SignatureExpired) as e:
        raise HTTPException(status_code=403, detail="CSRF token invalid or expired")
    
    params = getCreds()
    try:
        fecha_desde_validada = DiscoveryAccountRequest.validate_fecha_desde(fecha_desde)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        discovery_response = await getDiscoveryAccount(
            params, user_name, fecha_desde_validada, account_metrics, media_metrics
        )
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    return {"discovery_response": discovery_response}