# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from jsonfield import JSONField

from app_gv import *

# Create your models here.
# Master Table
class MA_COUNTRY(models.Model):
    NAME = models.CharField(max_length=255, db_index=True)
    ISO2 = models.CharField(max_length=2)
    ISO3 = models.CharField(max_length=3)
    CREATED_ON =  models.DateTimeField(auto_now_add=True)
    UPDATED_ON = models.DateTimeField(auto_now=True)
    DATAMODE = models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

    def __unicode__(self):
        return "{0}".format(self.NAME)

    class Meta:
        db_table = 'MA_COUNTRY'
        ordering = ['-pk', ]
        app_label = 'kodys'


class MA_STATE(models.Model):
    COUNTRY = models.ForeignKey(MA_COUNTRY)
    NAME = models.CharField(max_length=255, db_index=True)
    SHORT_CODE = models.CharField(max_length=5)
    CREATED_ON =  models.DateTimeField(auto_now_add=True)
    UPDATED_ON = models.DateTimeField(auto_now=True)
    DATAMODE = models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

    def __unicode__(self):
        return "{0}".format(self.NAME)

    class Meta:
        db_table = 'MA_STATE'
        ordering = ['-pk', ]
        app_label = 'kodys'


class MA_APPLICATION(models.Model):
	NAME 		= models.CharField(max_length=100)
	VERSION 	= models.CharField(max_length=50)
	LOGO		= models.TextField()
	ABOUT		= models.TextField()
	WEBSITE		= models.TextField()
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.NAME)

	class Meta:
		db_table = 'MA_APPLICATION'
		ordering = ['-pk', ]
		app_label = 'kodys'


class MA_APPLICATION_MANUALS(models.Model):
	NAME 		= models.CharField(max_length=100)
	CATEGORY 	= models.CharField(max_length=20, choices=SERVICE_CHOICES)
	SUB_CATEGORY = models.CharField(max_length=20, choices=APPLICATION_CHOICES)
	DESCRIPTION	= models.TextField()
	MANUAL_PATH	= models.TextField(blank=True, null=True)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.NAME)

	class Meta:
		db_table = 'MA_APPLICATION_MANUALS'
		ordering = ['-pk', ]
		app_label = 'kodys'


class MA_APPLICATION_CONTACTS(models.Model):
	NAME 		= models.CharField(max_length=100)
	POSITION 	= models.CharField(max_length=100)
	EMAIL 		= models.EmailField(blank=True, null=True)
	MOBILE_NUMBER = models.CharField(max_length=50)
	DISPLAY_ORDER = models.IntegerField(default=1000)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.NAME)

	class Meta:
		db_table = 'MA_APPLICATION_CONTACTS'
		ordering = ['-pk', ]
		app_label = 'kodys'


class MA_APPLICATION_SETTINGS(models.Model):
	KEY_TYPE 	= models.CharField(max_length=100)
	KEY_NAME 	= models.CharField(max_length=100)
	KEY_CODE 	= models.CharField(max_length=100)
	KEY_VALUE 	= models.CharField(max_length=100)
	KEY_ORDER 	= models.CharField(max_length=100)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.KEY_NAME)

	class Meta:
		db_table = 'MA_APPLICATION_SETTINGS'
		ordering = ['-pk', ]
		app_label = 'kodys'


class MA_MEDICALAPPS(models.Model):
	APP_NAME 	= models.CharField(max_length=100)
	CODE 	= models.CharField(max_length=20)
	DESCRIPTION	= models.TextField(blank=True, null=True)
	ICON_PATH	= models.TextField()
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.APP_NAME)

	class Meta:
		db_table = 'MA_MEDICALAPPS'
		ordering = ['-pk', ]
		app_label = 'kodys'


class MA_MEDICALTESTMASTER(models.Model):
	TEST_NAME 	= models.CharField(max_length=255)
	CODE 	= models.CharField(max_length=20)
	MEDICAL_APP = models.ForeignKey(MA_MEDICALAPPS)
	ORGAN_IMAGE	= models.TextField(blank=True, null=True)
	ORGAN_TYPE	= models.CharField(max_length=20, blank=True, null=True)
	DESCRIPTION	= models.TextField(blank=True, null=True)
	REFERRED_BY = models.CharField(max_length=100, blank=True, null=True)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.TEST_NAME)

	class Meta:
		db_table = 'MA_MEDICALTESTMASTER'
		ordering = ['-pk', ]
		app_label = 'kodys'


