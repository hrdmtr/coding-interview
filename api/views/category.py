from django.db.models import QuerySet
from rest_framework import viewsets

from api.models import Category
from api.serializers.category import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet[Category]):
    """
    CategoryモデルのCRUD操作を提供するViewSet

    提供するエンドポイント:
    - GET /api/categories/ - カテゴリ一覧取得
    - POST /api/categories/ - カテゴリ作成
    - GET /api/categories/{id}/ - カテゴリ詳細取得
    - PUT /api/categories/{id}/ - カテゴリ更新
    - PATCH /api/categories/{id}/ - カテゴリ部分更新
    - DELETE /api/categories/{id}/ - カテゴリ削除
    """

    queryset: QuerySet[Category] = Category.objects.all()
    serializer_class = CategorySerializer
