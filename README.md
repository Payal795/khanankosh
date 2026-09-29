# खनन KOSH

### AI-Powered Knowledge and Decision-Support Platform for CMPDI/CIL and its Subsidiaries

## Overview

**खनन KOSH** is an AI-powered knowledge and decision-support platform designed to transform heterogeneous organisational data into a unified, searchable and verifiable knowledge system.

The name reflects its purpose: **“Khanan” (खनन)** represents the mining domain, while **“KOSH”** represents a repository of knowledge.

The platform is designed to work with scanned PDFs, digital documents, spreadsheets, tables, images and GIS data. It combines intelligent retrieval, AI-based reasoning, topic discovery, GIS-based feasibility analysis and automated report generation to support evidence-backed decision-making.

## Key Capabilities

- **AI Q&A Agent**  
  Enables natural-language querying, semantic retrieval, reasoning and cross-source analysis.

- **Word Cloud & Topic Identification**  
  Identifies important terms, themes and trends from large reports and groups technical passages into mining-related context clusters.

- **GIS Feasibility Engine**  
  Performs spatial feasibility assessment using predefined geological, environmental and infrastructure-related parameters.

- **Automated Report Generation**  
  Combines validated information from multiple organisations and sources to generate structured reports using custom templates.

- **Source Validation & Provenance**  
  Maintains source-level traceability and validates generated information before finalisation.

## System Workflow

The platform follows an end-to-end pipeline:

**Data Ingestion → Extraction & Parsing → AI Agent & Analysis → Intelligent Modules → Validation → Verified Output**

### Data Ingestion and Processing

The system accepts:

- Scanned documents
- PDF, DOCX and TXT files
- Excel and tabular data
- Images
- GIS and spatial data
- Potential integration with an official CIL/subsidiary database

Documents are processed using OCR/VLM-based extraction, document parsing and table extraction.

### Knowledge Representation

The extracted information is organised into:

- **Unstructured data:** chunked, embedded and stored in a vector database
- **Structured data:** stored in an SQL database
- **Spatial data:** processed and stored using spatial database capabilities

This allows the platform to select the appropriate retrieval mechanism depending on the query.

## AI Agent and RAG Pipeline

The AI agent performs:

1. Query understanding
2. Semantic search and retrieval
3. Context matching
4. Retrieval-based reasoning
5. Cross-source analysis
6. Source validation
7. Response generation

A confidence-based retrieval gate ensures that only sufficiently reliable retrieved content is passed to the LLM for response generation.

If the required information is not available or does not meet the required confidence level, the system can indicate that the information is unavailable rather than generating an unsupported response.

## Topic Discovery

The topic discovery workflow uses reports and technical passages to identify recurring mining-related themes.

The system:

1. Screens relevant documents
2. Filters and extracts content
3. Identifies technical passages
4. Clusters related content
5. Generates an interactive word cloud
6. Links identified terms and topics to relevant information

The questionnaire database can also use official Lok Sabha reports and publicly available parliamentary questions to identify historical question patterns and suggest relevant questions and topics.

## GIS-Based Feasibility Analysis

The feasibility module performs weighted spatial analysis using:

| Parameter | Weight |
|---|---:|
| Slope | 30% |
| NDVI | 30% |
| Bare Soil Index | 25% |
| Topographic Position | 15% |

The resulting scores are classified into four threshold-based zones with area and mean statistics.

**NDWI-based water detection** is retained as an auxiliary, unscored layer.

## Report Generation

The report-generation workflow consists of:

1. Selecting a report template
2. Retrieving and extracting relevant information
3. Validating and cross-checking information
4. Generating the structured report
5. Performing verification and correction where required

The generated report undergoes manual verification for accuracy and completeness. Identified errors are routed back through the validation and correction cycle before finalisation.

## Accuracy and Evaluation

The platform evaluates both retrieval quality and generated RAG/LLM responses.

### Retrieval Evaluation

The retrieval stage is evaluated using:

- **Contextual Recall**
- **Contextual Precision**
- **Contextual Relevancy**

These metrics assess whether the vector store retrieves sufficient, precise and relevant information for a query.

### RAG/LLM Output Evaluation

Generated responses are evaluated using:

- **Faithfulness**
- **Answer Relevancy**
- **Correctness**
- **Completeness**
- **Style**

The retrieved context is checked within the RAG pipeline to ensure that the LLM response is appropriately grounded in the retrieved information.

### Human-in-the-Loop Validation

An automated human-in-the-loop validation mechanism provides an additional verification layer. Generated outputs are checked for accuracy and completeness, with flagged outputs routed for review and correction before finalisation.

## Technology Stack

### Backend

- FastAPI
- Python
- Redis

### AI / ML

- LangChain
- Ollama / vLLM
- VLM
- Mistral
- BERTopic
- Scikit-learn

### Data and Databases

- PostgreSQL
- ChromaDB
- Spatial Database

### Document Processing

- OCR
- PyMuPDF
- pdfplumber
- pdf2docx

### Frontend

- React
- TypeScript
- Tailwind CSS
- Leaflet
- Esri
- Plotly
- WordCloud2.js

### Evaluation

- DeepEval

### Deployment and Infrastructure

- AWS
- Docker
- Vercel
- GitHub

## Security and Deployment

The platform is designed for deployment within a private AWS network.

The architecture includes:

- Private VPC deployment
- Protected databases and vector search
- Locally hosted Ollama AI engine
- Dockerised and isolated services
- Authenticated and encrypted API access
- Secure key and secret management through AWS IAM
- Controlled CPU and RAM allocation
- Separate development, testing and production environments
- Load-balanced backend services
- Independently scalable GPU nodes for AI workloads
- Centralised tracking and monitoring

The design ensures that organisational documents and AI queries remain within the protected deployment environment and do not require exposure to external AI APIs.

## Expected Impact

खनन KOSH is intended to support:

- Faster decision support
- Improved accuracy and traceability
- Preservation of organisational knowledge
- Reduced manual information retrieval and report preparation
- Better parliamentary and administrative responses
- A foundation for future digital and analytical integrations

## Core Value Proposition

खनन KOSH transforms fragmented organisational information into a **searchable, connected, validated and decision-ready knowledge system**, combining AI-powered retrieval and reasoning with topic discovery, spatial analysis, source validation and automated reporting.

## Project Information

| Field | Details |
|---|---|
| **Problem Statement ID** | 26023 |
| **Theme** | Smart Automation |
| **Category** | Software |
| **Team** | Code_Miners |
| **Event** | Smart India Hackathon 2026 |
