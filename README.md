# Duck-Gallery

Duck-Gallery é uma aplicação que facilita a catalogação de imagens utilizando o LabelMe e o MongoDB. O projeto oferece schemas personalizados e uma interface de linha de comando (CLI) que permite executar diversas operações, como:

- Baixar imagens
- Inserir dados no banco de dados
- Atualizar registros
- Visualizar informações consolidadas das coleções

## Tabela de Conteúdos

- [Recursos](#recursos)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
  - [Módulo Database](#módulo-database)
  - [Módulo DB_Backend](#módulo-db_backend)
  - [Módulo Do_Label](#módulo-do_label)
- [Ativando o Ambiente Virtual](#ativando-o-ambiente-virtual)
- [Uso](#uso)
- [CLI - Interface de Linha de Comando](#cli---interface-de-linha-de-comando)

## Recursos

- **Integração entre LabelMe e MongoDB:** Facilita o gerenciamento e a visualização de imagens.
- **Schemas Personalizados:** Adequados para a catalogação e consulta dos dados.
- **Interface CLI:** Permite executar operações essenciais de forma simples e prática.

## Requisitos

- **Python 3.12**
- **Docker**

## Instalação

Cada módulo do projeto requer uma instalação individual. Siga as instruções específicas para cada um:

### Módulo Database

1. **Preparação do Dump:**
   - Insira o seu dump no diretório `\database\dump`.
2. **Inicialização:**
   - Na primeira vez que o contêiner for iniciado, o dump será copiado automaticamente para o diretório correto.
3. **Reset do Banco de Dados:**
   - Para resetar, exclua os arquivos dentro da pasta `\database\data`.

### Módulo DB_Backend

1. **Criação do Ambiente Virtual:**
   ```bash
   python -m venv <nome_ambiente>
   ```
2. **Ativando o Ambiente Virtual:**
   - **Windows:**
     ```bash
     <nome_ambiente>\Scripts\activate
     ```
   - **Linux / macOS:**
     ```bash
     source <nome_ambiente>/bin/activate
     ```
3. **Instalação dos Pacotes:**
   ```bash
   pip install .
   ```

### Módulo Do_Label

1. **Criação do Ambiente Virtual:**
   ```bash
   python -m venv <nome_ambiente>
   ```
2. **Ativando o Ambiente Virtual:**
   - **Windows:**
     ```bash
     <nome_ambiente>\Scripts\activate
     ```
   - **Linux / macOS:**
     ```bash
     source <nome_ambiente>/bin/activate
     ```
3. **Instalação dos Pacotes:**
   ```bash
   pip install -r requirements.txt
   ```

## Ativando o Ambiente Virtual

Após criar o ambiente virtual com o comando:

```bash
python -m venv <nome_ambiente>
```

Utilize os comandos abaixo para ativá-lo conforme o seu sistema operacional:

- **Windows:**
  ```bash
  <nome_ambiente>\Scripts\activate
  ```
- **Linux / macOS:**
  ```bash
  source <nome_ambiente>/bin/activate
  ```

## Uso

Antes de utilizar o CLI do Duck-Gallery, é necessário subir o contêiner do banco de dados:

### 1. Subindo o Contêiner do MongoDB
Execute o comando abaixo no terminal:

```bash
docker-compose -f database/docker-compose.yaml up
```

Após o banco de dados estar rodando, você poderá utilizar a interface de linha de comando para executar as operações desejadas.

## CLI - Interface de Linha de Comando

O CLI do Duck-Gallery foi desenvolvido utilizando o Typer e fornece os seguintes comandos:

- **`next`**
  - **Descrição:** Busca e baixa o próximo conjunto de imagens que ainda não estão catalogadas para o álbum informado.
  - **Argumentos/Opções:**
    - `album_key` (argumento obrigatório): Nome do álbum. Deve ser um dos seguintes valores: `HISTORICA`, `EXPLORACAO`, `REFINO`, `GAS`, `ELETRICA`, `TRANSPORTE`, `RENOVAVEL`, `PATROCINIO`.
    - `--limit` (opcional): Quantidade de imagens a serem baixadas (padrão: 20).

- **`post`**
  - **Descrição:** Insere as imagens catalogadas no banco de dados a partir dos arquivos JSON correspondentes e, em seguida, exclui a pasta temporária utilizada para armazená-las.

- **`update`**
  - **Descrição:** Atualiza as imagens catalogadas no banco de dados utilizando os arquivos JSON e remove a pasta temporária após a operação.

- **`recent`**
  - **Descrição:** Baixa as imagens catalogadas mais recentes.
  - **Opções:**
    - `--limit` (opcional): Quantidade de imagens a serem baixadas (padrão: 20).

- **`describe`**
  - **Descrição:** Exibe informações consolidadas das imagens catalogadas.
  - **Opções:**
    - `--album-key`: Nome do álbum selecionado (padrão: `"NONE"`, que indica que não há filtro por álbum).
    - `--coverage`: Se ativado, mostra a porcentagem de cobertura (relação entre imagens catalogadas e disponíveis).
    - `--labels`: Se ativado, exibe uma contagem dos rótulos (labels) presentes nas imagens catalogadas.

- **`--version`**
  - **Descrição:** Exibe a versão atual da aplicação (atualmente `0.0.1`).

Caso nenhum comando seja informado, o CLI apresenta uma mensagem de orientação indicando os comandos disponíveis: `next`, `post`, `recent` ou `describe`.

