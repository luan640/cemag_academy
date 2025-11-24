from .base import *

# Configurações específicas de desenvolvimento
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'obligations-donation-practices-problems.trycloudflare.com']
CSRF_TRUSTED_ORIGINS = [
    'https://obligations-donation-practices-problems.trycloudflare.com',
]

# Banco de dados para desenvolvimento
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'OPTIONS': {
            'options': f'-c search_path={env("SCHEMA_DB_NAME_TESTE")}',
        },
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Configurações adicionais para desenvolvimento (opcional)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

