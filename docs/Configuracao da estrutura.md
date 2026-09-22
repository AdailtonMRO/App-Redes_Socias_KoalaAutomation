Você é um Arquiteto de DevOps especializado em GitHub Actions, Docker e ambientes corporativos no padrão AppSpace 2 / d9i3-templates.

Preciso que você configure a estrutura completa de CI/CD e configuração de deploy para um novo repositório, seguindo exatamente o padrão arquitetural que já utilizo em outro projeto.

---

### 📋 REQUISITOS DA ESTRUTURA

Crie os arquivos necessários na raiz do projeto conforme a árvore abaixo:

1. **`VERSION`**:
   - Arquivo de texto simples contendo a versão semântica inicial (ex: `1.0.0`).

2. **`.github/configs/deploy-config.yml`**:
   - Configurações declarativas de deploy por ambiente.
   - Parâmetros do container: `codigoAplicacao`, portas internas (`8080`), healthcheck paths, CPU/memória e réplicas.
   - Registry padrão: `localhost:5000`.
   - Mapeamento dos ambientes (`DSV`, `HMG`, `PRD`), especificando portas expostas (ex: DSV na `8082`, HMG na `8083`, PRD na `8084`), container names e variáveis de ambiente específicas.

3. **`.github/configs/pipeline-config.yml`**:
   - Metadados da aplicação (código, nome, time, stack).
   - Definições de build e testes.
   - Registry local (`localhost:5000`, insecure: true).
   - Flags de qualidade (SonarQube, SAST, DAST marcados como desativados no ambiente local).
   - Configuração de rede Docker compartilhada e serviços de infraestrutura (banco de dados, cache, endpoint de serviços emulados).

4. **Workflows em `.github/workflows/`**:

   - **`ci.yml`**:
     - `runs-on: ubuntu-latest`.
     - Trigger: `push` e `pull_request` na branch `main`.
     - Passos: checkout, setup do runtime do projeto, instalação de dependências com lockfile, lint, typecheck/testes e build de validação.

   - **`snapshot.yml`**:
     - `runs-on: [self-hosted, build-linux-x64]`.
     - Trigger: `push` em qualquer branch exceto `main` (`branches-ignore: [main]`) e `workflow_dispatch`.
     - Leitura do arquivo `VERSION` para gerar versão dinâmica `${VERSION}-${{ github.run_number }}-SNAPSHOT`.
     - `docker build` gerando tags com a versão snapshot e `:snapshot-latest`.
     - `docker push` para o registry local `localhost:5000`.
     - Deploy automático no ambiente **DSV**: parar container anterior se existir, subir novo container na rede definida, injetar variáveis de ambiente e mapear porta.
     - Validação com retry em loop do endpoint de healthcheck (`curl` checando status HTTP 200).
     - Geração de sumário Markdown via `$GITHUB_STEP_SUMMARY`.

   - **`start-release.yml`**:
     - `runs-on: [self-hosted, build-linux-x64]`.
     - Trigger: `pull_request` direcionado à `main` (`types: [opened, reopened, synchronize]`).
     - Versão no padrão Release Candidate: `${VERSION}-RC.${{ github.run_number }}`.
     - Build e push das tags RC.
     - Deploy simultâneo em **DSV** e **HMG** com healthchecks pós-deploy em cada um.
     - Sumário de Release Candidate.

   - **`finish-release.yml`**:
     - `runs-on: [self-hosted, deploy-linux-x64]`.
     - Trigger: `push` na branch `main` (após merge do PR).
     - Leitura da versão semântica limpa do arquivo `VERSION`.
     - Criação da tag Git correspondente (`git tag -a v${VERSION}`).
     - Re-tag da imagem Docker aprovada para `:latest` e `${VERSION}`, com push no registry.
     - Deploy automático em **PRD**.
     - Healthcheck pós-deploy em PRD e sumário final.

   - **`redeploy.yml`**:
     - `runs-on: [self-hosted, deploy-linux-x64]`.
     - Trigger: `workflow_dispatch` com inputs:
       * `version` (string, default: `snapshot-latest`).
       * `environment` (choice: `DSV`, `HMG`, `PRD`).
     - Validação se a imagem existe no registry local via API HTTP ou `docker pull`.
     - De-para de variáveis e portas por ambiente selecionado.
     - Recriação do container específico e verificação de saúde com healthcheck.

---

### ⚙️ DADOS DO NOVO PROJETO
(Substitua os dados abaixo pelos do seu novo repositório antes de gerar o código):
- **Código da Aplicação**: [EX: A99999]
- **Nome do Projeto / Repositório**: [EX: novo-servico]
- **Linguagem / Stack**: [EX: Node.js / Python / Go / etc.]
- **Porta interna do container**: [EX: 8080]
- **Portas externas mapeadas**: DSV ([8082]), HMG ([8083]), PRD ([8084])
- **Rede Docker**: [EX: novo-projeto-network]
- **Rota de Healthcheck**: [EX: /healthz ou /api/health]

Por favor, gere o conteúdo completo de todos os arquivos YAML e scripts necessários, comentados e prontos para uso.
