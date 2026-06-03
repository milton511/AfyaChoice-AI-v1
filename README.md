# AfyaChoice AI – Kenya FP Decision Support

## Features
- Safety‑first MEC filtering (Kenya FP Guidelines 2025)
- ML ranking using real Kenyan datasets
- LLM‑powered myth busting (Groq)
- Provider assistant mode
- Deployable to Streamlit Cloud

## Setup

1. Clone this repository.
2. Place your four Excel datasets in `app/data/`.
3. Create a `.env` file with `GROQ_API_KEY=...`
4. Install dependencies: `pip install -r requirements.txt`
5. Train the model: `python train_model.py`
6. Run the app: `streamlit run app/streamlit_app.py`

## Deployment
- Streamlit Cloud: point to `app/streamlit_app.py`
- Make sure `.env` secrets are added in the dashboard.