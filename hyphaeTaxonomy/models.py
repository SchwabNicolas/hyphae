import os
from io import BytesIO

from PIL import Image
from django.core.files.base import ContentFile, File
from django.db import models
from django.db.models import Model, F, SET_DEFAULT
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from polymorphic.models import PolymorphicModel

import utils.image
from hyphaeLibrary.models import License

from utils.database import generate_unique_vanity_fixed
from utils.image import dominant_color


def file_path(instance, subfolder, filename):
    ext = os.path.splitext(filename)
    filename = f"{instance.unique_identifier}{ext[-1]}"
    return os.path.join('uploads', subfolder, filename)


def file(instance, filename):
    return file_path(instance=instance, subfolder='illustrations', filename=filename)


class Name(Model):
    LEGITIMATE_NAME = 'LEG'
    ILLEGITIMATE_NAME = 'ILLEG'
    UNAVAILABLE_NAME = 'UNAV'

    INVALID_NAME = 'Invalid'
    VALID_NAME = 'Valid'
    SANCTIONED_NAME = 'Sanctioned'
    CONSERVED_NAME = 'Conserved'
    PROTECTED_NAME = 'Protected'
    SUPPRESSED_NAME = 'Suppressed'

    NAME_LEGITIMACY = [
        (LEGITIMATE_NAME, 'Legitimate'),
        (ILLEGITIMATE_NAME, 'Illegitimate'),
        (UNAVAILABLE_NAME, 'Unavailable'),
    ]

    VALID_NAMES = [
        (VALID_NAME, 'Nomen validum'),
        (SANCTIONED_NAME, 'Nomen sanctionatum'),
        (CONSERVED_NAME, 'Nomen conservandum'),
        (PROTECTED_NAME, 'Nomen protectum'),
    ]

    INVALID_NAMES = [
        (INVALID_NAME, 'Nomen invalidum'),
        (SUPPRESSED_NAME, 'Nomen rejiciendum'),
    ]

    NAME_VALIDITY = VALID_NAMES + INVALID_NAMES

    name = models.CharField(max_length=100, default="")
    authors = models.CharField(max_length=200, default="")
    literature = models.CharField(max_length=200, default="")
    volume = models.CharField(max_length=20, null=True, blank=True)
    part = models.CharField(max_length=20, null=True, blank=True)
    page = models.CharField(max_length=20, null=True, blank=True)
    year_of_publication = models.IntegerField(null=True, blank=True)
    year_on_publication = models.IntegerField(null=True, blank=True)
    legitimacy = models.CharField(max_length=5, default=LEGITIMATE_NAME, choices=NAME_LEGITIMACY)
    validity = models.CharField(max_length=10, default=VALID_NAME, choices=NAME_VALIDITY)
    original_orthography = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.CharField(max_length=25, blank=True, null=True)
    icn_identifier = models.IntegerField(blank=True, null=True)
    nomenclatural_comment = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Taxon(PolymorphicModel):
    SPECIES = 'sp.'
    GENUS = 'gen.'
    FAMILY = 'fam.'
    ORDER = 'ord.'
    SUBCLASS = 'subcl.'
    CLASS = 'class'
    SUBPHYLUM = 'subd.'
    PHYLUM = 'div.'
    SUBKINGDOM = 'subregn.'
    KINGDOM = 'regn.'

    RANK_LEVELS = {
        SPECIES: 9,
        GENUS: 8,
        FAMILY: 7,
        ORDER: 6,
        SUBCLASS: 5,
        CLASS: 4,
        SUBPHYLUM: 3,
        PHYLUM: 2,
        SUBKINGDOM: 1,
        KINGDOM: 0
    }

    SPECIES_RANK = {
        SPECIES: 'Species',
    }

    HIGHER_RANKS = {
        KINGDOM: 'Kingdom',
        SUBKINGDOM: 'Subkingdom',
        PHYLUM: 'Division',
        SUBPHYLUM: 'Subdivision',
        CLASS: 'Class',
        SUBCLASS: 'Subclass',
        ORDER: 'Order',
        FAMILY: 'Family',
        GENUS: 'Genus',
    }

    RANKS = HIGHER_RANKS | SPECIES_RANK

    RANK_CHOICES = [(k, v) for k, v in RANKS.items()]

    current_name = models.ForeignKey(Name, on_delete=models.DO_NOTHING, related_name='current_name', default=None, null=True)
    basionym = models.ForeignKey(Name, on_delete=models.DO_NOTHING, related_name='basionyms', default=None, null=True)
    synonyms = models.ManyToManyField(Name, related_name='synonyms', related_query_name='synonym')
    rank = models.CharField(max_length=10, verbose_name="Rank", default=KINGDOM, choices=RANK_CHOICES)
    parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, verbose_name="Parent", default=None, null=True)
    slug = models.SlugField(blank=True, unique=True, verbose_name="Slug")
    diagnosis = MarkdownxField(blank=True, null=True, verbose_name="Diagnosis", )
    cover_illustration = models.ForeignKey('Illustration', on_delete=models.DO_NOTHING, related_name='cover_illustration', related_query_name='cover_illustrations', default=None, null=True)

    def has_children(self):
        return Taxon.objects.filter(parent=self).exists()

    def rank_level(self):
        return list(self.RANKS).index(self.rank)

    def get_parents(self):
        if self.parent is None:
            return Taxon.objects.none()
        return self.parent.get_parents() | Taxon.objects.filter(slug=self.parent.slug)

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.current_name}")
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.current_name.name


