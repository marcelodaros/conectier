# Server Workspace Connector

App em Python (Flet) para listar e mapear pastas de rede em servidores. Traz mapeamento dinâmico no Windows (via `win_letter.txt`), com verificação de unidades em uso para uma conexão segura e sem conflitos.

## ✨ Funcionalidades

- **Compatibilidade:** Focado no **Windows** (usando o `net use`).
- **Interface Moderna:** Desenvolvido com **Flet** (baseado em Flutter) para uma experiência de usuário fluida, com tema dark e componentes Material Design nativos.
- **Processamento Assíncrono:** Interface sempre responsiva, pois a comunicação de rede é executada em *threads* separadas.
- **Mapeamento Inteligente:** 
  - Lê dinamicamente um arquivo `win_letter.txt` na raiz da pasta do servidor para saber em qual letra (ex: `Z:`) a unidade deve ser montada.
  - Previne sobrescrever unidades de disco locais caso a letra já esteja em uso no computador.

## 🚀 Como Executar

### Pré-requisitos
Certifique-se de ter o [Python 3](https://www.python.org/) instalado na sua máquina.

### Instalação

1. Clone o repositório para o seu computador:
   ```bash
   git clone https://github.com/marcelodaros/conectier.git
   cd conectier
   ```

2. (Opcional, mas recomendado) Crie um ambiente virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Rodando o App

Execute o arquivo principal:
```bash
python conectar_servidor.py
```

## 🛠 Arquitetura do Projeto

O código está estruturado para separar completamente as operações do Sistema Operacional da Interface Gráfica:

- **`core.py`:** Contém toda a lógica de negócio pesada, comandos `subprocess` nativos para autenticação via protocolo SMB e tratamento de arquivos via rede.
- **`conectar_servidor.py`:** Responsável apenas pela experiência visual do usuário (UI), instanciando o app Flet e manipulando os eventos de forma assíncrona (`asyncio`).

## ⚙️ Regras do `win_letter.txt`

Para que o mapeamento funcione corretamente, é necessário criar um pequeno arquivo de texto chamado `win_letter.txt` **na raiz da pasta compartilhada no servidor**.
- O arquivo deve conter apenas a letra desejada (exemplo: `Z` ou `Z:`).
- Caso o arquivo **não exista**, não tenha uma letra válida, ou se a letra especificada já estiver sendo usada por um pendrive/HD no computador do usuário, **o sistema reportará um erro e abortará o mapeamento** daquela pasta específica por segurança.
