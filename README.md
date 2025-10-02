# 🏛️ Assistant Juridique Marocain - API RAG Multi-Agents

Une API FastAPI avancée utilisant un système RAG (Retrieval-Augmented Generation) multi-agents pour fournir une assistance juridique basée sur les lois marocaines.

## 🎯 Fonctionnalités

- **Système RAG hybride** : Combinaison de recherche sémantique (FAISS) et lexicale (BM25)
- **Architecture multi-agents** : Agents spécialisés par domaine juridique
- **Routage intelligent** : Dispatcher automatique vers les agents pertinents
- **API REST complète** : Endpoints spécialisés et génériques
- **Support multilingue** : Optimisé pour l'arabe avec modèle LaBSE
- **Monitoring intégré** : Logging et statistiques en temps réel

## 📚 Corpus Juridique

Le système indexe **477 articles** issus de **6 textes juridiques marocains** :

| Loi | Articles | Description |
|-----|----------|-------------|
| الدستور المغربي 2011 | 28 | Constitution marocaine |
| مجموعة القانون الجنائي | 180 | Code pénal et procédure pénale |
| قانون المسطرة المدنية | 39 | Code de procédure civile |
| قانون التجمعات العمومية | 50 | Loi sur les rassemblements publics |
| قانون الصحافة والنشر 2016 | 17 | Loi sur la presse et l'édition |
| القانون الدولي الإنساني | 163 | Droit international humanitaire |

## 🏗️ Architecture

```
legal_rag_api/
├── app/
│   ├── agents/           # Agents spécialisés par domaine
│   │   ├── base_agent.py
│   │   ├── constitution_agent.py
│   │   ├── penal_agent.py
│   │   ├── civil_agent.py
│   │   ├── media_agent.py
│   │   ├── international_law_agent.py
│   │   └── assembly_agent.py
│   ├── core/             # Composants centraux
│   │   ├── rag_core.py   # Système RAG principal
│   │   └── dispatcher.py # Routage des requêtes
│   ├── schemas/          # Modèles Pydantic
│   │   └── schemas.py
│   └── main.py           # Application FastAPI
├── data/                 # Données et index
│   ├── *.json           # Documents juridiques traités
│   ├── processed_articles.json
│   └── legal_index.faiss
└── test_api.py          # Tests automatisés
```

## 🚀 Installation et Démarrage

### 1. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 2. Traitement des données (si nécessaire)

```bash
python app/data/processor.py
```

### 3. Création de l'index vectoriel (si nécessaire)

```bash
python app/core/rag_core.py
```

### 4. Démarrage de l'API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

L'API sera accessible sur `http://localhost:8000`

## 📡 Endpoints API

### Endpoints Principaux

- **GET /** : Page d'accueil et statut
- **GET /health** : Vérification de santé
- **POST /query** : Requête générale (routage automatique)
- **GET /stats** : Statistiques du corpus

### Endpoints Spécialisés

- **POST /query/constitution** : Questions constitutionnelles
- **POST /query/penal** : Droit pénal
- **POST /query/civil** : Procédure civile
- **POST /query/media** : Droit des médias
- **POST /query/international** : Droit international
- **POST /query/assembly** : Rassemblements publics

### Format des Requêtes

```json
{
  "query": "ما هي حرية الفكر؟",
  "k": 5
}
```

### Format des Réponses

```json
{
  "query": "ما هي حرية الفكر؟",
  "results": [
    {
      "id": "constitution_marocaine_2011-ar_25",
      "title": "الفصل 25",
      "text": "حرية الفكر والرأي والتعبير مكفولة بكل أشكالها...",
      "article_number": 25,
      "page": 15,
      "source": "constitution_marocaine_2011-ar",
      "law_name": "الدستور المغربي 2011",
      "word_count": 45,
      "char_count": 234
    }
  ],
  "total_results": 1,
  "processing_time": 0.15
}
```

## 🧪 Tests

Exécuter la suite de tests automatisés :

```bash
python test_api.py
```

Les tests vérifient :
- ✅ Connectivité API
- ✅ Endpoints de santé
- ✅ Requêtes générales
- ✅ Endpoints spécialisés  
- ✅ Statistiques

## ⚙️ Configuration Technique

### Modèle d'Embeddings
- **Modèle** : `sentence-transformers/LaBSE`
- **Dimensions** : 768
- **Langues supportées** : 109 (incluant l'arabe)

### Indexation
- **Sémantique** : FAISS IndexFlatL2
- **Lexicale** : BM25Okapi
- **Fusion** : Recherche hybride avec re-ranking

### Performance
- **Documents indexés** : 477 articles
- **Temps de réponse moyen** : < 200ms
- **Mémoire requise** : ~2GB (avec modèle)

## 🔍 Exemples d'Utilisation

### Requête cURL

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "ما هي حقوق الإنسان؟", "k": 3}'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "ما هي العقوبات الجنائية؟", "k": 5}
)

results = response.json()
for doc in results["results"]:
    print(f"📄 {doc['title']} - {doc['law_name']}")
    print(f"📝 {doc['text'][:100]}...")
```

## 🛠️ Développement

### Ajout d'un Nouvel Agent

1. Créer une classe héritant de `BaseLegalAgent`
2. Définir le `law_name` correspondant
3. Ajouter l'agent au dispatcher
4. Créer l'endpoint spécialisé

### Extension du Corpus

1. Ajouter les fichiers JSON dans `/data`
2. Mettre à jour le processeur de données
3. Recréer l'index FAISS
4. Redémarrer l'API

## 📊 Statistiques du Système

- **Total documents** : 477 articles
- **Total mots** : 307,845 mots
- **Moyenne mots/document** : 645.38 mots
- **Taille index FAISS** : ~1.5MB
- **Temps d'initialisation** : ~10 secondes

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :
1. Fork le projet
2. Créer une branche feature
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **Sentence Transformers** pour les modèles d'embeddings
- **FAISS** pour l'indexation vectorielle efficace
- **FastAPI** pour le framework web moderne
- **Hugging Face** pour l'écosystème de modèles

---

**Développé avec ❤️ pour la communauté juridique marocaine**
