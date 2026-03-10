import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

client = bigquery.Client()

def testar_conexao() -> dict:
    """Testa a conexão contando o número de usuários no dataset público."""
    query = """
        SELECT count(*) as total_users
        FROM `bigquery-public-data.thelook_ecommerce.users`
    """
    try:
        query_job = client.query(query)
        resultados = query_job.result()
        
        for linha in resultados:
            return {"status": "sucesso", "total_usuarios": linha.total_users}
            
    except Exception as e:
        return {"status": "erro", "detalhe": str(e)}

def get_traffic_volume(traffic_source: str, start_date: str, end_date: str) -> dict:
    """
    Busca o volume de usuários filtrado por origem de tráfego e período.
    Esta é uma das ferramentas que a IA poderá chamar autonomamente.
    """
    
    query = """
        SELECT count(id) as total_users
        FROM `bigquery-public-data.thelook_ecommerce.users`
        WHERE traffic_source = @traffic_source
          AND DATE(created_at) >= DATE(@start_date)
          AND DATE(created_at) <= DATE(@end_date)
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("traffic_source", "STRING", traffic_source),
            bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
            bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        resultados = query_job.result()
        
        for linha in resultados:
            return {
                "status": "sucesso", 
                "traffic_source": traffic_source,
                "total_users": linha.total_users
            }
            
    except Exception as e:
        return {"status": "erro", "detalhe": str(e)}

def get_channel_performance(start_date: str, end_date: str) -> dict:
    """
    Calcula a performance (receita, pedidos e usuários) de cada canal de tráfego.
    Cruza users, orders e order_items usando JOINs.
    """
    
    query = """
        SELECT 
            u.traffic_source,
            COUNT(DISTINCT u.id) as total_users,
            COUNT(DISTINCT o.order_id) as total_orders,
            ROUND(SUM(oi.sale_price), 2) as total_revenue
        FROM `bigquery-public-data.thelook_ecommerce.users` u
        JOIN `bigquery-public-data.thelook_ecommerce.orders` o ON u.id = o.user_id
        JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi ON o.order_id = oi.order_id
        WHERE LOWER(o.status) NOT IN ('cancelled', 'returned')
          AND DATE(o.created_at) >= DATE(@start_date)
          AND DATE(o.created_at) <= DATE(@end_date)
        GROUP BY u.traffic_source
        ORDER BY total_revenue DESC
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "STRING", start_date),
            bigquery.ScalarQueryParameter("end_date", "STRING", end_date),
        ]
    )
    
    try:
        query_job = client.query(query, job_config=job_config)
        resultados = query_job.result(timeout=30)
        
        performance_data = []
        for linha in resultados:
            performance_data.append({
                "traffic_source": linha.traffic_source,
                "total_users": linha.total_users,
                "total_orders": linha.total_orders,
                "total_revenue": float(linha.total_revenue) if linha.total_revenue else 0.0
            })
            
        return {"status": "sucesso", "data": performance_data}
            
    except Exception as e:
        return {"status": "erro", "detalhe": str(e)}