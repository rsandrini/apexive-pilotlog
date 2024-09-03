# Generated by Django 5.1 on 2024-09-03 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DynamicModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table', models.CharField(max_length=255)),
                ('guid', models.CharField(max_length=255)),
                ('user_id', models.IntegerField()),
                ('platform', models.IntegerField()),
                ('_modified', models.BigIntegerField()),
                ('meta', models.JSONField()),
            ],
        ),
    ]
