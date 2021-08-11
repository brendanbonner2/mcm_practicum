import tensorflow as tf
import matplotlib.pyplot as plt

from lifecycle import lifecycle_db
from lifecycle import lifecycle_model


%load_ext autoreload
%autoreload 2

#### Lifecycle Change: Create a classes

#!pip install DeepDiff
#!pip install dnspython

!pip install lifecycle-0.0.3.tar.gz


from lifecycle import lifecycle_model
from lifecycle import lifecycle_db


# local_db_cluster = 'cluster0.7ilyj.mongodb.net'
# local_username = 'projectUser'
# local_password = 'DCUpassword'
# localcloudclient = "mongodb+srv://{}:{}@{}/local_test".format(
#     local_username, local_password, local_db_cluster
#     )

my_life = lifecycle_model()
mydb = lifecycle_db (
#    localclient=localcloudclient,
    username = 'projectUser',password = 'DCUpassword',
    user='brendan.bonner2@mail.dcu.ie', organisation='Dublin City University',
    lifecycle=my_life)
mydb.init_model_db()

# Initialise Databases

model_vgg16 = tf.keras.applications.VGG16(
    include_top=True,
    weights="imagenet",
    input_tensor=None,
    input_shape=None,
    pooling=None,
    classes=1000
)

model_resnet50 = tf.keras.applications.ResNet50(
    include_top=True,
    weights='imagenet',
    input_tensor=None,
    input_shape=None,
    pooling=None
)


signature_vgg = mydb.push_model(model_vgg16_imagenet)
mydb.push_to_cloud(signature_vgg)
signature_resnet = mydb.push_model(model_resnet50_imagenet,local=False)



# Push all default models from Keras
keras_model_list = {
    'VGG16': tf.keras.applications.VGG16,
    'DenseNet121': tf.keras.applications.DenseNet121,
    'Xception': tf.keras.applications.Xception
}

for name, model_type in enumerate(keras_model_list):
    print(model_type)
    model = keras_model_list[model_type]()
    print(push_model(model,model_source = model_type, organisation='Keras'))

# Make a small adjustment to test the SHA change
model_vgg16_test = model_vgg16_imagenet

for x in range(5):
    weights = model_vgg16_test.layers[1].get_weights()
    weights[0][0][0][0] = weights[0][0][0][0] * 1.004
    model_vgg16_test.layers[1].set_weights(weights)
    last = mydb.push_model(model_vgg16_test, useParent=True)
    print(last)



def show_history(signature):

    print("Getting Signature: ",signature)
    signature_data = get_model(signature)
    if (signature_data):
        baseline_model_data = get_model_data(signature_data['model_data'])

        if baseline_model_data == None:
            print ('no model data for : ', signature_data['model_data'])
        else:
            print('Layers: ', len(baseline_model_data['data']))
            print( signature_data['_id'].generation_time, ' : Model Id ', signature_data['model_data'])
            old_data = baseline_model_data['data']

            history = []
            while signature_data['parent'] != None:

                # get model
                signature_data = get_model(signature_data['parent'])
                print( signature_data['_id'].generation_time, ' : Model Id ', signature_data['model_data'])

                new_model_data = get_model_data(signature_data['model_data'])
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
    else:
        print('signature not found')



def diff_model(model_vgg16, model_resnet50):
    for l1, l2 in zip(model_vgg16.layers, model_resnet50.layers):
        w1 = l1.get_weights()
        w2 = l2.get_weights()
        if len(w1) > 0:
            wa1 = np.ndarray.flatten(w1[0])
            wa2 = np.ndarray.flatten(w2[0])
            # Weights available
            print(l1.get_config()['name'],
                w1[0].shape,
                np.std(wa1), np.median(wa1),
                w2[0].shape,
                np.std(wa2), np.median(wa2),
                np.std(wa1) == np.std(wa2)
            )
            
        else:
            print(l1.get_config()['name'],len(w1))


def get_weights_print_stats(layer):
    W = layer.get_weights()
    if len(W) > 0:
        print(len(W))
        print(W[0].shape)
    return W

def hist_weights(weights, bins=100, label='default'):
    for weight in weights:
        
        plt.hist(np.ndarray.flatten(weight), bins=bins, label=label)



show_all = False

hist_std1 = []
hist_std2 = []
hist_skew1 = []
hist_skew2 = []

for l1, l2 in zip(model_vgg16_imagenet.layers, model_vgg16.layers):

    w1 = l1.get_weights()
    w2 = l2.get_weights()


    if len(w1) > 0:
        # Layers available

        weight1_value   = np.ndarray.flatten(w1[0])
        weight1_skew  = skew(np.ndarray.flatten(w1[0]))
        weight1_std     = np.std(weight1_value).item()
        # print('std1 {:.4f}, skew1 {:.4f}'.format(weight1_std, weight1_skew))
        
        weight2_value   = np.ndarray.flatten(w2[0])
        weight2_skew  = skew(np.ndarray.flatten(w2[0]))
        weight2_std     = np.std(weight2_value).item()
        # print('std2 {:.4f}, skew2 {:.4f}'.format(weight2_std, weight2_skew))

        hist_std1.append(weight1_std)
        hist_std2.append(weight2_std)
        hist_skew1.append(weight1_skew)
        hist_skew2.append(weight2_skew)
        
        if show_all:
            print(l1.get_config()['name'],len(w1), w1[0].shape)
            plt.hist(
                [ np.ndarray.flatten(w1[0]),
                np.ndarray.flatten(w2[0])],
                alpha=0.5, bins=1000, label=['X','Y'])
            plt.legend(loc='upper right')

            plt.show()


hist_std = 1
hist_skew = 1
for i,v in enumerate(hist_std1):
    if (v != 0):
        hist_std = (hist_std2[i] / v) * hist_std
    if (hist_skew1[i] != 0):
        hist_skew = (hist_skew2[i] / hist_skew1[i]) * hist_skew

print ('std diff : {:.4f} %'.format((1-hist_std) * 100))
print ('skw diff : {:.4f} %'.format((1-hist_skew) * 100))

layers = len(hist_std1)
plt.bar( np.arange(layers) * 2, hist_std1, color = 'red' , alpha=0.5, label='std1')
plt.bar( np.arange(layers)* 2 + 1, hist_std2, color = 'blue', alpha=0.5, label='std2' )
plt.legend(loc='upper right')

plt.show

layers = len(hist_skew1)
print(layers)
plt.bar( np.arange(layers) * 2, hist_skew1, color = 'red' , alpha=0.5, label='skew1')
plt.bar( np.arange(layers)* 2 + 1, hist_skew2, color = 'blue', alpha=0.5, label='skew2' )
plt.legend(loc='upper right')
plt.show
