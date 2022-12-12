from django.contrib import admin
from .models import User, MessageCard, Tag, Reply

admin.site.register(User)
admin.site.register(MessageCard)
admin.site.register(Reply)
admin.site.register(Tag)
