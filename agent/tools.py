from langchain.tools import tool
from database.bigquery_client import get_traffic_volume, get_channel_performance

@tool
def tool_get_traffic_volume(traffic_source: str, start_date: str, end_date: str) -> str:
    """
    Use esta ferramenta para descobrir o volume total de usuários de um canal de mídia (traffic_source) específico em um determinado período.
    Os canais válidos são: 'Search', 'Organic', 'Facebook', 'Email', 'Display'.
    As datas de início (start_date) e fim (end_date) DEVEM estar no formato 'YYYY-MM-DD'.
    """
    resultado = get_traffic_volume(traffic_source, start_date, end_date)
    return str(resultado)

@tool
def tool_get_channel_performance(start_date: str, end_date: str) -> str:
    """
    Use esta ferramenta para descobrir o ROI, performance, receita total, número de pedidos ou qual é o melhor canal de mídia em um determinado período.
    Ela retorna um ranking de todos os canais com seus usuários, pedidos e receita real (excluindo cancelados).
    As datas DEVEM estar no formato 'YYYY-MM-DD'.
    """
    resultado = get_channel_performance(start_date, end_date)
    return str(resultado)

todas_as_tools = [tool_get_traffic_volume, tool_get_channel_performance]