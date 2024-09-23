from django.contrib import admin
from .models import Task, Status, Role, Topic, Profile, Comment, Result, Coordination
# Register your models here.

admin.site.register(Task)
admin.site.register(Status)
admin.site.register(Role)
admin.site.register(Topic)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Result)
admin.site.register(Coordination)