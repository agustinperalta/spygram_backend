import requests
import json
from datetime import datetime
import aiohttp

def getCreds() :
	""" Get creds required for use in the applications
	
	Returns:
		dictonary: credentials needed globally

	"""

	creds = dict() # dictionary to hold everything
	creds['access_token'] = 'EAAOWmxWj5uABO1wwUn1lEskJZBWrRRHKebCDtG0BP6mbjHBR15MLXrDzwZBergdaWyRrDphksibcDVUHhZAxYqk7BfKxbZAEfiiKuYy1Mdvzu7ZA73sdSxhCMenDpQSpMl8TGsfbAHvZCRKKiqWOtWiKX6562xtd5WJgvvBpSyXQM20kyltNO0mgZDZD' # access token for use with all api calls
	creds['client_id'] = '1010017757292256' # client id from facebook app IG Graph API Test
	creds['client_secret'] = 'dfaeca94739282661dc064c8bd353f56' # client secret from facebook app
	creds['graph_domain'] = 'https://graph.facebook.com/' # base domain for api calls
	creds['graph_version'] = 'v20.0' # version of the api we are hitting
	creds['endpoint_base'] = creds['graph_domain'] + creds['graph_version'] # base endpoint with domain and version
	creds['debug'] = 'no' # debug mode for api call

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