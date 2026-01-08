# Data Directory

## Purpose
Storage for uploaded documents and data files used by PCBot.

## Directory Structure

### `uploads/`
Temporary storage for uploaded PDF files during processing.
- Files are processed and converted to vector embeddings
- Stored temporarily before being added to Qdrant database

## Usage

Files uploaded via the web interface are temporarily stored here before being:
1. Parsed and chunked
2. Embedded using sentence-transformers
3. Stored in Qdrant vector database
4. Made available for RAG retrieval

## Notes
- This directory may be empty if no files are currently being processed
- Uploaded files are not persisted after vector embedding
- The main knowledge base (Manual for Development Projects 2024) is embedded in Qdrant
