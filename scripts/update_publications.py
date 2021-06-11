import os
from os import listdir
from os.path import isfile, join

from hyphae import settings
from hyphaeLibrary.models import Literature, Document


def update_publications():
    literature = Literature.objects.all()

    for publication in literature:
        publication.save()


def update_documents():
    documents = Document.objects.all()

    for document in documents:
        document.save()


def create_documents():
    literature = Literature.objects.all()

    for publication in literature:
        doc = Document.objects.get(unique_identifier=publication.vanity)
        publication.document = doc
        publication.save()


def prune_unused_files():
    path = os.path.join(settings.MEDIA_ROOT, "uploads", "literature")
    files = [f for f in listdir(path) if isfile(join(path, f))]

    i = 0
    wd = os.getcwd()
    os.chdir(path)
    for file in files:
        identifier = os.path.splitext(file)[0]
        document = Document.objects.filter(unique_identifier=identifier)
        if not document.exists():
            i += 1
            new_name = f"prune-{i}.pdf"
            print(file)
            os.rename(file, new_name)

    os.chdir(wd)
