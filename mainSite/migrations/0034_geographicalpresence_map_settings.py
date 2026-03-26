from django.db import migrations, models


def set_visible_regions_from_addresses(apps, schema_editor):
    GeographicalPresence = apps.get_model('mainSite', 'GeographicalPresence')
    RegionAdress = apps.get_model('mainSite', 'RegionAdress')

    visible_region_ids = RegionAdress.objects.filter(
        visible_on_site=True
    ).values_list('geographical_presence_id', flat=True).distinct()

    GeographicalPresence.objects.filter(id__in=visible_region_ids).update(visible_on_map=True)


class Migration(migrations.Migration):

    dependencies = [
        ('mainSite', '0033_alter_representatives_company_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='geographicalpresence',
            name='city_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='Город для подписи на карте'),
        ),
        migrations.AddField(
            model_name='geographicalpresence',
            name='linked_regions',
            field=models.ManyToManyField(blank=True, help_text='Эти регионы будут подсвечиваться вместе с текущим.', to='mainSite.geographicalpresence', verbose_name='Связанные регионы'),
        ),
        migrations.AddField(
            model_name='geographicalpresence',
            name='popup_description',
            field=models.TextField(blank=True, help_text='Необязательный текст, который показывается над адресами.', verbose_name='Описание для popup'),
        ),
        migrations.AddField(
            model_name='geographicalpresence',
            name='show_city_label',
            field=models.BooleanField(default=False, verbose_name='Показывать город на карте'),
        ),
        migrations.AddField(
            model_name='geographicalpresence',
            name='visible_on_map',
            field=models.BooleanField(default=False, verbose_name='Показывать на карте'),
        ),
        migrations.AlterField(
            model_name='regionadress',
            name='visible_on_site',
            field=models.BooleanField(default=False, verbose_name='Показывать в popup?'),
        ),
        migrations.RunPython(set_visible_regions_from_addresses, migrations.RunPython.noop),
    ]
