import os
import django
import json
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from kodys.models import *
from django.contrib.auth.models import User

def populate():
    # 0. User for auditing
    admin_user = User.objects.get(username='admin')

    # 1. Ensure MA_APPLICATION exists
    if not MA_APPLICATION.objects.filter(DATAMODE="A").exists():
        MA_APPLICATION.objects.create(
            NAME="Kodys Medical",
            VERSION="1.0",
            LOGO="/site_media/img/png/kodys_logo.png",
            DATAMODE="A"
        )
        print("Created MA_APPLICATION")

    # 2. Ensure MA_APPLICATION_SETTINGS exist
    settings_keys = [
        ("SET-09", '{"style": "Times_New_Roman", "size": 23, "color": "rgb(0, 0, 0)"}'),
        ("SET-10", '{"style": "Times_New_Roman", "size": 14, "color": "rgb(0, 0, 0)"}'),
        ("SET-11", '{"style": "Times_New_Roman", "size": 14, "color": "rgb(0, 0, 0)"}'),
    ]
    for key_code, key_value in settings_keys:
        if not MA_APPLICATION_SETTINGS.objects.filter(KEY_CODE=key_code).exists():
            MA_APPLICATION_SETTINGS.objects.create(
                KEY_CODE=key_code,
                KEY_VALUE=key_value,
                DATAMODE="A"
            )
            print("Created setting %s" % key_code)

    # 3. Create TX_ACCOUNT (Hospital Profile)
    if not TX_ACCOUNT.objects.filter(DATAMODE="A").exists():
        TX_ACCOUNT.objects.create(
            BUSINESS_NAME="Test Hospital",
            ADDRESS_LINE_1="123 Health Street",
            CITY="Chennai",
            ZIPCODE="600001",
            DATAMODE="A"
        )
        print("Created TX_ACCOUNT")

    # 4. Create Medical Apps
    apps_data = [
        ('DOPPLER', 'Kodys Doppler', '/site_media/img/png/doppler_icon.png'),
        ('BIOTHEZIVPT', 'Biothezi VPT', '/site_media/img/png/vpt_icon.png'),
        ('BIOTHEZIVPTULTRA', 'Biothezi VPT Ultra', '/site_media/img/png/vpt_ultra_icon.png'),
        ('PODOIMAT', 'Podo I Mat', '/site_media/img/png/podo_imat_icon.png'),
        ('PODOTMAP', 'Podo T Map', '/site_media/img/png/podo_tmap_icon.png'),
        ('KODYSHCPELITE', 'Kodys HCP Elite', '/site_media/img/png/hcp_elite_icon.png'),
        ('CAN', 'Kodys CAN', '/site_media/img/png/kodyscan_icon.png'),
    ]

    for code, name, icon in apps_data:
        MA_MEDICALAPPS.objects.get_or_create(
            CODE=code,
            defaults={
                'APP_NAME': name,
                'ICON_PATH': icon,
                'DATAMODE': 'A'
            }
        )
    print("Seeded all medical applications.")

    # 5. Create Test Master (Example for CAN)
    med_app = MA_MEDICALAPPS.objects.get(CODE='CAN')
    test_master, created = MA_MEDICALTESTMASTER.objects.get_or_create(
        CODE='CAN',
        defaults={
            'TEST_NAME': "Kodys CAN Test",
            'MEDICAL_APP': med_app,
            'DATAMODE': 'A'
        }
    )

    # 6. Create a Patient
    patient, created = TX_PATIENTS.objects.get_or_create(
        FRIENDLY_UID="100100",
        defaults={
            'UID': 'PAT-001',
            'NAME': "John Doe",
            'GENDER': "MALE",
            'AGE': 35,
            'PATIENT_MOBILE_NUMBER': "9876543210",
            'ADDRESS_LINE_1': "Street 1",
            'ZIPCODE': "600001",
            'DATAMODE': "A",
            'PREFIX': "Mr.",
            'CREATED_BY': admin_user,
            'UPDATED_BY': admin_user
        }
    )
    if created: print("Created Patient John Doe")

    # 7. Create Medical Test
    med_test, created = TX_MEDICALTESTS.objects.get_or_create(
        FRIENDLY_UID="TEST-100",
        defaults={
            'UID': 'T-100',
            'MEDICALTESTMASTER': test_master,
            'PATIENT': patient,
            'REPORTED_ON': timezone.now(),
            'DATAMODE': 'A'
        }
    )

    # 8. Create a CAN Report
    dummy_ecg = ",".join([str(i%100) for i in range(1000)])
    
    report, created = TX_MEDICALTESTREPORTS.objects.get_or_create(
        FRIENDLY_UID="REP-100",
        defaults={
            'UID': 'R-100',
            'MEDICALTEST': med_test,
            'TEST_TYPE': "KODYSCAN",
            'TEST_STATUS': "COMPLETED",
            'REPORTED_ON': timezone.now(),
            'CREATED_BY': admin_user,
            'UPDATED_BY': admin_user,
            'TEST_RESULT': json.dumps({"resting": {"peaklist": [10, 50, 90]}}),
        }
    )
    if created:
        # Check if fields exist before setting
        if hasattr(report, 'TM15_processed_data'):
            report.TM15_processed_data = dummy_ecg
        report.save()
        print("Created CAN Report for John Doe")

populate()