class MA_MEDICALAPPDEVICES(models.Model):
	MEDICAL_APP = models.ForeignKey(MA_MEDICALAPPS)
	DEVICE_NAME = models.CharField(max_length=100)
	DEVICE_TYPE = models.CharField(max_length=100, choices=DEVICE_CHOICES)
	DEVICE_KEY 	= models.CharField(max_length=20,blank=True,null=True)
	PRODUCT_ID  = models.CharField(max_length=10,blank=True,null=True)
	VENDOR_ID   = models.CharField(max_length=10,blank=True,null=True)
	PORT_NAME   = models.CharField(max_length=10,blank=True,null=True)
	DEVICE_CONFIG = models.CharField(max_length=20,blank=True,null=True)
	DEVICE_MORE_OPTION = models.TextField(blank=True,null=True)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.DEVICE_NAME)

	class Meta:
		db_table = 'MA_MEDICALAPPDEVICES'
		ordering = ['-pk', ]
		app_label = 'kodys'


class MA_MEDICALTESTFIELDS(models.Model):
	MEDICALTESTMASTER = models.ForeignKey(MA_MEDICALTESTMASTER)
	KEY_POSITION = models.CharField(max_length=100)
	KEY_ORDER 	= models.CharField(max_length=100)
	KEY_NAME 	= models.CharField(max_length=100, blank=True, null=True)
	KEY_CODE 	= models.CharField(max_length=100)
	KEY_TYPE 	= models.CharField(max_length=100)
	KEY_VALUE_OPTIONS = models.CharField(max_length=100)
	KEY_UNITS 	= models.CharField(max_length=5)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.KEY_NAME)

	class Meta:
		db_table = 'MA_MEDICALTESTFIELDS'
		ordering = ['-pk', ]
		app_label = 'kodys'


class MA_MEDICALTESTMASTERINTERPERTATION(models.Model):
	MEDICALTESTMASTER = models.ForeignKey(MA_MEDICALTESTMASTER)
	RANGES 		= JSONField()
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.MEDICALTESTMASTER.TEST_NAME)

	class Meta:
		db_table = 'MA_MEDICALTESTMASTERINTERPERTATION'
		ordering = ['-pk', ]
		app_label = 'kodys'


class MA_MEDICALTESTINSTRUCTION(models.Model):
	MEDICALTESTMASTER = models.ForeignKey(MA_MEDICALTESTMASTER)
	INSTRUCTION_TYPE = models.CharField(max_length=100, choices=INSTRUCTIONTYPE_CHOICES)
	INSTRUCTION_CONTENT = models.TextField()
	INSTRUCTION_IMAGE = JSONField(blank=True, null=True)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.INSTRUCTION_CONTENT)

	class Meta:
		db_table = 'MA_MEDICALTESTINSTRUCTION'
		ordering = ['-pk', ]
		app_label = 'kodys'			


class MA_MEDICALTESTREPORTTEMPLATES(models.Model):
	MEDICALTESTMASTER = models.ForeignKey(MA_MEDICALTESTMASTER)
	NAME 	= models.CharField(max_length=100)
	CODE 	= models.CharField(max_length=20)
	TEMPLATE_PATH = models.TextField()
	DESCRIPTION	= models.TextField()
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.NAME)

	class Meta:
		db_table = 'MA_MEDICALTESTREPORTTEMPLATES'
		ordering = ['-pk', ]
		app_label = 'kodys'

#Master Table for Account
class MA_ACCOUNTROLE(models.Model):
	NAME 	= models.CharField(max_length=100)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.NAME)

	class Meta:
		db_table = 'MA_ACCOUNTROLE'
		ordering = ['-pk', ]
		app_label = 'kodys'


class MA_ACCOUNTPERMISSION(models.Model):
	NAME 	= models.CharField(max_length=100)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.NAME)

	class Meta:
		db_table = 'MA_ACCOUNTPERMISSION'
		ordering = ['-pk', ]
		app_label = 'kodys'	


