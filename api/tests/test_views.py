import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Category, Company


class CategoryViewTests(APITestCase):
    def setUp(self) -> None:
        """テストデータのセットアップ"""
        # テスト用の企業を作成
        self.company1 = Company.objects.create(name="テスト企業1")
        self.company2 = Company.objects.create(name="テスト企業2")

        # テスト用のカテゴリを作成
        self.category1 = Category.objects.create(company=self.company1, name="カテゴリ1")
        self.category2 = Category.objects.create(
            company=self.company1, name="カテゴリ2", parent_category=self.category1
        )
        self.category3 = Category.objects.create(company=self.company2, name="カテゴリ3")

    # ============================================================
    # 正常系テスト
    # ============================================================

    # --- 基本CRUD ---

    def test_list(self) -> None:
        """カテゴリ一覧取得のテスト"""
        print("カテゴリ取得のテスト（LIST）")
        url = "/api/categories/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_retrieve(self) -> None:
        """カテゴリ詳細取得のテスト"""
        print("カテゴリ取得のテスト（GET）")
        url = f"/api/categories/{self.category1.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "カテゴリ1")
        self.assertEqual(str(response.data["company"]), str(self.company1.id))
        self.assertIsNone(response.data["parent_category"])

    def test_create(self) -> None:
        """カテゴリ作成のテスト"""
        print("カテゴリ作成のテスト（POST）")
        url = "/api/categories/"
        data = {"company": str(self.company1.id), "name": "新規カテゴリ"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "新規カテゴリ")
        self.assertEqual(Category.objects.count(), 4)

    def test_update(self) -> None:
        """カテゴリ更新のテスト（PUT）"""
        print("カテゴリ更新のテスト（PUT）")

        url = f"/api/categories/{self.category1.id}/"
        data = {
            "company": str(self.company1.id),
            "name": "更新されたカテゴリ1",
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "更新されたカテゴリ1")

        # DBから再取得して確認
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.name, "更新されたカテゴリ1")

    def test_partial_update(self) -> None:
        """カテゴリ部分更新のテスト（PATCH）"""
        print("カテゴリ更新のテスト（PATCH）")
        url = f"/api/categories/{self.category1.id}/"
        data = {"name": "部分更新されたカテゴリ"}
        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "部分更新されたカテゴリ")

    def test_destroy(self) -> None:
        """カテゴリ削除のテスト"""
        print("カテゴリ削除のテスト")
        url = f"/api/categories/{self.category1.id}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 2)
        self.assertFalse(Category.objects.filter(id=self.category1.id).exists())

    # --- 階層構造 ---

    def test_create_with_parent(self) -> None:
        """親カテゴリを指定したカテゴリ作成のテスト"""
        print("親カテゴリ指定のカテゴリ作成のテスト")
        url = "/api/categories/"
        data = {
            "company": str(self.company1.id),
            "name": "子カテゴリ",
            "parent_category": str(self.category1.id),
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "子カテゴリ")
        self.assertEqual(str(response.data["parent_category"]), str(self.category1.id))

    def test_retrieve_with_parent(self) -> None:
        """親カテゴリを持つカテゴリの詳細取得のテスト"""
        print("親カテゴリを持つカテゴリ取得のテスト")
        url = f"/api/categories/{self.category2.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "カテゴリ2")
        self.assertEqual(str(response.data["parent_category"]), str(self.category1.id))

    def test_update_parent_category(self) -> None:
        """親カテゴリを更新するテスト"""
        print("親カテゴリ更新のテスト")
        url = f"/api/categories/{self.category1.id}/"
        data = {
            "company": str(self.company1.id),
            "name": "カテゴリ1",
            "parent_category": str(self.category2.id),
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data["parent_category"]), str(self.category2.id))

    # --- 特殊ケース ---

    def test_create_duplicate_name_different_company(self) -> None:
        """異なる企業で同じ名前のカテゴリ作成のテスト（成功）"""
        print("異なる企業での同名カテゴリ作成のテスト（正常系）")
        url = "/api/categories/"
        data = {"company": str(self.company2.id), "name": "カテゴリ1"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "カテゴリ1")

    # ============================================================
    # 異常系テスト
    # ============================================================

    # --- 作成時のバリデーション ---

    def test_create_duplicate_name_same_company(self) -> None:
        """カテゴリ名重複のバリデーションテスト（異常系）"""
        print("作成時のカテゴリ名重複バリデーションテスト（異常系）")
        url = "/api/categories/"
        data = {"company": str(self.company1.id), "name": "カテゴリ1"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_with_parent_from_different_company(self) -> None:
        """親カテゴリの企業整合性バリデーションテスト（異常系）"""
        print("作成時の親カテゴリ企業整合性バリデーションテスト（異常系）")
        url = "/api/categories/"
        data = {
            "company": str(self.company2.id),
            "name": "不正な子カテゴリ",
            "parent_category": str(self.category1.id),
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- 更新時のバリデーション ---

    def test_update_duplicate_name_validation(self) -> None:
        """更新時のカテゴリ名重複バリデーションテスト（異常系）"""
        print("更新時のカテゴリ名重複バリデーションテスト（異常系）")
        url = f"/api/categories/{self.category1.id}/"
        data = {
            "company": str(self.company1.id),
            "name": "カテゴリ2",  # 既存のカテゴリ2と重複
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_parent_different_company_validation(self) -> None:
        """更新時の親カテゴリ企業整合性バリデーションテスト（異常系）"""
        print("更新時の親カテゴリ企業整合性バリデーションテスト（異常系）")
        url = f"/api/categories/{self.category1.id}/"
        data = {
            "company": str(self.company1.id),
            "name": "カテゴリ1",
            "parent_category": str(self.category3.id),  # 異なる企業のカテゴリを親に設定
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    def test_update_self_reference_validation(self) -> None:
        """更新時の自己参照バリデーションテスト（異常系）"""
        print("更新時の自己参照バリデーションテスト（異常系）")
        url = f"/api/categories/{self.category1.id}/"
        data = {
            "company": str(self.company1.id),
            "name": "カテゴリ1",
            "parent_category": str(self.category1.id),  # 自分自身を親に設定
        }
        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_category", response.data)

    # --- 存在チェック ---

    def test_retrieve_nonexistent(self) -> None:
        """存在しないカテゴリの取得のテスト（異常系）"""
        print("存在しないカテゴリの取得のテスト（異常系）")
        url = f"/api/categories/{uuid.uuid4()}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_nonexistent(self) -> None:
        """存在しないカテゴリの削除のテスト（異常系）"""
        print("存在しないカテゴリの削除のテスト（異常系）")
        url = f"/api/categories/{uuid.uuid4()}/"
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
