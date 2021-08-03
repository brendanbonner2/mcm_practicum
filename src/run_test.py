from lifecycle import database
from lifecycle import models


%load_ext autoreload
%autoreload 2
from lifecycle import database

mydb = database.lifecycle_db (username = 'projectUser',password = 'DCUpassword')
mydb.init_model_db()



bb_username = 'brendan.bonner@mail.dcu.ie'
bb_organisation = 'DCU'
bb_model_source = 'created in python'

bb_username = 'brendan.bonner@mail.dcu.ie'
bb_organisation = 'DCU'
bb_model_source = 'created in python'

mongodb_username = 'projectUser'
mongodb_password = 'DCUpassword'




# Initialise Databases

model_vgg16 = tf.keras.applications.VGG16(
    include_top=True,
    weights=None,
    input_tensor=None,
    input_shape=None,
    pooling=None,
    classes=1000
)

model_vgg16_imagenet = tf.keras.applications.VGG16(
    include_top=True,
    weights="imagenet",
    input_tensor=None,
    input_shape=None,
    pooling=None,
    classes=1000
)


model_vgg16_test = tf.keras.applications.VGG16(
    include_top=True,
    weights="imagenet",
    input_tensor=None,
    input_shape=None,
    pooling=None,
    classes=1000
)

model_resnet50 = tf.keras.applications.ResNet50(
    include_top=True,
    weights=None,
    input_tensor=None,
    input_shape=None,
    pooling=None,
    classes=500
)


model_resnet50_imagenet = tf.keras.applications.ResNet50(
    include_top=True,
    weights='imagenet',
    input_tensor=None,
    input_shape=None,
    pooling=None
)


signature1, layer_data1 = create_model_data(model_vgg16)
print(signature1)
signature2, layer_data2 = create_model_data(model_vgg16_test)
print(signature2)




parent = push_model(model_resnet50,local=False)
last = push_model(model_resnet50_imagenet,parent=parent,local=False)
print(parent, last)
parent = push_model(model_vgg16_imagenet,local=False)
last = push_model(model_vgg16_test, parent=parent,local=False)
print(parent, last)




parent = push_model(model_resnet50,local=False)
last = push_model(model_resnet50_imagenet,parent=parent,local=False)
print(parent, last)
parent = push_model(model_vgg16_imagenet,local=False)
last = push_model(model_vgg16_test, parent=parent,local=False)
print(parent, last)



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


xception1 = get_model_data(get_model('bbd930cc56dfa39dc55e1318d9b5da2571d9eff0eeb96de7648faacb69c253cd')['model_data'])
xception2 = get_model_data(get_model('bbd930cc56dfa39dc55e1318d9b5da2571d9eff0eeb96de7648faacb69c253cd')['model_data'])

x = xception1['structure']
y = xception2['structure']

shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}
print (len(shared_items))
unshared_items = {k: x[k] for k in x if k in y and x[k] != y[k]}
print (len(unshared_items))


# %%
# Make a small adjustment to test the SHA change
last = push_model(model_vgg16_test, parent=last, username='brendanboner@gmail.com', local=False)

for x in range(5):
    weights = model_vgg16_test.layers[1].get_weights()
    weights[0][0][0][0] = weights[0][0][0][0] * 1.004
    model_vgg16_test.layers[1].set_weights(weights)
    last = push_model(model_vgg16_test, parent=last)
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