class MA_ACCOUNTROLEPERMISSION(models.Model):
	ACCOUNTROLE 	= models.ForeignKey(MA_ACCOUNTROLE)
	ACCOUNTPERMISSION 	= models.ForeignKey(MA_ACCOUNTPERMISSION)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}-{1}".format(self.ACCOUNTROLE.NAME,self.ACCOUNTPERMISSION.NAME)

	class Meta:
		db_table = 'MA_ACCOUNTROLEPERMISSION'
		ordering = ['-pk', ]
		app_label = 'kodys'	


class MA_HCP_SPECIALIZATION(models.Model):
	NAME 	= models.CharField(max_length=100)
	MEDICAL_APP = models.ForeignKey(MA_MEDICALAPPS)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.NAME)

	class Meta:
		db_table = 'MA_HCP_SPECIALIZATION'
		ordering = ['-pk', ]
		app_label = 'kodys'	

# Transcation Table
class TX_ACCOUNT(models.Model):
	BUSINESS_NAME = models.CharField(max_length=100)
	BUSINESS_SHORT_NAME = models.CharField(max_length=100, blank=True, null=True)
	BUSINESS_SHORT_CODE = models.CharField(max_length=100, blank=True, null=True)
	BUSINESS_LOGO_PATH	= models.TextField(blank=True, null=True)
	EMAIL = models.EmailField(blank=True, null=True)
	PHONE_NUMBER = models.CharField(max_length=20)
	MOBILE_NUMBER = models.CharField(max_length=20, blank=True, null=True)
	FAX_NUMBER = models.CharField(max_length=20, blank=True, null=True)
	IS_REPORT_HEADER = models.BooleanField(default=True)
	ADDRESS_LINE_1 = models.TextField()
	ADDRESS_LINE_2 = models.TextField(blank=True, null=True)
	ADDRESS_LINE_3 = models.TextField(blank=True, null=True)
	CITY = models.CharField(max_length=50, blank=True, null=True)
	STATE = models.CharField(max_length=50, blank=True, null=True)
	COUNTRY = models.CharField(max_length=50, blank=True, null=True)
	ZIPCODE = models.CharField(max_length=10, blank=True, null=True)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.BUSINESS_NAME)

	class Meta:
		db_table = 'TX_ACCOUNT'
		ordering = ['-pk', ]
		app_label = 'kodys'	


class TX_ACCOUNTLICENSE(models.Model):
	ACCOUNT = models.ForeignKey(TX_ACCOUNT)
	ACCOUNT_LICENSE_KEY = models.CharField(max_length=100)
	ACCOUNT_LICENSE_SECRET = models.CharField(max_length=100)
	ACCOUNT_LICENSE = JSONField()
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.ACCOUNT_LICENSE_KEY)

	class Meta:
		db_table = 'TX_ACCOUNTLICENSE'
		ordering = ['-pk', ]
		app_label = 'kodys'	


class TX_APPLICATIONSERVICEREQUESTS(models.Model):
	ACCOUNT = models.ForeignKey(TX_ACCOUNT, blank=True, null=True)
	HOSPITAL_NAME = models.CharField(max_length=255, blank=True, null=True)
	C_NAME = models.CharField(max_length=100)
	C_EMAIL = models.EmailField()
	C_MOBILE_NUMBER = models.CharField(max_length=20)
	ATTACHMENT_FILE_PATH = models.TextField()
	SR_TYPE = models.CharField(max_length=100, choices=SERVICETYPE_CHOICES)
	SR_DETAILS = models.TextField()
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.C_NAME)

	class Meta:
		db_table = 'TX_APPLICATIONSERVICEREQUESTS'
		ordering = ['-pk', ]
		app_label = 'kodys'			


class TX_ACCOUNTUSER(models.Model):
	UID = models.CharField(max_length=100)
	USER = models.ForeignKey(User)
	ACCOUNTROLE = models.ForeignKey(MA_ACCOUNTROLE)
	LAST_LOGIN  = models.DateTimeField(blank=True, null=True)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.UID)

	class Meta:
		db_table = 'TX_ACCOUNTUSER'
		ordering = ['-pk', ]
		app_label = 'kodys'			


