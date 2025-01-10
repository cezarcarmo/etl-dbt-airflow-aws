import csv
import random
import os
from faker import Faker
from datetime import datetime, timedelta

def generate_transactions(output_file, num_transactions=1000):
    
    # Verificar se o diretório existe
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    fake = Faker()
    Faker.seed(42)
    random.seed(42)

    # Definição de categorias e tipos de transação
    transaction_types = ["transferência", "pagamento", "saque", "depósito"]
    categories = ["aluguel", "alimentação", "lazer", "transporte", "educação", "saúde"]

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Cabeçalhos
        writer.writerow([
            "transaction_id",
            "account_id",
            "transaction_date",
            "amount",
            "transaction_type",
            "category",
            "description"
        ])

        # Gerando transações
        for transaction_id in range(1, num_transactions + 1):
            account_id = random.randint(1000, 9999)  # IDs fictícios para contas
            transaction_date = fake.date_time_between(start_date='-2y', end_date='now')
            amount = round(random.uniform(-1000.0, 5000.0), 2)  # Valores entre -1000 e 5000
            transaction_type = random.choice(transaction_types)
            category = random.choice(categories)
            description = fake.sentence(nb_words=6)

            writer.writerow([
                transaction_id,
                account_id,
                transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                amount,
                transaction_type,
                category,
                description
            ])

    print(f"Arquivo gerado: {output_file}")

if __name__ == "__main__":
    # Caminho para salvar o arquivo CSV
    output_file = "data/bank_transactions.csv"
    generate_transactions(output_file, num_transactions=1000)
