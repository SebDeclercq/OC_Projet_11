# Generated by Django 2.1.7 on 2019-03-15 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Food', '0002_auto_20190315_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='products',
            field=models.ManyToManyField(to='Food.Product'),
        ),
    ]
