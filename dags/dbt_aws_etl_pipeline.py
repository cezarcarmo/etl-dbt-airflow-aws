from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.glue_crawler import GlueCrawlerOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO

# Configurações básicas
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Função para exportar dados refinados do PostgreSQL para S3 no formato Parquet
def export_to_s3():
    # Conectar ao banco local
    pg_hook = PostgresHook(postgres_conn_id="airflow_postgres")
    connection = pg_hook.get_conn()
    cursor = connection.cursor()

    # Extrair dados refinados
    cursor.execute("SELECT * FROM public.refined_transations;")  # Corrigido o nome da tabela
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)

    # Salvar como Parquet no S3
    s3_hook = S3Hook(aws_conn_id="aws_default")
    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)

    # Carregar para o bucket S3
    s3_hook.load_file_obj(
        file_obj=parquet_buffer,
        key="refined_transactions/refined_transactions.parquet",
        bucket_name="etl-dbt-athena-data",
        replace=True
    )
    print("Dados exportados para o S3 com sucesso!")

# DAG principal
with DAG(
    dag_id='dbt_aws_etl_pipeline',
    default_args=default_args,
    description='Pipeline ETL com DBT, S3 e Glue Crawler',
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['dbt', 'aws', 'glue'],
) as dag:

    # Tarefa 1: Executar os modelos DBT
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --project-dir /opt/airflow --profiles-dir /home/airflow/.dbt --profile airflow_postgres',
    )

    # Tarefa 2: Exportar os dados refinados para o S3
    export_to_s3_task = PythonOperator(
        task_id='export_to_s3',
        python_callable=export_to_s3,
    )

    # Tarefa 3: Executar o Glue Crawler para mapear os dados no Glue Catalog
    glue_crawler_task = GlueCrawlerOperator(
        task_id='glue_crawler',
        config={"Name": "etl_dbt_crawler"},  # Nome do crawler criado no Glue
        aws_conn_id='aws_default',
        wait_for_completion=True,  # Esperar a conclusão do crawler
    )

    # Ordem das tarefas no pipeline
    dbt_run >> export_to_s3_task >> glue_crawler_task
