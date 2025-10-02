from typing import List, Dict, Any
from app.core.dispatcher import Dispatcher
from app.agents.base_agent import BaseLegalAgent

class ComplexAgent:
    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher = dispatcher

    def answer(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Analyse une requête complexe, la route vers les agents pertinents et synthétise les résultats."""
        
        # Router la requête pour obtenir les agents concernés
        relevant_agents = self.dispatcher.route_query(query)
        
        # Si un seul agent est pertinent, l'utiliser directement
        if len(relevant_agents) == 1:
            return relevant_agents[0].answer(query, k)
        
        # Si plusieurs agents sont pertinents, interroger chacun et fusionner les résultats
        all_results = []
        for agent in relevant_agents:
            results = agent.answer(query, k)
            all_results.extend(results)
            
        # Éliminer les doublons et classer les résultats (simplifié pour l'instant)
        unique_results = {res["id"]: res for res in all_results}
        
        # Pour une meilleure pertinence, un re-classement basé sur un modèle plus avancé serait nécessaire.
        # Ici, nous nous contentons de retourner les résultats uniques.
        
        return list(unique_results.values())[:k]

