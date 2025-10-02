from app.agents.base_agent import BaseLegalAgent
from app.core.rag_core import RAGSystem

class CivilAgent(BaseLegalAgent):
    def __init__(self, rag_system: RAGSystem):
        super().__init__(rag_system, law_name='قانون المسطرة المدنية')

