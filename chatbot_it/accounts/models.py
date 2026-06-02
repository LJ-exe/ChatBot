"""
Modèles pour la gestion des utilisateurs et administrateurs.
Basé sur le diagramme de classes : User et Admin.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé.
    Représente la classe User du diagramme.
    Champs : Id (auto), Name, LastName, Age, UserName, Pswd_hash (password), Email.
    Le rôle 'is_staff' / 'is_superuser' distingue Admin et User.
    """
    name = models.CharField("Prénom", max_length=100)
    last_name = models.CharField("Nom", max_length=100)
    age = models.PositiveIntegerField("Âge", null=True, blank=True)
    email = models.EmailField("Email", unique=True)

    # On utilise username comme identifiant
    REQUIRED_FIELDS = ['email', 'name', 'last_name']

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.name} {self.last_name})"

    @property
    def full_name(self):
        return f"{self.name} {self.last_name}".strip() or self.username

    @property
    def is_admin_role(self):
        """Renvoie True si l'utilisateur est un administrateur."""
        return self.is_staff or self.is_superuser
