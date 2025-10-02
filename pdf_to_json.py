import os
import re
import json
import fitz  # PyMuPDF

# Répertoires
INPUT_DIR = "/home/achraf-bouyalloul/Desktop/chatha9i"
OUTPUT_DIR = "/home/achraf-bouyalloul/Desktop/chatha9i/output_json"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Regex robuste pour capturer titres d’articles
TITLE_PATTERN = re.compile(
    r"(المادة\s+[0-9٠-٩]+|الفصل\s+[0-9٠-٩]+|الفصل\s+[أ-ي]+)"
)

def clean_text(text: str) -> str:
    """Nettoyage basique du texte"""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[‪‬\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()

def extract_articles_from_pdf(pdf_path):
    """Extraction classique (PDF normal avec texte structuré)"""
    doc = fitz.open(pdf_path)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    articles = []
    current_article = None
    article_number = 0

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        if not text.strip():
            continue

        matches = list(TITLE_PATTERN.finditer(text))
        if matches:
            for i, match in enumerate(matches):
                if current_article:
                    articles.append(current_article)

                article_number += 1
                title = match.group().strip()
                start_idx = match.end()
                end_idx = matches[i+1].start() if i + 1 < len(matches) else len(text)
                article_text = text[start_idx:end_idx].strip()

                current_article = {
                    "title": title,
                    "text": article_text,
                    "article_number": article_number,
                    "page": page_num,
                    "source": pdf_name
                }
        else:
            if current_article:
                current_article["text"] += "\n" + text.strip()

    if current_article:
        articles.append(current_article)

    return {
        "document_info": {
            "file_name": pdf_name + ".pdf",
            "total_pages": len(doc),
            "total_articles": len(articles)
        },
        "articles": articles
    }

# -------------------
# Fallback pour PDF scannés ou problématiques
# -------------------
def extract_text_from_blocks(page):
    """Extraire le texte en organisant par blocs"""
    blocks = page.get_text("dict")["blocks"]
    text_parts = []
    for block in blocks:
        if "lines" in block:
            block_text = ""
            for line in block["lines"]:
                for span in line["spans"]:
                    block_text += span["text"] + " "
            if block_text.strip():
                text_parts.append(block_text.strip())
    return "\n".join(text_parts)

def extract_text_from_scanned_pdf(pdf_path):
    """Extraction multi-méthodes pour PDF scannés"""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page_num, page in enumerate(doc):
        candidates = [
            page.get_text("text"),
            page.get_text("text", sort=True),
            page.get_text("rawtext"),
            " ".join([w[4] for w in page.get_text("words")]),
            extract_text_from_blocks(page)
        ]
        best = max(candidates, key=lambda t: len(clean_text(t)))
        full_text += f"\n--- Page {page_num + 1} ---\n{clean_text(best)}\n"
    doc.close()
    return full_text

def extract_articles_with_fallback(text, pdf_name):
    """Essayer de découper les articles même si le texte est brouillé"""
    pattern = r"(المادة\s+\d+|الفصل\s+\S+)"
    titles = [m for m in re.finditer(pattern, text)]
    articles = []
    for i in range(len(titles)):
        current_title = titles[i].group().strip()
        start = titles[i].end()
        end = titles[i+1].start() if i + 1 < len(titles) else len(text)
        article_text = text[start:end].strip()
        if len(article_text) > 10:
            articles.append({
                "title": current_title,
                "text": article_text,
                "article_number": i+1,
                "page": None,   # page pas fiable ici
                "source": pdf_name
            })
    return articles

def process_problematic_pdf(pdf_path, output_dir):
    """Pipeline fallback"""
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    print(f"\n⚠️ PDF problématique détecté: {pdf_name}")

    text = extract_text_from_scanned_pdf(pdf_path)
    if len(text.strip()) < 100:
        print("   ❌ Extraction vide")
        return

    articles = extract_articles_with_fallback(text, pdf_name)
    data = {
        "document_info": {
            "file_name": pdf_name + ".pdf",
            "total_articles": len(articles),
            "analysis_notes": "PDF problématique - fallback OCR"
        },
        "articles": articles
    }

    out_path = os.path.join(output_dir, f"{pdf_name}_SPECIAL.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"   ✅ Sauvegardé: {out_path}")

# -------------------
# Main
# -------------------
def main():
    for file in os.listdir(INPUT_DIR):
        if not file.endswith(".pdf"):
            continue
        pdf_path = os.path.join(INPUT_DIR, file)
        try:
            data = extract_articles_from_pdf(pdf_path)
            if data["document_info"]["total_articles"] == 0:
                process_problematic_pdf(pdf_path, OUTPUT_DIR)
            else:
                out_path = os.path.join(OUTPUT_DIR, file.replace(".pdf", ".json"))
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"✅ Fichier traité: {file} → {out_path}")
        except Exception as e:
            print(f"⚠️ Erreur avec {file}: {e}")
            process_problematic_pdf(pdf_path, OUTPUT_DIR)

if __name__ == "__main__":
    main()
