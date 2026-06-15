# Conectier

App em Python (Flet) para listar e mapear pastas de rede de servidores Windows diretamente no seu computador. Realiza mapeamento dinâmico de unidades via `win_letter.txt`, com verificação de conflitos para uma conexão segura.

## ✨ Funcionalidades

- **Windows Nativo:** Utiliza os comandos `net use` e `net view` para autenticação SMB e listagem de compartilhamentos.
- **Interface Moderna:** Desenvolvido com **Flet** (baseado em Flutter) para uma experiência fluida, com tema dark e componentes Material Design.
- **Processamento Assíncrono:** Interface sempre responsiva, pois as operações de rede são executadas em *threads* separadas via `asyncio`.
- **Mapeamento Inteligente:**
  - Lê um arquivo `win_letter.txt` na raiz da pasta compartilhada para saber qual letra de unidade (ex: `Z:`) deve ser usada.
  - Previne sobrescrever unidades locais caso a letra já esteja em uso.
  - Remapeia automaticamente unidades do mesmo servidor se a letra já estiver apontando para ele.
  - Salva as credenciais no **Windows Credential Manager** para reconexão automática após reiniciar.
- **Desconexão Total:** Botão dedicado para desconectar todas as unidades de rede mapeadas de uma só vez.

## 🚀 Como Executar

### Pré-requisitos

Certifique-se de ter o [Python 3](https://www.python.org/) instalado na sua máquina Windows.

### Instalação

1. Clone o repositório:
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

```bash
python conectar_servidor.py
```

## 🛠 Arquitetura do Projeto

O código está estruturado para separar completamente as operações do Sistema Operacional da Interface Gráfica:

- **`core.py`:** Contém toda a lógica de negócio — autenticação via `net use`, listagem via `net view`, mapeamento de unidades e desconexão.
- **`conectar_servidor.py`:** Responsável pela interface visual (UI Flet), instanciando o app e despachando eventos de forma assíncrona.

## ⚙️ Regras do `win_letter.txt`

Para que o mapeamento funcione corretamente, é necessário criar um arquivo de texto chamado `win_letter.txt` **na raiz de cada pasta compartilhada no servidor**.

- O arquivo deve conter apenas a letra de unidade desejada (ex: `Z` ou `Z:`).
- Caso o arquivo **não exista** ou não contenha uma letra válida, o mapeamento daquela pasta será abortado com uma mensagem de erro.
- Caso a letra especificada já esteja em uso por uma **unidade local** (pendrive, HD), o mapeamento também é abortado para evitar conflitos.
- Caso a letra já esteja em uso por uma **unidade de rede do mesmo servidor**, o mapeamento antigo é removido e refeito automaticamente.
