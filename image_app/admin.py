from django.contrib import admin
from image_app.models import UploadedImage


class UploadedImageAdmin(admin.ModelAdmin):
    pass


admin.site.register(UploadedImage, UploadedImageAdmin)
