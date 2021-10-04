# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import F


def clear_thumbnails_cache_migrate(apps, schema_editor):
    SessaoPlenaria = apps.get_model("sessao", "SessaoPlenaria")
    OrdemDia = apps.get_model("sessao", "OrdemDia")
    ExpedienteMateria = apps.get_model("sessao", "ExpedienteMateria")

    for m in (OrdemDia, ExpedienteMateria):

        p1 = {f'{m._meta.model_name}__isnull': False}
        p2 = {f'{m._meta.model_name}__data_ordem': F('data_inicio')}

        sps = SessaoPlenaria.objects.filter(
            **p1
        ).exclude(
            **p2
        ).distinct().all().values('id', 'data_inicio')

        for sp in sps:
            m.objects.filter(
                sessao_plenaria_id=sp['id']
            ).exclude(
                data_ordem=F('sessao_plenaria__data_inicio')
            ).update(data_ordem=sp['data_inicio'])


class Migration(migrations.Migration):

    dependencies = [
        ('parlamentares', '0020_fix_inicio_mandato'),
    ]

    operations = [
        migrations.RunPython(clear_thumbnails_cache_migrate),
    ]
