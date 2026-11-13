This is an AI-powered Suspicious Activity Report (SAR) processing system that automates financial crime detection using multi-agent architecture with Chain-of-Thought and ReACT prompting strategies.

- **Detects suspicious financial activity** using AI-powered pattern recognition
- **Generates regulatory-compliant reports** for FinCEN submission
- **Implements human-in-the-loop decision gates** for compliance oversight
- **Creates comprehensive audit trails** for regulatory examination

### 🏗️ System Architecture Overview

```
📊 CSV Data → 🔍 Risk Analyst Agent → 👤 Human Review → ✅ Compliance Officer Agent → 📄 SAR Filing
                 (Chain-of-Thought)                      (ReACT Framework)
```
1: Foundation & Data Modeling

1. Identified suspicious activity patterns
2. Implemented Pydantic schemas in `foundation_sar.py`
3. Created data loading and audit logging systems
4. Delivered a working foundation module with validated schemas

2: Risk Analyst Agent

1. Implemented risk analysis agent in `risk_analyst_agent.py`
2. Tested with different suspicious activity patterns
3. Validated JSON output parsing and error handling
4. Delivered Risk Analyst Agent that classifies 5 crime types with confidence scores

3: Compliance Officer Agent

1. Implemented compliance agent in `compliance_officer_agent.py`
2. Generated SAR narratives ≤120 words with regulatory citations
3. Validated narrative completeness and terminology
4. Delivered Compliance Officer Agent that generates regulatory-compliant narratives

4: System Integration

1. Integrated both agents into unified workflow
2. Implemented human-in-the-loop decision gates
3. Generated complete SAR documents
4. Created efficiency metrics and cost optimization
5. Delivered End-to-end SAR processing system with audit trails


# Output Directories

This folder contains generated outputs from the SAR processing system:

## 📄 filed_sars/
Generated SAR documents in JSON format. Each SAR includes:
- Customer information
- Transaction details: We group transactions by customer through account ownership. We compute totals/counts before screening.
- Risk analysis results
- Compliance narrative
- Regulatory citations
- Audit trail references

## 📊 audit_logs/
Comprehensive audit trails in JSONL format capturing:
- Agent decisions and reasoning
- Processing timestamps
- Input/output data summaries
- Success/failure status
- Error messages and debugging info

These outputs demonstrate the explainability and auditability required for regulatory compliance in financial crime detection systems.

Local Machine Instructions

Follow these steps to set up your environment.
Prerequisites

    Python 3.8+
    OpenAI API key
    VS Code with the Jupyter extension (recommended) or another IDE that supports Jupyter notebooks.

**Required Python packages** (automatically installed via requirements.txt):
```
pandas>=2.0.0          # Data manipulation
pydantic>=2.0.0         # Data validation
openai>=1.0.0          # AI/LLM integration
python-dotenv>=1.0.0   # Environment variables
jupyter>=1.0.0         # Notebook development
pytest>=7.0.0          # Testing framework
matplotlib>=3.7.0      # Visualization
seaborn>=0.12.0        # Statistical plots
```

Setup Steps

Step 1: Clone the Project Repository

If you haven't already, clone the project repository to your local machine.

Step 2: Navigate to the Starter Directory

Open your terminal or command prompt and navigate to the project's starter directory:

cd project/starter

Step 3: Install Dependencies

Install all the required Python packages using the requirements.txt file:

pip install \-r requirements.txt

Step 4: Configure your OpenAI API Key

Create a .env file to securely store your API key. You can do this by copying the template file:

cp .env.template .env

Next, open the newly created .env file in a text editor and replace your_openai_api_key_here with your actual OpenAI API key:

\# .env  
OPENAI_API_KEY=your_actual_api_key_here
Step 5: Verify Your Setup  

You can verify that your environment is set up correctly by running the setup cells in the notebooks/01_data_exploration.ipynb notebook. If they run without errors, you are ready to begin the project.

