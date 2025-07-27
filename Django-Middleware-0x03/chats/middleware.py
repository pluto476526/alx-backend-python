# chats/middleware.py

from django.http import HttpResponseForbidden
from datetime import datetime
from collections import defaultdict
import logging, time

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        logging.basicConfig(
            filename='requests.log',
            level=logging.INFO,
            format='%(message)s'
        )

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else 'Anonymous'
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logging.info(log_entry)

        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_hour = datetime.now().hour

        # Block access if NOT between 18:00 (6PM) and 21:00 (9PM)
        if not (18 <= current_hour < 21):
            return HttpResponseForbidden("Access to the messaging app is restricted during this time.")

        return self.get_response(request)


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Tracks messages per IP: {ip: [timestamp1, timestamp2, ...]}
        self.message_log = defaultdict(list)
        self.limit = 5  # messages
        self.time_window = 60  # seconds

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith("/api/messages"):
            ip = self.get_client_ip(request)
            now = time.time()

            # Filter timestamps within the last 60 seconds
            recent_timestamps = [
                ts for ts in self.message_log[ip] if now - ts < self.time_window
            ]
            self.message_log[ip] = recent_timestamps

            if len(recent_timestamps) >= self.limit:
                return HttpResponseForbidden("Rate limit exceeded. Try again later.")

            self.message_log[ip].append(now)

        return self.get_response(request)

    def get_client_ip(self, request):
        # Handles proxies or direct requests
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')



class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # Allow if not authenticated (e.g., login route) or staff
        if user.is_authenticated:
            # You can customize this part depending on how user roles are defined
            if not (user.is_superuser or getattr(user, 'role', '') in ['admin', 'moderator']):
                return HttpResponseForbidden("Access denied. Admin or Moderator only.")

        return self.get_response(request)

