import datetime
import logging
import sys
from urllib.request import urlretrieve

from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient

ACCOUNT_URL = "https://stirve1770015923.dfs.core.windows.net/"
FILE_SYSTEM = "bronze"
DATA_URL = (
    "https://www.data.gouv.fr/api/1/datasets/r/eb76d20a-8501-400e-b336-d85724de5435"
)


def run_upload(
    filename: str, account_url: str = ACCOUNT_URL, file_system: str = FILE_SYSTEM
) -> None:
    try:
        credential = DefaultAzureCredential()
        service_client = DataLakeServiceClient(account_url, credential=credential)

        file_system_client = service_client.get_file_system_client(
            file_system=file_system
        )

        file_client = file_system_client.get_file_client(filename)

        logging.info("Début du transfert...")
        with open(filename, "rb") as f:
            file_client.upload_data(f, overwrite=True)
        logging.info("Fichier envoyé avec succès.")

    except Exception as e:
        logging.exception("Erreur lors de l'upload: %s", e)
        raise


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logging.info("Hello from irve-analysis!")
    date_str = datetime.date.today().isoformat()
    filename = f"data_gouv_{date_str}.csv"
    # filename = "data_gouv_2026-01-30.csv"  # override for debugging
    try:
        urlretrieve(DATA_URL, filename)
        logging.info("Fichier téléchargé : %s", filename)
    except Exception as e:
        logging.exception("Erreur lors du téléchargement: %s", e)
        sys.exit(1)
    try:
        run_upload(filename)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
