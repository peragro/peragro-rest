from django.contrib import admin

from reversion import VersionAdmin

from damn_rest.models import FileReference, AssetReference

class FileReferenceAdmin(VersionAdmin):
    list_display = ( '__unicode__', 'nr_of_versions')
        
class AssetReferenceAdmin(VersionAdmin):
    list_display = ( '__unicode__', 'nr_of_versions')
        
admin.site.register(FileReference, FileReferenceAdmin)
admin.site.register(AssetReference, AssetReferenceAdmin)
