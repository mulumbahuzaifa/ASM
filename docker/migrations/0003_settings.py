# Generated by Django 3.1 on 2020-11-13 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docker', '0002_auto_20200923_1506'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('afparam', models.CharField(max_length=100, primary_key=True, serialize=False, verbose_name='Parameter')),
                ('afvalue', models.CharField(max_length=200, verbose_name='Value')),
                ('aftimestamp', models.DateTimeField(auto_now_add=True, verbose_name='Time stamp')),
            ],
        ),
    ]
