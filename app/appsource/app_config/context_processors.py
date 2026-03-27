# -*- coding: utf-8 -*-
import json
from django.conf import settings
from kodys.models import *

def app_config(request):
	COMMON_INFO = dict()
	try:
		kodys_info = MA_APPLICATION.objects.get(DATAMODE="A")
		COMMON_INFO['KODYS_LOGO'] = kodys_info.LOGO
		COMMON_INFO['KODYS_NAME'] = kodys_info.NAME
		COMMON_INFO['KODYS_VERSION'] = kodys_info.VERSION
	except:
		COMMON_INFO['KODYS_LOGO'] = "/site_media/img/png/kodys_logo.png"
		COMMON_INFO['KODYS_NAME'] = "Kodys Medical"
		COMMON_INFO['KODYS_VERSION'] = "1.0"
	
	if request.user.is_authenticated() and TX_ACCOUNTUSER.objects.filter(USER=request.user).exists():
		accountuser = TX_ACCOUNTUSER.objects.get(USER=request.user)

		COMMON_INFO['LAST_LOGIN'] = accountuser.LAST_LOGIN
		if TX_HCP.objects.filter(ACCOUNTUSER=accountuser).exists():
			hcp = TX_HCP.objects.get(ACCOUNTUSER=accountuser)
			COMMON_INFO['USERNAME'] = "%s %s"%(hcp.PREFIX, hcp.NAME)
	else:
		COMMON_INFO['LAST_LOGIN'] = ""
		COMMON_INFO['USERNAME'] = ""

	if TX_ACCOUNT.objects.filter(DATAMODE="A").exists():
		hospital_info = TX_ACCOUNT.objects.get(DATAMODE="A")
	else:
		hospital_info = ""
	
	if TX_ACCOUNTUSER.objects.filter(ACCOUNTROLE__NAME="MANAGER", DATAMODE="A").exists():
		hospital_accountuser = TX_ACCOUNTUSER.objects.get(ACCOUNTROLE__NAME="MANAGER", DATAMODE="A")
		COMMON_INFO['HOSPITAL_ACCOUNTUSER'] = hospital_accountuser
	else:
		COMMON_INFO['HOSPITAL_ACCOUNTUSER'] = ""
	if hospital_info:
		COMMON_INFO['HOSPITAL_NAME'] = hospital_info.BUSINESS_NAME
		COMMON_INFO['HOSPITAL_ADDRESS1'] = hospital_info.ADDRESS_LINE_1
		COMMON_INFO['HOSPITAL_ADDRESS2'] = hospital_info.ADDRESS_LINE_2
		COMMON_INFO['HOSPITAL_ADDRESS3'] = hospital_info.ADDRESS_LINE_3
		COMMON_INFO['CITY'] = hospital_info.CITY
		COMMON_INFO['STATE'] = hospital_info.STATE
		COMMON_INFO['COUNTRY'] = hospital_info.COUNTRY
		COMMON_INFO['ZIPCODE'] = hospital_info.ZIPCODE
		COMMON_INFO['MOBILE_NUMBER'] = hospital_info.MOBILE_NUMBER
		if hospital_info.BUSINESS_LOGO_PATH:
			COMMON_INFO['HOSPITAL_LOGO'] = hospital_info.BUSINESS_LOGO_PATH
			logo_name = hospital_info.BUSINESS_LOGO_PATH.split("/")
			COMMON_INFO['HOSPITAL_LOGO_NAME'] = logo_name[-1]
		else:
			COMMON_INFO['HOSPITAL_LOGO'] = "/site_media/img/png/default_hospital_logo.png"
			COMMON_INFO['HOSPITAL_LOGO_NAME'] = ""
		COMMON_INFO['FAX_NUMBER'] = hospital_info.FAX_NUMBER
		COMMON_INFO['EMAIL'] = hospital_info.EMAIL
		COMMON_INFO['PHONE_NUMBER'] = hospital_info.PHONE_NUMBER
		COMMON_INFO['IS_REPORT_HEADER'] = hospital_info.IS_REPORT_HEADER
	else:
		COMMON_INFO['HOSPITAL_NAME'] = ""
		COMMON_INFO['HOSPITAL_ADDRESS1'] = ""
		COMMON_INFO['HOSPITAL_ADDRESS2'] = ""
		COMMON_INFO['HOSPITAL_ADDRESS3'] = ""
		COMMON_INFO['PHONE_NUMBER'] = ""
		COMMON_INFO['CITY'] = ""
		COMMON_INFO['STATE'] = ""	
		COMMON_INFO['COUNTRY'] = "" 
		COMMON_INFO['ZIPCODE'] = ""
		COMMON_INFO['MOBILE_NUMBER'] = ""
		COMMON_INFO['HOSPITAL_LOGO'] = "/site_media/img/png/default_hospital_logo.png"
		COMMON_INFO['HOSPITAL_LOGO_NAME'] = ""
		COMMON_INFO['FAX_NUMBER'] = ""
		COMMON_INFO['EMAIL'] = ""
		COMMON_INFO['IS_REPORT_HEADER'] = True
	
	try:
		hospital_name_font_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-09", DATAMODE="A")
		if hospital_name_font_settings.KEY_VALUE:
			name_font_settings = json.loads(hospital_name_font_settings.KEY_VALUE)
			COMMON_INFO['HOSPITAL_NAME_FONT_STYLE'] = name_font_settings["style"]
			COMMON_INFO['HOSPITAL_NAME_FONT_SIZE'] = name_font_settings["size"]
			COMMON_INFO['HOSPITAL_NAME_FONT_COLOR'] = name_font_settings["color"]
		else:
			raise Exception("Empty value")
	except:
		COMMON_INFO['HOSPITAL_NAME_FONT_STYLE'] = "Times_New_Roman"
		COMMON_INFO['HOSPITAL_NAME_FONT_SIZE'] = 23
		COMMON_INFO['HOSPITAL_NAME_FONT_COLOR'] = "rgb(0, 0, 0)"

	try:
		hospital_address_font_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-10", DATAMODE="A")
		if hospital_address_font_settings.KEY_VALUE:
			address_font_settings = json.loads(hospital_address_font_settings.KEY_VALUE)
			COMMON_INFO['HOSPITAL_ADDRESS_FONT_STYLE'] = address_font_settings["style"]
			COMMON_INFO['HOSPITAL_ADDRESS_FONT_SIZE'] = address_font_settings["size"]
			COMMON_INFO['HOSPITAL_ADDRESS_FONT_COLOR'] = address_font_settings["color"]
		else:
			raise Exception("Empty value")
	except:
		COMMON_INFO['HOSPITAL_ADDRESS_FONT_STYLE'] = "Times_New_Roman"
		COMMON_INFO['HOSPITAL_ADDRESS_FONT_SIZE'] = 14
		COMMON_INFO['HOSPITAL_ADDRESS_FONT_COLOR'] = "rgb(0, 0, 0)"

	try:
		hospital_number_font_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-11", DATAMODE="A")
		if hospital_number_font_settings.KEY_VALUE:
			number_font_settings = json.loads(hospital_number_font_settings.KEY_VALUE)
			COMMON_INFO['HOSPITAL_NUMBER_FONT_STYLE'] = number_font_settings["style"]
			COMMON_INFO['HOSPITAL_NUMBER_FONT_SIZE'] = number_font_settings["size"]
			COMMON_INFO['HOSPITAL_NUMBER_FONT_COLOR'] = number_font_settings["color"]
		else:
			raise Exception("Empty value")
	except:
		COMMON_INFO['HOSPITAL_NUMBER_FONT_STYLE'] = "Times_New_Roman"
		COMMON_INFO['HOSPITAL_NUMBER_FONT_SIZE'] = 14
		COMMON_INFO['HOSPITAL_NUMBER_FONT_COLOR'] = "rgb(0, 0, 0)"
	
	if request.user.is_authenticated():
		account_user = TX_ACCOUNTUSER.objects.filter(USER=request.user)
		if account_user:
			account_user = account_user.first()
		else:
			account_user = None
		if account_user:
			COMMON_INFO['ACCOUNTUSERROLE'] = account_user.ACCOUNTROLE.NAME
		else:
			COMMON_INFO['ACCOUNTUSERROLE'] = "MEMBER"

	return {'COMMON_INFO':COMMON_INFO}
