from flask import Blueprint, request
from flask.helpers import make_response
from bson.objectid import ObjectId

from src.utils.validation_utils import validate_body_request_data
from src.utils.database_utils import insert_one_document

def build_moral_persons_blueprint(mongo_client, database, SECRET_KEY):

    moral_persons_bp = Blueprint('moral_persons_bp', __name__)

    moral_persons_collection = database.moral_persons

    @moral_persons_bp.route('/moral_persons', methods=['POST'])
    def register_moral_person():
        
        neccesary_data = [
            "RFC", "business_name", "street", "external_number", "internal_number", "suburb",
            "postal_code", "town", "email", "password", "password_reafirmation"
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
                "email" : request.json["email"],
                "password" : request.json["password"]
            }

            insert_one_document(new_moral_person, moral_persons_collection)
            new_moral_person.pop("password")

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
            moral_person_info.pop('password')
            resulting_response = make_response((
                moral_person_info,
                200,
                {'Access-Control-Allow-Origin': '*', 'mimetype':'application/json'}
            ))

        return resulting_response

    return moral_persons_bp
