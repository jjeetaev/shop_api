from rest_framework import generics
from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductReviewSerializer,
    ReviewSerializer,
    ProductSerializer,
)
from users.permissions import IsModerator
from common.validators import validate_user_age  


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.annotate(products_count=Count("products"))
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.annotate(products_count=Count("products"))
    serializer_class = CategorySerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated]


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            if self.request.user.is_staff:
                return [IsModerator()]  
            return [IsAuthenticated()]  
        return [IsAuthenticated() | IsModerator()]

    def perform_create(self, serializer):
        validate_user_age(self.request.user)
        serializer.save()


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.prefetch_related("reviews").all()
    serializer_class = ProductSerializer
    lookup_field = "id"
    permission_classes = [IsModerator]


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.select_related("product").all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    lookup_field = "id"
    permission_classes = [IsAuthenticated]


class ProductsWithReviewsListView(generics.ListAPIView):
    queryset = Product.objects.prefetch_related("reviews").all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]
