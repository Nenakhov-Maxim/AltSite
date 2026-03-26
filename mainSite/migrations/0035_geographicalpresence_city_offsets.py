from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainSite', '0034_geographicalpresence_map_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='geographicalpresence',
            name='city_offset_x',
            field=models.IntegerField(default=0, verbose_name='Смещение города по X'),
        ),
        migrations.AddField(
            model_name='geographicalpresence',
            name='city_offset_y',
            field=models.IntegerField(default=0, verbose_name='Смещение города по Y'),
        ),
    ]
