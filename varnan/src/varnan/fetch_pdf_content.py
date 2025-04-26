import os
import pymupdf as fitz

def fetch_pdf_content(pdf_path: str):
    """Extract a compact dictionary with title and abstract-like summary from the PDF."""
    pdf_path = pdf_path

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
        first_page_text = doc[0].get_text("text")

        # Basic heuristic to extract title (first non-empty line)
        lines = [line.strip() for line in first_page_text.split('\n') if line.strip()]
        title = lines[0] if lines else "Untitled"

        # Try to extract abstract or fallback to first few lines
        full_text = "\n".join([page.get_text("text") for page in doc])
        abstract = ""

        # Search for "Abstract" section
        abstract_start = full_text.lower().find("abstract")
        if abstract_start != -1:
            # Try grabbing the paragraph following "abstract"
            abstract_block = full_text[abstract_start:abstract_start + 1000]
            abstract_lines = abstract_block.split('\n')
            abstract_lines = [line.strip() for line in abstract_lines if line.strip()]
            if len(abstract_lines) > 1:
                abstract = " ".join(abstract_lines[1:3])
            else:
                abstract = abstract_lines[0]
        else:
            # fallback: use first few lines
            abstract = " ".join(lines[1:3]) if len(lines) > 2 else "No abstract available."

        # Save the content as a dictionary
        pdf_summary = {
            "title": title,
            "abstract": abstract
        }

        # Optional: print or log
        print(f"PDF Summary:\nTitle: {title}\nAbstract: {abstract}")

        return title

    except Exception as e:
        raise RuntimeError(f"Failed to process PDF: {str(e)}") from e


if __name__=="__main__":
    pdf_path = "./research_paper_attention.pdf"
    pdf_summary = fetch_pdf_content(pdf_path)
    print(pdf_summary)