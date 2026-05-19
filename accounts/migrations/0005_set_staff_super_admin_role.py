from django.db import migrations


def set_staff_roles(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(is_staff=True).update(role='super_admin')


def reverse_roles(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(role='super_admin').update(role='customer')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_user_managed_territories_user_role'),
    ]

    operations = [
        migrations.RunPython(set_staff_roles, reverse_roles),
    ]
