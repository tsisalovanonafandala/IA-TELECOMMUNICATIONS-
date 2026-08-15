"""
Analyse d'un export Firebase de l'app "IA Télécommunication".

Format attendu (celui produit par exportAdminData() dans l'app) :
{
  "email@exemple.com": {
    "conversations": 12,
    "derniereActivite": "2026-08-10T14:32:00.000Z",
    "sessions": [
      {
        "id": "...",
        "preview": "...",
        "updatedAt": "...",
        "messages": [{"role": "user"|"assistant", "content": "..."}, ...]
      }
    ]
  },
  ...
}

Usage :
    python analyse_export_ia_telecom.py chemin/vers/export.json
"""

import json
import re
import sys
from collections import Counter
from datetime import datetime

# Mots vides à ignorer dans l'analyse des questions fréquentes
STOPWORDS = {
    "le", "la", "les", "de", "des", "du", "un", "une", "et", "en", "que",
    "qui", "quoi", "comment", "pourquoi", "est", "ce", "cette", "ces",
    "je", "tu", "il", "elle", "nous", "vous", "ils", "elles", "mon", "ma",
    "mes", "ton", "ta", "tes", "son", "sa", "ses", "pour", "avec", "sur",
    "dans", "au", "aux", "par", "sans", "plus", "moins", "tres", "peux",
    "peut", "faire", "fais", "svp", "stp", "bonjour", "salut", "merci",
    "ok", "oui", "non", "c'est", "j'ai", "a", "d", "l", "s", "y", "on",
}


def charger_export(chemin):
    with open(chemin, "r", encoding="utf-8") as f:
        return json.load(f)


def nettoyer_mots(texte):
    texte = texte.lower()
    mots = re.findall(r"[a-zàâäéèêëïîôöùûüç0-9\-]{3,}", texte)
    return [m for m in mots if m not in STOPWORDS]


def analyser(data):
    total_users = len(data)
    total_conversations = 0
    total_messages_user = 0
    total_messages_assistant = 0
    activite_par_mois = Counter()
    mots_questions = Counter()
    conversations_par_user = {}
    tailles_conversations = []

    for email, info in data.items():
        sessions = info.get("sessions", [])
        conversations_par_user[email] = len(sessions)
        total_conversations += len(sessions)

        for session in sessions:
            messages = session.get("messages", [])
            tailles_conversations.append(len(messages))

            updated_at = session.get("updatedAt")
            if updated_at:
                try:
                    dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    activite_par_mois[dt.strftime("%Y-%m")] += 1
                except ValueError:
                    pass

            for msg in messages:
                role = msg.get("role")
                content = msg.get("content", "") or ""
                if role == "user":
                    total_messages_user += 1
                    mots_questions.update(nettoyer_mots(content))
                elif role == "assistant":
                    total_messages_assistant += 1

    moyenne_taille = (
        sum(tailles_conversations) / len(tailles_conversations)
        if tailles_conversations else 0
    )

    return {
        "total_users": total_users,
        "total_conversations": total_conversations,
        "total_messages_user": total_messages_user,
        "total_messages_assistant": total_messages_assistant,
        "moyenne_messages_par_conversation": round(moyenne_taille, 1),
        "activite_par_mois": dict(sorted(activite_par_mois.items())),
        "mots_cles_frequents": mots_questions.most_common(20),
        "top_users": Counter(conversations_par_user).most_common(10),
    }


def afficher_rapport(resultats):
    print("=" * 55)
    print("RAPPORT D'ANALYSE — IA Télécommunication")
    print("=" * 55)
    print(f"Utilisateurs                 : {resultats['total_users']}")
    print(f"Conversations totales         : {resultats['total_conversations']}")
    print(f"Messages utilisateurs          : {resultats['total_messages_user']}")
    print(f"Messages assistant             : {resultats['total_messages_assistant']}")
    print(f"Moy. messages / conversation  : {resultats['moyenne_messages_par_conversation']}")

    print("\n--- Activité par mois ---")
    for mois, nb in resultats["activite_par_mois"].items():
        barre = "█" * nb
        print(f"{mois} : {barre} ({nb})")

    print("\n--- Top 10 utilisateurs les plus actifs ---")
    for email, nb in resultats["top_users"]:
        print(f"{email} : {nb} conversations")

    print("\n--- Mots-clés les plus fréquents dans les questions ---")
    for mot, freq in resultats["mots_cles_frequents"]:
        print(f"{mot:20s} {freq}")


def sauvegarder_json(resultats, chemin_sortie):
    with open(chemin_sortie, "w", encoding="utf-8") as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)
    print(f"\nRésultats détaillés sauvegardés dans : {chemin_sortie}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python analyse_export_ia_telecom.py chemin/vers/export.json")
        sys.exit(1)

    chemin_export = sys.argv[1]
    data = charger_export(chemin_export)
    resultats = analyser(data)
    afficher_rapport(resultats)
    sauvegarder_json(resultats, "resultats_analyse.json")
