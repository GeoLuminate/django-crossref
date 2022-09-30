from rest_framework import serializers
from crossref import models
from .models import Work, Author

class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Author
        exclude = ['id']

class WorkSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True, many=True)

    class Meta:
        model = Work
        exclude = ['last_queried_crossref','source']