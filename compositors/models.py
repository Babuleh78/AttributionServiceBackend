from django.db import models
from django.forms import model_to_dict
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import decimal


class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
class Composer(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Имя")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    portrait_url = models.URLField(blank=True, null=True, verbose_name="URL портрета",)
    biography = models.TextField(verbose_name="Биография", blank=True, null=True)


    analyzed_works = models.IntegerField(default=0, verbose_name="Проанализировано произведений")
    total_intervals = models.IntegerField(default=0, verbose_name="Всего интервалов")
    period = models.CharField(max_length=100, blank=True, verbose_name="Период творчества")
    polyphony_type = models.CharField(max_length=100, blank=True, verbose_name="Тип полифонии")

    unisons_seconds_freq = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Частота: Унисоны и секунды (%)")
    unisons_seconds_stddev = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,verbose_name="СКО: Унисоны и секунды")

    thirds_freq = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,verbose_name="Частота: Терции (%)")
    thirds_stddev = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,verbose_name="СКО: Терции")

    fourths_fifths_freq = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,verbose_name="Частота: Кварты и квинты (%)") 
    fourths_fifths_stddev = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,verbose_name="СКО: Кварты и квинты")
    
    sixths_sevenths_freq = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,verbose_name="Частота: Сексты и септимы (%)")
    sixths_sevenths_stddev = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,verbose_name="СКО: Сексты и септимы")

    octaves_freq = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,verbose_name="Частота: Октавы (%)")
    octaves_stddev = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,verbose_name="СКО: Октавы")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Композитор"
        verbose_name_plural = "Композиторы"
        db_table = "composers"
        ordering = ("pk",)


class Analysis(models.Model):
    STATUS_CHOICES = (
        (1, 'Черновик'),
        (2, 'Сформирован'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", default=timezone.now)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)
    musicologist_name = models.CharField(_('musicologist_name'), max_length=150, null=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_analyses',
         null=True,  
         blank=True  
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_analyses'
    )

    composers_list = models.JSONField(
        default=list,
        verbose_name="Список композиторов",
    )


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if 'composers_list' not in (kwargs.get('update_fields') or []):
            new_composers_list = self.get_composers()
            if self.composers_list != new_composers_list:
                self.composers_list = new_composers_list
                super().save(update_fields=['composers_list'])

    def get_composers(self):
        composers = []
        for item in ComposerAnalysis.objects.filter(analysis=self):
            composer_dict = model_to_dict(item.composer)
            composer_data = convert_decimals(composer_dict)
            composers.append(composer_data)
        return composers

    class Meta:
        verbose_name = "Анализ"
        verbose_name_plural = "Анализы"
        db_table = "analysiss"
        ordering = ('-date_formation',)



class ComposerAnalysis(models.Model):
    composer = models.ForeignKey(Composer, on_delete=models.DO_NOTHING, verbose_name="Композитор")
    analysis = models.ForeignKey(Analysis, on_delete=models.DO_NOTHING, verbose_name="Анализ")

    anon_unisons_seconds_freq = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Аноним: Унисоны и секунды (%)")
    anon_thirds_freq = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Аноним: Терции (%)")
    anon_fourths_fifths_freq = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Аноним: Кварты и квинты (%)")
    anon_sixths_sevenths_freq = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Аноним: Сексты и септимы (%)")
    anon_octaves_freq = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Аноним: Октавы (%)")
    
    potential_coincidence = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Вероятное совпадение")

    def __str__(self):
        return f"м-м №{self.id} (композитор {self.composer_id}, анализ {self.analysis_id})"

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "composer_analysis"
        ordering = ('id',)
        unique_together = ('composer', 'analysis')


def convert_decimals(obj):
    """Рекурсивно преобразует Decimal в float для JSON-сериализации."""
    if isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    else:
        return obj