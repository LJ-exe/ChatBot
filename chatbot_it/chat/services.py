"""
Service métier du chatbot.
1. Cherche d'abord dans la base FAQ (matching mots-clés + similarité).
2. Si rien trouvé, appelle l'API OpenAI (ChatGPT).
"""
import logging
import re
from difflib import SequenceMatcher

from django.conf import settings
from django.db.models import Q

from .models import FAQ

logger = logging.getLogger(__name__)


# Prompt système pour orienter ChatGPT sur l'IT
SYSTEM_PROMPT = (
    "Tu es un assistant expert en informatique (IT). "
    "Tu réponds en français de manière claire, pédagogique et concise "
    "à des questions sur les domaines : réseaux, programmation, systèmes d'exploitation, "
    "matériel informatique, cybersécurité, bases de données, cloud computing, "
    "intelligence artificielle et plus généralement tout ce qui concerne l'informatique. "
    "Si la question n'est pas liée à l'IT, indique poliment que tu es spécialisé en informatique. "
    "Limite tes réponses à 200 mots maximum sauf si plus de détails sont nécessaires."
)

# Mots vides français à ignorer dans la recherche par mots-clés
STOPWORDS = {
    'avec', 'alors', 'aussi', 'cela', 'cette', 'comme', 'dans', 'donc', 'elle',
    'entre', 'etre', 'être', 'comment', 'dont', 'fait', 'faire', 'leur', 'leurs',
    'mais', 'meme', 'même', 'notre', 'nous', 'plus', 'pour', 'pourquoi', 'quand',
    'quel', 'quelle', 'quels', 'quelles', 'sans', 'sera', 'sont', 'tout', 'tous',
    'toute', 'toutes', 'vous', 'votre', 'vos', 'difference', 'différence', 'cest',
    'est', 'que', 'qui', 'une', 'des', 'les', 'mon', 'son', 'ses', 'aux', 'sur',
}


def _normalize(text: str) -> str:
    """Normalise un texte : minuscules, suppression ponctuation, espaces."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def _similarity(a: str, b: str) -> float:
    """Calcule la similarité entre deux chaînes (0.0 à 1.0)."""
    return SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


def search_faq(question: str, sim_threshold: float = 0.75, kw_threshold: float = 0.6):
    """
    Cherche une FAQ correspondante.

    Stratégie unifiée : pour chaque FAQ active, on calcule deux scores :
      - similarité textuelle (SequenceMatcher)
      - ratio de mots-clés significatifs partagés
    Une FAQ est retenue si :
      - similarité >= sim_threshold (match quasi-exact, ex: paraphrase légère)
      - OU score mots-clés >= kw_threshold AVEC au moins 2 mots significatifs partagés
        (1 seul mot suffit s'il n'y a qu'un mot dans la question)

    Retourne la meilleure FAQ trouvée ou None.
    """
    normalized_q = _normalize(question)
    if not normalized_q:
        return None

    active_faqs = FAQ.objects.filter(is_active=True)
    if not active_faqs.exists():
        return None

    # Mots significatifs (hors stopwords) de la question
    # On garde aussi les mots de 3 lettres (utiles pour SSD, RAM, ROM, IPv, etc.)
    q_words = [
        w for w in normalized_q.split()
        if len(w) >= 3 and w not in STOPWORDS
    ]
    min_matches = 2 if len(q_words) >= 2 else 1

    best_faq = None
    best_combined_score = 0.0
    best_log = ""

    for faq in active_faqs:
        # Similarité textuelle brute
        sim = _similarity(question, faq.question)

        # Score basé sur les mots-clés significatifs
        faq_text = _normalize(f"{faq.question} {faq.keywords}")
        kw_matches = sum(1 for w in q_words if w in faq_text) if q_words else 0
        kw_ratio = kw_matches / len(q_words) if q_words else 0.0

        # Conditions de validation : on exige au moins 1 mot-clé partagé même
        # pour la similarité haute, afin d'éviter les faux positifs dus aux
        # préfixes communs comme "Qu'est-ce que ...".
        is_high_sim = sim >= sim_threshold and kw_matches >= 1
        is_good_kw = kw_ratio >= kw_threshold and kw_matches >= min_matches

        if not (is_high_sim or is_good_kw):
            continue

        # Score combiné pour comparer les candidats valides
        combined = max(sim, kw_ratio)
        if combined > best_combined_score:
            best_combined_score = combined
            best_faq = faq
            best_log = (
                f"sim={sim:.2f}, kw_ratio={kw_ratio:.2f} ({kw_matches}/{len(q_words)}) "
                f"→ {faq.question[:60]}"
            )

    if best_faq:
        logger.info(f"FAQ retenue : {best_log}")
    return best_faq


def ask_openai(question: str, conversation_history: list = None) -> str:
    """
    Appelle l'API d'IA (OpenAI, Groq, ou tout fournisseur compatible).
    Détecte automatiquement le fournisseur en fonction du préfixe de la clé.
    """
    api_key = settings.OPENAI_API_KEY
    if not api_key or 'votre' in api_key.lower():
        return (
            "⚠️ La clé API n'est pas configurée. "
            "Je ne trouve pas de réponse dans ma base de connaissances. "
            "Veuillez contacter un administrateur pour ajouter cette FAQ ou configurer l'API."
        )

    # Détection automatique du fournisseur
    base_url = getattr(settings, 'OPENAI_BASE_URL', '') or None
    if not base_url and api_key.startswith('gsk_'):
        base_url = 'https://api.groq.com/openai/v1'

    messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}]
    if conversation_history:
        messages_payload.extend(conversation_history)
    messages_payload.append({"role": "user", "content": question})

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages_payload,
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except ImportError:
        logger.error("Le package openai n'est pas installe.")
        return "⚠️ Le module openai n'est pas installé sur le serveur."
    except Exception as e:
        logger.exception("Erreur lors de l'appel a l'API d'IA")
        return (
            f"⚠️ Désolé, je n'ai pas pu obtenir une réponse via l'IA. "
            f"Erreur : {str(e)[:120]}"
     )


def build_conversation_history(user, max_messages: int = 5) -> list:
    """
    Construit l'historique de conversation des N derniers échanges
    de l'utilisateur, au format attendu par l'API OpenAI.
    Cela permet au bot de maintenir le contexte (mémoire conversationnelle).
    """
    from .models import Message
    recent = Message.objects.filter(user=user).order_by('-date')[:max_messages]
    history = []
    # On parcourt du plus ancien au plus récent
    for msg in reversed(list(recent)):
        history.append({"role": "user", "content": msg.question})
        history.append({"role": "assistant", "content": msg.response})
    return history


def get_bot_response(question: str, user=None):
    """
    Point d'entrée principal du chatbot.

    Args:
        question: La question de l'utilisateur.
        user: L'utilisateur connecté (pour récupérer son historique conversationnel).
              Si None, pas de contexte (utile pour des appels sans utilisateur).

    Retourne un tuple : (response_text, source, faq_object_or_none).
    source ∈ {'FAQ', 'OPENAI', 'ERROR'}
    """
    if not question or not question.strip():
        return ("Veuillez poser une question.", 'ERROR', None)

    # 1) Recherche FAQ
    faq = search_faq(question)
    if faq:
        return (faq.response, 'FAQ', faq)

    # 2) Fallback OpenAI avec contexte conversationnel
    history = build_conversation_history(user) if user else None
    response = ask_openai(question, conversation_history=history)
    source = 'OPENAI' if not response.startswith('⚠️') else 'ERROR'
    return (response, source, None)
