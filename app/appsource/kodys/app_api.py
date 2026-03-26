# -*- coding: utf-8 -*-

import datetime
import sys
import logging
import uuid
import subprocess
import json
import os
import glob
import urllib2
from shutil import copyfile
from datetime import timedelta
from pdf2image import convert_from_path
from PIL import Image
import base64
import cv2
import csv
# From Django
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.core.urlresolvers import reverse
# From Project App
from models import *
import app_logger as ulo
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.db.models import Q, Count, F
from cryptography.fernet import Fernet
#ECG
import heartpy as hp
import numpy as np
import pyhrv.time_domain as td
import pyhrv.frequency_domain as fd
from matplotlib import pyplot as plt
from scipy import signal
from scipy.integrate import trapz
import bwr
import qrs_detector as qrs_detect

logger = logging.getLogger(settings.LOGGER_FILE_NAME)

def user_signin(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	validation_error = None
	try:
		username = p_dict['username'].strip()
		password = p_dict['password'].strip()
		if username:
			user = User.objects.filter(email__iexact=username.lower()).first()
			if not user:
				user = User.objects.filter(username__iexact=username).first()
			if not user:
				if not password:
					result, msg = ulo._setmsg(success_msg, error_msg, False)
					validation_error = "Please enter your Password"
				else:
					result, msg = ulo._setmsg(success_msg, error_msg, False)
					validation_error =  "There is no account in our system for this Username"
			elif user and not user.is_active:
				result, msg = ulo._setmsg(success_msg, error_msg, False)
				validation_error = "Your account is inactive. Please contact administrator"
			elif password:
				if user and not user.check_password(password):
					result, msg = ulo._setmsg(success_msg, error_msg, False)
					validation_error =  "Invalid Password"
				else:
					#Authenticate the user
					user = authenticate(username=user.username, password=password)
					login(request, user)
					result, msg = ulo._setmsg(success_msg, error_msg, True)
			else:
				result, msg = ulo._setmsg(success_msg, error_msg, False)
				validation_error = "Please enter your Password"
		else:
			if password:
				validation_error = "Please enter your Username"
			else:
				validation_error = "Please enter your Username and Password"
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, validation_error


def user_signout(request):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	try:
		if request.user.is_authenticated():
			accountuser = TX_ACCOUNTUSER.objects.filter(USER=request.user).first()
			if accountuser:
				accountuser.LAST_LOGIN = request.user.last_login
				accountuser.save()
		logout(request)
		result, msg = ulo._setmsg(success_msg, error_msg, True)
	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def customer_support(request):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	user = None
	try:
		customer_support_technical = MA_APPLICATION_CONTACTS.objects.filter(POSITION="Technical Support", DATAMODE="A")
		customer_support_marketing = MA_APPLICATION_CONTACTS.objects.filter(POSITION="Marketing Support", DATAMODE="A")
		customer_support_product = MA_APPLICATION_CONTACTS.objects.filter(POSITION="Product Support", DATAMODE="A")
		customer_support = MA_APPLICATION_CONTACTS.objects.filter(POSITION="Customer Support Executives", DATAMODE="A")

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, customer_support, customer_support_technical, customer_support_marketing, customer_support_product


def home(request):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	doctors = dict()
	last_test_doctor = dict()
	examiner = dict()
	last_test_examiner = dict()
	try:
		kodys_apps = MA_MEDICALAPPS.objects.all().order_by('pk')
		for apps in kodys_apps:
			medical_test = TX_MEDICALTESTS.objects.filter(MEDICALTESTMASTER__MEDICAL_APP__CODE=apps.CODE, DATAMODE="A").first()
			if medical_test:
				if medical_test.DOCTOR:
					last_test_doctor[apps.CODE] = medical_test.DOCTOR.UID
				else:
					last_test_doctor[apps.CODE] = None
				if medical_test.EXAMINER:
					last_test_examiner[apps.CODE] = medical_test.EXAMINER.UID
				else:
					last_test_examiner[apps.CODE] = None
			else:
				last_test_doctor[apps.CODE] = None
				last_test_examiner[apps.CODE] = None
		result, msg = ulo._setmsg(success_msg, error_msg, True)
		specialization = MA_HCP_SPECIALIZATION.objects.filter(DATAMODE="A")
		for speciality in specialization:
			# doctor = TX_HCP.objects.filter(TYPE="DOCTOR", SPECIALIZATION=speciality, DATAMODE="A").order_by('pk')
			# doctors[speciality.MEDICAL_APP.CODE] = doctor
			doctor = TX_HCP_SPECIALIZATION.objects.filter(HCP__TYPE="DOCTOR", SPECIALIZATION=speciality, DATAMODE="A").order_by('pk')
			doctor_list = list()
			for hcp in doctor:
				doctor_list.append(hcp.HCP)
			doctors[speciality.MEDICAL_APP.CODE] = doctor_list
			# examiners = TX_HCP.objects.filter(TYPE="EXAMINER", SPECIALIZATION=speciality, DATAMODE="A").order_by('pk')
			# examiner[speciality.MEDICAL_APP.CODE] = examiners
			examiners = TX_HCP_SPECIALIZATION.objects.filter(HCP__TYPE="EXAMINER", SPECIALIZATION=speciality, DATAMODE="A").order_by('pk')
			examiner_list = list()
			for hcp in examiners:
				examiner_list.append(hcp.HCP)
			examiner[speciality.MEDICAL_APP.CODE] = examiner_list
			
		if "test_for" in request.session:
			request.session["test_for"] = ""
			request.session['test_completed_list'] = list()
			request.session['test_completed_list_length'] = 0

		result, msg = ulo._setmsg(success_msg, error_msg, True)
	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, kodys_apps, doctors, examiner, last_test_doctor,last_test_examiner


def service_email(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Send'
	error_msg ='ERROR'
	email_message = ""
	file_list = list()
	file_db_list = list()
	try:
		urllib2.urlopen('https://www.google.com/', timeout=1)
		from_email = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-01", DATAMODE="A").KEY_VALUE
		server = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-02", DATAMODE="A").KEY_VALUE
		port = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-03", DATAMODE="A").KEY_VALUE
		password = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-04", DATAMODE="A").KEY_VALUE
		to_email = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-05", DATAMODE="A").KEY_VALUE
		hospitalname = p_dict['hospitalname'].strip()
		doctorname = p_dict.get('doctorname','')
		if doctorname:
			doctorname = doctorname.strip()
		elif request.user.is_authenticated():
			if TX_HCP.objects.filter(ACCOUNTUSER__USER__username=request.user.username).exists():
				hcp = TX_HCP.objects.get(ACCOUNTUSER__USER__username=request.user.username)
				doctorname = "%s %s"%(hcp.PREFIX, hcp.NAME)

		mobileno = p_dict['mobileno'].strip()
		email = p_dict['email'].strip()
		productname = p_dict.get('productname','')
		if productname:
			productname = productname.strip()
		address = p_dict.get('address', '')
		if address:
			address = address.strip()
		prblmnature = p_dict.get('prblmnature','')
		if prblmnature:
			prblmnature = prblmnature.strip()
		attachment = request.FILES.getlist('attachment', [])
		if attachment:
			for attached_file in attachment:
				attached_file.name = attached_file.name.replace(" ", "_")
				with open('%s/service_request/%s'%(settings.MEDIA_DATA, attached_file), 'wb+') as destination:
					for chunk in attached_file.chunks():
						destination.write(chunk)

				filename="%sservice_request/%s" %(settings.DATA_URL,attached_file)
				filename_attach="%s/service_request/%s" %(settings.MEDIA_DATA,attached_file)
				file_list.append(filename_attach)
				file_db_list.append(filename)
		if not from_email:
			from_email = settings.DEFAULT_USER_EMAIL
			username = settings.EMAIL_HOST_USER
		else:
			username = from_email
		if not to_email:
			to_email = settings.SERVICE_EMAIL
		if not server:
			server = settings.EMAIL_HOST
		if not port:
			port = settings.EMAIL_PORT
		if not password:
			password = settings.EMAIL_HOST_PASSWORD
		if email:
			service_request = TX_APPLICATIONSERVICEREQUESTS()
			service_request.C_NAME = doctorname
			service_request.C_EMAIL = email.lower().strip()
			service_request.C_MOBILE_NUMBER = mobileno
			if TX_ACCOUNT.objects.filter(BUSINESS_NAME = hospitalname).exists():
				account = TX_ACCOUNT.objects.get(BUSINESS_NAME = hospitalname)
				service_request.ACCOUNT = account
				service_request.HOSPITAL_NAME = account.BUSINESS_NAME
			else:
				service_request.HOSPITAL_NAME = hospitalname
			if attachment:
				service_request.ATTACHMENT_FILE_PATH = file_db_list
			service_request.save()
			if productname:
				subject = "%s - %s"%(service_request.HOSPITAL_NAME, productname)
			else:
				subject = "%s"%(service_request.HOSPITAL_NAME)
			if hospitalname:
				email_message = "Hospital Name : %s<br />"%(hospitalname)
			if address:
				email_message = "%sHospital Address : %s<br />"%(email_message, address)
			if doctorname:
				email_message = "%sDoctor Name : %s<br />"%(email_message,service_request.C_NAME)
			if service_request.C_MOBILE_NUMBER:
				email_message = "%sDoctor Mobile Number : %s<br />"%(email_message, service_request.C_MOBILE_NUMBER)
			if service_request.C_EMAIL:
				email_message = "%sDoctor Email ID : %s<br />"%(email_message, service_request.C_EMAIL)
			if productname:
				email_message = "%sProduct Name : %s<br />"%(email_message, productname)
			if prblmnature:
				prblmnature = prblmnature.replace('\n','<br />')
				email_message = "%sNature of Problem :<br />&nbsp;&nbsp;%s"%(email_message, prblmnature)
			if attachment:
				email_message = "%s<br />Please find the attachment."%(email_message)

			service_request.SR_DETAILS = "%s<br />%s"%(subject, email_message)
			service_request.save()
			backend = EmailBackend(host="%s"%(server), port="%d"%(int(port)), username="%s"%(username), password="%s"%(password), use_tls=settings.EMAIL_USE_TLS)
			msg = EmailMessage(subject, email_message, from_email, [to_email], cc=[email.lower()], connection=backend)
			msg.content_subtype = "html"  
			if attachment:
				for filename_attach in file_list:
					msg.attach_file(filename_attach)
			try:
				msg.send()
				result, msg = ulo._setmsg(success_msg, error_msg, True)
			except Exception, e:
				result, msg = ulo._setmsg(success_msg, "Username and Password not accepted.Learn more at https://support.google.com/mail/?p=BadCredentials", False)
				logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
	except urllib2.URLError as err: 
		result, msg = ulo._setmsg(success_msg, "No Internet", False)
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, err))

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def about_content(request):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	user = None
	try:
		about_content = MA_APPLICATION.objects.get(DATAMODE="A")

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, about_content


def states(request):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	user = None
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, state


def hospital_profile(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	try:
		hospitalname = p_dict.get('hospitalname','')
		if hospitalname:
			hospitalname = hospitalname.strip()
		mobile_number = p_dict.get('mobileno','')
		if mobile_number:
			mobile_number = mobile_number.strip()
		phone_number = p_dict.get('phoneno','')
		if phone_number:
			phone_number = phone_number.strip()
		hospital_email = p_dict.get('hospital_email', '')
		if hospital_email:
			hospital_email = hospital_email.lower().strip()
		fax_number = p_dict.get('faxno','')
		if fax_number:
			fax_number = fax_number.strip()
		address1 = p_dict.get('address','')
		if address1:
			address1 = address1.strip()
			if address1[-1] == ",":
				address1 = address1[0:-1]
		address2 = p_dict.get('streetname','')
		if address2:
			address2 = address2.strip()
			if address2[-1] == ",":
				address2 = address2[0:-1]
		address3 = p_dict.get('areaname','')
		if address3:
			address3 = address3.strip()
			if address3[-1] == ",":
				address3 = address3[0:-1]
		city = p_dict.get('cityname','')
		if city:
			city = city.strip()
			if city[-1] == ",":
				city = city[0:-1]
		state = p_dict.get('statename','')
		if state:
			state = state.strip()
		pincode = p_dict.get('pincode','')
		if pincode:
			pincode = pincode.strip()
		logo = request.FILES.get('logo', '')
		username = p_dict.get('username', None)
		password = p_dict.get('password', None)
		email = p_dict.get('email', None)
		old_logo = p_dict.get('old_logo', None)
		if logo:
			if os.path.isfile('%s/hospital_profile/%s'%(settings.MEDIA_ROOT, logo)):
				filename="%shospital_profile/%s" %(settings.MEDIA_URL,logo)
			else:
				logo.name = logo.name.replace(" ", "_")
				with open('%s/hospital_profile/%s'%(settings.MEDIA_ROOT, logo), 'wb+') as destination:
					for chunk in logo.chunks():
						destination.write(chunk)

				filename="%shospital_profile/%s" %(settings.MEDIA_URL,logo)
		else:
			if old_logo:
				filename = "%shospital_profile/%s" %(settings.MEDIA_URL,old_logo)
			else:
				filename = ""
		if TX_ACCOUNT.objects.filter(DATAMODE="A").exists():
			account = TX_ACCOUNT.objects.get(DATAMODE="A")
		else:
			account = TX_ACCOUNT()
		account.BUSINESS_NAME = hospitalname
		# account.BUSINESS_SHORT_NAME = hospitalname
		# account.BUSINESS_SHORT_CODE = hospitalname
		if filename:
			account.BUSINESS_LOGO_PATH = filename
		else:
			account.BUSINESS_LOGO_PATH = ""
		account.PHONE_NUMBER = phone_number
		account.MOBILE_NUMBER = mobile_number
		account.FAX_NUMBER = fax_number
		account.ADDRESS_LINE_1 = address1
		account.ADDRESS_LINE_2 = address2
		account.ADDRESS_LINE_3 = address3
		account.EMAIL = hospital_email
		account.CITY = city
		if state:
			if MA_STATE.objects.filter(NAME=state).exists():
				state = MA_STATE.objects.get(NAME=state)
				account.STATE = state.NAME
				account.COUNTRY = state.COUNTRY.NAME
			else:
				account.STATE = state
		account.ZIPCODE = pincode
		account.save()
		if username and password:
			username=username.strip()
			password=password.strip()
			# email=email.strip()
			user = User.objects.get_or_create(username=username)
			first_name, last_name = parse_name(request, username)
			# user[0].email = email
			user[0].set_password(password)
			user[0].first_name = first_name
			user[0].last_name = last_name
			user[0].is_active = True
			user[0].save()
			if user[1]:
				if TX_ACCOUNTUSER.objects.filter(ACCOUNTROLE__NAME="MANAGER", DATAMODE="A").exists():
					accountusers = TX_ACCOUNTUSER.objects.filter(ACCOUNTROLE__NAME="MANAGER", DATAMODE="A")
					for account_user in accountusers:
						account_user.USER.is_active = False
						account_user.USER.save()
						account_user.DATAMODE = "D"
						account_user.save()
				accountuser = TX_ACCOUNTUSER()
				accountuser.UID = uuid.uuid4().hex[:30]
				accountuser.USER = user[0]
				account_role = MA_ACCOUNTROLE.objects.get(NAME="MANAGER")
				accountuser.ACCOUNTROLE = account_role
				accountuser.LAST_LOGIN = datetime.datetime.now()
				accountuser.save()
			elif TX_ACCOUNTUSER.objects.filter(USER=user[0], DATAMODE="D").exists() :
				accountusers = TX_ACCOUNTUSER.objects.filter(ACCOUNTROLE__NAME="MANAGER", DATAMODE="A")
				for account_user in accountusers:
					account_user.USER.is_active = False
					account_user.USER.save()
					account_user.DATAMODE = "D"
					account_user.save()
				new_account_user = TX_ACCOUNTUSER.objects.filter(USER=user[0], DATAMODE="D").first()
				new_account_user.DATAMODE = "A"
				new_account_user.save()
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def hospital_profile_details(request):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	user = None
	try:
		account = TX_ACCOUNT.objects.get(DATAMODE="A")
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, account


def doctors(request, speciality):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	hcp_user = list()
	try:
		specialization = MA_HCP_SPECIALIZATION.objects.filter(DATAMODE="A")
		if int(speciality) == 0:
			hcp_users = TX_HCP.objects.filter(DATAMODE="A").order_by('pk')
		else:
			hcp_speciality_users = TX_HCP_SPECIALIZATION.objects.filter(SPECIALIZATION__id=speciality, DATAMODE="A").order_by('pk')
			hcp_users = list()
			for hcp_special in hcp_speciality_users:
				hcp_users.append(hcp_special.HCP)
		for hcp in hcp_users:
			hcp_dict = dict()
			hcp_dict['FRIENDLY_UID'] = hcp.FRIENDLY_UID
			hcp_dict['NAME'] = hcp.NAME
			hcp_special = TX_HCP_SPECIALIZATION.objects.filter(HCP=hcp, DATAMODE="A")
			hcp_dict['SPECIALIZATION'] = list()
			for special in hcp_special:
				hcp_dict['SPECIALIZATION'].append(special.SPECIALIZATION.NAME)
			hcp_dict['MOBILE_NUMBER'] = hcp.MOBILE_NUMBER
			hcp_dict['GENDER'] = hcp.GENDER.capitalize()
			hcp_dict['TYPE'] = hcp.TYPE.capitalize()
			hcp_dict['PREFIX'] = hcp.PREFIX.capitalize()
			hcp_dict['UID'] = hcp.UID
			hcp_user.append(hcp_dict)

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, hcp_user, specialization


def patients(request):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	patient_list = list()
	try:
		patients = TX_PATIENTS.objects.filter(DATAMODE="A").order_by('pk')
		for patient in patients:
			patient_dict = dict()
			patient_dict['FRIENDLY_UID'] = patient.FRIENDLY_UID
			patient_dict['NAME'] = "%s %s %s"%(patient.NAME, patient.LAST_NAME, patient.SUR_NAME)
			patient_dict['PATIENT_MOBILE_NUMBER'] = patient.PATIENT_MOBILE_NUMBER
			patient_dict['POC_MOBILE_NUMBER'] = patient.POC_MOBILE_NUMBER
			patient_dict['GENDER'] = patient.GENDER.capitalize()
			patient_dict['PREFIX'] = patient.PREFIX.capitalize()
			patient_dict['UID'] = patient.UID
			patient_list.append(patient_dict)
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, patient_list


def parse_name(request, name):
    try:
        if name is not None:
            name=name.strip().split(' ',1)
            if len(name) > 1:
                first_name = name[0]
                last_name  = name[1]
            else:
                first_name = name[0]
                last_name  = ""
    except Exception,e:
        logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
    return first_name, last_name


def hcp_add(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	try:
		name = p_dict['name'].strip()
		first_name, last_name = parse_name(request, name)
		mobile_number = p_dict.get('mobile_number','')
		if mobile_number:
			mobile_number = mobile_number.strip()
		email = p_dict.get('email','')
		if email:
			email = email.lower().strip()
		gender = p_dict['gender'].strip()
		role = p_dict['role'].strip()
		username = p_dict.get('hcp_username', "")
		password = p_dict.get('hcp_password', "")
		if password:
			password = password.strip()
		prefix = p_dict.get('prefix', "")
		specialization = p_dict.get('specialization','')
		is_login_allowed = p_dict.get('is_login_allowed', False)
		if is_login_allowed == "on":
			is_login_allowed = True

		if username and password:
			user = User.objects.create_user(username=username, password=password)
			if email:
				user.email = email
			user.first_name = first_name
			user.last_name = last_name
			if not is_login_allowed:
				user.is_active = False
			user.save()
			accountuser = TX_ACCOUNTUSER()
			accountuser.UID = uuid.uuid4().hex[:8]
			accountuser.USER = user
			account_role = MA_ACCOUNTROLE.objects.get(NAME="MEMBER")
			accountuser.ACCOUNTROLE = account_role
			accountuser.LAST_LOGIN = datetime.datetime.now()
			accountuser.save()
		hcp = TX_HCP()
		hcp.UID = uuid.uuid4().hex[:8]
		if username and password:
			hcp.ACCOUNTUSER = accountuser
		hcp.NAME = name
		hcp.MOBILE_NUMBER = mobile_number
		hcp.GENDER = gender
		hcp.TYPE = role
		hcp.LOGIN_ALLOWED = is_login_allowed
		hcp.EMAIL = email
		hcp.PREFIX = prefix
		hcp.CREATED_BY = request.user
		hcp.UPDATED_BY = request.user
		hcp.save()
		if not hcp.FRIENDLY_UID:
			hcp.FRIENDLY_UID = "HCP-%04d"%(hcp.id)
			hcp.save()
		if specialization:
			specialization = specialization.replace("[","")
			specialization = specialization.replace("]","")
			specialization = specialization.split(",")
			for speciality in specialization:
				if speciality:
					speciality = speciality.replace(',','')
					specialization = MA_HCP_SPECIALIZATION.objects.get(NAME=speciality)
					hcp_speialization = TX_HCP_SPECIALIZATION()
					hcp_speialization.SPECIALIZATION = specialization
					hcp_speialization.HCP = hcp
					hcp_speialization.save()
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def hcp_edit(request, p_dict, hcp_uid):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	hcp_special_list = list()
	try:
		name = p_dict['name'].strip()
		first_name, last_name = parse_name(request, name)
		mobile_number = p_dict.get('mobile_number','')
		if mobile_number:
			mobile_number = mobile_number.strip()
		email = p_dict.get('email','')
		if email:
			email = email.lower().strip()
		gender = p_dict['gender'].strip()
		role = p_dict['role'].strip()
		username = p_dict.get('hcp_username', "")
		password = p_dict.get('hcp_password', "")
		prefix = p_dict.get('prefix', "")

		specialization = p_dict.get('specialization','')
		is_login_allowed = p_dict.get('is_login_allowed', False)
		if is_login_allowed == "on":
			is_login_allowed = True
		if hcp_uid:
			hcp = TX_HCP.objects.get(UID=hcp_uid, DATAMODE="A")
			if hcp.ACCOUNTUSER:
				user = User.objects.get(username=hcp.ACCOUNTUSER.USER.username)
				if is_login_allowed != hcp.LOGIN_ALLOWED:
					user.is_active = is_login_allowed
				if hcp.EMAIL != email:
					user.email = email
				if password:
					password = password.strip()
					if not user.check_password(password):
						user.set_password(password)
				user.save()

			else:
				if username and password:
					user = User.objects.create_user(username=username, password=password)
					if email:
						user.email = email
					user.first_name = first_name
					user.last_name = last_name
					user.save()
					accountuser = TX_ACCOUNTUSER()
					accountuser.UID = uuid.uuid4().hex[:8]
					accountuser.USER = user
					account_role = MA_ACCOUNTROLE.objects.get(NAME="MEMBER")
					accountuser.ACCOUNTROLE = account_role
					accountuser.LAST_LOGIN = datetime.datetime.now()
					accountuser.save()
					hcp.ACCOUNTUSER = accountuser
			hcp.NAME = name
			hcp.MOBILE_NUMBER = mobile_number
			hcp.GENDER = gender
			hcp.TYPE = role
			hcp.LOGIN_ALLOWED = is_login_allowed
			hcp.EMAIL = email
			hcp.PREFIX = prefix
			hcp.CREATED_BY = request.user
			hcp.UPDATED_BY = request.user
			hcp.save()
			if specialization:
				specialization = specialization.replace("[","")
				specialization = specialization.replace("]","")
				specialization = specialization.split(",")
				hcp_special = TX_HCP_SPECIALIZATION.objects.filter(HCP=hcp, DATAMODE="A")
				for special in hcp_special:
					hcp_special_list.append(special.id)
				for speciality in specialization:
					if speciality:
						speciality = speciality.replace(',','')
						if TX_HCP_SPECIALIZATION.objects.filter(HCP=hcp, SPECIALIZATION__NAME=speciality, DATAMODE="A").exists():
							hcp_speialization = TX_HCP_SPECIALIZATION.objects.filter(HCP=hcp, SPECIALIZATION__NAME=speciality, DATAMODE="A").first()
							if hcp_speialization.id in hcp_special_list:
								hcp_special_list.remove(hcp_speialization.id)
						elif TX_HCP_SPECIALIZATION.objects.filter(HCP=hcp, SPECIALIZATION__NAME=speciality, DATAMODE="D").exists():
							hcp_speialization = TX_HCP_SPECIALIZATION.objects.filter(HCP=hcp, SPECIALIZATION__NAME=speciality, DATAMODE="D").first()
							hcp_speialization.DATAMODE = "A"
							hcp_speialization.save()
						else:				
							specialization = MA_HCP_SPECIALIZATION.objects.get(NAME=speciality)
							hcp_speialization = TX_HCP_SPECIALIZATION()
							hcp_speialization.SPECIALIZATION = specialization
							hcp_speialization.HCP = hcp
							hcp_speialization.save()
				if hcp_special_list:
					for speciality in hcp_special_list:
						hcp_speialization = TX_HCP_SPECIALIZATION.objects.get(id=int(speciality), DATAMODE="A")
						hcp_speialization.DATAMODE = "D"
						hcp_speialization.save()
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def hcp_details(request, hcp_uid):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	hcp_details = dict()
	try:
		specialization = MA_HCP_SPECIALIZATION.objects.filter(DATAMODE="A")
		hcp = TX_HCP.objects.get(UID=hcp_uid, DATAMODE="A")
		hcp_details['EMAIL'] = hcp.EMAIL
		hcp_details['NAME'] = hcp.NAME
		hcp_details['SPECIALIZATION'] = list()
		hcp_special = TX_HCP_SPECIALIZATION.objects.filter(HCP=hcp, DATAMODE="A")
		for special in hcp_special:
			hcp_details['SPECIALIZATION'].append(special.SPECIALIZATION.NAME)
		hcp_details['MOBILE_NUMBER'] = hcp.MOBILE_NUMBER
		hcp_details['GENDER'] = hcp.GENDER
		hcp_details['TYPE'] = hcp.TYPE
		hcp_details['LOGIN_ALLOWED']= hcp.LOGIN_ALLOWED
		hcp_details['PREFIX']= hcp.PREFIX.capitalize()
		hcp_details['USERNAME']= hcp.ACCOUNTUSER.USER.username
		hcp_details['PASSWORD']= hcp.ACCOUNTUSER.USER.password
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, hcp_details, specialization


def hcp_specialization(request):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	specialization = list()
	try:
		specialization = MA_HCP_SPECIALIZATION.objects.filter(DATAMODE="A")
		if specialization:
			result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, specialization


def hcp_delete(request, hcp_uid):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	user = None
	try:
		if hcp_uid:
			hcp = TX_HCP.objects.get(UID=hcp_uid, DATAMODE="A")
			hcp.DATAMODE = "D"
			hcp.save()
			TX_HCP_SPECIALIZATION.objects.filter(HCP=hcp, DATAMODE="A").update(DATAMODE="D")
			accountuser = TX_ACCOUNTUSER.objects.get(UID=hcp.ACCOUNTUSER.UID)
			accountuser.DATAMODE="D"
			accountuser.save()
			user = User.objects.get(username=accountuser.USER.username)
			if user:
				new_user_name = "%s.%s"%(user.username, "deactivate")
				if User.objects.filter(username__contains=new_user_name).exists():
					user_old_name = User.objects.filter(username__contains=new_user_name).first()
					if user_old_name.username[-1].isdigit():
						count = int(user_old_name.username[-1]) +1
						user.username = "%s.%s%d"%(user.username, "deactivate", count)
					else:
						user.username = "%s.%s1"%(user.username, "deactivate")
				else:
					user.username = "%s.%s"%(user.username, "deactivate")
				user.is_active = False
				if user.email:
					new_user_email = "%s.%s"%(user.email, "deactivate")
					if User.objects.filter(email__contains=new_user_email).exists():
						user_old_email = User.objects.filter(email__contains=new_user_email).first()
						if user_old_email.email[-1].isdigit():
							count = int(user_old_email.email[-1]) +1
							user.email = "%s.%s%d"%(user.email, "deactivate", count)
						else:
							user.email = "%s.%s1"%(user.email, "deactivate")
					else:
						user.email = "%s.%s"%(user.email, "deactivate")

				user.save()
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def patients_add(request, p_dict, patient_uid=None):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	patients = None
	try:
		name = p_dict['name'].strip()
		patient_id = p_dict.get('patient_id', '')
		if patient_id:
			patient_id = patient_id.strip().upper()
		last_name = p_dict.get('last_name', '')
		if last_name:
			last_name = last_name.strip()
		sur_name = p_dict.get('sur_name', '')
		if sur_name:
			sur_name = sur_name.strip()
		mobile_number = p_dict.get('mobile_number','')
		if mobile_number:
			mobile_number = mobile_number.strip()
		email = p_dict.get('email','')
		if email:
			email = email.lower().strip()
		gender = p_dict['gender'].strip()
		prefix = p_dict['prefix'].strip()
		age = p_dict['age'].strip()
		poc_email = p_dict.get('poc_email','')
		if poc_email:
			poc_email = poc_email.lower().strip()
		poc_mobile_number = p_dict.get('poc_mobile_number','')
		if poc_mobile_number:
			poc_mobile_number = poc_mobile_number.strip()
		address1 = p_dict.get('address1', '')
		if address1:
			address1 = address1.strip()
			if address1[-1] == ",":
				address1 = address1[0:-1]
		address2 = p_dict.get('address2', '')
		if address2:
			address2 = address2.strip()
			if address2[-1] == ",":
				address2 = address2[0:-1]
		address3 = p_dict.get('address3','')
		if address3:
			address3 = address3.strip()
			if address3[-1] == ",":
				address3 = address3[0:-1]
		city = p_dict.get('city','')
		if city:
			city = city.strip()
			if city[-1] == ",":
				city = city[0:-1]
		state = p_dict.get('state', '')
		pincode = p_dict.get('pincode', '')
		height = p_dict.get('height','')
		weight = p_dict.get('weight', '')
		patient_prefix = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-07", DATAMODE="A")
		digits = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-08", DATAMODE="A").KEY_VALUE
			
		if patient_uid:
			patients = TX_PATIENTS.objects.get(UID=patient_uid, DATAMODE="A")
		else:
			patients = TX_PATIENTS()
			patients.UID = uuid.uuid4().hex[:8]
		patients.NAME = name
		patients.LAST_NAME = last_name
		patients.SUR_NAME = sur_name
		patients.PREFIX = prefix
		patients.PATIENT_MOBILE_NUMBER = mobile_number
		patients.POC_MOBILE_NUMBER = poc_mobile_number
		patients.GENDER = gender
		patients.AGE = age
		patients.PATIENT_EMAIL = email
		patients.POC_EMAIL = poc_email
		patients.USER = request.user
		patients.ADDRESS_LINE_1 = address1
		patients.ADDRESS_LINE_2 = address2
		patients.ADDRESS_LINE_3 = address3
		patients.CITY = city
		patients.HEIGHT = height
		patients.WEIGHT = weight
		if state:
			state = MA_STATE.objects.get(NAME=state)
			patients.STATE = state
			patients.COUNTRY = state.COUNTRY
		else:
			patients.STATE = None
			patients.COUNTRY = None
		patients.ZIPCODE = pincode
		patients.CREATED_BY = request.user
		patients.UPDATED_BY = request.user
		patients.save()
		
		if not patients.FRIENDLY_UID:
			if patient_id:
				patients.FRIENDLY_UID = patient_id.strip().upper()
				length = 0
				for digit_length in patient_id:
					if digit_length.isdigit():
						length = length + 1
				patients.PREFIX_DIGITS_LENGTH = int(length)
				patients.save()
			else:
				if patient_prefix.KEY_VALUE and digits:
					new_prefix = "%s%s"%(patient_prefix.KEY_VALUE, str(1).zfill(int(digits)))
					if TX_PATIENTS.objects.filter(FRIENDLY_UID=new_prefix).exists():
						exist_patient = TX_PATIENTS.objects.filter(FRIENDLY_UID__icontains=patient_prefix.KEY_VALUE, PREFIX_DIGITS_LENGTH=int(digits)).first()
						prefix_length = exist_patient.FRIENDLY_UID.replace("%s"%(patient_prefix.KEY_VALUE),"")
						if int(len(prefix_length)) == int(digits):
							prefix_length = prefix_length.replace("0", "")
							new_prefix = "%s%s"%(patient_prefix.KEY_VALUE, str(int(prefix_length)+1).zfill(int(digits)))
					else:
						new_prefix = "%s%s"%(patient_prefix.KEY_VALUE, str(1).zfill(int(digits)))
					
					patients.FRIENDLY_UID = new_prefix
					patients.PREFIX_DIGITS_LENGTH = int(digits)
					patients.save()
				else:
					new_prefix = "%s%s"%("PAT", str(1).zfill(4))
					if TX_PATIENTS.objects.filter(FRIENDLY_UID=new_prefix).exists():
						exist_patient = TX_PATIENTS.objects.filter(FRIENDLY_UID__icontains="PAT", PREFIX_DIGITS_LENGTH=int(4)).first()
						prefix_length = exist_patient.FRIENDLY_UID.replace("%s"%("PAT"),"")
						if int(len(prefix_length)) == int(4):
							prefix_length = prefix_length.replace("0", "")
							new_prefix = "%s%s"%("PAT", str(int(prefix_length)+1).zfill(int(4)))
					patients.FRIENDLY_UID = new_prefix
					patients.PREFIX_DIGITS_LENGTH = int(4)
					patients.save()
			result, msg = ulo._setmsg(success_msg, error_msg, True)

		elif patient_id:
			if patients.FRIENDLY_UID.upper() != patient_id.upper():
				patients.FRIENDLY_UID = patient_id.strip().upper()
				length = 0
				for digit_length in patient_id:
					if digit_length.isdigit():
						length = length + 1
				patients.PREFIX_DIGITS_LENGTH = int(length)
				patients.save()
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, patients


def patients_details(request, patient_uid):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	patients_details = dict()
	try:
		patients = TX_PATIENTS.objects.get(UID=patient_uid, DATAMODE="A")
		patients_details['NAME'] = patients.NAME
		patients_details['FRIENDLY_UID'] = patients.FRIENDLY_UID
		patients_details['LAST_NAME'] = patients.LAST_NAME
		patients_details['SUR_NAME'] = patients.SUR_NAME
		patients_details['PATIENT_MOBILE_NUMBER'] = patients.PATIENT_MOBILE_NUMBER
		patients_details['PATIENT_EMAIL'] = patients.PATIENT_EMAIL
		patients_details['PREFIX'] = patients.PREFIX.capitalize()
		patients_details['GENDER'] = patients.GENDER
		patients_details['AGE'] = patients.AGE
		patients_details['POC_MOBILE_NUMBER']= patients.POC_MOBILE_NUMBER
		patients_details['POC_EMAIL']= patients.POC_EMAIL
		patients_details['ADDRESS_LINE_1']= patients.ADDRESS_LINE_1
		patients_details['ADDRESS_LINE_2']= patients.ADDRESS_LINE_2
		patients_details['ADDRESS_LINE_3']= patients.ADDRESS_LINE_3
		patients_details['CITY']= patients.CITY
		patients_details['STATE']= patients.STATE
		patients_details['COUNTRY']= patients.COUNTRY
		patients_details['HEIGHT']= patients.HEIGHT
		patients_details['WEIGHT']= patients.WEIGHT
		patients_details['ZIPCODE']= patients.ZIPCODE
		state = MA_STATE.objects.filter(DATAMODE="A")

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, patients_details, state


def patients_delete(request, patients_uid):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	user = None
	try:
		if patients_uid:
			patients = TX_PATIENTS.objects.get(UID=patients_uid, DATAMODE="A")
			patients.DATAMODE = "D"
			patients.save()
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg	


def reports(request, speciality, duration):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	reports_list = list()
	orginal_start_date = ""
	orginal_end_date = ""
	try:
		accountuser = TX_ACCOUNTUSER.objects.get(USER=request.user)
		specialization = MA_MEDICALAPPS.objects.exclude(id=8).filter(DATAMODE="A")
		if speciality == "All":
			if duration:
				start_date, end_date = duration.split("_")
				start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
				end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
				orginal_start_date = start_date
				orginal_end_date = end_date
				if end_date.date() == datetime.datetime.now().date():
					end_date = end_date + timedelta(days=1)
				elif start_date == end_date:
					end_date = end_date + timedelta(days=1)
				if str(accountuser.ACCOUNTROLE) == "MEMBER":
					reports = TX_MEDICALTESTREPORTS.objects.filter(REPORTED_ON__range=[start_date.date(), end_date.date()], DATAMODE="A", CREATED_BY=accountuser.USER).order_by('-REPORTED_ON')
				else:
					reports = TX_MEDICALTESTREPORTS.objects.filter(REPORTED_ON__range=[start_date.date(), end_date.date()], DATAMODE="A").order_by('-REPORTED_ON')
			else:
				start_date = datetime.datetime.now() - timedelta(days=6)
				end_date = datetime.datetime.now() + timedelta(days=1)
				orginal_start_date = start_date
				orginal_end_date = datetime.datetime.now()
				if str(accountuser.ACCOUNTROLE) == "MEMBER":
					reports = TX_MEDICALTESTREPORTS.objects.filter(DATAMODE="A", REPORTED_ON__range=[start_date.date(), end_date.date()], CREATED_BY=accountuser.USER).order_by('-REPORTED_ON')
				else:
					reports = TX_MEDICALTESTREPORTS.objects.filter(DATAMODE="A", REPORTED_ON__range=[start_date.date(), end_date.date()]).order_by('-REPORTED_ON')
		else:
			if duration:
				start_date, end_date = duration.split("_")
				start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
				end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
				orginal_start_date = start_date
				orginal_end_date = end_date
				if end_date.date() == datetime.datetime.now().date():
					end_date = end_date + timedelta(days=1)
				elif start_date == end_date:
					end_date = end_date + timedelta(days=1)
				if str(accountuser.ACCOUNTROLE) == "MEMBER":
					reports = TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__MEDICALTESTMASTER__MEDICAL_APP__CODE=speciality, REPORTED_ON__range=[start_date.date(), end_date.date()], DATAMODE="A", CREATED_BY=accountuser.USER).order_by('-REPORTED_ON')
				else:
					reports = TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__MEDICALTESTMASTER__MEDICAL_APP__CODE=speciality, REPORTED_ON__range=[start_date.date(), end_date.date()], DATAMODE="A").order_by('-REPORTED_ON')
			else:
				start_date = datetime.datetime.now() - timedelta(days=6)
				end_date = datetime.datetime.now() + timedelta(days=1)
				orginal_end_date = datetime.datetime.now()
				orginal_start_date = start_date
				if str(accountuser.ACCOUNTROLE) == "MEMBER":
					reports = TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__MEDICALTESTMASTER__MEDICAL_APP__CODE=speciality, REPORTED_ON__range=[start_date.date(), end_date.date()], DATAMODE="A", CREATED_BY=accountuser.USER).order_by('-REPORTED_ON')
				else:
					reports = TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__MEDICALTESTMASTER__MEDICAL_APP__CODE=speciality, REPORTED_ON__range=[start_date.date(), end_date.date()], DATAMODE="A").order_by('-REPORTED_ON')

		# 	reports = TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__MEDICALTESTMASTER__MEDICAL_APP__CODE=speciality, DATAMODE="A").order_by('pk')
		for report in reports:
			report_dict = dict()
			report_dict['REPORTED_ON'] = report.REPORTED_ON.strftime("%d/%m/%Y %I:%M %p")
			report_dict['PATIENT_UID'] = report.MEDICALTEST.PATIENT.FRIENDLY_UID
			report_dict['PATIENT_NAME'] = "%s %s %s"%(report.MEDICALTEST.PATIENT.NAME, report.MEDICALTEST.PATIENT.LAST_NAME, report.MEDICALTEST.PATIENT.SUR_NAME)
			report_dict['PATIENT_PREFIX'] = report.MEDICALTEST.PATIENT.PREFIX.capitalize()
			if report.MEDICALTEST.DOCTOR:
				report_dict['DOCTOR_NAME'] = report.MEDICALTEST.DOCTOR.NAME
				report_dict['DOCTOR_PREFIX'] = report.MEDICALTEST.DOCTOR.PREFIX.capitalize()
				report_dict['DOCTOR_ID'] = report.MEDICALTEST.DOCTOR.UID
			else:
				report_dict['DOCTOR_NAME'] = ""
				report_dict['DOCTOR_PREFIX'] = ""
				report_dict['DOCTOR_ID'] = "no_uid"

			report_dict['TEST_STATUS'] = report.TEST_STATUS
			if report.MEDICALTEST.EXAMINER:
				report_dict['EXAMINER_NAME'] = report.MEDICALTEST.EXAMINER.NAME
				report_dict['EXAMINER_PREFIX'] = report.MEDICALTEST.EXAMINER.PREFIX.capitalize()
				report_dict['EXAMINER_ID'] = report.MEDICALTEST.EXAMINER.UID
			else:
				report_dict['EXAMINER_NAME'] = ""
				report_dict['EXAMINER_PREFIX'] = ""
				report_dict['EXAMINER_ID'] = "no_uid"
			if report.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE and report.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE.lower() == "hand":
				report_dict['MEDICALTEST'] = "%s - %s"%(report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.APP_NAME, report.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE)
			elif report.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE and report.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE.lower() == "other":
				report_dict['MEDICALTEST'] = "%s - %s"%(report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.APP_NAME, report.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE)
			else:
				if report.TEST_TYPE and report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.CODE == "APP-01":
					if report.MEDICALTEST.MEDICALTESTMASTER.CODE == "TM-01":
						report_dict['MEDICALTEST'] = "%s - %s"%(report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.APP_NAME, report.TEST_TYPE)
					else:
						report_dict['MEDICALTEST'] = "%s - %s"%(report.MEDICALTEST.MEDICALTESTMASTER.TEST_NAME, report.TEST_TYPE.replace("_", " "))
				elif report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.CODE == "APP-07":
					if report.TEST_TYPE == "All_test":
						report_dict['MEDICALTEST'] = "%s - All"%(report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.APP_NAME.replace('Test', '').strip())
					elif report.TEST_TYPE == "hrv_test":
						report_dict['MEDICALTEST'] = "%s - Hrv"%(report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.APP_NAME.replace('Test', '').strip())
					else:
						report_dict['MEDICALTEST'] = "%s - Parasympathetic"%(report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.APP_NAME.replace('Test', '').strip())
				elif report.TEST_TYPE:
					report_dict['MEDICALTEST'] = "%s - %s - %s"%(report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.APP_NAME, report.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE, report.TEST_TYPE)
				else:
					report_dict['MEDICALTEST'] = "%s - %s"%(report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.APP_NAME, report.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE)
			if report.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE:
				report_dict['TEST_TYPE'] = report.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE.lower()
			# elif report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.CODE == "APP-07":
			# 	report_dict['TEST_TYPE'] = report.TEST_TYPE
			else:
				report_dict['TEST_TYPE'] = ""
			TEST_CODE = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=report.MEDICALTEST.FRIENDLY_UID, DATAMODE="A").first()
			report_dict['TEST_CODE'] = TEST_CODE.MEDICALTESTMASTER.CODE
			report_dict['TEST_ENTRY'] = report.MEDICALTEST.FRIENDLY_UID
			report_dict['MEDICALTEST_FRIENDLY_UID'] = report.MEDICALTEST.FRIENDLY_UID
			report_dict['REPORT_UID'] = report.MEDICALTEST.FRIENDLY_UID
			report_dict['PATIENT_ID'] = report.MEDICALTEST.PATIENT.UID
			report_dict['APP_CODE'] = report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.CODE
			report_dict['CREATED_BY'] = "%s"%(report.CREATED_BY.username)
			reports_list.append(report_dict)
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, reports_list, specialization, orginal_start_date, orginal_end_date


