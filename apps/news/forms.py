from django import forms
from .models import Article, Comment
from .constants import BAD_WORDS, CENSORED_WORD

class ArticleSearchForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Поиск по заголовкам и тексту...',
        'class': 'search-input'
    }))
    category = forms.ChoiceField(required=False, choices=[])
    source = forms.ChoiceField(required=False, choices=[])
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category, Source
        self.fields['category'].choices = [('', 'Все категории')] + [
            (c.id, c.name) for c in Category.objects.all()
        ]
        self.fields['source'].choices = [('', 'Все источники')] + [
            (s.id, s.name) for s in Source.objects.filter(is_active=True)
        ]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишите ваш комментарий...',
                'maxlength': 1000
            })
        }
        labels = {
            'text': ''
        }
    
    def clean_text(self):
        """Фильтрация нежелательных слов"""
        from .constants import BAD_WORDS, CENSORED_WORD
        
        text = self.cleaned_data.get('text', '')
        
        # Проверяем на пустоту
        if not text or len(text.strip()) == 0:
            raise forms.ValidationError('Комментарий не может быть пустым')
        
        # Проверяем длину
        if len(text) < 3:
            raise forms.ValidationError('Комментарий слишком короткий (минимум 3 символа)')
        
        if len(text) > 1000:
            raise forms.ValidationError('Комментарий слишком длинный (максимум 1000 символов)')
        
        # Фильтрация нежелательных слов
        original_text = text
        lower_text = text.lower()
        
        for bad_word in BAD_WORDS:
            if bad_word.lower() in lower_text:
                # Заменяем слово на ***
                import re
                pattern = re.compile(re.escape(bad_word), re.IGNORECASE)
                text = pattern.sub(CENSORED_WORD, text)
        
        # Если были замены, добавляем предупреждение
        if text != original_text:
            self.add_warning('Комментарий содержит нежелательные выражения, они были заменены на ***')
        
        return text.strip()
    
    def add_warning(self, message):
        """Добавляем предупреждение в форму"""
        if not hasattr(self, 'warnings'):
            self.warnings = []
        self.warnings.append(message)