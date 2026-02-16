"""
Document loader for PDF files
"""
import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import config


def load_documents(folder_path: str = config.DOCS_FOLDER) -> List[Document]:
    """
    Load documents from the specified folder (PDF and TXT files)
    Uses actual policy documents from docs/ folder, skips semantic_reasoning/ subfolder

    Args:
        folder_path: Path to the folder containing document files

    Returns:
        List of Document objects
    """
    print(f"📄 Loading documents from: {folder_path}")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"⚠️  Created empty folder: {folder_path}")
        return []

    # Get all files in the folder (excluding subdirectories like semantic_reasoning/)
    all_items = os.listdir(folder_path)

    # Filter for actual policy documents only (TXT and PDF files at root level of docs/)
    pdf_files = [f for f in all_items if f.endswith('.pdf') and os.path.isfile(os.path.join(folder_path, f))]
    txt_files = [f for f in all_items if f.endswith('.txt') and os.path.isfile(os.path.join(folder_path, f))]

    # Exclude documentation and meta files
    exclude_files = {'semantic_reasoning', '__pycache__', '.gitkeep'}
    txt_files = [f for f in txt_files if not any(excl in f for excl in exclude_files)]

    if not pdf_files and not txt_files:
        print("⚠️  No document files found in the docs folder")
        print("   Looked for: .pdf and .txt files")
        print("   Note: Documentation files in docs/semantic_reasoning/ are excluded from RAG")
        return []

    if txt_files:
        print(f"📋 Found {len(txt_files)} TXT policy file(s):")
        for f in txt_files:
            print(f"   • {f}")
    if pdf_files:
        print(f"📄 Found {len(pdf_files)} PDF policy file(s):")

    if pdf_files:
        print(f"📄 Found {len(pdf_files)} PDF policy file(s):")
        for f in pdf_files:
            print(f"   • {f}")

    documents = []

    try:
        # Load PDF files
        if pdf_files:
            print(f"\n📄 Loading {len(pdf_files)} PDF file(s)...")
            pdf_loader = DirectoryLoader(
                folder_path,
                glob="*.pdf",  # Only root level PDFs, not subdirectories
                loader_cls=PyPDFLoader,
                show_progress=True
            )
            try:
                pdf_docs = pdf_loader.load()
                documents.extend(pdf_docs)
                print(f"   ✓ Loaded {len(pdf_docs)} PDF pages")
            except Exception as e:
                print(f"   ⚠️  Error loading PDFs: {e}")

        # Load TXT files
        if txt_files:
            print(f"\n📋 Loading {len(txt_files)} TXT policy file(s)...")
            from langchain_community.document_loaders import TextLoader
            for txt_file in txt_files:
                txt_path = os.path.join(folder_path, txt_file)
                try:
                    txt_loader = TextLoader(txt_path, encoding='utf-8')
                    txt_docs = txt_loader.load()
                    documents.extend(txt_docs)
                    print(f"   ✓ Loaded: {txt_file}")
                except Exception as e:
                    print(f"   ⚠️  Could not load {txt_file}: {e}")

        if documents:
            print(f"\n✅ Total: Loaded {len(documents)} document section(s)")
            print(f"   Files indexed: {', '.join(txt_files + pdf_files)}")
            return documents
        else:
            print("\n❌ No documents could be loaded")
            return []

    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        import traceback
        traceback.print_exc()
        return []


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents into chunks with enhanced metadata

    Args:
        documents: List of Document objects

    Returns:
        List of chunked Document objects with metadata
    """
    if not documents:
        return []

    print(f"✂️  Splitting documents into chunks...")

    # Use headers to split first - preserves policy sections
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
        separators=[
            "\n====",  # Section separator
            "\n---",   # Subsection separator
            "\n\n",    # Paragraph break
            "\n",      # Line break
            ". ",      # Sentence
            " ",       # Word
            ""         # Character
        ],
        keep_separator=True  # Keep separators with content
    )

    chunks = text_splitter.split_documents(documents)

    # Enhance metadata for better retrieval
    enhanced_chunks = []
    current_section = ""
    doc_section_map = {}  # Track section titles per document

    for i, chunk in enumerate(chunks):
        # Get document name from source
        doc_name = chunk.metadata.get('source', 'Unknown').split('/')[-1]

        # Extract section title from content
        content_lines = chunk.page_content.strip().split('\n')
        section_title = ""

        # Check if first line looks like a section header
        if content_lines:
            first_line = content_lines[0].strip()
            # More flexible header detection - look for any numbered/formatted lines
            header_keywords = [
                'Policy', 'POLICY', 'Leave', 'Leave Policy', 'Code of Conduct',
                'IT Security', 'Security', 'Access', 'Password', 'Authentication',
                'Multi-Factor', 'MFA', 'Incident', 'Prohibited', 'Actions',
                'Expense', 'Reimbursement', 'Remote', 'Work', 'Health', 'Safety',
                'Development', 'Review', 'Conduct', 'Equipment', 'Core Hours'
            ]

            # Check multiple conditions for section headers
            is_header = (
                (first_line and len(first_line) > 2) and (
                    (first_line[0].isdigit() and '. ' in first_line) or  # "1. Title"
                    first_line.isupper() or  # ALL CAPS
                    first_line.endswith(':') or  # Title:
                    any(keyword in first_line for keyword in header_keywords) or  # Has policy keywords
                    ('it_security' in doc_name and any(kw in first_line for kw in ['Password', 'Authentication', 'Access', 'Incident', 'Prohibited']))
                )
            )

            if is_header:
                section_title = first_line.rstrip(':').strip()
                current_section = section_title
                doc_section_map[doc_name] = section_title

        # Use previously detected section if not found in this chunk
        if not section_title and current_section:
            section_title = current_section
        elif not section_title and doc_name in doc_section_map:
            section_title = doc_section_map[doc_name]

        # Add enhanced metadata
        chunk.metadata['chunk_id'] = i
        chunk.metadata['section_title'] = section_title
        chunk.metadata['doc_name'] = doc_name
        chunk.metadata['relevance_boost'] = 1.0  # Default relevance weight

        # Boost relevance for key policy sections
        if section_title:
            section_lower = section_title.lower()
            if any(keyword in section_lower for keyword in ['sick', 'leave', 'medical', 'health', 'illness']):
                chunk.metadata['relevance_boost'] = 1.3
            elif any(keyword in section_lower for keyword in ['annual', 'vacation', 'holiday', 'time off']):
                chunk.metadata['relevance_boost'] = 1.2
            elif any(keyword in section_lower for keyword in ['security', 'password', 'authentication', 'it', 'access']):
                chunk.metadata['relevance_boost'] = 1.15

        enhanced_chunks.append(chunk)

    print(f"✓ Created {len(enhanced_chunks)} chunks with enhanced metadata")
    sections_found = set(c.metadata.get('section_title', 'N/A') for c in enhanced_chunks if c.metadata.get('section_title'))
    print(f"  Sections indexed: {', '.join(list(sections_found)[:10])}")

    return enhanced_chunks




# Note: Sample document creation removed - using actual policy documents from docs/ folder
# The following documents are automatically indexed from docs/:
# - code_of_conduct.txt
# - expense_policy.txt
# - it_security_policy.txt
# - leave_policy.txt
# - remote_work_policy.txt
# (and any .pdf files placed in docs/ folder)

