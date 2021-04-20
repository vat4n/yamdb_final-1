from api.filters import TitleFilter
from api.models import Category, Genre, Review, Title
from api.permissions import IsAdmin, IsAdminOrReadOnlyPermission, IsOwner
from api.permissions import IsOwnerOrAdminOrReadOnly
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleSerializerGet, TitleSerializerPost)

from api_yamdb.settings import EMAIL_ADMIN

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import JsonResponse

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related().all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = "username"

    @action(detail=False, methods=['get', 'patch'], url_path='me',
            permission_classes=[IsAdmin | IsOwner])
    def me(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            partial = kwargs.pop('partial', False)
            instance = self.request.user
            data = request.data.copy()
            data['username'] = self.request.user.username
            data['email'] = self.request.user.email
            serializer = self.get_serializer(instance, data=data,
                                             partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            instance = self.request.user
            serializer = self.get_serializer(instance)
            return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def EmailRegistration(request):
    email = request.POST.get('email', None)
    username = email.replace('@', '_').replace('.', '_')
    serializer = UserSerializer(data={'email': email, 'username': username})
    serializer.is_valid(raise_exception=True)
    serializer.save(is_active=False, confirmation_code='')
    confirmation_code = PasswordResetTokenGenerator().make_token(
        serializer.instance)
    send_mail(
        'Account activation',
        f'Please activate your account: '
        f'confirmation code is {confirmation_code}',
        EMAIL_ADMIN,
        [email, ],
        fail_silently=False, )
    return JsonResponse(
        {'Ok': f'User {email} created. Activation email sended.'},
        status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def EmailActivation(request):
    email = request.POST.get('email', None)
    user = User.objects.filter(email=email)
    if user.exists() and not user.first().is_active:
        user = user.first()
        confirmation_code = request.POST.get('confirmation_code', None)
        if PasswordResetTokenGenerator().check_token(user, confirmation_code):
            user.is_active = True
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            data = {'email': email, 'password': password}
            serializer = TokenObtainPairSerializer(data=data)
            try:
                serializer.is_valid(raise_exception=True)
            except TokenError as e:
                raise InvalidToken(e.args[0])
            return JsonResponse(serializer.validated_data, status=200)
    return JsonResponse({'Error': 'Not found'}, status=404)


class BaseViewSet(mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    permission_classes = (IsAdminOrReadOnlyPermission,)
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name', ]
    lookup_field = "slug"


class CategoryViewSet(BaseViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.select_related().annotate(
        rating=(Avg('review__score')))

    serializer_class = TitleSerializerPost
    permission_classes = [IsAdminOrReadOnlyPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        if self.request.method == 'GET':
            serializer_class = TitleSerializerGet
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrAdminOrReadOnly)

    def get_queryset(self):
        titles_pk = self.kwargs.get('title_pk', None)
        title = get_object_or_404(Title, pk=titles_pk)
        return title.review.all()

    def perform_create(self, serializer):
        titles_pk = self.kwargs.get('title_pk', None)
        title = get_object_or_404(Title, pk=titles_pk)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrAdminOrReadOnly)

    def get_queryset(self):
        titles_pk = self.kwargs.get('title_pk', None)
        reviews_pk = self.kwargs.get('review_pk', None)
        review = get_object_or_404(Review, pk=reviews_pk, title__id=titles_pk)
        return review.comment.all()

    def perform_create(self, serializer):
        titles_pk = self.kwargs.get('title_pk', None)
        reviews_pk = self.kwargs.get('review_pk', None)
        review = get_object_or_404(Review, pk=reviews_pk, title__id=titles_pk)
        serializer.save(author=self.request.user, review=review)
