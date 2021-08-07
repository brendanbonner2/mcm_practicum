# database functions for the lifecycle management

import pymongo
from bson.objectid import ObjectId
import numpy as np
import logging

log = logging.getLogger(__name__)

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
    if self.create_index:
        try:
            self.local_signature_collection.create_index(
                [("signature", pymongo.DESCENDING)],
                unique=True
            )
        except:
            log.warning('Cannot set Index for Local Database')

    remote_client       = pymongo.MongoClient(mongodb_login)
    dbclient_database_r = remote_client["model_database"]
    self.remote_data_collection       = dbclient_database_r["model_data"]
    self.remote_signature_collection  = dbclient_database_r["signature"]
    
    if self.create_index:

        try:
            # Only if there is a remote account, allow writing, otherwise read only
            self.remote_signature_collection.create_index(
                [("signature", pymongo.DESCENDING)],
                unique=True
            )
        except:
            log.warning('Cannot set Index for Remote Database')


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
    if self.get_signature(signature,local=local) == None:
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
    user='', organisation = '', model_source='', useParent=False):

    if self.lifecycle:
        signature, layer_data = self.lifecycle.create_model_data(model)

        if useParent:
            parent = self.parent

        self.write_model_db(
            signature=signature,
            model_data=layer_data,
            parent=parent,
            user=user,
            organisation=organisation,
            local=local,
            model_source=model_source
        )
        
        self.parent = signature
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

def get_baseline(self):
    # get local signature
    return self.signature

def set_baseline(self,signature):
    # get local signature
    self.signature = self.get_signature(signature=signature, local=True)
    if self.signature == None:
        # see if signature in repository
            self.signature = self.get_signature(signature=signature, local=False)


def push_to_cloud(self, signature):
    # Take a local model, and push to the cloud, useful for baselines

    # Check if signature already exist in cloud
    remote_signature = self.get_signature(signature,local=False)
    if remote_signature:
        log.info('Pushed signature already in cloud')
    else:
        local_signature = self.get_signature(signature)
        if local_signature:
            local_model_id = local_signature['model_data']
            log.info(local_model_id)
            local_model = self.get_model_data(local_model_id)
            if local_model:
                log.info('Local Model found for push to cloud')
                # remove local database ID
                local_model.pop('_id', None)
                log.info('Writing Model with Signature {}'.format(signature))
                self.write_model_db(
                    signature=signature,
                    model_data=local_model,
                    parent=local_signature['parent'],
                    user=self.user,
                    organisation=self.organisation,
                    local=False,
                    model_source=local_signature['model_source']
                )
            else:
                log.warning('model not found in local database')
        else:
            log.warning('signature not found in local database, push required')

