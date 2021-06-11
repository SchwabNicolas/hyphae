import os
from io import BytesIO
from django.forms import ModelForm, Form, BooleanField
from django_cleanup import cleanup
from pikepdf._qpdf import Pdf

from hyphaeLibrary.models import Literature, Publication, Thesis, Book, Document


class DocumentCreateUpdateForm(ModelForm):
    delete_first_page = BooleanField(label='Delete first page', required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.unique_identifier = kwargs.pop('unique_identifier', None)
        super(DocumentCreateUpdateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(DocumentCreateUpdateForm, self).save(commit=False)
        instance.uploader = self.user
        instance.unique_identifier = self.unique_identifier
        if commit:
            instance.save()
            if instance.file and self.cleaned_data['delete_first_page']:
                tempfile = BytesIO()
                with instance.file as file:
                    pdf = Pdf.open(file)
                    del pdf.pages[0]
                    pdf.save(tempfile)
                file.save(file.name, tempfile)
                instance.update_page_number()
                cleanup.refresh(instance)
        return instance

    class Meta:
        model = Document
        fields = '__all__'
        exclude = [
            'uploader',
            'upload_time',
            'unique_identifier'
        ]


class BaseLiteratureCreateUpdateForm(ModelForm):
    class Meta:
        model = Literature
        fields = [
            'title',
            'original_title',
            'authors',
            'year_of_publication',
            'year_on_publication',
            'doi',
            'language',
            'abstract',
            'keywords',
            'remarks',
        ]


class PublicationCreateUpdateForm(ModelForm):
    delete_first_page = BooleanField(label='Delete first page', required=False)

    class Meta:
        model = Publication
        fields = [
            'title',
            'original_title',
            'authors',
            'year_of_publication',
            'year_on_publication',
            'series',
            'volume',
            'part',
            'identifier',
            'first_page',
            'last_page',
            'doi',
            'language',
            'abstract',
            'keywords',
            'taxonomical_novelties',
            'remarks',
        ]


class ThesisCreateUpdateForm(ModelForm):
    class Meta:
        model = Thesis
        fields = [
            'title',
            'original_title',
            'authors',
            'university',
            'year_of_publication',
            'year_on_publication',
            'doi',
            'language',
            'abstract',
            'keywords',
            'taxonomical_novelties',
            'remarks',
        ]


class BookCreateUpdateForm(ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'edition',
            'original_title',
            'authors',
            'year_of_publication',
            'year_on_publication',
            'series',
            'volume',
            'doi',
            'isbn',
            'publisher',
            'location',
            'language',
            'abstract',
            'keywords',
            'taxonomical_novelties',
            'remarks',
        ]
