from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from hyphaeTaxonomy.models import Taxon, Name


class NameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Name
        fields = '__all__'


class TaxonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxon
        fields = '__all__'


class TreeDataTaxonSerializer(serializers.ModelSerializer):
    current_name = SerializerMethodField()
    authors = SerializerMethodField()
    year_of_publication = SerializerMethodField()
    parent = SerializerMethodField()
    has_children = SerializerMethodField()

    class Meta:
        model = Taxon
        fields = ['slug', 'current_name', 'authors', 'year_of_publication', 'rank', 'parent', 'has_children']

    def get_current_name(self, obj):
        return obj.current_name.name

    def get_authors(self, obj):
        return obj.current_name.authors

    def get_year_of_publication(self, obj):
        return obj.current_name.year_of_publication

    def get_parent(self, obj):
        if obj.parent is not None:
            return obj.parent.slug
        return ''

    def get_has_children(self, obj):
        return obj.has_children()
