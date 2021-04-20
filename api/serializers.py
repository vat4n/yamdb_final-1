from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.relations import SlugRelatedField

from .models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role')
        model = User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class TitleSerializerGet(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        fields = '__all__'
        model = Title


class TitleSerializerPost(serializers.ModelSerializer):
    genre = SlugRelatedField(slug_field='slug',
                             queryset=Genre.objects.all(), many=True)
    category = SlugRelatedField(slug_field='slug',
                                queryset=Category.objects.all(),
                                default=None)

    class Meta:
        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username',
                                          default=CurrentUserDefault())

    class Meta:
        model = Review
        read_only_fields = ('id', 'title', 'pub_date')
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, attrs):
        try:
            author = self.context['request'].user
            title = self.context['view'].kwargs['title_pk']
            method = self.context['request'].method
        except (AttributeError, KeyError):
            author = None
            title = None
            method = None
        if method != 'POST':
            return attrs
        if Review.objects.filter(author=author, title=title).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение')
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(read_only=True,
                                          slug_field='id')
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username',
                                          default=CurrentUserDefault())

    class Meta:
        fields = '__all__'
        model = Comment
