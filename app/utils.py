import json
import aiohttp
import os
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer


def load_env_variables():
    """
    Carga las variables de entorno necesarias dependiendo del entorno de ejecución.
    """
    env = os.getenv('ENV', 'production')

    if env == 'local':
        # Cargar variables desde el archivo .env si estamos en un entorno local
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)

# Cargar variables de entorno
load_env_variables()



def generate_csrf(secret_key):
    # Usar URLSafeTimedSerializer para generar el token CSRF
    serializer = URLSafeTimedSerializer(secret_key)
    csrf_token = serializer.dumps('csrf_token')
    return csrf_token

def getCreds():
    """Get creds required for use in the applications"""

    creds = dict()
    creds['access_token'] = os.getenv('FB_ACCESS_TOKEN')
    creds['client_id'] = os.getenv('FB_CLIENT_ID')
    creds['client_secret'] = os.getenv('FB_CLIENT_SECRET')
    creds['graph_domain'] = 'https://graph.facebook.com/' # base domain for api calls
    creds['graph_version'] = 'v20.0' # version of the api we are hitting
    creds['endpoint_base'] = creds['graph_domain'] + creds['graph_version'] # base endpoint with domain and version
    creds['debug'] = 'no' # debug mode for api call
    # Validar que las credenciales han sido correctamente cargadas
    if not creds['access_token']:
        raise ValueError("FB_ACCESS_TOKEN no está configurado")
    if not creds['client_id']:
        raise ValueError("FB_CLIENT_ID no está configurado")
    if not creds['client_secret']:
        raise ValueError("FB_CLIENT_SECRET no está configurado")
    
    return creds

def displayApiCallData( response ) :
	""" Print out to cli response from api call """

	print("\nURL: ") # title
	print(response['url']) # display url hit
	print("\nEndpoint Params: ") # title
	print(response['endpoint_params_pretty']) # display params passed to the endpoint
	print("\nResponse: ") # title
	print(response['json_data_pretty']) # make look pretty for cli
	
async def makeApiCall(url, endpointParams, debug='no'):
    """ Request data from endpoint with params
    
    Args:
        url: string of the url endpoint to make request from
        endpointParams: dictionary keyed by the names of the url parameters

    Returns:
        object: data from the endpoint
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=endpointParams) as response:
            data = await response.json()  # Parse JSON response directly

            response_data = {
                'url': url,
                'endpoint_params': endpointParams,
                'endpoint_params_pretty': json.dumps(endpointParams, indent=4),
                'json_data': data,
                'json_data_pretty': json.dumps(data, indent=4)
            }

            if debug == 'yes':
                displayApiCallData(response_data)

            return response_data

def debugAccessToken(params):
  """ GET info on an access token
  API Endpoint https://graph.facebook.com/debug_token?input_token={INPUT_TOKEN}&access_token={APP_ACCESS_TOKEN}
  Returns:
    JSON object: data from the endpoint
  """

  endpointParams = dict()
  endpointParams['input_token'] = params['access_token']
  endpointParams['access_token'] = params['access_token']

  url = params['graph_domain']+'/debug_token'
  

  return makeApiCall( url, endpointParams, params['debug'] )

def getLongLivedAccessToken( params ) :
	""" Get long lived access token
	
	API Endpoint:
		https://graph.facebook.com/{graph-api-version}/oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={your-access-token}

	Returns:
		object: data from the endpoint

	"""

	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['grant_type'] = 'fb_exchange_token' # tell facebook we want to exchange token
	endpointParams['client_id'] = params['client_id'] # client id from facebook app
	endpointParams['client_secret'] = params['client_secret'] # client secret from facebook app
	endpointParams['fb_exchange_token'] = params['access_token'] # access token to get exchange for a long lived token

	url = params['endpoint_base'] + '/oauth/access_token' # endpoint url

	return makeApiCall( url, endpointParams, params['debug'] ) # make the api call