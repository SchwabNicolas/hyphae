"""hyphae URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path

from hyphaeTaxonomy.views import TaxaListView, TaxonDetailView, HigherTaxonCreateView, IndexView, SpecificTaxonCreateView, HigherTaxonAutocomplete, APIListTaxonChildren, SynonymCreateView, NameUpdateView, IllustrationCreateView, SpecificTaxonAutocomplete, TaxonChangeCurrentNameView, TaxonUpdateView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('index/', IndexView.as_view(), name='index'),

    path('taxa/list', TaxaListView.as_view(), name='taxa-list'),
    path('taxon/create-higher', HigherTaxonCreateView.as_view(), name='taxon-create-higher'),
    path('taxon/create-species', SpecificTaxonCreateView.as_view(), name='taxon-create-species'),
    path('taxon/<slug:slug>/<str:layout>', TaxonDetailView.as_view(), name='taxon-detail'),
    path('taxon/<slug:slug>', TaxonDetailView.as_view(), name='taxon-detail'),

    path('taxon/edit/<slug:slug>/', TaxonUpdateView.as_view(), name='taxon-update'),
    path('taxon/edit/<slug:slug>/current-name', TaxonChangeCurrentNameView.as_view(), name='taxon-change-current-name'),
    path('taxon/edit/<slug:slug>/basionym', TaxonDetailView.as_view(), name='taxon-edit-basionym'),
    path('taxon/edit/<slug:slug>/create-synonym', SynonymCreateView.as_view(), name='taxon-create-synonym'),
    path('name/edit/<int:pk>/edit-name', NameUpdateView.as_view(), name='taxon-update-synonym'),

    path('name/edit/<int:pk>/edit-name', NameUpdateView.as_view(), name='name-edit'),

    path('illustration/create', IllustrationCreateView.as_view(), name='illustration-create'),

    url(r'^higher-taxon-autocomplete/$', HigherTaxonAutocomplete.as_view(), name='higher-taxon-autocomplete'),
    url(r'^specific-taxon-autocomplete/$', SpecificTaxonAutocomplete.as_view(), name='specific-taxon-autocomplete'),

    # API
    path('api/list-taxon-children/', APIListTaxonChildren.as_view()),
]
app_name = 'taxonomy'
