from rest_framework import serializers
from crossref import models
from .utils import get_publication_model, get_author_model

class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_author_model()
        exclude = ['id']

class PublicationSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True, many=True)

    class Meta:
        model = get_publication_model()
        exclude = ['crossref_last_queried','doi_queried','source']