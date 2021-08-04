# database functions for the lifecycle management

from re import X
import deepdiff
from deepdiff import diff
import pymongo
from deepdiff import DeepDiff

from pymongo import MongoClient
from bson.objectid import ObjectId

import logging
log = logging.getLogger(__name__)
logging.basicConfig(filename='{}.log'.format(__name__), encoding='utf-8', level=logging.DEBUG)



class lifecycle_db:
    def __init__(self, localclient=None, username=None, password=None,lifecycle=None,
        user=None, organisation = None):
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

        self.lifecycle = lifecycle
        self.user = user
        self.organisation = organisation

    def set_user(self, user):
        self.user = user

    def set_organisation(self,organisation):
        self.organisation = organisation


    def set_lifecycle(self, lifecycle):
        self.lifecycle = lifecycle

    def get_username(self):
        return self.username

    def init_model_db(self):

        global local_data_collection
        global local_signature_collection
        global remote_data_collection
        global remote_signature_collection

        db_cluster= 'cluster0.7ilyj.mongodb.net'
        
        # if username no provided, create a readonly client
        mongodb_login = "mongodb+srv://{}:{}@{}/test".format(self.username, self.password, db_cluster)
        dbclient_database   = self.dbclient["model_database"]
        self.local_data_collection         = dbclient_database["model_data"]
        self.local_signature_collection    = dbclient_database["signature"]

        log.info('Setting Cloud DB to {} for user {}'.format(db_cluster,self.username))

        # Make sure signatures are unique on both
        try:
            self.local_signature_collection.create_index(
                [("signature", pymongo.DESCENDING)],
                unique=True
            )
        except:
            log.warning('cannot set unique local database')

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
            log.warning('Cannot set unique signature in cloud database')
            no_db = True


    def write_model_db(self,
        signature,
        model_data,
        user = None,
        organisation = None,
        model_source=None,
        parent = '',
        local=True):



        if local:
            log.info('writing to local repository')
            db_data = self.local_data_collection
            db_sig = self.local_signature_collection
        else:
            log.info('writing to remote repository')
            db_data = self.remote_data_collection
            db_sig = self.remote_signature_collection

        if not user:
            user = self.user

        if not organisation:
            organisation = self.organisation

        # Insert Signature to Database (signatures)
        if self.get_signature(signature) == None:
            x = db_data.insert_one(model_data)
            model_id = x.inserted_id

            log.info('New model reference {} for {}'.format(
                model_id,
                signature)
            )

            # Inset Model Data to Database (modeldata)
            signature_data =  {
                'signature': signature,
                'parent': parent,
                'username': user,
                'organisation':organisation,
                'model_source': model_source,
                'model_data': model_id
            }

            x = db_sig.insert_one(signature_data)
            signature_model_id = x.inserted_id
            return signature_model_id
        else:
            log.warning('signature: {} already in database'.format(signature))
            return None


    def push_model(self,model, local=True, parent=None,
        user='', organisation = '', model_source=''):

        if self.lifecycle:
            signature, layer_data = self.lifecycle.create_model_data(model)

            self.write_model_db(
                signature=signature,
                model_data=layer_data,
                parent=parent,
                user=user,
                organisation=organisation,
                local=local,
                model_source=model_source
            )
            return signature
        else:
            log.warning('No model lifecycle set')
            return None



    def get_signature(self,signature, local=True):
        # print('looking for ', signature )
        
        if local:
            db_sig = self.local_signature_collection
        else:
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
            log.info('getting model for signature: {}'.format(signature))
            mysig = self.get_signature(signature=signature, local=local)
            if not mysig:
                # if not local then get remote
                log.info('could not find signature locally, searching remote repo')
                mysig = self.get_signature(signature=signature, local=False)

            if mysig:
                model_object = mysig['model_data']
                document = db_data.find_one({'_id': model_object})
            else:
                log.warning('Could not find signature')
                document = None
        else:
            log.info('getting model for model_id: {}'.format(model_id))

            document = db_data.find_one({'_id': ObjectId(model_id)})
            if (not document) and (local == True):
                log.info('could not find model_id locally, searching remote repo')
                document = self.remote_data_collection.find_one({'_id': ObjectId(model_id)})

            if not document:
                log.warning('Could not find model')

        return document
 

    def set_baseline(self,signature):
        # get local signature
        signature = self.get_signature(signature=signature, local=True)
        if signature == None:
            # see if signature in repository
                signature = self.get_signature(signature=signature, local=False)




# Get model and write to layer

    def show_history(self,signature):

        log.info("Getting Signature: {} ".format(signature))
        signature_data = self.get_signature(signature)
        if signature_data:

            # Print current signature
            print( '{}, Creator: {},{}'.format(
                signature_data['_id'].generation_time,
                signature_data['username'],
                signature_data['organisation']
                )
            )


            history = []
            while signature_data['parent'] != None:

                new_model_ref = signature_data['model_data']

                # get model
                signature_data = self.get_signature(signature_data['parent'])

                # Print current signature
                print( '{}, Creator: {},{}'.format(
                    signature_data['_id'].generation_time,
                    signature_data['username'],
                    signature_data['organisation']
                    )
                )
                model_ref = signature_data['model_data']

        else:
            print('signature not found')

    def compare_models(self,model_sig1, model_sig2):
        # pull models
        model2 = self.get_model_data(signature = model_sig2)
        model1 = self.get_model_data(signature = model_sig1)

        comparison = {}
        if model1 and model2:
            # Compare structure
            log.info(model1['structure'])
            log.info(model2['structure'])

            ddiff = DeepDiff(model1['structure'], model2['structure'])

            if ddiff:
                for i in ddiff:
                    comparison.update({ i: len(ddiff[i]) } )

        else:
            log.info('model not found')        
            
        return comparison


'''
    def compare_values(self,model1, model2)
        new_model_data = self.get_model_data(signature_data['model_data'])
        if new_model_data == None:
            print ('no model data for : ', signature_data['model_data'])
        else:
            history_layer = []
            data = new_model_data['data']
            for key, value in data.items():
                if (old_data[key]['weight_std'] == 0):
                    history_layer.append(old_data[key]['weight_std'])
                else:
                    history_layer.append(
                        value['weight_std']  / old_data[key]['weight_std']
                    )

            history.append(history_layer)
            old_data = new_model_data['data']




        print(signature_data['username'], signature_data['organisation'])
        print(history)

'''