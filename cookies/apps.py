from django.apps import AppConfig


class CookiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cookies'

    def ready(self):
        import cookies.signals  # Замените на имя вашего приложения