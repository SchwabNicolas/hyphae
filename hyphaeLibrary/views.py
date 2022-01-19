# Create your views here.
import polymorphic
from django.contrib import messages
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, UpdateView, TemplateView
from django.views.generic.detail import DetailView

from hyphaeLibrary.forms import BaseLiteratureCreateUpdateForm, PublicationCreateUpdateForm, ThesisCreateUpdateForm, BookCreateUpdateForm, DocumentCreateUpdateForm
from hyphaeLibrary.models import Literature, Publication, Thesis, Book, Document


class LibraryIndexView(TemplateView):
    template_name = 'hyphaeLibrary/literature/index.html'

    def post(self, request, *args, **kwargs):
        if 'searchLiterature' in self.request.POST:
            return redirect(reverse('library:literature-search', kwargs={"query": self.request.POST.get('searchLiterature')}))
        return HttpResponse(status=200)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['literature_count'] = Literature.objects.all().count()
        context['documents'] = Document.objects.all().aggregate(total_pages=Sum('page_number'))
        return context


class LiteratureAdvancedSearchView(TemplateView):
    template_name = 'hyphaeLibrary/literature/advanced_search.html'


class LiteratureSearchView(ListView):
    template_name = 'hyphaeLibrary/literature/literature_search.html'
    model = Literature

    def get_queryset(self):
        vector = SearchVector('title') + SearchVector('original_title') + SearchVector('abstract') + SearchVector('keywords')
        query = SearchQuery(self.kwargs.get('query'))
        return Literature.objects.annotate(
            rank=SearchRank(
                vector=vector,
                query=query
            )
        ).order_by('-rank').filter(rank__gt=0.0001)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['literature_count'] = Literature.objects.all().count()
        return context


class LiteratureCreateView(CreateView):
    template_name = 'hyphaeLibrary/literature/literature_create.html'
    model = Literature
    success_url = reverse_lazy('library:index')

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if 'type' in self.request.GET:
            if self.request.GET.get('type') == 'article':
                form_class = PublicationCreateUpdateForm
                self.form_class = PublicationCreateUpdateForm
            elif self.request.GET.get('type') == 'thesis':
                form_class = ThesisCreateUpdateForm
                self.form_class = ThesisCreateUpdateForm
            elif self.request.GET.get('type') == 'book':
                form_class = BookCreateUpdateForm
                self.form_class = BookCreateUpdateForm
            else:
                form_class = BaseLiteratureCreateUpdateForm
                self.form_class = BaseLiteratureCreateUpdateForm
        else:
            form_class = BaseLiteratureCreateUpdateForm
            self.form_class = BaseLiteratureCreateUpdateForm
        return form_class(**self.get_form_kwargs())

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            super().post(request, args, kwargs)

            doc_form = DocumentCreateUpdateForm(request.POST,
                                                request.FILES,
                                                user=self.request.user,
                                                unique_identifier=self.object.vanity)
            if doc_form.is_valid():
                doc_form.data.unique_identifier = self.object.vanity
                doc_form.save()
                self.object.document = doc_form.instance
            self.object.save()
            return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_class'] = self.get_form_class().__name__
        context['doc_form'] = DocumentCreateUpdateForm()
        return context


class LiteratureListView(ListView):
    template_name = 'hyphaeLibrary/literature/literature_list.html'
    context_object_name = 'literature_list'
    model = Literature

    def get_queryset(self):
        return self.model.objects.all()


class LiteratureUpdateView(UpdateView):
    template_name = 'hyphaeLibrary/literature/literature_update.html'
    context_object_name = 'literature'
    model = Literature
    slug_field = 'vanity'
    slug_url_kwarg = 'vanity'

    document_object = None

    def get_success_url(self):
        return reverse('library:literature-detail', kwargs={'vanity': self.get_object().vanity})

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        literature = self.get_object()
        if isinstance(literature, Publication):
            form_class = PublicationCreateUpdateForm
            self.form_class = PublicationCreateUpdateForm
        elif isinstance(literature, Thesis):
            form_class = ThesisCreateUpdateForm
            self.form_class = ThesisCreateUpdateForm
        elif isinstance(literature, Book):
            form_class = BookCreateUpdateForm
            self.form_class = BookCreateUpdateForm
        else:
            form_class = BaseLiteratureCreateUpdateForm
            self.form_class = BaseLiteratureCreateUpdateForm
        return form_class(**self.get_form_kwargs())

    def get_document(self, vanity):
        if Document.objects.filter(unique_identifier=vanity).exists():
            return Document.objects.get(unique_identifier=vanity)
        return None

    def get_doc_object(self, queryset=None):
        return self.get_document(self.kwargs['vanity'])

    def post(self, request, *args, **kwargs):
        self.document_object = self.get_doc_object()

        if 'updateSub' in self.request.POST:
            doc_form = DocumentCreateUpdateForm(self.request.POST,
                                                self.request.FILES,
                                                instance=self.document_object,
                                                user=self.request.user,
                                                unique_identifier=self.get_object().vanity)
            if doc_form.is_valid():
                form = self.get_form()
                form.instance = self.get_object()
                doc_form.save()
                form.instance.document = self.document_object
                doc_form.data.unique_identifier = self.get_object().vanity
                form.save()
                return HttpResponseRedirect(self.get_success_url())
            print(doc_form.errors)
            return render(request, self.template_name, {'doc_form': doc_form, 'form': self.get_form()})
        elif 'deleteSub' in self.request.POST:
            self.get_object().delete()
            messages.success(message='Successfully deleted publication!', request=self.request)
            return redirect('library:index')
        elif 'changeTypeSub' in self.request.POST:
            new_type = None
            if self.request.POST.get('changeTypeSelect') == 'Publication':
                new_type = Publication
            elif self.request.POST.get('changeTypeSelect') == 'Thesis':
                new_type = Thesis
            elif self.request.POST.get('changeTypeSelect') == 'Book':
                new_type = Book
            elif self.request.POST.get('changeTypeSelect') == 'Literature':
                new_type = Literature

            new_obj = new_type(
                title=self.get_object().title,
                authors=self.get_object().authors,
                doi=self.get_object().doi,
                abstract=self.get_object().abstract,
                keywords=self.get_object().keywords,
                language=self.get_object().language,
                year_of_publication=self.get_object().year_of_publication,
                year_on_publication=self.get_object().year_on_publication,
                remarks=self.get_object().remarks,
                file=self.get_object().file,
                date_created=self.get_object().date_created,
            )
            new_obj.save()

            self.get_object().delete()

            return redirect('library:literature-update', kwargs={'vanity': new_obj.vanity})

    def get(self, request, *args, **kwargs):
        self.document_object = self.get_doc_object()
        return super().get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_class'] = self.get_form_class().__name__
        context['doc_form'] = DocumentCreateUpdateForm(instance=self.get_doc_object())
        return context


class LiteratureDetailView(DetailView):
    template_name = 'hyphaeLibrary/literature/literature_detail.html'
    context_object_name = 'literature'
    model = Literature
    slug_field = 'vanity'
    slug_url_kwarg = 'vanity'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.get_object().get_citation("Hyphae"))
        return context
