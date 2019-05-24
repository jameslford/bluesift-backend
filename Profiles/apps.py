from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = 'Profiles'

    def ready(self):
        super().ready()
        import Profiles.signals
