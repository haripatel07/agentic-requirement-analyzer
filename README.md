# Agentic Requirement Analyzer

An autonomous multi-agent AI system that analyzes raw software requirements documents and generates structured Agile outputs: functional/non-functional requirements, user stories, acceptance criteria, and ambiguity/risk detection.

**Stack:** Python 3.11 · FastAPI · LangGraph · React 18 · Tailwind CSS · SQLite · Groq API (LLM)

---

## Quick Start

### 1. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your GROQ_API_KEY (get one free at https://console.groq.com)

# Initialize database
python -c "from backend import db; db.init_db()"

# Start backend server
uvicorn backend.main:app --reload
```

The backend will run on `http://localhost:8000`.

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (Vite)
npm run dev
```

The frontend will run on `http://localhost:5173`.

### 3. Upload & Analyze

1. Open `http://localhost:5173` in your browser.
2. Click "Upload & Analyze" and select a `.txt`, `.pdf`, or `.docx` file.
3. Watch the pipeline progress and view the generated report.

---

## Architecture

### Six Specialized Agents

```
┌─ Agent 1: Document Parsing
│  └─ Extracts clean text from PDF/DOCX/TXT
├─ Agent 2: Requirement Analysis
│  └─ Identifies actors, features, and constraints
├─ Agent 3: Classification
│  └─ Separates functional vs. non-functional requirements
├─ Agent 4: User Story Generation
│  └─ Creates Agile "As a / I want / So that" stories
├─ Agent 5: Acceptance Criteria
│  └─ Generates Given/When/Then criteria per story
└─ Agent 6: Risk & Ambiguity Detection
   └─ Flags vague language and suggests clarifications
```

Each agent:
- Takes a `PipelineState` (shared state dict)
- Returns a partial dict to merge back in
- Fails gracefully; errors logged to `state["errors"]`
- Uses LLM (Groq) for intelligence + JSON parsing

### State Schema

```python
class PipelineState(TypedDict):
    raw_text: str
    filename: str
    actors: list[str]
    features: list[str]
    constraints: list[str]
    functional_requirements: list[str]
    non_functional_requirements: list[str]
    user_stories: list[dict]          # {feature, story, priority}
    acceptance_criteria: list[dict]   # {story_ref, given, when, then}
    risks: list[dict]                 # {requirement, reason, suggestion}
    ambiguities: list[dict]           # {requirement, reason, suggestion}
    errors: list[str]
```

---

## API Endpoints

### Upload

```
POST /upload
```
- Body: multipart form-data with file
- Response: `{"filename": "path/to/file", "status": "uploaded"}`

### Analyze (Full Pipeline)

```
POST /analyze
```
- Body: `{"filename": "<path from /upload>"}`
- Response: `{"run_id": 1, "report": {...}}`

### Pipeline History

```
GET /runs
```
Response: `{"runs": [{"id": 1, "filename": "...", "created_at": "..."}, ...]}`

```
GET /runs/{run_id}
```
Response: `{"id": 1, "filename": "...", "created_at": "...", "report": {...}}`

### Debug: Step-1 (Agents 1-3 only)

```
POST /analyze/step1
```
- Body: `{"filename": "..."}`
- Returns state after parsing, analysis, and classification (useful for debugging)

---

## Sample Documents

Three example requirement documents are included to test the system:

1. **sample_docs/sample_requirement.txt** — ShopQuick e-commerce platform
   - Mix of clear and vague requirements
   - Tests basic functional and non-functional classification

2. **sample_docs/healthcare_portal.txt** — PatientHub medical records portal
   - HIPAA compliance, real-time data, security
   - Ambiguous terms: "should be high", "acceptable", "intuitive"

3. **sample_docs/hr_system.txt** — HRFlow internal HR management system
   - Employee records, payroll, performance reviews
   - Ambiguous terms: "responsive", "easily", "fast", "minimal downtime"

**To test all three:**

```bash
# Terminal 1: start backend
uvicorn backend.main:app --reload

# Terminal 2: test each sample
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"filename":"sample_docs/sample_requirement.txt"}'

curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"filename":"sample_docs/healthcare_portal.txt"}'

curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"filename":"sample_docs/hr_system.txt"}'
```

---

## Testing Notes

### Agent 6 (Risk & Ambiguity Detection)

The Risk & Ambiguity agent uses a seed corpus of known-vague phrases:
- "quickly", "user-friendly", "as needed", "should support", "scalable"

