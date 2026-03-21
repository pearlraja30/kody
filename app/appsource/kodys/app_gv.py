# -*- coding: utf-8 -*-
from django.conf import settings

DATAMODE_CHOICES = (('A','Active'),('I', 'Inactive'),('D','Deleted'))
GENDER_CHOICES = (('MALE','Male'),('FEMALE', 'Female'),('TRANSGENDER','Transgender'))
DATABASEBACKUP_CHOICES = (('DAYWISE','DayWise'),('AUTOMATIC', 'Automatic'),('MANUAL','Manual'))
SERVICE_CHOICES = (('USERMANUAL','User Manual'),('SERVICEMANUAL', 'Service Manual'),('TESTPROCEDURE','Test Procedure'),('INTERPRETATION','Interpretation'))
APPLICATION_CHOICES = (('DOPPLER','Doppler'),('PODOIMAT', 'Podo I Mat'),('PODOTMAP','Podo T Map'),('BIOTHEZIVPT','Biothezi VPT'),('BIOTHEZIVPTULTRA', 'Biothezi VPT Ultra'),('KODYSHCPELITE','Kodys HCP Elite'),('KODYSCAN','Kodys CAN'))
DEVICE_CHOICES = (('SCANNER','Scanner'),('MEDICALDEVICES', 'Medical Devices'),('PRINTER', 'Printer'))
ACCOUNTROLE_CHOICES = (('DOCTOR','Doctor'),('EXAMINER', 'Examiner'))
PREFIX_CHOICES = (('Mr.','Mr.'),('Mrs.', 'Mrs.'),('Miss.', 'Miss.'))
HCP_PREFIX_CHOICES = (('Dr.','Dr.'), ('Mr.','Mr.'),('Mrs.', 'Mrs.'),('Miss.', 'Miss.'))
SERVICETYPE_CHOICES = (('HARDWARE','Hardware'),('SOFTWARE', 'Software'))
CONNECTIONSTATUS_CHOICES = (('CONNECTED','Connected'),('DISCONNECTED', 'Disconnected'))
CONNECTIONTYPE_CHOICES = (('USB','USB'),('BLUETOOTH', 'BLUETOOTH'))
INSTRUCTIONTYPE_CHOICES = (('HELP','Help'),('PROCEDURE', 'Procedure'))
TEST_STATUS_CHOICES = (('COMPLETED','Completed'),('INCOMPLETE', 'Incomplete'))
TEMPERATURE_SCALE_CHOICES = (('CELSIUS','Celsius'),('FAHRENHEIT', 'Fahrenheit'))
