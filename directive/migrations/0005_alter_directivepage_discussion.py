# Generated by Django 3.2 on 2021-09-19 00:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directive', '0004_alter_directiveinstruction_instruction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directivepage',
            name='discussion',
            field=models.TextField(max_length=300, null=True, verbose_name='How would you lead the duscussion with the client?'),
        ),
    ]
