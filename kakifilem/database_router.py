class DefaultRouter:
    """
    A router to prevent Django from creating auth tables
    """
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Don't allow migrations for auth models since they exist
        if app_label == 'auth' or model_name in ['auth_user', 'auth_user_user_permissions']:
            return False
        return True

    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'
