# Compliance Officer Agent - ReACT Implementation  
# Implement Compliance Officer Agent using ReACT prompting

"""
Compliance Officer Agent Module

This agent generates regulatory-compliant SAR narratives using ReACT prompting.
It takes risk analysis results and creates structured documentation for 
FinCEN submission.

YOUR TASKS:
- Study ReACT (Reasoning + Action) prompting methodology
- Design system prompt with Reasoning/Action framework
- Implement narrative generation with word limits
- Validate regulatory compliance requirements
- Create proper audit logging and error handling
"""

import json
import openai
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Import foundation components
from src.foundation_sar import (
    ComplianceOfficerOutput,
    ExplainabilityLogger, 
    CaseData,
    RiskAnalystOutput
)

# Load environment variables
load_dotenv()

class ComplianceOfficerAgent:
    """
    Compliance Officer agent using ReACT prompting framework.
    
    Implement agent that:
    - Uses Reasoning + Action structured prompting
    - Generates regulatory-compliant SAR narratives
    - Enforces word limits and terminology
    - Includes regulatory citations
    - Validates narrative completeness
    """
    
    def __init__(self, openai_client, explainability_logger, model="gpt-4o-mini"):
        """Initialize the Compliance Officer Agent
        
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
        
        # Design ReACT system prompt

        self.system_prompt = """You are an senior Compliance Officer. 
        Use the following ReACT methodology: 
        "reasoning_phase": [
            "Review risk analysis findings",
            "Assess regulatory requirements", 
            "Identify compliance elements",
            "Plan narrative structure"
        ],
        "action_phase": [
            "Draft concise narrative",
            "Include specific details",
            "Reference activity patterns",
            "Use regulatory language"
        ]

        Relevant citations are "31 CFR 1020.320 (BSA)", "12 CFR 21.11 (SAR Filing)", "FinCEN SAR Instructions". Potential relevant terminologies are "Suspicious activity", "Regulatory threshold", "Financial institution", "Money laundering", "Bank Secrecy Act". Focus on BSA/AML compliance. Use BSA/SAR context as a reporting framework, not as proof of violation. Required wording are 'appears consistent with', 'may indicate' or 'raises suspicion of'. Only use 'Money laundering' as a term if the facts establish it. Only mention threshold-related concerns when the transaction facts actually support that. Do not re-invent transaction amount, use exact numbers as provided. Return the JSON fields: narrative(string), narrative_reasoning(string), regulatory_citations(list), completeness_check(bool). Word limit: 120 words. Must describe facts and suspicion, not legal conclusions."
        Must use the following format:
        Customer identification: customer name,
        Suspicious activity description and Transaction amounts and dates:
        Document the total incoming amount and related dates, and document the total outgoing amount and related dates, and document the total deposits amount and related dates. Only document total amount, not individual transaction amount. Format the amount as: $amount:,.2f,
        Location of the transaction: locations if related location information exists, else None,
        Why activity is suspicious: ...."""

    def generate_compliance_narrative(self, case_data, risk_analysis) -> 'ComplianceOfficerOutput':
        """
        Generate regulatory-compliant SAR narrative using ReACT framework.
        
        Implement narrative generation that:
        - Creates ReACT-structured user prompt
        - Includes risk analysis findings
        - Makes OpenAI API call with constraints
        - Validates narrative word count
        - Parses and validates JSON response
        - Logs operations for audit
        """
        start_time = datetime.now()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"{self._format_case_for_prompt(case_data)} {self._format_risk_analysis_for_prompt(risk_analysis)}"},
                ],
                temperature=0.2,  # Lower temperature for consistent reasoning
                max_tokens = 800
            )

            self.returned_response = self._extract_json_from_response(response.choices[0].message.content)
            print (json.loads(self.returned_response)['narrative'])
            self._validate_narrative_compliance(json.loads(self.returned_response)['narrative'], case_data, json.loads(self.returned_response)['regulatory_citations'], json.loads(self.returned_response)['completeness_check'])
            output_data = ComplianceOfficerOutput.model_validate(json.loads(self.returned_response))
            
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_agent_action("ComplianceOfficer", "generate_narrative", str(case_data.case_id), str(case_data.case_id), output_data, output_data.narrative_reasoning, execution_time_ms, True)

            return output_data
        except Exception as e:
            execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.log_agent_action("ComplianceOfficer", "generate_narrative", "unknown", "", "narrative generation failed before completion", "JSON parsing failed", execution_time_ms, False)
            raise

    def _extract_json_from_response(self, response_content: str) -> str:
        """Extract JSON content from LLM response
        
        Implement JSON extraction that handles:
        - JSON in code blocks (```json)
        - JSON in plain text
        - Malformed responses
        - Empty responses
        """
        import re
        if re.fullmatch(r"\s*", response_content):
            raise ValueError("No JSON content found")

        code_block_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_content)

        if code_block_match:
            json_text = code_block_match.group(1)
        else:
            json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
            if not json_match:
                
                raise ValueError("Failed to parse Compliance Officer JSON output")
            json_text = json_match.group()

        try:
            json_data = json.loads(json_text)
            ComplianceOfficerOutput.model_validate(json_data)
            return json.dumps(json_data)
        except Exception:
            raise ValueError("Failed to parse Compliance Officer JSON output")

    def _format_risk_analysis_for_prompt(self, risk_analysis) -> str:
        """Format risk analysis results for compliance prompt
        
        Create structured format that includes:
        - Classification and confidence
        - Key suspicious indicators
        - Risk level assessment
        - Analyst reasoning
        """
        if not risk_analysis:
            raise ValueError("Risk analysis is required.")
        else:
            classification = risk_analysis.classification if risk_analysis.classification else 0
            confidence_score = risk_analysis.confidence_score if risk_analysis.confidence_score else 0
            reasoning = risk_analysis.reasoning if risk_analysis.reasoning else 0
            key_indicators = risk_analysis.key_indicators if risk_analysis.key_indicators else 0
            risk_level = risk_analysis.risk_level if risk_analysis.risk_level else 0
            risk = str({"classification": classification, "confidence_score": str(confidence_score), "reasoning": reasoning, "key_indicators": key_indicators, "risk_level": risk_level})
            return risk

    def _validate_narrative_compliance(self, narrative: str, case_data, regulatory_citations, completeness) -> Dict[str, Any]:
        """Validate narrative meets regulatory requirements
        
        Implement validation that checks:
        - Word count (≤120 words)
        - Required elements present
        - Appropriate terminology
        - Regulatory completeness
        """
        if len(narrative.split()) > 120:
            raise ValueError("exceeds 120 word limit")
        if narrative == '':
            raise ValueError("empty narrative")
        if "violated the Bank Secrecy Act" in narrative or "in violation of BSA" in narrative:
            raise ValueError("states a legal violation as a fact")
        if "confirms" in narrative or "proves" in narrative:
            raise ValueError("unsupported certainty phrases")
        if self.incoming_total != 0 and f"${self.incoming_total:,.2f}" not in narrative and f"{self.incoming_total:,.2f}" not in narrative:
            raise ValueError('missing incoming total')
        if self.outgoing_total != 0 and f"${self.outgoing_total:,.2f}" not in narrative and f"{self.outgoing_total:,.2f}" not in narrative:
            raise ValueError('missing outgoing total')
        if self.deposits != 0 and f"${self.deposits:,.2f}" not in narrative and f"{self.deposits:,.2f}" not in narrative:
            raise ValueError("missing cash deposits total")
        if 'Customer identification' not in narrative or 'Suspicious activity description' not in narrative or 'Transaction amounts and dates' not in narrative or 'Location of the transaction' not in narrative or 'Why activity is suspicious' not in narrative:
            raise ValueError('missing required elements')
        if len(regulatory_citations) == 0:
            raise ValueError('missing regulatory citations')
        if completeness == False:
            raise ValueError('not meeting all requirements')

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
            self.incoming_total = 0
            self.incoming_dates = []
            self.outgoing_total = 0
            self.outgoing_dates = []
            self.deposits = 0
            self.deposit_dates = []
            if transactions:
                for t in transactions:
                    if t.description == 'Incoming wire transfer':
                        self.incoming_total += t.amount
                        self.incoming_dates.append(t.transaction_date)
                    elif t.description == 'Outgoing wire transfer':
                        self.outgoing_total += t.amount
                        self.outgoing_dates.append(t.transaction_date)
                    elif t.transaction_type == 'Cash_Deposit':
                        self.deposits += t.amount
                        self.deposit_dates.append(t.transaction_date)

                financial_summary = f"Customer has {len(self.incoming_dates)} incoming wire transfer with total amount of {str(self.incoming_total)} on {set(self.incoming_dates)} and {len(self.outgoing_dates)} outgoing wire transfer with total amount of {str(self.outgoing_total)} on {set(self.outgoing_dates)} and {len(self.deposit_dates)} cash deposits with total amount of {str(self.deposits)} on {set(self.deposit_dates)}."
            else:
                financial_summary = "Customer has no transactions."
            case1 = {"case_id": case_id, "customer": customer, "accounts": accounts, "transaction": transactions, "financial_summary": financial_summary}
            return case1

    def _format_transactions_for_compliance(self, transactions) -> str:
        if not transactions:
            raise ValueError("transactions data is required.")
        else:
            transactions_content = ''
            transaction_number = 1
            for transaction in transactions:
                
                transactions_content += f"{transaction_number}. {transaction.transaction_date}: ${transaction.amount:,.2f} {transaction.transaction_type} {transaction.description} at {transaction.location} via {transaction.method}"

                transaction_number += 1
            return transactions_content

# ===== REACT PROMPTING HELPERS =====

def create_react_framework():
    """Helper function showing ReACT structure
    
    **REASONING Phase:**
    1. Review the risk analyst's findings
    2. Assess regulatory narrative requirements
    3. Identify key compliance elements
    4. Consider narrative structure
    
    **ACTION Phase:**
    1. Draft concise narrative (≤120 words)
    2. Include specific details and amounts
    3. Reference suspicious activity pattern
    4. Ensure regulatory language
    """
    return {
        "reasoning_phase": [
            "Review risk analysis findings",
            "Assess regulatory requirements", 
            "Identify compliance elements",
            "Plan narrative structure"
        ],
        "action_phase": [
            "Draft concise narrative",
            "Include specific details",
            "Reference activity patterns",
            "Use regulatory language"
        ]
    }

def get_regulatory_requirements():
    """Key regulatory requirements for SAR narratives
    """
    return {
        "word_limit": 120,
        "required_elements": [
            "Customer identification",
            "Suspicious activity description", 
            "Transaction amounts and dates (calculate the total incoming amount and document related dates, and do the same for the total of outgoing transactions and cash deposits)",
            "Location of the transaction if location information exists",
            "Why activity is suspicious",
        ],
        "terminology": [
            "Suspicious activity",
            "Regulatory threshold",
            "Financial institution",
            "Money laundering",
            "Bank Secrecy Act"
        ],
        "citations": [
            "31 CFR 1020.320 (BSA)",
            "12 CFR 21.11 (SAR Filing)",
            "FinCEN SAR Instructions"
        ]
    }

# ===== TESTING UTILITIES =====

def test_narrative_generation():
    """Test the agent with sample risk analysis
    
    Use this function to test your implementation:
    - Create sample risk analysis results
    - Initialize compliance agent
    - Generate narrative
    - Validate compliance requirements
    """
    print("🧪 Testing Compliance Officer Agent")

def validate_word_count(text: str, max_words: int = 120) -> bool:
    """Helper to validate word count
    """
    word_count = len(text.split())
    return word_count <= max_words

if __name__ == "__main__":
    print("✅ Compliance Officer Agent Module")
    print("ReACT prompting for regulatory narrative generation")
    print("\n📋 TODO Items:")
    print("• Design ReACT system prompt")
    print("• Implement generate_compliance_narrative method")
    print("• Add narrative validation (word count, terminology)")
    print("• Create regulatory citation system")
    print("• Test with sample risk analysis results")
    print("\n💡 Key Concepts:")
    print("• ReACT: Reasoning + Action structured prompting")
    print("• Regulatory Compliance: BSA/AML requirements")
    print("• Narrative Constraints: Word limits and terminology")
    print("• Audit Logging: Complete decision documentation")
