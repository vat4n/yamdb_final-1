import datetime as dt

from api.validators import validate_score

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _


class UserRoles(models.TextChoices):
    ROLE_ADMIN = 'admin', _('Administrator')
    ROLE_MODER = 'moderator', _('Moderator')
    ROLE_USER = 'user', _('Regular user')


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    role = models.CharField(max_length=150, choices=UserRoles.choices,
                            default=UserRoles.ROLE_USER)
    bio = models.CharField(max_length=150, blank=True, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def is_admin(self):
        return self.is_superuser or self.role == UserRoles.ROLE_ADMIN

    @property
    def is_moder_or_admin(self):
        return (self.is_superuser or self.role == UserRoles.ROLE_ADMIN
                or self.role == UserRoles.ROLE_MODER)

    class Meta:
        ordering = ('email',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


class Category(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name='Категория',
                            help_text='Введите имя категории')

    slug = models.SlugField(unique=True,
                            verbose_name='Слуг категории',
                            help_text='Введите слуг для категории')

    class Meta:
        ordering = ['name', ]
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100,
                            verbose_name='Жанр',
                            help_text='Введите имя жанра')
    slug = models.SlugField(unique=True,
                            verbose_name='Слуг жанра',
                            help_text='Введите слуг для жанра')

    class Meta:
        ordering = ['name', ]
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=100, null=False, db_index=True,
                            verbose_name='Название произведения',
                            help_text='Введите название произведения')
    year = models.IntegerField(null=True,
                               validators=[MinValueValidator(1),
                                           MaxValueValidator(
                                               dt.datetime.now().year)],
                               verbose_name='Год произведения',
                               help_text='Введите год выпуска произведения')
    description = models.TextField(blank=True, default='',
                                   verbose_name='Описание произведения',
                                   help_text='Введите описание произведения')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 related_name='title_in_category', null=True,
                                 default=None,
                                 verbose_name='Категория произведения',
                                 help_text='Выберете категорию произведения')
    genre = models.ManyToManyField(Genre, default=None,
                                   verbose_name='Список жанров произведения',
                                   help_text='Выберете подходящие жанры')

    class Meta:
        ordering = ['name', ]
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='review',
                              verbose_name='Произведение',
                              help_text='Выберете произведение для отзыва')
    text = models.TextField(
        verbose_name='Отзыв на произведение',
        help_text='Напишите отзыв на произведение')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='review',
                               verbose_name='Автор отзыва',
                               help_text='Выберете автора отзыва')

    score = models.IntegerField(
        validators=[validate_score, ],
        verbose_name='Оценка произведения',
        help_text='Поставьте оценку произведению от 1 до 10.')

    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        constraints = [UniqueConstraint(fields=['title', 'author'],
                                        name='unique_review'), ]

    def __str__(self):
        return self.title.name + ' - ' + self.author.email


class Comment(models.Model):
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comment',
                               verbose_name='Отзыв',
                               help_text='Выберете отзыв для комментария')
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Комментарий для отзыва')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comment',
                               verbose_name='Автор комментария',
                               help_text='Выберете автора комментария')
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ['-pub_date', ]
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return (f'Комментарий {self.author.email} на обзор от '
                f'{self.review.author.email}')
