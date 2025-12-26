import uuid

from django.db import models

from .company import Company


class Category(models.Model):
    """
    カテゴリモデル

    企業ごとのカテゴリ情報を管理するモデル。
    階層構造をサポートし、親カテゴリを持つことができます。

    制約:
        - 同一企業内で同じカテゴリ名は重複不可
        - 親カテゴリは同じ企業に属する必要がある（シリアライザでバリデーション）
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, related_name="+", on_delete=models.CASCADE, db_comment="企業ID")
    name = models.CharField(max_length=255, db_comment="カテゴリ名")
    parent_category = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.SET_NULL,
        db_comment="親カテゴリID",
    )
    created_at = models.DateTimeField(auto_now_add=True, editable=False, db_comment="作成日時")
    updated_at = models.DateTimeField(auto_now=True, editable=False, db_comment="更新日時")

    class Meta:
        db_table = "categories"
        db_table_comment = "カテゴリテーブル"
        verbose_name = "category"
        verbose_name_plural = "categories"
        # 同一企業内でカテゴリ名の重複を防ぐ制約
        constraints = [models.UniqueConstraint(fields=["company", "name"], name="unique_company_category_combination")]
        # 企業とカテゴリ名での検索を高速化するインデックス
        indexes = [models.Index(fields=["company", "name"])]

    def __str__(self) -> str:
        """カテゴリの文字列表現を返す"""
        return f"{self.name} ({self.company.name})"
