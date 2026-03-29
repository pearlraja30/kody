"""app_config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import os
from django.conf.urls import url
from django.contrib import admin
import django.views.static as django_static_view
from django.conf import settings
from kodys.views import *

# --- HARDENED STATIC/MEDIA ROUTING (v2.2.41) ---
# 1. Bundled Assets Root (Read-Only Installation Directory)
INSTALL_DIR = os.path.dirname(settings.BASE_DIR)
BUNDLED_MEDIA_ROOT = os.path.join(INSTALL_DIR, "app_assets", "media")
BUNDLED_DATA_ROOT = os.path.join(INSTALL_DIR, "app_assets", "DATA")

# Find the real physical location of gstatic (handles source vs dist flattening)
_source_gstatic = os.path.join(settings.BASE_DIR, "kodys", "templates", "gstatic")
_dist_gstatic = os.path.join(INSTALL_DIR, "kodys", "templates", "gstatic")
GSTATIC_PATH = _source_gstatic if os.path.exists(_source_gstatic) else _dist_gstatic

def flexible_serve(request, path, document_root=None, fallback_root=None, **kwargs):
    """Attempt to serve from primary document_root, fall back to fallback_root."""
    def local_log(msg):
        try:
            import datetime
            local_app_data = os.environ.get('LOCALAPPDATA', os.environ.get('APPDATA', os.getcwd()))
            l_path = os.path.join(local_app_data, "KodysFootClinikV2", "logs", "application_trace.log")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(l_path, 'a') as f:
                f.write("%s | [ERROR] | ASSET_404 | %s\n" % (timestamp, msg))
        except: pass

    # 1. Try Primary (Writable AppData)
    primary_file = os.path.join(document_root, path)
    if os.path.exists(primary_file):
        return django_static_view.serve(request, path, document_root=document_root, **kwargs)
    
    # 2. Try Fallback (Bundled Program Files)
    fallback_file = os.path.join(fallback_root, path)
    if os.path.exists(fallback_file):
        return django_static_view.serve(request, path, document_root=fallback_root, **kwargs)
    
    # 3. Final Fallback with Logging
    local_log("404 Asset: %s (Tried: %s and %s)" % (path, primary_file, fallback_file))
        
    return django_static_view.serve(request, path, document_root=document_root, **kwargs)

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # 1. Bundled Static Assets (CSS, JS, Fonts)
    url(r'^static/(?P<path>.*)$', django_static_view.serve, {'document_root': GSTATIC_PATH}),
    
    # 2. User Media / Bundled Media Fallback (v2.2.41)
    url(r'^site_media/(?P<path>.*)$', flexible_serve, {
        'document_root': settings.MEDIA_ROOT, 
        'fallback_root': BUNDLED_MEDIA_ROOT
    }),
    
    # 3. Application Data / Bundled Data Fallback (v2.2.41)
    url(r'^site_data/(?P<path>.*)$', flexible_serve, {
        'document_root': settings.MEDIA_DATA, 
        'fallback_root': BUNDLED_DATA_ROOT
    }),
    
    # 4. Django Admin Static Files
    url(r'^static/admin/(?P<path>.*)$', django_static_view.serve, {'document_root': settings.STATIC_ROOT}),
    url(r'^about/$', about, name="about"),
    url(r'^signin/$', signin, name="signin"),
    url(r'^signout/$', signout, name="signout"),
	url(r'^$', home, name="home"),
    url(r'^customer/support/$', customer_support, name="customer_support"),
    url(r'^export/patients/$', export_patients_excel, name="export_patients_excel"),
    url(r'^hospital/profile/$', hospital_profile, name="hospital_profile"),
    url(r'^doctors/$', doctors, name="doctors"),
    url(r'^doctors/(?P<speciality>[-\d]+)/$', doctors, name="doctors"),
    url(r'^hcp/add/$', hcp_add, name="hcp_add"),
    url(r'^hcp/edit/(?P<hcp_uid>[-\w]+)/$', hcp_edit, name="hcp_edit"),
    url(r'^hcp/delete/(?P<hcp_uid>[-\w]+)/$', hcp_delete, name="hcp_delete"),
    url(r'^patients/$', patients, name="patients"),
    url(r'^patient/add/$', patients_add, name="patients_add"),
    url(r'^patient/edit/(?P<patients_uid>[-\w]+)/$', patients_edit, name="patients_edit"),
    url(r'^patient/delete/(?P<patients_uid>[-\w]+)/$', patients_delete, name="patients_delete"),
    url(r'^app/configuration/$', app_configuration, name="app_configuration"),
    url(r'^reports/$', reports, name="reports"),
    url(r'^reports/(?P<speciality>[-\w]+)/(?P<duration>[-\w]+)/$', reports, name="reports"),
    url(r'^manuals/$', manuals, name="manuals"),
    url(r'^manuals/(?P<category>[-\w]+)/$', manuals, name="manuals"),
    url(r'^report/view/canyscope/(?P<test_entry_code>[-\w]+)/$', canyscope_report_view, name="canyscope_report_view"),
    url(r'^report/view/(?P<test_entry_code>[-\w]+)/$', report_view, name="report_view"),
    url(r'^report/view/(?P<test_entry_code>[-\w]+)/(?P<mode>[-\w]+)/$', report_view, name="report_view"),
    url(r'^manuals/view/(?P<manuals_code>[-\w]+)/$', manuals_view, name="manuals_view"),
    url(r'^database/backup/$', database_backup, name="database_backup"),
    url(r'^restore/database/$', restore_database, name="restore_database"),
    url(r'^app/configuration/mail/(?P<key_code>[-\w]+)/$', app_configuration_mail, name="app_configuration_mail"),
    url(r'^app/configuration/settings/$', app_configuration_settings, name="app_configuration_settings"),
    url(r'^patient/search/(?P<search_key>[-\w]+)/$', patient_search, name="patient_search"),
    url(r'^patient/edit/search/(?P<patient_uid>[-\w]+)/(?P<search_key>[-\w]+)/$', patient_edit_search, name="patient_edit_search"),
    # url(r'^medical/test/entry/$', medical_test_entry, name="medical_test_entry"),
    # url(r'^medical/test/details/(?P<app_code>[-\w]+)/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$', medical_test_details, name="medical_test_details"),
    # url(r'^APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/$', thermocool_foot, name="thermocool_foot"),
    url(r'^APP-01/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$', doppler, name="doppler"),
    url(r'^APP-01/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', doppler, name="doppler"),
    url(r'^APP-01/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', doppler, name="doppler"),
    url(r'^graphical/APP-01/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', doppler_graphical, name="doppler_graphical"),
    url(r'^graphical/APP-01/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', doppler_graphical, name="doppler_graphical"),
    url(r'^graphical/template/upload/$', doppler_graphical_template, name="doppler_graphical_template"),
    url(r'^APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$', vpt_foot, name="vpt_foot"),
    url(r'^APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', vpt_foot, name="vpt_foot"),
    url(r'^APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', vpt_foot, name="vpt_foot"),
    url(r'^hand/APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', vpt_hand, name="vpt_hand"),
    url(r'^hand/APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', vpt_hand, name="vpt_hand"),
    url(r'^hand/APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$', vpt_hand, name="vpt_hand"),    
    url(r'^APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$', vpt_ultra_foot, name="vpt_ultra_foot"),
    url(r'^APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', vpt_ultra_foot, name="vpt_ultra_foot"),
    url(r'^APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', vpt_ultra_foot, name="vpt_ultra_foot"),
    url(r'^hand/APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', vpt_ultra_hand, name="vpt_ultra_hand"),
    url(r'^hand/APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', vpt_ultra_hand, name="vpt_ultra_hand"),
    url(r'^hand/APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$', vpt_ultra_hand, name="vpt_ultra_hand"),
    url(r'^APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$', thermocool_foot, name="thermocool_foot"),
    url(r'^APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', thermocool_foot, name="thermocool_foot"),
    url(r'^APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', thermocool_foot, name="thermocool_foot"),
    url(r'^APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$', thermocool_foot, name="thermocool_foot"),
    url(r'^hand/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', thermocool_hand, name="thermocool_hand"),
    url(r'^hand/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', thermocool_hand, name="thermocool_hand"),
    url(r'^hand/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$', thermocool_hand, name="thermocool_hand"),
    url(r'^generate/report/(?P<test_uid>[-\w]+)/$', generate_report, name="generate_report"),
    url(r'^test/patient/edit/(?P<patient_uid>[-\w]+)/(?P<app_code>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$', test_patient_edit, name="test_patient_edit"),
    url(r'^test/patient/hand/edit/(?P<patient_uid>[-\w]+)/(?P<app_code>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', test_patient_hand_edit, name="test_patient_hand_edit"),
    url(r'^test/patient/other/edit/(?P<patient_uid>[-\w]+)/(?P<app_code>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', test_patient_other_edit, name="test_patient_other_edit"),
    url(r'^test/impression/$', test_impression, name="test_impression"),
    url(r'^device-config-save/(?P<app_code>[-\w]+)/$', device_config_save, name="device_config_save"),
    url(r'^test/referred/$', test_referred, name="test_referred"),
    url(r'^email/report/$', email_report, name="email_report"),
    # url(r'^other/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$', thermocool_other, name="thermocool_hand"),
    url(r'^other/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', thermocool_other, name="thermocool_hand"),
    url(r'^other/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', thermocool_other, name="thermocool_other"),
    url(r'^other/APP-04/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$', thermocool_other, name="thermocool_other"),
    url(r'^other/APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', vpt_ultra_other, name="vpt_ultra_other"),
    url(r'^other/APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', vpt_ultra_other, name="vpt_ultra_other"),
    url(r'^other/APP-03/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$', vpt_ultra_other, name="vpt_ultra_other"),
    url(r'^other/APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', vpt_other, name="vpt_other"),
    url(r'^other/APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', vpt_other, name="vpt_other"),
    url(r'^other/APP-02/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$', vpt_other, name="vpt_other"),
    url(r'^generate/license/$', generate_license, name="generate_license"),
    url(r'^patient/email/$', patient_email, name="patient_email"),
    url(r'^patient/id/search/(?P<search_key>[-\w]+)/$', patient_id_search, name="patient_id_search"),
    url(r'^test/patient/graphical/edit/(?P<patient_uid>[-\w]+)/(?P<app_code>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', test_patient_graphical_edit, name="test_patient_graphical_edit"),
    url(r'^APP-05/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$', podo_i_mat, name="podo_i_mat"),
    url(r'^APP-05/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', podo_i_mat, name="podo_i_mat"),
    url(r'^APP-05/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', podo_i_mat, name="podo_i_mat"),
    # url(r'^APP-05/foot/convert/$', podo_i_mat_foot_convert, name="podo_i_mat_foot_convert"),
    url(r'^APP-06/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$', podo_t_map, name="podo_t_map"),
    url(r'^APP-06/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', podo_t_map, name="podo_t_map"),
    url(r'^APP-06/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', podo_t_map, name="podo_t_map"),
    url(r'^APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/$', kodys_can, name="kodys_can"),
    url(r'^APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', kodys_can, name="kodys_can"),
    url(r'^APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', kodys_can, name="kodys_can"),
    url(r'^sympathetic/APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', kodys_can_sympathetic, name="kodys_can_sympathetic"),
    url(r'^sympathetic/APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', kodys_can_sympathetic, name="kodys_can_sympathetic"),
    url(r'^sympathetic/APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$', kodys_can_sympathetic, name="kodys_can_sympathetic"),
    url(r'^hrv/APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', kodys_can_hrv, name="kodys_can_hrv"),
    url(r'^hrv/APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/$', kodys_can_hrv, name="kodys_can_hrv"),
    url(r'^hrv/APP-07/(?P<patient_uid>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/(?P<test_entry>[-\w]+)/(?P<previous_test_code>[-\w]+)/$', kodys_can_hrv, name="kodys_can_hrv"),
    url(r'^test/patient/hrv/edit/(?P<patient_uid>[-\w]+)/(?P<app_code>[-\w]+)/(?P<doctor_uid>[-\w]+)/(?P<examiner_uid>[-\w]+)/(?P<test_code>[-\w]+)/$', test_patient_hrv_edit, name="test_patient_hrv_edit"),
    ]
