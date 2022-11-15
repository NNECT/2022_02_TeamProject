from django.contrib import admin
from .models import User, MessageCard, Tag, Reply

admin.site.register(User)
admin.site.register(MessageCard)
admin.site.register(Reply)


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name', )}


admin.site.register(Tag, TagAdmin)
