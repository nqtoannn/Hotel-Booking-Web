# Generated by Django 4.2.5 on 2023-10-28 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_alter_bookinghotel_date_return'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookinghotel',
            name='date_return',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]