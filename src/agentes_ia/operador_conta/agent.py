from google.adk import Agent
from google.adk.tools import ToolContext
from google.adk.tools.function_tool import FunctionTool

FATURAS = {
    "cliente_123": [
        {
            "id": "FAT-0001",
            "valor": 100.00,
            "data_emissao": "2026-01-01",
            "data_vencimento": "2026-01-10",
            "status": "paga"
        },
        {
            "id": "FAT-0002",
            "valor": 200.00,
            "data_emissao": "2026-01-01",
            "data_vencimento": "2026-01-10",
            "status": "paga"
        },
        {
            "id": "FAT-0003",
            "valor": 300.00,
            "data_emissao": "2026-01-01",
            "data_vencimento": "2026-01-10",
            "status": "aberto"
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
            payload={
                cliente_id: cliente_id,
                senha: ""
            }
        )
        return {"status": "aguardando_confirmacao"}

    if not tool_context.tool_confirmation.confirmed:
        return {"status": "nao_cancelado", "message": "Cancelamento não confirmado pelo usuário"}

    if senha != "keity":
        return {"status": "nao_cancelado", "message": "Senha incorreta. Cancelamento não autorizado."}

    assinatura = ASSINATURAS.get(cliente_id)
    if assinatura is not None:
        assinatura["status"] = "cancelada"

    return {
        "status": "cancelado",
        "cliente_id": cliente_id
    }

def listar_faturas(cliente_id: str) -> dict:
    """ 
    Lista as faturas do cliente.
    Args:
        cliente_id: str
    Returns:
        dict: Dicionário com a lista de faturas do cliente
    """ # docstring para a função
    return {
        "faturas": FATURAS.get(cliente_id, [])
    }


def verificar_valor_assinatura(cliente_id: str, valor: float) -> bool:
    return valor <= 200;

root_agent = Agent(
    name="operador_conta",
    instruction="""
    Voce é um atendente de conta interativo da Acme.
    Voce é responsável por:
    - Informar ao cliente sobre sua assinatura: o plano, status e renovação.
    - Tirar dúvidas sobre as faturas do cliente.
    - Cancelar a assinatura do cliente, se solicitado pelo cliente.
    O usuário precisa fornecer o ID do cliente para que voce possa buscar as informações corretamente.
    Seja cordial e direto no seu atendimento.
    """,
    model="gemini-3.5-flash-lite",
    tools=[
        listar_faturas, 
        cancelar_assinatura
        # FunctionTool(cancelar_assinatura, require_confirmation=verificar_valor_assinatura)
    ]
)
