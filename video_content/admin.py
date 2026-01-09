from django.contrib import admin

from .models import Video

class videoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status')
    search_fields = ('category',)
    ordering = ('created_at',)

admin.site.register(Video, videoAdmin)

