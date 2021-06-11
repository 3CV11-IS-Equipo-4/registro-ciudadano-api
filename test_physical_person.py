import unittest
from setuptools import setup, find_packages
from app import app, database
from ast import literal_eval
from json import dumps, loads
import data_test

class PhysicalPersonTest(unittest.TestCase):
    
    @classmethod
    def tearDownClass(cls):
        
        pp_collection = database.physical_persons
        pp_collection.delete_many({})

        print("Pruebas completadas")


    def test_prueba(self):
        tester = app.test_client(self)
        response = tester.get('/prueba')
        status_code = response.status_code
        filtrado = loads(response.data)
        self.assertEqual(status_code, 200)
        self.assertEqual(filtrado, {'valor' : True, 'perrito' : 'Sí'})

    def test_register_physical_person(self):

        tester = app.test_client(self)

        # Registro inválido. Falta CURP y/o RFC.
        response = tester.post('/physical_persons', 
                                data=dumps(data_test.pp_register_1),
                                content_type='application/json'
                            )
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(response.data)
        print(response.status_code)
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')                            
        self.assertEqual(response.status_code, 400)
        self.assertTrue(b'error' in response.data)

        # Registro válido.
        response = tester.post('/physical_persons', 
                                data=dumps(data_test.pp_register_2),
                                content_type='application/json'
                            )
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(response.data)
        print(response.status_code)
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        self.assertEqual(response.status_code, 201)

        # Registro con CURP repetido.
        response = tester.post('/physical_persons', 
                                data=dumps(data_test.pp_register_3),
                                content_type='application/json'
                            )
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(response.data)
        print(response.status_code)
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')                            
        self.assertEqual(response.status_code, 400) 

        # Registro con Google ID token repetido.
        response = tester.post('/physical_persons', 
                                data=dumps(data_test.pp_register_4),
                                content_type='application/json'
                            )
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print(response.data)
        print(response.status_code)
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++')                            
        self.assertEqual(response.status_code, 400)               


if __name__ == "__main__":
    unittest.main()