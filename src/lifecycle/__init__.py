# Package for the lifecycle_db class
import pymongo

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

    #Imported methods
    from ._database import init_model_db, write_model_db, get_model_data, get_signature, push_model, push_to_cloud
    from ._analysis  import get_ancestor, get_history, compare_models, compare_model_data
    from ._plot import plot_changes, plot_history

    def set_user(self, user):
        self.user = user

    def set_organisation(self,organisation):
        self.organisation = organisation


    def set_lifecycle(self, lifecycle):
        self.lifecycle = lifecycle

    def get_username(self):
        return self.username


class lifecycle_model:
    def __init__(self):
        pass

    from ._models import create_layer_data, create_model_data

