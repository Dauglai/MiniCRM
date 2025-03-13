from django.utils.timezone import now
from django.contrib.auth.middleware import get_user
from django.apps import apps  # 👈 Загружаем модель динамически

class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = get_user(request)
        if user.is_authenticated:
            Profile = apps.get_model("employee", "Profile")  # 👈 Получаем модель динамически
            profile = Profile.objects.filter(author=user).first()
            if profile:
                profile.last_seen = now()
                profile.save(update_fields=["last_seen"])

        return response
