import os
import sys
from datetime import date
from pathlib import Path

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

CONTAINER_NAME = "landing"
DOMAIN = "investimentos"
ARQUIVOS = ["ativos.csv", "contas_investimento.csv", "cotacoes.csv", "ordens.csv"]

def conexao_storage() -> BlobServiceClient:
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise ValueError(
            "AZURE_STORAGE_CONNECTION_STRING não encontrada"
        )

    return BlobServiceClient.from_connection_string(connection_string)

def caminho_destino(nome_arquivo: str, data_ingestao: date) -> str:
    nome_tabela = nome_arquivo.replace(".csv", "")
    return(
        f"{DOMAIN} / {nome_tabela}/"
        f"ano={data_ingestao.year}/"
        f"mes={data_ingestao.month}/"
        f"dia={data_ingestao.day}/"
        f"{nome_arquivo}"
    )

def upload_arquivo(client: BlobServiceClient, caminho_origem: Path, destino: str) -> None:
    container = client.get_container_client(CONTAINER_NAME)
    if not container.exists():
        container.create_container()
        print(f"Container '{CONTAINER_NAME}' criado.")

    with open(caminho_origem, "rb") as arquivo:
        container.get_blob_client(destino).upload_blob(arquivo, overwrite=True)

    print(f"OK {caminho_origem} -> {CONTAINER_NAME} / {destino}")

def main() -> None:
    pasta_origem = Path(sys.argv[1] if len(sys.argv) > 1 else Path("."))

    print(f"Pasta de origem: {pasta_origem.resolve()}")
    print(f"Data de ingestão: {data_ingestao.isoformat()}\n")

    client = conexao_storage() 

    enviados, faltando = [], []
    for nome in ARQUIVOS:
        caminho = pasta_origem / nome
        if not caminho.exists():
            faltando.append(nome)
            print(f"FALTA: {caminho}")
            continue
        upload_arquivo(client, caminho, caminho_destino(nome, data_ingestao))
        enviados.append(nome)

        print(f"\n{len(enviados) / len(ARQUIVOS)} arquivos enviados")
        if faltando:
            print(f"Não encontrados: { ', '.join(faltando)}")

if __name__ == "__main__":
    main()
