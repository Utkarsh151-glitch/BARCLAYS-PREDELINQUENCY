from langchain.llms import OpenAI


llm = OpenAI(temperature=0.2)


def generate_playbook(risk_level, early_signals):

    prompt = f"""
    Customer risk level is {risk_level}.
    Early warning signals:
    {early_signals}

    Generate a step-by-step pre-delinquency intervention playbook.
    """

    response = llm.invoke(prompt)
    return response
