from google.oauth2 import id_token
from google.auth.transport import requests
import datetime

def validate_body_request_data(request_body, list_keys):
    """ Checks if a body request dictionary contains all the
        required keys.

        @type request_body: dictionary
        @param request_body: Recieved body.
        @type list_keys: list
        @param list_keys: List of the keys that the dictionary must have.
        @return: True if all the keys exist, False in another case.

        @todo: Return a dictionary with the missing keys.
    """

    for key in list_keys:
        if key not in request_body.keys():
            return False

    return True


def validate_google_id_token(token_id, GOOGLE_CLIENT_ID):
    """ Checks if a recieved Google id token is valid.

    @type token_id: str
    @param token_id: Recieved Google id token from a request.
    @type GOOGLE_CLIENT_ID: str
    @param GOOGLE_CLIENT_ID: The specific GOOGLE_CLIENT_ID for the application.
    @return True if the Google id_token is valid, Flase in any other case.
    """

    try:
        id_info = id_token.verify_oauth2_token(token_id, requests.Request(), GOOGLE_CLIENT_ID)

        if not id_info['aud'] == GOOGLE_CLIENT_ID:
            return False, id_info
        
        if not (id_info['iss'] == 'accounts.google.com' or id_info['iss'] == 'https://accounts.google.com'):
            return False, id_info
        
        if datetime.date.today() < datetime.datetime.fromtimestamp(id_info['exp']).date():
            return False, id_info
        
        return True, id_info

    except ValueError:
        return False, None
