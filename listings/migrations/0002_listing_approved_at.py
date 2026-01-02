from django.db import migrations, models
from django.db.models import F


def backfill_approved_at(apps, schema_editor):
    Listing = apps.get_model('listings', 'Listing')
    Listing.objects.filter(status='APPROVED', approved_at__isnull=True).update(
        approved_at=F('updated_at')
    )


class Migration(migrations.Migration):
    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_approved_at, migrations.RunPython.noop),
    ]
