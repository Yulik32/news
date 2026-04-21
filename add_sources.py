import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_aggregator.settings')
django.setup()

from apps.news.models import Source, Category

# Создаём категории
categories = {
    'Политика': 'politics',
    'Экономика': 'economy',
    'Технологии': 'tech',
    'Наука': 'science',
    'Спорт': 'sport',
}

for cat_name, cat_slug in categories.items():
    cat, created = Category.objects.get_or_create(
        name=cat_name,
        defaults={'slug': cat_slug}
    )
    if created:
        print(f"✅ Создана категория: {cat_name}")

# RSS-источники
rss_sources = [
    {
        'name': 'Лента.ру',
        'url': 'https://lenta.ru/rss',
        'category': 'Политика',
    },
    {
        'name': 'РИА Новости',
        'url': 'https://ria.ru/export/rss2/index.xml',
        'category': 'Политика',
    },
    {
        'name': 'Хабр',
        'url': 'https://habr.com/ru/rss/all/',
        'category': 'Технологии',
    },
    {
        'name': 'Коммерсантъ',
        'url': 'https://www.kommersant.ru/RSS/main.xml',
        'category': 'Экономика',
    },
    {
        'name': 'Наука и жизнь',
        'url': 'https://www.nkj.ru/rss/',
        'category': 'Наука',
    },
]

# Добавляем источники
for src_data in rss_sources:
    category = Category.objects.get(name=src_data['category'])
    source, created = Source.objects.get_or_create(
        url=src_data['url'],
        defaults={
            'name': src_data['name'],
            'source_type': 'rss',
            'category': category,
            'is_active': True,
        }
    )
    if created:
        print(f"✅ Добавлен источник: {src_data['name']}")
    else:
        print(f"ℹ Источник уже существует: {src_data['name']}")

print("\n🎉 Готово! Запусти парсинг: python manage.py parse_rss --all")