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

from hyphaeLibrary.views import LiteratureListView, LiteratureCreateView, LiteratureUpdateView, LiteratureDetailView, LibraryIndexView, LiteratureSearchView, LiteratureAdvancedSearchView

app_name = 'library'

urlpatterns = [
    path('', LibraryIndexView.as_view(), name='index'),
    path('index/', LibraryIndexView.as_view(), name='index'),
    path('literature/list/', LiteratureListView.as_view(), name='literature-list'),
    path('literature/advanced-search/', LiteratureAdvancedSearchView.as_view(), name='literature-advanced-search'),
    path('literature/search/<str:query>/', LiteratureSearchView.as_view(), name='literature-search'),
    path('literature/modify/<slug:vanity>/', LiteratureUpdateView.as_view(), name='literature-update'),
    path('literature/detail/<slug:vanity>/', LiteratureDetailView.as_view(), name='literature-detail'),
    path('literature/create/', LiteratureCreateView.as_view(), name='literature-create'),
]
