
from pycloak import auth
import os

def get_session(params):
    """
    Attempts to create a session from the input parameters and environment, preferring offline token use to username password.  Uses the following order:
      - 'token' input parameter
      - KEYCLOAK_OFFLINE_TOKEN environment variable
      - 'username'/'password' input parameter

      If an auth session cannot be established with any of these, a pycloak.auth.AuthException is thrown.
    """
    if params['token'] is not None:
        return auth.AuthSession(offline_token=params['token'], host=params['host'], realm=params['auth_realm'], client_id=params['auth_client_id'])
    elif os.environ['KEYCLOAK_OFFLINE_TOKEN'] is not None:
        return auth.AuthSession(offline_token=os.environ['KEYCLOAK_OFFLINE_TOKEN'], host=params.get('host'), realm=params['auth_realm'], client_id=params['auth_client_id'])
    elif params['username'] is not None and params['password'] is not None:
        return auth.AuthSession(params['username'], params['password'], host=params.get('host'), realm=params['auth_realm'], client_id=params['auth_client_id'])
    else:
        # TODO throw descriptive exception
        return None
