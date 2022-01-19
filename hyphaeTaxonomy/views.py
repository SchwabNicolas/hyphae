from dal import autocomplete
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, TemplateView, FormView, UpdateView
from rest_framework.generics import ListAPIView

from hyphaeTaxonomy.forms import HigherRankTaxonCreateForm, NameCreateForm, BasionymCreateForm, SpecificTaxonCreateForm, IllustrationCreateUpdateForm, TaxonUpdateForm
from hyphaeTaxonomy.models import Taxon, Name, HigherRankTaxon, Illustration, SpecificTaxon
from hyphaeTaxonomy.serializers import TreeDataTaxonSerializer


class IndexView(TemplateView):
    template_name = 'hyphae/index.html'


class TaxaListView(ListView):
    template_name = 'hyphaeTaxonomy/taxa/taxa_list.html'
    context_object_name = 'taxa'
    model = Taxon

    def get_queryset(self):
        # illustrations = Illustration.objects.all()
        # for illustration in illustrations:
        #     illustration.save()
        #
        # taxa = Taxon.objects.all()
        # for taxon in taxa:
        #     illustration = Illustration.objects.filter(taxon=taxon).first()
        #     taxon.cover_illustration = illustration
        #     taxon.save()

        return HigherRankTaxon.objects.filter(rank=HigherRankTaxon.KINGDOM)


class TaxonDetailView(DetailView):
    template_name = 'hyphaeTaxonomy/taxa/taxon_detail.html'
    model = Taxon
    context_object_name = 'taxon'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['children_taxa'] = Taxon.objects.filter(parent__slug=self.get_object().slug).order_by('current_name__name')
        context['illustrations'] = Illustration.objects.filter(taxon_id=self.get_object().id)
        context['parent_taxa'] = Taxon.objects.filter(parent__slug=self.get_object().slug)
        layout = 'grid'
        if self.kwargs.get('layout'):
            layout = self.kwargs.get('layout')
        context['layout'] = layout
        return context


class TaxonUpdateView(UpdateView):
    template_name = "hyphaeTaxonomy/taxa/taxon_update.html"
    model = Taxon
    context_object_name = 'taxon'
    form_class = TaxonUpdateForm
    success_url = reverse_lazy("taxonomy:index")

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if 'deleteTaxon' in self.request.POST:
                parent = self.get_object().parent
                self.get_object().delete()
                messages.success(message='Successfully deleted publication!', request=self.request)
                return redirect(reverse_lazy('taxonomy:taxon-detail', kwargs={'slug': parent.slug}))
            else:
                super().post(request, *args, **kwargs)
                return redirect(reverse_lazy('taxonomy:taxon-detail', kwargs={'slug': self.object.slug}))


