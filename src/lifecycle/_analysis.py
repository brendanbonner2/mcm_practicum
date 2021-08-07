# analysis functions for the lifecycle management

from deepdiff import DeepDiff, model
import numpy as np


import logging
log = logging.getLogger(__name__)

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

