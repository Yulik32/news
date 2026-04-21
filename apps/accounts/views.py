from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView  # Добавь этот импорт!
from .models import Profile

# Исправленный класс
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        # После входа проверяем, есть ли параметр next
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        
        # Если пользователь админ - отправляем в админку
        if self.request.user.is_staff:
            return '/admin/'
        
        # Обычного пользователя - на главную
        return '/'

# Остальные функции...
def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('news:index')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    """Профиль пользователя"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        profile, created = Profile.objects.get_or_create(user=user)
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.save()
        
        messages.success(request, 'Профиль обновлён')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html', {'user': request.user})

def custom_logout(request):
    """Кастомный выход с редиректом на главную"""
    logout(request)
    return redirect('news:index')