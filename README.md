# Server Workspace Connector

App multiplataforma em Python (PyQt5 + Material Design) para listar e mapear pastas de rede em servidores. Traz integração nativa no macOS e mapeamento dinâmico no Windows (via `win_letter.txt`), com verificação de unidades em uso para uma conexão segura e sem conflitos.

## ✨ Funcionalidades

- **Multiplataforma:** Compatível com **macOS** (usando `smbutil` e `osascript`) e **Windows** (usando o `net use`).
- **Interface Moderna:** Desenvolvido com PyQt5 e utilizando o tema Material Design Dark para uma experiência de usuário elegante.
- **Processamento Assíncrono:** Interface sempre responsiva, pois a comunicação de rede é executada em *threads* separadas.
- **Mapeamento Inteligente (Windows):** 
  - Lê dinamicamente um arquivo `win_letter.txt` na raiz da pasta do servidor para saber em qual letra (ex: `Z:`) a unidade deve ser montada.
  - Previne sobrescrever unidades de disco locais caso a letra já esteja em uso no computador.
- **Integração Mac:** Mapeia automaticamente o compartilhamento para o diretório `/Volumes` e os exibe no Finder.

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
   source venv/bin/activate  # No Mac/Linux
   # ou no Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install PyQt5 qt-material==2.14
   ```
   > **Nota:** É recomendável fixar o `qt-material` na versão `2.14` para evitar warnings falsos de compatibilidade com o PyQt5 nas versões mais recentes.

### Rodando o App

Execute o arquivo principal:
```bash
python conectar_servidor.py
```

## 🛠 Arquitetura do Projeto

O código está estruturado para separar completamente as operações do Sistema Operacional da Interface Gráfica:

- **`core.py`:** Contém toda a lógica de negócio pesada, comandos `subprocess` nativos para autenticação via protocolo SMB (Mac/Win) e tratamento de arquivos via rede.
- **`conectar_servidor.py`:** Responsável apenas pela experiência visual do usuário (UI), instanciando a janela do PyQt5, aplicando temas do `qt-material` e rodando os workers secundários (`QThread`).

## ⚙️ Regras do `win_letter.txt` (Apenas Windows)

Para que o mapeamento funcione corretamente no Windows, é necessário criar um pequeno arquivo de texto chamado `win_letter.txt` **na raiz da pasta compartilhada no servidor**.
- O arquivo deve conter apenas a letra desejada (exemplo: `Z` ou `Z:`).
- Caso o arquivo **não exista**, não tenha uma letra válida, ou se a letra especificada já estiver sendo usada por um pendrive/HD no computador do usuário, **o sistema reportará um erro e abortará o mapeamento** daquela pasta específica por segurança.