def report_view(request, test_entry_code):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	report = dict()
	REPORT_PATH = None
	try:
		reports = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=test_entry_code, DATAMODE="A")
		report["APP_CODE"] = reports.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.CODE
		report["TEST_CODE"] = reports.MEDICALTEST.MEDICALTESTMASTER.CODE
		report["reports"] = reports
		if reports.IMPRESSION_NOTES:
			try:
				if reports.TEST_TYPE == "All_test":
					report["test_impression"] = json.loads(reports.IMPRESSION_NOTES)
				else:
					report["test_impression"] = reports.IMPRESSION_NOTES
			except Exception:
				report["test_impression"] = reports.IMPRESSION_NOTES
		else:
			report["test_impression"] = ""
		
		if reports.TEST_RESULT:
			try:
				report["report_result"] = json.loads(reports.TEST_RESULT)
			except Exception:
				report["report_result"] = {}
		else:
			report["report_result"] = {}

		medical_test = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry_code, DATAMODE="A").order_by('pk')
		if medical_test:
			# if medical_test[0].MEDICALTESTMASTER.MEDICAL_APP.CODE == "APP-04":
			if medical_test[0].MEDICALTESTMASTER.CODE == "TM-07":
				report["medical_test_organ_type"] = medical_test[0].MEDICALTESTMASTER.ORGAN_TYPE
				if len(medical_test) == 4:
					report["medical_test_type"] = "All"
				else:
					report["medical_test_type"] = "Warm"
			elif medical_test[0].MEDICALTESTMASTER.CODE == "TM-11":
				report["medical_test_organ_type"] = medical_test[0].MEDICALTESTMASTER.ORGAN_TYPE
				report["medical_test_type"] = "Warm"
			elif medical_test[0].MEDICALTESTMASTER.CODE == "TM-16":
				report["medical_test_organ_type"] = medical_test[0].MEDICALTESTMASTER.ORGAN_TYPE
				report["medical_test_type"] = "Warm"
			else:
				report["medical_test_organ_type"] = medical_test[0].MEDICALTESTMASTER.ORGAN_TYPE
				report["medical_test_type"] = ""

			for medical_test_value in medical_test:
				tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
				report[medical_test_value.MEDICALTESTMASTER.CODE.replace("-","")] = tx_test_entries
				try:
					if medical_test[0].MEDICALTESTMASTER.MEDICAL_APP.CODE != "APP-07":
						medical_test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_value.MEDICALTESTMASTER.CODE, DATAMODE="A")
						report["medical_test"] = medical_test_value
						if medical_test_interpertation.MEDICALTESTMASTER.CODE == "TM-13":
							for key, value in medical_test_interpertation.RANGES.iteritems():
								report[str(key.replace(" ", "_"))] = [str(key), value]
						else:
							report["medical_test_interpertation"] = medical_test_interpertation
					elif medical_test[0].MEDICALTESTMASTER.MEDICAL_APP.CODE == "APP-07":
						if medical_test_value.MEDICALTESTMASTER.CODE != "TM-25": 
							try:
								# Safe access to raw data entry
								raw_data_entry = report[medical_test_value.MEDICALTESTMASTER.CODE.replace("-","")]
								if len(raw_data_entry) > 2:
									raw_data = (raw_data_entry[2].KEY_VALUE).replace(" ","")
									raw_data = raw_data.split(",")
								else:
									raw_data = []
							except:
								raw_data = []

							# First, design the Notch filter for 50Hz (Power Line Interference)
							fs = 250.0 
							f0 = 50.0  
							Q = 30.0   
							b_notch, a_notch = signal.iirnotch(f0, Q, fs)

							# Second, design the Butterworth bandpass filter (5-15 Hz)
							lowcut = 5.0
							highcut = 15.0
							nyq = 0.5 * fs
							low = lowcut / nyq
							high = highcut / nyq
							B, A = signal.butter(2, [low, high], btype='band')

							data_list = list()
							for data in raw_data:
								if data:
									data_list.append(int(data))

							# Apply filters
							notched_data = signal.filtfilt(b_notch, a_notch, data_list)
							smooth_data_list = signal.filtfilt(B, A, notched_data)
							(baseline, ecg_out) = bwr.bwr(smooth_data_list)
							ecg_out_string = ""
							if len(ecg_out) >= 15000:
								for i in ecg_out[0:15000]:
									ecg_out_string += str(i+100)+","
							else:
								for i in ecg_out:
									ecg_out_string += str(i+100)+","
							report[medical_test_value.MEDICALTESTMASTER.CODE.replace("-","")+"_processed_data"] = ecg_out_string
						if medical_test_value.MEDICALTESTMASTER.CODE == "TM-21":
							raw_data = (report[medical_test_value.MEDICALTESTMASTER.CODE.replace("-","")][6].KEY_VALUE).replace(" ","")
							raw_data = raw_data.split(",")
							# First, design the Notch filter for 50Hz
							fs = 250.0 
							f0 = 50.0  
							Q = 30.0   
							b_notch, a_notch = signal.iirnotch(f0, Q, fs)

							# Second, design the Butterworth bandpass filter (5-15 Hz)
							lowcut = 5.0
							highcut = 15.0
							nyq = 0.5 * fs
							low = lowcut / nyq
							high = highcut / nyq
							B, A = signal.butter(2, [low, high], btype='band')

							data_list = list()
							for data in raw_data:
								if data:
									data_list.append(int(data))

							# Apply filters
							notched_data = signal.filtfilt(b_notch, a_notch, data_list)
							smooth_data_list = signal.filtfilt(B, A, notched_data)
							(baseline, ecg_out) = bwr.bwr(smooth_data_list)
							ecg_out_string = ""
							if len(ecg_out) >= 15000:
								for i in ecg_out[0:15000]:
									ecg_out_string += str(i+100)+","
							else:
								for i in ecg_out:
									ecg_out_string += str(i+100)+","
							report[medical_test_value.MEDICALTESTMASTER.CODE.replace("-","")+"_processed_data"] = ecg_out_string
							fs = 250.0
							high = highcut / nyq
							B, A = signal.butter(2, [low, high], btype='band')

							data_list = list()
							for data in raw_data:
								if data:
									data_list.append(int(data))

							# Apply filters
							notched_data = signal.filtfilt(b_notch, a_notch, data_list)
							smooth_data_list = signal.filtfilt(B, A, notched_data)
							(baseline, ecg_out) = bwr.bwr(smooth_data_list)
							ecg_out_string = ""
							if len(ecg_out) >= 15000:
								for i in ecg_out[0:15000]:
									ecg_out_string += str(i+100)+","
							else:
								for i in ecg_out:
									ecg_out_string += str(i+100)+","
							report[medical_test_value.MEDICALTESTMASTER.CODE.replace("-","")+"_standing_processed_data"] = ecg_out_string
						report["medical_test"] = medical_test_value
						interpertation_dict = dict()
						for interpertation in medical_test:
							if interpertation.MEDICALTESTMASTER.CODE != "TM-25":
								test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=interpertation.MEDICALTESTMASTER.CODE, DATAMODE="A")
								interpertation_dict[interpertation.MEDICALTESTMASTER.CODE.replace("-","")] = test_interpertation.RANGES
						report["medical_test_interpertation"] = interpertation_dict
				except Exception,e:
					print(e)
		if DOPPLER_GRAPHICAL_PDF.objects.filter(TEST_REPORT__id=reports.id).exists():
			dopplerpdf = DOPPLER_GRAPHICAL_PDF.objects.get(TEST_REPORT__id=reports.id)
			report["doppler_pdf_json"] = json.loads(dopplerpdf.BASE_64_IMAGES)

			# test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry_code, DATAMODE="A")

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, report


def app_configuration(request):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	app_config_dict = dict()
	try:
		if TX_ACCOUNT.objects.filter(DATAMODE="A").exists():
			account = TX_ACCOUNT.objects.get(DATAMODE="A")
			if TX_ACCOUNTLICENSE.objects.filter(ACCOUNT__BUSINESS_NAME=account.BUSINESS_NAME, DATAMODE="A").exists():
				license = TX_ACCOUNTLICENSE.objects.get(ACCOUNT__BUSINESS_NAME=account.BUSINESS_NAME, DATAMODE="A")
			else:
				license = ""
			if license:
				app_config_dict["license"] = license
			else:
				app_config_dict["license"] = ""
		else:
			app_config_dict["license"] = ""

		if TX_DATABASEBACKUPLOGS.objects.filter(DATAMODE="A").exists():
			backup = TX_DATABASEBACKUPLOGS.objects.filter(DATAMODE="A").first()
			app_config_dict['backup'] = backup.CREATED_ON.strftime("%B %d, %Y at %I:%M %p")
		else:
			app_config_dict['backup'] = "No Backup for Database"

		app_config_details = MA_APPLICATION_SETTINGS.objects.filter(DATAMODE="A").order_by('pk')
		for app_details in app_config_details:
			if app_details.KEY_VALUE:
				app_details.KEY_NAME = app_details.KEY_NAME.replace(" ", "_").lower()
				if app_details.KEY_NAME not in app_config_dict.keys():
					app_config_dict[app_details.KEY_NAME] = dict()
					if app_details.KEY_CODE == 'SET-09' or app_details.KEY_CODE == 'SET-10' or app_details.KEY_CODE == 'SET-11':
						app_config_dict[app_details.KEY_NAME] = (json.loads(app_details.KEY_VALUE), app_details.KEY_CODE)
					else:
						app_config_dict[app_details.KEY_NAME] = (app_details.KEY_VALUE, app_details.KEY_CODE)
				else:
					if app_details.KEY_CODE == 'SET-09' or app_details.KEY_CODE == 'SET-10' or app_details.KEY_CODE == 'SET-11':
						app_config_dict[app_details.KEY_NAME] = (json.loads(app_details.KEY_VALUE), app_details.KEY_CODE)
					else:
						app_config_dict[app_details.KEY_NAME] = (app_details.KEY_VALUE, app_details.KEY_CODE)

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, app_config_dict


def manuals(request, category):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	manuals_list = list()
	try:
		manuals_list = MA_APPLICATION_MANUALS.objects.filter(CATEGORY=category, DATAMODE="A").order_by('pk')
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, manuals_list	


def manuals_view(request, manuals_code):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	manuals = dict()
	MANUAL_PATH = None
	try:
		manuals = MA_APPLICATION_MANUALS.objects.get(id=manuals_code, DATAMODE="A")
		if manuals:
			pass
		else:
			MANUAL_PATH = "Manual is not available."
		
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, manuals, MANUAL_PATH


def database_backup(request):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	manuals = dict()
	MANUAL_PATH = None
	try:
		urllib2.urlopen('https://www.google.com/', timeout=1)
		from_email = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-01", DATAMODE="A").KEY_VALUE
		server = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-02", DATAMODE="A").KEY_VALUE
		port = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-03", DATAMODE="A").KEY_VALUE
		password = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-04", DATAMODE="A").KEY_VALUE
		to_email = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-05", DATAMODE="A").KEY_VALUE
		if not from_email:
			from_email = settings.DEFAULT_USER_EMAIL
			username = settings.DEFAULT_USER_EMAIL
		else:
			username = from_email
		if not to_email:
			to_email = settings.SERVICE_EMAIL
		if not server:
			server = settings.EMAIL_HOST
		if not port:
			port = settings.EMAIL_PORT
		if not password:
			password = settings.EMAIL_HOST_PASSWORD
		destination_file = "%s/database_backup/db_%s.json"%(settings.MEDIA_DATA, datetime.datetime.now().strftime("%d_%m_%Y_%I_%M"))
		destination_filename = destination_file.replace("%s/"%(settings.MEDIA_DATA), settings.DATA_URL)
		try:
			process = subprocess.Popen("python manage.py dumpdata > %s"%(destination_file), shell=True, stdout=subprocess.PIPE)
			process.wait()

			database = TX_DATABASEBACKUPLOGS()
			database.TYPE = "MANUAL"
			database.BACKUP_PATH = destination_filename
			database.CREATED_BY = request.user
			database.UPDATED_BY = request.user
			database.save()
			result, msg = ulo._setmsg(success_msg, error_msg, True)

			if TX_ACCOUNT.objects.filter(DATAMODE="A").exists():
				hospital_info = TX_ACCOUNT.objects.get(DATAMODE="A")
				message = "DB Backup from %s"%(hospital_info.BUSINESS_NAME)
				backend = EmailBackend(host="%s"%(server), port="%d"%(int(port)), username="%s"%(username), password="%s"%(password), use_tls=settings.EMAIL_USE_TLS)
				msg = EmailMessage("DB Backup", message, from_email, [to_email], connection=backend)
				msg.content_subtype = "html"  
				msg.attach_file(destination_file)
				try:
					msg.send()
					result, msg = ulo._setmsg(success_msg, error_msg, True)
				except Exception, e:
					result, msg = ulo._setmsg(success_msg, error_msg, True)
					result = "Error"
					logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))

		except Exception,e:
			logger.error(ulo.error_log(None, sys.exc_traceback.tb_lineno, e))
			result, msg = ulo._setmsg(success_msg, error_msg, False)
	except urllib2.URLError as err: 
		result, msg = ulo._setmsg(success_msg, err, False)
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, err))

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def migrate_app_database():
    result = False
    try:
        app_list = ["kodys"]
        for apps in app_list:
            apps = apps.replace(".","/")
            migration_path = os.path.join(settings.BASE_DIR, '%s/migrations'%(apps))
            for file in glob.glob(migration_path+"/0*.py"):
                os.remove(file)
        result = True
    except Exception,e:
       print('Error at %s:%s' %(sys.exc_traceback.tb_lineno,e))
    return result


def restore_database(request):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	manuals = dict()
	MANUAL_PATH = None
	try:
		source_file = request.FILES.get("backup_db_file", "")
		if source_file:
			src = "%s/initial_database/db.sqlite3"%(settings.MEDIA_DATA)
			dst = "%s/db.sqlite3"%(settings.BASE_DIR)
			os.remove("../db.sqlite3")
			migrate_app_database()
			copyfile(src, dst)
			source_file_path = "%s/database_backup/%s"%(settings.MEDIA_DATA, source_file)
			process = subprocess.Popen("python manage.py makemigrations", shell=True, stdout=subprocess.PIPE)
			process = subprocess.Popen("python manage.py migrate --run-syncdb", shell=True, stdout=subprocess.PIPE)
			process = subprocess.Popen("python manage.py loaddata %s"%(source_file_path), shell=True, stdout=subprocess.PIPE)
			process.wait()
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg

def app_license(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	try:
		if 'license' in p_dict and p_dict['license']:
			license_value = p_dict['license'].strip()
			license_file =request.FILES.get("license_file", "")
			if license_file:
				output_license_file = '%s_%s.kod' % ("license", datetime.datetime.now().strftime("%d_%m_%Y_%I_%M"))
				license_data = license_file.read()
				if os.path.isfile('%s/hospital_license/%s'%(settings.MEDIA_ROOT, license_file)):
					pass
				else:
					with open('%s/hospital_license/%s'%(settings.MEDIA_DATA, output_license_file), 'wb+') as destination:
						destination.write(license_data)
				try:
					license = Fernet(str(license_value))
					decrypted = license.decrypt(license_data)
					decrypted = json.loads(decrypted)
					if TX_ACCOUNT.objects.filter(BUSINESS_NAME=decrypted["hospital_name"].strip(), DATAMODE="A").exists():
						account = TX_ACCOUNT.objects.get(BUSINESS_NAME=decrypted["hospital_name"].strip(), DATAMODE="A")
					else:
						TX_ACCOUNT.objects.filter(DATAMODE="A").update(DATAMODE="D")
						account = TX_ACCOUNT()
					account.BUSINESS_NAME = decrypted["hospital_name"]
					account.PHONE_NUMBER = decrypted["phone_number"]
					account.MOBILE_NUMBER = decrypted["mobile"]
					account.ADDRESS_LINE_1 = decrypted["address"]
					street = decrypted.get("street","")
					if street:
						street = street.strip()
					account.ADDRESS_LINE_2 = street
					area = decrypted.get("area","")
					if area:
						area = area.strip()
					account.ADDRESS_LINE_3 = area
					if "email_id" in decrypted:
						account.EMAIL = decrypted["email_id"].lower()
					fax_number = decrypted.get('fax_number','')
					if fax_number:
						fax_number = fax_number.strip()
					account.FAX_NUMBER = fax_number
					if decrypted["state"]:
						if MA_STATE.objects.filter(NAME=decrypted["state"]).exists():
							state = MA_STATE.objects.get(NAME=decrypted["state"])
							account.STATE = state.NAME
							account.COUNTRY = state.COUNTRY.NAME
						else:
							account.STATE = decrypted["state"]
							if 'country' in decrypted:
								account.COUNTRY = decrypted["country"]
					city = decrypted.get("city","")
					if city:
						city = city.strip()
					account.CITY = city
					pincode = decrypted.get("pincode","")
					if pincode:
						pincode = pincode.strip()
					account.ZIPCODE = pincode
					account.save()
					if decrypted["TEST"]:
						MA_MEDICALAPPS.objects.exclude(CODE="APP-08").all().update(DATAMODE="D")
						for test in decrypted["TEST"]:
							medical_app = MA_MEDICALAPPS.objects.get(CODE=str(test))
							medical_app.DATAMODE = "A"
							medical_app.save()
					if TX_ACCOUNTLICENSE.objects.filter(DATAMODE="A").exists():
						TX_ACCOUNTLICENSE.objects.filter(DATAMODE="A").update(DATAMODE="D")

					license = TX_ACCOUNTLICENSE()
					license.ACCOUNT = account
					license.ACCOUNT_LICENSE_KEY = license_value
					license.ACCOUNT_LICENSE = output_license_file
					license.save()
				except Exception,e:
					result, msg = ulo._setmsg(success_msg, e, False)
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			result, msg = ulo._setmsg(success_msg, e, False)


	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg

def app_configuration_settings(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	try:
		if 'From' in p_dict and p_dict['From']:
			mail_value = p_dict['From'].lower().strip()
			mail_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_NAME="From", DATAMODE="A")
			mail_settings.KEY_VALUE = mail_value
			mail_settings.save()
		if 'Server' in p_dict and p_dict['Server']:
			mail_value = p_dict['Server'].strip()
			mail_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_NAME="Server", DATAMODE="A")
			mail_settings.KEY_VALUE = mail_value
			mail_settings.save()
		if 'Port' in p_dict and p_dict['Port']:
			mail_value = p_dict['Port'].strip()
			mail_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_NAME="Port", DATAMODE="A")
			mail_settings.KEY_VALUE = mail_value
			mail_settings.save()
		if 'Password' in p_dict and p_dict['Password']:
			mail_value = p_dict['Password'].strip()
			mail_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_NAME="Password", DATAMODE="A")
			mail_settings.KEY_VALUE = mail_value
			mail_settings.save()
		if 'Prefix' in p_dict:
			mail_value = p_dict['Prefix']
			if p_dict['Prefix']:
				mail_value = p_dict['Prefix'].strip()
			mail_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_NAME="Prefix", DATAMODE="A")
			mail_settings.KEY_VALUE = mail_value.upper()
			mail_settings.save()
		if 'Digits' in p_dict:
			mail_value = p_dict['Digits']
			if p_dict['Digits']:
				mail_value = p_dict['Digits'].strip()
			mail_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_NAME="Digits", DATAMODE="A")
			mail_settings.KEY_VALUE = mail_value
			mail_settings.save()
		if 'To' in p_dict and p_dict['To']:
			mail_value = p_dict['To'].lower().strip()
			mail_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_NAME="To", DATAMODE="A")
			mail_settings.KEY_VALUE = mail_value
			mail_settings.save()
		if 'font_hospname' in p_dict and p_dict['font_hospname']:
			font_hospname = p_dict['font_hospname'].strip()
			color_hospname = p_dict['color_hospname'].strip()
			size_hospname = p_dict['size_hospname'].strip()
			mail_value = dict()
			mail_value["style"] = font_hospname
			mail_value["color"] = color_hospname
			mail_value["size"] = size_hospname
			mail_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-09", DATAMODE="A")
			mail_settings.KEY_VALUE = json.dumps(mail_value)
			mail_settings.save()
		if 'font_hospaddr' in p_dict and p_dict['font_hospaddr']:
			font_hospaddr = p_dict['font_hospaddr'].strip()
			color_hospaddr = p_dict['color_hospaddr'].strip()
			size_hospaddr = p_dict['size_hospaddr'].strip()
			mail_value = dict()
			mail_value["style"] = font_hospaddr
			mail_value["color"] = color_hospaddr
			mail_value["size"] = size_hospaddr
			mail_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-10", DATAMODE="A")
			mail_settings.KEY_VALUE = json.dumps(mail_value)
			mail_settings.save()
		if 'font_hospphno' in p_dict and p_dict['font_hospphno']:
			font_hospphno = p_dict['font_hospphno'].strip()
			color_hospphno = p_dict['color_hospphno'].strip()
			size_hospphno = p_dict['size_hospphno'].strip()
			mail_value = dict()
			mail_value["style"] = font_hospphno
			mail_value["color"] = color_hospphno
			mail_value["size"] = size_hospphno
			mail_settings = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-11", DATAMODE="A")
			mail_settings.KEY_VALUE = json.dumps(mail_value)
			mail_settings.save()
		if 'is_report_header' in p_dict:
			if TX_ACCOUNT.objects.filter(DATAMODE="A").exists():
				account = TX_ACCOUNT.objects.get(DATAMODE="A")
				account.IS_REPORT_HEADER = p_dict['is_report_header']
				account.save()

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def search(request, search_key):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='No search results'
	patient_list = list()
	try:
		patients = TX_PATIENTS.objects.filter(
			Q(NAME__icontains=search_key) |
			Q(LAST_NAME__icontains=search_key) |
			Q(SUR_NAME__icontains=search_key) |
			Q(FRIENDLY_UID__icontains=search_key),
			DATAMODE="A"
		).order_by('pk')
		for patient in patients:
			patient_dict = dict()
			patient_dict['NAME'] = "%s %s %s (%s)"%(patient.NAME, patient.LAST_NAME, patient.SUR_NAME, patient.FRIENDLY_UID)
			patient_dict['FRIENDLY_UID'] = patient.FRIENDLY_UID
			patient_dict['GENDER'] = patient.GENDER.capitalize()
			patient_dict['AGE'] = patient.AGE
			patient_dict['UID'] = patient.UID
			patient_list.append(patient_dict)
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception, e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
	return result, msg, patient_list


def medical_test_entry(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	try:
		test_type = p_dict.get('test_type',None)
		test_for = p_dict.get('test_for',None)
		
		if test_type:
			request.session['test_type'] = test_type
		if test_for:
			request.session['test_for'] = test_for

		patient = p_dict['patient_uid'].strip()
		doctor = p_dict.get('doctor_uid', None)
		examiner = p_dict.get('examiner_uid', None)
		app_code = p_dict['app_code'].strip()
		test_code = p_dict['test_code'].strip()
		test_entry = p_dict.get('test_entry', None)
		kodys_apps = MA_MEDICALAPPS.objects.filter(CODE=app_code, DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=app_code, DATAMODE="A").last()
		if test_code:
			medical_test_type  = MA_MEDICALTESTMASTER.objects.filter(CODE=test_code, DATAMODE="A").first()
			test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=test_code, DATAMODE="A")
			normal = str(test_interpertation.RANGES['Normal'])
			abnormal = str(test_interpertation.RANGES['Abnormal'])
			normal = normal.split("-")
			if doctor.strip() != "no_uid":
				doctor = TX_HCP.objects.get(UID=doctor, DATAMODE="A")
			else:
				doctor = ""
			if examiner.strip() != "no_uid":
				examiner = TX_HCP.objects.get(UID=examiner, DATAMODE="A")
			else:
				examiner = ""
			patients = TX_PATIENTS.objects.get(UID=patient, DATAMODE="A")
			if test_entry and TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, MEDICALTESTMASTER__CODE=test_code).exists():
				medical_test_fields = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, MEDICALTEST__MEDICALTESTMASTER__CODE=test_code)
				for test_fields in medical_test_fields:
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_fields.KEY_VALUE = test_field_value
						if test_field_value.isalpha():
							test_fields.KEY_VALUE_STATUS = "Abnormal"
						elif float(test_field_value) >= float(normal[0]) and float(test_field_value) <= float(normal[1]):
							test_fields.KEY_VALUE_STATUS = "Normal"
						elif "<" in abnormal:
							abnormal_value = abnormal.replace("<", "")
							if float(test_field_value) < float(abnormal_value):
								test_fields.KEY_VALUE_STATUS = "Abnormal"
							else:
								test_fields.KEY_VALUE_STATUS = "Not_in_Range"
						elif ">" in abnormal:
							abnormal_value = abnormal.replace(">", "")
							if float(test_field_value) > float(abnormal_value):
								test_fields.KEY_VALUE_STATUS = "Abnormal"
							else:
								test_fields.KEY_VALUE_STATUS = "Not_in_Range"
					else:
						test_fields.KEY_VALUE = ""
						test_fields.KEY_VALUE_STATUS = "No_Data"
					# test_fields.KEY_VALUE = p_dict.get(test_fields.KEY_CODE, "").strip()
					test_fields.save()
				# medical_test = test_fields.MEDICALTEST
				medical_test = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, DATAMODE="A").first()
			
			else:
				medical_test = TX_MEDICALTESTS()
				medical_test.UID = uuid.uuid4().hex[:30]
				medical_test.MEDICALTESTMASTER = medical_test_type
				medical_test.PATIENT = patients
				medical_test.INTERPERTATION = test_interpertation.RANGES
				if doctor:
					medical_test.DOCTOR = doctor
				if examiner:
					medical_test.EXAMINER = examiner
				medical_test.REPORTED_ON = datetime.datetime.now()
				medical_test.save()
				if test_entry:
					test_entry = test_entry.strip()
					medical_test.FRIENDLY_UID = test_entry
				else:
					medical_test.FRIENDLY_UID = "TST-%08d"%(medical_test.id)
				medical_test.save() 

				medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A")
				for test_fields in medical_test_fields:
					test_entries = TX_MEDICALTESTENTRIES()
					test_entries.UID = uuid.uuid4().hex[:30]
					test_entries.MEDICALTEST = medical_test
					test_entries.MEDICALTESTFIELDS = test_fields
					test_entries.KEY_NAME = test_fields.KEY_NAME
					test_entries.KEY_CODE = test_fields.KEY_CODE
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_entries.KEY_VALUE = test_field_value
						if test_field_value.isalpha():
							test_entries.KEY_VALUE_STATUS = "Abnormal"
						elif float(test_field_value) >= float(normal[0]) and float(test_field_value) <= float(normal[1]):
							test_entries.KEY_VALUE_STATUS = "Normal"
						elif "<" in abnormal:
							abnormal_value = abnormal.replace("<", "")
							if float(test_field_value) < float(abnormal_value):
								test_entries.KEY_VALUE_STATUS = "Abnormal"
							else:
								test_entries.KEY_VALUE_STATUS = "Not_in_Range"
						elif ">" in abnormal:
							abnormal_value = abnormal.replace(">", "")
							if float(test_field_value) > float(abnormal_value):
								test_entries.KEY_VALUE_STATUS = "Abnormal"
							else:
								test_entries.KEY_VALUE_STATUS = "Not_in_Range"
					else:
						test_entries.KEY_VALUE = ""
						test_entries.KEY_VALUE_STATUS = "No_Data"
					test_entries.save()
				
			if TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A").exists():
				pass
			else:
				test_report = TX_MEDICALTESTREPORTS()
				test_report.UID = uuid.uuid4().hex[:30]
				# test_report.FRIENDLY_UID = uuid.uuid4().hex[:30]
				test_report.MEDICALTEST = medical_test
				test_report.TEMPERATURE_SCALE = "CELSIUS"
				test_report.REFERRED_BY = referred_by_medical_test_type.REFERRED_BY
				if test_for:
					test_report.TEST_TYPE = test_for
				else:
					test_report.TEST_TYPE = "Warm"
				test_report.REPORTED_ON = datetime.datetime.now()
				test_report.CREATED_BY = request.user
				test_report.UPDATED_BY = request.user
				test_report.save()
				test_report.FRIENDLY_UID = "REP-%08d"%(test_report.id)
				test_report.save()

				# Pre-calculate ECG results to solve report lag and apply algorithmic fixes
				try:
					processed_results = process_can_test_data(test_report)
					if processed_results:
						test_report.TEST_RESULT = json.dumps(processed_results)
						test_report.save()
				except Exception as e:
					print("Pre-calculation failed: ", e)
				
			if 'test_completed_list' in request.session:
				if test_code in request.session['test_completed_list']:
					pass
				else:
					request.session['test_completed_list'].append(test_code)
			else:
				request.session['test_completed_list'] = list()
				request.session['test_completed_list'].append(test_code)
			request.session['test_completed_list_length'] = len(request.session['test_completed_list'])
			medical_test_result['test_entry_id'] = medical_test.FRIENDLY_UID
			medical_test_result['current_test_code'] = medical_test.MEDICALTESTMASTER.CODE
	
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			medical_test_result['test_entry_id'] = None
			medical_test_result['current_test_code'] = None
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test_result


def test_impression(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	try:
		test_entry = p_dict.get('test_entry',None)
		notes = p_dict.get('notes',None)
		# test_result = p_dict.get('test_result',"")
		if test_entry and notes:
			medical_test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=test_entry, DATAMODE="A")
			if medical_test_report.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.CODE == "APP-07":
				if medical_test_report.TEST_TYPE == "All_test":
					medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, DATAMODE="A").first()
					if medical_tests.MEDICALTESTMASTER.CODE == "TM-24":
						comments = dict()
						comments['para'] = notes
						medical_test_report.IMPRESSION_NOTES = json.dumps(comments)
					elif medical_tests.MEDICALTESTMASTER.CODE == "TM-25" and medical_test_report.IMPRESSION_NOTES:
						comments = json.loads(medical_test_report.IMPRESSION_NOTES)
						comments["hrv"] = notes
						medical_test_report.IMPRESSION_NOTES = json.dumps(comments)
					elif medical_tests.MEDICALTESTMASTER.CODE == "TM-25":
						comments = dict()
						comments["hrv"] = notes
						medical_test_report.IMPRESSION_NOTES = json.dumps(comments)
				else:
					medical_test_report.IMPRESSION_NOTES = notes
			else:
				medical_test_report.IMPRESSION_NOTES = notes
			medical_test_report.save()
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def test_referred(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	try:
		referred = p_dict.getlist('referred[]',[])
		app_code = p_dict.get('app_code',"")
		temp_referred = ""
		for ref in referred:
			if ref:
				temp_referred = ref
		if app_code:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=app_code, DATAMODE="A").last()
			medical_test_type.REFERRED_BY = temp_referred
			medical_test_type.save()
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg



