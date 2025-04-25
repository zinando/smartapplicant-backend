# Smart Applicant 🔍✨

**ATS-Optimized Resume Analysis Platform**  
*Get instant feedback on your resume's compatibility with applicant tracking systems and AI-powered improvement suggestions.*

[![Django REST](https://img.shields.io/badge/Django_REST-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Next.js](https://img.shields.io/badge/Next.js-13-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![Eleventy](https://img.shields.io/badge/Eleventy-1.0.0-4A2B8C?style=for-the-badge)](https://www.11ty.dev/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 🏗️ System Architecture
┌───────────────────────────────────────────────────────────────┐

│ Smart Applicant │
│ │

│ ┌─────────────┐ ┌─────────────┐ ┌──────────────────┐ │

│ │ HTML │ │ Eleventy │ │ Django REST │ │

│ │ (App) ◄───► (Marketing) │ │ (API) │ │

│ └──────┬──────┘ └─────────────┘ └───────┬──────────┘ │

│ │ │ │
│ ▼ ▼ │

│ ┌─────────────┐ ┌──────────────────┐ │

│ │ Tailwind │ │ PostgreSQL │ │

│ │ (UI) │ │ (Database) │ │

│ └─────────────┘ └─────────┬────────┘ │

│ ┌────────────────────────────────────────────────┘ │

│ │ │
│ ▼ │
│ ┌──────────────────┐ ┌──────────────────┐ │

│ │ │ │ │ │

│ │ spaCy NLP │ │ OpenAI API │ │

│ │ (Parsing) │ │ (Enhancements) │ │

│ │ │ │ │ │

│ └──────────────────┘ └──────────────────┘ │

│ │

└───────────────────────────────────────────────────────────────┘




## 🌟 Key Features

### Core Analysis Engine
- **ATS Readability Scan**  
  - Parsing accuracy scoring (PDF/DOCX)
  - Section visibility detection
  - Format compatibility checks

- **Smart Keyword Extraction**  
  ```python
  def extract_keywords(text):
      nlp = spacy.load("en_core_web_md")
      doc = nlp(text)
      return [chunk.text for chunk in doc.noun_chunks]

🛠️ Tech Stack
__________________________________________________________
Layer	     |             Components
__________________________________________________________
Frontend   |            HTML5, CSS3, Eleventy, Tailwind
----------------------------------------------------------
Backend    |	          Django 4.2, DRF, Celery, Redis
----------------------------------------------------------
Storage    |          	PostgreSQL
----------------------------------------------------------
AI         |          	spaCy, Gemini
----------------------------------------------------------

🚀 Quick Start
```bash
  # Backend
  cd backend && python -m venv venv
  source venv/bin/activate  # macOS/Linux
  venv\Scripts\activate     # Windows
  pip install -r requirements.txt
  python manage.py runserver
```
```bash
  # Frontend
  cd ../ui
  npm install
  npx eleventy --serve
```