from django.apps import AppConfig

class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.news'  # Важно! Указываем полный путь
    verbose_name = 'Новости'