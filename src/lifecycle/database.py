# database functions for the lifecycle management

from re import X
import pymongo
import datetime

from pymongo import MongoClient
from bson.objectid import ObjectId



class lifecycle_db:
    def __init__(self, localclient=None, username=None, password=None):
        if localclient:
            self.dbclient = pymongo.MongoClient(localclient)
        else:
            self.dbclient = pymongo.MongoClient("mongodb://localhost:27017/")

        if username:
            self.username = username
            self.password = password
            self.remote_ro = False


        else:
            self.username = 'readonly'
            self.password =  'modelpassword'
            self.remote_ro = True


    def get_username(self):
        return self.username

    def init_model_db(self):

        global local_data_collection
        global local_signature_collection
        global remote_data_collection
        global remote_signature_collection

        # if username no provided, create a readonly client
        mongodb_login = "mongodb+srv://{}:{}@cluster0.7ilyj.mongodb.net/test".format(self.username, self.password)


        dbclient_database   = self.dbclient["model_database"]
        self.local_data_collection         = dbclient_database["model_data"]
        self.local_signature_collection    = dbclient_database["signature"]

        # Make sure signatures are unique on both
        try:
            self.local_signature_collection.create_index(
                [("signature", pymongo.DESCENDING)],
                unique=True
            )
        except:
            print('cannot set unique local database')

        remote_client       = pymongo.MongoClient(mongodb_login)
        dbclient_database_r = remote_client["model_database"]
        self.remote_data_collection       = dbclient_database_r["model_data"]
        self.remote_signature_collection  = dbclient_database_r["signature"]
        
        try:
            # Only if there is a remote account, allow writing, otherwise read only
            self.remote_signature_collection.create_index(
                [("signature", pymongo.DESCENDING)],
                unique=True
            )
        except:
            no_db = True


    def write_model_db(self,
        signature,
        model_data,
        username = '',
        organisation = '',
        model_source='',
        parent = '',
        local=True):



        if local:
            print('writing to local repository')
            db_data = self.local_data_collection
            db_sig = self.local_signature_collection
        else:
            print('writing to remote repository')
            db_data = self.remote_data_collection
            db_sig = self.remote_signature_collection

        # Insert Signature to Database (signatures)
        if self.get_model(signature) == None:
            x = db_data.insert_one(model_data)
            model_id = x.inserted_id
            # print(model_id, 'for sig: ', signature)

            # Inset Model Data to Database (modeldata)
            signature_data =  {
                'signature': signature,
                'parent': parent,
                'username': username,
                'organisation':organisation,
                'model_source': model_source,
                'model_data': model_id
            }

            x = db_sig.insert_one(signature_data)
            signature_model_id = x.inserted_id
            return signature_model_id
        else:
            print('signature: ', signature, ' already in database')
            return None


    def push_model(self,model, local=True, parent=None,
        username='', organisation = '', model_source=''):

        signature, layer_data = self.create_model_data(model)

        self.write_model_db(
            signature=signature,
            model_data=layer_data,
            parent=parent,
            username=username,
            organisation=organisation,
            local=local,
            model_source=model_source
        )
        return signature



    def get_model(self,signature, local=True):
        print('looking for ', signature )
        
        if local:
            db_data = self.local_data_collection
            db_sig = self.local_signature_collection
        else:
            db_data = self.remote_data_collection
            db_sig = self.remote_signature_collection

        signature_data = db_sig.find_one({'signature': signature})
        
        if(signature_data):
            return signature_data
        else:
            return None


    # The web framework gets post_id from the URL and passes it as a string
    def get_model_data(self, model_id=None, signature=None, local=True):
        if local:
            db_data = self.local_data_collection
        else:
            db_data = self.remote_data_collection

        if signature:
            model_object = self.get_model(signature=signature, local=local)['model_data']
            document = db_data.find_one({'_id': model_object})
            return document
        else:
            document = db_data.find_one({'_id': ObjectId(model_id)})
            return document
 


