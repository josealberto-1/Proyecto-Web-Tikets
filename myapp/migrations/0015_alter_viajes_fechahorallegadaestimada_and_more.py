# Generated by Django 5.0.9 on 2024-12-03 20:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0014_alter_vehiculos_anofabricacion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='viajes',
            name='fechahorallegadaestimada',
            field=models.DateTimeField(verbose_name='Hora estimada de llegada del viaje'),
        ),
        migrations.AlterField(
            model_name='viajes',
            name='vehiculoid',
            field=models.ForeignKey(blank=True, db_column='vehiculoid', null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.vehiculos', verbose_name='ID de Vehiculo'),
        ),
    ]