class TX_HCP(models.Model):
	UID = models.CharField(max_length=100)
	FRIENDLY_UID = models.CharField(max_length=100)
	ACCOUNTUSER = models.ForeignKey(TX_ACCOUNTUSER, blank=True, null=True)
	NAME = models.CharField(max_length=100)
	# USERNAME = models.CharField(max_length=100)
	TYPE = models.CharField(max_length=100, choices=ACCOUNTROLE_CHOICES)
	# SPECIALIZATION = models.ForeignKey(MA_HCP_SPECIALIZATION)
	PREFIX 	= models.CharField(max_length=5, choices=HCP_PREFIX_CHOICES)
	GENDER = models.CharField(max_length=10, choices=GENDER_CHOICES)
	MOBILE_NUMBER = models.CharField(max_length=20, blank=True, null=True)
	EMAIL = models.EmailField(blank=True, null=True)
	LOGIN_ALLOWED = models.BooleanField(default=True)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	CREATED_BY 	= models.ForeignKey(User,related_name = "%(class)s_createdby")
	UPDATED_BY 	= models.ForeignKey(User,related_name = "%(class)s_updatedby")
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.UID)

	class Meta:
		db_table = 'TX_HCP'
		ordering = ['-pk', ]
		app_label = 'kodys'			


class TX_HCP_SPECIALIZATION(models.Model):
	SPECIALIZATION = models.ForeignKey(MA_HCP_SPECIALIZATION)
	HCP = models.ForeignKey(TX_HCP)
	DATAMODE = models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)
	
	def __unicode__(self):
		return "{0}".format(self.HCP.UID)

	class Meta:
		db_table = 'TX_HCP_SPECIALIZATION'
		ordering = ['-pk', ]
		app_label = 'kodys'		


class TX_PATIENTS(models.Model):
	UID = models.CharField(max_length=100)
	NAME = models.CharField(max_length=100)
	LAST_NAME = models.CharField(max_length=100, blank=True, null=True)
	SUR_NAME = models.CharField(max_length=100, blank=True, null=True)
	FRIENDLY_UID = models.CharField(max_length=100)
	PREFIX 	= models.CharField(max_length=5, choices=PREFIX_CHOICES)
	GENDER = models.CharField(max_length=10, choices=GENDER_CHOICES)
	AGE = models.IntegerField()
	PATIENT_MOBILE_NUMBER = models.CharField(max_length=20, blank=True, null=True)
	PATIENT_EMAIL = models.EmailField(blank=True, null=True)
	POC_MOBILE_NUMBER = models.CharField(max_length=20, blank=True, null=True)
	PREFIX_DIGITS_LENGTH = models.CharField(max_length=20, blank=True, null=True)
	POC_EMAIL = models.EmailField(blank=True, null=True)
	ADDRESS_LINE_1 = models.TextField()
	ADDRESS_LINE_2 = models.TextField(blank=True, null=True)
	ADDRESS_LINE_3 = models.TextField(blank=True, null=True)
	CITY = models.CharField(max_length=50, blank=True, null=True)
	STATE = models.ForeignKey(MA_STATE, blank=True, null=True)
	COUNTRY = models.ForeignKey(MA_COUNTRY, blank=True, null=True)
	ZIPCODE = models.CharField(max_length=10)
	HEIGHT = models.CharField(max_length=6, blank=True, null=True)
	WEIGHT = models.CharField(max_length=6, blank=True, null=True)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	CREATED_BY 	= models.ForeignKey(User,related_name = "%(class)s_createdby")
	UPDATED_BY 	= models.ForeignKey(User,related_name = "%(class)s_updatedby")
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.FRIENDLY_UID)

	class Meta:
		db_table = 'TX_PATIENTS'
		ordering = ['-pk', ]
		app_label = 'kodys'			


class TX_MEDICALTESTS(models.Model):
	UID = models.CharField(max_length=100)
	FRIENDLY_UID = models.CharField(max_length=100)
	MEDICALTESTMASTER = models.ForeignKey(MA_MEDICALTESTMASTER)
	PATIENT = models.ForeignKey(TX_PATIENTS)
	DOCTOR 	= models.ForeignKey(TX_HCP,related_name = "%(class)s_doctor", blank=True, null=True)
	EXAMINER 	= models.ForeignKey(TX_HCP,related_name = "%(class)s_examiner", blank=True, null=True)
	INTERPERTATION = models.TextField(blank=True, null=True)
	# IMPRESSION_NOTES = models.TextField(blank=True, null=True)
	REPORTED_ON = models.DateTimeField()
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.FRIENDLY_UID)

	class Meta:
		db_table = 'TX_MEDICALTESTS'
		ordering = ['-pk', ]
		app_label = 'kodys'	


