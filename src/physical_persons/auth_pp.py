import jwt
import datetime

def encode_auth_token_physical_person(email, names, first_surname, physical_person_id, SECRET_KEY):
    """ Generates auth token for a physical persons.

    @type email: str
    @param email: email associated with the physical person
    @type names: str
    @param: names of the physical person
    @type first_surname: str
    @param first surname: of the physical person
    @param physical_person_id: _id associated with the document in the Mongo database.
    @return Generated token, exception in any other case.

    """

    try:
        payload = {
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
            'iat' : datetime.datetime.utcnow(),
            'sub' : {
                'email' : email,
                'names' : names,
                'first_surname' : first_surname, 
                '_id': str(physical_person_id)
                }
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    except Exception as e:
        return None

def decode_auth_token_physical_person(auth_token, SECRET_KEY):
    """
    Decode the recivied token.
    """

    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return -1
    except jwt.InvalidTokenError:
        return -2    

def validate_authorization(request):
    """ Checks if the requests contains a valid authorization header with the specified format.

    """

    if 'Authorization' not in request.headers:
        return ({"error" : "Autorización inválida."}, 400, 
                        {'Access-Control-Allow-Origin': '*', 
                        'mimetype':'application/json'})
    else:
        contenido_authorization = request.headers["Authorization"].split()
        if len(contenido_authorization) != 2 or contenido_authorization[0] != "Bearer":
            return ({"error" : "Autorización inválida."}, 400, 
                                    {'Access-Control-Allow-Origin': '*', 
                                    'mimetype':'application/json'})
        else:
            return tuple()        
