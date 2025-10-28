from django.db import migrations
from django.db.models.functions import Substr

def truncate_referido_a(apps, schema_editor):
    DocumentoReferencia = apps.get_model('historiales', 'DocumentoReferencia')
    DocumentoReferencia.objects.update(referido_a=Substr('referido_a', 1, 40))

class Migration(migrations.Migration):

    dependencies = [
        ('historiales', '0005_alter_documentoreferencia_referido_a'),
    ]

    operations = [
        migrations.RunPython(truncate_referido_a),
    ]