class TX_MEDICALTESTENTRIES(models.Model):
	UID = models.CharField(max_length=100)
	MEDICALTEST = models.ForeignKey(TX_MEDICALTESTS)
	MEDICALTESTFIELDS = models.ForeignKey(MA_MEDICALTESTFIELDS)
	KEY_NAME = models.CharField(max_length=100, blank=True, null=True)
	KEY_CODE = models.CharField(max_length=100)
	KEY_VALUE = models.TextField(blank=True, null=True)
	KEY_VALUE_STATUS = models.CharField(max_length=100, blank=True, null=True)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.UID)

	class Meta:
		db_table = 'TX_MEDICALTESTENTRIES'
		ordering = ['-pk', ]
		app_label = 'kodys'		


class TX_MEDICALTESTREPORTS(models.Model):
	UID = models.CharField(max_length=100)
	FRIENDLY_UID = models.CharField(max_length=100)
	MEDICALTEST = models.ForeignKey(TX_MEDICALTESTS)
	REPORT_PATH	= models.TextField(blank=True, null=True)
	REPORTED_ON = models.DateTimeField()
	TEST_RESULT = models.TextField(blank=True, null=True)
	TEST_TYPE = models.CharField(max_length=20, blank=True, null=True)
	TEST_STATUS = models.CharField(max_length=20, default='INCOMPLETE', choices=TEST_STATUS_CHOICES)
	TEMPERATURE_SCALE= models.CharField(max_length=20, choices=TEMPERATURE_SCALE_CHOICES, blank=True, null=True)
	IMPRESSION_NOTES = models.TextField(blank=True, null=True)
	REFERRED_BY = models.CharField(max_length=255, blank=True, null=True)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	CREATED_BY 	= models.ForeignKey(User,related_name = "%(class)s_createdby")
	UPDATED_BY 	= models.ForeignKey(User,related_name = "%(class)s_updatedby")
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.UID)

	class Meta:
		db_table = 'TX_MEDICALTESTREPORTS'
		ordering = ['-pk', ]
		app_label = 'kodys'				


class TX_MEDICALDEVICESTATUS(models.Model):
	UID = models.CharField(max_length=100)
	MEDICAL_DEVICE = models.ForeignKey(MA_MEDICALAPPDEVICES)
	CONNECTION_STATUS = models.CharField(max_length=100, choices=CONNECTIONSTATUS_CHOICES)
	CONNECTION_TYPE = models.CharField(max_length=100, choices=CONNECTIONTYPE_CHOICES)
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.UID)

	class Meta:
		db_table = 'TX_MEDICALDEVICESTATUS'
		ordering = ['-pk', ]
		app_label = 'kodys'		


class TX_DATABASEBACKUPLOGS(models.Model):
	TYPE 		= models.CharField(max_length=20, default='AUTOMATIC', choices=DATABASEBACKUP_CHOICES)
	BACKUP_PATH	= models.TextField()
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	CREATED_BY 	= models.ForeignKey(User,related_name = "%(class)s_createdby")
	UPDATED_BY 	= models.ForeignKey(User,related_name = "%(class)s_updatedby")
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.BACKUP_PATH)

	class Meta:
		db_table = 'TX_DATABASEBACKUPLOGS'
		ordering = ['-pk', ]
		app_label = 'kodys'


class DOPPLER_GRAPHICAL_PDF(models.Model):
	TEST_REPORT = models.ForeignKey(TX_MEDICALTESTREPORTS)
	BASE_64_IMAGES = JSONField()
	CREATED_ON 	= models.DateTimeField(auto_now_add=True)
	UPDATED_ON 	= models.DateTimeField(auto_now=True)
	CREATED_BY 	= models.ForeignKey(User,related_name = "%(class)s_createdby")
	UPDATED_BY 	= models.ForeignKey(User,related_name = "%(class)s_updatedby")
	DATAMODE 	= models.CharField(max_length=1, default='A', choices=DATAMODE_CHOICES)

	def __unicode__(self):
		return "{0}".format(self.TEST_REPORT.UID)

	class Meta:
		db_table = 'DOPPLER_GRAPHICAL_PDF'
		ordering = ['-pk', ]
		app_label = 'kodys'