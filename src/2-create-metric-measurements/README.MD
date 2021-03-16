# Create Metric Measurments

This directory will contain the dunctions necessary to produce an efficient method of measuring the changes in deep neural networks.

While low parameter networks can be stored in model hd5 format, we are looking to provide enough information to identify the difference in training to allow the trainer to identify where the activity is being changed, but also the resolution needed to be usable.

On a simple perspective, we can establish a checksum of the complete model, plus on the next level an aggregation of the difference in each layers.

function	baseline
input		model
output		reduced_model_delta

The function will run through each layer of a neural network, and for each, reduce down to an x*y 2 array  stored in a series of numpy arrays. We will test is x*y needs to be reduced, or if we will allow full top level network layer size. For deep network arrays (i.e. 100x100x64) or dense layers.
