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