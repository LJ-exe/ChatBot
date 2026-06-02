"""
Vues pour l'application chat.
- Utilisateurs : dashboard avec chat, historique, feedback
- Admins : panneau de gestion (utilisateurs, FAQ, conversations, feedback)
"""
from django.contrib import messages as django_messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

from accounts.forms import AdminUserEditForm
from .forms import FAQForm, ChatMessageForm
from .models import FAQ, Message, ConvHistory, MessageFeedback
from .services import get_bot_response

User = get_user_model()


def is_admin(user):
    """Test si user est admin."""
    return user.is_authenticated and user.is_admin_role


def get_suggestions(limit=4):
    """
    Retourne les questions FAQ les plus populaires (basées sur l'usage).
    Si pas assez d'historique, complète avec des FAQ aléatoires actives.
    """
    # FAQ les plus utilisées
    top_faqs = (
        FAQ.objects.filter(is_active=True, used_in_messages__isnull=False)
        .annotate(usage=Count('used_in_messages'))
        .order_by('-usage')[:limit]
    )
    suggestions = list(top_faqs.values_list('question', flat=True))

    # Compléter avec des FAQ aléatoires si besoin
    if len(suggestions) < limit:
        already = set(suggestions)
        extras = FAQ.objects.filter(is_active=True).exclude(question__in=already)[:limit - len(suggestions)]
        suggestions.extend(extras.values_list('question', flat=True))

    return suggestions


# ===========================================================================
# Vues UTILISATEUR
# ===========================================================================

@login_required
def dashboard(request):
    """
    Page principale du chat pour l'utilisateur.
    Affiche l'interface de chat avec les derniers messages et suggestions.
    """
    if request.user.is_admin_role:
        return redirect('chat:admin_dashboard')

    recent_messages = Message.objects.filter(user=request.user).order_by('-date')[:10]
    recent_messages = list(reversed(recent_messages))

    return render(request, 'chat/dashboard.html', {
        'form': ChatMessageForm(),
        'recent_messages': recent_messages,
        'suggestions': get_suggestions(),
    })


@login_required
@require_POST
@ratelimit(key='user', rate='30/h', method='POST', block=False)
def send_message(request):
    """
    Endpoint AJAX pour envoyer une question au bot.
    Retourne du JSON : la question et la réponse du bot.
    Rate limit : 30 messages par heure par utilisateur.
    """
    # Vérification du rate limit
    if getattr(request, 'limited', False):
        return JsonResponse({
            'error': "Vous avez atteint la limite de 30 messages par heure. "
                     "Merci de patienter avant de poser de nouvelles questions."
        }, status=429)

    form = ChatMessageForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'Question invalide.'}, status=400)

    question = form.cleaned_data['question'].strip()

    # Obtenir la réponse via le service (avec contexte conversationnel)
    response_text, source, faq = get_bot_response(question, user=request.user)

    # Créer le Message
    message = Message.objects.create(
        user=request.user,
        question=question,
        response=response_text,
        source=source,
        faq_used=faq,
    )
    # Créer l'entrée d'historique
    ConvHistory.objects.create(user=request.user, message=message)

    return JsonResponse({
        'success': True,
        'message_id': message.id,
        'question': message.question,
        'response': message.response,
        'source': message.get_source_display(),
        'source_code': message.source,
        'date': message.date.strftime('%d/%m/%Y %H:%M'),
    })


@login_required
@require_POST
def submit_feedback(request, message_id):
    """
    Enregistre un feedback 👍/👎 pour un message.
    Endpoint AJAX retournant du JSON.
    """
    message = get_object_or_404(Message, pk=message_id, user=request.user)
    try:
        rating = int(request.POST.get('rating', 0))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Note invalide.'}, status=400)

    if rating not in (1, -1):
        return JsonResponse({'error': 'Note invalide.'}, status=400)

    comment = request.POST.get('comment', '').strip()[:500]

    # update_or_create pour permettre de changer d'avis
    feedback, created = MessageFeedback.objects.update_or_create(
        message=message,
        defaults={'rating': rating, 'comment': comment},
    )

    return JsonResponse({
        'success': True,
        'rating': feedback.rating,
        'created': created,
    })


@login_required
def history(request):
    """Historique complet des messages de l'utilisateur connecté."""
    search = request.GET.get('q', '').strip()
    messages_qs = Message.objects.filter(user=request.user).select_related('feedback')

    if search:
        messages_qs = messages_qs.filter(
            Q(question__icontains=search) | Q(response__icontains=search)
        )

    paginator = Paginator(messages_qs.order_by('-date'), 15)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'chat/history.html', {
        'page_obj': page,
        'search': search,
    })


@login_required
def delete_message(request, pk):
    """Supprimer un message de son propre historique."""
    msg = get_object_or_404(Message, pk=pk, user=request.user)
    if request.method == 'POST':
        msg.delete()
        django_messages.success(request, "Message supprimé de votre historique.")
    return redirect('chat:history')


# ===========================================================================
# Vues ADMIN
# ===========================================================================

