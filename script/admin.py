from django.contrib import admin
from models import Line
# Register your models here.

class LineAdmin(admin.ModelAdmin):
    list_display = ('speaker', 'line', 'content_id')
    ordering = ['content']

    def content_id(self, obj):
        return obj.content.id

admin.site.register(Line, LineAdmin)