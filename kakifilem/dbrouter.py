class AuthRouter:
    """
    A router to control database operations for auth models.
    """
    def db_for_read(self, model, **hints):
        # Skip auth models
        if model._meta.app_label == 'auth':
            return None
        return 'default'

    def db_for_write(self, model, **hints):
        # Skip auth models
        if model._meta.app_label == 'auth':
            return None
        return 'default'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Prevent migrations for auth models
        if app_label == 'auth':
            return False
        return True
