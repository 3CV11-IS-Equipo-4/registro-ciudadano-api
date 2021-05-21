from flask.helpers import make_response
from flask import Blueprint, request
from bson.objectid import ObjectId

from src.utils.validation_utils import validate_body_request_data
from src.utils.database_utils import insert_one_document

def build_physical_persons_blueprint(mongo_client, database, SECRET_KEY):

    physical_persons_bp = Blueprint('physical_persons_bp', __name__)

    physical_persons_table = database.physical_persons

    @physical_persons_bp.route('/physical_persons', methods=['POST'])
    def register_physical_person():

        neccesary_data = [
            "CURP", "RFC", "names", "first_surname", "second_surname", "birth_date",
            "street", "external_number", "internal_number", "suburb", "postal_code",
            "town", "google_email"]
        is_data_complete = validate_body_request_data(request.json, neccesary_data)

        if is_data_complete:
            
            # Check if RFC, CURP or google_email is already registered.
            physical_person_already_registered = []

            if request.json["CURP"] != "":
                physical_person_curp = physical_persons_table.find_one({"CURP" : request.json["CURP"]})
                if physical_person_curp is not None:
                    physical_person_already_registered.append('CURP')
            
            if request.json["RFC"] != "":
                physical_person_rfc = physical_persons_table.find_one({"RFC" : request.json["RFC"]})
                if physical_person_rfc is not None:
                    physical_person_already_registered.append("RFC")

            if request.json["google_email"] != "":
                physical_person_email = physical_persons_table.find_one({"google_email" : request.json["google_email"]})
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
                        "id" : 1,
                        "street" : request.json["street"],
                        "extenal_number" : request.json["external_number"],
                        "internal_number" : request.json["internal_number"],
                        "suburb" : request.json["suburb"],
                        "postal_code" : request.json["postal_code"],
                        "town" : request.json["town"]    
                    }
                ],
                "actual_address" : 0,
                "google_email" : request.json["google_email"]
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

        physical_person_info = physical_persons_table.find_one({'_id' : ObjectId(id)})
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

    return physical_persons_bp
