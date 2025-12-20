# api/middleware.py
from .models import UserProfile


class AutoCreateUserProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not hasattr(request.user, 'profile'):
            UserProfile.objects.create(user=request.user, role='client')

        response = self.get_response(request)
        return response