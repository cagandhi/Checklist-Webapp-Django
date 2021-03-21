from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "users"

    def ready(self):
        # in order for signals for user and profile to work
        import users.signals  # noqa: F401
