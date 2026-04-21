from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from unfold.dashboard import Dashboard, DashboardWidget
from unfold.dashboard.widgets import RecentActionsWidget, AppListWidget, LinkListWidget

class CustomDashboard(Dashboard):
    def get_widgets(self, request):
        from .models import Article, Source, Category
        
        return [
            # Блок 1: Быстрые действия
            DashboardWidget(
                title="Быстрые действия",
                widget=LinkListWidget(
                    links=[
                        {"title": "➕ Добавить новость", "url": reverse("admin:news_article_add")},
                        {"title": "📡 Добавить источник", "url": reverse("admin:news_source_add")},
                        {"title": "🏷️ Добавить категорию", "url": reverse("admin:news_category_add")},
                    ]
                ),
                column=1,
                order=1,
            ),
            
            # Блок 2: Последние новости
            DashboardWidget(
                title="Последние новости",
                widget=AppListWidget(
                    models=["apps.news.models.Article"],
                    limit=5,
                ),
                column=1,
                order=2,
            ),
            
            # Блок 3: Статистика
            DashboardWidget(
                title="Статистика",
                widget=LinkListWidget(
                    links=[
                        {"title": f"📰 Всего статей: {Article.objects.count()}", 
                         "url": reverse("admin:news_article_changelist")},
                        {"title": f"📡 Активных источников: {Source.objects.filter(is_active=True).count()}", 
                         "url": reverse("admin:news_source_changelist")},
                        {"title": f"🏷️ Категорий: {Category.objects.count()}", 
                         "url": reverse("admin:news_category_changelist")},
                    ]
                ),
                column=2,
                order=1,
            ),
            
            # Блок 4: Последние действия
            DashboardWidget(
                title="Недавние действия",
                widget=RecentActionsWidget(limit=10),
                column=2,
                order=2,
            ),
        ]

# Функция для обратного вызова
def dashboard_callback(request, context):
    return CustomDashboard().get_widgets(request)