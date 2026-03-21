# -*- coding: utf-8 -*-
# From Django
from django.forms.widgets import *
from django import forms
from django.contrib.auth import (get_user_model, password_validation)
from django.contrib.auth.models import User
from django.conf import settings
import re
from models import *

class SigninForm(forms.Form):
    username = forms.CharField(label="User Name / Email", max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username', 'autocomplete': 'off'}))
    password = forms.CharField(label="Password", max_length=30, required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def __init__(self, *args, **kwargs):
        super(SigninForm, self).__init__(*args, **kwargs)
        self.fields['username'].error_messages['required'] = "Username cannot be empty"
        self.fields['password'].error_messages['required'] = "Password cannot be empty"

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user = User.objects.filter(email__iexact=username.lower()).first()
        if not user:
            user = User.objects.filter(username__iexact=username).first()
        if user and not user.is_staff:
            raise forms.ValidationError("Your account is inactive. Please contact administrator")
        
        if not user:
            raise forms.ValidationError("There is no account in our system for this Username")    
            
        return username
        
    def clean_password(self):
        username = self.cleaned_data.get('username')
        user = User.objects.filter(email__iexact=username).first()
        if not user:
            user = User.objects.filter(username__iexact=username).first()
        password = self.cleaned_data.get('password')
        if user:
            if not user.check_password(password):
                raise forms.ValidationError("Invalid Password")
        
        return password

class HCPForm(forms.Form):
    hcp_username = forms.CharField(label="User Name / Email", max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Username', 'autocomplete': 'off'}))
    hcp_password = forms.CharField(label="Password", max_length=30, required=False, widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    email = forms.CharField(max_length=100, required=False, label="", widget=forms.TextInput(attrs={'placeholder': 'Email', 'autocomplete': 'off'}))

    def __init__(self, *args, **kwargs):
        self.hcp_uid = kwargs.pop("hcp_uid", None)
        super(HCPForm, self).__init__(*args, **kwargs)

    def clean_hcp_username(self):
        username = self.cleaned_data.get('hcp_username')
        if username:
            if self.hcp_uid:
                hcp = TX_HCP.objects.get(UID=self.hcp_uid, DATAMODE="A")
                if hcp.ACCOUNTUSER and hcp.ACCOUNTUSER.USER.username == username:
                    raise forms.ValidationError("Username is already exists.")
            else:
                user = User.objects.filter(username__iexact=username).first()
                if user:
                    raise forms.ValidationError("Username is already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and '@' in email:
            email = email.strip().lower()
            valid_email = re.match(settings.SA_ACCOUNTAPP_EMAIL_REGEX, email, re.I)
            if valid_email:
                if self.hcp_uid:
                    hcp_email = TX_HCP.objects.get(UID=self.hcp_uid, DATAMODE="A").EMAIL
                    if hcp_email == email:
                        pass
                    elif User.objects.filter(email=email).exists():
                        raise forms.ValidationError("Email is already exists")
                elif User.objects.filter(email=email).exists():
                        raise forms.ValidationError("Email is already exists")
            else:
                raise forms.ValidationError("Please enter valid Email address.")
    
        return email 


class HospitalForm(forms.Form):
    email = forms.CharField(max_length=100, required=False, label="", widget=forms.TextInput(attrs={'placeholder': 'Email', 'autocomplete': 'off'}))

    def __init__(self, *args, **kwargs):
        super(HospitalForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and '@' in email:
            email = email.strip().lower()
            valid_email = re.match(settings.SA_ACCOUNTAPP_EMAIL_REGEX, email, re.I)
            if valid_email:
                accountuser = TX_ACCOUNTUSER.objects.filter(ACCOUNTROLE__NAME="MANAGER", DATAMODE="A").first()
                if accountuser:
                    hospital_email = User.objects.get(username=accountuser.USER.username).email
                    if hospital_email == email:
                        pass
                    elif User.objects.filter(email=email).exists():
                        raise forms.ValidationError("Email is already exists")
            else:
                raise forms.ValidationError("Please enter valid Email address.")
        else:
            raise forms.ValidationError("Please enter valid Email address.")
    
        return email 