class SpecificTaxonCreateView(CreateView):
    template_name = 'hyphaeTaxonomy/taxa/species_create.html'
    form_class = SpecificTaxonCreateForm
    success_url = reverse_lazy('taxonomy:index')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            basionym_form = BasionymCreateForm(request.POST, prefix="bn")
            cn_form = NameCreateForm(request.POST, prefix="cn")

            all_forms_valid = True
            if not self.get_form().is_valid():
                all_forms_valid = False
            if not cn_form.is_valid():
                all_forms_valid = False
            if request.POST.get('bn-is_current_name_basionym') is None:
                if not basionym_form.is_valid():
                    all_forms_valid = False

            if not all_forms_valid:
                print(f"Errors => \nf : {self.get_form().errors}\nbf : {basionym_form.errors}\ncnf : {cn_form.errors}")
                print(self.request.POST)
                return render(self.request, self.template_name, context={"form": self.get_form(), "cn_form": cn_form, "basionym_form": basionym_form})

            super().post(request, args, kwargs)

            cn_instance = cn_form.save()
            self.object.current_name = cn_instance

            if request.POST.get('bn-is_current_name_basionym') is None:
                basionym_form.save()
                print(basionym_form.data)
                self.object.basionym = basionym_form.instance
            else:
                self.object.basionym = cn_instance

            self.object.save()

            return HttpResponseRedirect(reverse_lazy('taxonomy:taxon-detail', kwargs={'slug': self.object.slug}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cn_form'] = NameCreateForm(prefix="cn")
        context['basionym_form'] = BasionymCreateForm(prefix="bn")
        return context


class HigherTaxonCreateView(CreateView):
    template_name = 'hyphaeTaxonomy/taxa/taxon_create.html'
    model = HigherRankTaxon
    success_url = reverse_lazy('taxonomy:index')
    form_class = HigherRankTaxonCreateForm

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            basionym_form_prefix = "bn"
            cn_form_prefix = "cn"
            basionym_form = BasionymCreateForm(request.POST, prefix=basionym_form_prefix)
            cn_form = NameCreateForm(request.POST, prefix=cn_form_prefix)

            all_forms_valid = True
            if not self.get_form().is_valid():
                all_forms_valid = False
            if not cn_form.is_valid():
                all_forms_valid = False
            if request.POST.get('bn-is_current_name_basionym') is None:
                if not basionym_form.is_valid():
                    all_forms_valid = False

            if not all_forms_valid:
                return self.render_to_response(self.get_context_data(form=self.get_form(), cn_form=cn_form, basionym_form=basionym_form))

            super().post(request, args, kwargs)

            cn_instance = cn_form.save()
            self.object.current_name = cn_instance

            if request.POST.get('bn-is_current_name_basionym') is None:
                basionym_form.save()
                self.object.basionym = basionym_form.instance
            else:
                self.object.basionym = cn_instance

            self.object.save()

            return HttpResponseRedirect(reverse_lazy('taxonomy:taxon-detail', kwargs={'slug': self.object.slug}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cn_form'] = NameCreateForm(prefix="cn")
        context['basionym_form'] = BasionymCreateForm(prefix="bn")
        return context


class SynonymCreateView(CreateView):
    template_name = 'hyphaeTaxonomy/names/create_synonym.html'
    model = Name
    form_class = NameCreateForm
    success_url = reverse_lazy('taxonomy:index')

    def post(self, request, *args, **kwargs):
        if not self.get_form().is_valid():
            return self.render_to_response(self.get_context_data(form=self.get_form()))

        taxon = Taxon.objects.get(slug=self.kwargs.get('slug'))
        super().post(request, args, kwargs)
        taxon.synonyms.add(self.object)
        taxon.save()
        return HttpResponseRedirect(reverse_lazy('taxonomy:taxon-detail', kwargs={'slug': taxon.slug}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxon'] = Taxon.objects.get(slug=self.kwargs.get('slug'))
        return context


class TaxonChangeCurrentNameView(CreateView):
    model = Name
    template_name = 'hyphaeTaxonomy/taxa/change_current_name.html'
    form_class = NameCreateForm
    success_url = reverse_lazy('taxonomy:index')

    def post(self, request, *args, **kwargs):
        if not self.get_form().is_valid():
            return self.render_to_response(self.get_context_data(form=self.get_form()))
        super().post(request, args, kwargs)
        taxon = Taxon.objects.get(slug=self.kwargs.get('slug'))
        old_name = taxon.current_name
        self.object.save()
        taxon.synonyms.add(old_name)
        taxon.current_name = self.object
        taxon.save()

        return HttpResponseRedirect(reverse_lazy('taxonomy:taxon-detail', kwargs={'slug': taxon.slug}))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxon'] = Taxon.objects.get(slug=self.kwargs.get('slug'))
        return context


class NameCreateView(CreateView):
    model = Name
    template_name = 'hyphaeTaxonomy/names/create_name.html'
    form_class = NameCreateForm
    success_url = reverse_lazy('taxonomy:index')


class NameUpdateView(UpdateView):
    model = Name
    template_name = 'hyphaeTaxonomy/names/update_name.html'
    form_class = NameCreateForm
    success_url = reverse_lazy('taxonomy:index')

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            taxon = self.get_object().synonyms.first()
            if 'deleteName' in self.request.POST:
                self.get_object().delete()
                messages.success(message='Successfully deleted name!', request=self.request)
                return redirect(reverse_lazy('taxonomy:taxon-detail', kwargs={'slug': taxon.slug}))
            else:
                return super().post(request, *args, **kwargs)


class IllustrationCreateView(CreateView):
    model = Illustration
    template_name = 'hyphaeTaxonomy/illustrations/illustration_create.html'
    form_class = IllustrationCreateUpdateForm
    success_url = reverse_lazy('taxonomy:index')


class HigherTaxonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return HigherRankTaxon.objects.none()

        qs = HigherRankTaxon.objects.all()

        if self.q:
            qs = qs.filter(current_name__name__istartswith=self.q)

        return qs


class SpecificTaxonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return SpecificTaxon.objects.none()

        qs = SpecificTaxon.objects.all()

        if self.q:
            qs = qs.filter(current_name__name__istartswith=self.q)

        return qs


class APIListTaxonChildren(ListAPIView):
    serializer_class = TreeDataTaxonSerializer

    def get_queryset(self):
        slug = self.request.query_params.get('slug')
        children = Taxon.objects.filter(parent__slug=slug)
        return children
