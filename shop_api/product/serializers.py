from django.db.models import Avg
from rest_framework import serializers
from .models import Category, Product, Review
from common.validators import validate_user_age


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']

    def validate_name(self, value):
        name = value.strip()
        if not name:
            raise serializers.ValidationError("Название категории не может быть пустым.")
        if Category.objects.filter(name__iexact=name).exists():
            raise serializers.ValidationError("Категория с таким названием уже существует.")
        return name


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category']

    def validate_title(self, value):
        title = value.strip()
        if not title:
            raise serializers.ValidationError("Название продукта не может быть пустым.")
        return title

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть больше 0.")
        return value

    def validate_category(self, value):
        if not Category.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Указанная категория не существует.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        validate_user_age(user) 
        title = attrs.get('title', '').strip()
        category = attrs.get('category')
        if category and Product.objects.filter(title__iexact=title, category=category).exists():
            raise serializers.ValidationError("В этой категории уже есть продукт с таким названием.")
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'text', 'stars', 'product']

    def validate_text(self, value):
        text = value.strip()
        if not text:
            raise serializers.ValidationError("Текст отзыва не может быть пустым.")
        return text

    def validate_stars(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5.")
        return value

    def validate(self, attrs):
        product = attrs.get('product')
        user = self.context['request'].user if self.context.get('request') else None

        if user and Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError("Вы уже оставили отзыв на этот продукт.")
        return attrs


class ProductReviewSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'reviews', 'rating']

    def get_rating(self, obj):
        avg = obj.reviews.aggregate(avg_stars=Avg('stars'))['avg_stars']
        return round(avg or 0, 2)
