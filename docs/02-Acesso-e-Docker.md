Viewed 02-Acesso-e-Docker.md:1-100
Viewed SETUP-SERVIDOR-PASSO-A-PASSO.md:1-337
Viewed 05-Acesso-Externo.md:1-229

Aqui está um guia estruturado explicando toda a arquitetura de acesso e permissões do seu servidor, seguido pelo **prompt pronto e completo** para você fornecer a outra IA para reproduzir essa mesma configuração de segurança em outro servidor.

---

### Resumo da Arquitetura de Acesso e Permissões do Servidor

1. **Acesso ao Sistema Operacional (Ubuntu Server Headless)**:
   * **Usuário Não-Root**: O sistema opera com usuário dedicado (`executamais`), evitando o uso direto de `root`.
   * **Permissões Administrativas**: O usuário pertence ao grupo `sudo` para tarefas administrativas pontuais.
   * **Conexão SSH**: Acesso via terminal remoto (`ssh executamais@<IP>`) tanto na rede local quanto externamente.

2. **Permissões do Docker Engine & Daemon**:
   * **Instalação Nativa**: Instalado via APT oficial com repositório Docker (sem uso de snap).
   * **Grupo `docker`**: O usuário foi adicionado ao grupo do sistema (`sudo usermod -aG docker $USER`), permitindo executar comandos `docker` e `docker compose` sem necessidade de `sudo`. Isso é fundamental para automações de CI/CD.
   * **Acesso ao Socket**: Mapeamento seguro de `/var/run/docker.sock` quando necessário para containers de infraestrutura.

3. **Acesso Externo Seguro (Zero Trust / VPN)**:
   * **Sem Redirecionamento de Portas (Sem Port Forwarding)**: As portas 22 (SSH), 5432 (Postgres), 4566 (AWS) e os apps **não** são expostos diretamente na internet/roteador.
   * **Tailscale Mesh VPN**: Conexão ponto a ponto criptografada via WireGuard. O servidor recebe um IP privado seguro (`100.x.x.x`), permitindo acesso SSH e consumo de APIs de qualquer lugar do mundo com segurança total.

4. **Permissões do GitHub Self-Hosted Runner**:
   * O agente do runner executa sob o usuário do sistema com permissão de acesso ao daemon do Docker e à rede local.
   * Possui as tags `[self-hosted, build-linux-x64]` e `[self-hosted, deploy-linux-x64]`, concedendo permissão para criar imagens, publicar no registry local (`localhost:5000`) e subir/reiniciar containers nos ambientes (`DSV`, `HMG`, `PRD`).

---

### Prompt Pronto para Enviar para Outra IA

Copie e cole o texto abaixo para a outra IA:

````markdown
Você é um Engenheiro de Infraestrutura Linux e Especialista em Segurança e DevOps.

Preciso que você configure o acesso remoto, as políticas de segurança e a hierarquia de permissões de um novo servidor Ubuntu Server (headless / sem monitor), replicando exatamente o modelo de segurança e automação que já utilizo em outro servidor.

---

### 🛡️ ESPECIFICAÇÃO DE ACESSO E PERMISSÕES

Siga rigorosamente as diretrizes abaixo para gerar os passos e scripts de configuração:

#### 1. Usuários e Privilégios no Sistema Operacional (Ubuntu Server)
- Crie ou configure um usuário administrativo comum (não-root) para operação diária (ex: `devops` ou nome especificado).
- Conceda acesso ao grupo `sudo` para elevação de privilégios quando necessário.
- Garanta que o usuário possua seu diretório `/home` devidamente configurado com permissões `700` (`chmod 700 ~/.ssh`).
- Configure o serviço OpenSSH para autenticação segura.

#### 2. Permissões do Docker e Execução sem Sudo
- Instale a engine oficial do Docker via APT oficial (docker-ce, containerd, docker-compose-plugin), evitando versões em Snap.
- Configure o grupo de sistema `docker` e adicione o usuário operacional a ele (`usermod -aG docker <usuario>`).
- Garanta que o usuário e os processos de automação possam executar `docker ps`, `docker build`, `docker run` e `docker compose` sem exigir senha ou `sudo`.

#### 3. Conectividade e Acesso Externo Seguro (Zero Trust)
- **Bloqueio de Exposição Direta**: Não configure redirecionamento de portas (port forwarding) no roteador para serviços críticos (SSH 22, bancos de dados, etc.).
- **Tailscale Mesh VPN**:
  - Instale e configure o cliente Tailscale no servidor (`curl -fsSL https://tailscale.com/install.sh | sh`).
  - Gere o procedimento para conectar o servidor à malha privada (`sudo tailscale up`), obtendo um IP global privado `100.x.x.x`.
  - Documente como acessar o servidor via SSH e acessar os serviços web a partir de qualquer dispositivo conectado à mesma conta Tailscale.

#### 4. Permissões para GitHub Actions Self-Hosted Runner
- Documente como baixar e registrar os GitHub Runners no servidor sob o mesmo usuário configurado.
- Configure as labels dos runners para atender aos pipelines de CI/CD:
  - `[self-hosted, build-linux-x64]` (para tarefas de build, testes e registry push).
  - `[self-hosted, deploy-linux-x64]` (para orquestração de containers de deploy em DSV, HMG e PRD).
- Instale e habilite o runner como um serviço do `systemd` (`./svc.sh install` e `./svc.sh start`), garantindo que ele reinicie automaticamente com o boot do servidor e herde as permissões do grupo Docker.

#### 5. Permissões de Rede e Recursos Locais do Docker
- Crie uma rede Docker isolada (bridge) para que os containers de aplicação e serviços (banco de dados, cache, serviços emulados) possam se comunicar por DNS interno sem expor portas desnecessárias para a rede física.
- Garanta que scripts de provisionamento (ex: `init.sh` ou scripts SQL) recebam permissão de execução (`chmod +x`).

---

### 📋 DADOS DO NOVO SERVIDOR
(Substitua os dados abaixo pelos do seu ambiente):
- **Nome do Usuário Operacional**: [ex: executamais / adail / ubuntu]
- **IP Local do Servidor (LAN)**: [ex: 10.0.0.11 ou 192.168.1.50]
- **Nome da Rede Docker Interna**: [ex: app-network]
- **Repositório GitHub onde o Runner será registrado**: [URL ou Organização/Repo]

Por favor, forneça o passo a passo sequencial com todos os comandos bash comentados, testes de validação para cada etapa e boas práticas aplicadas.
````