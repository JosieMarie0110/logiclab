import os
import gradio as gr
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CYBERSECURITY_CONCEPTS = [
    "Zero Trust",
    "Network Access Control (NAC)",
    "Endpoint Detection and Response (EDR)",
    "Security Information and Event Management (SIEM)",
    "Security Orchestration, Automation, and Response (SOAR)",
    "SASE",
    "CASB",
    "Identity and Access Management (IAM)",
    "Network Segmentation",
    "Threat Intelligence",
    "MFA",
    "SSO",
    "XDR",
    "ZTNA",
    "Secure Web Gateway (SWG)",
    "Firewall",
    "IDS",
    "IPS",
    "DLP",
    "Microsegmentation",
]

SYSTEM_PROMPT = """
You are Logic Lab, an AI-powered cybersecurity learning assistant.

Be clear, structured, practical, and easy to study.
Use markdown formatting.
"""

def build_prompt(mode: str, concept: str, custom_query: str) -> str:
    query = custom_query.strip() if custom_query.strip() else concept.strip()

    if mode == "Explain":
        return f"""
Explain this cybersecurity concept clearly for study:

{query}

Use this format:

# Concept
# Definition
# Why It Exists
# Where It Is Used
# Related Concepts
# Common Misconceptions
# Business Value
# Example
"""
    elif mode == "Compare":
        return f"""
Compare these cybersecurity concepts clearly for study:

{query}

Use this format:

# Comparison

| Category | Concept 1 | Concept 2 |

# Key Takeaway
# When Each Is Most Useful
"""
    elif mode == "Map":
        return f"""
Create a concept map for this cybersecurity topic:

{query}

Use this format:

# Concept Map

Then provide a text hierarchy.

# How To Read This Map
# Key Study Notes
"""
    else:
        return query


def ask_logic_lab(mode: str, concept: str, custom_query: str) -> str:
    query = custom_query.strip() if custom_query.strip() else concept.strip()

    if not query:
        return "Please select a concept or type a study request."

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Error: OPENAI_API_KEY is not set in your terminal."

    prompt = build_prompt(mode, concept, custom_query)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {str(e)}"


def load_prompt_suggestion(mode: str, concept: str) -> str:
    concept = concept.strip() if concept else "Zero Trust"

    if mode == "Explain":
        return f"Explain {concept}"
    elif mode == "Compare":
        if "SIEM" in concept:
            return "Compare SIEM vs SOAR"
        elif "NAC" in concept:
            return "Compare NAC vs EDR"
        else:
            return f"Compare {concept} vs a related concept"
    elif mode == "Map":
        return f"Map {concept} and related concepts"

    return ""


with gr.Blocks(title="Logic Lab") as demo:
    gr.Markdown(
        """
# Logic Lab
Cybersecurity concept learning engine
"""
    )

    with gr.Row():
        with gr.Column(scale=1):
            mode = gr.Radio(
                choices=["Explain", "Compare", "Map"],
                value="Explain",
                label="Learning Mode"
            )

            concept = gr.Dropdown(
                choices=CYBERSECURITY_CONCEPTS,
                value="Zero Trust",
                label="Select Concept",
                allow_custom_value=True
            )

            custom_query = gr.Textbox(
                label="Study Prompt",
                placeholder="Explain Zero Trust | Compare SIEM vs SOAR | Map SASE",
                lines=2,
                max_lines=3
            )

            suggestion_btn = gr.Button("Load Study Prompt")
            generate_btn = gr.Button("Generate Insight", variant="primary")

        with gr.Column(scale=3):
            output = gr.Markdown("Your study output will appear here.")

    suggestion_btn.click(
        fn=load_prompt_suggestion,
        inputs=[mode, concept],
        outputs=[custom_query]
    )

    generate_btn.click(
        fn=ask_logic_lab,
        inputs=[mode, concept, custom_query],
        outputs=[output]
    )

if __name__ == "__main__":
    demo.launch()
