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
from django.urls import path

from hyphaeTaxonomy.views import TaxaListView, TaxonDetailView, NameCreateView, NamesListView, TaxonCreateView, IndexView

app_name = 'taxonomy'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('index/', IndexView.as_view(), name='index'),

    path('taxa/list', TaxaListView.as_view(), name='taxa-list'),
    path('taxon/create', TaxonCreateView.as_view(), name='taxon-create'),
    path('taxon/<slug:slug>', TaxonDetailView.as_view(), name='taxon-detail'),

    path('names/list', NamesListView.as_view(), name='name-list'),
    path('name/create', NameCreateView.as_view(), name='name-create'),
]
