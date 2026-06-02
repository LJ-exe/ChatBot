"""
Modèles du chatbot basés sur le diagramme de classes :
- FAQ : base de connaissances Question/Réponse
- Message : échange utilisateur <-> bot
- Conv_History : historique des conversations d'un utilisateur
"""
from django.conf import settings
from django.db import models


class FAQ(models.Model):
    """
    Base de connaissances : questions fréquentes et leurs réponses.
    Classe FAQ du diagramme : Id, Question, response.
    """
    question = models.CharField("Question", max_length=500)
    response = models.TextField("Réponse")
    keywords = models.CharField(
        "Mots-clés",
        max_length=500,
        blank=True,
        help_text="Mots-clés séparés par des virgules pour faciliter la recherche"
    )
    category = models.CharField(
        "Catégorie",
        max_length=100,
        default='Général',
        help_text="Ex: Réseau, Hardware, Software, Sécurité..."
    )
    is_active = models.BooleanField("Active", default=True)
    created_at = models.DateTimeField("Créée le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifiée le", auto_now=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['-created_at']

    def __str__(self):
        return self.question[:80]


class Message(models.Model):
    """
    Représente un échange : question de l'utilisateur + réponse du bot.
    Classe Message du diagramme : Id, user_id, Question, response, Date.
    """
    SOURCE_CHOICES = [
        ('FAQ', 'Base de connaissances FAQ'),
        ('OPENAI', 'API ChatGPT'),
        ('ERROR', 'Erreur'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Utilisateur"
    )
    question = models.TextField("Question")
    response = models.TextField("Réponse")
    source = models.CharField(
        "Source de la réponse",
        max_length=10,
        choices=SOURCE_CHOICES,
        default='FAQ'
    )
    faq_used = models.ForeignKey(
        FAQ,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='used_in_messages',
        verbose_name="FAQ utilisée"
    )
    date = models.DateTimeField("Date", auto_now_add=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date.strftime('%d/%m/%Y %H:%M')}"


class ConvHistory(models.Model):
    """
    Historique des conversations.
    Classe Conv_History du diagramme : user_id, id_message.
    Permet de retrouver tout l'historique des messages d'un utilisateur.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conv_history',
        verbose_name="Utilisateur"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history_entries',
        verbose_name="Message"
    )
    created_at = models.DateTimeField("Date", auto_now_add=True)

    class Meta:
        verbose_name = "Historique de conversation"
        verbose_name_plural = "Historiques de conversations"
        ordering = ['-created_at']
        unique_together = ('user', 'message')

    def __str__(self):
        return f"Historique #{self.id} - {self.user.username}"


class MessageFeedback(models.Model):
    """
    Évaluation 👍/👎 d'un message par l'utilisateur.
    Permet aux admins de détecter les réponses ChatGPT à transformer en FAQ.
    """
    RATING_CHOICES = [
        (1, '👍 Utile'),
        (-1, '👎 Pas utile'),
    ]
    message = models.OneToOneField(
        Message,
        on_delete=models.CASCADE,
        related_name='feedback',
        verbose_name="Message"
    )
    rating = models.IntegerField("Note", choices=RATING_CHOICES)
    comment = models.TextField("Commentaire", blank=True)
    created_at = models.DateTimeField("Date", auto_now_add=True)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_rating_display()} - {self.message}"
