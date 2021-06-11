from django.forms import ModelForm

from hyphaeTaxonomy.models import Taxon, Name


class TaxonCreateForm(ModelForm):
    class Meta:
        model = Taxon
        fields = '__all__'


class NameCreateForm(ModelForm):
    class Meta:
        model = Name
        fields = '__all__'
