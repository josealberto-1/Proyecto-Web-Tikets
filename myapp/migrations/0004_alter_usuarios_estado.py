# Generated by Django 5.0.2 on 2024-03-22 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_alter_clientes_correoelectronico'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuarios',
            name='estado',
            field=models.CharField(blank=True, default='Activo', max_length=10, null=True, verbose_name='Estado'),
        ),
    ]
