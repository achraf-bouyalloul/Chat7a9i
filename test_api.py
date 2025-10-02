#!/usr/bin/env python3
"""
Script de test pour l'API RAG juridique marocaine.
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test de l'endpoint de santé."""
    print("🔍 Test de l'endpoint de santé...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Endpoint de santé OK")
            print(f"   Réponse: {response.json()}")
        else:
            print(f"❌ Erreur endpoint de santé: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API. Assurez-vous qu'elle est démarrée.")
        return False
    return True

def test_query_endpoint():
    """Test de l'endpoint de requête principale."""
    print("\n🔍 Test de l'endpoint de requête...")
    
    test_queries = [
        "ما هي حرية الفكر؟",
        "ما هي العقوبات الجنائية؟",
        "كيف تتم المحاكمة المدنية؟"
    ]
    
    for query in test_queries:
        print(f"   Requête: {query}")
        try:
            payload = {"query": query, "k": 3}
            response = requests.post(f"{API_BASE_URL}/query", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Réponse OK - {data['total_results']} résultats trouvés")
                print(f"   ⏱️  Temps de traitement: {data['processing_time']:.2f}s")
                
                # Afficher le premier résultat
                if data['results']:
                    first_result = data['results'][0]
                    print(f"   📄 Premier résultat: {first_result['title']}")
                    print(f"   📖 Source: {first_result['law_name']}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                print(f"   Détail: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

def test_specialized_endpoints():
    """Test des endpoints spécialisés."""
    print("\n🔍 Test des endpoints spécialisés...")
    
    endpoints = [
        ("/query/constitution", "ما هو دور الملك؟"),
        ("/query/penal", "ما هي عقوبة السرقة؟"),
        ("/query/civil", "كيف تتم المرافعة؟")
    ]
    
    for endpoint, query in endpoints:
        print(f"   Test {endpoint}...")
        try:
            payload = {"query": query, "k": 2}
            response = requests.post(f"{API_BASE_URL}{endpoint}", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ OK - {data['total_results']} résultats")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

def test_stats_endpoint():
    """Test de l'endpoint de statistiques."""
    print("\n🔍 Test de l'endpoint de statistiques...")
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print("✅ Statistiques OK")
            print(f"   📊 Total documents: {data['total_documents']}")
            print(f"   📝 Total mots: {data['total_words']}")
            print(f"   📈 Moyenne mots/doc: {data['average_words_per_document']}")
            print("   📚 Répartition par source:")
            for source, count in data['documents_by_source'].items():
                print(f"      - {source}: {count} documents")
        else:
            print(f"❌ Erreur statistiques: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def main():
    """Fonction principale de test."""
    print("🚀 Démarrage des tests de l'API RAG juridique marocaine")
    print("=" * 60)
    
    # Test de connectivité
    if not test_health_endpoint():
        print("\n❌ Tests interrompus - API non accessible")
        return
    
    # Tests fonctionnels
    test_query_endpoint()
    test_specialized_endpoints()
    test_stats_endpoint()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")

if __name__ == "__main__":
    main()
