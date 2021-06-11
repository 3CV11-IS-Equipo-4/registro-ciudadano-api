from flask.helpers import make_response
from flask import Blueprint, request, render_template
from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument
from src.utils.validation_utils import validate_google_id_token
from src.physical_persons.auth_pp import decode_auth_token_physical_person, encode_auth_token_physical_person, validate_authorization


from src.utils.validation_utils import validate_body_request_data
from src.utils.database_utils import insert_one_document

def build_physical_persons_blueprint(mongo_client, database, SECRET_KEY, GOOGLE_CLIENT_ID):

    physical_persons_bp = Blueprint('physical_persons_bp', __name__)

    physical_persons_table = database.physical_persons
    moral_persons_table = database.moral_persons

    @physical_persons_bp.route('/prueba', methods=['GET'])
    def prueba():

        return make_response(({'valor' : True, 'perrito' : 'Sí'}, 200, {
                'Access-Control-Allow-Origin': '*', 
                'mimetype':'application/json'
                }))

    @physical_persons_bp.route('/physical_persons/login_google', methods=['POST'])
    def login_physical_person():
        
        if 'google_id_token' not in request.json.keys():
            return make_response({"authentication": False}, 400, {
                'Access-Control-Allow-Origin': '*', 
                'mimetype':'application/json'
                })

        is_authenticated, id_info = validate_google_id_token(request.json['google_id_token'], GOOGLE_CLIENT_ID)

        if not is_authenticated :
            return make_response({"authentication": False}, 400, {
                'Access-Control-Allow-Origin': '*', 
                'mimetype':'application/json'
                })

        found_physical_person = physical_persons_table.find_one({'google_email' : id_info['email']})

        if found_physical_person is None:
            return make_response({"authentication": False}, 400, {
                'Access-Control-Allow-Origin': '*', 
                'mimetype':'application/json'
                })

        moral_persons_associated = []

        moral_persons_admin_by_pp = moral_persons_table.find({'admins' : {'$elemMatch' : {'_id' : str(found_physical_person['_id']) }}})
        for admin in moral_persons_admin_by_pp:
            moral_persons_associated.append({
                                            '_id' : str(admin['_id']), 'RFC' : admin['RFC'], 
                                            'business_name' : admin['business_name'], 'is_admin' : True
                                            })

        moral_persons_repre_by_pp = moral_persons_table.find({'representatives' : {'$elemMatch' : {'_id' : str(found_physical_person['_id']) }}})
        for r in moral_persons_repre_by_pp:
            moral_persons_associated.append({
                                            '_id' : str(r['_id']), 'RFC' : r['RFC'], 
                                            'business_name' : r['business_name'], 'is_admin' : False
                                            })

        generated_token = encode_auth_token_physical_person(
            id_info['email'],
            found_physical_person['names'],
            found_physical_person['first_surname'],
            found_physical_person['_id'],
            moral_persons_associated,
            SECRET_KEY
        )

        if generated_token is None:
            return make_response({"authentication": False}, 400, {
                'Access-Control-Allow-Origin': '*', 
                'mimetype':'application/json'
                })

        return make_response(({"authentication": True, "key_pp" : generated_token}, 200, {
            'Access-Control-Allow-Origin': '*', 
            'mimetype':'application/json'}))        

    @physical_persons_bp.route('/physical_persons', methods=['POST'])
    def register_physical_person():

        neccesary_data = [
            'CURP', 'RFC', 'names', 'first_surname', 'second_surname', 'birth_date',
            'street', 'external_number', 'internal_number', 'suburb', 'postal_code',
            'town', 'google_id_token']
        is_data_complete = validate_body_request_data(request.json, neccesary_data)

        if is_data_complete:
            
            # Check if RFC and CURP aren't empty.
            if request.json['CURP'] == '' and request.json['RFC'] == '':
                resulting_response = make_response((
                    {"error" : "CURP and RFC cannot be empty"},
                    400,
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
                return resulting_response                

            # Check if RFC, CURP or google_email is already registered.
            physical_person_already_registered = []

            is_authenticated, id_info = validate_google_id_token(request.json['google_id_token'], GOOGLE_CLIENT_ID)

            if not is_authenticated :
                resulting_response = make_response((
                    {"error" : "Invalid Google Account"},
                    400,
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
                return resulting_response
            

            if request.json["CURP"] != "":
                physical_person_curp = physical_persons_table.find_one({"CURP" : request.json["CURP"]})
                if physical_person_curp is not None:
                    physical_person_already_registered.append('CURP')
            
            if request.json["RFC"] != "":
                physical_person_rfc = physical_persons_table.find_one({"RFC" : request.json["RFC"]})
                if physical_person_rfc is not None:
                    physical_person_already_registered.append("RFC")

            physical_person_email = physical_persons_table.find_one({"google_email" : id_info["email"]})
            if physical_person_email is not None:
                physical_person_already_registered.append("google_email")

            if len(physical_person_already_registered) != 0:
                resulting_response = make_response(
                    {"error" : "There is a physical person already with that information.",
                    "duplicated_data" : physical_person_already_registered},
                    400,
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                )
                return resulting_response
            
            new_physical_person = {
                "CURP" : request.json["CURP"],
                "RFC" : request.json["RFC"],
                "names" : request.json["names"],
                "first_surname" : request.json["first_surname"],
                "second_surname" : request.json["second_surname"],
                "birth_date" : request.json["birth_date"],
                "addresses" : [
                    {
                        "street" : request.json["street"],
                        "extenal_number" : request.json["external_number"],
                        "internal_number" : request.json["internal_number"],
                        "suburb" : request.json["suburb"],
                        "postal_code" : request.json["postal_code"],
                        "town" : request.json["town"]    
                    }
                ],
                "actual_address" : 0,
                "google_email" : id_info["email"]

            }

            insert_one_document(new_physical_person, physical_persons_table)

            resulting_response = make_response((
                new_physical_person, 201, {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
            ))
            return resulting_response

        else:
            resulting_response = make_response((
                {"error" : "missing_data"},
                400,
                {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
            ))
            return resulting_response

    @physical_persons_bp.route('/physical_persons/<id>', methods=['GET'])
    def query_physical_person_information(id):

        authorization_header_validation = validate_authorization(request)
        if len(authorization_header_validation) != 0:
            return authorization_header_validation

        decoded_token = decode_auth_token_physical_person(request.headers["Authorization"].split()[1], SECRET_KEY)
        if decoded_token == -1:
            return make_response({'error' : 'Invalid information'}, 
                                 400, 
                                 {'Access-Control-Allow-Origin': '*', 
                                    'mimetype':'application/json'})
        elif decoded_token == -2:
            return make_response({'error' : 'Invalid information'}, 
                                 400, 
                                 {'Access-Control-Allow-Origin': '*', 
                                    'mimetype':'application/json'})

        else:          

            try:
                physical_person_info = physical_persons_table.find_one({'_id' : ObjectId(id)})
            except:
                resulting_response = make_response((
                    {'error' : 'Invalid information'}, 
                    400, 
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
                return resulting_response         

            
            if physical_person_info is None:
                resulting_response = make_response((
                    {'error' : 'Invalid information'}, 
                    400, 
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
            else:
                id_copy = physical_person_info['_id']
                physical_person_info.pop('_id')
                physical_person_info['_id'] = str(id_copy)
                resulting_response = make_response((
                    physical_person_info, 
                    200, 
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
            
            return resulting_response

    @physical_persons_bp.route('/physical_persons/<id>', methods=['PATCH'])
    def change_current_address(id):
        
        authorization_header_validation = validate_authorization(request)
        if len(authorization_header_validation) != 0:
            return authorization_header_validation

        decoded_token = decode_auth_token_physical_person(request.headers["Authorization"].split()[1], SECRET_KEY)
        if decoded_token == -1:
            return make_response({"error" : "Sesión expirada."}, 
                                 400, 
                                 {'Access-Control-Allow-Origin': '*', 
                                    'mimetype':'application/json'})
        elif decoded_token == -2:
            return make_response({"error" : "Ciudadano inválido"}, 
                                 400, 
                                 {'Access-Control-Allow-Origin': '*', 
                                    'mimetype':'application/json'})

        else:        

            if 'is_new_direction' not in request.json.keys():
                resulting_response = make_response((
                    {'error' : 'Missing information'}, 
                    400, 
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
                return resulting_response
            
            if request.json['is_new_direction']:
                # Crear nueva dirección.

                neccesary_data = ["street", "external_number", "internal_number", "suburb", "postal_code","town"]
                is_data_complete = validate_body_request_data(request.json, neccesary_data)
                if is_data_complete:
                    # Información necesaria completa.

                    previous_information = physical_persons_table.find_one({'_id' : ObjectId(id)})
                    last_address_id = len(previous_information['addresses'])

                    new_address = {
                        'street' : request.json['street'],
                        'external_number' : request.json['external_number'],
                        'internal_number' : request.json['internal_number'],
                        'suburb' : request.json['suburb'],
                        'postal_code' : request.json['postal_code'],
                        'town' : request.json['town'],
                    }

                    new_physical_person_information = physical_persons_table.find_one_and_update(
                        {'_id' : ObjectId(id)},
                        {'$set' : {"actual_address" : last_address_id}, '$push' : {'addresses' : new_address}},
                        return_document = ReturnDocument.AFTER
                    )

                    new_physical_person_information.pop('_id')
                    new_physical_person_information['_id'] = str(id)                

                    resulting_response = make_response((
                        new_physical_person_information,
                        200,
                        {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                    ))
                    return resulting_response

                else:
                    resulting_response = make_response((
                        {'error' : 'Missing information'}, 
                        400, 
                        {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                    ))
                    return resulting_response
            else:
                if 'previous_new_direction' not in request.json.keys():
                    resulting_response = make_response((
                        {'error' : 'Missing information'}, 
                        400, 
                        {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                    ))
                    return resulting_response
                
                try:
                    physical_person_info = physical_persons_table.find_one({'_id' : ObjectId(id)})
                except:
                    resulting_response = make_response((
                        {'error' : 'Invalid information'}, 
                        400, 
                        {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                    ))
                    return resulting_response

                if physical_person_info is None:
                    resulting_response = make_response((
                        {'error' : 'Invalid information'}, 
                        400, 
                        {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                    ))
                    return resulting_response                    
                
                number_addresses = len(physical_person_info['addresses'])           

                if request.json['previous_new_direction'] < 0 or request.json['previous_new_direction'] >= number_addresses:
                    resulting_response = make_response((
                        {'error' : 'Incorrect information'}, 
                        400, 
                        {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                    ))
                    return resulting_response
                
                new_physical_person_information = physical_persons_table.find_one_and_update(
                    {"_id" : ObjectId(id)},
                    {"$set" : {'actual_address' : request.json['previous_new_direction']}},
                    return_document=ReturnDocument.AFTER
                )

                new_physical_person_information.pop('_id')
                new_physical_person_information['_id'] = str(id)

                resulting_response = make_response((
                    new_physical_person_information,
                    200,
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
                return resulting_response

    return physical_persons_bp
