from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from typing import List
import io
import os
import tempfile
from .lib.literature_chain import generate_comparison_report

app = FastAPI()

# Add CORS middleware for flexibility (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

def extract_pages_from_pdf(file: UploadFile) -> List:
    """
    Extract text from each page of a PDF file using PyPDFLoader.
   
    Args:
        file (UploadFile): The uploaded PDF file.
   
    Returns:
        List: A list of document objects with page content.
    """
    try:
        # We need to save the uploaded file temporarily since PyPDFLoader works with file paths
        import tempfile
        import os
        
        # Create a temporary file to save the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Reset the file pointer to the beginning and read all content
            file.file.seek(0)
            content = file.file.read()
            # Write content to temp file
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Use PyPDFLoader with the temp file path
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(temp_path)
        pages = loader.load_and_split()
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        return pages
    except Exception as e:
        import traceback
        print(f"Error in extract_pages_from_pdf: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error reading PDF: {str(e)}")
    finally:
        # Make sure to reset the file pointer in case it's used elsewhere
        file.file.seek(0)
# Simple placeholder for your comparison function

@app.post("/upload")
async def upload_papers(
    paper_1: UploadFile = File(...),
    paper_2: UploadFile = File(...),
    paper_3: UploadFile = File(...)
):
    """
    Accept three PDF files, extract their content, and generate a comparison.
   
    Returns:
        dict: Contains the comparison report.
    """
    try:
        # Validate file types
        for paper, name in [(paper_1, "Paper 1"), (paper_2, "Paper 2"), (paper_3, "Paper 3")]:
            content_type = paper.content_type
            if not content_type or "pdf" not in content_type.lower():
                raise HTTPException(
                    status_code=415, 
                    detail=f"{name} ({paper.filename}) must be a PDF. Got content type: {content_type}"
                )
        
        # Extract text from each PDF
        pages_1 = extract_pages_from_pdf(paper_1)
        pages_2 = extract_pages_from_pdf(paper_2)
        pages_3 = extract_pages_from_pdf(paper_3)
        
        # Generate comparison (replace with your actual implementation)
        comparison = generate_comparison_report(pages_1 = pages_1,pages_2 = pages_2,pages_3 = pages_3)
        
        return {
            "status": "success",
            "comparison": comparison,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Error processing files: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Error processing files: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)