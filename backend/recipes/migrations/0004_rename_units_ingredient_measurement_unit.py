# Generated by Django 3.2 on 2022-11-27 18:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0003_rename_shoppinglist_shoppingcart"),
    ]

    operations = [
        migrations.RenameField(
            model_name="ingredient",
            old_name="units",
            new_name="measurement_unit",
        ),
    ]
