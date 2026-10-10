# Credence AI — Explainable Alternative Credit Scoring

**Making credit assessment more inclusive, transparent, and explainable.**

Credence AI is an alternative credit scoring platform designed to help assess the creditworthiness of micro-entrepreneurs, gig workers, and individuals who may lack traditional payslips or established credit histories.

The platform analyzes financial and cash-flow data to support credit risk assessment while providing explainable insights into scoring decisions. It also includes fairness monitoring, fraud-related checks, what-if simulations, and PDF report generation.

## Problem Statement

Many micro-entrepreneurs and gig workers face difficulties accessing formal credit because they lack conventional income documentation or sufficient credit bureau history. Traditional credit assessment systems may also provide limited explanations for their decisions.

Credence AI explores how alternative financial data and explainable machine learning can help address these challenges.

## Key Features

- **Alternative Credit Scoring:** Assess creditworthiness using available financial and cash-flow information.
- **Income Synthesis:** Support analysis of informal or irregular income patterns.
- **Explainable AI:** Understand factors influencing a credit score or assessment.
- **Cash-Flow Analysis:** Analyze financial data to identify income and spending patterns.
- **Fraud-Related Checks:** Apply heuristic checks to identify potentially suspicious patterns.
- **Fairness Monitoring:** Examine model outcomes for potential fairness concerns.
- **What-If Simulation:** Explore how changes in financial inputs may affect an assessment.
- **Application Management:** Review and manage credit analysis applications.
- **Decision History and Audit:** Review assessment decisions and related records.
- **PDF Report Generation:** Generate PDF reports containing credit assessment information.
- **Demo Mode:** Demonstrate the application using sample data.

## Technology Stack

- **Frontend:** React, TypeScript, Vite, Tailwind CSS
- **Backend:** Python, FastAPI
- **Machine Learning:** Scikit-learn
- **Explainable AI:** SHAP
- **Authentication:** JWT-based authentication
- **Reporting:** PDF report generation
- **Testing:** Backend tests and end-to-end verification

## Project Structure

```text
creditanalyzer/
├── backend/
│   ├── app/
│   │   ├── auth/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── model_artifacts/
│   ├── sample_data/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   └── services/
│   ├── package.json
│   └── index.html
└── README.md
```

## Getting Started

### Prerequisites

Install the following:

- Python
- Node.js and npm
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/shreyasnarnaware810-commits/creditanalyzer.git
cd creditanalyzer
```

### 2. Set Up the Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure your local environment variables using `.env.example` as a reference. Create a `.env` file with appropriate values for your environment. Never publish real secrets or credentials.

Start the backend using the project's configured FastAPI entry point. For a standard setup, the command may be:

```bash
uvicorn app.main:app --reload
```

### 3. Set Up the Frontend

Open another terminal in the project root and run:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed by Vite in your terminal.

**Note:** Verify the startup commands and environment configuration against the actual project files before running the application.

## Demo Data and Responsible Use

The project supports demonstrations using sample data and demo mode.

- Sample or synthetic data is not verified real-world financial information.
- Model predictions are estimates, not guaranteed lending outcomes.
- Fairness indicators and explainability outputs do not prove that a model is free from bias.
- Real-world lending deployment requires appropriate validation, privacy protection, security controls, regulatory compliance, and human oversight.

Credence AI is intended to demonstrate explainable alternative credit assessment. Its outputs should not replace a properly validated lending decision process.

## Future Scope

- Support additional sources of alternative financial data.
- Improve model validation and monitoring.
- Expand explainability and fairness evaluation.
- Strengthen security and access controls.
- Add further reporting and integration capabilities.
- Evaluate performance on appropriately governed real-world datasets.

## Contributing

Suggestions, improvements, and feedback are welcome. Contributions should include a clear description of the change and relevant testing.

## License

No license has been specified. Add an appropriate license if you intend to permit others to reuse, modify, or distribute this project.

---

**Credence AI — Explainable insights for more inclusive credit assessment.**
