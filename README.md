# click_predict

## Configuração do Ambiente (venv)

Crie e ative um ambiente virtual para isolar as dependências do projeto.

### Linux / macOS (bash/zsh)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

**Para desativar o ambiente virtual:**

```bash
deactivate
```

---

## Instalação de Dependências

O repositório inclui um arquivo `requirements.txt`. Com o ambiente virtual ativado, rode:

```bash
pip install -r requirements.txt
```

---


## Dica

Quando adicionar ou remover bibliotecas, atualize o arquivo:

```bash
pip freeze > requirements.txt
```