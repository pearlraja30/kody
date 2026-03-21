import sys
import os
import json
import glob
import pandas as pd
import shutil
import uuid

from django.core.wsgi import get_wsgi_application
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
application = get_wsgi_application()

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage


def dropDatabase():
    os.remove("../db.sqlite3")
    print("DB deleted")


def migrate_app_database():
    result = False
    try:
        app_list = ["kodys"]
        for apps in app_list:
            apps = apps.replace(".","/")
            migration_path = os.path.join(settings.BASE_DIR, '%s/migrations'%(apps))
            for file in glob.glob(migration_path+"/0*.py"):
                os.remove(file)
        call_command('makemigrations', interactive=False)
        call_command('migrate', interactive=False)
        result = True
    except Exception,e:
       print('Error at %s:%s' %(sys.exc_traceback.tb_lineno,e))
    return result


def load_default_users():
    u1 = User()
    u1.username = settings.DEFAULT_USER_EMAIL
    u1.first_name = settings.DEFAULT_USER_FIRSTNAME
    u1.last_name = ''
    u1.email = settings.DEFAULT_USER_EMAIL
    u1.is_staff = 1
    u1.is_active = 1
    u1.is_superuser = 1
    u1.set_password(settings.DEFAULT_USER_PASSWORD)
    u1.save()
    accountuser = TX_ACCOUNTUSER()
    accountuser.UID = uuid.uuid4().hex[:30]
    accountuser.USER = u1
    account_role = MA_ACCOUNTROLE.objects.get(NAME="ADMIN")
    accountuser.ACCOUNTROLE = account_role
    accountuser.LAST_LOGIN = datetime.datetime.now()
    accountuser.save()
    return u1


def load_default_account_users():
    request = dict()
    pDict = dict()
    pDict['email'] = settings.DEFAULT_USER_EMAIL
    pDict['password'] = settings.DEFAULT_USER_PASSWORD
    pDict['user'] = User.objects.filter(username=settings.DEFAULT_USER_EMAIL).first()
    pDict['account_role_permission'] = 1


def build_fixtures(app_name):
    try:
        apps_list = ['kodys']
        # exclude form processor xlsx
        if app_name:
            app_model_list = [model_obj.model for model_obj in ContentType.objects.filter(app_label=app_name.split(".")[-1])]
            result = xlsx_to_json(app_name, app_model_list)
        else:
            for app_label in apps_list:
                app_model_list = [model_obj.model for model_obj in ContentType.objects.filter(app_label=app_label.split(".")[-1])]
                result = xlsx_to_json(app_label, app_model_list)
    except Exception,e:
        print('Error at %s:%s' %(sys.exc_traceback.tb_lineno,e))


def _load_fixture(fixture_name):
    try:
        call_command('loaddata','%s'%(fixture_name), verbosity=1)
    except Exception,e:
        print('Error at %s:%s' %(sys.exc_traceback.tb_lineno,e))


def run_fixtures(app_name):
    try:
        if app_name:
            app_path = "/".join(app_name.split("."))
            json_folder = os.path.join(settings.BASE_DIR, app_path, 'fixtures', 'json')
            for fixture_name in sorted(glob.glob(json_folder+"/"+"*.json")):
                _load_fixture(fixture_name)
        else:
            apps_list = ['kodys']
            for app_label in apps_list:
                app_path = "/".join(app_label.split("."))
                json_folder = os.path.join(settings.BASE_DIR, app_path, 'fixtures', 'json')
                for fixture_name in sorted(glob.glob(json_folder+"/"+"*.json")):
                    _load_fixture(fixture_name)
    except Exception,e:
        print('Error at %s:%s' %(sys.exc_traceback.tb_lineno,e))


def xlsx_to_json(app_label, app_model_list):
    result = False
    try:
        app_path = "/".join(app_label.split("."))
        fixture_path = os.path.join(settings.BASE_DIR, app_path,'fixtures', 'xlsx',"%s.xlsx"%(app_label.split(".")[-1]))
        # json folder remove and create
        if os.path.exists(fixture_path):
            json_folder = os.path.join(settings.BASE_DIR, app_path, 'fixtures', 'json')
            if os.path.isdir(json_folder):
                shutil.rmtree(json_folder)
            os.makedirs(json_folder)
            xl = pd.ExcelFile(fixture_path)
            for sheet_count,sheet_name in enumerate(xl.sheet_names):
                if sheet_name.lower() in app_model_list:
                    if len(str(sheet_count)) == 1:
                        sheet_count = "0%s"%(sheet_count)
                    data = xl.parse(sheet_name)

                    json_path = os.path.join(json_folder,"%s-%s-%s.json"%(app_label.split(".")[-1],sheet_count,sheet_name.lower()))
                    count = 0
                    json_list = list()
                    for record in json.loads(data.to_json(orient="records")):
                        for key,value in record.iteritems():
                            if isinstance(value, type(None)):
                                record[key] = ""
                        count += 1
                        updated_record = dict()
                        updated_record['model'] = "%s.%s"%(app_label.split(".")[-1],sheet_name.lower())
                        updated_record['pk'] = count
                        updated_record['fields'] = record
                        json_list.append(updated_record)

                    # data.to_json(json_path, orient='records', lines=False)
                    full_data = json.dumps(json_list)
                    with open(json_path, 'w') as jsonfile:
                        jsonfile.write(full_data)
                    print("Appname: %s ModelName: %s Success"%(app_label, sheet_name))
                else:
                    print("Appname: %s ModelName: %s Failed"%(app_label, sheet_name))
        else:
            print("Appname: %s Failed"%(app_label))
        result = True
    except Exception,e:
        print('Error at %s:%s' %(sys.exc_traceback.tb_lineno,e))
    return result