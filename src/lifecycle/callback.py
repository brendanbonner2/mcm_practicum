from tensorflow.python import keras
from lifecycle import lifecycle_db
import logging
log = logging.getLogger(__name__)

class LifecycleCallback(keras.callbacks.Callback):
    # UpdateLifecycleCallback descends from Callback
    def __init__(self, lifecycledb ):
        """ Save params in constructor
        """
        self.db = lifecycledb

    def on_epoch_end(self, epoch, logs=None):
        self.db.push_model(self.model, useParent = True)
        log.info('pushing model to lifecycle store (epoch: {})'.format(epoch))


class LifecycleEpochCallback(keras.callbacks.Callback):
    # UpdateLifecycleCallback descends from Callback
    def __init__(self, lifecycledb ):
        self.db = lifecycledb

def on_train_batch_end(self, batch, logs=None):
        self.db.push_model(self.model, useParent = True)
        log.info('pushing model to lifecycle store (batch: {})'.format(batch))

