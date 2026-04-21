import feedparser
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.news.models import Source, Article, Category
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import urllib.request
import urllib.parse
import ssl

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Парсинг RSS-лент источников для наполнения сайта новостями'
    
    def add_arguments(self, parser):
        parser.add_argument('--source', type=int, help='ID конкретного источника для парсинга')
        parser.add_argument('--all', action='store_true', help='Парсить все активные источники')
        parser.add_argument('--proxy', type=str, help='Прокси-сервер (например: http://user:pass@host:port)')
    
    def setup_proxy_for_feedparser(self, proxy_url):
        """Настройка прокси для feedparser"""
        if proxy_url:
            # Сохраняем оригинальный urlopen
            import feedparser.api
            import urllib.request
            
            # Создаем обработчик прокси
            proxy_handler = urllib.request.ProxyHandler({
                'http': proxy_url,
                'https': proxy_url
            })
            opener = urllib.request.build_opener(proxy_handler)
            
            # Подменяем urlopen в feedparser
            feedparser.api._open_resource = opener.open
            
            self.stdout.write(f"[ПРОКСИ] Прокси настроен для feedparser: {proxy_url}")
            return True
        return False
    
    def fetch_rss_with_proxy(self, url, proxy_url):
        """Загрузка RSS через прокси с помощью urllib"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        try:
            if proxy_url:
                # Настраиваем прокси для этого запроса
                proxy_handler = urllib.request.ProxyHandler({
                    'http': proxy_url,
                    'https': proxy_url
                })
                opener = urllib.request.build_opener(proxy_handler)
                response = opener.open(req, timeout=30)
                return response.read()
            else:
                # Отключаем проверку SSL если нужно
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                response = urllib.request.urlopen(req, timeout=30, context=ssl_context)
                return response.read()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ОШИБКА] Не удалось загрузить RSS: {e}"))
            return None
    
    def handle(self, *args, **options):
        proxy_url = options.get('proxy')
        
        # Получаем источники для парсинга
        if options.get('source'):
            sources = Source.objects.filter(pk=options['source'], is_active=True)
        else:
            sources = Source.objects.filter(is_active=True, source_type='rss')
        
        if not sources.exists():
            self.stdout.write(self.style.WARNING("[ВНИМАНИЕ] Нет активных RSS-источников для парсинга"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"[ИНФО] Найдено источников для парсинга: {sources.count()}"))
        
        total_new = 0
        for source in sources:
            self.stdout.write(f"\n[ПАРСИНГ] {source.name} ({source.url})...")
            
            try:
                # ВАРИАНТ 1: Используем feedparser с прокси через urllib
                if proxy_url:
                    # Загружаем RSS через urllib с прокси
                    rss_data = self.fetch_rss_with_proxy(source.url, proxy_url)
                    if not rss_data:
                        continue
                    
                    # Парсим полученные данные
                    feed = feedparser.parse(rss_data)
                else:
                    # Без прокси
                    feed = feedparser.parse(source.url)
                
                new_count = 0
                
                # Проверяем ошибки парсинга
                if feed.bozo:
                    self.stdout.write(self.style.WARNING(
                        f"[ПРЕДУПРЕЖДЕНИЕ] {source.name}: {feed.bozo_exception}"
                    ))
                
                # Проверяем, есть ли записи
                if not feed.entries:
                    self.stdout.write(self.style.WARNING(f"[ВНИМАНИЕ] {source.name}: Нет записей в RSS"))
                    continue
                
                self.stdout.write(f"[ИНФО] {source.name}: Найдено записей в RSS: {len(feed.entries)}")
                
                for entry in feed.entries[:30]:
                    # Проверяем, есть ли уже такая статья
                    if Article.objects.filter(url=entry.link).exists():
                        continue
                    
                    # Извлекаем описание
                    description = entry.get('description', '')
                    if description:
                        soup = BeautifulSoup(description, 'html.parser')
                        description = soup.get_text()[:500]
                    
                    # Извлекаем контент
                    content = ''
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].value
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    else:
                        content = description
                    
                    if content:
                        soup = BeautifulSoup(content, 'html.parser')
                        content = soup.get_text()
                    
                    # Извлекаем изображение
                    image_url = ''
                    if hasattr(entry, 'media_content') and entry.media_content:
                        image_url = entry.media_content[0].get('url', '')
                    elif hasattr(entry, 'links'):
                        for link in entry.links:
                            if link.get('type', '').startswith('image'):
                                image_url = link.href
                                break
                    
                    # Определяем категорию
                    category = source.category
                    if hasattr(entry, 'tags') and entry.tags:
                        for tag in entry.tags[:1]:
                            tag_term = tag.term[:100]
                            
                            # Создаем уникальный slug
                            base_slug = tag_term.lower().replace(' ', '-').replace('/', '-')[:50]
                            slug = base_slug
                            counter = 1
                            
                            while Category.objects.filter(slug=slug).exists():
                                slug = f"{base_slug}-{counter}"
                                counter += 1
                            
                            cat, created = Category.objects.get_or_create(
                                name=tag_term,
                                defaults={'slug': slug}
                            )
                            category = cat
                            break
                    
                    # Дата публикации
                    published = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published = datetime(*entry.updated_parsed[:6])
                    else:
                        published = timezone.now()
                    
                    if timezone.is_naive(published):
                        published = timezone.make_aware(published)
                    
                    # Создаём статью
                    Article.objects.create(
                        title=entry.title[:500],
                        content=content[:10000] if content else '',
                        excerpt=description[:500] if description else '',
                        source=source,
                        category=category,
                        url=entry.link,
                        image_url=image_url,
                        published_at=published,
                    )
                    new_count += 1
                    self.stdout.write(f"  [+] Добавлена статья: {entry.title[:50]}...")
                
                # Обновляем время последнего парсинга
                source.last_parsed = timezone.now()
                source.parse_error = ''
                source.save()
                
                total_new += new_count
                self.stdout.write(self.style.SUCCESS(
                    f"[ГОТОВО] Добавлено {new_count} новых статей из {source.name}"
                ))
                
            except Exception as e:
                source.parse_error = str(e)
                source.save()
                self.stdout.write(self.style.ERROR(
                    f"[ОШИБКА] При парсинге {source.name}: {e}"
                ))
                logger.error(f"Error parsing {source.name}: {e}", exc_info=True)
        
        self.stdout.write(self.style.SUCCESS(f"\n[ИТОГО] Всего добавлено новых статей: {total_new}"))