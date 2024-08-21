import os
from app.utils import makeApiCall,getCreds
from fastapi import APIRouter, HTTPException



router = APIRouter()


def getAccounts( params ) :
  """
  Get All Account Data from https://graph.facebook.com/{graph-api-version}/me/accounts
  Returns:
    JSON object: data from the endpoint
  """
  endpointParams = dict()
  endpointParams['access_token'] = params['access_token']

  url = params['endpoint_base'] + '/me/accounts'
  return makeApiCall( url,endpointParams, params['debug'] )

def getInstagramAccounts( params ) :
  """
  Get All Instagram Accounts from https://graph.facebook.com/{graph-api-version}/{page_id}?access_token={your-access-token}&fields=instagram_business_account
  Returns:
    JSON object: data from the endpoint
  """
  endpointParams = dict()
  endpointParams['access_token'] = params['access_token']
  endpointParams['fields'] = 'instagram_business_account'

  url = params['endpoint_base'] + '/'+params['page_id']
  return makeApiCall( url,endpointParams, params['debug'] )

@router.get("/accounts/")
def read_accounts():
    params = getCreds()
    response = getAccounts(params)
    if 'data' not in response['json_data']:
        raise HTTPException(status_code=400, detail="Unable to fetch accounts")
    
    page_id = response['json_data']['data'][0]['id']
    os.environ['FB_PAGE_ID'] = page_id
    params['page_id'] = page_id
    instagram_response = getInstagramAccounts(params)
    
    if 'instagram_business_account' in instagram_response['json_data']:
        instagram_id = instagram_response['json_data']['instagram_business_account']['id']
        os.environ['INSTAGRAM_ACCOUNT_ID'] = instagram_id
    
    return {
        "facebook_accounts": response['json_data'],
        "instagram_accounts": instagram_response['json_data']
    }