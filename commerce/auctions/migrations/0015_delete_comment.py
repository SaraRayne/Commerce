# Generated by Django 2.2.12 on 2021-03-06 21:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_listing_active'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
