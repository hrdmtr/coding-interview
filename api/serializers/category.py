from typing import Any

from rest_framework import serializers

from api.models import Category, Company


class CategorySerializer(serializers.ModelSerializer[Category]):
    """
    カテゴリモデルのシリアライザ

    カテゴリの作成・更新・取得時に使用され、以下のバリデーションを実行します：
    - 親カテゴリの自己参照禁止
    - 親カテゴリと同じ企業に属することの確認
    """

    class Meta:
        model = Category
        fields = ["id", "company", "name", "parent_category", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        カテゴリのバリデーション

        Args:
            attrs: バリデーション対象の属性辞書

        Returns:
            バリデーション済みの属性辞書

        Raises:
            serializers.ValidationError: バリデーションエラー時
                - 親カテゴリが自分自身を参照している場合
                - 親カテゴリが異なる企業に属している場合
        """
        # 親カテゴリが自分自身を参照していないかチェック
        # 更新時(self.instance が存在)のみチェック
        parent_category = attrs.get("parent_category")
        if self.instance and parent_category == self.instance:
            raise serializers.ValidationError({"parent_category": "カテゴリは自分自身を親カテゴリに設定できません。"})

        # 親カテゴリが同じ企業に属しているかチェック
        # 新規作成時は attrs から、更新時は instance から企業情報を取得
        company: Company | None = attrs.get("company") or (self.instance.company if self.instance else None)
        if parent_category and company and parent_category.company != company:
            raise serializers.ValidationError({"parent_category": "親カテゴリは同じ企業に属している必要があります。"})

        return attrs
