from rest_framework import generics
from django.db.models import Count
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductReviewSerializer,
    ReviewSerializer,
    ProductSerializer,
)


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.annotate(products_count=Count("products"))
    serializer_class = CategorySerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.annotate(products_count=Count("products"))
    serializer_class = CategorySerializer
    lookup_field = "id"


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.prefetch_related("reviews").all()
    serializer_class = ProductSerializer
    lookup_field = "id"


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.select_related("product").all()
    serializer_class = ReviewSerializer


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    lookup_field = "id"


class ProductsWithReviewsListView(generics.ListAPIView):
    queryset = Product.objects.prefetch_related("reviews").all()
    serializer_class = ProductReviewSerializer
