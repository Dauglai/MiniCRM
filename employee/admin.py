from django.contrib import admin
from .models import Task, Topic, Profile, Comment, Result, Coordination
# Register your models here.

admin.site.register(Task)
admin.site.register(Topic)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Result)
admin.site.register(Coordination)