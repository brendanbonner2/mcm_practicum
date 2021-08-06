# database functions for the lifecycle management

from re import X
import pymongo
from deepdiff import DeepDiff, model
import numpy as np


from bson.objectid import ObjectId
import numpy as np

import logging

from tensorflow.python.keras.backend import sign
log = logging.getLogger(__name__)
logging.basicConfig(filename='{}.log'.format(__name__), encoding='utf-8', level=logging.DEBUG)

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.pyplot import figure



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
 

    def set_baseline(self,signature):
        # get local signature
        signature = self.get_signature(signature=signature, local=True)
        if signature == None:
            # see if signature in repository
                signature = self.get_signature(signature=signature, local=False)




# Get model and write to layer

    def get_history(self,search_sig, full_data=False):

        log.info("Getting Signature: {} ".format(search_sig))
        signature_data = self.get_signature(search_sig)
        if signature_data:

            # Print current signature
            history = []
            last_loop = False

            while True:

                # compare with parent
                if signature_data['parent']:
                    changes = self.compare_models(search_sig,signature_data['parent'])
                    structural_diff = len(changes['structure'])
                    data_diff = {'weight':np.prod(changes['data']['weight']), 'skew':np.prod(changes['data']['skew'])}
                else:
                    changes = {'structure':{}, 'data':{}}
                    structural_diff = 0
                    data_diff = {'weight':1, 'skew':1}
                    last_loop = True

                # Print current signature
                history_entry = {
                        'signature':    signature_data['signature'],
                        'timestamp':    signature_data['_id'].generation_time,
                        'username':     signature_data['username'],
                        'organisation': signature_data['organisation'],
                        'structural_diff':    structural_diff,
                        'data_diff':         data_diff,
                        'structure': {},
                        'data': {}
                }

                if full_data:
                    log.info('getting hist model based on signature {}'.format(search_sig))
                    model_data = self.get_model_data(signature=search_sig)
                    model_data.pop('_id', None)

                    history_entry['structure'] = changes['structure']                    
                    history_entry['data'] = model_data['data']
                    log.info(model  )

                history.append( history_entry )
                if last_loop:
                    return history
                
                # get next model
                signature_data = self.get_signature(signature_data['parent'])
                search_sig = signature_data['signature']

        else:
            print('signature not found')




# Get model and write to layer

    def get_ancestor(self,signature):

        log.info("Getting Ancestor: {} ".format(signature))
        signature_data = self.get_signature(signature)
        if signature_data:
            while signature_data['parent'] != None:
                signature_data = self.get_signature(signature_data['parent'])

            return signature_data['signature']

        else:
            print('signature not found')




    def compare_models(self,model_sig1, model_sig2):
        # pull models
        model2 = self.get_model_data(signature = model_sig2)
        model1 = self.get_model_data(signature = model_sig1)

        comparison = {}
        comp_struct = {}

        if model1 and model2:
            # Compare structure
            log.info('Comparing Model Structures')
            ddiff = DeepDiff(model1['structure'], model2['structure'])

            log.info(len(ddiff))
            # put ddif in dictionary
            comp_struct = {}
            if ddiff:
                
                for i in ddiff:
                    
                    comp_struct.update({ i: len(ddiff[i]) } )

            comp_data = self.compare_model_data(model1['data'], model2['data'])

            log.info('Comparing Model Values')
            comparison.update({'structure':comp_struct, 'data': comp_data})

        else:
            log.info('model not found')        

        return comparison


    # Compare two pulled sets for equivilance of stdev and bias
    def compare_model_data(self, model_data_1, model_data_2):
        log.info('Comparing model data')
        weight_history = []
        skew_history = []

        # pick the shortest model for comparison layers
        if len(model_data_2) > len(model_data_1):
            ref_model = model_data_1
        else:
            ref_model = model_data_2

        for key, value in ref_model.items():
            # Compare Weights
            if (model_data_1[key]['weight_std'] == 0) or (model_data_2[key]['weight_std'] == 0):
                weight_history.append(1)
            else:
                weight_history.append(
                    model_data_2[key]['weight_std']  / model_data_1[key]['weight_std']
                )
            
            # Compare Skew
            if (model_data_1[key]['skew'] == 0) or (model_data_2[key]['skew'] == 0):
                skew_history.append(1)
            else:
                skew_history.append(
                    model_data_2[key]['skew']  / model_data_1[key]['skew']
                )

        return {'weight':weight_history, 'skew':skew_history}


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

    def plot_history(self, signature):

        local_history = self.get_history(signature)

        weights = []
        skews = []
        dates = []

        for x in local_history:
            dates.append(x['timestamp'])
            if x['data_diff']:
                weights.append(x['data_diff']['weight'] * 100)
                skews.append(x['data_diff']['skew'] * 100)
            else:
                weights.append(0)
                skews.append(0)

        plt_dates = mdates.date2num(dates)

        plt.rcParams["figure.figsize"] = (10,5)
        fig, ax = plt.subplots()
        ax2 = ax.twinx()
        ax.set_ylim([0,100])
        ax2.set_ylim([-200,200])

        ax.plot_date(plt_dates, weights, 'b-')
        ax2.plot_date(plt_dates, skews)
        xfmt = mdates.DateFormatter('%d-%m %H:%M')
        ax.xaxis.set_major_formatter(xfmt)

        ax.set_xlabel('Layers')
        
        ax.set_ylabel('Weight Change %')
        ax2.set_ylabel('Skew Change %')
        ax.set_title('Model Training')

        plt.show()

    def plot_changes(self,sig1,sig2):
        model_diff = self.compare_models(sig1,sig2)

        data = []
        for x in model_diff['data']['weight']:
            if x:
                data.append(x * 100)
            else:
                data.append(0)



        # Example data
        y_pos = np.arange(len(data))

        plt.rcParams["figure.figsize"] = (5,10)
        fig, ax = plt.subplots()
        ax.barh(y_pos, data, align='center')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(y_pos)
        ax.set_ylabel('Layers')
        ax.set_xlabel('Change %')

        ax.set_xlim([np.min(data), np.max(data)])


        if len(model_diff['structure']) == 0:
            ax.set_title('Model : No structural changes')
        else:
            ax.set_title('Model : Structural changes found')

        plt.show()