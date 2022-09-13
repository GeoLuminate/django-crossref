from rest_framework import viewsets
from crossref.serialize import PublicationSerializer

class PublicationModelViewSet(viewsets.ModelViewSet):
    """API endpoint to request a set of publications from the World Heat Flow Database."""
    serializer_class = PublicationSerializer

    def get_queryset(self):
        return super().get_queryset().prefetch_related('author')
