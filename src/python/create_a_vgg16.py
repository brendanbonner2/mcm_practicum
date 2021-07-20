import numpy as np
import pandas as pd

from tf.keras.applications import VGG16

model = VGG16 (
    include_top=True,
    weights="imagenet",
    input_tensor=None,
    input_shape=None,
    pooling=None,
    classes=1000,
    classifier_activation="softmax",
)