# DecisionRAG
## Uncertainty-Aware Retrieval-Augmented Decision System

### Overview
DecisionRAG is a document-based AI system that combines semantic retrieval, grounded answer generation, confidence estimation, and decision logic to improve reliability under ambiguity or insufficient evidence. It is designed as a focused research-engineering portfolio project: serious enough to discuss in AI/ML PhD interviews, but compact enough to understand end to end.

### Why this project matters
Many RAG systems answer too eagerly even when evidence is weak or the user query is underspecified. Real-world AI systems should know when to answer, when to ask for clarification, and when to abstain. DecisionRAG demonstrates that behavior with transparent, interpretable rules rather than opaque confidence claims.

### Key Features
- Document ingestion for PDF, TXT, and Markdown
- Semantic retrieval with FAISS and sentence-transformers
- Grounded answer generation
- Transparent confidence scoring
- Abstention and clarification policies
- Streamlit demo
- Lightweight evaluation suite

### System Architecture
```text
User Query
   ↓
Retriever
   ↓
Grounded Answer Generator
   ↓
Confidence Estimator
   ↓
Decision Policy
   ↓
{ Answer | Clarification | Abstain }
```

### Project Structure
```text
decisionrag/
├── app/
├── core/
├── ingestion/
├── retrieval/
├── generation/
├── uncertainty/
├── decision/
├── evaluation/
├── storage/
├── data/
├── tests/
├── .env.example
├── requirements.txt
├── README.md
├── run_app.py
└── LICENSE
```

- `app/`: Streamlit application, UI components, and styling
- `core/`: configuration, schemas, logging, and pipeline orchestration
- `ingestion/`: document loading and chunking
- `retrieval/`: embedding, FAISS indexing, and retrieval
- `generation/`: OpenAI-compatible LLM wrapper, prompts, and grounded answering
- `uncertainty/`: transparent confidence signals and aggregation
- `decision/`: ambiguity detection and policy logic
- `evaluation/`: handcrafted evaluation set, metrics, and evaluation runner
- `data/sample_docs/`: bundled demo corpus for immediate use
- `storage/`: persisted indices and JSONL interaction logs

### Installation
```bash
git clone <your-repo-url>
cd decisionrag
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # On Windows PowerShell: Copy-Item .env.example .env
```

### Environment Variables
- `DEFAULT_LLM_PROVIDER`: default provider used by the app (`openai`, `gemini`, or `llama`)
- `OPENAI_API_KEY`: API key for OpenAI mode
- `OPENAI_BASE_URL`: optional custom base URL for OpenAI-compatible OpenAI mode
- `OPENAI_MODEL`: chat model used for OpenAI mode
- `GEMINI_API_KEY`: API key for Gemini mode
- `GEMINI_BASE_URL`: Gemini OpenAI-compatible endpoint base URL
- `GEMINI_MODEL`: chat model used for Gemini mode
- `LLAMA_API_KEY`: optional key for Llama-compatible providers
- `LLAMA_BASE_URL`: base URL for a local or hosted OpenAI-compatible Llama endpoint
- `LLAMA_MODEL`: chat model used for Llama-compatible mode

### Running the App
```bash
python run_app.py
```

The Streamlit demo includes:
- sample-document loading for an immediate demo
- local file upload for PDF, TXT, and Markdown
- FAISS index creation
- runtime selection between OpenAI, Gemini, and Llama-compatible generation backends
- confidence-aware answer, clarification, and abstention behavior
- evidence inspection with source names, page numbers, and similarity scores
- a debug panel exposing confidence components and policy decisions

### Example Behaviors
`ANSWER`

Query: `What deployment requirement is needed before the system can recommend an answer?`

Behavior: retrieves the technical memo, reports the confidence threshold and supporting-passage requirement, and surfaces the supporting chunk citations.

`ASK FOR CLARIFICATION`

Query: `Explain this result.`

Behavior: detects underspecification, lowers confidence through an ambiguity penalty, and asks the user to narrow the topic or section.

`ABSTAIN`

Query: `What GPU cluster was used for training?`

Behavior: retrieves weak or irrelevant evidence, marks the answer as unsupported, and abstains rather than speculating.

### Evaluation
Run the lightweight evaluation suite on the bundled sample corpus:

```bash
python evaluation/run_eval.py
```

The evaluation script rebuilds a small FAISS index from the sample documents, runs the full pipeline on `evaluation/eval_dataset.json`, saves `evaluation/eval_results.json`, and prints:
- decision accuracy
- abstention rate
- clarification rate
- counts per decision type
- average confidence by decision type

### Tech Stack
- Python 3.11
- Streamlit
- sentence-transformers
- FAISS
- PyMuPDF
- pydantic
- numpy
- pandas
- python-dotenv
- OpenAI-compatible client

### CV-Ready Summary
Designed and implemented an uncertainty-aware retrieval-augmented decision system for document-based question answering. Combined semantic retrieval, grounded answer generation, confidence scoring, and abstention/clarification policies to improve reliability under ambiguous or insufficient evidence. Built a modular Python pipeline with FAISS, sentence-transformers, PyMuPDF, and a Streamlit-based interactive demo.

### Future Improvements
- richer calibration
- learned decision policies
- multimodal evidence
- broader benchmark evaluation

### License
MIT License.
