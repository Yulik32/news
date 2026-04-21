from django.shortcuts import redirect
from django.http import HttpResponseForbidden

class AdminAccessMiddleware:
    """Защита админки - только для админов, вход только через сайт"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Проверяем, пытается ли пользователь зайти в админку
        if request.path.startswith('/admin/') or request.path.startswith('/admin-panel/'):
            # Если пользователь не авторизован - отправляем на страницу входа сайта
            if not request.user.is_authenticated:
                return redirect('/accounts/login/?next=' + request.path)
            
            # Если пользователь авторизован, но не админ - доступ запрещен
            if not request.user.is_staff:
                return HttpResponseForbidden("Доступ запрещен. Только для администраторов.")
        
        # Если все проверки пройдены - продолжаем
        response = self.get_response(request)
        return response