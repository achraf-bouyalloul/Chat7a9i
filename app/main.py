import json
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.schemas import QueryRequest, QueryResponse, HealthResponse, LegalDocument
from app.core.rag_core import RAGSystem
from app.core.dispatcher import Dispatcher
from app.agents.constitution_agent import ConstitutionAgent
from app.agents.penal_agent import PenalAgent
from app.agents.civil_agent import CivilAgent
from app.agents.media_agent import MediaAgent
from app.agents.international_law_agent import InternationalLawAgent
from app.agents.assembly_agent import AssemblyAgent
from app.agents.complex_agent import ComplexAgent

#from sentence_transformers import SentenceTransformer

#print("Chargement du modèle LaBSE...")
#model = SentenceTransformer("./LaBSE")  # chemin local


# Initialisation de l'application FastAPI
app = FastAPI(
    title="Assistant Juridique Marocain",
    description="API RAG multi-agents pour l'assistance juridique basée sur les lois marocaines",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales pour les composants du système
rag_system = None
agents = {}
dispatcher = None
complex_agent = None

@app.on_event("startup")
async def startup_event():
    """Initialise le système RAG et les agents au démarrage de l'application."""
    global rag_system, agents, dispatcher, complex_agent
    
    print("Initialisation du système RAG...")
    
    # Charger les documents traités
    with open('/home/achraf-bouyalloul/Desktop/chatha9i/data/processed_articles.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # Initialiser le système RAG
    rag_system = RAGSystem()
    rag_system.documents = articles
    rag_system.load_index('/home/achraf-bouyalloul/Desktop/chatha9i/data/legal_index.faiss')
    
    # Recréer l'index BM25 (non sauvegardé dans FAISS)
    texts = [doc["full_text"] for doc in rag_system.documents]
    from rank_bm25 import BM25Okapi
    tokenized_corpus = [doc.split(" ") for doc in texts]
    rag_system.bm25 = BM25Okapi(tokenized_corpus)
    
    # Initialiser les agents spécialisés
    agents = {
        'constitution': ConstitutionAgent(rag_system),
        'penal': PenalAgent(rag_system),
        'civil': CivilAgent(rag_system),
        'media': MediaAgent(rag_system),
        'international': InternationalLawAgent(rag_system),
        'assembly': AssemblyAgent(rag_system)
    }
    
    # Initialiser le dispatcher et l'agent complexe
    dispatcher = Dispatcher(agents)
    complex_agent = ComplexAgent(dispatcher)
    
    print("Système initialisé avec succès!")

@app.get("/", response_model=HealthResponse)
async def root():
    """Endpoint de santé de l'API."""
    return HealthResponse(
        status="healthy",
        message="Assistant Juridique Marocain API est opérationnel",
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de l'état de santé de l'API."""
    return HealthResponse(
        status="healthy",
        message="Tous les systèmes fonctionnent normalement",
        version="1.0.0"
    )

@app.post("/query", response_model=QueryResponse)
async def query_legal_documents(request: QueryRequest):
    """Endpoint principal pour interroger les documents juridiques."""
    if not rag_system or not complex_agent:
        raise HTTPException(status_code=503, detail="Système non initialisé")
    
    start_time = time.time()
    
    try:
        # Utiliser l'agent complexe pour traiter la requête
        results = complex_agent.answer(request.query, request.k)
        
        # Convertir les résultats en modèles Pydantic
        legal_documents = [LegalDocument(**result) for result in results]
        
        processing_time = time.time() - start_time
        
        return QueryResponse(
            query=request.query,
            results=legal_documents,
            total_results=len(legal_documents),
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement de la requête: {str(e)}")

@app.post("/query/constitution", response_model=QueryResponse)
async def query_constitution(request: QueryRequest):
    """Endpoint spécialisé pour interroger la constitution."""
    if not agents.get('constitution'):
        raise HTTPException(status_code=503, detail="Agent constitution non initialisé")
    
    start_time = time.time()
    
    try:
        results = agents['constitution'].answer(request.query, request.k)
        legal_documents = [LegalDocument(**result) for result in results]
        processing_time = time.time() - start_time
        
        return QueryResponse(
            query=request.query,
            results=legal_documents,
            total_results=len(legal_documents),
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement de la requête: {str(e)}")

@app.post("/query/penal", response_model=QueryResponse)
async def query_penal_law(request: QueryRequest):
    """Endpoint spécialisé pour interroger le droit pénal."""
    if not agents.get('penal'):
        raise HTTPException(status_code=503, detail="Agent pénal non initialisé")
    
    start_time = time.time()
    
    try:
        results = agents['penal'].answer(request.query, request.k)
        legal_documents = [LegalDocument(**result) for result in results]
        processing_time = time.time() - start_time
        
        return QueryResponse(
            query=request.query,
            results=legal_documents,
            total_results=len(legal_documents),
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement de la requête: {str(e)}")

@app.post("/query/civil", response_model=QueryResponse)
async def query_civil_law(request: QueryRequest):
    """Endpoint spécialisé pour interroger le droit civil."""
    if not agents.get('civil'):
        raise HTTPException(status_code=503, detail="Agent civil non initialisé")
    
    start_time = time.time()
    
    try:
        results = agents['civil'].answer(request.query, request.k)
        legal_documents = [LegalDocument(**result) for result in results]
        processing_time = time.time() - start_time
        
        return QueryResponse(
            query=request.query,
            results=legal_documents,
            total_results=len(legal_documents),
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement de la requête: {str(e)}")

@app.get("/stats")
async def get_statistics():
    """Endpoint pour obtenir des statistiques sur les documents juridiques."""
    if not rag_system:
        raise HTTPException(status_code=503, detail="Système non initialisé")
    
    # Calculer les statistiques
    total_documents = len(rag_system.documents)
    
    # Statistiques par source
    source_stats = {}
    for doc in rag_system.documents:
        source = doc['law_name']
        source_stats[source] = source_stats.get(source, 0) + 1
    
    # Statistiques sur les mots
    total_words = sum(doc['word_count'] for doc in rag_system.documents)
    avg_words_per_doc = total_words / total_documents if total_documents > 0 else 0
    
    return {
        "total_documents": total_documents,
        "total_words": total_words,
        "average_words_per_document": round(avg_words_per_doc, 2),
        "documents_by_source": source_stats
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Requête reçue: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Réponse envoyée: {response.status_code}")
    return response

