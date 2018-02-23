class DeployRouter(object):
    """
    A router to control all database operations on models in the
    bugzilla application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read bugzilla models go to bugzilla DB.
        """
        if model._meta.app_label == 'auto_deploy':
            return 'deploy'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write bugzilla models go to bugzilla DB.
        """
        if model._meta.app_label == 'auto_deploy':
            return 'deploy'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the bugzilla app is involved.
        """
        if obj1._meta.app_label == 'auto_deploy' or \
                        obj2._meta.app_label == 'auto_deploy':
            return True
        return None

    def allow_migrate(self,db, app_label, model_name=None, **hints):
        """
        Make sure the bugzilla app only appears in the bugzilla database.
        """
        #if app_label == 'auto_deploy':
        #    print(db)
        #    return db =='deploy'
            
        #return None
        if db == 'deploy':
            return True
        elif db == 'default':
            return False
        else:
            return None



