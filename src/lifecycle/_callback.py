from tensorflow.python import keras
from lifecycle import database
import logging
log = logging.getLogger(__name__)

class LifecycleCallback(keras.callbacks.Callback):
    # UpdateLifecycleCallback descends from Callback
    def __init__(self, models, lifecycledb ):
        """ Save params in constructor
        """
        self.db = lifecycledb

    def on_epoch_end(self, epoch, logs=None):
        signature = self.db.push_model(self.model, useParent = True)
        log.info('pushing model to lifecycle store (epoch: {})'.format(epoch))


class LifecycleCallback(keras.callbacks.Callback):
    # UpdateLifecycleCallback descends from Callback
    def __init__(self, models, lifecycledb ):
        self.db = lifecycledb

def on_train_batch_end(self, batch, logs=None):
        signature = self.db.push_model(self.model, useParent = True)
        log.info('pushing model to lifecycle store (batch: {})'.format(batch))

