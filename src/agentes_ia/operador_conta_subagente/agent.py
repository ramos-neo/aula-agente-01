from google.adk import Agent
from google.adk.tools.tool_context import ToolContext

# from google.adk.tools.function_tool import FunctionTool

FATURAS = {
    "cliente_123": [
        {
            "id": "FAT-0001",
            "valor": 100.00,
            "data_emissao": "2026-01-01",
            "data_vencimento": "2026-01-10",
            "status": "paga",
        },
        {
            "id": "FAT-0002",
            "valor": 200.00,
            "data_emissao": "2026-01-01",
            "data_vencimento": "2026-01-10",
            "status": "paga",
        },
        {
            "id": "FAT-0003",
            "valor": 300.00,
            "data_emissao": "2026-01-01",
            "data_vencimento": "2026-01-10",
            "status": "aberto",
        },
    ]
}

ASSINATURAS = {
    "cliente_123": {"plano": "Basic", "status": "ativo", "data_renovacao": "2026-01-01"}
}

def cancelar_assinatura(cliente_id: str, senha: str, tool_context: ToolContext) -> dict:
    """
    Cancela a assinatura do cliente.
    Args:
        cliente_id: str
        senha: str
    Returns:
        dict: Assinatura cancelada
    """

    if tool_context.tool_confirmation is None:
        tool_context.request_confirmation(
            hint="O valor da assinatura é alto. Tem certeza que deseja cancelar a assinatura?",
            payload={cliente_id: cliente_id, senha: ""},
        )
        return {"status": "aguardando_confirmacao"}

    if not tool_context.tool_confirmation.confirmed:
        return {
            "status": "nao_cancelado",
            "message": "Cancelamento não confirmado pelo usuário",
        }

    if senha != "keity":
        return {
            "status": "nao_cancelado",
            "message": "Senha incorreta. Cancelamento não autorizado.",
        }

    assinatura = ASSINATURAS.get(cliente_id)
    if assinatura is not None:
        assinatura["status"] = "cancelada"

    return {"status": "cancelado", "cliente_id": cliente_id}


def listar_faturas(cliente_id: str) -> dict:
    """
    Lista as faturas do cliente.
    Args:
        cliente_id: str
    Returns:
        dict: Dicionário com a lista de faturas do cliente
    """  # docstring para a função

    # simular erro de sistema
    return {"error": "Erro de sistema ao listar as faturas do cliente."}
    return {"faturas": FATURAS.get(cliente_id, [])}


# def verificar_valor_assinatura(
#     cliente_id: str,
#     valor: float
# ) -> bool:
#     return valor <= 200

def obter_status_acme() -> dict:
    """
    Obtém o status dos serviços da Acme.
    Returns:
        dict: Status dos serviços da Acme
    """
    # randomico entre operacional, manutenção e intermitentes
    import random
    status = random.choice(["operacional", "manutenção", "intermitentes"])
    return {"status": status, "mensagem": f"A empresa Acme está {status}."}

consultor_faturas_subagente = Agent(
    name="consultor_faturas",
    description="Especialista em faturas, responsável por listar as faturas do cliente e informações sobre elas.",
    instruction="""
    Voce é um consultor de faturas da Acme.
    Voce é responsável por:
    - Listar as faturas do cliente.
    - Informar ao cliente sobre o valor da fatura.
    - Informar ao cliente sobre o status da fatura.
    - Informar ao cliente sobre a data de vencimento da fatura.
    - Informar ao cliente sobre a data de emissão da fatura.
    Quando terminar faça um `tranfer_to_agent` para o agente `operador_conta` para que ele possa continuar o atendimento.
    """,
    model="gemini-3.5-flash",
    tools=[listar_faturas],
    # disallow_transfer_to_parent=False,
    disallow_transfer_to_peers=True,
    # mode="single_turn",
)

consultor_assinaturas_subagente = Agent(
    name="consultor_assinaturas",
    description="""
    Especialista em assinaturas, responsável por informar ao cliente sobre sua assinatura: 
    o plano, status e renovação.
    """,
    instruction="""
    Voce é um consultor de assinaturas da Acme.
    Voce é responsável por:
    - Informar ao cliente sobre sua assinatura: o plano, status e renovação.
    """,
    model="gemini-3.5-flash",
    tools=[cancelar_assinatura],
)

acme_status_subsagente = Agent(
    name="acme_status",
    description="Especialista em identificar se os serviços da Acme estão operacionais, em manutenção ou intermitentes.",
    instruction="""
    Voce é um consultor de status da Acme.
    Voce é responsável por:
    - Fornecer informações sobre o status dos serviços da Acme.
    """,
    model="gemini-3.5-flash-lite",
    tools=[
        obter_status_acme
    ],
    mode="single_turn",
)

# Agente coordenador
root_agent = Agent(
    name="operador_conta",
    description="Coordenador responsalve por ajudar o cliente a encontrar as informações que ele precisa.",
    instruction="""
    Voce é um atendente de conta interativo da Acme.
    Quando algum subagente retornar um erro de sistema,
    use o subagente `acme_status` para obter o status dos serviços da Acme.
    
    Caso os serviços estejam intermitentes ou em manutenção, informe o usuário que os serviços estão temporariamente indisponíveis.
    Caso o status dos serviços seja desconhecido, informe o usuário que os serviços estão temporariamente indisponíveis.
    Caso os serviços estejam operacionais, continue com o atendimento normal.

    O que são erros de sistema?
    São erros que não são causados por bugs, erros de comunicação com sistemas externos, como banco de dados, APIs de terceiros, etc.
    Esses erros porem ser temporários.
    Não informe ao usuário detalhes tecnicos sobre o erro de sistema, apenas informe que houve um erro de sistema e que estamos trabalhando para resolver o problema.
    Seja cordial e direto no seu atendimento.
    """,
    model="gemini-3.5-flash-lite",
    tools=[
        # cancelar_assinatura
        # FunctionTool(cancelar_assinatura, require_confirmation=verificar_valor_assinatura)
    ],
    sub_agents=[consultor_faturas_subagente, consultor_assinaturas_subagente, acme_status_subsagente],
)
