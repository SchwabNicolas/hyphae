from dal import autocomplete
from django.forms import ModelForm, BooleanField, CharField

from hyphaeTaxonomy.models import Name, HigherRankTaxon, SpecificTaxon, Illustration, Taxon


class HigherRankTaxonCreateForm(ModelForm):
    class Meta:
        model = HigherRankTaxon
        fields = '__all__'
        exclude = [
            'current_name',
            'basionym',
            'synonyms',
            'cover_illustration',
        ]
        widgets = {
            'parent': autocomplete.ModelSelect2(url='taxonomy:higher-taxon-autocomplete'),
            'data-minimum-input-length': 3,
        }


class SpecificTaxonCreateForm(ModelForm):
    rank = CharField(required=False)

    class Meta:
        model = SpecificTaxon
        fields = '__all__'
        exclude = [
            'current_name',
            'basionym',
            'synonyms',
            'cover_illustration',
        ]
        widgets = {
            'parent': autocomplete.ModelSelect2(url='taxonomy:higher-taxon-autocomplete'),
            'data-minimum-input-length': 3,
        }


class NameCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Name'})
        self.fields['authors'].widget.attrs.update({'placeholder': 'Authors'})
        self.fields['literature'].widget.attrs.update({'placeholder': 'Literature'})
        self.fields['volume'].widget.attrs.update({'placeholder': 'Volume'})
        self.fields['part'].widget.attrs.update({'placeholder': 'Part'})
        self.fields['page'].widget.attrs.update({'placeholder': 'Page'})
        self.fields['year_of_publication'].widget.attrs.update({'placeholder': 'Year of publication'})
        self.fields['year_on_publication'].widget.attrs.update({'placeholder': 'Year on publication'})
        self.fields['original_orthography'].widget.attrs.update({'placeholder': 'Original orthography'})
        self.fields['nomenclatural_comment'].widget.attrs.update({'placeholder': 'Nomenclatural comment'})
        self.fields['remarks'].widget.attrs.update({'placeholder': 'Remarks'})
        self.fields['icn_identifier'].widget.attrs.update({'placeholder': 'ICN identifier'})

    class Meta:
        model = Name
        fields = '__all__'


class BasionymCreateForm(NameCreateForm):
    is_current_name_basionym = BooleanField(label='Current name is basionym', required=False, initial=True)


class IllustrationCreateUpdateForm(ModelForm):
    class Meta:
        model = Illustration
        fields = '__all__'
        exclude = [
            'vanity',
        ]
        widgets = {
            'taxon': autocomplete.ModelSelect2(url='taxonomy:specific-taxon-autocomplete'),
            'data-minimum-input-length': 3,
        }


class TaxonUpdateForm(ModelForm):
    class Meta:
        model = Taxon
        fields = ['parent', 'rank']

        widgets = {
            'parent': autocomplete.ModelSelect2(url='taxonomy:higher-taxon-autocomplete'),
            'data-minimum-input-length': 3,
        }
