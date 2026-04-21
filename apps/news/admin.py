from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display
from django.db.models import Count
from .models import Category, Source, Article, SavedArticle, Comment

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'articles_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_per_page = 20
    
    def articles_count(self, obj):
        return obj.articles.count()
    articles_count.short_description = 'Статей'


@admin.register(Source)
class SourceAdmin(ModelAdmin):
    list_display = ['name', 'source_type', 'category', 'is_active', 'last_parsed', 'articles_count']
    list_filter = ['source_type', 'is_active', 'category']
    search_fields = ['name', 'url']
    list_per_page = 20
    list_editable = ['is_active']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'url', 'source_type', 'category'),
            'classes': ('tab',),
        }),
        ('Статус', {
            'fields': ('is_active', 'last_parsed', 'parse_error'),
            'classes': ('tab',),
        }),
    )
    
    def articles_count(self, obj):
        return obj.articles.count()
    articles_count.short_description = 'Статей'


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ['title_preview', 'category', 'published_date', 'views', 'is_active']
    list_filter = ['category', 'is_active', 'published_at']
    search_fields = ['title', 'content']
    readonly_fields = ['views', 'created_at', 'image_preview']
    date_hierarchy = 'published_at'
    list_per_page = 20
    list_editable = ['is_active']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'category', 'published_at'),
            'description': 'Заголовок и категория статьи'
        }),
        ('Текст статьи', {
            'fields': ('excerpt', 'content'),
            'description': 'Краткое описание и полный текст'
        }),
        ('Изображение', {
            'fields': ('image', 'image_url', 'image_preview'),
            'description': 'Вы можете загрузить изображение с компьютера или указать ссылку'
        }),
        ('Дополнительно', {
            'fields': ('source', 'url', 'is_active', 'views', 'created_at'),
            'classes': ('collapse',),
            'description': 'Техническая информация'
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        if not obj:  # При создании новой статьи
            return (
                ('Основная информация', {
                    'fields': ('title', 'category', 'published_at'),
                }),
                ('Текст статьи', {
                    'fields': ('excerpt', 'content'),
                }),
                ('Изображение', {
                    'fields': ('image', 'image_url'),
                    'description': 'Вы можете загрузить изображение с компьютера или указать ссылку'
                }),
                ('Дополнительно', {
                    'fields': ('source', 'url', 'is_active'),
                    'classes': ('collapse',),
                }),
            )
        return super().get_fieldsets(request, obj)
    
    def title_preview(self, obj):
        return obj.title[:70] + '...' if len(obj.title) > 70 else obj.title
    title_preview.short_description = 'Заголовок'
    
    def published_date(self, obj):
        return obj.published_at.strftime('%d.%m.%Y %H:%M')
    published_date.short_description = 'Дата'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        elif obj.image_url:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 150px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />',
                obj.image_url
            )
        return "Нет изображения"
    image_preview.short_description = 'Превью'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Настройка полей
        form.base_fields['title'].widget.attrs.update({
            'style': 'width: 100%; padding: 10px; font-size: 16px;',
            'placeholder': 'Введите заголовок статьи'
        })
        form.base_fields['content'].widget.attrs.update({
            'rows': 20,
            'style': 'width: 100%; font-family: monospace;',
            'placeholder': 'Напишите текст статьи здесь...'
        })
        form.base_fields['excerpt'].widget.attrs.update({
            'rows': 3,
            'style': 'width: 100%;',
            'placeholder': 'Короткое описание для превью (до 500 символов)'
        })
        form.base_fields['source'].required = False
        form.base_fields['url'].required = False
        form.base_fields['source'].widget.attrs.update({
            'style': 'width: 100%;',
            'help_text': 'Можно оставить пустым для своих статей'
        })
        form.base_fields['url'].widget.attrs.update({
            'style': 'width: 100%;',
            'placeholder': 'https://... (необязательно)'
        })
        
        return form
    
    actions = ['mark_active', 'mark_inactive']
    
    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✅ {updated} статей опубликовано')
    mark_active.short_description = 'Опубликовать выбранные статьи'
    
    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'❌ {updated} статей снято с публикации')
    mark_inactive.short_description = 'Снять с публикации'


@admin.register(SavedArticle)
class SavedArticleAdmin(ModelAdmin):
    list_display = ['user', 'article_title', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'article__title']
    list_per_page = 20
    
    def article_title(self, obj):
        return obj.article.title[:60]
    article_title.short_description = 'Статья'


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ['user', 'article_title', 'text_preview', 'created_at', 'is_approved']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['user__username', 'text']
    list_editable = ['is_approved']
    list_per_page = 20
    
    def article_title(self, obj):
        return obj.article.title[:50]
    article_title.short_description = 'Статья'
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'
    
    actions = ['approve_comments', 'reject_comments']
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'✅ {updated} комментариев одобрено')
    approve_comments.short_description = 'Одобрить выбранные комментарии'
    
    def reject_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'❌ {updated} комментариев отклонено')
    reject_comments.short_description = 'Отклонить выбранные комментарии'