class HigherRankTaxon(Taxon):
    pass


class SpecificTaxon(Taxon):
    REGIONALLY_EXTINCT = ('RE', 'Regionally extinct')

    CRITICALLY_ENDANGERED = ('CR', 'Critically endangered')
    ENDANGERED = ('EN', 'Endangered')
    VULNERABLE = ('VU', 'Vulnerable')
    NEAR_THREATENED = ('NT', 'Near threatened')
    LEAST_CONCERN = ('LC', 'Least concern')
    DATA_DEFICIENT = ('DD', 'Data deficient')
    NOT_EVALUATED = ('NE', 'Not evaluated')
    NOT_APPLICABLE = ('NA', 'Not applicable')

    EXTINCT = ('EX', 'Extinct')
    EXTINCT_IN_THE_WILD = ('EW', 'Extinct in the wild')

    REGIONAL_IUCN_CATEGORIES = [
        REGIONALLY_EXTINCT,
        CRITICALLY_ENDANGERED,
        ENDANGERED,
        VULNERABLE,
        NEAR_THREATENED,
        LEAST_CONCERN,
        DATA_DEFICIENT,
        NOT_APPLICABLE,
        NOT_EVALUATED,
    ]

    GLOBAL_IUCN_CATEGORIES = [
        EXTINCT,
        EXTINCT_IN_THE_WILD,
        CRITICALLY_ENDANGERED,
        ENDANGERED,
        VULNERABLE,
        NEAR_THREATENED,
        LEAST_CONCERN,
        DATA_DEFICIENT,
        NOT_EVALUATED,
    ]

    UNKNOWN = "UN"
    NOT_LICHENIZED = "NL"
    LICHENIZED = "LI"
    MYCOPHYCOBIOSIS = "MY"

    LICHENIZATION_TYPES = [
        (UNKNOWN, 'Unknown'),
        (NOT_LICHENIZED, 'Not lichenized'),
        (LICHENIZED, 'Lichenized'),
        (MYCOPHYCOBIOSIS, 'Mycophycobiosis'),
    ]

    lichenization = models.CharField(default=NOT_LICHENIZED, choices=LICHENIZATION_TYPES, max_length=5)

    class Meta:
        verbose_name = 'taxon'
        verbose_name_plural = 'taxa'

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.current_name}")
        self.rank = self.SPECIES
        return super().save(*args, **kwargs)


class TaxaListEntry(Model):
    ORGANISM_GROUPS = [
        ('AGA', 'Agaricoids'),
        ('BOL', 'Boletoids'),
        ('POL', 'Polyporoids'),
        ('COR', 'Corticioids'),
        ('GAS', 'Gasteromycetoids'),
        ('PLE', 'Pleurotoids'),
        ('CYP', 'Cyphelloids'),
        ('CYP', 'Clavarioids'),
        ('RUS', 'Rusts'),
        ('SMU', 'Smuts'),
        ('EXO', 'Exobasidiomycetes'),

        ('DIS', 'Discomycetes'),
        ('PYR', 'Pyrenomycetes'),
        ('PHY', 'Phytopathogenic Ascomycetes'),
        ('TAP', 'Taphrinomycetes'),
        ('OTH', 'Other Ascomycetes'),

        ('OOM', 'Oomycetes'),
        ('CHY', 'Chytridiomycetes'),
        ('GLO', 'Glomeromycetes'),
        ('MYX', 'Myxomycetes'),
    ]

    taxon = models.ForeignKey(Taxon, on_delete=models.DO_NOTHING, null=True)
    aggregatum = models.BooleanField(default=False, verbose_name="Aggregatum")
    organism_group = models.CharField(choices=ORGANISM_GROUPS, max_length=3, default='AGA', verbose_name="Organism Group")