@user_passes_test(is_admin, login_url='accounts:login')
def admin_dashboard(request):
    """Tableau de bord administrateur avec statistiques."""
    stats = {
        'total_users': User.objects.filter(is_staff=False).count(),
        'total_admins': User.objects.filter(is_staff=True).count(),
        'total_messages': Message.objects.count(),
        'total_faqs': FAQ.objects.count(),
        'active_faqs': FAQ.objects.filter(is_active=True).count(),
        'messages_from_faq': Message.objects.filter(source='FAQ').count(),
        'messages_from_ai': Message.objects.filter(source='OPENAI').count(),
        'positive_feedback': MessageFeedback.objects.filter(rating=1).count(),
        'negative_feedback': MessageFeedback.objects.filter(rating=-1).count(),
    }
    recent_messages = Message.objects.select_related('user').order_by('-date')[:10]
    top_users = (
        User.objects.filter(is_staff=False)
        .annotate(msg_count=Count('messages'))
        .order_by('-msg_count')[:5]
    )

    # Réponses ChatGPT mal notées (opportunités de FAQ)
    bad_ai_responses = (
        Message.objects.filter(source='OPENAI', feedback__rating=-1)
        .select_related('user', 'feedback')
        .order_by('-feedback__created_at')[:5]
    )

    return render(request, 'admin_panel/dashboard.html', {
        'stats': stats,
        'recent_messages': recent_messages,
        'top_users': top_users,
        'bad_ai_responses': bad_ai_responses,
    })


# --- Gestion des utilisateurs ---

@user_passes_test(is_admin)
def admin_users_list(request):
    search = request.GET.get('q', '').strip()
    users_qs = User.objects.all()
    if search:
        users_qs = users_qs.filter(
            Q(username__icontains=search) | Q(email__icontains=search) |
            Q(name__icontains=search) | Q(last_name__icontains=search)
        )
    users_qs = users_qs.annotate(msg_count=Count('messages')).order_by('-date_joined')
    paginator = Paginator(users_qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/users_list.html', {
        'page_obj': page, 'search': search,
    })


@user_passes_test(is_admin)
def admin_user_edit(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            django_messages.success(request, f"Utilisateur {user_obj.username} mis à jour.")
            return redirect('chat:admin_users_list')
    else:
        form = AdminUserEditForm(instance=user_obj)
    return render(request, 'admin_panel/user_edit.html', {
        'form': form, 'user_obj': user_obj,
    })


@user_passes_test(is_admin)
def admin_user_delete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if user_obj == request.user:
        django_messages.error(request, "Vous ne pouvez pas supprimer votre propre compte.")
        return redirect('chat:admin_users_list')
    if request.method == 'POST':
        username = user_obj.username
        user_obj.delete()
        django_messages.success(request, f"Utilisateur {username} supprimé.")
        return redirect('chat:admin_users_list')
    return render(request, 'admin_panel/user_confirm_delete.html', {'user_obj': user_obj})


@user_passes_test(is_admin)
def admin_user_history(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    messages_qs = Message.objects.filter(user=user_obj).select_related('feedback').order_by('-date')
    paginator = Paginator(messages_qs, 15)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/user_history.html', {
        'user_obj': user_obj, 'page_obj': page,
    })


# --- Gestion des FAQ ---

@user_passes_test(is_admin)
def admin_faq_list(request):
    search = request.GET.get('q', '').strip()
    faqs = FAQ.objects.all()
    if search:
        faqs = faqs.filter(
            Q(question__icontains=search) | Q(response__icontains=search) |
            Q(keywords__icontains=search) | Q(category__icontains=search)
        )
    paginator = Paginator(faqs.order_by('-created_at'), 15)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/faq_list.html', {
        'page_obj': page, 'search': search,
    })


@user_passes_test(is_admin)
def admin_faq_create(request):
    """
    Créer une FAQ.
    Peut être pré-remplie depuis un message ChatGPT existant (via query params)
    pour faciliter la conversion réponse-AI → FAQ.
    """
    initial = {}
    from_msg_id = request.GET.get('from_message')
    if from_msg_id:
        try:
            msg = Message.objects.get(pk=from_msg_id)
            initial = {'question': msg.question, 'response': msg.response}
        except Message.DoesNotExist:
            pass

    if request.method == 'POST':
        form = FAQForm(request.POST)
        if form.is_valid():
            faq = form.save()
            django_messages.success(request, f"FAQ « {faq.question[:50]}... » créée.")
            return redirect('chat:admin_faq_list')
    else:
        form = FAQForm(initial=initial)
    return render(request, 'admin_panel/faq_form.html', {
        'form': form, 'title': 'Nouvelle FAQ',
    })


@user_passes_test(is_admin)
def admin_faq_edit(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == 'POST':
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            django_messages.success(request, "FAQ mise à jour.")
            return redirect('chat:admin_faq_list')
    else:
        form = FAQForm(instance=faq)
    return render(request, 'admin_panel/faq_form.html', {
        'form': form, 'title': 'Modifier la FAQ', 'faq': faq,
    })


@user_passes_test(is_admin)
def admin_faq_delete(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == 'POST':
        faq.delete()
        django_messages.success(request, "FAQ supprimée.")
        return redirect('chat:admin_faq_list')
    return render(request, 'admin_panel/faq_confirm_delete.html', {'faq': faq})


# --- Consultation des conversations globales ---

@user_passes_test(is_admin)
def admin_conversations(request):
    """Toutes les conversations (tous utilisateurs), avec filtres."""
    search = request.GET.get('q', '').strip()
    source = request.GET.get('source', '').strip()
    feedback = request.GET.get('feedback', '').strip()

    msgs = Message.objects.select_related('user', 'faq_used', 'feedback')
    if search:
        msgs = msgs.filter(
            Q(question__icontains=search) | Q(response__icontains=search) |
            Q(user__username__icontains=search)
        )
    if source in ('FAQ', 'OPENAI', 'ERROR'):
        msgs = msgs.filter(source=source)
    if feedback == 'positive':
        msgs = msgs.filter(feedback__rating=1)
    elif feedback == 'negative':
        msgs = msgs.filter(feedback__rating=-1)

    paginator = Paginator(msgs.order_by('-date'), 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/conversations.html', {
        'page_obj': page, 'search': search, 'source': source, 'feedback': feedback,
    })
