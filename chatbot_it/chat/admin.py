"""Configuration admin Django pour les modèles chat."""
from django.contrib import admin
from .models import FAQ, Message, ConvHistory, MessageFeedback


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('question', 'response', 'keywords')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_short', 'source', 'date')
    list_filter = ('source', 'date')
    search_fields = ('question', 'response', 'user__username')

    def question_short(self, obj):
        return obj.question[:60] + ('...' if len(obj.question) > 60 else '')
    question_short.short_description = 'Question'


@admin.register(ConvHistory)
class ConvHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
    search_fields = ('user__username',)


@admin.register(MessageFeedback)
class MessageFeedbackAdmin(admin.ModelAdmin):
    list_display = ('message', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('message__question', 'comment')
