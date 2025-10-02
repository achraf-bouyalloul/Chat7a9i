#!/bin/bash

echo "🚀 Démarrage de l'Assistant Juridique Marocain API"
echo "=================================================="

# Vérifier que les dépendances sont installées
if ! python3 -c "import fastapi, sentence_transformers, faiss" 2>/dev/null; then
    echo "❌ Dépendances manquantes. Installation..."
    pip3 install -r requirements.txt
fi

# Vérifier que les données sont présentes
if [ ! -f "data/processed_articles.json" ]; then
    echo "❌ Données traitées manquantes. Traitement..."
    python3 app/data/processor.py
fi

# Vérifier que l'index FAISS existe
if [ ! -f "data/legal_index.faiss" ]; then
    echo "❌ Index FAISS manquant. Création..."
    python3 app/core/rag_core.py
fi

echo "✅ Tous les prérequis sont satisfaits"
echo "🌐 Démarrage du serveur sur http://localhost:8000"
echo "📚 Documentation API : http://localhost:8000/docs"
echo ""
echo "Pour arrêter le serveur : Ctrl+C"
echo ""

# Démarrer l'API
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
