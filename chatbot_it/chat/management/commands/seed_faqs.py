"""
Commande Django : python manage.py seed_faqs
Charge un jeu de FAQ IT de démarrage.
"""
from django.core.management.base import BaseCommand
from chat.models import FAQ


FAQS_DATA = [
    {
        'category': 'Réseau',
        'question': "Qu'est-ce qu'une adresse IP ?",
        'keywords': 'adresse ip, ip, internet protocol, ipv4, ipv6',
        'response': (
            "Une adresse IP (Internet Protocol) est un identifiant numérique unique attribué à "
            "chaque appareil connecté à un réseau informatique utilisant le protocole IP. "
            "Il en existe deux versions : IPv4 (ex : 192.168.1.1, composée de 4 nombres séparés "
            "par des points) et IPv6 (plus longue, en hexadécimal). L'adresse IP permet aux "
            "appareils de communiquer entre eux et d'être identifiés sur Internet ou un réseau local."
        ),
    },
    {
        'category': 'Réseau',
        'question': "Quelle est la différence entre HTTP et HTTPS ?",
        'keywords': 'http, https, ssl, tls, sécurité web, certificat',
        'response': (
            "HTTP (HyperText Transfer Protocol) est le protocole de base utilisé pour le transfert "
            "de données sur le web. HTTPS est sa version sécurisée : les données échangées entre "
            "le navigateur et le serveur sont chiffrées grâce à SSL/TLS. HTTPS protège contre "
            "l'interception des données (mots de passe, infos bancaires...) et nécessite un "
            "certificat SSL. Aujourd'hui, HTTPS est devenu la norme et est obligatoire pour le "
            "référencement sur Google."
        ),
    },
    {
        'category': 'Programmation',
        'question': "Qu'est-ce que la programmation orientée objet ?",
        'keywords': 'poo, oop, classe, objet, héritage, encapsulation, polymorphisme',
        'response': (
            "La programmation orientée objet (POO) est un paradigme de programmation basé sur le "
            "concept d'objets, qui contiennent des données (attributs) et du code (méthodes). "
            "Ses 4 piliers sont : \n"
            "1. **Encapsulation** : regrouper données et méthodes dans une classe.\n"
            "2. **Héritage** : créer de nouvelles classes à partir de classes existantes.\n"
            "3. **Polymorphisme** : utiliser une même interface pour différents types d'objets.\n"
            "4. **Abstraction** : masquer les détails complexes derrière une interface simple.\n"
            "Langages populaires : Java, Python, C++, C#."
        ),
    },
    {
        'category': 'Programmation',
        'question': "Qu'est-ce que Python ?",
        'keywords': 'python, langage, programmation, script',
        'response': (
            "Python est un langage de programmation interprété, de haut niveau, créé par Guido van "
            "Rossum en 1991. Il est apprécié pour sa syntaxe claire et lisible, sa polyvalence et "
            "sa large communauté. Python est utilisé dans de nombreux domaines : développement web "
            "(Django, Flask), data science (pandas, numpy), intelligence artificielle (TensorFlow, "
            "PyTorch), automatisation, scripts système et bien plus. C'est un excellent langage "
            "pour débuter en programmation."
        ),
    },
    {
        'category': 'Sécurité',
        'question': "Qu'est-ce qu'un pare-feu (firewall) ?",
        'keywords': 'pare-feu, firewall, sécurité, réseau, filtrage',
        'response': (
            "Un pare-feu (firewall) est un dispositif de sécurité réseau, matériel ou logiciel, qui "
            "surveille et contrôle le trafic entrant et sortant en se basant sur des règles de "
            "sécurité prédéfinies. Il agit comme une barrière entre un réseau interne sécurisé et "
            "des réseaux externes non fiables (comme Internet). Il bloque les connexions non "
            "autorisées et protège contre les attaques. Exemples : Windows Defender Firewall, "
            "iptables (Linux), pfSense."
        ),
    },
    {
        'category': 'Sécurité',
        'question': "Comment créer un mot de passe sécurisé ?",
        'keywords': 'mot de passe, password, sécurité, sécurisé, fort',
        'response': (
            "Un mot de passe sécurisé doit :\n"
            "- Contenir au moins 12 caractères\n"
            "- Mélanger majuscules, minuscules, chiffres et caractères spéciaux\n"
            "- Éviter les mots du dictionnaire, dates de naissance, noms\n"
            "- Être unique pour chaque service\n"
            "- Être changé en cas de fuite de données\n\n"
            "Conseil : utilisez un **gestionnaire de mots de passe** (Bitwarden, 1Password, "
            "KeePass) et activez la **double authentification (2FA)** quand c'est possible."
        ),
    },
    {
        'category': 'Hardware',
        'question': "Quelle est la différence entre RAM et ROM ?",
        'keywords': 'ram, rom, mémoire, vive, morte, hardware',
        'response': (
            "**RAM** (Random Access Memory) : mémoire vive, volatile (s'efface à l'extinction), "
            "rapide, utilisée pour stocker temporairement les données et programmes en cours "
            "d'exécution.\n\n"
            "**ROM** (Read-Only Memory) : mémoire morte, non-volatile (conservée sans alimentation), "
            "en lecture seule, utilisée pour stocker des programmes essentiels comme le BIOS."
        ),
    },
    {
        'category': 'Hardware',
        'question': "C'est quoi un SSD ?",
        'keywords': 'ssd, disque, stockage, hdd, ssd vs hdd',
        'response': (
            "Un SSD (Solid State Drive) est un dispositif de stockage qui utilise de la mémoire "
            "flash (sans pièces mobiles), contrairement aux disques durs traditionnels (HDD) qui "
            "utilisent des plateaux rotatifs. Avantages du SSD : vitesse de lecture/écriture "
            "beaucoup plus rapide, consommation moindre, silencieux, plus résistant aux chocs. "
            "Inconvénients : prix plus élevé au Go, durée de vie limitée par le nombre de cycles "
            "d'écriture."
        ),
    },
    {
        'category': 'Systèmes',
        'question': "Quelle est la différence entre Linux et Windows ?",
        'keywords': 'linux, windows, os, système exploitation, unix',
        'response': (
            "**Linux** : système d'exploitation open-source basé sur Unix, gratuit, hautement "
            "personnalisable, très utilisé sur les serveurs, populaire chez les développeurs. "
            "Existe en nombreuses distributions (Ubuntu, Debian, Fedora, Arch...).\n\n"
            "**Windows** : système propriétaire développé par Microsoft, payant, plus convivial "
            "pour le grand public, domine sur les PC de bureau, large compatibilité logicielle "
            "et avec les jeux."
        ),
    },
    {
        'category': 'Cloud',
        'question': "Qu'est-ce que le cloud computing ?",
        'keywords': 'cloud, computing, aws, azure, gcp, saas, paas, iaas',
        'response': (
            "Le cloud computing désigne la fourniture de services informatiques (serveurs, "
            "stockage, bases de données, logiciels, analytique) via Internet (« le cloud »). "
            "Il permet de payer à l'usage sans investir dans une infrastructure physique. "
            "Trois modèles principaux :\n"
            "- **IaaS** (Infrastructure as a Service) : ex. AWS EC2\n"
            "- **PaaS** (Platform as a Service) : ex. Heroku, Google App Engine\n"
            "- **SaaS** (Software as a Service) : ex. Gmail, Office 365\n\n"
            "Principaux fournisseurs : AWS (Amazon), Azure (Microsoft), Google Cloud."
        ),
    },
    {
        'category': 'Base de données',
        'question': "Quelle est la différence entre SQL et NoSQL ?",
        'keywords': 'sql, nosql, base de données, mongodb, mysql, postgresql',
        'response': (
            "**SQL** (relationnel) : données structurées en tables avec relations, schéma fixe, "
            "langage SQL standard. Exemples : MySQL, PostgreSQL, SQL Server, Oracle. Idéal pour "
            "les données structurées avec relations complexes (ERP, CRM, finance).\n\n"
            "**NoSQL** (non-relationnel) : flexible, sans schéma fixe, scalable horizontalement. "
            "Types : documents (MongoDB), clé-valeur (Redis), colonnes (Cassandra), graphes "
            "(Neo4j). Idéal pour Big Data, applications temps réel, données non structurées."
        ),
    },
    {
        'category': 'IA',
        'question': "Qu'est-ce que l'intelligence artificielle ?",
        'keywords': 'ia, intelligence artificielle, ai, machine learning, deep learning',
        'response': (
            "L'intelligence artificielle (IA) désigne l'ensemble des techniques permettant à des "
            "machines de simuler l'intelligence humaine : apprentissage, raisonnement, perception, "
            "résolution de problèmes. Sous-domaines :\n"
            "- **Machine Learning (ML)** : apprentissage à partir de données.\n"
            "- **Deep Learning** : ML utilisant des réseaux de neurones profonds.\n"
            "- **NLP** : traitement du langage naturel (ex. ChatGPT).\n"
            "- **Computer Vision** : reconnaissance d'images.\n\n"
            "Applications : assistants vocaux, recommandations, voitures autonomes, diagnostics "
            "médicaux."
        ),
    },
    {
        'category': 'Web',
        'question': "C'est quoi une API ?",
        'keywords': 'api, rest, application programming interface, endpoint, json',
        'response': (
            "Une API (Application Programming Interface) est un ensemble de règles et de protocoles "
            "permettant à deux logiciels de communiquer entre eux. Elle expose des fonctionnalités "
            "ou des données sans nécessiter de connaître l'implémentation interne.\n\n"
            "Types courants : **REST** (le plus populaire, basé sur HTTP), **GraphQL**, **SOAP**. "
            "Exemple : quand une app météo récupère les prévisions, elle appelle l'API d'un service "
            "météo qui renvoie les données (souvent en JSON)."
        ),
    },
    {
        'category': 'Général',
        'question': "Comment fonctionne ce chatbot ?",
        'keywords': 'chatbot, fonctionnement, comment marche, bot',
        'response': (
            "Ce chatbot fonctionne en deux étapes :\n"
            "1️⃣ **Recherche dans la FAQ** : il cherche d'abord votre question dans une base de "
            "connaissances IT préenregistrée par les administrateurs.\n"
            "2️⃣ **Appel à ChatGPT** : si aucune réponse n'est trouvée, il fait appel à l'API "
            "OpenAI (ChatGPT) pour générer une réponse personnalisée.\n\n"
            "Toutes vos conversations sont sauvegardées dans votre historique. Posez vos questions "
            "sur l'informatique : réseaux, programmation, sécurité, hardware, cloud, IA... 🚀"
        ),
    },
]


class Command(BaseCommand):
    help = "Charge un ensemble de FAQ IT par défaut dans la base de données."

    def handle(self, *args, **options):
        created = 0
        existed = 0
        for data in FAQS_DATA:
            faq, was_created = FAQ.objects.get_or_create(
                question=data['question'],
                defaults=data,
            )
            if was_created:
                created += 1
            else:
                existed += 1
        self.stdout.write(self.style.SUCCESS(
            f"✅ Terminé : {created} FAQ créées, {existed} déjà existantes."
        ))
