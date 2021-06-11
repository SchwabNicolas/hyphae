from django.forms import ModelForm

from hyphaeTaxonomy.models import Taxon, Illustration


class TaxonAddForm(ModelForm):
    class Meta:
        model = Taxon
        fields = "__all__"


class IllustrationAddForm(ModelForm):
    class Meta:
        model = Illustration
        fields = "__all__"
