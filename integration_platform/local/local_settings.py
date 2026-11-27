"""Local-only Django fixture settings; never use for production."""
import os
import secrets
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORK=Path(os.environ['OPIS_LOCAL_WORKSPACE']).resolve() if os.environ.get('OPIS_LOCAL_WORKSPACE') else None
SECRET_KEY=(WORK/'secret.txt').read_text(encoding='utf-8').strip() if WORK else secrets.token_urlsafe(48)
DEBUG=False
ALLOWED_HOSTS=['127.0.0.1','localhost','testserver']
ROOT_URLCONF='local_urls'
INSTALLED_APPS=['django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware']
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':str(WORK/'auth.sqlite') if WORK else ':memory:'}}
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[ROOT/'expert_review'/'templates',ROOT/'local'/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth']}}]
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
LOGIN_URL='/accounts/login/'
LOGIN_REDIRECT_URL='/fixture/core-review/SYNTHETIC-001-PA1/'
LANGUAGE_CODE='ko'
TIME_ZONE='Asia/Seoul'
USE_TZ=True
OPIS_SYNTHETIC_CORE_REVIEW_ENABLED=bool(WORK)


def connection_factory():
    if not WORK or not (WORK/'READY_SYNTHETIC').is_file():raise ValueError('fixture workspace not ready')
    path=WORK/'core.sqlite'
    if path.is_symlink() or not path.is_file():raise ValueError('fixture database missing')
    from c09_connection import reopen
    db=reopen(path)
    if db.execute('SELECT queue_id FROM event ORDER BY queue_id').fetchall()!=[(f'SYNTHETIC-{i:03}',) for i in range(3)]:
        db.close();raise ValueError('fixture event scope')
    return db

OPIS_SYNTHETIC_CORE_CONNECTION_FACTORY=connection_factory
