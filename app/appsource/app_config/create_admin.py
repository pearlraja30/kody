import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from django.contrib.auth.models import User

try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created with password 'admin123'")
    else:
        u = User.objects.get(username='admin')
        u.set_password('admin123')
        u.save()
        print("Updated password for 'admin' to 'admin123'")
except Exception as e:
    print("Error: %s" % str(e))
