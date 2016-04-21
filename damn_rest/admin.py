from django.contrib import admin
from django import forms
from reversion.admin import VersionAdmin

from mptt.admin import MPTTModelAdmin
from mptt.forms import TreeNodeChoiceField

from damn_rest.models import FileReference, AssetReference, Path

class FileReferenceAdminForm(forms.ModelForm):
    class Meta:
        model = FileReference
        exclude = ()
        #widgets = {
        #  'path': TreeNodeChoiceField(queryset=Path.objects.all())
        #}

class FileReferenceAdmin(VersionAdmin):
    list_display = ( '__unicode__', 'nr_of_versions')
    form = FileReferenceAdminForm

class AssetReferenceAdmin(VersionAdmin):
    list_display = ( '__unicode__', 'nr_of_versions')

admin.site.register(FileReference, FileReferenceAdmin)
admin.site.register(AssetReference, AssetReferenceAdmin)

admin.site.register(Path, MPTTModelAdmin)
