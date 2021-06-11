from flask import Blueprint, request
from flask.helpers import make_response
from bson.objectid import ObjectId
from pymongo.collection import ReturnDocument
from src.physical_persons.auth_pp import validate_authorization, decode_auth_token_physical_person

from src.utils.validation_utils import validate_body_request_data
from src.utils.database_utils import insert_one_document

def build_moral_persons_blueprint(mongo_client, database, SECRET_KEY):

    moral_persons_bp = Blueprint('moral_persons_bp', __name__)

    moral_persons_collection = database.moral_persons
    physical_persons_collection = database.physical_persons

    @moral_persons_bp.route('/moral_persons', methods=['POST'])
    def register_moral_person():

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
        
            neccesary_data = [
                "RFC", "business_name", "street", "external_number", "internal_number", "suburb",
                "postal_code", "town"
            ]
            is_data_complete = validate_body_request_data(request.json, neccesary_data)

            if is_data_complete:

                # Checks if RFC is already registered.
                if request.json["RFC"] == '':
                    # RFC must be provided.
                    resulting_response = make_response(
                        {"error" : "RFC must be provided."},
                        400,
                        {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                    )
                    return resulting_response
                
                moral_person_rfc = moral_persons_collection.find_one({"RFC" : request.json["RFC"]})
                if moral_person_rfc is not None:
                    # There is a moral person already registered with the provided RFC.
                    resulting_response = make_response(
                        {"error" : "There is a moral person already with that information."},
                        400,
                        {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                    )
                    return resulting_response

                new_moral_person = {
                    "RFC" : request.json["RFC"],
                    "business_name" : request.json["business_name"],
                    "addresses" : [{
                        "street" : request.json["street"],
                        "external_number" : request.json["external_number"],
                        "internal_number" : request.json["internal_number"],
                        "suburb" : request.json["suburb"],
                        "postal_code" : request.json["postal_code"],
                        "town" : request.json["town"],
                    }],
                    "actual_address" : 0,
                    "admins" : [
                        {'_id' : decoded_token['_id']}
                    ],
                    'representatives' : []
                }

                insert_one_document(new_moral_person, moral_persons_collection)

                resulting_response = make_response((
                    new_moral_person, 201, {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
                return resulting_response
            else:
                resulting_response = make_response((
                    {"error" : "missing_data"},
                    400,
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
                return resulting_response            

    @moral_persons_bp.route('/moral_persons/<id>', methods=['GET'])
    def query_moral_person_information(id):

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

            moral_person_info = moral_persons_collection.find_one({'_id' : ObjectId(id)})
            if moral_person_info is None:
                resulting_response = make_response((
                    {'error' : 'Invalid information'}, 
                    400, 
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
            else:
                id_copy = moral_person_info['_id']
                moral_person_info.pop('_id')
                moral_person_info['_id'] = str(id_copy)
                resulting_response = make_response((
                    moral_person_info,
                    200,
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))

            return resulting_response

    @moral_persons_bp.route('/moral_persons/<id>', methods=['PATCH'])
    def change_curret_address(id):

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

            if 'is_new_direction' not in request.json.keys():
                resulting_response = make_response((
                    {'error' : 'Missing information'}, 
                    400, 
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
                return resulting_response

            previous_information = moral_persons_collection.find_one({'_id' : ObjectId(id)})

            if previous_information is None:
                resulting_response = make_response((
                    {'error' : 'Invalid informarion'}, 
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

                    last_address_id = len(previous_information['addresses'])

                    new_address = {
                        'street' : request.json['street'],
                        'external_number' : request.json['external_number'],
                        'internal_number' : request.json['internal_number'],
                        'suburb' : request.json['suburb'],
                        'postal_code' : request.json['postal_code'],
                        'town' : request.json['town'],
                    }

                    new_moral_person_information = moral_persons_collection.find_one_and_update(
                        {'_id' : ObjectId(id)},
                        {'$set' : {"actual_address" : last_address_id}, '$push' : {'addresses' : new_address}},
                        return_document = ReturnDocument.AFTER
                    )

                    new_moral_person_information.pop('_id')
                    new_moral_person_information['_id'] = str(id)                

                    resulting_response = make_response((
                        new_moral_person_information,
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
                
                moral_person_info = moral_persons_collection.find_one({'_id' : ObjectId(id)})
                number_addresses = len(moral_person_info['addresses'])           

                if request.json['previous_new_direction'] < 0 or request.json['previous_new_direction'] >= number_addresses:
                    resulting_response = make_response((
                        {'error' : 'Incorrect information'}, 
                        400, 
                        {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                    ))
                    return resulting_response
                
                new_moral_person_information = moral_persons_collection.find_one_and_update(
                    {"_id" : ObjectId(id)},
                    {"$set" : {'actual_address' : request.json['previous_new_direction']}},
                    return_document=ReturnDocument.AFTER
                )

                new_moral_person_information.pop('_id')
                new_moral_person_information['_id'] = str(id)

                resulting_response = make_response((
                    new_moral_person_information,
                    200,
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
                return resulting_response            

    @moral_persons_bp.route('/moral_persons/<id>/representatives', methods=['PATCH'])
    def add_representative(id):
        
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
            neccesary_data = [
                "RFC_physical_person", "CURP_physical_person"
            ]
            is_data_complete = validate_body_request_data(request.json, neccesary_data)

            if is_data_complete:

                new_representative = physical_persons_collection.find_one({'CURP' : request.json['CURP_physical_person'], 'RFC' : request.json['RFC_physical_person']})

                if new_representative is None:
                    return make_response({'error' : 'Invalid information'}, 
                                        400, 
                                        {'Access-Control-Allow-Origin': '*', 
                                            'mimetype':'application/json'})                   

                previous_information = moral_persons_collection.find_one({'_id' : ObjectId(id)})

                for representative in previous_information['representatives']:
                    if representative['_id'] == str(new_representative['_id']):
                        return make_response({'error' : 'Invalid information'}, 
                                            400, 
                                            {'Access-Control-Allow-Origin': '*', 
                                                'mimetype':'application/json'})

                new_moral_person_information = moral_persons_collection.find_one_and_update(
                    {'_id' : ObjectId(id)},
                    {'$push' : {'representatives' : {'_id' : str(new_representative['_id']), 'RFC' : new_representative['RFC'],  'CURP' : new_representative['CURP'] }}},
                    return_document = ReturnDocument.AFTER
                )

                new_moral_person_information.pop('_id')
                new_moral_person_information['_id'] = str(id)                

                resulting_response = make_response((
                    new_moral_person_information,
                    200,
                    {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
                ))
                return resulting_response           


    return moral_persons_bp