For each requirement, it:
1. Embeds the requirement and queries a FAISS index of seed phrases
2. If similarity is above threshold, calls the LLM to confirm and suggest a fix

The healthcare and HR sample docs are loaded with these ambiguous terms to demonstrate the agent's output.

### Manual QA Flow

1. **Upload a sample**: Use the React UI or `curl` to test a doc
2. **Check /analyze response**: Verify all 8 report sections are populated
3. **Check /runs**: Confirm the run was persisted in SQLite
4. **Review ambiguities**: Confirm Agent 6 flagged vague language with suggestions

### Automated Tests

Run the project test suite from the repo root:

```bash
./venv/bin/python -m pytest -q
```

The current suite covers:
- `backend.state.empty_state`
- document parsing for `.txt` files
- SQLite persistence helpers
- report assembly with a monkeypatched summary generator
- FastAPI health, upload, and analyze endpoints

### LLM Fallback

If `GROQ_API_KEY` is not set, the agents will fail gracefully and log errors to `state["errors"]`. The pipeline will continue with empty defaults for that agent's output. For production, implement an Ollama fallback per the spec.

### Performance Notes

- Full pipeline on sample docs: ~5-15 seconds (depends on LLM latency)
- FAISS embedding is optional; if unavailable, simple keyword heuristics are used
- Database is single-threaded SQLite; fine for demo, upgrade for production

---

## File Structure

```
agentic-requirement-analyzer/
├── context.md                           # Architecture & week-by-week plan
├── README.md                            # This file
├── requirements.txt                     # Python dependencies
├── .env.example                         # Environment template
├── backend/
│   ├── main.py                         # FastAPI app & endpoints
│   ├── state.py                        # PipelineState TypedDict
│   ├── graph.py                        # Pipeline orchestration
│   ├── report.py                       # Report assembly (8 sections)
│   ├── db.py                           # SQLite setup & queries
│   └── agents/
│       ├── parser.py                   # Agent 1: Document parsing
│       ├── analyzer.py                 # Agent 2: Requirement analysis
│       ├── classifier.py               # Agent 3: FR/NFR classification
│       ├── story_generator.py          # Agent 4: User story generation
│       ├── acceptance.py               # Agent 5: Acceptance criteria
│       └── risk_detector.py            # Agent 6: Risk & ambiguity detection
├── frontend/
│   ├── package.json
│   ├── tailwind.config.js
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── UploadForm.jsx          # File upload + analysis trigger
│       │   ├── PipelineProgress.jsx    # Step indicator
│       │   └── ReportView.jsx          # 8-section report display
│       └── api/
│           └── client.js               # API helpers
└── sample_docs/
    ├── sample_requirement.txt           # E-commerce example
    ├── healthcare_portal.txt            # Healthcare example
    └── hr_system.txt                    # HR tool example
```

---

## Design Decisions

1. **LangGraph over CrewAI**: Explicit state machine for deterministic, debuggable agent handoffs.
2. **Module-level PROMPT constants**: Each agent is self-contained; easy to tune and review prompt quality.
3. **Graceful degradation**: Every agent returns empty defaults on failure; pipeline never crashes.
4. **Seed corpus + FAISS**: Agent 6 uses concrete grounding (matched ambiguous phrases) before LLM judgment, not just raw heuristics.
5. **SQLite for storage**: Simple, portable, sufficient for demo; upgrade for production.

---

## Development & Contributing

- **Add a new agent**: Create `backend/agents/your_agent.py` with a function `your_agent_function(state: Dict) -> Dict`.
- **Tune prompts**: Each agent's prompt is a module-level constant; edit and test in isolation.
- **Extend report sections**: Modify `backend/report.py` and update `frontend/src/components/ReportView.jsx`.

---

## Known Limitations

- LLM calls are synchronous; no streaming or async progress updates.
- Single-threaded SQLite; not suitable for high concurrency.
- Groq API key is required; no local LLM fallback implemented yet (can be added).
- PDF extraction via pypdf may fail on scanned PDFs; recommend OCR preprocessing for production.

---

## Demo & Viva Notes

- The sample docs intentionally include ambiguous language to showcase Agent 6.
- Run all three samples and inspect the reports to show:
  - Functional vs. non-functional separation
  - User story generation from features
  - Ambiguity detection and concrete suggestions
  - SQLite persistence (check `/runs`)
- Highlight the LangGraph choice: explicit state machine vs. autonomous multi-agent frameworks.

---

## License

This is a 4-week internship project. See `context.md` for architecture reference and week-by-week plan.
