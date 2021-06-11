from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView

from hyphaeTaxonomy.forms import TaxonCreateForm, NameCreateForm
from hyphaeTaxonomy.models import Taxon, Name


class IndexView(TemplateView):
    template_name = 'hyphae/index.html'


class TaxaListView(ListView):
    template_name = 'hyphaeTaxonomy/taxa/taxa_list.html'
    context_object_name = 'taxa'
    model = Taxon


class TaxonDetailView(DetailView):
    template_name = 'hyphaeTaxonomy/taxa/taxon_detail.html'
    context_object_name = 'taxon'
    model = Taxon


class TaxonCreateView(CreateView):
    template_name = 'hyphaeTaxonomy/taxa/taxon_create.html'
    form_class = TaxonCreateForm


class NamesListView(ListView):
    template_name = 'hyphaeTaxonomy/taxa/taxa_list.html'
    context_object_name = 'names_list'
    model = Name

    def get_queryset(self):
        return self.model.objects.all()


class NameCreateView(FormView):
    template_name = 'hyphaeTaxonomy/names/name_create.html'
    success_url = reverse_lazy('taxonomy:name-list')
    form_class = NameCreateForm
