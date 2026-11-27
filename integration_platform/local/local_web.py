"""Initialize or run a loopback-only synthetic OPIS expert review demo."""
import argparse
import getpass
import os
from pathlib import Path
import secrets
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),*(str(ROOT/d) for d in ('db','consensus','analytics','dashboard','tests'))]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['init','run']);p.add_argument('--workspace',type=Path,required=True);args=p.parse_args()
    work=args.workspace.resolve();repo=ROOT.parent
    if work==repo or repo in work.parents:p.error('workspace must be outside repository')
    import django
    if args.action=='init':
        if work.exists():p.error('new workspace required')
        password=getpass.getpass('Password for fixture:expert (at least 12 characters): ')
        if len(password)<12 or password!=getpass.getpass('Confirm password: '):p.error('password mismatch or too short')
        work.mkdir(mode=0o700,parents=True,exist_ok=False)
        with (work/'secret.txt').open('x',encoding='utf-8') as file:file.write(secrets.token_urlsafe(48))
        if os.name!='nt':(work/'secret.txt').chmod(0o600)
        from c09_core_e2e import fixture
        from c09_guard import install
        from c04_r1_bridge import calculate
        db=fixture(3)
        try:
            install(db);calculate(db,1);dest=sqlite3.connect(work/'core.sqlite')
            try:db.backup(dest)
            finally:dest.close()
        finally:db.close()
    elif not (work/'READY_SYNTHETIC').is_file():p.error('initialize a synthetic workspace first')
    os.environ['OPIS_LOCAL_WORKSPACE']=str(work);os.environ['DJANGO_SETTINGS_MODULE']='local_settings'
    django.setup()
    from django.core.management import call_command
    if args.action=='init':
        from django.contrib.auth.models import Group,User
        call_command('migrate',interactive=False,verbosity=0)
        group,_=Group.objects.get_or_create(name='EXPERT');user=User.objects.create_user(username='fixture:expert',password=password);user.groups.add(group)
        (work/'READY_SYNTHETIC').write_text('SYNTHETIC_ONLY\n',encoding='utf-8')
        print('Synthetic workspace initialized:',work)
    else:call_command('runserver','127.0.0.1:8000',use_reloader=False)

if __name__=='__main__':main()
