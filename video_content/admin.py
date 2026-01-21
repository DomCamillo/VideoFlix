from django.contrib import admin

from .models import Video

class videoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status')
    search_fields = ('category',)
    ordering = ('created_at',)


    """  Customize the admin panel form to provide better help text for the thumbnail field."""
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if 'thumbnail' in form.base_fields:
            form.base_fields['thumbnail'].help_text = (
                'Optional: Upload a custom thumbnail. '
                'If left empty, a thumbnail will be automatically generated from the video.'
            )

        return form


admin.site.register(Video, videoAdmin)