def thermocool_foot(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").last()
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").exists():
			device_details = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").first()
		else:
			device_details = dict()
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		medical_test['medical_device'] = medical_device
		medical_test['device_details'] = device_details
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		normal = str(test_interpertation.RANGES['Normal'])
		abnormal = str(test_interpertation.RANGES['Abnormal'])
		medical_test['normal'] = normal
		medical_test['abnormal'] = abnormal
		medical_test['test_completed_list'] = list()
		request.session['test_completed_list'] = list()
		if option['test_entry']:
			medical_test_type.REFERRED_BY = ""
			medical_test_type.save()
			request.session["referred"] = ""
			medical_test_completed_list = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A").order_by('pk')
			for completed_list in medical_test_completed_list:
				medical_test['test_completed_list'].append(completed_list.MEDICALTESTMASTER.CODE)
				if 'test_completed_list' in request.session:
					if completed_list.MEDICALTESTMASTER.CODE in request.session['test_completed_list']:
						pass
					else:
						request.session['test_completed_list'].append(completed_list.MEDICALTESTMASTER.CODE)
			request.session['test_completed_list_length'] = len(request.session['test_completed_list'])
			medical_test['test_completed_list_length'] = len(medical_test_completed_list)
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			request.session['test_type'] = medical_test_type.ORGAN_TYPE
			request.session['test_for'] = test_report.TEST_TYPE 
			medical_test['test_type'] = medical_test_type.ORGAN_TYPE 
			medical_test['test_for'] = test_report.TEST_TYPE 
		else:
			medical_test['test_completed_list_length'] = 0

		if option['test_code'] and option['test_entry']:
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			if request.session['test_type'] == "Foot" and request.session['test_for'] == "All" and len(request.session['test_completed_list']) == 4:
				medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				test_report.TEST_STATUS = "COMPLETED"
				test_report.save()
			elif request.session['test_type'] == "Foot" and request.session['test_for'] =="Warm" and len(request.session['test_completed_list'])==2:
				medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				test_report.TEST_STATUS = "COMPLETED"
				test_report.save()
			else:
				medical_tests = list()
			if medical_tests:
				hcp_test_values = dict()
				for medical_test_value in medical_tests:
					tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")

					right_hand_result, left_foot_result = "", ""
					right_avg = 0.0
					left_avg = 0.0
					right_count = 0
					left_count = 0
					for tx_test in tx_test_entries[0:6]:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							right_avg = right_avg + float(tx_test.KEY_VALUE)
							right_count = right_count +1
					for tx_test in tx_test_entries[8:14]:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							left_avg = left_avg + float(tx_test.KEY_VALUE)
							left_count = left_count +1
					medical_test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_value.MEDICALTESTMASTER.CODE, DATAMODE="A")
					normal = str(medical_test_interpertation.RANGES['Normal'])
					abnormal = str(medical_test_interpertation.RANGES['Abnormal'])
					hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE] = dict()
					normal = normal.split("-")
					if right_count != 0 and right_avg:
						right_avg = round(float(right_avg / right_count), 1)
					
						if float(right_avg) >= float(normal[0]) and float(right_avg) <= float(normal[1]):
							right_hand_result = "Normal"
						elif "<" in abnormal:
							abnormal_value = abnormal.replace("<", "")
							if float(right_avg) < float(abnormal_value):
								right_hand_result = "Abnormal"
							else:
								right_hand_result = "Not in Range"
						elif ">" in abnormal:
							abnormal_value = abnormal.replace(">", "")
							if float(right_avg) > float(abnormal_value):
								right_hand_result = "Abnormal"
							else:
								right_hand_result = "Not in Range"
						else:
							right_hand_result = "Not in Range"
						hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE]['right_foot_result'] = ["%.1f"%(right_avg), right_hand_result]
					else:
						hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE]['right_foot_result'] = ["No Data", ""]

					if left_count != 0 and left_avg:
						left_avg = round(float(left_avg / left_count), 1)
						if float(left_avg) >= float(normal[0]) and float(left_avg) <= float(normal[1]):
							left_foot_result = "Normal"
						elif "<" in abnormal:
							abnormal_value = abnormal.replace("<", "")
							if float(left_avg) < float(abnormal_value):
								left_foot_result = "Abnormal"
							else:
								left_foot_result = "Not in Range"
						elif ">" in abnormal:
							abnormal_value = abnormal.replace(">", "")
							if float(left_avg) > float(abnormal_value):
								left_foot_result = "Abnormal"
							else:
								left_foot_result = "Not in Range"
						else:
							left_foot_result = "Not in Range"
						hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE]['left_foot_result'] = ["%.1f"%(left_avg), left_foot_result]
					else:
						hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE]['left_foot_result'] = ["No Data", ""]

				medical_test["hcp_test_values"] = hcp_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(hcp_test_values)
				report.save()

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state

def thermocool_hand(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE="TM-11", DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option["app_code"], DATAMODE="A").last()
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").exists():
			device_details = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").first()
		else:
			device_details = dict()
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		medical_test['medical_device'] = medical_device
		medical_test['device_details'] = device_details
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		normal = str(test_interpertation.RANGES['Normal'])
		abnormal = str(test_interpertation.RANGES['Abnormal'])
		medical_test['normal'] = normal
		medical_test['abnormal'] = abnormal
		medical_test['test_completed_list'] = list()
		request.session['test_completed_list'] = list()
		if option['test_entry']:
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			medical_test_completed_list = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			for completed_list in medical_test_completed_list:
				medical_test['test_completed_list'].append(completed_list.MEDICALTESTMASTER.CODE)
				if 'test_completed_list' in request.session:
					if completed_list.MEDICALTESTMASTER.CODE in request.session['test_completed_list']:
						pass
					else:
						request.session['test_completed_list'].append(completed_list.MEDICALTESTMASTER.CODE)
			request.session['test_completed_list_length'] = len(request.session['test_completed_list'])
			medical_test['test_completed_list_length'] = len(medical_test_completed_list)
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			request.session['test_type'] = medical_test_type.ORGAN_TYPE
			request.session['test_for'] = "Warm" 
			medical_test['test_type'] = medical_test_type.ORGAN_TYPE 
			medical_test['test_for'] = "Warm" 
		else:
			medical_test['test_completed_list_length'] = 0
		if option['test_code'] and option['test_entry']:
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			if request.session['test_type'] == "Hand" and len(request.session['test_completed_list'])==2:
				medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				test_report.TEST_STATUS = "COMPLETED"
				test_report.save()
				hcp_test_values = dict()
				for medical_test_value in medical_tests:
					tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
					
					right_hand_result, left_hand_result = "", ""
					right_avg = 0.0
					left_avg = 0.0
					right_count = 0
					left_count = 0
					for tx_test in tx_test_entries[0:7]:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							right_avg = right_avg + float(tx_test.KEY_VALUE)
							right_count = right_count +1
					for tx_test in tx_test_entries[7:14]:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							left_avg = left_avg + float(tx_test.KEY_VALUE)
							left_count = left_count +1
					medical_test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_value.MEDICALTESTMASTER.CODE, DATAMODE="A")
					normal = str(medical_test_interpertation.RANGES['Normal'])
					abnormal = str(medical_test_interpertation.RANGES['Abnormal'])
					hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE] = dict()
					normal = normal.split("-")
					if right_count != 0 and right_avg:
						right_avg = round(float(right_avg / right_count), 1)
						if float(right_avg) >= float(normal[0]) and float(right_avg) <= float(normal[1]):
							right_hand_result = "Normal"
						elif "<" in abnormal:
							abnormal_value = abnormal.replace("<", "")
							if float(right_avg) < float(abnormal_value):
								right_hand_result = "Abnormal"
							else:
								right_hand_result = "Not in Range"
						elif ">" in abnormal:
							abnormal_value = abnormal.replace(">", "")
							if float(right_avg) > float(abnormal_value):
								right_hand_result = "Abnormal"
							else:
								right_hand_result = "Not in Range"
						else:
							right_hand_result = "Not in Range"
						hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE]['right_hand_result'] = ["%.1f"%(right_avg), right_hand_result]
					else:
						hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE]['right_hand_result'] = ["No Data", ""]
					if left_count != 0 and left_avg:
						left_avg = round(float(left_avg / left_count), 1)
						if float(left_avg) >=  float(normal[0]) and float(left_avg) <= float(normal[1]):
							left_hand_result = "Normal"
						elif "<" in abnormal:
							abnormal_value = abnormal.replace("<", "")
							if float(left_avg) < float(abnormal_value):
								left_hand_result = "Abnormal"
							else:
								left_hand_result = "Not in Range"
						elif ">" in abnormal:
							abnormal_value = abnormal.replace(">", "")
							if float(left_avg) > float(abnormal_value):
								left_hand_result = "Abnormal"
							else:
								left_hand_result = "Not in Range"
						else:
							left_hand_result = "Not in Range"
						hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE]['left_hand_result'] = ["%.1f"%(left_avg), left_hand_result]
					else:
						hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE]['left_hand_result'] = ["No Data", ""]

				medical_test["hcp_test_values"] = hcp_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(hcp_test_values)
				report.save()
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def other_medical_test_entry(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	try:
		test_type = p_dict.get('test_type',None)
		test_for = p_dict.get('test_for',"Other")
		
		if test_type:
			request.session['test_type'] = test_type
		if test_for:
			request.session['test_for'] = test_for

		patient = p_dict['patient_uid'].strip()
		doctor = p_dict.get('doctor_uid', None)
		examiner = p_dict.get('examiner_uid', None)
		app_code = p_dict['app_code'].strip()
		test_code = p_dict['test_code'].strip()
		test_entry = p_dict.get('test_entry', None)
		kodys_apps = MA_MEDICALAPPS.objects.filter(CODE=app_code, DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=app_code, DATAMODE="A").last()
		if test_code:
			medical_test_type  = MA_MEDICALTESTMASTER.objects.filter(CODE=test_code, DATAMODE="A").first()
			test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=test_code, DATAMODE="A")
			normal = str(test_interpertation.RANGES['Normal'])
			abnormal = str(test_interpertation.RANGES['Abnormal'])
			normal = normal.split("-")
			if doctor.strip() != "no_uid":
				doctor = TX_HCP.objects.get(UID=doctor, DATAMODE="A")
			else:
				doctor = ""
			if examiner.strip() != "no_uid":
				examiner = TX_HCP.objects.get(UID=examiner, DATAMODE="A")
			else:
				examiner = ""
			patients = TX_PATIENTS.objects.get(UID=patient, DATAMODE="A")
			if test_entry and TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, MEDICALTESTMASTER__CODE=test_code).exists():
				medical_test_fields = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, MEDICALTEST__MEDICALTESTMASTER__CODE=test_code)
				for test_fields in medical_test_fields:
					if "V" in test_fields.KEY_CODE:
						KEY_NAME = test_fields.KEY_CODE.replace("V", "K")
					test_fields.KEY_NAME =  p_dict.get(KEY_NAME, "")
					test_fields.MEDICALTESTFIELDS.KEY_NAME = p_dict.get(KEY_NAME, "")
					test_fields.MEDICALTESTFIELDS.save()
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_fields.KEY_VALUE = test_field_value
						if test_field_value.isalpha():
							test_fields.KEY_VALUE_STATUS = "Abnormal"
						elif float(test_field_value) >= float(normal[0]) and float(test_field_value) <= float(normal[1]):
							test_fields.KEY_VALUE_STATUS = "Normal"
						elif "<" in abnormal:
							abnormal_value = abnormal.replace("<", "")
							if float(test_field_value) < float(abnormal_value):
								test_fields.KEY_VALUE_STATUS = "Abnormal"
							else:
								test_fields.KEY_VALUE_STATUS = "Not_in_Range"
						elif ">" in abnormal:
							abnormal_value = abnormal.replace(">", "")
							if float(test_field_value) > float(abnormal_value):
								test_fields.KEY_VALUE_STATUS = "Abnormal"
							else:
								test_fields.KEY_VALUE_STATUS = "Not_in_Range"
					else:
						test_fields.KEY_VALUE = ""
						test_fields.KEY_VALUE_STATUS = "No_Data"
					# test_fields.KEY_VALUE = p_dict.get(test_fields.KEY_CODE, "").strip()
					test_fields.save()
				# medical_test = test_fields.MEDICALTEST
				medical_test = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, DATAMODE="A").first()
			
			else:
				medical_test = TX_MEDICALTESTS()
				medical_test.UID = uuid.uuid4().hex[:30]
				medical_test.MEDICALTESTMASTER = medical_test_type
				medical_test.PATIENT = patients
				medical_test.INTERPERTATION = test_interpertation.RANGES
				if doctor:
					medical_test.DOCTOR = doctor
				if examiner:
					medical_test.EXAMINER = examiner
				medical_test.REPORTED_ON = datetime.datetime.now()
				medical_test.save()
				if test_entry:
					test_entry = test_entry.strip()
					medical_test.FRIENDLY_UID = test_entry
				else:
					medical_test.FRIENDLY_UID = "TST-%08d"%(medical_test.id)
				medical_test.save() 

				medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A")
				for test_fields in medical_test_fields:
					test_entries = TX_MEDICALTESTENTRIES()
					test_entries.UID = uuid.uuid4().hex[:30]
					test_entries.MEDICALTEST = medical_test
					test_entries.MEDICALTESTFIELDS = test_fields
					# test_entries.KEY_NAME = test_fields.KEY_NAME
					test_entries.KEY_CODE = test_fields.KEY_CODE
					if "V" in test_fields.KEY_CODE:
						KEY_NAME = test_fields.KEY_CODE.replace("V", "K")
					test_entries.KEY_NAME =  p_dict.get(KEY_NAME, "")
					test_fields.KEY_NAME = p_dict.get(KEY_NAME, "")
					test_fields.save()
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_entries.KEY_VALUE = test_field_value
						if test_field_value.isalpha():
							test_entries.KEY_VALUE_STATUS = "Abnormal"
						elif float(test_field_value) >= float(normal[0]) and float(test_field_value) <= float(normal[1]):
							test_entries.KEY_VALUE_STATUS = "Normal"
						elif "<" in abnormal:
							abnormal_value = abnormal.replace("<", "")
							if float(test_field_value) < float(abnormal_value):
								test_entries.KEY_VALUE_STATUS = "Abnormal"
							else:
								test_entries.KEY_VALUE_STATUS = "Not_in_Range"
						elif ">" in abnormal:
							abnormal_value = abnormal.replace(">", "")
							if float(test_field_value) > float(abnormal_value):
								test_entries.KEY_VALUE_STATUS = "Abnormal"
							else:
								test_entries.KEY_VALUE_STATUS = "Not_in_Range"
					else:
						test_entries.KEY_VALUE = ""
						test_entries.KEY_VALUE_STATUS = "No_Data"
					test_entries.save()
				
			if TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A").exists():
				pass
			else:
				test_report = TX_MEDICALTESTREPORTS()
				test_report.UID = uuid.uuid4().hex[:30]
				# test_report.FRIENDLY_UID = uuid.uuid4().hex[:30]
				test_report.MEDICALTEST = medical_test
				test_report.TEMPERATURE_SCALE = "CELSIUS"
				test_report.REFERRED_BY = referred_by_medical_test_type.REFERRED_BY
				if test_for:
					test_report.TEST_TYPE = test_for
				else:
					test_report.TEST_TYPE = "Warm"
				test_report.REPORTED_ON = datetime.datetime.now()
				test_report.CREATED_BY = request.user
				test_report.UPDATED_BY = request.user
				test_report.save()
				test_report.FRIENDLY_UID = "REP-%08d"%(test_report.id)
				test_report.save()

				# Pre-calculate ECG results to solve report lag and apply algorithmic fixes
				try:
					processed_results = process_can_test_data(test_report)
					if processed_results:
						test_report.TEST_RESULT = json.dumps(processed_results)
						test_report.save()
				except Exception as e:
					print("Pre-calculation failed: ", e)
				
			if 'test_completed_list' in request.session:
				if test_code in request.session['test_completed_list']:
					pass
				else:
					request.session['test_completed_list'].append(test_code)
			else:
				request.session['test_completed_list'] = list()
				request.session['test_completed_list'].append(test_code)
			request.session['test_completed_list_length'] = len(request.session['test_completed_list'])
			medical_test_result['test_entry_id'] = medical_test.FRIENDLY_UID
			medical_test_result['current_test_code'] = medical_test.MEDICALTESTMASTER.CODE
	
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			medical_test_result['test_entry_id'] = None
			medical_test_result['current_test_code'] = None
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test_result


def thermocool_other(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE="TM-16", DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").exists():
			device_details = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").first()
		else:
			device_details = dict()
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		medical_test['medical_device'] = medical_device
		medical_test['device_details'] = device_details
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		normal = str(test_interpertation.RANGES['Normal'])
		abnormal = str(test_interpertation.RANGES['Abnormal'])
		medical_test['normal'] = normal
		medical_test['abnormal'] = abnormal
		medical_test['test_completed_list'] = list()
		request.session['test_completed_list'] = list()
		if option['test_entry']:
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			medical_test_completed_list = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			for completed_list in medical_test_completed_list:
				medical_test['test_completed_list'].append(completed_list.MEDICALTESTMASTER.CODE)
				if 'test_completed_list' in request.session:
					if completed_list.MEDICALTESTMASTER.CODE in request.session['test_completed_list']:
						pass
					else:
						request.session['test_completed_list'].append(completed_list.MEDICALTESTMASTER.CODE)
			request.session['test_completed_list_length'] = len(request.session['test_completed_list'])
			medical_test['test_completed_list_length'] = len(medical_test_completed_list)
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			request.session['test_type'] = medical_test_type.ORGAN_TYPE
			request.session['test_for'] = "Warm" 
			medical_test['test_type'] = medical_test_type.ORGAN_TYPE 
			medical_test['test_for'] = "Warm" 
		else:
			medical_test['test_completed_list_length'] = 0
		if option['test_code'] and option['test_entry']:
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			if request.session['test_type'] == "Other" and len(request.session['test_completed_list'])==2:
				medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				test_report.TEST_STATUS = "COMPLETED"
				test_report.save()
				hcp_test_values = dict()
				for medical_test_value in medical_tests:
					tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
					
				 	other_result = ""
					other_avg = 0.0
					other_count = 0
					for tx_test in tx_test_entries:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							other_avg = other_avg + float(tx_test.KEY_VALUE)
							other_count = other_count +1
					medical_test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_value.MEDICALTESTMASTER.CODE, DATAMODE="A")
					normal = str(medical_test_interpertation.RANGES['Normal'])
					abnormal = str(medical_test_interpertation.RANGES['Abnormal'])
					hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE] = dict()
					normal = normal.split("-")
					if other_count != 0 and other_avg:
						other_avg = round(float(other_avg / other_count), 1)
						if float(other_avg) >= float(normal[0]) and float(other_avg) <= float(normal[1]):
							other_result = "Normal"
						elif "<" in abnormal:
							abnormal_value = abnormal.replace("<", "")
							if float(other_avg) < float(abnormal_value):
								other_result = "Abnormal"
							else:
								other_result = "Not in Range"
						elif ">" in abnormal:
							abnormal_value = abnormal.replace(">", "")
							if float(other_avg) > float(abnormal_value):
								other_result = "Abnormal"
							else:
								other_result = "Not in Range"
						else:
							other_result = "Not in Range"
						hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE]['other_result'] = ["%.1f"%(other_avg), other_result]
					else:
						hcp_test_values[medical_test_value.MEDICALTESTMASTER.CODE]['other_result'] = ["No Data", ""]

				medical_test["hcp_test_values"] = hcp_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(hcp_test_values)
				report.save()
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def vpt_ultra_medical_test_entry(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	extra_list = ['F-29', 'F-30', 'F-31', 'F-32', 'H-28', 'H-29', 'H-30', 'H-31',]
	try:
		patient = p_dict['patient_uid'].strip()
		doctor = p_dict.get('doctor_uid', None)
		examiner = p_dict.get('examiner_uid', None)
		app_code = p_dict['app_code'].strip()
		test_code = p_dict['test_code'].strip()
		test_entry = p_dict.get('test_entry', None)
		kodys_apps = MA_MEDICALAPPS.objects.filter(CODE=app_code, DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=app_code, DATAMODE="A").last()
		if test_code:
			medical_test_type  = MA_MEDICALTESTMASTER.objects.filter(CODE=test_code, DATAMODE="A").first()
			if doctor.strip() != "no_uid":
				doctor = TX_HCP.objects.get(UID=doctor, DATAMODE="A")
			else:
				doctor = ""
			if examiner.strip() != "no_uid":
				examiner = TX_HCP.objects.get(UID=examiner, DATAMODE="A")
			else:
				examiner = ""
			patients = TX_PATIENTS.objects.get(UID=patient, DATAMODE="A")
			test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=test_code, DATAMODE="A")
			normal = str(test_interpertation.RANGES['Normal'])
			risk = str(test_interpertation.RANGES['Risk'])
			mild = str(test_interpertation.RANGES['Mild'])
			severe = str(test_interpertation.RANGES['Severe'])
			moderate = str(test_interpertation.RANGES['Moderate'])
			bmi_normal = str(test_interpertation.RANGES['BMI']['Normal'])
			bmi_over_weight = str(test_interpertation.RANGES['BMI']['Over Weight'])
			bmi_obese = str(test_interpertation.RANGES['BMI']['Obese'])
			bmi_uder_weight = str(test_interpertation.RANGES['BMI']['Underweight'])
			abi_normal = str(test_interpertation.RANGES['ABI']['Normal'])
			abi_mild = str(test_interpertation.RANGES['ABI']['Mild'])
			abi_severe = str(test_interpertation.RANGES['ABI']['Severe'])
			abi_gangrene = str(test_interpertation.RANGES['ABI']['Gangrene'])
			abi_moderate = str(test_interpertation.RANGES['ABI']['Moderate'])
			abi_calcified = str(test_interpertation.RANGES['ABI']['Calcified'])
			normal = normal.split("-")
			mild = mild.split("-")
			severe = severe.split("-")
			moderate = moderate.split("-")
			risk = risk.replace(">", "")
			if test_entry and TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, MEDICALTESTMASTER__CODE=test_code).exists():
				medical_test_fields = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, MEDICALTEST__MEDICALTESTMASTER__CODE=test_code)
				for test_fields in medical_test_fields:
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_fields.MEDICALTESTFIELDS.KEY_CODE in extra_list:
						if "F" in test_fields.KEY_CODE:
							KEY_NAME = test_fields.KEY_CODE.replace("F", "K")
							test_fields.KEY_NAME = p_dict.get(KEY_NAME, "")
						elif "H" in test_fields.KEY_CODE:
							KEY_NAME = test_fields.KEY_CODE.replace("H", "K")
							test_fields.KEY_NAME = p_dict.get(KEY_NAME, "")
						test_fields.MEDICALTESTFIELDS.KEY_NAME = p_dict.get(KEY_NAME, "")
						test_fields.MEDICALTESTFIELDS.save()
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_fields.KEY_VALUE = test_field_value
						if test_field_value.isalpha():
							if len(test_field_value) == 1:
								if test_field_value == "Y":
									test_fields.KEY_VALUE_STATUS = "Normal"
								else:								
									test_fields.KEY_VALUE_STATUS = "Not_in_Range"
							else:	
								test_fields.KEY_VALUE_STATUS = "Not_in_Range"
						elif float(test_field_value) >= float(normal[0]) and float(test_field_value) <= float(normal[1]):
							test_fields.KEY_VALUE_STATUS = "Normal"
						elif float(test_field_value) >= float(mild[0]) and float(test_field_value) <= float(mild[1]):
							test_fields.KEY_VALUE_STATUS = "Mild"
						elif float(test_field_value) >= float(severe[0]) and float(test_field_value) <= float(severe[1]):
							test_fields.KEY_VALUE_STATUS = "Severe"
						elif float(test_field_value) >= float(moderate[0]) and float(test_field_value) <= float(moderate[1]):
							test_fields.KEY_VALUE_STATUS = "Moderate"
						elif float(test_field_value) >= float(risk):
							test_fields.KEY_VALUE_STATUS = "Risk"
						else:
							test_fields.KEY_VALUE_STATUS = "Not_in_Range"
					else:
						test_fields.KEY_VALUE = ""
						test_fields.KEY_VALUE_STATUS = "No_Data"
					test_fields.save()
				medical_test = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, DATAMODE="A").first()
			else:
				medical_test = TX_MEDICALTESTS()
				medical_test.UID = uuid.uuid4().hex[:30]
				medical_test.MEDICALTESTMASTER = medical_test_type
				medical_test.PATIENT = patients
				medical_test.INTERPERTATION = test_interpertation.RANGES
				if doctor:
					medical_test.DOCTOR = doctor
				if examiner:
					medical_test.EXAMINER = examiner
				medical_test.REPORTED_ON = datetime.datetime.now()
				medical_test.save()
				medical_test.FRIENDLY_UID = "TST-%08d"%(medical_test.id)
				medical_test.save() 

				medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A")
				for test_fields in medical_test_fields:
					test_entries = TX_MEDICALTESTENTRIES()
					test_entries.UID = uuid.uuid4().hex[:30]
					test_entries.MEDICALTEST = medical_test
					test_entries.MEDICALTESTFIELDS = test_fields
					if test_fields.KEY_CODE in extra_list:
						if "F" in test_fields.KEY_CODE:
							KEY_NAME = test_fields.KEY_CODE.replace("F", "K")
							test_entries.KEY_NAME = p_dict.get(KEY_NAME, "")
						elif "H" in test_fields.KEY_CODE:
							KEY_NAME = test_fields.KEY_CODE.replace("H", "K")
							test_entries.KEY_NAME = p_dict.get(KEY_NAME, "")
						test_fields.KEY_NAME = p_dict.get(KEY_NAME, "")
						test_fields.save()
					else:
						test_entries.KEY_NAME = test_fields.KEY_NAME
					test_entries.KEY_CODE = test_fields.KEY_CODE
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_entries.KEY_VALUE = test_field_value
						if test_field_value.isalpha():
							if len(test_field_value) == 1:
								if test_field_value == "Y":
									test_entries.KEY_VALUE_STATUS = "Normal"
								else:								
									test_entries.KEY_VALUE_STATUS = "Not_in_Range"
							else:	
								test_entries.KEY_VALUE_STATUS = "Not_in_Range"
						elif float(test_field_value) >= float(normal[0]) and float(test_field_value) <= float(normal[1]):
							test_entries.KEY_VALUE_STATUS = "Normal"
						elif float(test_field_value) >= float(mild[0]) and float(test_field_value) <= float(mild[1]):
							test_entries.KEY_VALUE_STATUS = "Mild"
						elif float(test_field_value) >= float(severe[0]) and float(test_field_value) <= float(severe[1]):
							test_entries.KEY_VALUE_STATUS = "Severe"
						elif float(test_field_value) >= float(moderate[0]) and float(test_field_value) <= float(moderate[1]):
							test_entries.KEY_VALUE_STATUS = "Moderate"
						elif float(test_field_value) >= float(risk):
							test_entries.KEY_VALUE_STATUS = "Risk"
						else:
							test_entries.KEY_VALUE_STATUS = "Not_in_Range"
					else:
						test_entries.KEY_VALUE = ""
						test_entries.KEY_VALUE_STATUS = "No_Data"
					test_entries.save()
				
			if TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A").exists():
				pass
			else:
				test_report = TX_MEDICALTESTREPORTS()
				test_report.UID = uuid.uuid4().hex[:30]
				test_report.MEDICALTEST = medical_test
				test_report.TEMPERATURE_SCALE = "Volts"
				test_report.REFERRED_BY = referred_by_medical_test_type.REFERRED_BY
				test_report.REPORTED_ON = datetime.datetime.now()
				test_report.TEST_STATUS = "COMPLETED"
				test_report.CREATED_BY = request.user
				test_report.UPDATED_BY = request.user
				test_report.save()
				test_report.FRIENDLY_UID = "REP-%08d"%(test_report.id)
				test_report.save()

				# Pre-calculate ECG results to solve report lag and apply algorithmic fixes
				try:
					processed_results = process_can_test_data(test_report)
					if processed_results:
						test_report.TEST_RESULT = json.dumps(processed_results)
						test_report.save()
				except Exception as e:
					print("Pre-calculation failed: ", e)
			medical_test_result['test_entry_id'] = medical_test.FRIENDLY_UID
			medical_test_result['current_test_code'] = medical_test.MEDICALTESTMASTER.CODE
	
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			medical_test_result['test_entry_id'] = None
			medical_test_result['current_test_code'] = None
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test_result


