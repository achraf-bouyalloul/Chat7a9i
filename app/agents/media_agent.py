from app.agents.base_agent import BaseLegalAgent
from app.core.rag_core import RAGSystem

class MediaAgent(BaseLegalAgent):
    def __init__(self, rag_system: RAGSystem):
        super().__init__(rag_system, law_name='قانون الصحافة والنشر 2016')

