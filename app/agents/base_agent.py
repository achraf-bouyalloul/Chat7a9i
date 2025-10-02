'''Module définissant l'agent de base pour les requêtes juridiques.'''

from typing import List, Dict, Any
from app.core.rag_core import RAGSystem

class BaseLegalAgent:
    '''Agent de base pour interroger un domaine juridique spécifique.'''

    def __init__(self, rag_system: RAGSystem, law_name: str):
        self.rag_system = rag_system
        self.law_name = law_name

    def answer(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        '''Répond à une question en utilisant le système RAG et en filtrant par domaine juridique.'''
        
        # Recherche initiale plus large pour avoir assez de documents à filtrer
        search_results = self.rag_system.search(query, k * 3) 
        
        # Filtrer les résultats pour ne garder que ceux du domaine de l'agent
        filtered_results = []
        for result in search_results:
            if result.get('law_name') == self.law_name:
                filtered_results.append(result)
        
        return filtered_results[:k]