def vpt_ultra_foot(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").last()
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").exists():
			device_details = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").first()
		else:
			device_details = dict()
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		medical_test['medical_device'] = medical_device
		medical_test['device_details'] = device_details
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		risk = str(test_interpertation.RANGES['Risk'])
		normal = str(test_interpertation.RANGES['Normal'])
		mild = str(test_interpertation.RANGES['Mild'])
		severe = str(test_interpertation.RANGES['Severe'])
		moderate = str(test_interpertation.RANGES['Moderate'])
		bmi_normal = str(test_interpertation.RANGES['BMI']['Normal'])
		bmi_over_weight = str(test_interpertation.RANGES['BMI']['Over Weight'])
		bmi_obese = str(test_interpertation.RANGES['BMI']['Obese'])
		bmi_under_weight = str(test_interpertation.RANGES['BMI']['Underweight'])
		abi_normal = str(test_interpertation.RANGES['ABI']['Normal'])
		abi_mild = str(test_interpertation.RANGES['ABI']['Mild'])
		abi_severe = str(test_interpertation.RANGES['ABI']['Severe'])
		abi_gangrene = str(test_interpertation.RANGES['ABI']['Gangrene'])
		abi_moderate = str(test_interpertation.RANGES['ABI']['Moderate'])
		abi_calcified = str(test_interpertation.RANGES['ABI']['Calcified'])
		medical_test['normal'] = normal
		medical_test['risk'] = risk
		medical_test['mild'] = mild
		medical_test['severe'] = severe
		medical_test['moderate'] = moderate
		medical_test['bmi_normal'] = bmi_normal
		medical_test['bmi_over_weight'] = bmi_over_weight
		medical_test['bmi_obese'] = bmi_obese
		medical_test['bmi_under_weight'] = bmi_under_weight
		medical_test['abi_normal'] = abi_normal
		medical_test['abi_mild'] = abi_mild
		medical_test['abi_severe'] = abi_severe
		medical_test['abi_gangrene'] = abi_gangrene
		medical_test['abi_moderate'] = abi_moderate
		medical_test['abi_calcified'] = abi_calcified
		if option['test_entry']:
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			request.session["referred"] = ""
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			request.session['test_type'] = medical_test_type.ORGAN_TYPE
			request.session['test_for'] = test_report.TEST_TYPE 
			medical_test['test_type'] = medical_test_type.ORGAN_TYPE 
			medical_test['test_for'] = test_report.TEST_TYPE 

		if option['test_code'] and option['test_entry']:
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			if medical_tests:
				vpt_ultra_test_values = dict()
				for medical_test_value in medical_tests:
					tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
				 	right_foot_result, left_foot_result = "", ""
					right_avg = 0.0
					left_avg = 0.0
					right_count = 0
					left_count = 0
					for tx_test in tx_test_entries[0:6]:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							right_avg = right_avg + float(tx_test.KEY_VALUE)
							right_count = right_count +1
					for tx_test in tx_test_entries[8:14]:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							left_avg = left_avg + float(tx_test.KEY_VALUE)
							left_count = left_count +1
					normal = normal.split("-")
					mild = mild.split("-")
					severe = severe.split("-")
					moderate = moderate.split("-")
					risk = risk.replace(">", "")
					# abi_normal = abi_normal.split("-")
					abi_mild = abi_mild.split("-")
					abi_severe = abi_severe.split("-")
					abi_gangrene = abi_gangrene.replace("<", "")
					abi_moderate = abi_moderate.split("-")
					abi_calcified = abi_calcified.replace(">", "")

					if right_count != 0 and right_avg:
						right_avg = round(float(right_avg / right_count), 1)
						if float(right_avg) >= float(normal[0]) and float(right_avg) <= float(normal[1]):
							right_foot_result = "Normal"
						elif float(right_avg) >= float(mild[0]) and float(right_avg) <= float(mild[1]):
							right_foot_result = "Mild"
						elif float(right_avg) >= float(severe[0]) and float(right_avg) <= float(severe[1]):
							right_foot_result = "Severe"
						elif float(right_avg) >= float(moderate[0]) and float(right_avg) <= float(moderate[1]):
							right_foot_result = "Moderate"
						elif float(right_avg) >= float(risk):
							right_foot_result = "Risk"
						else:
							right_foot_result = "Not in Range"
						vpt_ultra_test_values['right_foot_result'] = ["%.1f"%(right_avg), right_foot_result]
					else:
						vpt_ultra_test_values['right_foot_result'] = ["No Data", ""]

					if left_count != 0 and left_avg:
						left_avg = round(float(left_avg / left_count), 1)
						if float(left_avg) >= float(normal[0]) and float(left_avg) <= float(normal[1]):
							left_foot_result = "Normal"
						elif float(left_avg) >= float(mild[0]) and float(left_avg) <= float(mild[1]):
							left_foot_result = "Mild"
						elif float(left_avg) >= float(severe[0]) and float(left_avg) <= float(severe[1]):
							left_foot_result = "Severe"
						elif float(left_avg) >= float(moderate[0]) and float(left_avg) <= float(moderate[1]):
							left_foot_result = "Moderate"
						elif float(left_avg) >= float(risk):
							left_foot_result = "Risk"
						else:
							left_foot_result = "Not in Range"
						vpt_ultra_test_values['left_foot_result'] = ["%.1f"%(left_avg), left_foot_result]
					else:
						vpt_ultra_test_values['left_foot_result'] = ["No Data", ""]
					if patient.HEIGHT and patient.WEIGHT:
						if float(patient.HEIGHT) and float(patient.WEIGHT):
							bmi_normal = bmi_normal.split("-")
							bmi_over_weight = bmi_over_weight.split("-")
							bmi_obese_value = bmi_obese.replace(">", "")
							bmi_under_weight = bmi_under_weight.replace("<", "")
							bmi_avg = round(float(float(patient.WEIGHT)/((float(patient.HEIGHT)/100)*(float(patient.HEIGHT)/100))), 2)
							if float(bmi_avg) >= float(bmi_normal[0]) and float(bmi_avg) <= float(bmi_normal[1]):
								bmi_result = "Normal"
							elif float(bmi_avg) >= float(bmi_over_weight[0]) and float(bmi_avg) <= float(bmi_over_weight[1]):
								bmi_result = "Over Weight"
							elif float(bmi_avg) > float(bmi_obese_value):
								bmi_result = "Obese"
							elif float(bmi_avg) <= float(bmi_under_weight):
								bmi_result = "Under Weight"
						else:
							bmi_avg = 0.0
							bmi_result = "Invalid Data"
						vpt_ultra_test_values['bmi_result'] = [bmi_avg, bmi_result]

					if tx_test_entries[20].KEY_VALUE and tx_test_entries[22].KEY_VALUE:
						if tx_test_entries[20].KEY_VALUE.isalpha() or tx_test_entries[22].KEY_VALUE.isalpha():
							vpt_ultra_test_values['right_abi_result'] = ["No Data", ""]
						else:
							if float(tx_test_entries[20].KEY_VALUE) and float(tx_test_entries[22].KEY_VALUE):
								try:
									denominator = float(tx_test_entries[22].KEY_VALUE)
									if denominator != 0:
										right_abi = round(float(float(tx_test_entries[20].KEY_VALUE)/denominator), 2)
									else:
					right_abi = 0.0
								except:
									right_abi = 0.0
								if float(right_abi) >= float(abi_severe[0]) and float(right_abi) <= float(abi_severe[1]):
									right_abi_result = "Severe"
								elif float(right_abi) >= float(abi_moderate[0]) and float(right_abi) <= float(abi_moderate[1]):
									right_abi_result = "Moderate"
								elif float(right_abi) >= float(abi_mild[0]) and float(right_abi) <= float(abi_mild[1]):
									right_abi_result = "Mild"
								elif float(right_abi) >= float(0.7) and float(right_abi) <= float(1.3):
									right_abi_result = "Normal"
								elif float(right_abi) > float(abi_calcified):
										right_abi_result = "Calcified"
								elif float(right_abi) < float(abi_gangrene):
									right_abi_result = "Gangrene"
								else:
									right_abi_result = "Not in Range"
							else:
								right_abi = 0.0
								right_abi_result = "No Data"
							vpt_ultra_test_values['right_abi_result'] = ["%.2f"%(right_abi), right_abi_result]

					if tx_test_entries[21].KEY_VALUE and tx_test_entries[23].KEY_VALUE:
						if tx_test_entries[21].KEY_VALUE.isalpha() and tx_test_entries[23].KEY_VALUE.isalpha():
							vpt_ultra_test_values['left_abi_result'] = ["No Data", ""]
						else:
							if float(tx_test_entries[21].KEY_VALUE) and float(tx_test_entries[23].KEY_VALUE):
								left_abi = round(float(float(tx_test_entries[21].KEY_VALUE)/float(tx_test_entries[23].KEY_VALUE)), 2)
								if float(left_abi) >= float(abi_severe[0]) and float(left_abi) <= float(abi_severe[1]):
									left_abi_result = "Severe"
								elif float(left_abi) >= float(abi_moderate[0]) and float(left_abi) <= float(abi_moderate[1]):
									left_abi_result = "Moderate"
								elif float(left_abi) >= float(abi_mild[0]) and float(left_abi) <= float(abi_mild[1]):
									left_abi_result = "Mild"
								elif float(left_abi) >= float(0.7) and float(left_abi) <= float(1.3):
									left_abi_result = "Normal"
								elif float(left_abi) >= float(abi_calcified):
										left_abi_result = "Calcified"
								elif float(left_abi) <= float(abi_gangrene):
									left_abi_result = "Gangrene"
								else:
									left_abi_result = "Not in Range"
							else:
								left_abi = 0.0
								left_abi_result = "No Data"
							vpt_ultra_test_values['left_abi_result'] = ["%.2f"%(left_abi), left_abi_result]
				
				medical_test["vpt_ultra_test_values"] = vpt_ultra_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(vpt_ultra_test_values)
				report.save()

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def vpt_ultra_hand(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").last()
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").exists():
			device_details = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").first()
		else:
			device_details = dict()
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		medical_test['medical_device'] = medical_device
		medical_test['device_details'] = device_details
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		risk = str(test_interpertation.RANGES['Risk'])
		normal = str(test_interpertation.RANGES['Normal'])
		mild = str(test_interpertation.RANGES['Mild'])
		severe = str(test_interpertation.RANGES['Severe'])
		moderate = str(test_interpertation.RANGES['Moderate'])
		bmi_normal = str(test_interpertation.RANGES['BMI']['Normal'])
		bmi_over_weight = str(test_interpertation.RANGES['BMI']['Over Weight'])
		bmi_obese = str(test_interpertation.RANGES['BMI']['Obese'])
		bmi_under_weight = str(test_interpertation.RANGES['BMI']['Underweight'])
		abi_normal = str(test_interpertation.RANGES['ABI']['Normal'])
		abi_mild = str(test_interpertation.RANGES['ABI']['Mild'])
		abi_severe = str(test_interpertation.RANGES['ABI']['Severe'])
		abi_gangrene = str(test_interpertation.RANGES['ABI']['Gangrene'])
		abi_moderate = str(test_interpertation.RANGES['ABI']['Moderate'])
		abi_calcified = str(test_interpertation.RANGES['ABI']['Calcified'])
		medical_test['normal'] = normal
		medical_test['risk'] = risk
		medical_test['mild'] = mild
		medical_test['severe'] = severe
		medical_test['moderate'] = moderate
		medical_test['bmi_normal'] = bmi_normal
		medical_test['bmi_over_weight'] = bmi_over_weight
		medical_test['bmi_obese'] = bmi_obese
		medical_test['bmi_under_weight'] = bmi_under_weight
		medical_test['abi_normal'] = abi_normal
		medical_test['abi_mild'] = abi_mild
		medical_test['abi_severe'] = abi_severe
		medical_test['abi_gangrene'] = abi_gangrene
		medical_test['abi_moderate'] = abi_moderate
		medical_test['abi_calcified'] = abi_calcified
		if option['test_entry']:
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			request.session["referred"] = ""
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			request.session['test_type'] = medical_test_type.ORGAN_TYPE
			request.session['test_for'] = test_report.TEST_TYPE 
			medical_test['test_type'] = medical_test_type.ORGAN_TYPE 
			medical_test['test_for'] = test_report.TEST_TYPE 
		if option['test_code'] and option['test_entry']:
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			if medical_tests:
				vpt_ultra_test_values = dict()
				for medical_test_value in medical_tests:
					tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
					right_hand_result, left_hand_result = "", ""
					right_avg = 0.0
					left_avg = 0.0
					right_count = 0
					left_count = 0
					for tx_test in tx_test_entries[0:7]:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							right_avg = right_avg + float(tx_test.KEY_VALUE)
							right_count = right_count +1
					for tx_test in tx_test_entries[7:14]:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							left_avg = left_avg + float(tx_test.KEY_VALUE)
							left_count = left_count +1
					normal = normal.split("-")
					mild = mild.split("-")
					severe = severe.split("-")
					moderate = moderate.split("-")
					risk = risk.replace(">", "")
					abi_mild = abi_mild.split("-")
					abi_severe = abi_severe.split("-")
					abi_gangrene = abi_gangrene.replace("<", "")
					abi_moderate = abi_moderate.split("-")
					abi_calcified = abi_calcified.replace(">", "")

					if right_count != 0 and right_avg:
						right_avg = round(float(right_avg / right_count), 1)
						if float(right_avg) >= float(normal[0]) and float(right_avg) <= float(normal[1]):
							right_hand_result = "Normal"
						elif float(right_avg) >= float(mild[0]) and float(right_avg) <= float(mild[1]):
							right_hand_result = "Mild"
						elif float(right_avg) >= float(severe[0]) and float(right_avg) <= float(severe[1]):
							right_hand_result = "Severe"
						elif float(right_avg) >= float(moderate[0]) and float(right_avg) <= float(moderate[1]):
							right_hand_result = "Moderate"
						elif float(right_avg) >= float(risk):
							right_hand_result = "Risk"
						else:
							right_hand_result = "Not in Range"
						vpt_ultra_test_values['right_hand_result'] = ["%.1f"%(right_avg), right_hand_result]
					else:
						vpt_ultra_test_values['right_hand_result'] = ["No Data", ""]

					if left_count != 0 and left_avg:
						left_avg = round(float(left_avg / left_count), 1)
						if float(left_avg) >= float(normal[0]) and float(left_avg) <= float(normal[1]):
							left_hand_result = "Normal"
						elif float(left_avg) >= float(mild[0]) and float(left_avg) <= float(mild[1]):
							left_hand_result = "Mild"
						elif float(left_avg) >= float(severe[0]) and float(left_avg) <= float(severe[1]):
							left_hand_result = "Severe"
						elif float(left_avg) >= float(moderate[0]) and float(left_avg) <= float(moderate[1]):
							left_hand_result = "Moderate"
						elif float(left_avg) >= float(risk):
							left_hand_result = "Risk"
						else:
							left_hand_result = "Not in Range"
						vpt_ultra_test_values['left_hand_result'] = ["%.1f"%(left_avg), left_hand_result]
					else:
						vpt_ultra_test_values['left_hand_result'] = ["No Data", ""]
					if patient.HEIGHT and patient.WEIGHT:
						if float(patient.HEIGHT) and float(patient.WEIGHT):
							bmi_normal = bmi_normal.split("-")
							bmi_over_weight = bmi_over_weight.split("-")
							bmi_obese_value = bmi_obese.replace(">", "")
							bmi_under_weight = bmi_under_weight.replace("<", "")
							bmi_avg = round(float(float(patient.WEIGHT)/((float(patient.HEIGHT)/100)*(float(patient.HEIGHT)/100))), 2)
							if float(bmi_avg) >= float(bmi_normal[0]) and float(bmi_avg) <= float(bmi_normal[1]):
								bmi_result = "Normal"
							elif float(bmi_avg) >= float(bmi_over_weight[0]) and float(bmi_avg) <= float(bmi_over_weight[1]):
								bmi_result = "Over Weight"
							elif float(bmi_avg) > float(bmi_obese_value):
								bmi_result = "Obese"
							elif float(bmi_avg) <= float(bmi_under_weight):
								bmi_result = "Under Weight"
						else:
							bmi_avg = 0.0
							bmi_result = "Invalid Data"
						vpt_ultra_test_values['bmi_result'] = [bmi_avg, bmi_result]
				
				medical_test["vpt_ultra_test_values"] = vpt_ultra_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(vpt_ultra_test_values)
				report.save()

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def vpt_ultra_other_medical_test_entry(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	try:
		test_for = p_dict.get('test_for',"Other")

		patient = p_dict['patient_uid'].strip()
		doctor = p_dict.get('doctor_uid', None)
		examiner = p_dict.get('examiner_uid', None)
		app_code = p_dict['app_code'].strip()
		test_code = p_dict['test_code'].strip()
		test_entry = p_dict.get('test_entry', None)
		kodys_apps = MA_MEDICALAPPS.objects.filter(CODE=app_code, DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=app_code, DATAMODE="A").last()
		if test_code:
			medical_test_type  = MA_MEDICALTESTMASTER.objects.filter(CODE=test_code, DATAMODE="A").first()
			test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=test_code, DATAMODE="A")
			risk = str(test_interpertation.RANGES['Risk'])
			normal = str(test_interpertation.RANGES['Normal'])
			mild = str(test_interpertation.RANGES['Mild'])
			severe = str(test_interpertation.RANGES['Severe'])
			moderate = str(test_interpertation.RANGES['Moderate'])
			bmi_normal = str(test_interpertation.RANGES['BMI']['Normal'])
			bmi_over_weight = str(test_interpertation.RANGES['BMI']['Over Weight'])
			bmi_obese = str(test_interpertation.RANGES['BMI']['Obese'])
			bmi_under_weight = str(test_interpertation.RANGES['BMI']['Underweight'])
			abi_normal = str(test_interpertation.RANGES['ABI']['Normal'])
			abi_mild = str(test_interpertation.RANGES['ABI']['Mild'])
			abi_severe = str(test_interpertation.RANGES['ABI']['Severe'])
			abi_gangrene = str(test_interpertation.RANGES['ABI']['Gangrene'])
			abi_moderate = str(test_interpertation.RANGES['ABI']['Moderate'])
			abi_calcified = str(test_interpertation.RANGES['ABI']['Calcified'])
			normal = normal.split("-")
			mild = mild.split("-")
			severe = severe.split("-")
			moderate = moderate.split("-")
			risk = risk.replace(">", "")
			abi_mild = abi_mild.split("-")
			abi_severe = abi_severe.split("-")
			abi_gangrene = abi_gangrene.replace("<", "")
			abi_moderate = abi_moderate.split("-")
			abi_calcified = abi_calcified.replace(">", "")

			if doctor.strip() != "no_uid":
				doctor = TX_HCP.objects.get(UID=doctor, DATAMODE="A")
			else:
				doctor = ""
			if examiner.strip() != "no_uid":
				examiner = TX_HCP.objects.get(UID=examiner, DATAMODE="A")
			else:
				examiner = ""
			patients = TX_PATIENTS.objects.get(UID=patient, DATAMODE="A")
			if test_entry and TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, MEDICALTESTMASTER__CODE=test_code).exists():
				medical_test_fields = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, MEDICALTEST__MEDICALTESTMASTER__CODE=test_code)
				for test_fields in medical_test_fields:
					if "V" in test_fields.KEY_CODE:
						KEY_NAME = test_fields.KEY_CODE.replace("V", "K")
					if "B" in test_fields.KEY_CODE:
						KEY_NAME = test_fields.KEY_CODE.replace("B", "K")
					test_fields.KEY_NAME =  p_dict.get(KEY_NAME, "")
					test_fields.MEDICALTESTFIELDS.KEY_NAME = p_dict.get(KEY_NAME, "")
					test_fields.MEDICALTESTFIELDS.save()
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_fields.KEY_VALUE = test_field_value
						if test_field_value.isalpha():
							if len(test_field_value) == 1:
								if test_field_value == "Y":
									test_fields.KEY_VALUE_STATUS = "Normal"
								else:								
									test_fields.KEY_VALUE_STATUS = "Not_in_Range"
							else:								
								test_fields.KEY_VALUE_STATUS = "Not_in_Range"
						elif float(test_field_value) >= float(normal[0]) and float(test_field_value) <= float(normal[1]):
							test_fields.KEY_VALUE_STATUS = "Normal"
						elif float(test_field_value) >= float(mild[0]) and float(test_field_value) <= float(mild[1]):
							test_fields.KEY_VALUE_STATUS = "Mild"
						elif float(test_field_value) >= float(severe[0]) and float(test_field_value) <= float(severe[1]):
							test_fields.KEY_VALUE_STATUS = "Severe"
						elif float(test_field_value) >= float(moderate[0]) and float(test_field_value) <= float(moderate[1]):
							test_fields.KEY_VALUE_STATUS = "Moderate"
						elif float(test_field_value) >= float(risk):
							test_fields.KEY_VALUE_STATUS = "Risk"
						else:
							test_fields.KEY_VALUE_STATUS = "Not_in_Range"
					else:
						test_fields.KEY_VALUE = ""
						test_fields.KEY_VALUE_STATUS = "No_Data"
					test_fields.save()
				medical_test = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, DATAMODE="A").first()
			
			else:
				medical_test = TX_MEDICALTESTS()
				medical_test.UID = uuid.uuid4().hex[:30]
				medical_test.MEDICALTESTMASTER = medical_test_type
				medical_test.PATIENT = patients
				medical_test.INTERPERTATION = test_interpertation.RANGES
				if doctor:
					medical_test.DOCTOR = doctor
				if examiner:
					medical_test.EXAMINER = examiner
				medical_test.REPORTED_ON = datetime.datetime.now()
				medical_test.save()
				if test_entry:
					test_entry = test_entry.strip()
					medical_test.FRIENDLY_UID = test_entry
				else:
					medical_test.FRIENDLY_UID = "TST-%08d"%(medical_test.id)
				medical_test.save() 

				medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A")
				for test_fields in medical_test_fields:
					test_entries = TX_MEDICALTESTENTRIES()
					test_entries.UID = uuid.uuid4().hex[:30]
					test_entries.MEDICALTEST = medical_test
					test_entries.MEDICALTESTFIELDS = test_fields
					test_entries.KEY_CODE = test_fields.KEY_CODE
					if "V" in test_fields.KEY_CODE:
						KEY_NAME = test_fields.KEY_CODE.replace("V", "K")
					if "B" in test_fields.KEY_CODE:
						KEY_NAME = test_fields.KEY_CODE.replace("B", "K")
					test_entries.KEY_NAME =  p_dict.get(KEY_NAME, "")
					test_fields.KEY_NAME = p_dict.get(KEY_NAME, "")
					test_fields.save()
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_entries.KEY_VALUE = test_field_value
						if test_field_value.isalpha():
							if len(test_field_value) == 1:
								if test_field_value == "Y":
									test_entries.KEY_VALUE_STATUS = "Normal"
								else:								
									test_entries.KEY_VALUE_STATUS = "Not_in_Range"
							else:								
								test_entries.KEY_VALUE_STATUS = "Not_in_Range"
						elif float(test_field_value) >= float(normal[0]) and float(test_field_value) <= float(normal[1]):
							test_entries.KEY_VALUE_STATUS = "Normal"
						elif float(test_field_value) >= float(mild[0]) and float(test_field_value) <= float(mild[1]):
							test_entries.KEY_VALUE_STATUS = "Mild"
						elif float(test_field_value) >= float(severe[0]) and float(test_field_value) <= float(severe[1]):
							test_entries.KEY_VALUE_STATUS = "Severe"
						elif float(test_field_value) >= float(moderate[0]) and float(test_field_value) <= float(moderate[1]):
							test_entries.KEY_VALUE_STATUS = "Moderate"
						elif float(test_field_value) >= float(risk):
							test_entries.KEY_VALUE_STATUS = "Risk"
						else:
							test_entries.KEY_VALUE_STATUS = "Not_in_Range"
					else:
						test_entries.KEY_VALUE = ""
						test_entries.KEY_VALUE_STATUS = "No_Data"
					test_entries.save()
				
			if TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A").exists():
				pass
			else:
				test_report = TX_MEDICALTESTREPORTS()
				test_report.UID = uuid.uuid4().hex[:30]
				test_report.MEDICALTEST = medical_test
				test_report.TEMPERATURE_SCALE = "Volts"
				test_report.REFERRED_BY = referred_by_medical_test_type.REFERRED_BY
				if test_for:
					test_report.TEST_TYPE = test_for
				else:
					test_report.TEST_TYPE = "Other"
				test_report.REPORTED_ON = datetime.datetime.now()
				test_report.TEST_STATUS = "COMPLETED"
				test_report.CREATED_BY = request.user
				test_report.UPDATED_BY = request.user
				test_report.save()
				test_report.FRIENDLY_UID = "REP-%08d"%(test_report.id)
				test_report.save()

				# Pre-calculate ECG results to solve report lag and apply algorithmic fixes
				try:
					processed_results = process_can_test_data(test_report)
					if processed_results:
						test_report.TEST_RESULT = json.dumps(processed_results)
						test_report.save()
				except Exception as e:
					print("Pre-calculation failed: ", e)
				
			medical_test_result['test_entry_id'] = medical_test.FRIENDLY_UID
			medical_test_result['current_test_code'] = medical_test.MEDICALTESTMASTER.CODE
	
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			medical_test_result['test_entry_id'] = None
			medical_test_result['current_test_code'] = None
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test_result


def vpt_ultra_other(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE="TM-18", DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").exists():
			device_details = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").first()
		else:
			device_details = dict()
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		medical_test['medical_device'] = medical_device
		medical_test['device_details'] = device_details
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		risk = str(test_interpertation.RANGES['Risk'])
		normal = str(test_interpertation.RANGES['Normal'])
		mild = str(test_interpertation.RANGES['Mild'])
		severe = str(test_interpertation.RANGES['Severe'])
		moderate = str(test_interpertation.RANGES['Moderate'])
		bmi_normal = str(test_interpertation.RANGES['BMI']['Normal'])
		bmi_over_weight = str(test_interpertation.RANGES['BMI']['Over Weight'])
		bmi_obese = str(test_interpertation.RANGES['BMI']['Obese'])
		bmi_under_weight = str(test_interpertation.RANGES['BMI']['Underweight'])
		abi_normal = str(test_interpertation.RANGES['ABI']['Normal'])
		abi_mild = str(test_interpertation.RANGES['ABI']['Mild'])
		abi_severe = str(test_interpertation.RANGES['ABI']['Severe'])
		abi_gangrene = str(test_interpertation.RANGES['ABI']['Gangrene'])
		abi_moderate = str(test_interpertation.RANGES['ABI']['Moderate'])
		abi_calcified = str(test_interpertation.RANGES['ABI']['Calcified'])
		medical_test['normal'] = normal
		medical_test['risk'] = risk
		medical_test['mild'] = mild
		medical_test['severe'] = severe
		medical_test['moderate'] = moderate
		medical_test['bmi_normal'] = bmi_normal
		medical_test['bmi_over_weight'] = bmi_over_weight
		medical_test['bmi_obese'] = bmi_obese
		medical_test['bmi_under_weight'] = bmi_under_weight
		medical_test['abi_normal'] = abi_normal
		medical_test['abi_mild'] = abi_mild
		medical_test['abi_severe'] = abi_severe
		medical_test['abi_gangrene'] = abi_gangrene
		medical_test['abi_moderate'] = abi_moderate
		medical_test['abi_calcified'] = abi_calcified
		normal = normal.split("-")
		mild = mild.split("-")
		severe = severe.split("-")
		moderate = moderate.split("-")
		risk = risk.replace(">", "")
		abi_mild = abi_mild.split("-")
		abi_severe = abi_severe.split("-")
		abi_gangrene = abi_gangrene.replace("<", "")
		abi_moderate = abi_moderate.split("-")
		abi_calcified = abi_calcified.replace(">", "")
	
		if option['test_code'] and option['test_entry']:
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			vpt_ultra_test_values = dict()
			for medical_test_value in medical_tests:
				tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
				
				other_result = ""
				other_avg = 0.0
				other_count = 0
				for tx_test in tx_test_entries[0:12]:
					if tx_test.KEY_VALUE.isalpha():
						pass
					elif tx_test.KEY_VALUE:
						other_avg = other_avg + float(tx_test.KEY_VALUE)
						other_count = other_count +1

				if other_count != 0 and other_avg:
					other_avg = round(float(other_avg / other_count), 1)
					if float(other_avg) >= float(normal[0]) and float(other_avg) <= float(normal[1]):
						other_result = "Normal"
					elif float(other_avg) >= float(mild[0]) and float(other_avg) <= float(mild[1]):
						other_result = "Mild"
					elif float(other_avg) >= float(severe[0]) and float(other_avg) <= float(severe[1]):
						other_result = "Severe"
					elif float(other_avg) >= float(moderate[0]) and float(other_avg) <= float(moderate[1]):
						other_result = "Moderate"
					elif float(other_avg) >= float(risk):
						other_result = "Risk"
					else:
						other_result = "Not in Range"
					vpt_ultra_test_values['other_result'] = ["%.1f"%(other_avg), other_result]
				else:
					vpt_ultra_test_values['other_result'] = ["No Data", ""]

				if patient.HEIGHT and patient.WEIGHT:
					if float(patient.HEIGHT) and float(patient.WEIGHT):
						bmi_normal = bmi_normal.split("-")
						bmi_over_weight = bmi_over_weight.split("-")
						bmi_obese_value = bmi_obese.replace(">", "")
						bmi_under_weight = bmi_under_weight.replace("<", "")
						bmi_avg = round(float(float(patient.WEIGHT)/((float(patient.HEIGHT)/100)*(float(patient.HEIGHT)/100))), 2)
						if float(bmi_avg) >= float(bmi_normal[0]) and float(bmi_avg) <= float(bmi_normal[1]):
							bmi_result = "Normal"
						elif float(bmi_avg) >= float(bmi_over_weight[0]) and float(bmi_avg) <= float(bmi_over_weight[1]):
							bmi_result = "Over Weight"
						elif float(bmi_avg) > float(bmi_obese_value):
							bmi_result = "Obese"
						elif float(bmi_avg) <= float(bmi_under_weight):
							bmi_result = "Under Weight"
					else:
						bmi_avg = 0.0
						bmi_result = "Invalid Data"
					vpt_ultra_test_values['bmi_result'] = [bmi_avg, bmi_result]
				# else:
				# 	vpt_ultra_test_values['bmi_result'] = ["", ""]

				medical_test["vpt_ultra_test_values"] = vpt_ultra_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(vpt_ultra_test_values)
				report.save()
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def vpt_medical_test_entry(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	extra_list = ['F-29', 'F-30', 'F-31', 'F-32', 'H-28', 'H-29', 'H-30', 'H-31',]
	try:
		patient = p_dict['patient_uid'].strip()
		doctor = p_dict.get('doctor_uid', None)
		examiner = p_dict.get('examiner_uid', None)
		app_code = p_dict['app_code'].strip()
		test_code = p_dict['test_code'].strip()
		test_entry = p_dict.get('test_entry', None)
		kodys_apps = MA_MEDICALAPPS.objects.filter(CODE=app_code, DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=app_code, DATAMODE="A").last()
		if test_code:
			medical_test_type  = MA_MEDICALTESTMASTER.objects.filter(CODE=test_code, DATAMODE="A").first()
			if doctor.strip() != "no_uid":
				doctor = TX_HCP.objects.get(UID=doctor, DATAMODE="A")
			else:
				doctor = ""
			if examiner.strip() != "no_uid":
				examiner = TX_HCP.objects.get(UID=examiner, DATAMODE="A")
			else:
				examiner = ""
			patients = TX_PATIENTS.objects.get(UID=patient, DATAMODE="A")
			test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=test_code, DATAMODE="A")
			normal = str(test_interpertation.RANGES['Normal'])
			risk = str(test_interpertation.RANGES['Risk'])
			mild = str(test_interpertation.RANGES['Mild'])
			severe = str(test_interpertation.RANGES['Severe'])
			moderate = str(test_interpertation.RANGES['Moderate'])
			bmi_normal = str(test_interpertation.RANGES['BMI']['Normal'])
			bmi_over_weight = str(test_interpertation.RANGES['BMI']['Over Weight'])
			bmi_obese = str(test_interpertation.RANGES['BMI']['Obese'])
			bmi_under_weight = str(test_interpertation.RANGES['BMI']['Underweight'])
			abi_normal = str(test_interpertation.RANGES['ABI']['Normal'])
			abi_mild = str(test_interpertation.RANGES['ABI']['Mild'])
			abi_severe = str(test_interpertation.RANGES['ABI']['Severe'])
			abi_gangrene = str(test_interpertation.RANGES['ABI']['Gangrene'])
			abi_moderate = str(test_interpertation.RANGES['ABI']['Moderate'])
			abi_calcified = str(test_interpertation.RANGES['ABI']['Calcified'])
			normal = normal.split("-")
			mild = mild.split("-")
			severe = severe.split("-")
			moderate = moderate.split("-")
			risk = risk.replace(">", "")
			if test_entry and TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, MEDICALTESTMASTER__CODE=test_code).exists():
				medical_test_fields = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, MEDICALTEST__MEDICALTESTMASTER__CODE=test_code)
				for test_fields in medical_test_fields:
					if test_fields.MEDICALTESTFIELDS.KEY_CODE in extra_list:
						if "F" in test_fields.KEY_CODE:
							KEY_NAME = test_fields.KEY_CODE.replace("F", "K")
							test_fields.KEY_NAME = p_dict.get(KEY_NAME, "")
						elif "H" in test_fields.KEY_CODE:
							KEY_NAME = test_fields.KEY_CODE.replace("H", "K")
							test_fields.KEY_NAME = p_dict.get(KEY_NAME, "")
						test_fields.MEDICALTESTFIELDS.KEY_NAME = p_dict.get(KEY_NAME, "")
						test_fields.MEDICALTESTFIELDS.save()
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_fields.KEY_VALUE = test_field_value
						if test_field_value.isalpha():
							if len(test_field_value) == 1:
								if test_field_value == "Y":
									test_fields.KEY_VALUE_STATUS = "Normal"
								else:								
									test_fields.KEY_VALUE_STATUS = "Not_in_Range"
							else:	
								test_fields.KEY_VALUE_STATUS = "Not_in_Range"
						elif float(test_field_value) >= float(normal[0]) and float(test_field_value) <= float(normal[1]):
							test_fields.KEY_VALUE_STATUS = "Normal"
						elif float(test_field_value) >= float(mild[0]) and float(test_field_value) <= float(mild[1]):
							test_fields.KEY_VALUE_STATUS = "Mild"
						elif float(test_field_value) >= float(severe[0]) and float(test_field_value) <= float(severe[1]):
							test_fields.KEY_VALUE_STATUS = "Severe"
						elif float(test_field_value) >= float(moderate[0]) and float(test_field_value) <= float(moderate[1]):
							test_fields.KEY_VALUE_STATUS = "Moderate"
						elif float(test_field_value) >= float(risk):
							test_fields.KEY_VALUE_STATUS = "Risk"
						else:
							test_fields.KEY_VALUE_STATUS = "Not_in_Range"
					else:
						test_fields.KEY_VALUE = ""
						test_fields.KEY_VALUE_STATUS = "No_Data"
					test_fields.save()
				medical_test = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, DATAMODE="A").first()
			else:
				medical_test = TX_MEDICALTESTS()
				medical_test.UID = uuid.uuid4().hex[:30]
				medical_test.MEDICALTESTMASTER = medical_test_type
				medical_test.PATIENT = patients
				medical_test.INTERPERTATION = test_interpertation.RANGES
				if doctor:
					medical_test.DOCTOR = doctor
				if examiner:
					medical_test.EXAMINER = examiner
				medical_test.REPORTED_ON = datetime.datetime.now()
				medical_test.save()
				medical_test.FRIENDLY_UID = "TST-%08d"%(medical_test.id)
				medical_test.save() 

				medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A")
				for test_fields in medical_test_fields:
					test_entries = TX_MEDICALTESTENTRIES()
					test_entries.UID = uuid.uuid4().hex[:30]
					test_entries.MEDICALTEST = medical_test
					test_entries.MEDICALTESTFIELDS = test_fields
					# if test_fields.KEY_NAME:
					if test_fields.KEY_CODE in extra_list:
						if "F" in test_fields.KEY_CODE:
							KEY_NAME = test_fields.KEY_CODE.replace("F", "K")
							test_entries.KEY_NAME = p_dict.get(KEY_NAME, "")
						elif "H" in test_fields.KEY_CODE:
							KEY_NAME = test_fields.KEY_CODE.replace("H", "K")
							test_entries.KEY_NAME = p_dict.get(KEY_NAME, "")
						test_fields.KEY_NAME = p_dict.get(KEY_NAME, "")
						test_fields.save()
					else:
						test_entries.KEY_NAME = test_fields.KEY_NAME
					test_entries.KEY_CODE = test_fields.KEY_CODE
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_entries.KEY_VALUE = test_field_value
						if test_field_value.isalpha():
							if len(test_field_value) == 1:
								if test_field_value == "Y":
									test_entries.KEY_VALUE_STATUS = "Normal"
								else:								
									test_entries.KEY_VALUE_STATUS = "Not_in_Range"
							else:	
								test_entries.KEY_VALUE_STATUS = "Not_in_Range"
						elif float(test_field_value) >= float(normal[0]) and float(test_field_value) <= float(normal[1]):
							test_entries.KEY_VALUE_STATUS = "Normal"
						elif float(test_field_value) >= float(mild[0]) and float(test_field_value) <= float(mild[1]):
							test_entries.KEY_VALUE_STATUS = "Mild"
						elif float(test_field_value) >= float(severe[0]) and float(test_field_value) <= float(severe[1]):
							test_entries.KEY_VALUE_STATUS = "Severe"
						elif float(test_field_value) >= float(moderate[0]) and float(test_field_value) <= float(moderate[1]):
							test_entries.KEY_VALUE_STATUS = "Moderate"
						elif float(test_field_value) >= float(risk):
							test_entries.KEY_VALUE_STATUS = "Risk"
						else:
							test_entries.KEY_VALUE_STATUS = "Not_in_Range"
					else:
						test_entries.KEY_VALUE = ""
						test_entries.KEY_VALUE_STATUS = "No_Data"
					test_entries.save()
				
			if TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A").exists():
				pass
			else:
				test_report = TX_MEDICALTESTREPORTS()
				test_report.UID = uuid.uuid4().hex[:30]
				test_report.MEDICALTEST = medical_test
				test_report.TEMPERATURE_SCALE = "Volts"
				test_report.REFERRED_BY = referred_by_medical_test_type.REFERRED_BY
				test_report.REPORTED_ON = datetime.datetime.now()
				test_report.TEST_STATUS = "COMPLETED"
				test_report.CREATED_BY = request.user
				test_report.UPDATED_BY = request.user
				test_report.save()
				test_report.FRIENDLY_UID = "REP-%08d"%(test_report.id)
				test_report.save()

				# Pre-calculate ECG results to solve report lag and apply algorithmic fixes
				try:
					processed_results = process_can_test_data(test_report)
					if processed_results:
						test_report.TEST_RESULT = json.dumps(processed_results)
						test_report.save()
				except Exception as e:
					print("Pre-calculation failed: ", e)
			medical_test_result['test_entry_id'] = medical_test.FRIENDLY_UID
			medical_test_result['current_test_code'] = medical_test.MEDICALTESTMASTER.CODE
	
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			medical_test_result['test_entry_id'] = None
			medical_test_result['current_test_code'] = None
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test_result


