from stocks.models import Stock
from django.contrib.auth.models import User
from rest_framework import serializers


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ["pk", "company_name", "price", "is_growing", "date_modified", "url"]


from stocks.models import Stock
from stocks.models import AuthUser
from rest_framework import serializers

class FullStockSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Stock
        fields = ["pk", "company_name", "price", "is_growing", "date_modified", "url", "user"]


class UserSerializer(serializers.ModelSerializer):
    stock_set = StockSerializer(many=True, read_only=True)

    class Meta:
        model = AuthUser
        fields = ["id", "first_name", "last_name", "stock_set"]