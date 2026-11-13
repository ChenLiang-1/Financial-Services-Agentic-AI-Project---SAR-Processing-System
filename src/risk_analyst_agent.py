# Risk Analyst Agent - Chain-of-Thought Implementation
# Implement Risk Analyst Agent using Chain-of-Thought prompting

"""
Risk Analyst Agent Module

This agent performs suspicious activity classification using Chain-of-Thought reasoning.
It analyzes customer profiles, account behavior, and transaction patterns to identify
potential financial crimes.

YOUR TASKS:
- Study Chain-of-Thought prompting methodology
- Design system prompt with structured reasoning framework
- Implement case analysis with proper error handling
- Parse and validate structured JSON responses
- Create comprehensive audit logging
"""

import json
import openai
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Import your foundation components
from src.foundation_sar import (
    RiskAnalystOutput, 
    ExplainabilityLogger, 
    CaseData
)

# Load environment variables
load_dotenv()
import re
class RiskAnalystAgent:
    """
    Risk Analyst agent using Chain-of-Thought reasoning.
    
    Implement agent that:
    - Uses systematic Chain-of-Thought prompting
    - Classifies suspicious activity patterns
    - Returns structured JSON output
    - Handles errors gracefully
    - Logs all operations for audit
    """
    
    def __init__(self, openai_client, explainability_logger, model="gpt-4o-mini"):
        """Initialize the Risk Analyst Agent
        
        Args:
            openai_client: OpenAI client instance
            explainability_logger: Logger for audit trails
            model: OpenAI model to use
        """
        # Initialize agent components
        self.client = openai_client
        self.logger = explainability_logger
        self.explainability_logger = explainability_logger
        self.model = model
        
        # Design Chain-of-Thought system prompt
        self.system_prompt = "You are an experienced Financial Crime analyst. Use the following Chain-of-Thought methodology: " + json.dumps(create_chain_of_thought_framework()) + " The categories are: " + json.dumps(get_classification_categories()) + " Return the JSON fields: classification(Use the exact words from the keys of get_classification_categories()), confidence_score, reasoning, key_indicators, risk_level(choose from 'Low', 'Medium', 'High', 'Critical')."
       

    def analyze_case(self, case_data) -> 'RiskAnalystOutput':  # Use quotes for forward reference
        """
        Perform risk analysis on a case using Chain-of-Thought reasoning.
        
        Implement analysis that:
        - Creates structured user prompt with case details
        - Makes OpenAI API call with system prompt
        - Parses and validates JSON response
        - Handles errors and logs operations
        - Returns validated RiskAnalystOutput
        """
        start_time = datetime.now()
        try:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": self._format_case_for_prompt(case_data)},
                    ],
                    temperature=0.3,  # Lower temperature for consistent reasoning
                    max_tokens = 1000
                )
                
                returned_response = self._extract_json_from_response(response.choices[0].message.content)
                
                output_data = RiskAnalystOutput.model_validate(json.loads(returned_response))
            except ValueError:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": f"{self.system_prompt} Please return valid JSON response that match the required schema"},
                        {"role": "user", "content": self._format_case_for_prompt(case_data)},
                    ],
                    temperature=0.3,  # Lower temperature for consistent reasoning
                    max_tokens = 1000
                )
                
                returned_response = self._extract_json_from_response(response.choices[0].message.content)
                
                output_data = RiskAnalystOutput.model_validate(json.loads(returned_response))
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_agent_action("RiskAnalyst", "analyze_case", str(case_data.case_id), str(case_data), output_data, output_data.reasoning, execution_time_ms, True)

            return output_data

        except Exception as e:
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_agent_action("RiskAnalyst", "analyze_case", str(case_data.case_id), str(case_data), "case analysis failed before completion", "JSON parsing failed", execution_time_ms, False, str(e))
            raise
    def _extract_json_from_response(self, response_content: str) -> str:

        if re.fullmatch(r"\s*", response_content):
            raise ValueError("No JSON content found")

        code_block_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_content)

        if code_block_match:
            json_text = code_block_match.group(1)
        else:
            json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
            if not json_match:
                raise ValueError("Failed to parse Risk Analyst JSON output")
            json_text = json_match.group()

        try:
            json_data = json.loads(json_text)
            RiskAnalystOutput.model_validate(json_data)
            return json.dumps(json_data)
        except Exception:
            raise ValueError("Failed to parse Risk Analyst output")


    def _format_case_for_prompt(self, case_data) -> str:
        """Format case data for the analysis prompt
        
        Create readable prompt format that includes:
        - Customer profile summary
        - Account information
        - Transaction details with key metrics
        - Financial summary statistics
        """
        if not case_data:
            raise ValueError("Case data is required.")
        else:
            case_id = case_data.case_id if case_data.case_id else None
            customer = case_data.customer if case_data.customer else None
            accounts = case_data.accounts if case_data.accounts else None
            transactions = case_data.transactions if case_data.transactions else None
            incoming_total = 0
            incoming_dates = []
            outgoing_total = 0
            outgoing_dates = []
            deposits = 0
            deposit_dates = []
            if transactions:
                for t in transactions:
                    if t.description == 'Incoming wire transfer':
                        incoming_total += t.amount
                        incoming_dates.append(t.transaction_date)
                    elif t.description == 'Outgoing wire transfer':
                        outgoing_total += t.amount
                        outgoing_dates.append(t.transaction_date)
                    elif t.transaction_type == 'Cash_Deposit':
                        deposits += t.amount
                        deposit_dates.append(t.transaction_date)

                financial_summary = f"Customer has {len(incoming_dates)} incoming wire transfer with total amount of {str(incoming_total)} on {str(set(incoming_dates))} and {len(outgoing_dates)} outgoing wire transfer with total amount of {str(outgoing_total)} on {str(set(outgoing_dates))} and {len(deposit_dates)} cash deposits with total amount of {str(deposits)} on {set(deposit_dates)}."
            else:
                financial_summary = "Customer has no transactions."
            case1 = str({"case_id": case_id, "customer": customer, "accounts": accounts, "transaction": transactions, "financial_summary": financial_summary})
            return case1

    def _format_accounts(self, accounts) -> str:
        """Format account data for the analysis prompt
        
        Create readable prompt format that includes:
        - Customer profile summary
        - Account information
        - Transaction details with key metrics
        - Financial summary statistics
        """
        if not accounts:
            raise ValueError("account data is required.")
        else:
            account_content = ''
            for account in accounts:
                account.current_balance = f"${account.current_balance:,.2f}"
                account.average_monthly_balance = f"${account.average_monthly_balance:,.2f}"
                account_content += str(account)
            return account_content

    def _format_transactions(self, transactions) -> str:
        """Format account data for the analysis prompt
        
        Create readable prompt format that includes:
        - Customer profile summary
        - Account information
        - Transaction details with key metrics
        - Financial summary statistics
        """
        if not transactions:
            raise ValueError("transactions data is required.")
        else:
            transactions_content = ''
            transaction_number = 1
            for transaction in transactions:
                transactions_content += f"{transaction_number}. {transaction.transaction_date}: {transaction.transaction_type} ${transaction.amount:,.2f} {transaction.description} at {transaction.location} "
                transaction_number += 1
            return transactions_content
