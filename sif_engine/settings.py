from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'sih-26165-demo-secret-key-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1','localhost']
INSTALLED_APPS = ['django.contrib.contenttypes','django.contrib.sessions','django.contrib.staticfiles','detector']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware']
ROOT_URLCONF = 'sif_engine.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'detector'/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request']}}]
WSGI_APPLICATION = 'sif_engine.wsgi.application'
DATABASES = {'default': {'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'db.sqlite3'}}
LANGUAGE_CODE='en-us'; TIME_ZONE='Asia/Kolkata'; USE_I18N=True; USE_TZ=True
STATIC_URL='static/'; STATICFILES_DIRS=[BASE_DIR/'detector'/'static']; DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
