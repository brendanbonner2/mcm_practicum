from tensorflow.keras.layers import Input, Conv2D, Dense, Flatten
from tensorflow.keras.models import Model

ipt = Input(shape=(16, 16, 16))
x   = Conv2D(12, 8, 1)(ipt)
x   = Flatten()(x)
out = Dense(16)(x)

model = Model(ipt, out)
model.compile('adam', 'mse')

X = np.random.randn(10, 16, 16, 16)  # toy data
Y = np.random.randn(10, 16)  # toy labels
for _ in range(10):
    model.train_on_batch(X, Y)

def get_weights_print_stats(layer):
    W = layer.get_weights()
    print(len(W))
    for w in W:
        print(w.shape)
    return W

def hist_weights(weights, bins=500):
    for weight in weights:
        plt.hist(np.ndarray.flatten(weight), bins=bins)

W = get_weights_print_stats(model.layers[1])
# 2
# (8, 8, 16, 12)
# (12,)

hist_weights(W)
