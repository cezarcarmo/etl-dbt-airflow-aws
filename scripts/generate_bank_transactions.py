import random
from faker import Faker
import psycopg2

def generate_fake_data_to_db():
    fake = Faker()
    conn = psycopg2.connect(
        dbname="airflow",
        user="airflow",
        password="airflow",
        host="postgres",  # Nome do serviço no docker-compose.yml
        port="5432"
    )
    cursor = conn.cursor()
    # Limpa a tabela antes de inserir novos dados
    cursor.execute("TRUNCATE TABLE bank_transactions;")

    # Insere novos dados fictícios
    for _ in range(1000):
        account_id = random.randint(1000, 9999)
        transaction_date = fake.date_time_between(start_date='-2y', end_date='now')
        amount = round(random.uniform(-1000.0, 5000.0), 2)
        transaction_type = random.choice(["transferência", "pagamento", "saque", "depósito"])
        category = random.choice(["aluguel", "alimentação", "lazer", "transporte", "educação", "saúde"])
        description = fake.sentence(nb_words=6)

        cursor.execute("""
            INSERT INTO bank_transactions (account_id, transaction_date, amount, transaction_type, category, description)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (account_id, transaction_date, amount, transaction_type, category, description))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Dados inseridos no banco com sucesso.")

if __name__ == "__main__":
    generate_fake_data_to_db()