def vpt_foot(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").last()
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").exists():
			device_details = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").first()
		else:
			device_details = dict()
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		medical_test['medical_device'] = medical_device
		medical_test['device_details'] = device_details
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		risk = str(test_interpertation.RANGES['Risk'])
		normal = str(test_interpertation.RANGES['Normal'])
		mild = str(test_interpertation.RANGES['Mild'])
		severe = str(test_interpertation.RANGES['Severe'])
		moderate = str(test_interpertation.RANGES['Moderate'])
		bmi_normal = str(test_interpertation.RANGES['BMI']['Normal'])
		bmi_over_weight = str(test_interpertation.RANGES['BMI']['Over Weight'])
		bmi_obese = str(test_interpertation.RANGES['BMI']['Obese'])
		bmi_under_weight = str(test_interpertation.RANGES['BMI']['Underweight'])
		abi_normal = str(test_interpertation.RANGES['ABI']['Normal'])
		abi_mild = str(test_interpertation.RANGES['ABI']['Mild'])
		abi_severe = str(test_interpertation.RANGES['ABI']['Severe'])
		abi_gangrene = str(test_interpertation.RANGES['ABI']['Gangrene'])
		abi_moderate = str(test_interpertation.RANGES['ABI']['Moderate'])
		abi_calcified = str(test_interpertation.RANGES['ABI']['Calcified'])
		medical_test['normal'] = normal
		medical_test['risk'] = risk
		medical_test['mild'] = mild
		medical_test['severe'] = severe
		medical_test['moderate'] = moderate
		medical_test['bmi_normal'] = bmi_normal
		medical_test['bmi_over_weight'] = bmi_over_weight
		medical_test['bmi_obese'] = bmi_obese
		medical_test['bmi_under_weight'] = bmi_under_weight
		medical_test['abi_normal'] = abi_normal
		medical_test['abi_mild'] = abi_mild
		medical_test['abi_severe'] = abi_severe
		medical_test['abi_gangrene'] = abi_gangrene
		medical_test['abi_moderate'] = abi_moderate
		medical_test['abi_calcified'] = abi_calcified
		if option['test_entry']:
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			request.session["referred"] = ""
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			request.session['test_type'] = medical_test_type.ORGAN_TYPE
			request.session['test_for'] = test_report.TEST_TYPE 
			medical_test['test_type'] = medical_test_type.ORGAN_TYPE 
			medical_test['test_for'] = test_report.TEST_TYPE 

		if option['test_code'] and option['test_entry']:
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			if medical_tests:
				vpt_test_values = dict()
				for medical_test_value in medical_tests:
					tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
				 	right_foot_result, left_foot_result = "", ""
					right_avg = 0.0
					left_avg = 0.0
					right_count = 0
					left_count = 0
					for tx_test in tx_test_entries[0:6]:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							right_avg = right_avg + float(tx_test.KEY_VALUE)
							right_count = right_count +1
					for tx_test in tx_test_entries[8:14]:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							left_avg = left_avg + float(tx_test.KEY_VALUE)
							left_count = left_count +1
					normal = normal.split("-")
					mild = mild.split("-")
					severe = severe.split("-")
					moderate = moderate.split("-")
					risk = risk.replace(">", "")
					# abi_normal = abi_normal.split("-")
					abi_mild = abi_mild.split("-")
					abi_severe = abi_severe.split("-")
					abi_gangrene = abi_gangrene.replace("<", "")
					abi_moderate = abi_moderate.split("-")
					abi_calcified = abi_calcified.replace(">", "")

					if right_count != 0 and right_avg:
						right_avg = round(float(right_avg / right_count), 1)
						if float(right_avg) >= float(normal[0]) and float(right_avg) <= float(normal[1]):
							right_foot_result = "Normal"
						elif float(right_avg) >= float(mild[0]) and float(right_avg) <= float(mild[1]):
							right_foot_result = "Mild"
						elif float(right_avg) >= float(severe[0]) and float(right_avg) <= float(severe[1]):
							right_foot_result = "Severe"
						elif float(right_avg) >= float(moderate[0]) and float(right_avg) <= float(moderate[1]):
							right_foot_result = "Moderate"
						elif float(right_avg) >= float(risk):
							right_foot_result = "Risk"
						else:
							right_foot_result = "Not in Range"
						vpt_test_values['right_foot_result'] = ["%.1f"%(right_avg), right_foot_result]
					else:
						vpt_test_values['right_foot_result'] = ["No Data", ""]

					if left_count != 0 and left_avg:
						left_avg = round(float(left_avg / left_count), 1)
						if float(left_avg) >= float(normal[0]) and float(left_avg) <= float(normal[1]):
							left_foot_result = "Normal"
						elif float(left_avg) >= float(mild[0]) and float(left_avg) <= float(mild[1]):
							left_foot_result = "Mild"
						elif float(left_avg) >= float(severe[0]) and float(left_avg) <= float(severe[1]):
							left_foot_result = "Severe"
						elif float(left_avg) >= float(moderate[0]) and float(left_avg) <= float(moderate[1]):
							left_foot_result = "Moderate"
						elif float(left_avg) >= float(risk):
							left_foot_result = "Risk"
						else:
							left_foot_result = "Not in Range"
						vpt_test_values['left_foot_result'] = ["%.1f"%(left_avg), left_foot_result]
					else:
						vpt_test_values['left_foot_result'] = ["No Data", ""]
					if patient.HEIGHT and patient.WEIGHT:
						if float(patient.HEIGHT) and float(patient.WEIGHT):
							bmi_normal = bmi_normal.split("-")
							bmi_over_weight = bmi_over_weight.split("-")
							bmi_obese_value = bmi_obese.replace(">", "")
							bmi_under_weight_value = bmi_under_weight.replace("<", "")
							bmi_avg = round(float(float(patient.WEIGHT)/((float(patient.HEIGHT)/100)*(float(patient.HEIGHT)/100))), 2)
							if float(bmi_avg) >= float(bmi_normal[0]) and float(bmi_avg) <= float(bmi_normal[1]):
								bmi_result = "Normal"
							elif float(bmi_avg) >= float(bmi_over_weight[0]) and float(bmi_avg) <= float(bmi_over_weight[1]):
								bmi_result = "Over Weight"
							elif float(bmi_avg) > float(bmi_obese_value):
								bmi_result = "Obese"
							elif float(bmi_avg) <= float(bmi_under_weight_value):
								bmi_result = "Under Weight"
						else:
							bmi_avg = 0.0
							bmi_result = "Invalid Data"
						vpt_test_values['bmi_result'] = [bmi_avg, bmi_result]
					# else:
					# 	vpt_test_values['bmi_result'] = ["", ""]

					if tx_test_entries[20].KEY_VALUE and tx_test_entries[22].KEY_VALUE:
						if tx_test_entries[20].KEY_VALUE.isalpha() or tx_test_entries[22].KEY_VALUE.isalpha():
							vpt_test_values['right_abi_result'] = ["No Data", ""]
						else:
							if float(tx_test_entries[20].KEY_VALUE) and float(tx_test_entries[22].KEY_VALUE):
								try:
									denominator = float(tx_test_entries[22].KEY_VALUE)
									if denominator != 0:
										right_abi = round(float(float(tx_test_entries[20].KEY_VALUE)/denominator), 2)
									else:
					right_abi = 0.0
								except:
									right_abi = 0.0
								if float(right_abi) >= float(abi_severe[0]) and float(right_abi) <= float(abi_severe[1]):
									right_abi_result = "Severe"
								elif float(right_abi) >= float(abi_moderate[0]) and float(right_abi) <= float(abi_moderate[1]):
									right_abi_result = "Moderate"
								elif float(right_abi) >= float(abi_mild[0]) and float(right_abi) <= float(abi_mild[1]):
									right_abi_result = "Mild"
								elif float(right_abi) >= float(0.7) and float(right_abi) <= float(1.3):
									right_abi_result = "Normal"
								elif float(right_abi) > float(abi_calcified):
										right_abi_result = "Calcified"
								elif float(right_abi) < float(abi_gangrene):
									right_abi_result = "Gangrene"
								else:
									right_abi_result = "Not in Range"
							else:
								right_abi = 0.0
								right_abi_result = "No Data"
							vpt_test_values['right_abi_result'] = ["%.2f"%(right_abi), right_abi_result]
					else:
						right_abi = "No Data"
						vpt_test_values['right_abi_result'] = ["No Data", ""]

					if tx_test_entries[21].KEY_VALUE and tx_test_entries[23].KEY_VALUE:
						if tx_test_entries[21].KEY_VALUE.isalpha() and tx_test_entries[23].KEY_VALUE.isalpha():
							vpt_test_values['left_abi_result'] = ["No Data", ""]
						else:
							if float(tx_test_entries[21].KEY_VALUE) and float(tx_test_entries[23].KEY_VALUE):
								left_abi = round(float(float(tx_test_entries[21].KEY_VALUE)/float(tx_test_entries[23].KEY_VALUE)), 2)
								if float(left_abi) >= float(abi_severe[0]) and float(left_abi) <= float(abi_severe[1]):
									left_abi_result = "Severe"
								elif float(left_abi) >= float(abi_moderate[0]) and float(left_abi) <= float(abi_moderate[1]):
									left_abi_result = "Moderate"
								elif float(left_abi) >= float(abi_mild[0]) and float(left_abi) <= float(abi_mild[1]):
									left_abi_result = "Mild"
								elif float(left_abi) >= float(0.7) and float(left_abi) <= float(1.3):
									left_abi_result = "Normal"
								elif float(left_abi) >= float(abi_calcified):
										left_abi_result = "Calcified"
								elif float(left_abi) <= float(abi_gangrene):
									left_abi_result = "Gangrene"
								else:
									left_abi_result = "Not in Range"
							else:
								left_abi = 0.0
								left_abi_result = "No Data"
							vpt_test_values['left_abi_result'] = ["%.2f"%(left_abi), left_abi_result]
				
				medical_test["vpt_test_values"] = vpt_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(vpt_test_values)
				report.save()

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def vpt_hand(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").last()
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").exists():
			device_details = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").first()
		else:
			device_details = dict()
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		medical_test['medical_device'] = medical_device
		medical_test['device_details'] = device_details
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		risk = str(test_interpertation.RANGES['Risk'])
		normal = str(test_interpertation.RANGES['Normal'])
		mild = str(test_interpertation.RANGES['Mild'])
		severe = str(test_interpertation.RANGES['Severe'])
		moderate = str(test_interpertation.RANGES['Moderate'])
		bmi_normal = str(test_interpertation.RANGES['BMI']['Normal'])
		bmi_over_weight = str(test_interpertation.RANGES['BMI']['Over Weight'])
		bmi_obese = str(test_interpertation.RANGES['BMI']['Obese'])
		bmi_under_weight = str(test_interpertation.RANGES['BMI']['Underweight'])
		abi_normal = str(test_interpertation.RANGES['ABI']['Normal'])
		abi_mild = str(test_interpertation.RANGES['ABI']['Mild'])
		abi_severe = str(test_interpertation.RANGES['ABI']['Severe'])
		abi_gangrene = str(test_interpertation.RANGES['ABI']['Gangrene'])
		abi_moderate = str(test_interpertation.RANGES['ABI']['Moderate'])
		abi_calcified = str(test_interpertation.RANGES['ABI']['Calcified'])
		medical_test['normal'] = normal
		medical_test['risk'] = risk
		medical_test['mild'] = mild
		medical_test['severe'] = severe
		medical_test['moderate'] = moderate
		medical_test['bmi_normal'] = bmi_normal
		medical_test['bmi_over_weight'] = bmi_over_weight
		medical_test['bmi_obese'] = bmi_obese
		medical_test['bmi_under_weight'] = bmi_under_weight
		medical_test['abi_normal'] = abi_normal
		medical_test['abi_mild'] = abi_mild
		medical_test['abi_severe'] = abi_severe
		medical_test['abi_gangrene'] = abi_gangrene
		medical_test['abi_moderate'] = abi_moderate
		medical_test['abi_calcified'] = abi_calcified
		if option['test_entry']:
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			request.session["referred"] = ""
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			request.session['test_type'] = medical_test_type.ORGAN_TYPE
			request.session['test_for'] = test_report.TEST_TYPE 
			medical_test['test_type'] = medical_test_type.ORGAN_TYPE 
			medical_test['test_for'] = test_report.TEST_TYPE 
		if option['test_code'] and option['test_entry']:
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			if medical_tests:
				vpt_test_values = dict()
				for medical_test_value in medical_tests:
					tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
					right_hand_result, left_hand_result = "", ""
					right_avg = 0.0
					left_avg = 0.0
					right_count = 0
					left_count = 0
					for tx_test in tx_test_entries[0:7]:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							right_avg = right_avg + float(tx_test.KEY_VALUE)
							right_count = right_count +1
					for tx_test in tx_test_entries[7:14]:
						if tx_test.KEY_VALUE.isalpha():
							pass
						elif tx_test.KEY_VALUE:
							left_avg = left_avg + float(tx_test.KEY_VALUE)
							left_count = left_count +1
					normal = normal.split("-")
					mild = mild.split("-")
					severe = severe.split("-")
					moderate = moderate.split("-")
					risk = risk.replace(">", "")
					abi_mild = abi_mild.split("-")
					abi_severe = abi_severe.split("-")
					abi_gangrene = abi_gangrene.replace("<", "")
					abi_moderate = abi_moderate.split("-")
					abi_calcified = abi_calcified.replace(">", "")

					if right_count != 0 and right_avg:
						right_avg = round(float(right_avg / right_count), 1)
						if float(right_avg) >= float(normal[0]) and float(right_avg) <= float(normal[1]):
							right_hand_result = "Normal"
						elif float(right_avg) >= float(mild[0]) and float(right_avg) <= float(mild[1]):
							right_hand_result = "Mild"
						elif float(right_avg) >= float(severe[0]) and float(right_avg) <= float(severe[1]):
							right_hand_result = "Severe"
						elif float(right_avg) >= float(moderate[0]) and float(right_avg) <= float(moderate[1]):
							right_hand_result = "Moderate"
						elif float(right_avg) >= float(risk):
							right_hand_result = "Risk"
						else:
							right_hand_result = "Not in Range"
						vpt_test_values['right_hand_result'] = ["%.1f"%(right_avg), right_hand_result]
					else:
						vpt_test_values['right_hand_result'] = ["No Data", ""]

					if left_count != 0 and left_avg:
						left_avg = round(float(left_avg / left_count), 1)
						if float(left_avg) >= float(normal[0]) and float(left_avg) <= float(normal[1]):
							left_hand_result = "Normal"
						elif float(left_avg) >= float(mild[0]) and float(left_avg) <= float(mild[1]):
							left_hand_result = "Mild"
						elif float(left_avg) >= float(severe[0]) and float(left_avg) <= float(severe[1]):
							left_hand_result = "Severe"
						elif float(left_avg) >= float(moderate[0]) and float(left_avg) <= float(moderate[1]):
							left_hand_result = "Moderate"
						elif float(left_avg) >= float(risk):
							left_hand_result = "Risk"
						else:
							left_hand_result = "Not in Range"
						vpt_test_values['left_hand_result'] = ["%.1f"%(left_avg), left_hand_result]
					else:
						vpt_test_values['left_hand_result'] = ["No Data", ""]
					if patient.HEIGHT and patient.WEIGHT:
						if float(patient.HEIGHT) and float(patient.WEIGHT):
							bmi_normal = bmi_normal.split("-")
							bmi_over_weight = bmi_over_weight.split("-")
							bmi_obese_value = bmi_obese.replace(">", "")
							bmi_under_weight_value = bmi_under_weight.replace("<", "")
							bmi_avg = round(float(float(patient.WEIGHT)/((float(patient.HEIGHT)/100)*(float(patient.HEIGHT)/100))), 2)
							if float(bmi_avg) >= float(bmi_normal[0]) and float(bmi_avg) <= float(bmi_normal[1]):
								bmi_result = "Normal"
							elif float(bmi_avg) >= float(bmi_over_weight[0]) and float(bmi_avg) <= float(bmi_over_weight[1]):
								bmi_result = "Over Weight"
							elif float(bmi_avg) > float(bmi_obese_value):
								bmi_result = "Obese"
							elif float(bmi_avg) <= float(bmi_under_weight_value):
								bmi_result = "Under Weight"
						else:
							bmi_avg = 0.0
							bmi_result = "Invalid Data"
						vpt_test_values['bmi_result'] = [bmi_avg, bmi_result]
					# else:
					# 	vpt_test_values['bmi_result'] = ["", ""]

					if tx_test_entries[18].KEY_VALUE and tx_test_entries[20].KEY_VALUE:
						if tx_test_entries[18].KEY_VALUE.isalpha() or tx_test_entries[20].KEY_VALUE.isalpha():
							vpt_test_values['right_abi_result'] = ["No Data", ""]
						else:
							right_abi = round(float(float(tx_test_entries[18].KEY_VALUE)/float(tx_test_entries[20].KEY_VALUE)), 1)
							if float(right_abi) >= float(abi_severe[0]) and float(right_abi) <= float(abi_severe[1]):
								right_abi_result = "Severe"
							elif float(right_abi) >= float(abi_moderate[0]) and float(right_abi) <= float(abi_moderate[1]):
								right_abi_result = "Moderate"
							elif float(right_abi) >= float(abi_mild[0]) and float(right_abi) <= float(abi_mild[1]):
								right_abi_result = "Mild"
							elif float(right_abi) >= float(0.7) and float(right_abi) <= float(1.3):
								right_abi_result = "Normal"
							elif float(right_abi) > float(abi_calcified):
									right_abi_result = "Calcified"
							elif float(right_abi) < float(abi_gangrene):
								right_abi_result = "Gangrene"
							else:
								right_abi_result = "Not in Range"
							vpt_test_values['right_abi_result'] = ["%.1f"%(right_abi), right_abi_result]
					else:
						right_abi = "No Data"
						vpt_test_values['right_abi_result'] = ["No Data", ""]

					if tx_test_entries[19].KEY_VALUE and tx_test_entries[21].KEY_VALUE:
						if tx_test_entries[19].KEY_VALUE.isalpha() and tx_test_entries[21].KEY_VALUE.isalpha():
							vpt_test_values['left_abi_result'] = ["No Data", ""]
						else:
							left_abi = round(float(float(tx_test_entries[19].KEY_VALUE)/float(tx_test_entries[21].KEY_VALUE)), 1)
							if float(left_abi) >= float(abi_severe[0]) and float(left_abi) <= float(abi_severe[1]):
								left_abi_result = "Severe"
							elif float(left_abi) >= float(abi_moderate[0]) and float(left_abi) <= float(abi_moderate[1]):
								left_abi_result = "Moderate"
							elif float(left_abi) >= float(abi_mild[0]) and float(left_abi) <= float(abi_mild[1]):
								left_abi_result = "Mild"
							elif float(left_abi) >= float(0.7) and float(left_abi) <= float(1.3):
								left_abi_result = "Normal"
							elif float(left_abi) > float(abi_calcified):
									left_abi_result = "Calcified"
							elif float(left_abi) < float(abi_gangrene):
								left_abi_result = "Gangrene"
							else:
								left_abi_result = "Not in Range"
							vpt_test_values['left_abi_result'] = ["%.1f"%(left_abi), left_abi_result]
					else:
						left_abi = "No Data"
						vpt_test_values['left_abi_result'] = ["No Data", ""]
				
				medical_test["vpt_test_values"] = vpt_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(vpt_test_values)
				report.save()

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def vpt_other_medical_test_entry(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	try:
		test_for = p_dict.get('test_for',"Other")

		patient = p_dict['patient_uid'].strip()
		doctor = p_dict.get('doctor_uid', None)
		examiner = p_dict.get('examiner_uid', None)
		app_code = p_dict['app_code'].strip()
		test_code = p_dict['test_code'].strip()
		test_entry = p_dict.get('test_entry', None)
		kodys_apps = MA_MEDICALAPPS.objects.filter(CODE=app_code, DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=app_code, DATAMODE="A").last()
		if test_code:
			medical_test_type  = MA_MEDICALTESTMASTER.objects.filter(CODE=test_code, DATAMODE="A").first()
			test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=test_code, DATAMODE="A")
			risk = str(test_interpertation.RANGES['Risk'])
			normal = str(test_interpertation.RANGES['Normal'])
			mild = str(test_interpertation.RANGES['Mild'])
			severe = str(test_interpertation.RANGES['Severe'])
			moderate = str(test_interpertation.RANGES['Moderate'])
			bmi_normal = str(test_interpertation.RANGES['BMI']['Normal'])
			bmi_over_weight = str(test_interpertation.RANGES['BMI']['Over Weight'])
			bmi_obese = str(test_interpertation.RANGES['BMI']['Obese'])
			bmi_under_weight = str(test_interpertation.RANGES['BMI']['Underweight'])
			abi_normal = str(test_interpertation.RANGES['ABI']['Normal'])
			abi_mild = str(test_interpertation.RANGES['ABI']['Mild'])
			abi_severe = str(test_interpertation.RANGES['ABI']['Severe'])
			abi_gangrene = str(test_interpertation.RANGES['ABI']['Gangrene'])
			abi_moderate = str(test_interpertation.RANGES['ABI']['Moderate'])
			abi_calcified = str(test_interpertation.RANGES['ABI']['Calcified'])
			normal = normal.split("-")
			mild = mild.split("-")
			severe = severe.split("-")
			moderate = moderate.split("-")
			risk = risk.replace(">", "")
			abi_mild = abi_mild.split("-")
			abi_severe = abi_severe.split("-")
			abi_gangrene = abi_gangrene.replace("<", "")
			abi_moderate = abi_moderate.split("-")
			abi_calcified = abi_calcified.replace(">", "")

			if doctor.strip() != "no_uid":
				doctor = TX_HCP.objects.get(UID=doctor, DATAMODE="A")
			else:
				doctor = ""
			if examiner.strip() != "no_uid":
				examiner = TX_HCP.objects.get(UID=examiner, DATAMODE="A")
			else:
				examiner = ""
			patients = TX_PATIENTS.objects.get(UID=patient, DATAMODE="A")
			if test_entry and TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, MEDICALTESTMASTER__CODE=test_code).exists():
				medical_test_fields = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, MEDICALTEST__MEDICALTESTMASTER__CODE=test_code)
				for test_fields in medical_test_fields:
					if "V" in test_fields.KEY_CODE:
						KEY_NAME = test_fields.KEY_CODE.replace("V", "K")
					if "B" in test_fields.KEY_CODE:
						KEY_NAME = test_fields.KEY_CODE.replace("B", "K")
					test_fields.KEY_NAME =  p_dict.get(KEY_NAME, "")
					test_fields.MEDICALTESTFIELDS.KEY_NAME = p_dict.get(KEY_NAME, "")
					test_fields.MEDICALTESTFIELDS.save()
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_fields.KEY_VALUE = test_field_value
						if test_field_value.isalpha():
							if len(test_field_value) == 1:
								if test_field_value == "Y":
									test_fields.KEY_VALUE_STATUS = "Normal"
								else:								
									test_fields.KEY_VALUE_STATUS = "Not_in_Range"
							else:								
								test_fields.KEY_VALUE_STATUS = "Not_in_Range"
						elif float(test_field_value) >= float(normal[0]) and float(test_field_value) <= float(normal[1]):
							test_fields.KEY_VALUE_STATUS = "Normal"
						elif float(test_field_value) >= float(mild[0]) and float(test_field_value) <= float(mild[1]):
							test_fields.KEY_VALUE_STATUS = "Mild"
						elif float(test_field_value) >= float(severe[0]) and float(test_field_value) <= float(severe[1]):
							test_fields.KEY_VALUE_STATUS = "Severe"
						elif float(test_field_value) >= float(moderate[0]) and float(test_field_value) <= float(moderate[1]):
							test_fields.KEY_VALUE_STATUS = "Moderate"
						elif float(test_field_value) >= float(risk):
							test_fields.KEY_VALUE_STATUS = "Risk"
						else:
							test_fields.KEY_VALUE_STATUS = "Not_in_Range"
					else:
						test_fields.KEY_VALUE = ""
						test_fields.KEY_VALUE_STATUS = "No_Data"
					test_fields.save()
				medical_test = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, DATAMODE="A").first()
			
			else:
				medical_test = TX_MEDICALTESTS()
				medical_test.UID = uuid.uuid4().hex[:30]
				medical_test.MEDICALTESTMASTER = medical_test_type
				medical_test.PATIENT = patients
				medical_test.INTERPERTATION = test_interpertation.RANGES
				if doctor:
					medical_test.DOCTOR = doctor
				if examiner:
					medical_test.EXAMINER = examiner
				medical_test.REPORTED_ON = datetime.datetime.now()
				medical_test.save()
				if test_entry:
					test_entry = test_entry.strip()
					medical_test.FRIENDLY_UID = test_entry
				else:
					medical_test.FRIENDLY_UID = "TST-%08d"%(medical_test.id)
				medical_test.save() 

				medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A")
				for test_fields in medical_test_fields:
					test_entries = TX_MEDICALTESTENTRIES()
					test_entries.UID = uuid.uuid4().hex[:30]
					test_entries.MEDICALTEST = medical_test
					test_entries.MEDICALTESTFIELDS = test_fields
					test_entries.KEY_CODE = test_fields.KEY_CODE
					if "V" in test_fields.KEY_CODE:
						KEY_NAME = test_fields.KEY_CODE.replace("V", "K")
					if "B" in test_fields.KEY_CODE:
						KEY_NAME = test_fields.KEY_CODE.replace("B", "K")
					test_entries.KEY_NAME =  p_dict.get(KEY_NAME, "")
					test_fields.KEY_NAME = p_dict.get(KEY_NAME, "")
					test_fields.save()
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_entries.KEY_VALUE = test_field_value
						if test_field_value.isalpha():
							if len(test_field_value) == 1:
								if test_field_value == "Y":
									test_entries.KEY_VALUE_STATUS = "Normal"
								else:								
									test_entries.KEY_VALUE_STATUS = "Not_in_Range"
							else:								
								test_entries.KEY_VALUE_STATUS = "Not_in_Range"
						elif float(test_field_value) >= float(normal[0]) and float(test_field_value) <= float(normal[1]):
							test_entries.KEY_VALUE_STATUS = "Normal"
						elif float(test_field_value) >= float(mild[0]) and float(test_field_value) <= float(mild[1]):
							test_entries.KEY_VALUE_STATUS = "Mild"
						elif float(test_field_value) >= float(severe[0]) and float(test_field_value) <= float(severe[1]):
							test_entries.KEY_VALUE_STATUS = "Severe"
						elif float(test_field_value) >= float(moderate[0]) and float(test_field_value) <= float(moderate[1]):
							test_entries.KEY_VALUE_STATUS = "Moderate"
						elif float(test_field_value) >= float(risk):
							test_entries.KEY_VALUE_STATUS = "Risk"
						else:
							test_entries.KEY_VALUE_STATUS = "Not_in_Range"
					else:
						test_entries.KEY_VALUE = ""
						test_entries.KEY_VALUE_STATUS = "No_Data"
					test_entries.save()
				
			if TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A").exists():
				pass
			else:
				test_report = TX_MEDICALTESTREPORTS()
				test_report.UID = uuid.uuid4().hex[:30]
				test_report.MEDICALTEST = medical_test
				test_report.TEMPERATURE_SCALE = "Volts"
				test_report.REFERRED_BY = referred_by_medical_test_type.REFERRED_BY
				if test_for:
					test_report.TEST_TYPE = test_for
				else:
					test_report.TEST_TYPE = "Other"
				test_report.REPORTED_ON = datetime.datetime.now()
				test_report.TEST_STATUS = "COMPLETED"
				test_report.CREATED_BY = request.user
				test_report.UPDATED_BY = request.user
				test_report.save()
				test_report.FRIENDLY_UID = "REP-%08d"%(test_report.id)
				test_report.save()

				# Pre-calculate ECG results to solve report lag and apply algorithmic fixes
				try:
					processed_results = process_can_test_data(test_report)
					if processed_results:
						test_report.TEST_RESULT = json.dumps(processed_results)
						test_report.save()
				except Exception as e:
					print("Pre-calculation failed: ", e)
				
			medical_test_result['test_entry_id'] = medical_test.FRIENDLY_UID
			medical_test_result['current_test_code'] = medical_test.MEDICALTESTMASTER.CODE
	
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			medical_test_result['test_entry_id'] = None
			medical_test_result['current_test_code'] = None
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test_result


def vpt_other(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE="TM-19", DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").exists():
			device_details = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").first()
		else:
			device_details = dict()
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		medical_test['medical_device'] = medical_device
		medical_test['device_details'] = device_details
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		risk = str(test_interpertation.RANGES['Risk'])
		normal = str(test_interpertation.RANGES['Normal'])
		mild = str(test_interpertation.RANGES['Mild'])
		severe = str(test_interpertation.RANGES['Severe'])
		moderate = str(test_interpertation.RANGES['Moderate'])
		bmi_normal = str(test_interpertation.RANGES['BMI']['Normal'])
		bmi_over_weight = str(test_interpertation.RANGES['BMI']['Over Weight'])
		bmi_obese = str(test_interpertation.RANGES['BMI']['Obese'])
		bmi_under_weight = str(test_interpertation.RANGES['BMI']['Underweight'])
		abi_normal = str(test_interpertation.RANGES['ABI']['Normal'])
		abi_mild = str(test_interpertation.RANGES['ABI']['Mild'])
		abi_severe = str(test_interpertation.RANGES['ABI']['Severe'])
		abi_gangrene = str(test_interpertation.RANGES['ABI']['Gangrene'])
		abi_moderate = str(test_interpertation.RANGES['ABI']['Moderate'])
		abi_calcified = str(test_interpertation.RANGES['ABI']['Calcified'])
		medical_test['normal'] = normal
		medical_test['risk'] = risk
		medical_test['mild'] = mild
		medical_test['severe'] = severe
		medical_test['moderate'] = moderate
		medical_test['bmi_normal'] = bmi_normal
		medical_test['bmi_over_weight'] = bmi_over_weight
		medical_test['bmi_obese'] = bmi_obese
		medical_test['bmi_under_weight'] = bmi_under_weight
		medical_test['abi_normal'] = abi_normal
		medical_test['abi_mild'] = abi_mild
		medical_test['abi_severe'] = abi_severe
		medical_test['abi_gangrene'] = abi_gangrene
		medical_test['abi_moderate'] = abi_moderate
		medical_test['abi_calcified'] = abi_calcified
		normal = normal.split("-")
		mild = mild.split("-")
		severe = severe.split("-")
		moderate = moderate.split("-")
		risk = risk.replace(">", "")
		abi_mild = abi_mild.split("-")
		abi_severe = abi_severe.split("-")
		abi_gangrene = abi_gangrene.replace("<", "")
		abi_moderate = abi_moderate.split("-")
		abi_calcified = abi_calcified.replace(">", "")
	
		if option['test_code'] and option['test_entry']:
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			vpt_test_values = dict()
			for medical_test_value in medical_tests:
				tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
			 	other_result = ""
				other_avg = 0.0
				other_count = 0
				i = 0
				for tx_test in tx_test_entries[0:12]:
					i = i+1
					if tx_test.KEY_VALUE.isalpha():
						pass
					elif tx_test.KEY_VALUE:
						other_avg = other_avg + float(tx_test.KEY_VALUE)
						other_count = other_count +1

				if other_count != 0 and other_avg:
					other_avg = round(float(other_avg / other_count), 1)
					if float(other_avg) >= float(normal[0]) and float(other_avg) <= float(normal[1]):
						other_result = "Normal"
					elif float(other_avg) >= float(mild[0]) and float(other_avg) <= float(mild[1]):
						other_result = "Mild"
					elif float(other_avg) >= float(severe[0]) and float(other_avg) <= float(severe[1]):
						other_result = "Severe"
					elif float(other_avg) >= float(moderate[0]) and float(other_avg) <= float(moderate[1]):
						other_result = "Moderate"
					elif float(other_avg) >= float(risk):
						other_result = "Risk"
					else:
						other_result = "Not in Range"
					vpt_test_values['other_result'] = ["%.1f"%(other_avg), other_result]
				else:
					vpt_test_values['other_result'] = ["No Data", ""]

				if patient.HEIGHT and patient.WEIGHT:
					if float(patient.HEIGHT) and float(patient.WEIGHT):
						bmi_normal = bmi_normal.split("-")
						bmi_over_weight = bmi_over_weight.split("-")
						bmi_obese_value = bmi_obese.replace(">", "")
						bmi_under_weight_value = bmi_under_weight.replace("<", "")
						bmi_avg = round(float(float(patient.WEIGHT)/((float(patient.HEIGHT)/100)*(float(patient.HEIGHT)/100))), 2)
						if float(bmi_avg) >= float(bmi_normal[0]) and float(bmi_avg) <= float(bmi_normal[1]):
							bmi_result = "Normal"
						elif float(bmi_avg) >= float(bmi_over_weight[0]) and float(bmi_avg) <= float(bmi_over_weight[1]):
							bmi_result = "Over Weight"
						elif float(bmi_avg) > float(bmi_obese_value):
							bmi_result = "Obese"
						elif float(bmi_avg) <= float(bmi_under_weight_value):
							bmi_result = "Under Weight"
					else:
						bmi_avg = 0.0
						bmi_result = "Invalid Data"
					vpt_test_values['bmi_result'] = [bmi_avg, bmi_result]

				medical_test["vpt_test_values"] = vpt_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(vpt_test_values)
				report.save()
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def generate_report(request, test_uid, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(UID=test_uid, DATAMODE="A")
		test_entries = TX_MEDICALTESTENTRIES()
		patient = p_dict['patient_uid'].strip()
		doctor = p_dict['doctor_uid'].strip()
		examiner = p_dict['examiner_uid'].strip()
		app_code = p_dict['app_code'].strip()
		kodys_apps = MA_MEDICALAPPS.objects.filter(CODE=app_code, DATAMODE="A")
		medical_test_type  = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A")
		doctors = TX_HCP.objects.get(UID=doctor, DATAMODE="A")
		examiner = TX_HCP.objects.get(UID=examiner, DATAMODE="A")
		patients = TX_PATIENTS.objects.get(UID=patient, DATAMODE="A")
		
		medical_test = TX_MEDICALTESTS()
		medical_test.UID = uuid.uuid4().hex[:30]
		medical_test.MEDICALTESTMASTER = medical_test_type
		medical_test.PATIENT = patients
		medical_test.DOCTOR = doctors
		medical_test.EXAMINER = examiner
		medical_test.REPORTED_ON = datetime.datetime.now()
		medical_test.save() 
		medical_test.FRIENDLY_UID = "TST-%08d"%(medical_test.id)
		medical_test.save() 
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test


def device_config_save(request, app_code, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		medical_device = MA_MEDICALAPPDEVICES.objects.filter(MEDICAL_APP__CODE=app_code,DATAMODE="A")
		if medical_device:
			medical_device = medical_device.first()
			medical_device.DEVICE_KEY    = p_dict.get('key',"")
			medical_device.DEVICE_CONFIG    = p_dict.get('mac_address_id',"")
			more_option = dict()
			if 'mode' in p_dict and 'gain' in p_dict:
				more_option["mode"] = p_dict['mode']
				more_option["gain"] = p_dict['gain']
				medical_device.DEVICE_MORE_OPTION = more_option
			medical_device.save()

		medical_device_status = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE__id=medical_device.id,DATAMODE="A")
		if medical_device_status:
			medical_device_status = medical_device_status.first()
		else:
			medical_device_status = TX_MEDICALDEVICESTATUS()
			medical_device_status.MEDICAL_DEVICE = medical_device
		medical_device_status.CONNECTION_STATUS = " "
		medical_device_status.CONNECTION_TYPE = p_dict.get('connection_type',"")
		medical_device_status.save()
		result, msg = ulo._setmsg(success_msg, error_msg, True)
	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def email_report(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	manuals = dict()
	MANUAL_PATH = None
	try:
		urllib2.urlopen('https://www.google.com/', timeout=1)
		report_uid = p_dict.get("report_uid","")
		ele = p_dict.get("ele","")
		patient_uid = p_dict.get("patient_uid", "")
		patient_email = p_dict.get("patient_email", "")
		if patient_uid and patient_email:
			patient = TX_PATIENTS.objects.get(UID=patient_uid, DATAMODE="A")
			patient.PATIENT_EMAIL = patient_email.lower().strip()
			patient.save()
		if report_uid:
			reports = TX_MEDICALTESTREPORTS.objects.filter(UID=report_uid, DATAMODE="A").first()
			from_email = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-01", DATAMODE="A").KEY_VALUE
			server = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-02", DATAMODE="A").KEY_VALUE
			port = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-03", DATAMODE="A").KEY_VALUE
			password = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-04", DATAMODE="A").KEY_VALUE
			to_email = MA_APPLICATION_SETTINGS.objects.get(KEY_CODE="SET-05", DATAMODE="A").KEY_VALUE
			if not from_email:
				from_email = settings.DEFAULT_USER_EMAIL
				username = settings.DEFAULT_USER_EMAIL
			else:
				username = from_email
			if not to_email:
				to_email = settings.SERVICE_EMAIL
			if not server:
				server = settings.EMAIL_HOST
			if not port:
				port = settings.EMAIL_PORT
			if not password:
				password = settings.EMAIL_HOST_PASSWORD
			if TX_ACCOUNT.objects.filter(DATAMODE="A").exists() and reports.MEDICALTEST.PATIENT.PATIENT_EMAIL:
				report_pdf_path="%s/report/%s" %(settings.MEDIA_DATA, ele)
				hospital_info = TX_ACCOUNT.objects.get(DATAMODE="A")
				if reports.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.CODE == "APP-01":
					subject = "Doppler Test"
					message = "Hospital Name : %s<br />Test Name : Doppler Test<br />"%(hospital_info.BUSINESS_NAME)
				elif reports.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.CODE == "APP-02" or reports.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.CODE == "APP-03":
					if reports.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE.lower() == "other":
						subject = "Poly Neuropathy Test - VPT"
						message = "Hospital Name : %s<br />Test Name : Poly Neuropathy Test - VPT <br />"%(hospital_info.BUSINESS_NAME)
					elif reports.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE.lower() == "hand":
						subject = "Hand Sensory Test - VPT"
						message = "Hospital Name : %s<br />Test Name : Hand Sensory Test - VPT <br />"%(hospital_info.BUSINESS_NAME)
					else:
						subject = "Diabetic Neuropathy Test - VPT"
						message = "Hospital Name : %s<br />Test Name : Diabetic Neuropathy Test - VPT <br />"%(hospital_info.BUSINESS_NAME)
				elif reports.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.CODE == "APP-04":
					if reports.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE.lower() == "other":
						subject = "Poly Neuropathy Test - HCP"
						message = "Hospital Name : %s<br />Test Name : Poly Neuropathy Test - HCP <br />"%(hospital_info.BUSINESS_NAME)
					elif reports.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE.lower() == "hand":
						subject = "Hand Sensory Test - HCP"
						message = "Hospital Name : %s<br />Test Name : Hand Sensory Test - HCP <br />"%(hospital_info.BUSINESS_NAME)
					else:
						subject = "Diabetic Neuropathy Test - HCP"
						message = "Hospital Name : %s<br />Test Name : Diabetic Neuropathy Test - HCP <br />"%(hospital_info.BUSINESS_NAME)
				elif reports.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.CODE == "APP-05":
						subject = "Foot Pressure Test"
						message = "Hospital Name : %s<br />Test Name : Foot Pressure Test<br />"%(hospital_info.BUSINESS_NAME)
				elif reports.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.CODE == "APP-06":
					subject = "Foot Temperature Test"
					message = "Hospital Name : %s<br />Test Name : Foot Temperature Test<br />"%(hospital_info.BUSINESS_NAME)
				else:
					subject = "%s Report"%(reports.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.APP_NAME)
					message = "Hospital Name : %s<br />Test Name : %s<br />"%(hospital_info.BUSINESS_NAME, reports.MEDICALTEST.MEDICALTESTMASTER.MEDICAL_APP.APP_NAME)

				if reports.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE:
					subject = "%s - %s"%(subject, reports.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE.capitalize())
					message = "%sReport For : %s<br />"%(message, reports.MEDICALTEST.MEDICALTESTMASTER.ORGAN_TYPE.capitalize())

				message = "%s<br />Please find the attachment."%(message)

				backend = EmailBackend(host="%s"%(server), port="%d"%(int(port)), username="%s"%(username), password="%s"%(password), use_tls=settings.EMAIL_USE_TLS)
				email_msg = EmailMessage(subject, message, from_email, [reports.MEDICALTEST.PATIENT.PATIENT_EMAIL], connection=backend)
				email_msg.content_subtype = "html"  
				email_msg.attach_file(report_pdf_path)
				try:
					email_msg.send()
					os.remove("%s/report/%s" %(settings.MEDIA_DATA, ele))
					result, msg = ulo._setmsg(success_msg, error_msg, True)
				except Exception,e:
					result, msg = ulo._setmsg(success_msg, "Username and Password not accepted.", False)
					logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
	except urllib2.URLError as err:
		result, msg = ulo._setmsg(success_msg, err, False)
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, err))
	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def generate_license(request):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	try:

		license_file = request.FILES.get("license_file", "")
		if license_file:
			pass
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def patient_email(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	try:

		patient_uid = p_dict.get("patient_uid", "")
		patient_email = p_dict.get("patient_email", "")
		if patient_uid and patient_email:
			patient = TX_PATIENTS.objects.get(UID=patient_uid, DATAMODE="A")
			patient.PATIENT_EMAIL = patient_email
			patient.save()
		else:
			result, msg = ulo._setmsg(success_msg, "Pateint doesn't have email.", False)

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg


def search_id(request, search_key):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='No search results'
	patient_list = list()
	try:
		if TX_PATIENTS.objects.filter(FRIENDLY_UID=search_key.upper()).exists():
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception, e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
	return result, msg


def search_edit_id(request, patient_uid, search_key):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='No search results'
	patient_list = list()
	try:
		if TX_PATIENTS.objects.exclude(UID=patient_uid).filter(FRIENDLY_UID=search_key.upper()).exists():
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception, e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
	return result, msg


def doppler_medical_test_entry(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	try:
		test_type = p_dict.get('test_type',"ABI")
		if test_type:
			request.session['test_type'] = test_type

		patient = p_dict['patient_uid'].strip()
		doctor = p_dict.get('doctor_uid', None)
		examiner = p_dict.get('examiner_uid', None)
		app_code = p_dict['app_code'].strip()
		test_code = p_dict['test_code'].strip()
		test_entry = p_dict.get('test_entry', None)
		kodys_apps = MA_MEDICALAPPS.objects.filter(CODE=app_code, DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=app_code, DATAMODE="A").last()
		if test_code:
			medical_test_type  = MA_MEDICALTESTMASTER.objects.filter(CODE=test_code, DATAMODE="A").first()
			test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=test_code, DATAMODE="A")

			if doctor.strip() != "no_uid":
				doctor = TX_HCP.objects.get(UID=doctor, DATAMODE="A")
			else:
				doctor = ""
			if examiner.strip() != "no_uid":
				examiner = TX_HCP.objects.get(UID=examiner, DATAMODE="A")
			else:
				examiner = ""
			patients = TX_PATIENTS.objects.get(UID=patient, DATAMODE="A")
			if test_entry and TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, MEDICALTESTMASTER__CODE=test_code).exists():
				request.session["referred"] = ""
				medical_test_fields = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, MEDICALTEST__MEDICALTESTMASTER__CODE=test_code)
				for test_fields in medical_test_fields:
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_fields.KEY_VALUE = test_field_value
					else:
						test_fields.KEY_VALUE = test_field_value
						# if test_field_value.isalpha():
						# 	test_fields.KEY_VALUE_STATUS = "Abnormal"
					test_fields.save()
				medical_test = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, DATAMODE="A").first()
			else:
				medical_test = TX_MEDICALTESTS()
				medical_test.UID = uuid.uuid4().hex[:30]
				medical_test.MEDICALTESTMASTER = medical_test_type
				medical_test.PATIENT = patients
				medical_test.INTERPERTATION = test_interpertation.RANGES
				if doctor:
					medical_test.DOCTOR = doctor
				if examiner:
					medical_test.EXAMINER = examiner
				medical_test.REPORTED_ON = datetime.datetime.now()
				medical_test.save()
				medical_test.FRIENDLY_UID = "TST-%08d"%(medical_test.id)
				medical_test.save() 
				medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A")
				for test_fields in medical_test_fields:
					test_entries = TX_MEDICALTESTENTRIES()
					test_entries.UID = uuid.uuid4().hex[:30]
					test_entries.MEDICALTEST = medical_test
					test_entries.MEDICALTESTFIELDS = test_fields
					test_entries.KEY_NAME = test_fields.KEY_NAME
					test_entries.KEY_CODE = test_fields.KEY_CODE
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_entries.KEY_VALUE = test_field_value
						# if test_field_value.isalpha():
						# 	test_entries.KEY_VALUE_STATUS = "Abnormal"
					test_entries.save()
				
			if TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A").exists():
				pass
			else:
				test_report = TX_MEDICALTESTREPORTS()
				test_report.UID = uuid.uuid4().hex[:30]
				# test_report.FRIENDLY_UID = uuid.uuid4().hex[:30]
				test_report.MEDICALTEST = medical_test
				test_report.TEMPERATURE_SCALE = ""
				test_report.REFERRED_BY = referred_by_medical_test_type.REFERRED_BY
				if test_type:
					test_report.TEST_TYPE = test_type
				else:
					test_report.TEST_TYPE = "ABI"
				test_report.REPORTED_ON = datetime.datetime.now()
				if test_code == "TM-01":
					test_report.TEST_STATUS = "COMPLETED"
				test_report.CREATED_BY = request.user
				test_report.UPDATED_BY = request.user
				test_report.save()
				test_report.FRIENDLY_UID = "REP-%08d"%(test_report.id)
				test_report.save()

				# Pre-calculate ECG results to solve report lag and apply algorithmic fixes
				try:
					processed_results = process_can_test_data(test_report)
					if processed_results:
						test_report.TEST_RESULT = json.dumps(processed_results)
						test_report.save()
				except Exception as e:
					print("Pre-calculation failed: ", e)
			medical_test_result['test_entry_id'] = medical_test.FRIENDLY_UID
			medical_test_result['current_test_code'] = medical_test.MEDICALTESTMASTER.CODE
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			medical_test_result['test_entry_id'] = None
			medical_test_result['current_test_code'] = None
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test_result


