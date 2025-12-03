import os
import json
import sys
from openai import OpenAI


try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"Error initializing OpenAI client: {e}", file=sys.stderr)
    sys.exit(1)
    
CODE_CHANGES = os.environ.get("CODE_CHANGES", "")

if not CODE_CHANGES:
    result = {"score": 10, "summary": "No code changes detected for review.", "issues": []}
    with open("ai_review_result.json", "w") as f:
        json.dump(result, f)
    sys.exit(0)


SYSTEM_PROMPT = (
    "You are a Senior Software Engineer specializing in security and code quality. "
    "Your task is to review a git diff and provide a structured assessment. "
    "Focus on identifying potential bugs, security risks (like XSS or injection risks), and performance issues. "
    "Respond ONLY with a single JSON object. DO NOT include any text, markdown, or commentary outside the JSON."
)

USER_PROMPT = f"""
Review the following git diff code changes:
---
{CODE_CHANGES[:15000]}
---
Provide a final quality score out of 10.
If no issues are found, the score is 10.
The JSON must strictly adhere to this format:
{{
"score": integer,
"summary": "A concise, 1-2 sentence summary of the review.",
"issues": [
    {{"file": "filename_or_path", "description": "Description of the issue and its potential impact."}}
]
}}
"""

# 4. Make the API Call
try:
    response = client.chat.completions.create(
        model="gpt-4o-mini", # Use a cost-effective, fast model for review
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT}
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    
    # 5. Extract and validate the JSON response
    ai_response_text = response.choices[0].message.content.strip()
    review_data = json.loads(ai_response_text)
    
except Exception as e:
    print(f"OpenAI API call failed or JSON parsing error: {e}", file=sys.stderr)
    # Return a safe, low score on failure to force human review
    review_data = {"score": 1, "summary": "AI Review failed due to API or parsing error.", "issues": [{"file": "N/A", "description": str(e)}]}

# 6. Save the final JSON result to a file for the next GitHub Action step
with open("ai_review_result.json", "w") as f:
    json.dump(review_data, f)