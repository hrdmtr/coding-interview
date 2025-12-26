"""
APIルーティング設定

Django REST Framework の Router を使用して、カテゴリAPIのエンドポイントを自動生成します。
ベースURL: /api/
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.category import CategoryViewSet

# DefaultRouter によって以下のエンドポイントが自動生成されます:
# - GET    /api/categories/      - 一覧取得
# - POST   /api/categories/      - 作成
# - GET    /api/categories/{id}/ - 詳細取得
# - PUT    /api/categories/{id}/ - 更新
# - PATCH  /api/categories/{id}/ - 部分更新
# - DELETE /api/categories/{id}/ - 削除
router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [path("", include(router.urls))]
