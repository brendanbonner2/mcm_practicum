
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import hashlib
from scipy.stats import skew


from lifecycle.database import lifecycle_db

class lifecycle:
    def __init__(self, lifecycle_db, user, organisation):
        self.lifecycle_db = lifecycle_db
        self.user = user
        self.organisation = organisation

    def set_user(self, user):
        self.user = user

    def set_organisation(self,organisation):
        self.organisation = organisation


    # internal Layer Functions 
    def create_layer_data(layer):

        # get structure array
        layer_structure  = {
            "class": layer.__class__.__name__,
            "input_shape": layer.input_shape,
            "output_shape": layer.output_shape,
            "trainable": layer.trainable,
            "params": layer.count_params()
    #        ,
    #        "name": layer.name
        }

        # get layer weights and bias
        weights = layer.get_weights()
    

        if len(weights) == 0:
            calc_weight_std = 0
            calc_weight_mean = 0
            calc_bias_std = 0
            calc_bias_mean = 0
            calc_skew = 0

        if len(weights) == 1:
        #    weight_x = np.ndarray.flatten(weights[0])
            calc_weight_std = np.std(weights[0]).astype(float32)
            calc_weight_mean = np.mean(weights[0]).astype(float32)
            calc_skew = skew(np.ndarray.flatten(weights[0]))
            calc_bias_std = 0
            calc_bias_mean = 0

        if len(weights) > 1:
            calc_weight_std = np.std(weights[0]).astype(float32)
            calc_weight_mean = np.mean(weights[0]).astype(float32)
            calc_skew = skew(np.ndarray.flatten(weights[0]))
            calc_bias_std = np.std(weights[1]).astype(float32)
            calc_bias_mean = np.mean(weights[1]).astype(float32)
            
        layer_values = {
            "weight_std" : calc_weight_std,
            "weight_mean" : calc_weight_mean,
            "bias_std" : calc_bias_std,
            "bias_mean" : calc_bias_mean,
            "skew" : calc_skew
        }

        return layer_structure, layer_values

    def create_model_data(self, model):
        # initiate hashing function
        sha = hashlib.sha256()

        layer_data_set = {}
        layer_structure_set = {}
        
        for index, value in enumerate(model.layers):
            # Run through the layers
            layer_structure, layer_data = self.create_layer_data(value)
            # print(layer_data, layer_values, hash(layer_values))
            sha.update(repr(layer_structure).encode('utf-8'))
            sha.update(repr(layer_data).encode('utf-8'))

            layer_data_set[str(index)] = layer_data
            layer_structure_set[str(index)] = layer_structure

        
        layer_data = {"structure":layer_structure_set, "data":layer_data_set}

        return sha.hexdigest(), layer_data




