from django.db import models
from django.db.models import Model
from django.utils.text import slugify

from hyphaeLibrary.models import Publication


class Name(Model):
    LEGITIMATE_NAME = 'LEG'
    ILLEGITIMATE_NAME = 'ILLEG'

    INVALID_NAME = 'Invalid'
    VALID_NAME = 'Valid'
    CONSERVED_NAME = 'Conserved'
    SUPPRESSED_NAME = 'Suppressed'

    NAME_LEGITIMACY = [
        (LEGITIMATE_NAME, 'Legitimate'),
        (ILLEGITIMATE_NAME, 'Illegitimate'),
    ]

    VALID_NAMES = [
        (VALID_NAME, 'Nomen validum'),
        (CONSERVED_NAME, 'Nomen conservandum'),
    ]

    INVALID_NAMES = [
        (INVALID_NAME, 'Nomen invalidum'),
        (SUPPRESSED_NAME, 'Nomen rejiciendum'),
    ]

    NAME_VALIDITY = VALID_NAMES + INVALID_NAMES

    name = models.CharField(max_length=100)
    authors = models.CharField(max_length=200)
    literature = models.ForeignKey(Publication, on_delete=models.DO_NOTHING, default=None, null=True)
    legitimacy = models.CharField(max_length=5, default=LEGITIMATE_NAME, choices=NAME_LEGITIMACY)
    basionym = models.ForeignKey('self', on_delete=models.DO_NOTHING, related_name='basionyms', default=None, null=True)
    validity = models.CharField(max_length=10, default=VALID_NAME, choices=NAME_VALIDITY)
    original_orthography = models.CharField(max_length=100, blank=True, null=True)
    diagnosis = models.TextField(default="", max_length=2000, blank=True, null=True, verbose_name="Diagnosis")


class Taxon(Model):
    SPECIES = 'Species'
    GENUS = 'Genus'
    FAMILY = 'Family'
    ORDER = 'Order'
    CLASS = 'Class'
    SUBPHYLUM = 'Subphylum'
    PHYLUM = 'Phylum'
    SUBKINGDOM = 'Subkingdom'
    KINGDOM = 'Kingdom'
    SUPERKINGDOM = 'Superkingdom'

    RANKS = [
        (SUPERKINGDOM, 'super.'),
        (KINGDOM, 'regn.'),
        (SUBKINGDOM, 'subregn.'),
        (PHYLUM, 'div.'),
        (SUBPHYLUM, 'subd.'),
        (CLASS, 'class'),
        (ORDER, 'ord.'),
        (FAMILY, 'fam.'),
        (GENUS, 'gen.'),
        (SPECIES, 'sp.'),
    ]

    current_name = models.ForeignKey(Name, on_delete=models.DO_NOTHING, related_name='current_name')
    synonyms = models.ManyToManyField(Name, related_name='synonyms', related_query_name='synonym')
    rank = models.CharField(max_length=10, verbose_name="Rank")
    parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, verbose_name="Parent", default=None, null=True)
    slug = models.SlugField(blank=True, unique=True, verbose_name="Slug")

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.current_name}")
        return super().save(*args, **kwargs)


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

    name = models.CharField(default="", max_length=100, verbose_name="Epithet")
    regional_iucn_category = models.CharField(choices=REGIONAL_IUCN_CATEGORIES, max_length=3, default='NE', verbose_name="Regional IUCN Category")
    global_iucn_category = models.CharField(choices=GLOBAL_IUCN_CATEGORIES, max_length=3, default='NE', verbose_name="Global IUCN Category")
    lichenization = models.CharField(default=NOT_LICHENIZED, choices=LICHENIZATION_TYPES, max_length=5)

    class Meta:
        verbose_name = 'taxon'
        verbose_name_plural = 'taxa'


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
    file = models.ImageField(upload_to='images/', verbose_name="File")
    legend = models.TextField(max_length=100, default="", blank=True, null=True, verbose_name="Legend")
    taxon = models.ForeignKey(Taxon, models.CASCADE, verbose_name="Taxon")

    class Meta:
        verbose_name = 'illustration'
        verbose_name_plural = 'illustrations'
