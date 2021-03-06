# Generated by Django 2.2.12 on 2021-02-26 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_auto_20210226_0300'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='photo',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.ManyToManyField(blank=True, related_name='categories', to='auctions.Category'),
        ),
    ]
