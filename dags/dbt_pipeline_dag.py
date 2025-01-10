from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Configuração básica do DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='dbt_pipeline',
    default_args=default_args,
    description='DAG para executar pipelines DBT',
    schedule_interval='@daily',  # Executar diariamente
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['dbt', 'etl'],
) as dag:

    # Tarefa 1: Executar o DBT Run
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --profiles-dir /opt/dbt',
        dag=dag,
    )

    # Tarefa 2: Executar Testes DBT
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test --profiles-dir /opt/dbt',
        dag=dag,
    )

    # Ordem de execução das tarefas
    dbt_run >> dbt_test