def doppler(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").last()
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		# medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		tbi_normal = str(test_interpertation.RANGES['TBI']['Normal'])
		tbi_abnormal = str(test_interpertation.RANGES['TBI']['Abnormal'])
		abi_normal = str(test_interpertation.RANGES['ABI']['Normal'])
		abi_mild = str(test_interpertation.RANGES['ABI']['Mild'])
		abi_severe = str(test_interpertation.RANGES['ABI']['Severe'])
		abi_gangrene = str(test_interpertation.RANGES['ABI']['Gangrene'])
		abi_moderate = str(test_interpertation.RANGES['ABI']['Moderate'])
		abi_calcified = str(test_interpertation.RANGES['ABI']['Calcified'])
		if option['test_entry']:
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			request.session["referred"] = ""
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			request.session['test_type'] = test_report.TEST_TYPE
			# medical_test['test_type'] = medical_test_type.ORGAN_TYPE 
			medical_test['test_type'] = test_report.TEST_TYPE 
			medical_test['report'] = test_report

		if option['test_code'] and option['test_entry']:
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			if medical_tests:
				doppler_test_values = dict()
				for medical_test_value in medical_tests:
					tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
				 	right_abi_result, left_abi_result, right_tbi_result, left_abi_result = "", "", "", ""
					right_abi = 0.0
					left_tbi, right_tbi = 0.0, 0.0
					
					tbi_normal = tbi_normal.replace(">", "")
					tbi_abnormal = tbi_abnormal.replace("<", "")
					abi_normal = abi_normal.replace(">", "")
					abi_mild = abi_mild.split("-")
					abi_severe = abi_severe.split("-")
					abi_gangrene = abi_gangrene.replace("<", "")
					abi_moderate = abi_moderate.split("-")
					abi_calcified = abi_calcified.replace(">", "")

					if tx_test_entries[0].KEY_VALUE and (tx_test_entries[1].KEY_VALUE or tx_test_entries[2].KEY_VALUE):
						if tx_test_entries[1].KEY_VALUE and float(tx_test_entries[0].KEY_VALUE):
							if float(tx_test_entries[1].KEY_VALUE) and tx_test_entries[2].KEY_VALUE:
								if float(tx_test_entries[2].KEY_VALUE):
									right_abi = round(float(float(float(float(tx_test_entries[1].KEY_VALUE) + float(tx_test_entries[2].KEY_VALUE))/2)/float(tx_test_entries[0].KEY_VALUE)), 2)
								else:
									right_abi = round(float(float(tx_test_entries[1].KEY_VALUE)/float(tx_test_entries[0].KEY_VALUE)), 2)
							elif tx_test_entries[2].KEY_VALUE:
								if float(tx_test_entries[2].KEY_VALUE):
									right_abi = round(float(float(tx_test_entries[2].KEY_VALUE)/float(tx_test_entries[0].KEY_VALUE)), 2)
							elif float(tx_test_entries[1].KEY_VALUE):
								right_abi = round(float(float(tx_test_entries[1].KEY_VALUE)/float(tx_test_entries[0].KEY_VALUE)), 2)
						elif float(tx_test_entries[0].KEY_VALUE):
							if tx_test_entries[2].KEY_VALUE:
								if float(tx_test_entries[2].KEY_VALUE):
									right_abi = round(float(float(tx_test_entries[2].KEY_VALUE)/float(tx_test_entries[0].KEY_VALUE)), 2)

						if right_abi:
							if float(right_abi) >= float(abi_severe[0]) and float(right_abi) <= float(abi_severe[1]):
								right_abi_result = "Severe"
							elif float(right_abi) >= float(abi_moderate[0]) and float(right_abi) <= float(abi_moderate[1]):
								right_abi_result = "Moderate"
							elif float(right_abi) >= float(abi_mild[0]) and float(right_abi) <= float(abi_mild[1]):
								right_abi_result = "Mild"
							elif float(right_abi) >= float(0.9) and float(right_abi) <= float(1.3):
								right_abi_result = "Normal"
							elif float(right_abi) > float(abi_calcified):
									right_abi_result = "Calcified"
							elif float(right_abi) < float(abi_gangrene):
								right_abi_result = "Gangrene"
							else:
								right_abi_result = "Not in Range"
							doppler_test_values['right_abi_result'] = ["%.2f"%(right_abi), right_abi_result]
						else:
							doppler_test_values['right_abi_result'] = ["Invalid Data", ""]
					else:
						doppler_test_values['right_abi_result'] = ["No Data", ""]

					if tx_test_entries[4].KEY_VALUE and (tx_test_entries[5].KEY_VALUE or tx_test_entries[6].KEY_VALUE):
						if tx_test_entries[5].KEY_VALUE and float(tx_test_entries[4].KEY_VALUE):
							if float(tx_test_entries[5].KEY_VALUE) and tx_test_entries[6].KEY_VALUE:
								if float(tx_test_entries[6].KEY_VALUE):
									left_abi = round(float(float(float(float(tx_test_entries[5].KEY_VALUE) + float(tx_test_entries[6].KEY_VALUE))/2)/float(tx_test_entries[4].KEY_VALUE)), 2)
								else:
									left_abi = round(float(float(tx_test_entries[5].KEY_VALUE)/float(tx_test_entries[4].KEY_VALUE)), 2)
							elif tx_test_entries[6].KEY_VALUE:
								if float(tx_test_entries[6].KEY_VALUE):
									left_abi = round(float(float(tx_test_entries[6].KEY_VALUE)/float(tx_test_entries[4].KEY_VALUE)), 2)
							elif float(tx_test_entries[5].KEY_VALUE):
								left_abi = round(float(float(tx_test_entries[5].KEY_VALUE)/float(tx_test_entries[4].KEY_VALUE)), 2)
						elif float(tx_test_entries[4].KEY_VALUE):
							if tx_test_entries[6].KEY_VALUE:
								if float(tx_test_entries[6].KEY_VALUE):
									left_abi = round(float(float(tx_test_entries[6].KEY_VALUE)/float(tx_test_entries[4].KEY_VALUE)), 2)
						if left_abi:
							if float(left_abi) >= float(abi_severe[0]) and float(left_abi) <= float(abi_severe[1]):
								left_abi_result = "Severe"
							elif float(left_abi) >= float(abi_moderate[0]) and float(left_abi) <= float(abi_moderate[1]):
								left_abi_result = "Moderate"
							elif float(left_abi) >= float(abi_mild[0]) and float(left_abi) <= float(abi_mild[1]):
								left_abi_result = "Mild"
							elif float(left_abi) >= float(0.9) and float(left_abi) <= float(1.3):
								left_abi_result = "Normal"
							elif float(left_abi) > float(abi_calcified):
									left_abi_result = "Calcified"
							elif float(left_abi) < float(abi_gangrene):
								left_abi_result = "Gangrene"
							else:
								left_abi_result = "Not in Range"
							doppler_test_values['left_abi_result'] = ["%.2f"%(left_abi), left_abi_result]
						else:
							doppler_test_values['left_abi_result'] = ["Invalid Data", ""]
					else:
						doppler_test_values['left_abi_result'] = ["No Data", ""]

					if tx_test_entries[3].KEY_VALUE and tx_test_entries[0].KEY_VALUE:
						# if tx_test_entries[3].KEY_VALUE.isalpha() or tx_test_entries[0].KEY_VALUE.isalpha():
						# 	doppler_test_values['right_tbi_result'] = ["Invalid Data", ""]
						# else:
						if float(tx_test_entries[3].KEY_VALUE) and float(tx_test_entries[0].KEY_VALUE):
							right_tbi = round(float(float(tx_test_entries[3].KEY_VALUE)/float(tx_test_entries[0].KEY_VALUE)), 2)
							if float(right_tbi) >= float(tbi_normal):
								right_tbi_result = "Normal"
							elif float(right_tbi) <= float(tbi_abnormal):
								right_tbi_result = "Abnormal"
							else:
								right_tbi_result = "Not in Range"
							doppler_test_values['right_tbi_result'] = ["%.2f"%(right_tbi), right_tbi_result]
						else:
							doppler_test_values['right_tbi_result'] = ["Invalid Data", ""]
					else:
						doppler_test_values['right_tbi_result'] = ["No Data", ""]

					if tx_test_entries[7].KEY_VALUE and tx_test_entries[4].KEY_VALUE:
						# if tx_test_entries[7].KEY_VALUE.isalpha() or tx_test_entries[4].KEY_VALUE.isalpha():
						# 	doppler_test_values['left_tbi_result'] = ["Invalid Data", ""]
						# else:
						if float(tx_test_entries[7].KEY_VALUE) and float(tx_test_entries[4].KEY_VALUE):
							left_tbi = round(float(float(tx_test_entries[7].KEY_VALUE)/float(tx_test_entries[4].KEY_VALUE)), 2)
							if float(left_tbi) >= float(tbi_normal):
								left_tbi_result = "Normal"
							elif float(left_tbi) <= float(tbi_abnormal):
								left_tbi_result = "Abnormal"
							else:
								left_tbi_result = "Not in Range"
							doppler_test_values['left_tbi_result'] = ["%.2f"%(left_tbi), left_tbi_result]
						else:
							doppler_test_values['left_tbi_result'] = ["Invalid Data", ""]
					else:
						doppler_test_values['left_tbi_result'] = ["No Data", ""]
				
				medical_test["doppler_test_values"] = doppler_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(doppler_test_values)
				report.save()

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def doppler_graphical(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
			# previous_graphical_report = TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			# medical_test['previous_graphical_report'] = previous_graphical_report.TEST_TYPE
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").last()
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		previous_graphical_report = TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A").first()
		if previous_graphical_report:
			medical_test['previous_graphical_report'] = previous_graphical_report.TEST_TYPE
		else:
			medical_test['previous_graphical_report'] = ""
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		# medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		tbi_normal = str(test_interpertation.RANGES['TBI']['Normal'])
		tbi_abnormal = str(test_interpertation.RANGES['TBI']['Abnormal'])
		abi_normal = str(test_interpertation.RANGES['ABI']['Normal'])
		abi_mild = str(test_interpertation.RANGES['ABI']['Mild'])
		abi_severe = str(test_interpertation.RANGES['ABI']['Severe'])
		abi_gangrene = str(test_interpertation.RANGES['ABI']['Gangrene'])
		abi_moderate = str(test_interpertation.RANGES['ABI']['Moderate'])
		abi_calcified = str(test_interpertation.RANGES['ABI']['Calcified'])
		if option['test_entry']:
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			request.session["referred"] = ""
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			request.session['test_type'] = test_report.TEST_TYPE
			medical_test['test_type'] = test_report.TEST_TYPE 
			medical_test['report'] = test_report

		if option['test_code'] and option['test_entry']:
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			if medical_tests:
				doppler_test_values = dict()
				for medical_test_value in medical_tests:
					tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
				 	right_abi_result, left_abi_result, right_tbi_result, left_abi_result = "", "", "", ""
					right_abi = 0.0
					left_tbi, right_tbi = 0.0, 0.0
					
					tbi_normal = tbi_normal.replace(">", "")
					tbi_abnormal = tbi_abnormal.replace("<", "")
					abi_normal = abi_normal.replace(">", "")
					abi_mild = abi_mild.split("-")
					abi_severe = abi_severe.split("-")
					abi_gangrene = abi_gangrene.replace("<", "")
					abi_moderate = abi_moderate.split("-")
					abi_calcified = abi_calcified.replace(">", "")

					if tx_test_entries[0].KEY_VALUE and (tx_test_entries[4].KEY_VALUE or tx_test_entries[5].KEY_VALUE):
						# if tx_test_entries[0].KEY_VALUE.isalpha() or (tx_test_entries[4].KEY_VALUE.isalpha() and tx_test_entries[5].KEY_VALUE.isalpha()):
						# 	pass
						if tx_test_entries[4].KEY_VALUE and float(tx_test_entries[0].KEY_VALUE):
							if float(tx_test_entries[4].KEY_VALUE) and tx_test_entries[5].KEY_VALUE:
								if float(tx_test_entries[5].KEY_VALUE):
									right_abi = round(float(float(float(float(tx_test_entries[4].KEY_VALUE) + float(tx_test_entries[5].KEY_VALUE))/2)/float(tx_test_entries[0].KEY_VALUE)), 2)
								else:
									right_abi = round(float(float(tx_test_entries[4].KEY_VALUE)/float(tx_test_entries[0].KEY_VALUE)), 2)
							elif float(tx_test_entries[4].KEY_VALUE):
								right_abi = round(float(float(tx_test_entries[4].KEY_VALUE)/float(tx_test_entries[0].KEY_VALUE)), 2)
							elif tx_test_entries[5].KEY_VALUE:
								if float(tx_test_entries[5].KEY_VALUE):
									right_abi = round(float(float(tx_test_entries[5].KEY_VALUE)/float(tx_test_entries[0].KEY_VALUE)), 2)
						elif float(tx_test_entries[0].KEY_VALUE):
							if tx_test_entries[5].KEY_VALUE:
								if float(tx_test_entries[5].KEY_VALUE):
									right_abi = round(float(float(tx_test_entries[5].KEY_VALUE)/float(tx_test_entries[0].KEY_VALUE)), 2)

						if right_abi:
							if float(right_abi) >= float(abi_severe[0]) and float(right_abi) <= float(abi_severe[1]):
								right_abi_result = "Severe"
							elif float(right_abi) >= float(abi_moderate[0]) and float(right_abi) <= float(abi_moderate[1]):
								right_abi_result = "Moderate"
							elif float(right_abi) >= float(abi_mild[0]) and float(right_abi) <= float(abi_mild[1]):
								right_abi_result = "Mild"
							elif float(right_abi) >= float(0.9) and float(right_abi) <= float(1.3):
								right_abi_result = "Normal"
							elif float(right_abi) > float(abi_calcified):
									right_abi_result = "Calcified"
							elif float(right_abi) < float(abi_gangrene):
								right_abi_result = "Gangrene"
							else:
								right_abi_result = "Not in Range"
							doppler_test_values['right_abi_result'] = ["%.2f"%(right_abi), right_abi_result]
						else:
							doppler_test_values['right_abi_result'] = ["Invalid Data", ""]
					else:
						doppler_test_values['right_abi_result'] = ["No Data", ""]

					if tx_test_entries[7].KEY_VALUE and (tx_test_entries[11].KEY_VALUE or tx_test_entries[12].KEY_VALUE):
						# if tx_test_entries[7].KEY_VALUE.isalpha() or (tx_test_entries[11].KEY_VALUE.isalpha() and tx_test_entries[12].KEY_VALUE.isalpha()):
						# 	pass
						if tx_test_entries[11].KEY_VALUE and float(tx_test_entries[7].KEY_VALUE):
							if float(tx_test_entries[11].KEY_VALUE) and tx_test_entries[12].KEY_VALUE:
								if float(tx_test_entries[12].KEY_VALUE):
									left_abi = round(float(float(float(float(tx_test_entries[11].KEY_VALUE) + float(tx_test_entries[12].KEY_VALUE))/2)/float(tx_test_entries[7].KEY_VALUE)), 2)
								else:
									left_abi = round(float(float(tx_test_entries[11].KEY_VALUE)/float(tx_test_entries[7].KEY_VALUE)), 2)
							elif float(tx_test_entries[11].KEY_VALUE):
								left_abi = round(float(float(tx_test_entries[11].KEY_VALUE)/float(tx_test_entries[7].KEY_VALUE)), 2)
							elif tx_test_entries[12].KEY_VALUE:
								if float(tx_test_entries[12].KEY_VALUE):
									left_abi = round(float(float(tx_test_entries[12].KEY_VALUE)/float(tx_test_entries[7].KEY_VALUE)), 2)
						elif float(tx_test_entries[7].KEY_VALUE):
							if tx_test_entries[12].KEY_VALUE:
								if float(tx_test_entries[12].KEY_VALUE):
									left_abi = round(float(float(tx_test_entries[12].KEY_VALUE)/float(tx_test_entries[7].KEY_VALUE)), 2)
									
						
						if left_abi:
							if float(left_abi) >= float(abi_severe[0]) and float(left_abi) <= float(abi_severe[1]):
								left_abi_result = "Severe"
							elif float(left_abi) >= float(abi_moderate[0]) and float(left_abi) <= float(abi_moderate[1]):
								left_abi_result = "Moderate"
							elif float(left_abi) >= float(abi_mild[0]) and float(left_abi) <= float(abi_mild[1]):
								left_abi_result = "Mild"
							elif float(left_abi) >= float(0.9) and float(left_abi) <= float(1.3):
								left_abi_result = "Normal"
							elif float(left_abi) > float(abi_calcified):
									left_abi_result = "Calcified"
							elif float(left_abi) < float(abi_gangrene):
								left_abi_result = "Gangrene"
							else:
								left_abi_result = "Not in Range"
							doppler_test_values['left_abi_result'] = ["%.2f"%(left_abi), left_abi_result]
						else:
							doppler_test_values['left_abi_result'] = ["Invalid Data", ""]
					else:
						doppler_test_values['left_abi_result'] = ["No Data", ""]

					if tx_test_entries[6].KEY_VALUE and tx_test_entries[0].KEY_VALUE:
						# if tx_test_entries[6].KEY_VALUE.isalpha() or tx_test_entries[0].KEY_VALUE.isalpha():
						# 	doppler_test_values['right_tbi_result'] = ["Invalid Data", ""]
						# else:
						if float(tx_test_entries[6].KEY_VALUE) and float(tx_test_entries[0].KEY_VALUE):
							right_tbi = round(float(float(tx_test_entries[6].KEY_VALUE)/float(tx_test_entries[0].KEY_VALUE)), 2)
							if float(right_tbi) >= float(tbi_normal):
								right_tbi_result = "Normal"
							elif float(right_tbi) <= float(tbi_abnormal):
								right_tbi_result = "Abnormal"
							else:
								right_tbi_result = "Not in Range"
							doppler_test_values['right_tbi_result'] = ["%.2f"%(right_tbi), right_tbi_result]
						else:
							doppler_test_values['right_tbi_result'] = ["Invalid Data",""]
					else:
						doppler_test_values['right_tbi_result'] = ["No Data", ""]

					if tx_test_entries[13].KEY_VALUE and tx_test_entries[7].KEY_VALUE:
						# if tx_test_entries[13].KEY_VALUE.isalpha() or tx_test_entries[7].KEY_VALUE.isalpha():
						# 	doppler_test_values['left_tbi_result'] = ["Invalid Data", ""]
						# else:
						if float(tx_test_entries[13].KEY_VALUE) and float(tx_test_entries[7].KEY_VALUE):
							left_tbi = round(float(float(tx_test_entries[13].KEY_VALUE)/float(tx_test_entries[7].KEY_VALUE)), 2)
							if float(left_tbi) >= float(tbi_normal):
								left_tbi_result = "Normal"
							elif float(left_tbi) <= float(tbi_abnormal):
								left_tbi_result = "Abnormal"
							else:
								left_tbi_result = "Not in Range"
							doppler_test_values['left_tbi_result'] = ["%.2f"%(left_tbi), left_tbi_result]
						else:
							doppler_test_values['left_tbi_result'] = ["Invalid Data", ""]
					else:
						doppler_test_values['left_tbi_result'] = ["No Data", ""]
				
				medical_test["doppler_test_values"] = doppler_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(doppler_test_values)
				medical_test["TEST_STATUS"] = report.TEST_STATUS
				report.save()
				
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def podo_t_map(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").last()
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		t_map_fahrenhit_normal = str(test_interpertation.RANGES['Fahrenhit']['Normal'])
		t_map_fahrenhit_abnormal = str(test_interpertation.RANGES['Fahrenhit']['Abnormal'])
		t_map_celsius_normal = str(test_interpertation.RANGES['Celsius']['Normal'])
		t_map_celsius_abnormal = str(test_interpertation.RANGES['Celsius']['Abnormal'])

		medical_test['fahrenhit_normal'] = t_map_fahrenhit_normal
		medical_test['fahrenhit_abnormal'] = t_map_fahrenhit_abnormal
		medical_test['celsius_normal'] = t_map_celsius_normal
		medical_test['celsius_abnormal'] = t_map_celsius_abnormal

		t_map_fahrenhit_normal = t_map_fahrenhit_normal.replace("<", "")
		t_map_fahrenhit_normal = t_map_fahrenhit_normal.replace("=", "")
		t_map_fahrenhit_abnormal = t_map_fahrenhit_abnormal.replace(">", "")
		t_map_celsius_normal = t_map_celsius_normal.replace("<", "")
		t_map_celsius_normal = t_map_celsius_normal.replace("=", "")
		t_map_celsius_abnormal = t_map_celsius_abnormal.replace(">", "")
		normal = t_map_celsius_normal
		abnormal = t_map_celsius_abnormal
		if option['test_entry']:
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			request.session["referred"] = ""
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			request.session['test_type'] = test_report.TEST_TYPE
			medical_test['test_type'] = test_report.TEST_TYPE 
			medical_test['report'] = test_report
			# medical_test['test_for'] = test_report.TEST_TYPE
			if test_report.TEST_TYPE == "Fahrenhit":
				normal = t_map_fahrenhit_normal
				abnormal = t_map_fahrenhit_abnormal
		if option['test_code'] and option['test_entry']:
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			if medical_tests:
				podo_t_map_test_values = dict()
				for medical_test_value in medical_tests:
					tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
					if tx_test_entries[6].KEY_VALUE and not tx_test_entries[6].KEY_VALUE.isalpha():
						for tx_test in tx_test_entries[0:6]:
							if tx_test.KEY_VALUE.isalpha():
								tx_test.KEY_VALUE_STATUS = "Abnormal"
								# podo_t_map_test_values[tx_test.KEY_CODE] = ["%s %s"%("Right",tx_test.KEY_NAME), tx_test.KEY_VALUE_STATUS]
							elif tx_test.KEY_VALUE:
								right_result = float(tx_test.KEY_VALUE) - float(tx_test_entries[6].KEY_VALUE)
								if float(right_result) <= float(normal):
									tx_test.KEY_VALUE_STATUS = "Normal"
								elif float(right_result) > float(abnormal):
									tx_test.KEY_VALUE_STATUS = "Abnormal"
									podo_t_map_test_values[tx_test.KEY_CODE] = ["%s %s"%("Right",tx_test.KEY_NAME), tx_test.KEY_VALUE_STATUS]
							else:
								tx_test.KEY_VALUE_STATUS = "No Data"
							tx_test.save()
					if tx_test_entries[13].KEY_VALUE and not tx_test_entries[13].KEY_VALUE.isalpha():
						for tx_test in tx_test_entries[7:13]:
							if tx_test.KEY_VALUE.isalpha():
								tx_test.KEY_VALUE_STATUS = "Abnormal"
								# podo_t_map_test_values[tx_test.KEY_CODE] = ["%s %s"%("Left",tx_test.KEY_NAME), tx_test.KEY_VALUE_STATUS]
							elif tx_test.KEY_VALUE:
								left_result = float(tx_test.KEY_VALUE) - float(tx_test_entries[13].KEY_VALUE)
								if float(left_result) <= float(normal):
									tx_test.KEY_VALUE_STATUS = "Normal"
								elif float(left_result) > float(abnormal):
									tx_test.KEY_VALUE_STATUS = "Abnormal"
									podo_t_map_test_values[tx_test.KEY_CODE] = ["%s %s"%("Left",tx_test.KEY_NAME), tx_test.KEY_VALUE_STATUS]
							else:
								tx_test.KEY_VALUE_STATUS = "No Data"
							tx_test.save()

				medical_test["podo_t_map_test_values"] = podo_t_map_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(podo_t_map_test_values)
				report.save()
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""

		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def podo_t_map_medical_test_entry(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	try:
		test_type = p_dict.get('test_type',"Celsius")

		patient = p_dict['patient_uid'].strip()
		doctor = p_dict.get('doctor_uid', None)
		examiner = p_dict.get('examiner_uid', None)
		app_code = p_dict['app_code'].strip()
		test_code = p_dict['test_code'].strip()
		test_entry = p_dict.get('test_entry', None)
		kodys_apps = MA_MEDICALAPPS.objects.filter(CODE=app_code, DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=app_code, DATAMODE="A").last()
		if test_code:
			medical_test_type  = MA_MEDICALTESTMASTER.objects.filter(CODE=test_code, DATAMODE="A").first()
			if doctor.strip() != "no_uid":
				doctor = TX_HCP.objects.get(UID=doctor, DATAMODE="A")
			else:
				doctor = ""
			if examiner.strip() != "no_uid":
				examiner = TX_HCP.objects.get(UID=examiner, DATAMODE="A")
			else:
				examiner = ""
			patients = TX_PATIENTS.objects.get(UID=patient, DATAMODE="A")
			test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=test_code, DATAMODE="A")
			t_map_fahrenhit_normal = str(test_interpertation.RANGES['Fahrenhit']['Normal'])
			t_map_fahrenhit_abnormal = str(test_interpertation.RANGES['Fahrenhit']['Abnormal'])
			t_map_celsius_normal = str(test_interpertation.RANGES['Celsius']['Normal'])
			t_map_celsius_abnormal = str(test_interpertation.RANGES['Celsius']['Abnormal'])

			t_map_fahrenhit_normal = t_map_fahrenhit_normal.replace("<", "")
			t_map_fahrenhit_normal = t_map_fahrenhit_normal.replace("=", "")
			t_map_fahrenhit_abnormal = t_map_fahrenhit_abnormal.replace(">", "")
			t_map_celsius_normal = t_map_celsius_normal.replace("<", "")
			t_map_celsius_normal = t_map_celsius_normal.replace("=", "")
			t_map_celsius_abnormal = t_map_celsius_abnormal.replace(">", "")

			if test_type == "Fahrenhit":
				normal = t_map_fahrenhit_normal
				abnormal = t_map_fahrenhit_abnormal
			else:
				normal = t_map_celsius_normal
				abnormal = t_map_celsius_abnormal
			if test_entry and TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, MEDICALTESTMASTER__CODE=test_code).exists():
				request.session["referred"] = ""
				medical_test_fields = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, MEDICALTEST__MEDICALTESTMASTER__CODE=test_code)
				for test_fields in medical_test_fields:
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_fields.KEY_VALUE = test_field_value
					test_fields.save()
				medical_test = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, DATAMODE="A").first()
			else:
				medical_test = TX_MEDICALTESTS()
				medical_test.UID = uuid.uuid4().hex[:30]
				medical_test.MEDICALTESTMASTER = medical_test_type
				medical_test.PATIENT = patients
				medical_test.INTERPERTATION = test_interpertation.RANGES
				if doctor:
					medical_test.DOCTOR = doctor
				if examiner:
					medical_test.EXAMINER = examiner
				medical_test.REPORTED_ON = datetime.datetime.now()
				medical_test.save()
				medical_test.FRIENDLY_UID = "TST-%08d"%(medical_test.id)
				medical_test.save() 

				medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A")
				for test_fields in medical_test_fields:
					test_entries = TX_MEDICALTESTENTRIES()
					test_entries.UID = uuid.uuid4().hex[:30]
					test_entries.MEDICALTEST = medical_test
					test_entries.MEDICALTESTFIELDS = test_fields
					test_entries.KEY_NAME = test_fields.KEY_NAME
					test_entries.KEY_CODE = test_fields.KEY_CODE
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_entries.KEY_VALUE = test_field_value
					test_entries.save()
				
			if TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A").exists():
				pass
			else:
				test_report = TX_MEDICALTESTREPORTS()
				test_report.UID = uuid.uuid4().hex[:30]
				test_report.MEDICALTEST = medical_test
				test_report.TEMPERATURE_SCALE = test_type
				test_report.REFERRED_BY = referred_by_medical_test_type.REFERRED_BY
				test_report.REPORTED_ON = datetime.datetime.now()
				test_report.TEST_STATUS = "COMPLETED"
				test_report.TEST_TYPE = test_type
				test_report.CREATED_BY = request.user
				test_report.UPDATED_BY = request.user
				test_report.save()
				test_report.FRIENDLY_UID = "REP-%08d"%(test_report.id)
				test_report.save()

				# Pre-calculate ECG results to solve report lag and apply algorithmic fixes
				try:
					processed_results = process_can_test_data(test_report)
					if processed_results:
						test_report.TEST_RESULT = json.dumps(processed_results)
						test_report.save()
				except Exception as e:
					print("Pre-calculation failed: ", e)
			medical_test_result['test_entry_id'] = medical_test.FRIENDLY_UID
			medical_test_result['current_test_code'] = medical_test.MEDICALTESTMASTER.CODE
	
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			medical_test_result['test_entry_id'] = None
			medical_test_result['current_test_code'] = None
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test_result


