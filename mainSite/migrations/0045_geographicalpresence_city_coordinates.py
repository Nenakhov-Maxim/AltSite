from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainSite', '0044_portfolio_facade_systems_alter_portfolio_object_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='geographicalpresence',
            name='city_x',
            field=models.FloatField(
                blank=True,
                help_text='Абсолютная X-координата подписи в системе SVG-карты. Если заполнена вместе с Y, смещения не используются.',
                null=True,
                verbose_name='X города на карте',
            ),
        ),
        migrations.AddField(
            model_name='geographicalpresence',
            name='city_y',
            field=models.FloatField(
                blank=True,
                help_text='Абсолютная Y-координата подписи в системе SVG-карты. Если заполнена вместе с X, смещения не используются.',
                null=True,
                verbose_name='Y города на карте',
            ),
        ),
    ]
