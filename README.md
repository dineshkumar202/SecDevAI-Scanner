# SecDevAI-Scanner

AI-powered security-analysis web app (Flask) + full CI/CD pipeline deploying to Azure AKS.

**Features**
- Paste code/logs and analyze with a configurable LLM API (Gemini or other).
- Full pipeline: GitHub Actions → build/push to ACR → Ansible deploy to AKS.
- Infrastructure with Terraform.

See repository layout in project root.

## Quick local run (dev)
1. Copy `.env.example` → `.env` and add `GEMINI_API_KEY` (or set env var).
2. From `app/`:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```
3. App runs on http://0.0.0.0:5000

## Docker (local)
```bash
cd app
docker build -t secdevai-scanner:local .
docker run -p 5000:5000 -e GEMINI_API_KEY="$GEMINI_API_KEY" secdevai-scanner:local
```

## Terraform / Azure / CI/CD overview
- `terraform/` provisions: resource group, ACR, AKS (system-assigned identity), role assignment to let AKS pull from ACR.
- GitHub Actions builds and pushes image to ACR and runs Ansible to patch K8s deployment image + GEMINI_API_KEY.

**Security notes**
- Never commit `GEMINI_API_KEY` or Azure credentials to git.
- Use GitHub Secrets:
  - `AZURE_CREDENTIALS` (service principal JSON)
  - `AZURE_SUBSCRIPTION_ID`
  - `AZURE_TENANT_ID`
  - `GEMINI_API_KEY`
- For production, use AKS managed identity / AAD Pod Identity instead of in-pod secrets where possible.
