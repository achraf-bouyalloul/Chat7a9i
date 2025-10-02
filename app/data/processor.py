"""
Module de traitement des données juridiques marocaines.
Nettoie et structure les textes pour l'indexation vectorielle.
"""

import json
import re
from typing import List, Dict, Any
from pathlib import Path
import unicodedata
from unidecode import unidecode


class LegalDataProcessor:
    """Processeur pour les données juridiques marocaines."""
    
    def __init__(self):
        self.tatweel_pattern = re.compile(r'ـ+')  # Pattern pour supprimer le tatweel
        self.diacritics_pattern = re.compile(r'[\u064B-\u0652\u0670\u0640]')  # Diacritiques arabes
        
    def normalize_arabic_text(self, text: str) -> str:
        """
        Normalise le texte arabe en supprimant les diacritiques et le tatweel.
        
        Args:
            text: Texte arabe à normaliser
            
        Returns:
            Texte normalisé
        """
        if not text:
            return ""
            
        # Supprimer le tatweel (caractère d'extension)
        text = self.tatweel_pattern.sub('', text)
        
        # Supprimer les diacritiques
        text = self.diacritics_pattern.sub('', text)
        
        # Normalisation Unicode
        text = unicodedata.normalize('NFKC', text)
        
        # Nettoyer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def clean_article_text(self, text: str) -> str:
        """
        Nettoie le texte d'un article juridique.
        
        Args:
            text: Texte brut de l'article
            
        Returns:
            Texte nettoyé
        """
        if not text:
            return ""
        
        # Normaliser le texte arabe
        text = self.normalize_arabic_text(text)
        
        # Supprimer les caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Supprimer les caractères spéciaux indésirables
        text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s\d\.\-\(\)\[\]،؛؟!]', ' ', text)
        
        # Nettoyer les espaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_article_number(self, title: str) -> int:
        """
        Extrait le numéro d'article du titre.
        
        Args:
            title: Titre de l'article
            
        Returns:
            Numéro de l'article ou 0 si non trouvé
        """
        # Rechercher les nombres dans le titre
        numbers = re.findall(r'\d+', title)
        if numbers:
            return int(numbers[0])
        return 0
    
    def process_legal_document(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Traite un document juridique JSON et retourne les articles structurés.
        
        Args:
            file_path: Chemin vers le fichier JSON
            
        Returns:
            Liste des articles traités
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            processed_articles = []
            
            for article in data.get('articles', []):
                # Nettoyer le texte
                clean_text = self.clean_article_text(article.get('text', ''))
                clean_title = self.clean_article_text(article.get('title', ''))
                
                if not clean_text or len(clean_text.strip()) < 10:
                    continue  # Ignorer les articles trop courts
                
                # Extraire le numéro d'article
                article_num = article.get('article_number', self.extract_article_number(clean_title))
                
                processed_article = {
                    'id': f"{article.get('source', 'unknown')}_{article_num}",
                    'title': clean_title,
                    'text': clean_text,
                    'article_number': article_num,
                    'page': article.get('page', 0),
                    'source': article.get('source', 'unknown'),
                    'law_name': self.get_law_name(article.get('source', '')),
                    'full_text': f"{clean_title} {clean_text}",  # Texte complet pour l'indexation
                    'word_count': len(clean_text.split()),
                    'char_count': len(clean_text)
                }
                
                processed_articles.append(processed_article)
            
            return processed_articles
            
        except Exception as e:
            print(f"Erreur lors du traitement de {file_path}: {str(e)}")
            return []
    
    def get_law_name(self, source: str) -> str:
        """
        Retourne le nom complet de la loi basé sur le nom du fichier source.
        
        Args:
            source: Nom du fichier source
            
        Returns:
            Nom complet de la loi
        """
        law_names = {
            'constitution_marocaine_2011-ar': 'الدستور المغربي 2011',
            'مجموعة-القانون-الجنائي-وقانون-المسطرة-الجنائية': 'مجموعة القانون الجنائي وقانون المسطرة الجنائية',
            'قانونالمسطرةالمدنية': 'قانون المسطرة المدنية',
            'التجمعات-العمومية': 'قانون التجمعات العمومية',
            'الصحافة-والنشر-2016': 'قانون الصحافة والنشر 2016',
            'القانون-الدولي-الإنساني': 'القانون الدولي الإنساني'
        }
        
        return law_names.get(source, source)
    
    def process_all_documents(self, data_dir: str) -> List[Dict[str, Any]]:
        """
        Traite tous les documents juridiques dans un répertoire.
        
        Args:
            data_dir: Répertoire contenant les fichiers JSON
            
        Returns:
            Liste de tous les articles traités
        """
        data_path = Path(data_dir)
        all_articles = []
        
        for json_file in data_path.glob('*.json'):
            print(f"Traitement de {json_file.name}...")
            articles = self.process_legal_document(str(json_file))
            all_articles.extend(articles)
            print(f"  -> {len(articles)} articles traités")
        
        print(f"Total: {len(all_articles)} articles traités")
        return all_articles
    
    def save_processed_data(self, articles: List[Dict[str, Any]], output_path: str):
        """
        Sauvegarde les articles traités dans un fichier JSON.
        
        Args:
            articles: Liste des articles traités
            output_path: Chemin de sortie
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        print(f"Données sauvegardées dans {output_path}")


if __name__ == "__main__":
    # Test du processeur
    processor = LegalDataProcessor()
    
    # Traiter tous les documents
    articles = processor.process_all_documents('/home/achraf-bouyalloul/Desktop/chatha9i/data')
    
    # Sauvegarder les données traitées
    processor.save_processed_data(articles, '/home/achraf-bouyalloul/Desktop/chatha9i/data/processed_articles.json')
    
    # Afficher quelques statistiques
    print(f"\nStatistiques:")
    print(f"Total articles: {len(articles)}")
    
    sources = {}
    for article in articles:
        source = article['source']
        sources[source] = sources.get(source, 0) + 1
    
    print("\nRépartition par source:")
    for source, count in sources.items():
        print(f"  {source}: {count} articles")
