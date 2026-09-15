# GATE DA Prep Hub

A Streamlit + Gemini practice workspace built directly from the official
**GATE 2027 Data Science and Artificial Intelligence (DA)** syllabus published
by IIT Madras. Every one of the syllabus's seven sections gets its own
practice track, its own prompts, and its own analytics — none is treated as
secondary.

## Sections (mirrors the syllabus PDF exactly)

| # | Section | Page/Route |
|---|---------|------------|
| 1 | Probability and Statistics | `pages/prob_stats.py` |
| 2 | Linear Algebra | `pages/linear_algebra.py` |
| 3 | Calculus and Optimization | `pages/calculus_optimization.py` |
| 4 | Programming, Data Structures and Algorithms | `pages/programming_dsa.py` |
| 5 | Database Management and Warehousing | `pages/dbms.py` |
| 6 | Machine Learning | `pages/machine_learning.py` |
| 7 | Artificial Intelligence | `pages/artificial_intelligence.py` |

Topic lists inside each section (see `utils/helpers.py::PRACTICE_BLUEPRINTS`)
are taken line-by-line from the syllabus PDF, grouped into logical subtopics.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# fill in GEMINI_API_KEY (required) and MONGODB_URI (optional, else CSV logging is used)
streamlit run app.py
```

## How it works

- Each section has its own **system prompt** and **generation prompt** under
  `prompts/`, scoped strictly to that section's syllabus content so Gemini
  never drifts off-syllabus.
- Questions are returned as schema-validated JSON (`schemas/generation_schema.json`)
  and stored either in MongoDB (`database/mongodb.py`) or as local CSV logs
  (`utils/csv_logger.py`) — whichever is configured.
- Difficulty adapts per section: accuracy above 80% raises difficulty,
  accuracy below 50% lowers it (`utils/helpers.py::recommend_difficulty`).
- `pages/dashboard.py` shows attempt coverage across all 7 sections so you
  can spot which parts of the syllabus you're neglecting.

## Customizing prompts or topics

- Add/edit topics: `utils/helpers.py::PRACTICE_BLUEPRINTS`.
- Change how questions are written: edit the relevant
  `prompts/<section>_system_prompt.txt` and
  `prompts/<section>_generate_question.txt` files.
- Change the visual theme: `utils/streamlit_support.py::apply_brand_styles`.