# ===== PROMPT ENGINEERING HELPERS =====

def create_chain_of_thought_framework():
    """Helper function showing Chain-of-Thought structure
    
    **Analysis Framework** (Think step-by-step):
    1. **Data Review**: What does the data tell us?
    2. **Pattern Recognition**: What patterns are suspicious?
    3. **Regulatory Mapping**: Which regulations apply?
    4. **Risk Quantification**: How severe is the risk?
    5. **Classification Decision**: What category fits best?
    """
    return {
        "step_1": "Data Review - Examine all available information",
        "step_2": "Pattern Recognition - Identify suspicious indicators", 
        "step_3": "Regulatory Mapping - Connect to known typologies",
        "step_4": "Risk Quantification - Assess severity level",
        "step_5": "Classification Decision - Determine final category"
    }

def get_classification_categories():
    """Standard SAR classification categories
    """
    return {
        "Structuring": "Transactions designed to avoid reporting thresholds",
        "Sanctions": "Potential sanctions violations or prohibited parties",
        "Fraud": "Fraudulent transactions or identity-related crimes",
        "Money_Laundering": "Complex schemes to obscure illicit fund sources", 
        "Other": "Suspicious patterns not fitting standard categories"
    }

# ===== TESTING UTILITIES =====

def test_agent_with_sample_case():
    """Test the agent with a sample case
    - Create sample case data
    - Initialize agent
    - Run analysis
    - Validate results
    """
    print("🧪 Testing Risk Analyst Agent")

if __name__ == "__main__":
    print("🔍 Risk Analyst Agent Module")
    print("Chain-of-Thought reasoning for suspicious activity classification")
    print("\n📋 TODO Items:")
    print("• Design Chain-of-Thought system prompt")
    print("• Implement analyze_case method")
    print("• Add JSON parsing and validation")
    print("• Create comprehensive error handling")
    print("• Test with sample cases")
    print("\n💡 Key Concepts:")
    print("• Chain-of-Thought: Step-by-step reasoning")
    print("• Structured Output: Validated JSON responses")
    print("• Financial Crime Detection: Pattern recognition")
    print("• Audit Logging: Complete decision trails")
