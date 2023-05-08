from django.contrib import admin

from .models import Item, Menu, ItemProxy, Url


# Register your models here.
class UrlAdmin(admin.ModelAdmin):
    search_fields = ('__all__',)
    list_filter = ('name',)


class MenuAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class ItemAdmin(admin.ModelAdmin):
    list_filter = ('menu',)
    search_fields = ('title', 'url',)


class ItemProxyAdmin(admin.ModelAdmin):
    list_filter = ('menu',)
    search_fields = ('title', 'url',)

    def get_queryset(self, request):
        return ItemProxy.objects.filter(parent=None)


admin.site.register(Url, UrlAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(ItemProxy, ItemProxyAdmin)
