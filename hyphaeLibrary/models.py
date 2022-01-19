import os

from django.core.files.storage import FileSystemStorage
from django.db import models

# Create your models here.
from django.db.models import Model, DO_NOTHING, CASCADE, SET_NULL, SET_DEFAULT
from django.urls import reverse
from pikepdf._qpdf import Pdf
from polymorphic.models import PolymorphicModel

from hyphaeAuth.models import HyphaeUser
from utils.database import generate_unique_vanity_fixed


class License(Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    short_name = models.CharField(max_length=50, verbose_name="Short name")
    link = models.CharField(max_length=100, blank=True, null=True, verbose_name="Link")
    public_available = models.BooleanField(blank=True, default=False, verbose_name="Available to public")

    def __str__(self):
        return self.short_name


class VanityNameFileStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if max_length and len(name) > max_length:
            raise (Exception("name's length is greater than max_length"))
        return name

    def _save(self, name, content):
        if self.exists(name):
            self.delete(name)
        return super(VanityNameFileStorage, self)._save(name, content)


def file_path(instance, subfolder, filename):
    ext = os.path.splitext(filename)
    filename = f"{instance.unique_identifier}{ext[-1]}"
    return os.path.join('uploads', subfolder, filename)


def file(instance, filename):
    return file_path(instance=instance, subfolder='literature', filename=filename)


def thumbnail(instance, filename):
    return file_path(instance=instance, subfolder='literature_thumbs', filename=filename)


class Document(Model):
    DEFAULT_LICENSE_ID = 1

    FILE_STATUS = [
        ('PU', 'Published'),
        ('IP', 'In press'),
        ('PP', 'Pre-print'),
        ('UN', 'Unpublished'),
    ]

    uploader = models.ForeignKey(HyphaeUser, on_delete=SET_NULL, null=True, blank=True, verbose_name='Uploaded by')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='Upload time')
    unique_identifier = models.CharField(max_length=50, verbose_name="Unique identifier")
    license = models.ForeignKey(License, on_delete=SET_DEFAULT, default=DEFAULT_LICENSE_ID)
    file = models.FileField(upload_to=file, null=True, blank=True, storage=VanityNameFileStorage(), verbose_name='File')
    thumbnail = models.ImageField(upload_to=thumbnail, null=True, blank=True, storage=VanityNameFileStorage(), verbose_name='thumbnail')
    file_status = models.CharField(max_length=5, choices=FILE_STATUS, default='PU', verbose_name='Status of the file')
    page_number = models.IntegerField(default=0, blank=True, null=True, verbose_name='Page number')

    def save(self, *args, **kwargs):
        self.update_page_number()
        return super(Document, self).save(*args, **kwargs)

    def update_page_number(self):
        pdf = Pdf.open(self.file.file)
        self.page_number = len(pdf.pages)


ORDER_NAME_FIRST = "name_first"
ORDER_INITIALS_FIRST = "initials_first"


