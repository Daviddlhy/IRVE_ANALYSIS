# IRVE_ANALYSIS

## Project Goal
The goal of this project is to use IRVE data to create a medallion architecture (Bronze, silver, gold).

## main.py
Script d'ingestion des données IRVE depuis data.gouv.fr vers Azure Data Lake (ADLS Gen2).

### Fonctionnement
- Construit un nom de fichier basé sur la date du jour: `data_gouv_YYYY-MM-DD.csv`.
- (Optionnel) Télécharge le fichier depuis `DATA_URL` via `urlretrieve`.
- Upload le fichier local vers le file system ADLS `bronze` via `DefaultAzureCredential`.

### Prérequis
- Python 3.11+ (cf. `.python-version`)
- Dépendances installées via `pyproject.toml`
- Authentification Azure active (ex: `az login`) pour `DefaultAzureCredential`
- Accès au compte ADLS `stirve1770015923`

### Utilisation
Exécution simple:
```bash
python main.py
```

Pour activer le téléchargement depuis data.gouv.fr, décommenter la ligne dans `main.py`:
```python
urlretrieve(DATA_URL, filename)
```

Pour forcer un fichier précis (debug), décommenter:
```python
filename = "data_gouv_2026-02-02.csv"
```

### Configuration
Les constantes en haut du fichier permettent de changer:
- `ACCOUNT_URL`: compte ADLS
- `FILE_SYSTEM`: conteneur / file system cible (par défaut `bronze`)
- `DATA_URL`: source de données

### Variables d'environnement (Docker)
Pour l'authentification Azure via `DefaultAzureCredential` dans un conteneur, utilisez un fichier `.env`
local (non versionné) et passez-le à `docker run`:

`.env` (exemple):
```env
AZURE_TENANT_ID=...
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
```

Un exemple est fourni dans `.env.example`.

Exécution:
```bash
docker run --rm --env-file .env irve-analysis:latest
```
