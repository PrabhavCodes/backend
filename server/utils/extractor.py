from typing import List
from langchain_community.document_loaders import PyPDFLoader

def extract_abstract(pages: List, min_words: int = 100, max_chars: int = 2000) -> str:
    """
    Extract the abstract from a list of pre-split PDF pages.
    
    Args:
        pages (List): List of Document objects from PyPDFLoader.load_and_split()
        min_words (int): Minimum number of words to consider a valid abstract (default: 100)
        max_chars (int): Maximum characters to extract if no clear end is found (default: 1500)
    
    Returns:
        str: The extracted abstract body as a string
    """
    # Limit to first 4 pages
    first_four_pages = pages[:4]
    
    # Combine text from first 4 pages
    full_text = "\n".join(page.page_content for page in first_four_pages)
    
    # Convert to lowercase for case-insensitive search
    text_lower = full_text.lower()
    
    # Find the start of the abstract
    abstract_start_idx = text_lower.find("abstract")
    if abstract_start_idx == -1:
        return "Abstract not found in the first 4 pages."
    
    # Extract text starting from "Abstract"
    start_idx = abstract_start_idx
    content_after_abstract = full_text[start_idx:]
    
    # Define potential section headings (case-insensitive)
    possible_end_markers = ["introduction", "keywords", "methodology", "background", "1."]
    
    # Initialize end index
    end_idx = None
    abstract_content = content_after_abstract
    
    # Look for paragraph break (double newline) after a minimum length
    min_chars = min_words * 5  # Rough estimate: 5 chars/word
    paragraph_break_idx = content_after_abstract.find("\n\n", min_chars)
    if paragraph_break_idx != -1:
        end_idx = paragraph_break_idx
        abstract_content = content_after_abstract[:end_idx]
    
    # Check for headings only after minimum length, ensuring they're standalone
    if end_idx is None or len(abstract_content.split()) < min_words:
        for marker in possible_end_markers:
            marker_idx = content_after_abstract.lower().find(marker, min_chars)
            if marker_idx != -1:
                # Verify it's a heading (standalone line, e.g., preceded by newline)
                if marker_idx > 0 and content_after_abstract[marker_idx - 1] == "\n":
                    potential_end = marker_idx
                    # Ensure enough content before stopping
                    if len(content_after_abstract[:potential_end].split()) >= min_words:
                        end_idx = potential_end
                        abstract_content = content_after_abstract[:end_idx]
                        break
    
    # If no clear end found, use max_chars
    if end_idx is None:
        end_idx = min(max_chars, len(content_after_abstract))
        abstract_content = content_after_abstract[:end_idx]
    
    # Clean up: Remove "Abstract" heading and trailing whitespace
    abstract_content = abstract_content.strip()
    if abstract_content.lower().startswith("abstract"):
        abstract_content = abstract_content[8:].strip()  # Remove "Abstract"
        if abstract_content.startswith(":"):
            abstract_content = abstract_content[1:].strip()  # Remove colon if present
    
    return abstract_content

def extract_introduction(pages: List, min_words: int = 200, max_chars: int = 3000) -> str:
    """
    Extract the introduction from a list of pre-split PDF pages.
    
    Args:
        pages (List): List of Document objects from PyPDFLoader.load_and_split()
        min_words (int): Minimum number of words to consider a valid introduction (default: 200)
        max_chars (int): Maximum characters to extract if no clear end is found (default: 3000)
    
    Returns:
        str: The extracted introduction body as a string
    """
    # Limit to pages 2 to 6 (0-based index: 1 to 5)
    target_pages = pages[1:6]  # Pages 2-6 inclusive
    
    # Combine text from target pages
    full_text = "\n".join(page.page_content for page in target_pages)
    
    # Convert to lowercase for case-insensitive search
    text_lower = full_text.lower()
    
    # Find the start of the introduction
    intro_start_idx = text_lower.find("introduction")
    if intro_start_idx == -1:
        return "Introduction not found between pages 2 and 6."
    
    # Extract text starting from "Introduction"
    start_idx = intro_start_idx
    content_after_intro = full_text[start_idx:]
    
    # Define potential section headings that might follow the introduction
    possible_end_markers = ["methods", "methodology", "results", "discussion", "2.", "materials"]
    
    # Initialize end index
    end_idx = None
    intro_content = content_after_intro
    
    # Look for paragraph break or next section after a minimum length
    min_chars = min_words * 5  # Rough estimate: 5 chars/word
    paragraph_break_idx = content_after_intro.find("\n\n", min_chars)
    if paragraph_break_idx != -1:
        # Check if enough words before the break
        potential_content = content_after_intro[:paragraph_break_idx]
        if len(potential_content.split()) >= min_words:
            end_idx = paragraph_break_idx
            intro_content = potential_content
    
    # Check for headings only after minimum length, ensuring they're standalone
    if end_idx is None or len(intro_content.split()) < min_words:
        for marker in possible_end_markers:
            marker_idx = content_after_intro.lower().find(marker, min_chars)
            if marker_idx != -1:
                # Verify it's a heading (standalone line, e.g., preceded by newline)
                if marker_idx > 0 and content_after_intro[marker_idx - 1] == "\n":
                    potential_end = marker_idx
                    # Ensure enough content before stopping
                    if len(content_after_intro[:potential_end].split()) >= min_words:
                        end_idx = potential_end
                        intro_content = content_after_intro[:end_idx]
                        break
    
    # If no clear end found, use max_chars
    if end_idx is None:
        end_idx = min(max_chars, len(content_after_intro))
        intro_content = content_after_intro[:end_idx]
    
    # Clean up: Remove "Introduction" heading and trailing whitespace
    intro_content = intro_content.strip()
    if intro_content.lower().startswith("introduction"):
        intro_content = intro_content[12:].strip()  # Remove "Introduction"
        if intro_content.startswith(":"):
            intro_content = intro_content[1:].strip()  # Remove colon if present
    
    return intro_content
