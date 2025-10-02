from typing import List, Dict, Any, Type
from app.agents.base_agent import BaseLegalAgent

class Dispatcher:
    def __init__(self, agents: Dict[str, BaseLegalAgent]):
        self.agents = agents
        self.agent_keywords = {
            'constitution': ['دستور', 'ملكي', 'حكومة', 'برلمان', 'فصل'],
            'penal': ['جنائي', 'جريمة', 'عقوبة', 'سجن', 'قتل', 'سرقة'],
            'civil': ['مدني', 'محكمة', 'قضية', 'إجراءات', 'مسطرة'],
            'media': ['صحافة', 'نشر', 'إعلام', 'تعبير', 'رأي'],
            'international': ['دولي', 'إنساني', 'حرب', 'معاهدة'],
            'assembly': ['تجمع', 'مظاهرة', 'اجتماع', 'عمومي'],
        }

    def route_query(self, query: str) -> List[BaseLegalAgent]:
        """Route la requête vers les agents les plus pertinents en fonction des mots-clés."""
        matched_agents = set()

        for agent_name, keywords in self.agent_keywords.items():
            if any(keyword in query for keyword in keywords):
                matched_agents.add(self.agents[agent_name])

        if not matched_agents:
            # Si aucun mot-clé ne correspond, on retourne tous les agents (stratégie de secours)
            return list(self.agents.values())

        return list(matched_agents)

