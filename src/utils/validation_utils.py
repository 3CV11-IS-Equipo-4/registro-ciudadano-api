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

