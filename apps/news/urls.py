from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.index, name='index'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('article/<int:pk>/save/', views.save_article, name='save_article'),
    path('saved/', views.saved_articles, name='saved_articles'),
    path('filter/save/', views.save_filter, name='save_filter'),
    path('sources/', views.sources, name='sources'),
    path('source/<int:pk>/', views.source_detail, name='source_detail'),
    path('api/search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('article/<int:article_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]