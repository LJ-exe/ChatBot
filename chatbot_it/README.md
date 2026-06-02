# 🤖 Chatbot IT — Application Django Complète 

Application web Django d'un chatbot spécialisé en informatique (IT), avec :
-  Espace utilisateur (inscription, chat, historique, feedback)
-  Panneau admin (gestion utilisateurs, FAQ, conversations, statistiques)
-  Intégration **OpenAI / ChatGPT** comme fallback quand aucune FAQ ne correspond
-  Modèles basés sur le diagramme de classes fourni (User, Admin, FAQ, Message, Conv_History)

---

##  Améliorations 

 
1. **Mémoire conversationnelle** — Le bot se souvient des 5 derniers échanges et peut comprendre des questions de suivi .
2. **Rate limiting** — Maximum 30 messages/heure par utilisateur (anti-abus, protège votre budget OpenAI).
3. **Système de feedback** — Les utilisateurs notent chaque réponse. Les admins voient les réponses ChatGPT mal notées et peuvent les **convertir en FAQ d'un clic**.
4.  **Suggestions de questions rapides** — Les nouveaux utilisateurs voient 4 questions cliquables basées sur les FAQ les plus populaires.
5.  **Mode sombre** — Toggle dans la navbar, persisté en `localStorage`, compatible Bootstrap 5.3 + highlight.js.

---

## 📐 Architecture

```
chatbot_it/
├── chatbot_it/              # Configuration Django (settings, urls)
├── accounts/                # App : utilisateurs & admins
├── chat/                    # App : chatbot, FAQ, historique, feedback
│   ├── models.py            # FAQ, Message, ConvHistory, MessageFeedback
│   ├── services.py          # 🧠 Recherche FAQ + appel OpenAI avec contexte
│   ├── views.py             # Vues utilisateurs + admin + rate limiting
│   └── management/commands/seed_faqs.py
├── templates/               # Templates HTML (Bootstrap 5.3 + dark mode)
├── static/css/style.css     # Styles (light + dark)
├── manage.py
├── requirements.txt
└── .env.example
```

---

## 🧩 Modèles (mapping avec le diagramme)

| Diagramme       | Modèle Django                          | Champs principaux |
|-----------------|----------------------------------------|-------------------|
| **User**        | `accounts.User`                        | username, name, last_name, age, email, password |
| **Admin**       | `accounts.User` avec `is_staff=True`   | (même modèle, rôle distingué par `is_staff`) |
| **FAQ**         | `chat.FAQ`                             | question, response, keywords, category |
| **Message**     | `chat.Message`                         | user, question, response, source, date |
| **Conv_History**| `chat.ConvHistory`                     | user, message, created_at |
| *(nouveau)*     | `chat.MessageFeedback`                 | message, rating (👍/👎), comment |

---

## 🔄 Comment fonctionne le chatbot (v2)

```
Utilisateur pose une question
        │
        ▼
┌────────────────────────────┐
│ 1. Recherche FAQ           │
│  - Similarité texte        │
│  - Match mots-clés         │
│  - Filtre stopwords        │
└──────┬─────────────────────┘
       │ trouvé ? ──► OUI ──► Réponse FAQ
       │
       NON
       │
       ▼
┌────────────────────────────┐
│ 2. Construction contexte   │ ← NOUVEAU : mémoire des 5 derniers
│    conversationnel         │   échanges de l'utilisateur
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ 3. Appel API OpenAI        │
│  - system: prompt IT       │
│  - history: messages       │
│  - user: question actuelle │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│ 4. Sauvegarde Message      │
│    + ConvHistory           │
└──────┬─────────────────────┘
       │
       ▼
Réponse au front (JSON)
+ utilisateur peut donner 👍/👎
```

---

## 🚀 Installation

### 1. Cloner / extraire le projet

```bash
cd chatbot_it
```

### 2. Environnement virtuel + dépendances

