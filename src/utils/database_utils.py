def insert_one_document(data_to_insert, collection):

    resulting_query = collection.insert_one(data_to_insert)
    data_to_insert.pop('_id')
    data_to_insert['_id'] = str(resulting_query.inserted_id)
