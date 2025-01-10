from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
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

# Função para gerar dados fictícios e salvar no PostgreSQL
def generate_fake_data_to_db():
    from scripts.generate_bank_transactions import generate_fake_data_to_db
    generate_fake_data_to_db()


# Criação do DAG
with DAG(
    dag_id='dbt_pipeline',
    default_args=default_args,
    description='DAG para executar pipelines DBT',
    schedule_interval='@daily',  # Executar diariamente
    start_date=datetime(2025, 1, 10),
    catchup=False,
    tags=['dbt', 'etl'],
) as dag:

    # Tarefa 1: Gerar Dados Fictícios no Banco de Dados
    generate_data_task = PythonOperator(
        task_id='generate_fake_data_to_db',
        python_callable=generate_fake_data_to_db,
    )

    # Tarefa 2: Executar o DBT Run
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='dbt run --project-dir /opt/airflow --profiles-dir /home/airflow/.dbt --profile airflow_postgres',
    )

    # Tarefa 3: Executar Testes DBT
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='dbt test --project-dir /opt/airflow --profiles-dir /home/airflow/.dbt --profile airflow_postgres',
    )

    # Ordem de execução das tarefas
    generate_data_task >> dbt_run >> dbt_test
