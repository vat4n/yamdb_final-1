from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet)

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import EmailActivation, EmailRegistration, UserViewSet

router = DefaultRouter()
router.register(r'titles/(?P<title_pk>\d+)/reviews', ReviewViewSet,
                basename='review')
router.register(
    r'titles/(?P<title_pk>\d+)/reviews/(?P<review_pk>\d+)/comments',
    CommentViewSet,
    basename='comment')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'titles', TitleViewSet, basename='title')
router.register(r'genres', GenreViewSet, basename='genre')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/auth/email/', EmailRegistration,
         name='email_reg'),
    path('v1/auth/token/', EmailActivation,
         name='email_act'),
    path('v1/', include(router.urls)),
]