def doppler_graphical_template(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	try:
		image_list = list()
		test_entry = p_dict['test_entry'].strip()
		test_entry = p_dict['test_entry'].strip()
		notes = p_dict.get('notes',None)

		template = request.FILES.get('template', None)
		if test_entry and TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, DATAMODE="A").exists():
			test_report = TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, DATAMODE="A").first()
			if notes:
				test_report.IMPRESSION_NOTES = notes.strip()
				test_report.save()
			if template:
				with open('%s/Doppler_Graphical_PDF/%s'%(settings.MEDIA_DATA, template), 'wb+') as destination:
					for chunk in template.chunks():
						destination.write(chunk)

				filename="%s/Doppler_Graphical_PDF/%s" %(settings.MEDIA_DATA,template)
				doppler_pdf_json = dict()
				app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
				pages = convert_from_path(filename, 100,poppler_path=app_dir+'\\py-dist\\poppler-0.68.0\\bin')
				if test_report.TEST_TYPE == "VASCULAR_SEGMENTAL_STUDY_REPORT_2":
					pages[0].save('%s/Doppler_Graphical/%s1.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Doppler_Graphical/%s1.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					pdf_image1 = Image.open("%s/Doppler_Graphical/%s1.jpg"%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					right_pdf_image = pdf_image1.crop((60, 280, 580, 1270))
					right_pdf_image.save('%s/Right_Doppler_Graphical/%s1.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Right_Doppler_Graphical/%s1.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					
					left_pdf_image = pdf_image1.crop((580, 280, 1100, 1270))
					left_pdf_image.save('%s/Left_Doppler_Graphical/%s1.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Left_Doppler_Graphical/%s1.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					
					right_base64_image = open('%s/Right_Doppler_Graphical/%s1.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					right_base64_image_read = right_base64_image.read()
					right_base64_image_encode = base64.encodestring(right_base64_image_read)

					left_base64_image = open('%s/Left_Doppler_Graphical/%s1.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					left_base64_image_read = left_base64_image.read()
					left_base64_image_encode = base64.encodestring(left_base64_image_read)
					doppler_pdf_json["right_base64"] = right_base64_image_encode
					doppler_pdf_json["left_base64"] = left_base64_image_encode
					if len(pages) > 1:
						pages[1].save('%s/Doppler_Graphical/%s2.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
						image_list.append('%s/Doppler_Graphical/%s2.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
						pdf_image2 = Image.open("%s/Doppler_Graphical/%s2.jpg"%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
						right_pdf_image = pdf_image2.crop((60, 280, 580, 440))
						right_pdf_image.save('%s/Right_Doppler_Graphical/%s2.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
						image_list.append('%s/Right_Doppler_Graphical/%s2.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))

						left_pdf_image = pdf_image2.crop((580, 280, 1100, 440))
						left_pdf_image.save('%s/Left_Doppler_Graphical/%s2.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
						image_list.append('%s/Left_Doppler_Graphical/%s2.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))

						right_base64_image = open('%s/Right_Doppler_Graphical/%s2.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
						right_base64_image_read = right_base64_image.read()
						right_base64_image_encode = base64.encodestring(right_base64_image_read)

						left_base64_image = open('%s/Left_Doppler_Graphical/%s2.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
						left_base64_image_read = left_base64_image.read()
						left_base64_image_encode = base64.encodestring(left_base64_image_read)
						doppler_pdf_json["right_brachial_base64"] = right_base64_image_encode
						doppler_pdf_json["left_brachial_base64"] = left_base64_image_encode
				elif test_report.TEST_TYPE == "VASCULAR_SEGMENTAL_STUDY_REPORT_1":
					for page in pages:
						page.save('%s/Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
						image_list.append('%s/Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					pdf_image = Image.open("%s/Doppler_Graphical/%s.jpg"%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					right_pdf_image = pdf_image.crop((60, 280, 580, 1270))
					right_pdf_image.save('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))

					left_pdf_image = pdf_image.crop((580, 280, 1100, 1270))
					left_pdf_image.save('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))

					right_base64_image = open('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					right_base64_image_read = right_base64_image.read()
					right_base64_image_encode = base64.encodestring(right_base64_image_read)

					left_base64_image = open('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					left_base64_image_read = left_base64_image.read()
					left_base64_image_encode = base64.encodestring(left_base64_image_read)
					doppler_pdf_json["right_base64"] = right_base64_image_encode
					doppler_pdf_json["left_base64"] = left_base64_image_encode
				elif test_report.TEST_TYPE == "ABI_DOPPLER":
					for page in pages:
						page.save('%s/Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
						image_list.append('%s/Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					pdf_image = Image.open("%s/Doppler_Graphical/%s.jpg"%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					right_pdf_brachial_image = pdf_image.crop((60, 520, 580, 760))
					right_pdf_image = pdf_image.crop((60, 770, 580, 1010))
					right_pdf_brachial_image.save('%s/Right_Doppler_Graphical/brachial_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					right_pdf_image.save('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Right_Doppler_Graphical/brachial_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					image_list.append('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))

					left_pdf_brachial_image = pdf_image.crop((580, 520, 1100, 760))
					left_pdf_image = pdf_image.crop((580, 770, 1100, 1010))
					left_pdf_brachial_image.save('%s/Left_Doppler_Graphical/brachial_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					left_pdf_image.save('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Left_Doppler_Graphical/brachial_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					image_list.append('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))

					right_brachial_base64_image = open('%s/Right_Doppler_Graphical/brachial_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					right_brachial_base64_image_read = right_brachial_base64_image.read()
					right_brachial_base64_image_encode = base64.encodestring(right_brachial_base64_image_read)
					right_base64_image = open('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					right_base64_image_read = right_base64_image.read()
					right_base64_image_encode = base64.encodestring(right_base64_image_read)

					left_brachial_base64_image = open('%s/Left_Doppler_Graphical/brachial_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					left_brachial_base64_image_read = left_brachial_base64_image.read()
					left_brachial_base64_image_encode = base64.encodestring(left_brachial_base64_image_read)
					left_base64_image = open('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					left_base64_image_read = left_base64_image.read()
					left_base64_image_encode = base64.encodestring(left_base64_image_read)

					doppler_pdf_json["right_brachial_base64"] = right_brachial_base64_image_encode
					doppler_pdf_json["left_brachial_base64"] = left_brachial_base64_image_encode
					doppler_pdf_json["right_base64"] = right_base64_image_encode
					doppler_pdf_json["left_base64"] = left_base64_image_encode
				elif test_report.TEST_TYPE == "ABI_TBI_DOPPLER_1":
					for page in pages:
						page.save('%s/Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
						image_list.append('%s/Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					pdf_image = Image.open("%s/Doppler_Graphical/%s.jpg"%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					right_pdf_brachial_image = pdf_image.crop((60, 520, 580, 760))
					right_pdf_image = pdf_image.crop((60, 770, 580, 1010))
					right_pdf_toe_image = pdf_image.crop((60, 1270, 580, 1510))
					right_pdf_brachial_image.save('%s/Right_Doppler_Graphical/brachial_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					right_pdf_image.save('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					right_pdf_toe_image.save('%s/Right_Doppler_Graphical/toe_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Right_Doppler_Graphical/brachial_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					image_list.append('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					image_list.append('%s/Right_Doppler_Graphical/toe_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))

					left_pdf_brachial_image = pdf_image.crop((580, 520, 1100, 760))
					left_pdf_image = pdf_image.crop((580, 770, 1100, 1010))
					left_pdf_toe_image = pdf_image.crop((580, 1270, 1100, 1510))
					left_pdf_brachial_image.save('%s/Left_Doppler_Graphical/brachial_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					left_pdf_image.save('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					left_pdf_toe_image.save('%s/Left_Doppler_Graphical/toe_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Left_Doppler_Graphical/brachial_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					image_list.append('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					image_list.append('%s/Left_Doppler_Graphical/toe_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))

					right_brachial_base64_image = open('%s/Right_Doppler_Graphical/brachial_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					right_brachial_base64_image_read = right_brachial_base64_image.read()
					right_brachial_base64_image_encode = base64.encodestring(right_brachial_base64_image_read)
					right_base64_image = open('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					right_base64_image_read = right_base64_image.read()
					right_base64_image_encode = base64.encodestring(right_base64_image_read)
					right_base64_toe_image = open('%s/Right_Doppler_Graphical/toe_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					right_base64_toe_image_read = right_base64_toe_image.read()
					right_base64_toe_image_encode = base64.encodestring(right_base64_toe_image_read)

					left_brachial_base64_image = open('%s/Left_Doppler_Graphical/brachial_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					left_brachial_base64_image_read = left_brachial_base64_image.read()
					left_brachial_base64_image_encode = base64.encodestring(left_brachial_base64_image_read)
					left_base64_image = open('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					left_base64_image_read = left_base64_image.read()
					left_base64_image_encode = base64.encodestring(left_base64_image_read)
					left_base64_toe_image = open('%s/Left_Doppler_Graphical/toe_%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					left_base64_toe_image_read = left_base64_toe_image.read()
					left_base64_toe_image_encode = base64.encodestring(left_base64_toe_image_read)
					
					doppler_pdf_json["right_brachial_base64"] = right_brachial_base64_image_encode
					doppler_pdf_json["left_brachial_base64"] = left_brachial_base64_image_encode
					doppler_pdf_json["right_base64"] = right_base64_image_encode
					doppler_pdf_json["left_base64"] = left_base64_image_encode
					doppler_pdf_json["right_toe_base64"] = right_base64_toe_image_encode
					doppler_pdf_json["left_toe_base64"] = left_base64_toe_image_encode
				elif test_report.TEST_TYPE == "ABI_TBI_DOPPLER_2":
					for page in pages:
						page.save('%s/Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
						image_list.append('%s/Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					pdf_image = Image.open("%s/Doppler_Graphical/%s.jpg"%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					right_pdf_image = pdf_image.crop((60, 520, 580, 1510))
					right_pdf_image.save('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))

					left_pdf_image = pdf_image.crop((580, 520, 1100, 1510))
					left_pdf_image.save('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))

					right_base64_image = open('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					right_base64_image_read = right_base64_image.read()
					right_base64_image_encode = base64.encodestring(right_base64_image_read)

					left_base64_image = open('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					left_base64_image_read = left_base64_image.read()
					left_base64_image_encode = base64.encodestring(left_base64_image_read)
					doppler_pdf_json["right_base64"] = right_base64_image_encode
					doppler_pdf_json["left_base64"] = left_base64_image_encode
				else:
					for page in pages:
						page.save('%s/Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
						image_list.append('%s/Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					pdf_image = Image.open("%s/Doppler_Graphical/%s.jpg"%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))
					right_pdf_image = pdf_image.crop((60, 280, 580, 1510))
					right_pdf_image.save('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))

					left_pdf_image = pdf_image.crop((580, 280, 1100, 1510))
					left_pdf_image.save('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'JPEG')
					image_list.append('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID))

					right_base64_image = open('%s/Right_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					right_base64_image_read = right_base64_image.read()
					right_base64_image_encode = base64.encodestring(right_base64_image_read)

					left_base64_image = open('%s/Left_Doppler_Graphical/%s.jpg'%(settings.MEDIA_ROOT, test_report.FRIENDLY_UID), 'rb')
					left_base64_image_read = left_base64_image.read()
					left_base64_image_encode = base64.encodestring(left_base64_image_read)
					doppler_pdf_json["right_base64"] = right_base64_image_encode
					doppler_pdf_json["left_base64"] = left_base64_image_encode
				dopplerpdf = DOPPLER_GRAPHICAL_PDF()
				dopplerpdf.TEST_REPORT = test_report
				dopplerpdf.BASE_64_IMAGES = json.dumps(doppler_pdf_json)
				dopplerpdf.CREATED_BY = request.user
				dopplerpdf.UPDATED_BY = request.user
				dopplerpdf.save()
				test_report.TEST_STATUS = "COMPLETED"
				test_report.save()
				for image_file in image_list:
					if os.path.exists(image_file):
						try:
							os.remove(image_file)
						except Exception,e:
							pass
				result, msg = ulo._setmsg(success_msg, error_msg, True)
			else:
				result, msg = ulo._setmsg(success_msg, "Enter a valid PDF.", False)
		else:
			result, msg = ulo._setmsg(success_msg, error_msg, False)
	except Exception,e:
		print(e,"aaaaa00a0a0a0-------------------------------------")
		print("aaaaa00a0a0a0-------------------------------------")
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, test_entry


def kodys_can(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	ma_medical_test_list = list()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").last()

		medical_test_types = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").order_by("pk")
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		medical_test['test_interpertation'] = test_interpertation.RANGES
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").exists():
			device_details = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").first()
		else:
			device_details = dict()
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		medical_test['medical_device'] = medical_device
		medical_test['device_details'] = device_details
		instruction = MA_MEDICALTESTINSTRUCTION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, INSTRUCTION_TYPE="PROCEDURE", DATAMODE="A")
		medical_test['instruction'] = json.loads(instruction.INSTRUCTION_CONTENT)
		prodecure = MA_MEDICALTESTINSTRUCTION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, INSTRUCTION_TYPE="HELP", DATAMODE="A")
		medical_test['prodecure'] = json.loads(prodecure.INSTRUCTION_CONTENT)
		medical_test['prodecure_image'] = prodecure.INSTRUCTION_IMAGE
	
		if option['test_entry']:
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			medical_test['test_type'] = test_report.TEST_TYPE 

		if option['test_code'] and option['test_entry']:
			for ma_medical_test in medical_test_types:
				ma_medical_test_list.append(ma_medical_test.CODE)
			next_procedure_index = ma_medical_test_list.index(option['test_code']) 
			next_procedure_code = ma_medical_test_list[next_procedure_index + 1]
			prodecure = MA_MEDICALTESTINSTRUCTION.objects.get(MEDICALTESTMASTER__CODE=next_procedure_code, INSTRUCTION_TYPE="HELP", DATAMODE="A")
			medical_test['next_prodecure'] = json.loads(prodecure.INSTRUCTION_CONTENT)
			medical_test['next_prodecure_image'] = prodecure.INSTRUCTION_IMAGE
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			report_pdf_path="%s/report/CAN/ecg.csv" %(settings.MEDIA_DATA)

			if option['test_code'] == "TM-21":
				if tx_test_entries and tx_test_entries[6].KEY_VALUE:
					test_value = tx_test_entries[6].KEY_VALUE.split(",")
					raw_data = list()
					for row in test_value:
						if row:
							raw_data.append(int(row))
					(baseline, ecg_out) = bwr.bwr(raw_data)
					if len(ecg_out) >= 15000:
						ecg_out = [i + 100 for i in ecg_out[0:15000]]
					else:
						ecg_out = [i + 100 for i in ecg_out]
					ecg_out = np.asarray(ecg_out)
			else:
				# Check for pre-calculated results to solve report lag
				pre_calculated = None
				if test_report.TEST_RESULT:
					try:
						pre_calculated = json.loads(test_report.TEST_RESULT)
					except:
						pass

				if pre_calculated and "processed_ecg" in pre_calculated:
					# Use pre-calculated data
					ecg_out_str = pre_calculated["processed_ecg"]
					ecg_out = [float(x) for x in ecg_out_str.split(",") if x]
					ecg_out = np.asarray(ecg_out)
					working_data = dict()
					working_data['RR_list_cor'] = pre_calculated.get("rr_intervals", [])
					# For Poincare, use the pre-calculated ones or the intervals
					measures = dict()
					measures['bpm'] = pre_calculated.get("bpm", 0)
				else:
					# Legacy/Slow way: Perform processing on the fly
					if tx_test_entries and tx_test_entries[2].KEY_VALUE:
						test_value = tx_test_entries[2].KEY_VALUE.split(",")
						raw_data = list()
						for row in test_value:
							if row:
								raw_data.append(int(row))

						(baseline, ecg_out) = bwr.bwr(raw_data)
						if len(ecg_out) >= 15000:
							ecg_out = [i + 100 for i in ecg_out[0:15000]]
						else:
							ecg_out = [i + 100 for i in ecg_out]
						ecg_out = np.asarray(ecg_out)
					if tx_test_entries:
						working_data = dict()
						measures = dict()
						try:
							qrs_detector = qrs_detect.QRSDetectorOffline(ecg_data=raw_data, verbose=True,log_data=False, plot_data=False, show_plot=False)
							rr_peak = qrs_detector.qrs_peaks_indices
							working_data['peaklist_cor'] = rr_peak
							nni = np.diff(rr_peak)
							rr_interval = (nni / 250.0)*1000
							working_data['RR_list_cor'] = rr_interval.tolist()
							results_td = td.time_domain(nni=working_data['RR_list_cor'],plot=False, show=False)
							measures['bpm']= int(round(results_td['hr_mean']))
						except Exception,e:
							print(e)

			if option['test_code'] == "TM-20":
				if tx_test_entries:
					raw_data = tx_test_entries[0].KEY_VALUE.split(",")
					heart_rate = [int(raw_data[i+1].strip()) for i in range(0, len(raw_data)) if raw_data[i] if int(raw_data[i].strip())==254 if int(raw_data[i+1].strip())]
					bpm_list = list(set(heart_rate))
					bpm_list.sort()
					bpm_graph = [(i, heart_rate.count(i)) for i in bpm_list]
					medical_test_result = json.loads(test_report.TEST_RESULT)
					results_td = td.time_domain(nni=working_data['RR_list_cor'],plot=False, show=False)
					rr_mean = round(results_td['nni_mean'],5)
					rr_std = round(results_td['sdnn'],5)
					breathing_dict = dict()
					if working_data['RR_list_cor']:
						if working_data['RR_list_cor'][0] < 400:
							del working_data['RR_list_cor'][0]
							try:
								working_data['peaklist_cor'] = working_data['peaklist_cor'].tolist()
								del working_data['peaklist_cor'][0]
							except:
								del working_data['peaklist_cor'][0]
					breathing_dict["rr_interval"] = working_data['RR_list_cor']
					if working_data['RR_list_cor']:
						breathing_dict["rrn"] = working_data['RR_list_cor'][0:-1]
						breathing_dict["rrn_plus1"] = working_data['RR_list_cor'][1:]
					else:
						breathing_dict["rrn"] = list()
						breathing_dict["rrn_plus1"] = list()
					breathing_dict["rr_interval"] = working_data['RR_list_cor']
					breathing_dict['peaklist'] = list(working_data['peaklist_cor'])
					breathing_dict["rr_mean"] = rr_mean
					breathing_dict["sdnn"] = rr_std
					cv = (float(rr_std)/float(rr_mean))*100
					breathing_dict["cv"] = round(cv, 2)
					breathing_dict['heart_rate'] = heart_rate
					breathing_dict['heart_rate_graph'] = bpm_graph
					breathing_dict['heart_rate_start'] = int(min(heart_rate)) - 5
					breathing_dict['heart_rate_end'] = int(max(heart_rate)) + 5
					breathing_dict['heart_rate_count_start'] = 0
					heart_rate_count = [heart_rate.count(i) for i in bpm_list]
					breathing_dict['heart_rate_count_end'] = int(max(heart_rate_count)) + 5
					if min(working_data['RR_list_cor']) != 0 or min(working_data['RR_list_cor']) != 0.0:
						breathing_dict['rr_interval_start'] = int(min(working_data['RR_list_cor'])) - 100
					else:
						breathing_dict['rr_interval_start'] = 0
					breathing_dict['rr_interval_end'] = int(max(working_data['RR_list_cor'])) + 100
					inspiration_min = list()
					expiration_max = list()
					avg_deep_breath_diff = list()
					dbd_list = list()
					if len(test_value) >= 2500:
						context ={"test_value": test_value[0:1250]}
						inspiration1 = deep_breathing_rr_calculation(request, context)
						context ={"test_value": test_value[1250:2500]}
						expiration1 = deep_breathing_rr_calculation(request, context)
						context ={"test_value": test_value[0:2500]}
						avg_deep_breath1 = deep_breathing_rr_calculation(request, context)
						hr_max = round(60000/avg_deep_breath1['nni_max'],2)
						hr_min = round(60000/avg_deep_breath1['nni_min'],2)
						avg_deep_breath_diff.append(avg_deep_breath1['nni_max']-avg_deep_breath1['nni_min'])
						dbd_list.append(abs(hr_max-hr_min))
						if expiration1["nni_max"] and expiration1["nni_min"]:
							expiration_max.append(expiration1["nni_max"])
						if inspiration1["nni_max"] and inspiration1["nni_min"]:
							inspiration_min.append(inspiration1["nni_min"])
					
					if len(test_value) >= 5000:
						context ={"test_value": test_value[2501:3750]}
						inspiration2 = deep_breathing_rr_calculation(request, context)
						context ={"test_value": test_value[3750:5000]}
						expiration2 = deep_breathing_rr_calculation(request, context)
						context ={"test_value": test_value[2501:5000]}
						avg_deep_breath2 = deep_breathing_rr_calculation(request, context)
						hr_max = round(60000/avg_deep_breath2['nni_max'],2)
						hr_min = round(60000/avg_deep_breath2['nni_min'],2)
						avg_deep_breath_diff.append(avg_deep_breath2['nni_max']-avg_deep_breath2['nni_min'])
						dbd_list.append(abs(hr_max-hr_min))
						if expiration2["nni_max"] and expiration2["nni_min"]:
							expiration_max.append(expiration2["nni_max"])
						if inspiration2["nni_max"] and inspiration2["nni_min"]:
							inspiration_min.append(inspiration2["nni_min"])

					if len(test_value) >= 7500:
						context ={"test_value": test_value[5001:6251]}
						inspiration3 = deep_breathing_rr_calculation(request, context)
						context ={"test_value": test_value[6251:7500]}
						expiration3 = deep_breathing_rr_calculation(request, context)
						context ={"test_value": test_value[5001:7500]}
						avg_deep_breath3 = deep_breathing_rr_calculation(request, context)
						hr_max = round(60000/avg_deep_breath3['nni_max'],2)
						hr_min = round(60000/avg_deep_breath3['nni_min'],2)
						avg_deep_breath_diff.append(avg_deep_breath3['nni_max']-avg_deep_breath3['nni_min'])
						dbd_list.append(abs(hr_max-hr_min))
						if expiration3["nni_max"] and expiration3["nni_min"]:
							expiration_max.append(expiration3["nni_max"])
						if inspiration3["nni_max"] and inspiration3["nni_min"]:
							inspiration_min.append(inspiration3["nni_min"])

					if len(test_value) >= 10000:
						context ={"test_value": test_value[7501:8750]}
						inspiration4 = deep_breathing_rr_calculation(request, context)
						context ={"test_value": test_value[8750:10000]}
						expiration4 = deep_breathing_rr_calculation(request, context)
						context ={"test_value": test_value[7501:10000]}
						avg_deep_breath4 = deep_breathing_rr_calculation(request, context)
						hr_max = round(60000/avg_deep_breath4['nni_max'],2)
						hr_min = round(60000/avg_deep_breath4['nni_min'],2)
						avg_deep_breath_diff.append(avg_deep_breath4['nni_max']-avg_deep_breath4['nni_min'])
						dbd_list.append(abs(hr_max-hr_min))
						if expiration4["nni_max"] and expiration4["nni_min"]:
							expiration_max.append(expiration4["nni_max"])
						if inspiration4["nni_max"] and inspiration4["nni_min"]:
							inspiration_min.append(inspiration4["nni_min"])

					if len(test_value) >= 12500:
						context ={"test_value": test_value[10001:11250]}
						inspiration5 = deep_breathing_rr_calculation(request, context)
						context ={"test_value": test_value[11250:12500]}
						expiration5 = deep_breathing_rr_calculation(request, context)
						context ={"test_value": test_value[10001:12500]}
						avg_deep_breath5 = deep_breathing_rr_calculation(request, context)
						hr_max = round(60000/avg_deep_breath5['nni_max'],2)
						hr_min = round(60000/avg_deep_breath5['nni_min'],2)
						avg_deep_breath_diff.append(avg_deep_breath5['nni_max']-avg_deep_breath5['nni_min'])
						dbd_list.append(abs(hr_max-hr_min))
						if expiration5["nni_max"] and expiration5["nni_min"]:
							expiration_max.append(expiration5["nni_max"])
						if inspiration5["nni_max"] and inspiration5["nni_min"]:
							inspiration_min.append(inspiration5["nni_min"])
					

					if len(test_value) >= 15000:
						context ={"test_value": test_value[12500:13750]}
						inspiration6 = deep_breathing_rr_calculation(request, context)
						
						context ={"test_value": test_value[13750:15000]}
						expiration6 = deep_breathing_rr_calculation(request, context)
						
						context ={"test_value": test_value[12500:15000]}
						avg_deep_breath6 = deep_breathing_rr_calculation(request, context)
						
						hr_max =  round(60000/avg_deep_breath6['nni_max'],2)
						hr_min =  round(60000/avg_deep_breath6['nni_min'],2)
						avg_deep_breath_diff.append(avg_deep_breath6['nni_max']-avg_deep_breath6['nni_min'])
						dbd_list.append(abs(hr_max-hr_min))
						if expiration6["nni_max"] and expiration6["nni_min"]:
							expiration_max.append(expiration6["nni_max"])
						if inspiration6["nni_max"] and inspiration6["nni_min"]:
							inspiration_min.append(inspiration6["nni_min"])

					avg_deep_breath_result = 0.0
					avg_inspiration_min_result = 0.0
					avg_expiration_max_result = 0.0
					
					avg_deep_breath_result = np.mean(avg_deep_breath_diff)

					breathing_dict["DBD"] = round(np.mean(dbd_list),2)

					avg_inspiration_min_result = np.mean(inspiration_min)
					avg_expiration_max_result = np.mean(expiration_max)
					
					if avg_deep_breath_result and (avg_expiration_max_result or avg_inspiration_min_result):
						breathing_dict["RSA"] = round(avg_deep_breath_result/breathing_dict["rr_mean"], 2)
						# breathing_dict["RSA"] = round(float(float(avg_deep_breath_result)/float((avg_inspiration_min_result + avg_expiration_max_result))) / 2, 2)

					if avg_expiration_max_result and avg_inspiration_min_result:
						breathing_dict["ratio"] = round(float(avg_expiration_max_result)/float(avg_inspiration_min_result), 2)
					
					normal = test_interpertation.RANGES['Normal'].replace(">","").replace("=","")
					ab_normal = test_interpertation.RANGES['Abnormal'].replace("<","").replace("=","")
					border = test_interpertation.RANGES['Border'].split("-")
					hr_diff = breathing_dict["DBD"]
					breathing_dict["hr_diff"] = hr_diff
					if int(hr_diff) >= int(normal):
						breathing_dict["final_result"] = "Normal"
					elif int(hr_diff) >= int(border[0]) and int(hr_diff) <= int(border[1]):
						breathing_dict["final_result"] = "Border"
					elif int(hr_diff) <= int(ab_normal):
						breathing_dict["final_result"] = "Abnormal"
					else:
						breathing_dict["final_result"] = "Not in Range"
					medical_test_result['deep_breathing_time'] = breathing_dict
					test_report.TEST_RESULT = json.dumps(medical_test_result)
					test_report.save()

			elif option['test_code'] == "TM-21":
				if tx_test_entries:
					raw_data = tx_test_entries[4].KEY_VALUE.split(",")
					heart_rate = [int(raw_data[i+1].strip()) for i in range(0, len(raw_data)) if raw_data[i] if int(raw_data[i].strip())==254 if int(raw_data[i+1].strip())]
					bpm_list = list(set(heart_rate))
					bpm_list.sort()
					bpm_graph = [(i, heart_rate.count(i)) for i in bpm_list]
					medical_test_result = json.loads(test_report.TEST_RESULT)
					results_td = td.time_domain(nni=working_data['RR_list_cor'],plot=False, show=False)
					rr_mean = round(results_td['nni_mean'],5)
					rr_std = round(results_td['sdnn'],5)
					standing_dict = dict()
					if working_data['RR_list_cor']:
						if working_data['RR_list_cor'][0] < 400:
							del working_data['RR_list_cor'][0]
							try:
								working_data['peaklist_cor'] = working_data['peaklist_cor'].tolist()
								del working_data['peaklist_cor'][0]
							except:
								del working_data['peaklist_cor'][0]
					standing_dict["rr_interval"] = working_data['RR_list_cor']
					standing_dict['peaklist'] = list(working_data['peaklist_cor'])
					if working_data['RR_list_cor']:
						standing_dict["rrn"] = working_data['RR_list_cor'][0:-1]
						standing_dict["rrn_plus1"] = working_data['RR_list_cor'][1:]
					else:
						standing_dict["rrn"] = list()
						standing_dict["rrn_plus1"] = list()
					standing_dict["rr_mean"] = round(rr_mean, 2)
					standing_dict["sdnn"] = round(rr_std, 2)
					cv = (float(rr_std)/float(rr_mean))*100
					standing_dict["cv"] = round(cv, 2)
					standing_dict['heart_rate'] = heart_rate
					standing_dict['heart_rate_graph'] = bpm_graph
					standing_dict['heart_rate_start'] = int(min(heart_rate)) - 5
					standing_dict['heart_rate_end'] = int(max(heart_rate)) + 5
					standing_dict['heart_rate_count_start'] = 0
					heart_rate_count = [heart_rate.count(i) for i in bpm_list]
					standing_dict['heart_rate_count_end'] = int(max(heart_rate_count)) + 5
					if min(working_data['RR_list_cor']) != 0 or min(working_data['RR_list_cor']) != 0.0:
						standing_dict['rr_interval_start'] = int(min(working_data['RR_list_cor'])) - 100
					else:
						standing_dict['rr_interval_start'] = 0
					standing_dict['rr_interval_end'] = int(max(working_data['RR_list_cor'])) + 100
					if len(working_data['RR_list_cor']) >= 16:
						standing_dict["15th_min"] = round(min(working_data['RR_list_cor'][12:17]), 2)
						if len(working_data['RR_list_cor']) >= 31:
							standing_dict["30th_max"] = round(max(working_data['RR_list_cor'][27:32]), 2)
							standing_dict["ratio"] = round(float(max(working_data['RR_list_cor'][27:32]))/float(min(working_data['RR_list_cor'][12:17])), 2)
						else:
							standing_dict["30th_max"] = 0.0
							standing_dict["ratio"] = 0.0
					else:
						standing_dict["15th_min"] = 0.0
						standing_dict["30th_max"] = 0.0
						standing_dict["ratio"] = 0.0

					normal = test_interpertation.RANGES['Normal'].replace(">","").replace("=","")
					ab_normal = test_interpertation.RANGES['Abnormal'].replace("<","").replace("=","")
					border = test_interpertation.RANGES['Border'].split("-")
					if float(standing_dict["ratio"]) >= float(normal):
						standing_dict["final_result"] = "Normal"
					elif float(standing_dict["ratio"]) >= float(border[0]) and float(standing_dict["ratio"]) <= float(border[1]):
						standing_dict["final_result"] = "Border"
					elif float(standing_dict["ratio"]) <= float(ab_normal):
						standing_dict["final_result"] = "Abnormal"
					else:
						standing_dict["final_result"] = "Not in Range"

					test_value = tx_test_entries[2].KEY_VALUE.split(",")
					raw_data = list()
					for row in test_value:
						if row:
							raw_data.append(int(row))

					(baseline, ecg_out) = bwr.bwr(raw_data)
					if len(ecg_out) >= 15000:
						ecg_out = [i + 100 for i in ecg_out[0:15000]]
					else:
						ecg_out = [i + 100 for i in ecg_out]
					ecg_out = np.asarray(ecg_out)

					working_data = dict()
					measures = dict()
					qrs_detector = qrs_detect.QRSDetectorOffline(ecg_data=raw_data, verbose=True,log_data=False, plot_data=False, show_plot=False)
					rr_peak = qrs_detector.qrs_peaks_indices
					working_data['peaklist_cor'] = rr_peak
					nni = np.diff(rr_peak)
					rr_interval = (nni / 250.0)*1000
					working_data['RR_list_cor'] = rr_interval.tolist()
					if working_data['RR_list_cor']:
						if working_data['RR_list_cor'][0] < 400:
							del working_data['RR_list_cor'][0]
							try:
								working_data['peaklist_cor'] = working_data['peaklist_cor'].tolist()
								del working_data['peaklist_cor'][0]
							except:
								del working_data['peaklist_cor'][0]
					results_td = td.time_domain(nni=working_data['RR_list_cor'],plot=False, show=False)
					measures['bpm']= int(round(results_td['hr_mean']))
					standing_dict["supine_rr_interval"] = working_data['RR_list_cor']
					standing_dict['supine_peaklist'] = list(working_data['peaklist_cor'])
					medical_test_result['ecg_standing_time'] = standing_dict
					
					test_report.TEST_RESULT = json.dumps(medical_test_result)
					test_report.save()
			elif option['test_code'] == "TM-22":
				if tx_test_entries:
					raw_data = tx_test_entries[0].KEY_VALUE.split(",")
					heart_rate = [int(raw_data[i+1].strip()) for i in range(0, len(raw_data)) if raw_data[i] if int(raw_data[i].strip())==254 if int(raw_data[i+1].strip())]
					bpm_list = list(set(heart_rate))
					bpm_list.sort()
					bpm_graph = [(i, heart_rate.count(i)) for i in bpm_list]
					medical_test_result = json.loads(test_report.TEST_RESULT)
					results_td = td.time_domain(nni=working_data['RR_list_cor'],plot=False, show=False)
					rr_mean = round(results_td['nni_mean'],5)
					rr_std = round(results_td['sdnn'],5)
					valsalva_dict = dict()
					if working_data['RR_list_cor']:
						if working_data['RR_list_cor'][0] < 400:
							del working_data['RR_list_cor'][0]
							try:
								working_data['peaklist_cor'] = working_data['peaklist_cor'].tolist()
								del working_data['peaklist_cor'][0]
							except:
								del working_data['peaklist_cor'][0]
					valsalva_dict["rr_interval"] = working_data['RR_list_cor']
					valsalva_dict['peaklist'] = list(working_data['peaklist_cor'])
					if working_data['RR_list_cor']:
						valsalva_dict["rrn"] = working_data['RR_list_cor'][0:-1]
						valsalva_dict["rrn_plus1"] = working_data['RR_list_cor'][1:]
					else:
						valsalva_dict["rrn"] = list()
						valsalva_dict["rrn_plus1"] = list()
					valsalva_dict["rr_mean"] = round(rr_mean, 2)
					valsalva_dict["sdnn"] = round(rr_std, 2)
					cv = (float(rr_std)/float(rr_mean))*100
					valsalva_dict["cv"] = round(cv, 2)
					valsalva_dict['heart_rate'] = heart_rate
					valsalva_dict['heart_rate_graph'] = bpm_graph
					valsalva_dict['heart_rate_start'] = int(min(heart_rate)) - 5
					valsalva_dict['heart_rate_end'] = int(max(heart_rate)) + 5
					valsalva_dict['heart_rate_count_start'] = 0
					heart_rate_count = [heart_rate.count(i) for i in bpm_list]
					valsalva_dict['heart_rate_count_end'] = int(max(heart_rate_count)) + 5
					if min(working_data['RR_list_cor']) != 0 or min(working_data['RR_list_cor']) != 0.0:
						valsalva_dict['rr_interval_start'] = int(min(working_data['RR_list_cor'])) - 100
					else:
						valsalva_dict['rr_interval_start'] = 0
					valsalva_dict['rr_interval_end'] = int(max(working_data['RR_list_cor'])) + 100
					context ={"test_value": test_value[1251:5000]}
					maneuver_min = deep_breathing_rr_calculation(request, context)
					valsalva_dict["min_rr"] = round(maneuver_min["nni_min"], 2)

					context ={"test_value": test_value[5001:]}
					maneuver_max = deep_breathing_rr_calculation(request, context)
					valsalva_dict["max_rr"] = round(maneuver_max["nni_max"], 2)

					if maneuver_min["nni_min"] and maneuver_max["nni_max"]:
						valsalva_dict["ratio"] = round(float(maneuver_max["nni_max"])/float(maneuver_min["nni_min"]), 2)

					normal = test_interpertation.RANGES['Normal'].replace(">","").replace("=","")
					ab_normal = test_interpertation.RANGES['Abnormal'].replace("<","").replace("=","")
					if float(valsalva_dict["ratio"]) >= float(normal):
						valsalva_dict["final_result"] = "Normal"
					elif float(valsalva_dict["ratio"]) <= float(ab_normal):
						valsalva_dict["final_result"] = "Abnormal"
					else:
						valsalva_dict["final_result"] = "Not in Range"
					medical_test_result['ecg_valsalva_time'] = valsalva_dict
				
					test_report.TEST_RESULT = json.dumps(medical_test_result)
					test_report.save()
			else:
				if tx_test_entries:			
					raw_data = tx_test_entries[0].KEY_VALUE.split(",")
					heart_rate = [int(raw_data[i+1].strip()) for i in range(0, len(raw_data)) if raw_data[i] if int(raw_data[i].strip())==254 if int(raw_data[i+1].strip())]
					bpm_list = list(set(heart_rate))
					bpm_list.sort()
					bpm_graph = [(i, heart_rate.count(i)) for i in bpm_list]
					resting_dict = dict()
					resting_dict['bpm'] = measures['bpm']
					if working_data['RR_list_cor']:
						if working_data['RR_list_cor'][0] < 400:
							del working_data['RR_list_cor'][0]
							try:
								working_data['peaklist_cor'] = working_data['peaklist_cor'].tolist()
								del working_data['peaklist_cor'][0]
							except:
								del working_data['peaklist_cor'][0]
					resting_dict['peaklist'] = list(working_data['peaklist_cor'])
					medical_test_result =dict()
					rr_mean = np.mean(working_data['RR_list_cor'])
					resting_dict['rr_mean'] =rr_mean
					resting_dict['rr_interval'] = working_data['RR_list_cor']
					if working_data['RR_list_cor']:
						resting_dict["rrn"] = working_data['RR_list_cor'][0:-1]
						resting_dict["rrn_plus1"] = working_data['RR_list_cor'][1:]
					else:
						resting_dict["rrn"] = list()
						resting_dict["rrn_plus1"] = list()
					resting_dict['heart_rate'] = heart_rate
					resting_dict['heart_rate_graph'] = bpm_graph
					resting_dict['heart_rate_start'] = int(min(heart_rate)) - 5
					resting_dict['heart_rate_end'] = int(max(heart_rate)) + 5
					resting_dict['heart_rate_count_start'] = 0
					heart_rate_count = [heart_rate.count(i) for i in bpm_list]
					resting_dict['heart_rate_count_end'] = int(max(heart_rate_count)) + 5
					if min(working_data['RR_list_cor']) != 0 or min(working_data['RR_list_cor']) != 0.0:
						resting_dict['rr_interval_start'] = int(min(working_data['RR_list_cor'])) - 100
					else:
						resting_dict['rr_interval_start'] = 0
					resting_dict['rr_interval_end'] = int(max(working_data['RR_list_cor'])) + 100
					normal_rr = test_interpertation.RANGES['Normal_rr'].split("-")
					ab_normal_rr = test_interpertation.RANGES['Abnormal_rr'].replace("<","").replace(">","").split("&")
					normal_hr = test_interpertation.RANGES['Normal_hr'].split("-")
					ab_normal_hr = test_interpertation.RANGES['Abnormal_hr'].replace("<","").replace(">","").split("&")
					rr_mean = float(rr_mean/1000)
					if float(rr_mean) >= float(normal_rr[0]) and float(rr_mean) <= float(normal_rr[1]):
						resting_dict["final_rr_result"] = "Normal"
					elif float(rr_mean) < float(ab_normal_rr[0]) or float(rr_mean) > float(ab_normal_rr[1]):
						resting_dict["final_rr_result"] = "Abnormal"
					else:
						resting_dict["final_rr_result"] = "Not in Range"

					if int(measures['bpm']) >= int(normal_hr[0]) and int(measures['bpm']) <= int(normal_hr[1]):
						resting_dict["final_hr_result"] = "Normal"
					elif int(measures['bpm']) < int(ab_normal_hr[0]) or int(measures['bpm']) > int(ab_normal_hr[1]):
						resting_dict["final_hr_result"] = "Abnormal"
					else:
						resting_dict["final_hr_result"] = "Not in Range"

					medical_test_result["resting"] = resting_dict
					test_report.TEST_RESULT = json.dumps(medical_test_result)
					test_report.save()

			if test_report.TEST_RESULT:
				medical_test["result"] = json.loads(test_report.TEST_RESULT)
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def kodys_can_sympathetic(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	ma_medical_test_list = list()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").last()
		medical_test_types = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").order_by("pk")
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").exists():
			device_details = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").first()
		else:
			device_details = dict()
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		medical_test['medical_device'] = medical_device
		medical_test['device_details'] = device_details
		instruction = MA_MEDICALTESTINSTRUCTION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, INSTRUCTION_TYPE="PROCEDURE", DATAMODE="A")
		medical_test['instruction'] = json.loads(instruction.INSTRUCTION_CONTENT)
		prodecure = MA_MEDICALTESTINSTRUCTION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, INSTRUCTION_TYPE="HELP", DATAMODE="A")
		medical_test['prodecure'] = json.loads(prodecure.INSTRUCTION_CONTENT)
		medical_test['prodecure_image'] = prodecure.INSTRUCTION_IMAGE
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		medical_test['test_interpertation'] = test_interpertation.RANGES
		
		if option['test_entry']:
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			medical_test['test_type'] = test_report.TEST_TYPE 

		if option['test_code'] and option['test_entry']:
			if test_report.TEST_TYPE != "All_test":
				medical_test_types = medical_test_types[0:6]
			for ma_medical_test in medical_test_types:
				ma_medical_test_list.append(ma_medical_test.CODE)
			next_procedure_index = ma_medical_test_list.index(option['test_code']) 
			if test_report.TEST_TYPE != "All_test" and option['test_code'] == "TM-24":
				next_procedure_code = ma_medical_test_list[next_procedure_index]
			else:
				next_procedure_code = ma_medical_test_list[next_procedure_index + 1]
			prodecure = MA_MEDICALTESTINSTRUCTION.objects.get(MEDICALTESTMASTER__CODE=next_procedure_code, INSTRUCTION_TYPE="HELP", DATAMODE="A")
			medical_test['next_prodecure'] = json.loads(prodecure.INSTRUCTION_CONTENT)
			medical_test['next_prodecure_image'] = prodecure.INSTRUCTION_IMAGE
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			medical_test_result = json.loads(test_report.TEST_RESULT)
			if option['test_code'] == "TM-23":
				postural_dict = dict()
				if tx_test_entries and tx_test_entries[0].KEY_VALUE and tx_test_entries[6].KEY_VALUE:
					postural_dict["fall_in_systolic"] = int(tx_test_entries[0].KEY_VALUE) - int(tx_test_entries[6].KEY_VALUE)
					postural_dict["supine_bp"] = "%d / %d" %(int(tx_test_entries[0].KEY_VALUE), int(tx_test_entries[1].KEY_VALUE))
					postural_dict["standing_bp"] = "%d / %d"%(int(tx_test_entries[3].KEY_VALUE), int(tx_test_entries[4].KEY_VALUE))
					postural_dict["after_1_min_bp"] = "%d / %d"%(int(tx_test_entries[6].KEY_VALUE), int(tx_test_entries[7].KEY_VALUE))
					normal = test_interpertation.RANGES['Normal'].replace("<","").replace("=","")
					ab_normal = test_interpertation.RANGES['Abnormal'].replace(">","").replace("=","")
					border = test_interpertation.RANGES['Border'].split("-")
					if int(postural_dict["fall_in_systolic"]) <= int(normal):
						postural_dict["final_postural_result"] = "Normal"
					elif int(postural_dict["fall_in_systolic"]) >= int(border[0]) and int(postural_dict["fall_in_systolic"]) <= int(border[1]):
						postural_dict["final_postural_result"] = "Border"
					elif int(postural_dict["fall_in_systolic"]) >= int(ab_normal):
						postural_dict["final_postural_result"] = "Abnormal"
					else:
						postural_dict["final_postural_result"] = "Abnormal"
				else:
					postural_dict["fall_in_systolic"] = 0
					postural_dict["final_postural_result"] = "Not in Range"
			
				medical_test_result['ecg_postural'] = postural_dict
			elif option['test_code'] == "TM-24":
				sustained_dict = dict()
				if tx_test_entries and tx_test_entries[1].KEY_VALUE and tx_test_entries[4].KEY_VALUE:
					sustained_dict["increase_in_diasystolic"] =  int(tx_test_entries[4].KEY_VALUE) - int(tx_test_entries[1].KEY_VALUE)
					sustained_dict["before_bp"] = "%d / %d"%(int(tx_test_entries[0].KEY_VALUE), int(tx_test_entries[1].KEY_VALUE))
					sustained_dict["after_bp"] = "%d / %d" %(int(tx_test_entries[3].KEY_VALUE), int(tx_test_entries[4].KEY_VALUE))
					normal = test_interpertation.RANGES['Normal'].replace(">","").replace("=","")
					ab_normal = test_interpertation.RANGES['Abnormal'].replace("<","").replace("=","")
					border = test_interpertation.RANGES['Border'].split("-")
					if int(sustained_dict["increase_in_diasystolic"]) >= int(normal):
						sustained_dict["final_sustained_result"] = "Normal"
					elif int(sustained_dict["increase_in_diasystolic"]) >= int(border[0]) and int(sustained_dict["increase_in_diasystolic"]) <= int(border[1]):
						sustained_dict["final_sustained_result"] = "Border"
					elif int(sustained_dict["increase_in_diasystolic"]) <= int(ab_normal):
						sustained_dict["final_sustained_result"] = "Abnormal"
					else:
						sustained_dict["final_sustained_result"] = "Abnormal"
				else:
					sustained_dict["increase_in_diasystolic"] = 0
					sustained_dict["final_sustained_result"] = "Not in Range"
				medical_test_result['ecg_sustained'] = sustained_dict

				if test_report.TEST_TYPE == "parasympathetic_test":
					para_sympathetic_list = [medical_test_result["resting"]["final_hr_result"], medical_test_result["deep_breathing_time"]["final_result"], medical_test_result["ecg_standing_time"]["final_result"], medical_test_result["ecg_valsalva_time"]["final_result"]]
					sympathetic_list = [medical_test_result["ecg_postural"]["final_postural_result"], medical_test_result["ecg_sustained"]["final_sustained_result"]]
					para_sympathetic_count = para_sympathetic_list.count("Normal")
					para_sympathetic_border_count = para_sympathetic_list.count("Border")
					para_sympathetic_abnormal_count = para_sympathetic_list.count("Abnormal")

					if para_sympathetic_count == 4:
						medical_test_result['para_sympathetic'] = "Normal"
					elif para_sympathetic_count == 3:
						medical_test_result['para_sympathetic'] = "Mild"
					elif para_sympathetic_count == 2:
						medical_test_result['para_sympathetic'] = "Moderate"
					elif para_sympathetic_count == 1:
						medical_test_result['para_sympathetic'] = "Severe"
					elif para_sympathetic_count == 0:
						medical_test_result['para_sympathetic'] = "Abnormal"
					else:
						medical_test_result['para_sympathetic'] = ""

					
					sympathetic_count = sympathetic_list.count("Normal")
					sympathetic_border_count = sympathetic_list.count("Border")
					sympathetic_abnormal_count = sympathetic_list.count("Abnormal")
					if sympathetic_count == 2:
						medical_test_result['sympathetic'] = "Normal"
					elif sympathetic_count == 1 and sympathetic_border_count == 1:
						medical_test_result['sympathetic'] = "Mild"
					elif sympathetic_count == 1 and sympathetic_abnormal_count == 1:
						medical_test_result['sympathetic'] = "Moderate"
					elif sympathetic_border_count == 2:
						medical_test_result['sympathetic'] = "Moderate"
					elif sympathetic_abnormal_count == 1 and sympathetic_border_count == 1:
						medical_test_result['sympathetic'] = "Severe"
					elif sympathetic_abnormal_count == 2:
						medical_test_result['sympathetic'] = "Abnormal"
					else:
						medical_test_result['sympathetic'] = ""

					if medical_test_result['para_sympathetic'] == "Normal" and medical_test_result['sympathetic'] == "Normal":
						medical_test_result['cardiac_autonomy'] = "Normal"
					elif medical_test_result['para_sympathetic'] != "Normal" and medical_test_result['sympathetic'] != "Normal":
						medical_test_result['cardiac_autonomy'] = "Combined"
					else:
						medical_test_result['cardiac_autonomy'] = ""

			test_report.TEST_RESULT = json.dumps(medical_test_result)
			test_report.save()

			if test_report.TEST_RESULT:
				medical_test["result"] = json.loads(test_report.TEST_RESULT)
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def frequency_domain(rri, fs=4):
	# Estimate the spectral density using Welch's method
	fxx, pxx = signal.welch(x=rri, fs=fs)

	'''
	Segement found frequencies in the bands 
	 - Very Low Frequency (VLF): 0-0.04Hz 
	 - Low Frequency (LF): 0.04-0.15Hz 
	 - High Frequency (HF): 0.15-0.4Hz
	'''
	cond_vlf = (fxx >= 0) & (fxx < 0.04)
	cond_lf = (fxx >= 0.04) & (fxx < 0.15)
	cond_hf = (fxx >= 0.15) & (fxx < 0.4)

	# calculate power in each band by integrating the spectral density 
	vlf = trapz(pxx[cond_vlf], fxx[cond_vlf])
	lf = trapz(pxx[cond_lf], fxx[cond_lf])
	hf = trapz(pxx[cond_hf], fxx[cond_hf])

	# sum these up to get total power
	total_power = vlf + lf + hf

	# find which frequency has the most power in each band
	peak_vlf = fxx[cond_vlf][np.argmax(pxx[cond_vlf])]
	peak_lf = fxx[cond_lf][np.argmax(pxx[cond_lf])]
	peak_hf = fxx[cond_hf][np.argmax(pxx[cond_hf])]

	# fraction of lf and hf
	lf_nu = 100 * lf / (lf + hf)
	hf_nu = 100 * hf / (lf + hf)
	vlf_log = float(np.log(vlf))
	lf_log = float(np.log(lf))
	hf_log = float(np.log(hf))
	ratio_log = float(np.log((float(lf)/float(hf))))
	total_power_log = float(np.log(total_power))
	results = {}
	results['Power VLF (ms2)'] = vlf
	results['Power LF (ms2)'] = lf
	results['Power HF (ms2)'] = hf   

	results['Log VLF'] = vlf_log
	results['Log LF'] = lf_log
	results['Log HF'] = hf_log
	results['Log Total Power'] = total_power_log
	results['Log LF/HF'] = ratio_log
	
	results['Power Total (ms2)'] = total_power

	results['LF/HF'] = (lf/hf)
	results['Peak VLF (Hz)'] = peak_vlf
	results['Peak LF (Hz)'] = peak_lf
	results['Peak HF (Hz)'] = peak_hf

	results['Fraction LF (nu)'] = lf_nu
	results['Fraction HF (nu)'] = hf_nu
	return results, fxx, pxx

def kodys_can_hrv(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	ma_medical_test_list = list()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").last()
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		medical_device = MA_MEDICALAPPDEVICES.objects.get(MEDICAL_APP=kodys_apps, DATAMODE="A")
		if TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").exists():
			device_details = TX_MEDICALDEVICESTATUS.objects.filter(MEDICAL_DEVICE=medical_device, DATAMODE="A").first()
		else:
			device_details = dict()
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		medical_test['medical_device'] = medical_device
		medical_test['device_details'] = device_details
		instruction = MA_MEDICALTESTINSTRUCTION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, INSTRUCTION_TYPE="PROCEDURE", DATAMODE="A")
		medical_test['instruction'] = json.loads(instruction.INSTRUCTION_CONTENT)
		prodecure = MA_MEDICALTESTINSTRUCTION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, INSTRUCTION_TYPE="HELP", DATAMODE="A")
		medical_test['prodecure'] = json.loads(prodecure.INSTRUCTION_CONTENT)
		medical_test['prodecure_image'] = prodecure.INSTRUCTION_IMAGE
		if option['test_entry']:
			test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			medical_test['test_type'] = test_report.TEST_TYPE 

		if option['test_code'] and option['test_entry']:
			medical_test['next_prodecure'] = dict()
			medical_test['next_prodecure_image'] = dict()
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			report_pdf_path="%s/report/CAN/ecg.csv" %(settings.MEDIA_DATA)

			test_value = tx_test_entries[2].KEY_VALUE.split(",")
			raw_data = list()
			for row in test_value:
				if row:
					raw_data.append(int(row))

			(baseline, ecg_out) = bwr.bwr(raw_data)

			if len(ecg_out) >= 300000:
				ecg_out = [i + 100 for i in ecg_out[0:300000]]
			else:
				ecg_out = [i + 100 for i in ecg_out]
			ecg_out = np.asarray(ecg_out)

			if tx_test_entries:		
				working_data = dict()
				measures = dict()
				qrs_detector = qrs_detect.QRSDetectorOffline(ecg_data=raw_data, verbose=True,log_data=False, plot_data=False, show_plot=False)
				rr_peak = qrs_detector.qrs_peaks_indices
				working_data['peaklist_cor'] = rr_peak
				nni = np.diff(rr_peak)
				rr_interval = (nni / 250.0)*1000
				working_data['RR_list_cor'] = rr_interval.tolist()
				if working_data['RR_list_cor']:
					if working_data['RR_list_cor'][0] < 400:
						del working_data['RR_list_cor'][0]
						try:
							working_data['peaklist_cor'] = working_data['peaklist_cor'].tolist()
							del working_data['peaklist_cor'][0]
						except:
							del working_data['peaklist_cor'][0]

			if test_report.TEST_RESULT:
				medical_test_result = json.loads(test_report.TEST_RESULT)
				para_sympathetic_list = [medical_test_result["resting"]["final_hr_result"], medical_test_result["deep_breathing_time"]["final_result"], medical_test_result["ecg_standing_time"]["final_result"], medical_test_result["ecg_valsalva_time"]["final_result"]]
				sympathetic_list = [medical_test_result["ecg_postural"]["final_postural_result"], medical_test_result["ecg_sustained"]["final_sustained_result"]]
				para_sympathetic_count = para_sympathetic_list.count("Normal")
				para_sympathetic_border_count = para_sympathetic_list.count("Border")
				para_sympathetic_abnormal_count = para_sympathetic_list.count("Abnormal")

				if para_sympathetic_count == 4:
					medical_test_result['para_sympathetic'] = "Normal"
				elif para_sympathetic_count == 3:
					medical_test_result['para_sympathetic'] = "Mild"
				elif para_sympathetic_count == 2 :
					medical_test_result['para_sympathetic'] = "Moderate"
				elif para_sympathetic_count == 1:
					medical_test_result['para_sympathetic'] = "Severe"
				elif para_sympathetic_count == 0:
					medical_test_result['para_sympathetic'] = "Abnormal"
				else:
					medical_test_result['para_sympathetic'] = ""

				sympathetic_count = sympathetic_list.count("Normal")
				sympathetic_border_count = sympathetic_list.count("Border")
				sympathetic_abnormal_count = sympathetic_list.count("Abnormal")
				if sympathetic_count == 2:
					medical_test_result['sympathetic'] = "Normal"
				elif sympathetic_count == 1 and sympathetic_border_count == 1:
					medical_test_result['sympathetic'] = "Mild"
				elif sympathetic_count == 1 and sympathetic_abnormal_count == 1:
					medical_test_result['sympathetic'] = "Moderate"
				elif sympathetic_border_count == 2:
					medical_test_result['sympathetic'] = "Moderate"
				elif sympathetic_abnormal_count == 1 and sympathetic_border_count == 1:
					medical_test_result['sympathetic'] = "Severe"
				elif sympathetic_abnormal_count == 2:
					medical_test_result['sympathetic'] = "Abnormal"
				else:
					medical_test_result['sympathetic'] = ""

				if medical_test_result['para_sympathetic'] == "Normal" and medical_test_result['sympathetic'] == "Normal":
						medical_test_result['cardiac_autonomy'] = "Normal"
				elif medical_test_result['para_sympathetic'] != "Normal" and medical_test_result['sympathetic'] != "Normal":
					medical_test_result['cardiac_autonomy'] = "Combined"
				else:
					medical_test_result['cardiac_autonomy'] = ""

			else:
				medical_test_result = dict()
			if tx_test_entries:
				raw_data = tx_test_entries[0].KEY_VALUE.split(",")
				heart_rate = [int(raw_data[i+1].strip()) for i in range(0, len(raw_data)) if raw_data[i] if int(raw_data[i].strip())==254 if int(raw_data[i+1].strip())]
				bpm_list = list(set(heart_rate))
				bpm_list.sort()
				bpm_graph = [(i, heart_rate.count(i)) for i in bpm_list]
				hrv_dict = dict()
				if working_data['RR_list_cor']:
					if working_data['RR_list_cor'][0] < 400:
						del working_data['RR_list_cor'][0]
						try:
							working_data['peaklist_cor'] = working_data['peaklist_cor'].tolist()
							del working_data['peaklist_cor'][0]
						except:
							del working_data['peaklist_cor'][0]

				hrv_dict["rr_interval"] = working_data['RR_list_cor']
				hrv_dict['peaklist'] = list(working_data['peaklist_cor'])
				if working_data['RR_list_cor']:
					hrv_dict["rrn"] = working_data['RR_list_cor'][0:-1]
					hrv_dict["rrn_plus1"] = working_data['RR_list_cor'][1:]
				else:
					hrv_dict["rrn"] = list()
					hrv_dict["rrn_plus1"] = list()

				hrv_dict['heart_rate'] = heart_rate
				hrv_dict['heart_rate_graph'] = bpm_graph
				hrv_dict['heart_rate_start'] = int(min(heart_rate)) - 5
				hrv_dict['heart_rate_end'] = int(max(heart_rate)) + 5
				hrv_dict['heart_rate_count_start'] = 0

				heart_rate_count = [heart_rate.count(i) for i in bpm_list]
				hrv_dict['heart_rate_count_end'] = int(max(heart_rate_count)) + 5
				if min(working_data['RR_list_cor']) != 0 or min(working_data['RR_list_cor']) != 0.0:
					hrv_dict['rr_interval_start'] = int(min(working_data['RR_list_cor'])) - 100
				else:
					hrv_dict['rr_interval_start'] = 0

				hrv_dict['rr_interval_end'] = int(max(working_data['RR_list_cor'])) + 100
				results_td = td.time_domain(nni=working_data['RR_list_cor'],plot=False, show=False)

				if results_td:
					hrv_dict['bpm'] = int(round(results_td['hr_mean']))
					measures['bpm'] = int(round(results_td['hr_mean']))
					hrv_dict["rr_mean"] = round(results_td['nni_mean'],5)
					hrv_dict["sdnn"] = round(results_td['sdnn'],5)
					hrv_dict["rmssd"] = round(results_td['rmssd'],5)
					hrv_dict["nn50"] = round(results_td['nn50'],5)
					hrv_dict["pnn50"] = round(results_td['pnn50'],5)
					hrv_dict["max_rr"] = round(results_td['nni_max'],5)
					hrv_dict["min_rr"] = round(results_td['nni_min'],5)
					hrv_dict["hr_mean"] = round(results_td['hr_mean'],5)
					hrv_dict["sdsd"] = round(results_td['hr_std'],5)
					hrv_dict["hr_mean_duplicate"] = round(np.mean(heart_rate),5)
					hrv_dict["sdsd_duplicate"] = round(np.std(heart_rate), 5)


				cv = (float(round(results_td['sdnn'],5))/float(round(results_td['nni_mean'],5)))*100
				hrv_dict["cv"] = round(cv, 2)

				result_welch,result_frequencies,result_power = fd.welch_psd(nni=working_data['RR_list_cor'],window='hann', show=False,mode='dev')
				result_frequencies = list(result_frequencies)
				result_power = result_power
				result_power = result_power.tolist()
				fft_graph = list()
				for i in range(0, len(result_frequencies)):
					fft_graph.append((round(result_frequencies[i],5),"%.10f"%(result_power[i])))
				hrv_dict['psd_max'] = max(result_power)
				hrv_dict['fft_psd_graph'] = fft_graph
				medical_test_result['hrv_time'] = hrv_dict			
				hrv_dict = dict()
				hrv_dict["lf_peak"] = round(result_welch['fft_peak'][1],5)
				hrv_dict["vlf_peak"] = round(result_welch['fft_peak'][0],5)
				hrv_dict["hf_peak"] = round(result_welch['fft_peak'][2],5)
				hrv_dict["lf_nu"] = round(result_welch['fft_norm'][0],5)
				hrv_dict["hf_nu"] = round(result_welch['fft_norm'][1],5)
				hrv_dict["total_power"] = round(result_welch["fft_total"],5)
				hrv_dict["hf_power"] = round(result_welch['fft_abs'][2],5)
				hrv_dict["lf_power"] = round(result_welch['fft_abs'][1],5)
				hrv_dict["vlf_power"] = round(result_welch['fft_abs'][0],5)
				hrv_dict["ratio"] = round(result_welch['fft_ratio'],5)
				hrv_dict["log_vlf"] =  round(result_welch['fft_log'][0],5)
				hrv_dict["log_lf"] =  round(result_welch['fft_log'][1],5)
				hrv_dict["log_hf"] =  round(result_welch['fft_log'][2],5)
				hrv_dict["log_total_power"] = round(float(np.log(result_welch['fft_total'])),5)
				hrv_dict["log_ratio"] =  round(float(np.log(result_welch['fft_ratio'])),5)
				
				try:
					fft_spectrum_graph = [float(float(hrv_dict["vlf_power"])/float(hrv_dict["vlf_peak"])), float(float(hrv_dict["lf_power"])/float(hrv_dict["lf_peak"])), float(float(hrv_dict["hf_power"])/float(hrv_dict["hf_peak"]))]
					if fft_spectrum_graph:
						hrv_dict["fft_spectrum_max"] = max(fft_spectrum_graph) + 100
						hrv_dict["fft_spectrum_graph"] = [(hrv_dict["vlf_peak"], fft_spectrum_graph[0]), (hrv_dict["lf_peak"], fft_spectrum_graph[1]), (hrv_dict["hf_peak"], fft_spectrum_graph[2])] 
				except Exception,e:
					print("--------------------------------ERROR-------------------------------------------")
					print(e)
					print("--------------------------------ERROR-------------------------------------------")
				medical_test_result['hrv_frequency'] = hrv_dict
				test_report.TEST_RESULT = json.dumps(medical_test_result)
				test_report.save()
				
				for entries in tx_test_entries:
					entries.KEY_VALUE =''
					entries.save()
		
			if test_report.TEST_RESULT:
				medical_test["result"] = json.loads(test_report.TEST_RESULT)
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		print("--------------------------------ERROR-------------------------------------------")
		print(e)
		print("--------------------------------ERROR-------------------------------------------")
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def podo_i_mat(request, option):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test = dict()
	try:
		state = MA_STATE.objects.filter(DATAMODE="A").order_by('pk')
		kodys_apps = MA_MEDICALAPPS.objects.get(CODE=option['app_code'], DATAMODE="A")
		if option['test_code']:
			medical_test_type = MA_MEDICALTESTMASTER.objects.get(CODE=option['test_code'], DATAMODE="A")
		else:
			medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP=kodys_apps, DATAMODE="A").last()
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=option['app_code'], DATAMODE="A").last()
		medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A").order_by('pk')
		medical_test['medical_test_fields'] = medical_test_fields
		medical_test['medical_test_type'] = medical_test_type
		if option['doctor_uid'] != "no_uid":
			doctor = TX_HCP.objects.get(UID=option['doctor_uid'], DATAMODE="A")
		else:
			doctor = ""
		if option['examiner_uid'] != "no_uid":
			examiner = TX_HCP.objects.get(UID=option['examiner_uid'], DATAMODE="A")
		else:
			examiner = ""
		
		patient = TX_PATIENTS.objects.get(UID=option['patient_uid'], DATAMODE="A")
		if doctor:
			medical_test['doctor'] = doctor
		if examiner:
			medical_test['examiner'] = examiner
		medical_test['patient'] = patient
		test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=medical_test_type.CODE, DATAMODE="A")
		for key, value in test_interpertation.RANGES.iteritems():
			medical_test[str(key.replace(" ", "_"))] = [str(key), value]
		if option['test_entry']:
			referred_by_medical_test_type.REFERRED_BY = ""
			referred_by_medical_test_type.save()
			request.session["referred"] = ""
		if option['test_code'] and option['test_entry']:
			tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=option['test_entry'], MEDICALTEST__MEDICALTESTMASTER__CODE=option['test_code'], DATAMODE="A")
			medical_tests = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=option['test_entry'], DATAMODE="A")
			if medical_tests:
				podo_i_mat_test_values = dict()
				for medical_test_value in medical_tests:
					tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__id=medical_test_value.id, DATAMODE="A")
					for tx_test in tx_test_entries:
						podo_i_mat_test_values[tx_test.KEY_NAME.replace(" ","_")] = tx_test.KEY_VALUE
						

				medical_test["podo_i_mat_test_values"] = podo_i_mat_test_values
				report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=option['test_entry'], DATAMODE="A")
				report.TEST_RESULT = json.dumps(podo_i_mat_test_values)
				report.save()
			if tx_test_entries:
				medical_test['test_entry_data'] = tx_test_entries
			else:
				medical_test['test_entry_data'] = ""

		result, msg = ulo._setmsg(success_msg, error_msg, True)
	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test, state


def podo_i_mat_medical_test_entry(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	podo_i_mat_test_values = dict()
	try:
		patient = p_dict['patient_uid'].strip()
		doctor = p_dict.get('doctor_uid', None)
		examiner = p_dict.get('examiner_uid', None)
		app_code = p_dict['app_code'].strip()
		test_code = p_dict['test_code'].strip()
		test_entry = p_dict.get('test_entry', None)
		kodys_apps = MA_MEDICALAPPS.objects.filter(CODE=app_code, DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=app_code, DATAMODE="A").last()
		if test_code:
			# converted_podo_i_mat_image = podo_i_mat_foot_convert(request, p_dict)
			# medical_test_result['converted_podo_i_mat_image'] = converted_podo_i_mat_image
			medical_test_type  = MA_MEDICALTESTMASTER.objects.filter(CODE=test_code, DATAMODE="A").first()
			if doctor.strip() != "no_uid":
				doctor = TX_HCP.objects.get(UID=doctor, DATAMODE="A")
			else:
				doctor = ""
			if examiner.strip() != "no_uid":
				examiner = TX_HCP.objects.get(UID=examiner, DATAMODE="A")
			else:
				examiner = ""
			patients = TX_PATIENTS.objects.get(UID=patient, DATAMODE="A")
			test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=test_code, DATAMODE="A")
			if test_entry and TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, MEDICALTESTMASTER__CODE=test_code).exists():
				medical_test_fields = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, MEDICALTEST__MEDICALTESTMASTER__CODE=test_code)
				for test_fields in medical_test_fields:
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_field_value = test_field_value.replace("?t=101", "")
						test_fields.KEY_VALUE = test_field_value
					test_fields.save()
				medical_test = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, DATAMODE="A").first()
			else:
				medical_test = TX_MEDICALTESTS()
				medical_test.UID = uuid.uuid4().hex[:30]
				medical_test.MEDICALTESTMASTER = medical_test_type
				medical_test.PATIENT = patients
				medical_test.INTERPERTATION = test_interpertation.RANGES
				if doctor:
					medical_test.DOCTOR = doctor
				if examiner:
					medical_test.EXAMINER = examiner
				medical_test.REPORTED_ON = datetime.datetime.now()
				medical_test.save()
				medical_test.FRIENDLY_UID = "TST-%08d"%(medical_test.id)
				medical_test.save() 

				medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A")
				for test_fields in medical_test_fields:
					test_entries = TX_MEDICALTESTENTRIES()
					test_entries.UID = uuid.uuid4().hex[:30]
					test_entries.MEDICALTEST = medical_test
					test_entries.MEDICALTESTFIELDS = test_fields
					test_entries.KEY_NAME = test_fields.KEY_NAME
					test_entries.KEY_CODE = test_fields.KEY_CODE
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_field_value = test_field_value.replace("?t=101", "")
						test_entries.KEY_VALUE = test_field_value
					test_entries.save()

			if TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A").exists():
				pass
			else:
				test_report = TX_MEDICALTESTREPORTS()
				test_report.UID = uuid.uuid4().hex[:30]
				test_report.MEDICALTEST = medical_test
				test_report.REFERRED_BY = referred_by_medical_test_type.REFERRED_BY
				test_report.REPORTED_ON = datetime.datetime.now()
				test_report.TEST_STATUS = "COMPLETED"
				test_report.CREATED_BY = request.user
				test_report.UPDATED_BY = request.user
				test_report.save()
				test_report.FRIENDLY_UID = "REP-%08d"%(test_report.id)
				test_report.save()

				# Pre-calculate ECG results to solve report lag and apply algorithmic fixes
				try:
					processed_results = process_can_test_data(test_report)
					if processed_results:
						test_report.TEST_RESULT = json.dumps(processed_results)
						test_report.save()
				except Exception as e:
					print("Pre-calculation failed: ", e)
			medical_test_result['test_entry_id'] = medical_test.FRIENDLY_UID
			medical_test_result['current_test_code'] = medical_test.MEDICALTESTMASTER.CODE
	
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			medical_test_result['test_entry_id'] = None
			medical_test_result['current_test_code'] = None
			result, msg = ulo._setmsg(success_msg, error_msg, False)
	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test_result


def podo_i_mat_foot_convert(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	image_name = ""
	try:
		side = p_dict['side'].strip()
		podo_i_mat_image = request.FILES.get("podo_i_mat_image", "")
		if podo_i_mat_image:
			if side.lower() == "right":
				with open('%s/Right_I_Mat/%s'%(settings.MEDIA_ROOT, podo_i_mat_image), 'wb+') as destination:
					for chunk in podo_i_mat_image.chunks():
						destination.write(chunk)
				uploaded_podo_i_mat_image ='%s/Right_I_Mat/%s'%(settings.MEDIA_ROOT, podo_i_mat_image)
			else:
				with open('%s/Left_I_Mat/%s'%(settings.MEDIA_ROOT, podo_i_mat_image), 'wb+') as destination:
					for chunk in podo_i_mat_image.chunks():
						destination.write(chunk)
				uploaded_podo_i_mat_image ='%s/Left_I_Mat/%s'%(settings.MEDIA_ROOT, podo_i_mat_image)
			if uploaded_podo_i_mat_image:
				img = cv2.imread(uploaded_podo_i_mat_image) 

				gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

				converted_podo_i_mat_image = uploaded_podo_i_mat_image.replace(podo_i_mat_image.name, "converted_%s"%(podo_i_mat_image.name))

				cv2.imwrite(converted_podo_i_mat_image,gray)
				img = cv2.imread(converted_podo_i_mat_image) 

				avging = cv2.blur(img,(10,10))

				cv2.imwrite(converted_podo_i_mat_image,avging)

				im = Image.open(converted_podo_i_mat_image)

				width, height = im.size

				for x in range(width):
					for y in range(height):
						r,g,b = im.getpixel((x,y))
						num1 = 0
						if (r >= 80 or g >= 80):
							num1 = 1
						else:
							if (b >= 80):
								num1 = 1
							else:
								num1 = 0
						if num1 == 0:
							im.putpixel((x,y), (255, 52, 0))
						else:
							num2 = 0
							if ((r >= 110 or (r <= 80 or g >= 110)) or (g <= 80)):
								num2 = 1
							else:
								if b >= 110:
									num2 = 1
								else:
									if (b <= 80):
										num2 = 1
									else:
										num2 = 0
							if num2 == 0:
								im.putpixel((x,y), (248, 146, 103))
							else:
								num3 = 0
								if ((r >= 150 or (r <= 110 or g >= 150)) or (g <= 110)):
									num3 = 1
								else:
									if b >= 150:
										num3 = 1
									else:
										if b <= 110:
											num3 = 1
										else:
											num3 = 0
								if num3 == 0:
									im.putpixel( (x,y),(238, 231, 84))
								else:
									num4 = 0
									if ((r >= 200 or (r <= 150 or g >= 200)) or (g <= 150)):
										num4 = 1
									else:
										if b >= 200:
											num4 = 1 
										else:
											if b <= 150:
												num4 = 1
											else:
												num4 =0
									if num4 == 0:
										im.putpixel( (x,y), (106, 231, 81))
									else:
										num5 = 0
										if ((r >= 210 or (r <= 200 or g >= 210)) or (g <= 200)):
											num5 = 1
										else:
											if b >= 210: 
												num5 = 1 
											else: 
												if b <= 200:
													num5 = 1
												else:
													num5 = 0
										if num5 == 0:
											im.putpixel( (x,y), (131, 110, 177))
										else:
											num6 = 0
											if ((r >= 255 or (r <= 210 or g >= 255)) or (g <= 210)):
												num6 = 1
											else:
												if b >= 255 :
													num6 = 1 
												else:
													if b <= 210 :
														num6 = 1
													else:
														num6 = 0
											if num6 == 0:
												im.putpixel( (x,y), (255, 255, 255))

				im.save(converted_podo_i_mat_image)  
				image_name = "converted_%s"%(podo_i_mat_image.name)
		result, msg = ulo._setmsg(success_msg, error_msg, True)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return image_name


def kodys_can_medical_test_entry(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	try:
		test_type = p_dict.get('test_type',"RESTING")
		patient = p_dict['patient_uid'].strip()
		doctor = p_dict.get('doctor_uid', None)
		examiner = p_dict.get('examiner_uid', None)
		app_code = p_dict['app_code'].strip()
		test_code = p_dict['test_code'].strip()
		test_entry = p_dict.get('test_entry', None)
		kodys_apps = MA_MEDICALAPPS.objects.filter(CODE=app_code, DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=app_code, DATAMODE="A").last()
		if test_code:
			medical_test_type  = MA_MEDICALTESTMASTER.objects.filter(CODE=test_code, DATAMODE="A").first()
			if test_code != "TM-25":
				test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=test_code, DATAMODE="A")
			if doctor.strip() != "no_uid":
				doctor = TX_HCP.objects.get(UID=doctor, DATAMODE="A")
			else:
				doctor = ""
			if examiner.strip() != "no_uid":
				examiner = TX_HCP.objects.get(UID=examiner, DATAMODE="A")
			else:
				examiner = ""
			patients = TX_PATIENTS.objects.get(UID=patient, DATAMODE="A")

			if test_entry and TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, MEDICALTESTMASTER__CODE=test_code).exists():
				request.session["referred"] = ""
				medical_test_fields = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, MEDICALTEST__MEDICALTESTMASTER__CODE=test_code)
				for test_fields in medical_test_fields:
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_fields.KEY_VALUE = test_field_value
					test_fields.save()
				medical_test = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, DATAMODE="A").first()
			else:
				medical_test = TX_MEDICALTESTS()
				medical_test.UID = uuid.uuid4().hex[:30]
				medical_test.MEDICALTESTMASTER = medical_test_type
				medical_test.PATIENT = patients
				if test_code != "TM-25":
					medical_test.INTERPERTATION = test_interpertation.RANGES
				if doctor:
					medical_test.DOCTOR = doctor
				if examiner:
					medical_test.EXAMINER = examiner
				medical_test.REPORTED_ON = datetime.datetime.now()
				medical_test.save()
				if test_entry:
					test_entry = test_entry.strip()
					medical_test.FRIENDLY_UID = test_entry
				else:
					medical_test.FRIENDLY_UID = "TST-%08d"%(medical_test.id)
				medical_test.save() 

				medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A")
				for test_fields in medical_test_fields:
					test_entries = TX_MEDICALTESTENTRIES()
					test_entries.UID = uuid.uuid4().hex[:30]
					test_entries.MEDICALTEST = medical_test
					test_entries.MEDICALTESTFIELDS = test_fields
					test_entries.KEY_NAME = test_fields.KEY_NAME
					test_entries.KEY_CODE = test_fields.KEY_CODE
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_entries.KEY_VALUE = test_field_value
					test_entries.save()
				
			if TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A").exists():
				test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A")
				if (test_report.TEST_TYPE == "All_test" or test_report.TEST_TYPE == "hrv_test") and test_code == "TM-25":
					test_report.TEST_STATUS = "COMPLETED"
					test_report.save()
			else:
				test_report = TX_MEDICALTESTREPORTS()
				test_report.UID = uuid.uuid4().hex[:30]
				test_report.MEDICALTEST = medical_test
				# test_report.TEMPERATURE_SCALE = test_type
				test_report.REFERRED_BY = referred_by_medical_test_type.REFERRED_BY
				test_report.REPORTED_ON = datetime.datetime.now()
				if test_type == "hrv_test" and test_code == "TM-25":
					test_report.TEST_STATUS = "COMPLETED"
				test_report.TEST_TYPE = test_type
				test_report.CREATED_BY = request.user
				test_report.UPDATED_BY = request.user
				test_report.save()
				test_report.FRIENDLY_UID = "REP-%08d"%(test_report.id)
				test_report.save()

				# Pre-calculate ECG results to solve report lag and apply algorithmic fixes
				try:
					processed_results = process_can_test_data(test_report)
					if processed_results:
						test_report.TEST_RESULT = json.dumps(processed_results)
						test_report.save()
				except Exception as e:
					print("Pre-calculation failed: ", e)
			medical_test_result['test_entry_id'] = medical_test.FRIENDLY_UID
			medical_test_result['current_test_code'] = medical_test.MEDICALTESTMASTER.CODE
	
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			medical_test_result['test_entry_id'] = None
			medical_test_result['current_test_code'] = None
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test_result


def kodys_can_sympathetic_medical_test_entry(request, p_dict):
	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	medical_test_result = dict()
	try:
		test_type = p_dict.get('test_type',"RESTING")

		patient = p_dict['patient_uid'].strip()
		doctor = p_dict.get('doctor_uid', None)
		examiner = p_dict.get('examiner_uid', None)
		app_code = p_dict['app_code'].strip()
		test_code = p_dict['test_code'].strip()
		test_entry = p_dict.get('test_entry', None)
		kodys_apps = MA_MEDICALAPPS.objects.filter(CODE=app_code, DATAMODE="A")
		referred_by_medical_test_type = MA_MEDICALTESTMASTER.objects.filter(MEDICAL_APP__CODE=app_code, DATAMODE="A").last()
		if test_code:
			medical_test_type  = MA_MEDICALTESTMASTER.objects.filter(CODE=test_code, DATAMODE="A").first()
			test_interpertation = MA_MEDICALTESTMASTERINTERPERTATION.objects.get(MEDICALTESTMASTER__CODE=test_code, DATAMODE="A")
			if doctor.strip() != "no_uid":
				doctor = TX_HCP.objects.get(UID=doctor, DATAMODE="A")
			else:
				doctor = ""
			if examiner.strip() != "no_uid":
				examiner = TX_HCP.objects.get(UID=examiner, DATAMODE="A")
			else:
				examiner = ""
			patients = TX_PATIENTS.objects.get(UID=patient, DATAMODE="A")

			if test_entry and TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, MEDICALTESTMASTER__CODE=test_code).exists():
				medical_test_fields = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST__FRIENDLY_UID=test_entry, MEDICALTEST__MEDICALTESTMASTER__CODE=test_code)
				for test_fields in medical_test_fields:
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_fields.KEY_VALUE = test_field_value
					test_fields.save()
				medical_test = TX_MEDICALTESTS.objects.filter(FRIENDLY_UID=test_entry, DATAMODE="A").first()
			else:
				medical_test = TX_MEDICALTESTS()
				medical_test.UID = uuid.uuid4().hex[:30]
				medical_test.MEDICALTESTMASTER = medical_test_type
				medical_test.PATIENT = patients
				medical_test.INTERPERTATION = test_interpertation.RANGES
				if doctor:
					medical_test.DOCTOR = doctor
				if examiner:
					medical_test.EXAMINER = examiner
				medical_test.REPORTED_ON = datetime.datetime.now()
				medical_test.save()
				if test_entry:
					test_entry = test_entry.strip()
					medical_test.FRIENDLY_UID = test_entry
				else:
					medical_test.FRIENDLY_UID = "TST-%08d"%(medical_test.id)
				medical_test.save() 

				medical_test_fields = MA_MEDICALTESTFIELDS.objects.filter(MEDICALTESTMASTER=medical_test_type, DATAMODE="A")
				for test_fields in medical_test_fields:
					test_entries = TX_MEDICALTESTENTRIES()
					test_entries.UID = uuid.uuid4().hex[:30]
					test_entries.MEDICALTEST = medical_test
					test_entries.MEDICALTESTFIELDS = test_fields
					test_entries.KEY_NAME = test_fields.KEY_NAME
					test_entries.KEY_CODE = test_fields.KEY_CODE
					test_field_value = p_dict.get(test_fields.KEY_CODE, "")
					if test_field_value:
						test_field_value = test_field_value.strip()
						test_entries.KEY_VALUE = test_field_value
					test_entries.save()
				
			if TX_MEDICALTESTREPORTS.objects.filter(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A").exists():
				test_report = TX_MEDICALTESTREPORTS.objects.get(MEDICALTEST__FRIENDLY_UID=medical_test.FRIENDLY_UID, DATAMODE="A")
				if test_report.TEST_TYPE == "parasympathetic_test" and test_code == "TM-24":
					test_report.TEST_STATUS = "COMPLETED"
					test_report.save()
			else:
				test_report = TX_MEDICALTESTREPORTS()
				test_report.UID = uuid.uuid4().hex[:30]
				test_report.MEDICALTEST = medical_test
				# test_report.TEMPERATURE_SCALE = test_type
				test_report.REFERRED_BY = referred_by_medical_test_type.REFERRED_BY
				test_report.REPORTED_ON = datetime.datetime.now()
				test_report.TEST_TYPE = test_type
				test_report.CREATED_BY = request.user
				test_report.UPDATED_BY = request.user
				test_report.save()
				test_report.FRIENDLY_UID = "REP-%08d"%(test_report.id)
				test_report.save()

				# Pre-calculate ECG results to solve report lag and apply algorithmic fixes
				try:
					processed_results = process_can_test_data(test_report)
					if processed_results:
						test_report.TEST_RESULT = json.dumps(processed_results)
						test_report.save()
				except Exception as e:
					print("Pre-calculation failed: ", e)
			medical_test_result['test_entry_id'] = medical_test.FRIENDLY_UID
			medical_test_result['current_test_code'] = medical_test.MEDICALTESTMASTER.CODE
	
			result, msg = ulo._setmsg(success_msg, error_msg, True)
		else:
			medical_test_result['test_entry_id'] = None
			medical_test_result['current_test_code'] = None
			result, msg = ulo._setmsg(success_msg, error_msg, False)

	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
		result, msg = ulo._setmsg(success_msg, error_msg, False)
	logger.info(ulo.end_log(request, fn))
	return result, msg, medical_test_result

def process_can_test_data(test_report):
	"""
	Centralized processing for CAN/ECG tests to be used during SAVE or VIEW.
	Handles: Notch Filter (50Hz), Bandpass (5-15Hz), BWR, QRS Detection, and HRV.
	"""
	medical_test = test_report.MEDICALTEST
	test_code = medical_test.MEDICALTESTMASTER.CODE
	
	# Get raw data from entries
	tx_test_entries = TX_MEDICALTESTENTRIES.objects.filter(MEDICALTEST=medical_test).order_by('id')
	if not tx_test_entries:
		return None

	# Logic varies by test code
	raw_ecg_str = ""
	if test_code in ["TM-20", "TM-21", "TM-22", "TM-23", "TM-24", "TM-25"]:
		# For CAN tests, the ECG data is usually in a specific entry
		for entry in tx_test_entries:
			if entry.KEY_CODE in ["TM-20", "TM-21", "TM-22", "TM-23", "TM-24", "TM-25", "RAW_DATA"]:
				raw_ecg_str = entry.KEY_VALUE.replace(" ","")
				break
	
	if not raw_ecg_str:
		return None

	try:
		raw_data_list = [int(x) for x in raw_ecg_str.split(",") if x]
		
		# 1. Notch Filter (50Hz - Power Line Interference)
		fs = 250.0 
		f0 = 50.0  
		Q = 30.0   
		b_notch, a_notch = signal.iirnotch(f0, Q, fs)
		notched_data = signal.filtfilt(b_notch, a_notch, raw_data_list)
		
		# 2. Butterworth Bandpass (5-15Hz - QRS enhancement)
		lowcut, highcut = 5.0, 15.0
		nyq = 0.5 * fs
		B, A = signal.butter(2, [lowcut/nyq, highcut/nyq], btype='band')
		smooth_data = signal.filtfilt(B, A, notched_data)
		
		# 3. Baseline Wander Removal (Wavelet-based)
		(baseline, ecg_out) = bwr.bwr(smooth_data)
		
		# 4. QRS Detection (Improved Pan-Tompkins via QRSDetectorOffline)
		qrs_detector = qrs_detect.QRSDetectorOffline(ecg_data=ecg_out, verbose=False)
		rr_peaks = qrs_detector.qrs_peaks_indices
		nni = np.diff(rr_peaks)
		rr_intervals = (nni / fs) * 1000.0  # Convert to ms
		
		# 5. HRV Analysis (Time Domain)
		if len(rr_intervals) > 2:
			results_td = td.time_domain(nni=rr_intervals.tolist(), plot=False, show=False)
			hr_mean = results_td.get('hr_mean', 0)
			sdnn = results_td.get('sdnn', 0)
		else:
			hr_mean, sdnn = 0, 0

		# Compile Results for Persistent Storage
		processed_results = {
			"processed_ecg": ",".join([str(round(i + 100, 2)) for i in ecg_out[:15000]]),
			"rr_intervals": rr_intervals.tolist(),
			"bpm": int(round(hr_mean)) if hr_mean else 0,
			"sdnn": round(sdnn, 2) if sdnn else 0,
			"poincare": {
				"rrn": rr_intervals[:-1].tolist() if len(rr_intervals) > 1 else [],
				"rrn_plus1": rr_intervals[1:].tolist() if len(rr_intervals) > 1 else []
			}
		}
		return processed_results
	except Exception as e:
		print("Error in process_can_test_data: ", e)
		return None

	fn=ulo._fn()
	logger.info(ulo.start_log(request, fn))
	success_msg= 'Success'
	error_msg ='ERROR'
	results = dict()
	try:
		raw_data = list()
		for row in options["test_value"]:
			if row:
				raw_data.append(int(row))

		(baseline, ecg_out) = bwr.bwr(raw_data)

		ecg_out = [i + 100 for i in ecg_out]

		ecg_out = np.asarray(ecg_out)

		working_data = dict()
		qrs_detector = qrs_detect.QRSDetectorOffline(ecg_data=raw_data, verbose=True,log_data=False, plot_data=False, show_plot=False)
		rr_peak = qrs_detector.qrs_peaks_indices
		nni = np.diff(rr_peak)
		rr_interval = (nni / 250.0)*1000
		working_data['RR_list_cor'] = rr_interval.tolist()

		if working_data['RR_list_cor']:
			del working_data['RR_list_cor'][0]

		if working_data['RR_list_cor']:
			min_rr = np.min(working_data['RR_list_cor'])
			max_rr = np.max(working_data['RR_list_cor'])
			results["nni_max"] = max_rr
			results["nni_min"] = min_rr
		else:
			results["nni_max"] = ""
			results["nni_min"] = ""
	except Exception,e:
		logger.error(ulo.error_log(request, sys.exc_traceback.tb_lineno, e))
	logger.info(ulo.end_log(request, fn))
	return results
