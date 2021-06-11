from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from django.db.models.signals import pre_save

from utils.database import generate_unique_vanity


def give_default_username(sender, instance, *args, **kwargs):
    """
    Add a default username.
    """

    instance.username = instance.email


class HyphaeUser(AbstractUser):
    REQUIRED_FIELDS = ['first_name', 'last_name']
    USERNAME_FIELD = 'email'

    profile_picture = models.ImageField(null=True, blank=True, upload_to="images/profile/", verbose_name="Profile picture")
    bio = models.TextField(max_length=512, null=True, blank=True, verbose_name="Bio", help_text="About you")
    last_login = models.DateTimeField(auto_now_add=True, verbose_name="Last login")
    organizations = models.CharField(max_length=200, verbose_name='Organizations', help_text='Separate organisations with a semicolon \';\'')
    orcid_id = models.CharField(max_length=20, verbose_name='Orcid ID')
    location = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(unique=True, verbose_name='Email', help_text='Email adress')
    vanity = models.SlugField(null=True, verbose_name="Vanity")

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def save(self, *args, **kwargs):
        if not self.vanity:
            self.vanity = generate_unique_vanity(5, 10, HyphaeUser)
        return super().save(*args, **kwargs)


pre_save.connect(give_default_username, sender=HyphaeUser)  # Signal se déclanchant avant l'enregistrement dans la base de donnée