```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration

```bash
cp .env.example .env
```

Éditez `.env` et ajoutez votre clé OpenAI (obtenez-la sur https://platform.openai.com/api-keys) :

```env
SECRET_KEY=une_clef_secrete_unique_longue_aleatoire
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
OPENAI_API_KEY=sk-votre_vraie_cle_openai_ici
OPENAI_MODEL=gpt-3.5-turbo
```

### 4. Base de données + données initiales

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser     # Compte admin
python manage.py seed_faqs           # 14 FAQ IT par défaut
```

### 5. Lancement

```bash
python manage.py runserver
```

Ouvrez : **http://127.0.0.1:8000/**

---

## 🎮 Utilisation

### Côté utilisateur
- 💬 **Chat** (`/chat/`) : posez vos questions IT
  - Cliquez sur les **suggestions** pour démarrer rapidement
  - Donnez votre avis (**👍/👎**) sur chaque réponse
  - Le bot maintient le **contexte** de votre conversation
- 🕘 **Historique** (`/chat/history/`) : recherche dans vos anciens échanges
- 👤 **Profil** : modifier vos infos
- 🌙 **Bouton lune/soleil** en haut à droite pour basculer le thème

### Côté admin
- 📊 **Dashboard** (`/chat/admin-panel/`) : stats globales + section **« Opportunités »** listant les réponses ChatGPT mal notées (avec bouton « En faire une FAQ »)
- 👥 **Utilisateurs** : CRUD + voir l'historique d'un utilisateur
- 📚 **FAQ** : CRUD (création possible depuis un message ChatGPT existant via `?from_message=<id>`)
- 💬 **Conversations** : vue globale avec filtres par **source** ET par **feedback** (👍 ou 👎)

---

## 🧪 Test du bot

**Questions FAQ (matchent les données seed) :**
- « Qu'est-ce qu'une adresse IP ? »
- « Différence entre SQL et NoSQL »
- « Comment créer un mot de passe sécurisé ? »

**Fallback ChatGPT (avec contexte) :**
- 1ère question : « Qu'est-ce que Docker ? »
- 2ème question (sans re-mentionner Docker) : « Et comment l'installer sur Ubuntu ? » → le bot comprend grâce au contexte !

---

## 🔧 Personnalisation

| Quoi | Où |
|------|-----|
| Modèle OpenAI (gpt-4o-mini, gpt-4, etc.) | `.env` → `OPENAI_MODEL` |
| Seuils de similarité FAQ | `chat/services.py` → `search_faq(sim_threshold, kw_threshold)` |
| Prompt système ChatGPT | `chat/services.py` → `SYSTEM_PROMPT` |
| Taille du contexte conversationnel | `chat/services.py` → `build_conversation_history(max_messages=5)` |
| Limite de taux | `chat/views.py` → `@ratelimit(rate='30/h')` |
| Nombre de suggestions | `chat/views.py` → `get_suggestions(limit=4)` |
| Styles (couleurs, dark mode) | `static/css/style.css` |

---

## 🛡️ Sécurité en production

1. `DEBUG=False` dans `.env`
2. `ALLOWED_HOSTS` avec votre domaine réel
3. PostgreSQL/MySQL au lieu de SQLite
4. `collectstatic` + serveur statique (nginx)
5. HTTPS (certbot)
6. Ne committez jamais `.env` (déjà dans `.gitignore`)

---

## 📊 Comparatif v1 → v2

| Fonctionnalité | v1 | v2 |
|----------------|----|----|
| Recherche FAQ | ✅ basique | ✅ avec stopwords + double critère |
| Appel OpenAI | ✅ question seule | ✅ + **contexte des 5 derniers échanges** |
| Rendu des réponses | texte brut + `<br>` | ✅ **markdown + coloration code** |
| Feedback utilisateur | ❌ | ✅ **👍/👎 + commentaire** |
| Suggestions | ❌ | ✅ **4 questions populaires** |
| Mode sombre | ❌ | ✅ **toggle navbar** |
| Rate limiting | ❌ | ✅ **30/h par user** |
| Tableau admin | stats simples | ✅ + **« Opportunités » de FAQ** |
| Conversion AI→FAQ | ❌ | ✅ **un clic depuis un message** |

---

## 📜 Licence

Projet pédagogique — libre de réutilisation.
