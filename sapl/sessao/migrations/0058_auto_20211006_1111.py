# Generated by Django 2.2.24 on 2021-10-06 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sessao', '0057_auto_20211006_0917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessaoplenaria',
            name='status_cronometro_aparte',
            field=models.CharField(default='S', max_length=1, verbose_name='Status do cronômetro discurso'),
        ),
        migrations.AlterField(
            model_name='sessaoplenaria',
            name='status_cronometro_consideracoes_finais',
            field=models.CharField(default='S', max_length=1, verbose_name='Status do cronômetro discurso'),
        ),
        migrations.AlterField(
            model_name='sessaoplenaria',
            name='status_cronometro_ordem_do_dia',
            field=models.CharField(default='S', max_length=1, verbose_name='Status do cronômetro discurso'),
        ),
    ]