class Illustration(Model):
    ILLUSTRATION_TYPES = [
        ('MAC', 'Macromorphology'),
        ('MIC', 'Micromorphology'),
        ('HAB', 'Habitat and ecology'),
        ('TAB', 'Table'),
        ('HIS', 'Historical illustration'),
        ('DRA', 'Drawing'),
        ('LIT', 'Lithography'),
        ('HER', 'Herbarium specimen photograph'),
        ('CYA', 'Cyanotype'),
    ]

    IMAGE_MAX_DIMENSIONS = (2000, 2000)
    SMALL_IMAGE_MAX_DIMENSIONS = (400, 400)
    THUMBNAIL_IMAGE_MAX_DIMENSIONS = (300, 300)
    DEFAULT_LICENSE_ID = 1

    vanity = models.SlugField(null=True, max_length=20, verbose_name='Vanity')
    file = models.ImageField(upload_to='images/', verbose_name="File")
    small = models.ImageField(upload_to='images/', verbose_name="Small", null=True, blank=True)
    thumbnail = models.ImageField(upload_to='images/', verbose_name="Thumbnail", null=True, blank=True)
    legend = models.TextField(max_length=700, default="", blank=True, null=True, verbose_name="Legend")
    location = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name="Location")
    specimen = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name="Specimen")
    source = models.CharField(max_length=250, default="", blank=True, null=True, verbose_name="Source")
    taxon = models.ForeignKey(Taxon, models.CASCADE, verbose_name="Taxon")
    author = models.CharField(max_length=100, default="", blank=True, null=True, verbose_name="Author")
    illustration_type = models.CharField(max_length=25, default="MAC", choices=ILLUSTRATION_TYPES, verbose_name="Illustration type")
    license = models.ForeignKey(License, on_delete=SET_DEFAULT, default=DEFAULT_LICENSE_ID, verbose_name="License")
    dominant_color = models.CharField(max_length=7, blank=True, null=True, verbose_name="Dominant color")

    class Meta:
        verbose_name = 'illustration'
        verbose_name_plural = 'illustrations'

    def save(self, *args, **kwargs):
        if not self.vanity:
            self.vanity = generate_unique_vanity_fixed(15, self.__class__)

        if self.pk is None and self.file is not None:
            img = Image.open(self.file)  # Catch original
            self.save_image(img)
            self.save_small(img)
            self.save_thumbnail(img)

        thumb = Image.open(self.thumbnail)
        self.dominant_color = utils.image.dominant_color(thumb)

        return super(Illustration, self).save(*args, **kwargs)

    def save_image(self, img):
        source_image = img.convert('RGB')
        source_image.thumbnail(self.IMAGE_MAX_DIMENSIONS)  # Resize to size
        output = BytesIO()
        source_image.save(output, format='JPEG')  # Save resize image to bytes
        output.seek(0)

        content_file = ContentFile(output.read())  # Read output and create ContentFile in memory
        file = File(content_file)

        name = f'{self.vanity}.jpg'
        self.file.save(name, file, save=False)

    def save_small(self, img):
        source_image = img.convert('RGB')
        source_image.thumbnail(self.SMALL_IMAGE_MAX_DIMENSIONS)  # Resize to size
        output = BytesIO()
        source_image.save(output, format='JPEG')  # Save resize image to bytes
        output.seek(0)

        content_file = ContentFile(output.read())  # Read output and create ContentFile in memory
        file = File(content_file)

        name = f'{self.vanity}-small.jpg'
        self.small.save(name, file, save=False)

    def save_thumbnail(self, img):
        source_image = img.convert('RGB')
        source_image.thumbnail(self.THUMBNAIL_IMAGE_MAX_DIMENSIONS)  # Resize to size
        width, height = source_image.size

        if height < width:
            left = (width - height) / 2
            right = (width + height) / 2
            top = 0
            bottom = height
            source_image = source_image.crop((left, top, right, bottom))

        elif height > width:
            left = 0
            right = width
            top = 0
            bottom = width
            source_image = source_image.crop((left, top, right, bottom))

        output = BytesIO()
        source_image.save(output, format='JPEG')  # Save resize image to bytes
        output.seek(0)

        content_file = ContentFile(output.read())  # Read output and create ContentFile in memory
        file = File(content_file)

        name = f'{self.vanity}-thumb.jpg'
        self.thumbnail.save(name, file, save=False)


@receiver(post_save, sender=Illustration, dispatch_uid="update_stock_count")
def illustration_post_save(sender, instance, **kwargs):
    print(instance.taxon)
    if instance.taxon.cover_illustration is None:
        instance.taxon.cover_illustration = instance
        instance.taxon.save()