class Literature(PolymorphicModel):
    LANGUAGES = [
        ('EN', 'English'),
        ('FR', 'French'),
        ('DE', 'German'),
        ('IT', 'Italian'),
        ('SP', 'Spanish'),
        ('PO', 'Portuguese'),
        ('LA', 'Latin'),
        ('GR', 'Greek'),
        ('RU', 'Russian'),
        ('SW', 'Swedish'),
        ('CZ', 'Czech'),
        ('RO', 'Roumanian'),
        ('CS', 'Chinese'),
        ('JP', 'Japanese'),
        ('HU', 'Hungarian'),
        ('DA', 'Danish'),
        ('CA', 'Catalan'),
        ('GA', 'Galician'),
        ('TU', 'Turkish'),
        ('SE', 'Serbian'),
    ]

    FILE_STATUS = [
        ('PU', 'Published'),
        ('PU', 'Reprint'),
        ('IP', 'In press'),
        ('PP', 'Pre-print'),
        ('UN', 'Unpublished'),
    ]

    title = models.CharField(max_length=600, blank=True, null=True, verbose_name='Title')
    original_title = models.CharField(max_length=500, blank=True, null=True, verbose_name='Original title')
    authors = models.TextField(max_length=2200, blank=True, null=True, verbose_name='Authors')
    doi = models.CharField(max_length=50, null=True, blank=True, verbose_name='DOI')
    abstract = models.TextField(max_length=10000, null=True, blank=True, verbose_name='Abstract')
    keywords = models.CharField(max_length=500, null=True, blank=True, verbose_name='Keywords')
    language = models.CharField(max_length=200, verbose_name='Language', choices=LANGUAGES, default='EN')
    year_of_publication = models.IntegerField(blank=True, null=True, verbose_name='Year of publication')
    year_on_publication = models.IntegerField(blank=True, null=True, verbose_name='Year on publication')
    taxonomical_novelties = models.TextField(max_length=5000, null=True, blank=True, verbose_name='Taxonomical novelties')
    remarks = models.TextField(max_length=1200, null=True, blank=True, verbose_name='Remarks')
    date_created = models.DateField(auto_now=True, verbose_name='Time created')
    vanity = models.SlugField(null=True, max_length=20, verbose_name='Vanity')

    document = models.ForeignKey(Document, on_delete=CASCADE, null=True, blank=True, verbose_name='Document')

    @property
    def truncated_abstract(self):
        return self.abstract[0:510]

    @property
    def authors_readable(self):
        if self.authors:
            split_authors = self.authors.split('; ')
            if len(split_authors) > 1:
                x = 0
                for author in split_authors:
                    split_authors[x] = author.replace(', ', ' ')
                    x += 1
                comma_sep = ', '.join(split_authors[:-1])
                return f'{comma_sep} & {split_authors[-1]}'
            else:
                return f'{split_authors[-1]}'.replace(', ', ' ')

    class Author:
        def __init__(self, name, initials):
            self.name = name
            self.initials = initials

    def split_authors(self):
        authors = []
        if self.authors:
            split_authors = self.authors.split(';')
            for author in split_authors:
                split_author = author.split(',')
                author_dict = {
                    'name': split_author[0].rstrip(),
                    'initials': split_author[1].rstrip()
                }
                authors.append(author_dict)
        return authors

    def join_authors(self, order=ORDER_NAME_FIRST, name_separator=", ", authors_separator=", ", last_author_indicator=None):
        split_authors = self.split_authors()
        authors_to_str = []
        if order == ORDER_NAME_FIRST:
            for author in split_authors:
                authors_to_str.append(f"{author['name']}{name_separator}{author['initials']}")
        elif order == ORDER_INITIALS_FIRST:
            for author in split_authors:
                authors_to_str.append(f"{author['initials']}{name_separator}{author['name']}")

        if len(authors_to_str) > 1:
            if last_author_indicator is not None:
                authors_str = authors_separator.join(authors_to_str[:-1])
                return f"{authors_str}{last_author_indicator}{authors_to_str[-1]}"
            else:
                return authors_separator.join(authors_to_str)
        else:
            return authors_to_str[0]

    @property
    def short_citation(self):
        y_of_pub_text = f'({self.year_of_publication})' if self.year_of_publication else '(unknown)'
        y_on_pub_text = f' [{self.year_on_publication}]' if self.year_on_publication else ''
        authors_text = f'{self.authors[0:30]}…' if len(self.authors) > 30 else self.authors

        return f'{authors_text} {y_of_pub_text}{y_on_pub_text}.'

    def get_citation(self, style):
        return "PLACEHOLDER CITATION"

    def save(self, *args, **kwargs):
        if not self.vanity:
            self.vanity = generate_unique_vanity_fixed(15, self.__class__)

        return super(Literature, self).save(*args, **kwargs)

    CITATION_STYLES = [
        'APA',
        'MLA',
        'Chicago/Turabian',
        'IEEE',
    ]

    def get_absolute_url(self):
        return reverse("library:literature-detail", kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse("library:literature-update", kwargs={'pk': self.id})

    def __str__(self):
        return self.short_citation

    def __unicode__(self):
        return self.short_citation


class Publication(Literature):
    volume = models.CharField(max_length=20, blank=True, null=True, verbose_name='Volume')
    part = models.CharField(max_length=20, blank=True, null=True, verbose_name='Part')
    identifier = models.CharField(max_length=20, blank=True, null=True, verbose_name='Identifier')
    first_page = models.IntegerField(blank=True, null=True, verbose_name='First page')
    last_page = models.IntegerField(blank=True, null=True, verbose_name='Last page')
    series = models.CharField(max_length=150, blank=True, null=True, verbose_name='Series')

    @property
    def short_citation(self):
        y_of_pub_text = f'({self.year_of_publication})' if self.year_of_publication else '(unknown)'
        y_on_pub_text = f' [{self.year_on_publication}]' if self.year_on_publication else ''
        volume_text = f' {self.volume}' if self.volume else ''
        part_text = f'({self.part})' if self.part else ''
        pages_text = f': {self.first_page}-{self.last_page}' if self.first_page else ''
        authors_text = f'{self.authors[0:30]}…' if len(self.authors) > 30 else self.authors

        return f'{authors_text} {y_of_pub_text}{y_on_pub_text}. {self.series}{volume_text}{part_text}){pages_text}.'

    def save(self, *args, **kwargs):
        y_of_pub_text = f'({self.year_of_publication})' if self.year_of_publication else '(unknown)'
        y_on_pub_text = f' [{self.year_on_publication}]' if self.year_on_publication else ''
        volume_text = f' {self.volume}' if self.volume else ''
        part_text = f'({self.part})' if self.part else ''
        pages_text = f': {self.first_page}-{self.last_page}' if self.first_page else ''
        series_text = self.series if self.series else ''

        self.citation = f'<b>{self.authors} {y_of_pub_text}{y_on_pub_text}</b>. {self.title}. <i>{series_text}{volume_text}{part_text}){pages_text}.</i>'

        return super().save(*args, **kwargs)

    def get_citation(self, style):
        # join_authors(self, order=ORDER_NAME_FIRST, name_separator=", ", authors_separator=", ", last_author_indicator=None)
        if style == 'APA':
            authors = super().join_authors(order=ORDER_NAME_FIRST, name_separator=', ', authors_separator=", ", last_author_indicator=", & ")
            citation = f"{authors} ({self.year_of_publication}). {self.title}. {self.series}"
            if self.part:
                citation += f" {self.volume}({self.part})"
            else:
                citation += f" {self.volume}"

            if self.identifier:
                citation += f", {self.identifier}"
            else:
                citation += f", {self.first_page}-{self.last_page}"

            if self.doi:
                citation += f". https://doi.org/{self.doi}"

            return citation
        elif style == "Hyphae":
            authors = super().join_authors(order=ORDER_NAME_FIRST, name_separator=' ', authors_separator=", ", last_author_indicator=" & ")
            citation = f"{authors} ({self.year_of_publication})"
            if self.year_on_publication:
                citation += f"[{self.year_on_publication}]."
            else:
                citation += f"."

            citation += f" {self.title}. {self.series}"

            if self.part:
                citation += f" {self.volume}({self.part})"
            else:
                citation += f" {self.volume}"

            if self.identifier:
                citation += f": {self.identifier}."
            else:
                citation += f": {self.first_page}-{self.last_page}."

            if self.doi:
                citation += f" DOI: {self.doi}"

            return citation


class Thesis(Literature):
    university = models.CharField(max_length=100, blank=True, null=True)

    def get_citation(self, style):
        return "CITATION PLACEHOLDER"


class Book(Literature):
    edition = models.CharField(max_length=20, blank=True, null=True, verbose_name="Edition")
    series = models.CharField(max_length=200, blank=True, null=True, verbose_name='Series')
    volume = models.CharField(max_length=20, blank=True, null=True, verbose_name='Volume')
    isbn = models.CharField(max_length=25, blank=True, null=True, verbose_name='ISBN')
    publisher = models.CharField(max_length=50, blank=True, null=True, verbose_name='Publisher')
    location = models.CharField(max_length=50, blank=True, null=True, verbose_name='Location')

    def get_citation(self, style):
        return "CITATION PLACEHOLDER"


class Series(Model):
    name = models.CharField(max_length=100, primary_key=True, verbose_name='Name', unique=True)
    abbreviated_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='Abbreviated name')


class Keyword(Model):
    pass
