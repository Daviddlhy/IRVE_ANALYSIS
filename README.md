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

## CI/CD GitHub Actions vers Azure Container Registry (ACR)

Le workflow est dans:
`/Users/daviddelhaye/Documents/Github/IRVE_ANALYSIS/.github/workflows/acr-build-push.yml`

Il build l'image Docker et la push automatiquement vers ACR sur chaque push sur `main`.
Authentification: GitHub OIDC vers Azure AD (sans mot de passe / sans client secret).

### 1) Créer une application + service principal Azure

```bash
ACR_NAME="<ton-acr-name>"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
ACR_ID=$(az acr show --name "$ACR_NAME" --query id -o tsv)

APP_NAME="github-acr-push-irve"
APP_ID=$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)

az ad sp create --id "$APP_ID"
az role assignment create \
  --assignee "$APP_ID" \
  --role AcrPush \
  --scope "$ACR_ID"
```

Récupérer le tenant:

```bash
TENANT_ID=$(az account show --query tenantId -o tsv)
echo "APP_ID=$APP_ID"
echo "TENANT_ID=$TENANT_ID"
echo "SUBSCRIPTION_ID=$SUBSCRIPTION_ID"
```

### 2) Créer la fédération OIDC GitHub -> Azure AD

Remplace `<ORG>` et `<REPO>`:

```bash
cat > federated-credential.json <<'JSON'
{
  "name": "github-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:<ORG>/<REPO>:ref:refs/heads/main",
  "description": "GitHub Actions main branch",
  "audiences": [
    "api://AzureADTokenExchange"
  ]
}
JSON

az ad app federated-credential create \
  --id "$APP_ID" \
  --parameters federated-credential.json
```

### 3) Configurer GitHub (Repository Settings)

Dans `Settings > Secrets and variables > Actions`:

- `Secrets`:
  - `AZURE_CLIENT_ID` = `APP_ID`
  - `AZURE_TENANT_ID` = `TENANT_ID`
  - `AZURE_SUBSCRIPTION_ID` = `SUBSCRIPTION_ID`
- `Variables`:
  - `ACR_NAME` = ex: `monacr`
  - `IMAGE_NAME` = ex: `irve_ingestion`

### 4) Déclencher le pipeline

- Push sur la branche `main`, ou
- Lancer manuellement via l'onglet `Actions` (`workflow_dispatch`).

### 5) Vérifier l'image dans ACR

```bash
az acr repository show-tags \
  --name "<ton-acr-name>" \
  --repository "<image-name>" \
  --output table
```
