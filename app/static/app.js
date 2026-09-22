/**
 * Koala Social Media Automation — Lógica do Painel de Controle
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elementos de Navegação
  const navItems = document.querySelectorAll(".nav-item");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const currentTabTitle = document.getElementById("current-tab-title");
  const currentTabSubtitle = document.getElementById("current-tab-subtitle");

  // Elementos do Formulário de Configuração
  const btnSaveAll = document.getElementById("btn-save-all");
  const igAccountId = document.getElementById("ig-account-id");
  const igAccessToken = document.getElementById("ig-access-token");
  const igAppId = document.getElementById("ig-app-id");
  const igAppSecret = document.getElementById("ig-app-secret");
  const igMediaBaseUrl = document.getElementById("ig-media-base-url");

  const geminiApiKey = document.getElementById("gemini-api-key");
  const geminiTextModel = document.getElementById("gemini-text-model");
  const veoVideoModel = document.getElementById("veo-video-model");

  const telegramBotToken = document.getElementById("telegram-bot-token");
  const telegramUserId = document.getElementById("telegram-user-id");

  // Teste de Conexão Instagram
  const btnTestInstagram = document.getElementById("btn-test-instagram");
  const igStatusBadge = document.getElementById("ig-status-badge");
  const igTestResult = document.getElementById("ig-test-result");

  // Perfis
  const profilesGrid = document.getElementById("profiles-grid");
  const btnNewProfile = document.getElementById("btn-new-profile");
  const profileModal = document.getElementById("profile-modal");
  const modalClose = document.getElementById("modal-close");
  const btnCancelModal = document.getElementById("btn-cancel-modal");
  const formProfileModal = document.getElementById("form-profile-modal");

  // Status Geral
  const systemHealthDot = document.getElementById("system-health-dot");
  const systemHealthLabel = document.getElementById("system-health-label");
  const btnRefreshStatus = document.getElementById("btn-refresh-status");

  // Tab Details Map
  const tabTitles = {
    "tab-instagram": {
      title: "Configuração do Instagram & Meta",
      subtitle: "Conecte sua conta profissional do Instagram para automação de Reels",
    },
    "tab-ai": {
      title: "Google Gemini & Veo",
      subtitle: "Configure os modelos de inteligência artificial generativa",
    },
    "tab-telegram": {
      title: "Telegram Bot & Aprovação",
      subtitle: "Defina o token do bot e seu ID autorizado para o fluxo semi-automático",
    },
    "tab-profiles": {
      title: "Perfis de Automação",
      subtitle: "Gerencie marcas, nichos, tons de voz e CTAs configurados",
    },
    "tab-system": {
      title: "Status e Infraestrutura",
      subtitle: "Monitoramento dos serviços, diretórios e saúde dos containers",
    },
    "tab-tutorial": {
      title: "Guia de Configuração e Tutorial",
      subtitle: "Passo a passo ilustrado para obter credenciais do Instagram, Gemini e Telegram",
    },
  };

  // Alternância de Abas
  navItems.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");

      navItems.forEach((item) => item.classList.remove("active"));
      tabPanes.forEach((pane) => pane.classList.remove("active"));

      btn.classList.add("active");
      const activePane = document.getElementById(targetTab);
      if (activePane) activePane.classList.add("active");

      if (tabTitles[targetTab]) {
        currentTabTitle.textContent = tabTitles[targetTab].title;
        currentTabSubtitle.textContent = tabTitles[targetTab].subtitle;
      }
    });
  });

  // Notificações Toast
  function showToast(message, type = "success") {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove("hidden");
    setTimeout(() => {
      toast.classList.add("hidden");
    }, 4000);
  }

  // 1. Carregar Configurações Atuais
  async function loadConfig() {
    try {
      const res = await fetch("/api/config");
      if (!res.ok) return;
      const data = await res.json();

      if (data.INSTAGRAM_ACCOUNT_ID) igAccountId.value = data.INSTAGRAM_ACCOUNT_ID;
      if (data.INSTAGRAM_APP_ID) igAppId.value = data.INSTAGRAM_APP_ID;
      if (data.PUBLIC_MEDIA_BASE_URL) igMediaBaseUrl.value = data.PUBLIC_MEDIA_BASE_URL;

      if (data.GEMINI_TEXT_MODEL) geminiTextModel.value = data.GEMINI_TEXT_MODEL;
      if (data.VEO_VIDEO_MODEL) veoVideoModel.value = data.VEO_VIDEO_MODEL;

      if (data.TELEGRAM_ALLOWED_USER_ID) telegramUserId.value = data.TELEGRAM_ALLOWED_USER_ID;

      // Placeholders indicativos caso já configurados
      if (data.INSTAGRAM_ACCESS_TOKEN_SET) igAccessToken.placeholder = "•••••••••••••••• (Configurado)";
      if (data.INSTAGRAM_APP_SECRET_SET) igAppSecret.placeholder = "•••••••••••••••• (Configurado)";
      if (data.GEMINI_API_KEY_SET) geminiApiKey.placeholder = "•••••••••••••••• (Configurado)";
      if (data.TELEGRAM_BOT_TOKEN_SET) telegramBotToken.placeholder = "•••••••••••••••• (Configurado)";

      const sysEnv = document.getElementById("sys-env");
      if (sysEnv) sysEnv.textContent = data.ENVIRONMENT || "DSV";
    } catch (e) {
      console.warn("Erro ao carregar configurações:", e);
    }
  }

  // 2. Salvar Configurações
  async function saveConfig() {
    const payload = {};

    if (igAccountId.value) payload.INSTAGRAM_ACCOUNT_ID = igAccountId.value.trim();
    if (igAccessToken.value) payload.INSTAGRAM_ACCESS_TOKEN = igAccessToken.value.trim();
    if (igAppId.value) payload.INSTAGRAM_APP_ID = igAppId.value.trim();
    if (igAppSecret.value) payload.INSTAGRAM_APP_SECRET = igAppSecret.value.trim();
    if (igMediaBaseUrl.value) payload.PUBLIC_MEDIA_BASE_URL = igMediaBaseUrl.value.trim();

    if (geminiApiKey.value) payload.GEMINI_API_KEY = geminiApiKey.value.trim();
    if (geminiTextModel.value) payload.GEMINI_TEXT_MODEL = geminiTextModel.value;
    if (veoVideoModel.value) payload.VEO_VIDEO_MODEL = veoVideoModel.value;

    if (telegramBotToken.value) payload.TELEGRAM_BOT_TOKEN = telegramBotToken.value.trim();
    if (telegramUserId.value) payload.TELEGRAM_ALLOWED_USER_ID = telegramUserId.value.trim();

    try {
      btnSaveAll.disabled = true;
      btnSaveAll.innerHTML = "⏳ Gravando...";

      const res = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (res.ok) {
        showToast("Configurações salvas com sucesso no .env!", "success");
        loadConfig();
        checkSystemHealth();
      } else {
        showToast(data.detail || "Erro ao salvar", "error");
      }
    } catch (e) {
      showToast("Falha de rede ao conectar com o servidor.", "error");
    } finally {
      btnSaveAll.disabled = false;
      btnSaveAll.innerHTML = '<span class="btn-icon">💾</span> Salvar Configurações';
    }
  }

  btnSaveAll.addEventListener("click", saveConfig);

  // 3. Testar Conexão com o Instagram
  btnTestInstagram.addEventListener("click", async () => {
    btnTestInstagram.disabled = true;
    btnTestInstagram.innerHTML = "⏳ Testando com a Meta API...";

    const payload = {};
    if (igAccessToken.value) payload.access_token = igAccessToken.value.trim();
    if (igAccountId.value) payload.account_id = igAccountId.value.trim();
    if (igAppId.value) payload.app_id = igAppId.value.trim();
    if (igAppSecret.value) payload.app_secret = igAppSecret.value.trim();

    try {
      const res = await fetch("/api/instagram/test-connection", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (data.success) {
        igStatusBadge.className = "badge badge-success";
        igStatusBadge.textContent = "Conectado";

        const acc = data.account || {};
        igTestResult.innerHTML = `
          <div class="diagnostic-success">
            <h4 style="color: #10b981; margin-bottom: 6px;">✅ Conexão Bem-Sucedida!</h4>
            <p><strong>Perfil:</strong> @${acc.username || "detectado"}</p>
            <p><strong>Nome:</strong> ${acc.name || "Conta Profissional"}</p>
            <p><strong>ID Numérico:</strong> <code>${acc.id || igAccountId.value}</code></p>
            <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;">${data.message}</p>
          </div>
        `;
        showToast("Instagram validado e pronto para automação!", "success");
      } else {
        igStatusBadge.className = "badge badge-danger";
        igStatusBadge.textContent = "Falha de Conexão";

        igTestResult.innerHTML = `
          <div class="diagnostic-error">
            <h4 style="color: #f43f5e; margin-bottom: 6px;">❌ Erro na Validação</h4>
            <p><strong>Mensagem:</strong> ${data.message}</p>
            ${data.remediation ? `<p style="margin-top: 8px; font-size: 12px;"><strong>Como resolver:</strong> ${data.remediation}</p>` : ""}
          </div>
        `;
        showToast("Não foi possível conectar. Verifique os dados.", "error");
      }
    } catch (e) {
      igStatusBadge.className = "badge badge-danger";
      igStatusBadge.textContent = "Erro de Rede";
      igTestResult.innerHTML = `<div class="diagnostic-error"><p>Falha ao comunicar com o endpoint de teste.</p></div>`;
      showToast("Erro ao testar conexão.", "error");
    } finally {
      btnTestInstagram.disabled = false;
      btnTestInstagram.innerHTML = '<span class="btn-icon">⚡</span> Testar Conexão com o Instagram';
    }
  });

  // 4. Perfis de Automação
  async function loadProfiles() {
    try {
      const res = await fetch("/api/profiles");
      if (!res.ok) return;
      const profiles = await res.json();

      profilesGrid.innerHTML = "";

      if (profiles.length === 0) {
        profilesGrid.innerHTML = `<p style="color: var(--text-muted)">Nenhum perfil cadastrado.</p>`;
        return;
      }

      profiles.forEach((p) => {
        const card = document.createElement("div");
        card.className = "profile-card";
        const igIdText = p.instagram_account_id ? `ID: ${p.instagram_account_id}` : "Usa ID Global";
        const hasTokenText = p.instagram_access_token ? "Token Próprio" : "Token Global";

        const logoImg = p.logo_url
          ? `<img src="${p.logo_url}" alt="${p.name}" style="width: 44px; height: 44px; object-fit: contain; border-radius: 8px; background: rgba(255,255,255,0.06); padding: 4px; border: 1px solid var(--border-color);">`
          : `<div style="width: 44px; height: 44px; border-radius: 8px; background: rgba(255,255,255,0.04); border: 1px dashed var(--border-color); display: flex; align-items: center; justify-content: center; font-size: 22px;">🐨</div>`;

        const logoBadge = p.logo_url
          ? `<span class="badge badge-success" style="font-size: 10px;">🏷️ Logo Ativa</span>`
          : `<span class="badge badge-neutral" style="font-size: 10px; background: rgba(255,255,255,0.04); color: #94a3b8;">⚪ Sem Logo</span>`;

        card.innerHTML = `
          <div class="profile-card-header" style="display: flex; gap: 12px; align-items: center;">
            ${logoImg}
            <div style="flex: 1;">
              <h4>${p.name}</h4>
              <span>${p.username}</span>
            </div>
            <span class="badge badge-info">${p.platform || "instagram"}</span>
          </div>
          <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 8px; display: flex; gap: 6px; flex-wrap: wrap;">
            <span class="badge badge-warning" style="font-size: 10px;">${igIdText}</span>
            <span class="badge badge-neutral" style="font-size: 10px; background: rgba(255,255,255,0.06); color: #cbd5e1;">${hasTokenText}</span>
            ${logoBadge}
          </div>
          <div class="profile-meta-tags">
            ${(p.niche || []).map((n) => `<span class="meta-tag">${n}</span>`).join("")}
          </div>
          <p style="font-size: 12px; color: var(--text-secondary); margin-top: 8px;">
            <strong>Tom:</strong> ${(p.tone || []).join(", ") || "Padrão"}
          </p>
          <p style="font-size: 12px; color: var(--text-secondary);">
            <strong>CTA:</strong> ${p.cta || "Nenhum"}
          </p>
          <div class="profile-card-actions">
            <button class="btn btn-sm btn-secondary btn-test-single-profile" data-id="${p.id}" style="color: var(--border-focus);">
              ⚡ Testar
            </button>
            <button class="btn btn-sm btn-secondary btn-edit-profile" data-profile='${JSON.stringify(p)}'>
              ✏️ Editar
            </button>
            <button class="btn btn-sm btn-secondary btn-delete-profile" data-id="${p.id}" style="color: var(--accent-rose);">
              Excluir
            </button>
          </div>
        `;
        profilesGrid.appendChild(card);
      });

      // Ação de Testar Conexão por Perfil
      document.querySelectorAll(".btn-test-single-profile").forEach((btn) => {
        btn.addEventListener("click", async (e) => {
          const id = e.target.getAttribute("data-id");
          e.target.disabled = true;
          e.target.textContent = "⏳ Testando...";
          try {
            const res = await fetch(`/api/profiles/${id}/test-connection`, { method: "POST" });
            const data = await res.json();
            if (data.success) {
              const acc = data.account || {};
              showToast(`✅ [${id}] Conexão OK para @${acc.username || "perfil"}!`, "success");
            } else {
              showToast(`❌ [${id}] ${data.message}`, "error");
            }
          } catch (err) {
            showToast(`Falha de conexão com a API para o perfil ${id}`, "error");
          } finally {
            e.target.disabled = false;
            e.target.textContent = "⚡ Testar";
          }
        });
      });

      // Ação de Editar Perfil
      document.querySelectorAll(".btn-edit-profile").forEach((btn) => {
        btn.addEventListener("click", (e) => {
          const raw = e.target.getAttribute("data-profile");
          if (!raw) return;
          const p = JSON.parse(raw);

          document.getElementById("modal-profile-title").textContent = `Editar Perfil: ${p.name}`;
          document.getElementById("prof-id").value = p.id;
          document.getElementById("prof-id").readOnly = true;
          document.getElementById("prof-name").value = p.name;
          document.getElementById("prof-username").value = p.username;
          document.getElementById("prof-ig-account-id").value = p.instagram_account_id || "";
          document.getElementById("prof-ig-access-token").value = p.instagram_access_token || "";
          document.getElementById("prof-niche").value = (p.niche || []).join(", ");
          document.getElementById("prof-tone").value = (p.tone || []).join(", ");
          document.getElementById("prof-cta").value = p.cta || "";
          document.getElementById("prof-avoid").value = (p.avoid || []).join(", ");

          // Preview da logomarca
          const previewImg = document.getElementById("prof-logo-preview");
          const previewPh = document.getElementById("prof-logo-preview-placeholder");
          const fileInput = document.getElementById("prof-logo-file");
          if (fileInput) fileInput.value = "";
          if (p.logo_url) {
            previewImg.src = p.logo_url;
            previewImg.style.display = "block";
            previewPh.style.display = "none";
          } else {
            previewImg.style.display = "none";
            previewPh.style.display = "block";
          }

          profileModal.classList.remove("hidden");
        });
      });

      // Ação de Excluir
      document.querySelectorAll(".btn-delete-profile").forEach((btn) => {
        btn.addEventListener("click", async (e) => {
          const id = e.target.getAttribute("data-id");
          if (confirm(`Tem certeza que deseja excluir o perfil "${id}"?`)) {
            await fetch(`/api/profiles/${id}`, { method: "DELETE" });
            showToast(`Perfil ${id} removido.`, "success");
            loadProfiles();
          }
        });
      });
    } catch (e) {
      console.warn("Erro ao carregar perfis:", e);
    }
  }

  // Modal de Perfis
  btnNewProfile.addEventListener("click", () => {
    formProfileModal.reset();
    document.getElementById("modal-profile-title").textContent = "Adicionar Novo Perfil de Automação";
    document.getElementById("prof-id").readOnly = false;
    const previewImg = document.getElementById("prof-logo-preview");
    const previewPh = document.getElementById("prof-logo-preview-placeholder");
    const fileInput = document.getElementById("prof-logo-file");
    if (fileInput) fileInput.value = "";
    if (previewImg) previewImg.style.display = "none";
    if (previewPh) previewPh.style.display = "block";
    profileModal.classList.remove("hidden");
  });

  // Preview dinâmico ao selecionar arquivo de logo
  const profLogoFileInput = document.getElementById("prof-logo-file");
  if (profLogoFileInput) {
    profLogoFileInput.addEventListener("change", (e) => {
      const file = e.target.files && e.target.files[0];
      const previewImg = document.getElementById("prof-logo-preview");
      const previewPh = document.getElementById("prof-logo-preview-placeholder");
      if (file) {
        const url = URL.createObjectURL(file);
        previewImg.src = url;
        previewImg.style.display = "block";
        previewPh.style.display = "none";
      } else {
        previewImg.style.display = "none";
        previewPh.style.display = "block";
      }
    });
  }

  modalClose.addEventListener("click", () => profileModal.classList.add("hidden"));
  btnCancelModal.addEventListener("click", () => profileModal.classList.add("hidden"));

  formProfileModal.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("prof-id").value.trim();
    const name = document.getElementById("prof-name").value.trim();
    const username = document.getElementById("prof-username").value.trim();
    const igAccountId = document.getElementById("prof-ig-account-id").value.trim();
    const igToken = document.getElementById("prof-ig-access-token").value.trim();
    const niche = document.getElementById("prof-niche").value.split(",").map((s) => s.trim()).filter(Boolean);
    const tone = document.getElementById("prof-tone").value.split(",").map((s) => s.trim()).filter(Boolean);
    const cta = document.getElementById("prof-cta").value.trim();
    const avoid = document.getElementById("prof-avoid").value.split(",").map((s) => s.trim()).filter(Boolean);

    const payload = {
      id,
      name,
      username,
      instagram_account_id: igAccountId || null,
      instagram_access_token: igToken || null,
      niche,
      tone,
      cta,
      avoid,
    };

    try {
      const res = await fetch("/api/profiles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        // Envio opcional da Logomarca caso um arquivo tenha sido selecionado
        const logoFileInput = document.getElementById("prof-logo-file");
        if (logoFileInput && logoFileInput.files && logoFileInput.files[0]) {
          const formData = new FormData();
          formData.append("file", logoFileInput.files[0]);
          await fetch(`/api/profiles/${id}/logo`, {
            method: "POST",
            body: formData,
          });
        }

        showToast(`Perfil "${name}" salvo com sucesso!`, "success");
        profileModal.classList.add("hidden");
        loadProfiles();
      } else {
        const err = await res.json();
        showToast(err.detail || "Erro ao salvar perfil", "error");
      }
    } catch (e) {
      showToast("Falha ao salvar perfil.", "error");
    }
  });

  // 5. Verificação da Saúde do Sistema
  async function checkSystemHealth() {
    try {
      const res = await fetch("/ready");
      if (!res.ok) throw new Error("Status não ok");
      const data = await res.json();

      systemHealthDot.className = "pulse-dot online";
      systemHealthLabel.textContent = "Sistema Online";

      // Itens da lista de saúde
      const dbBadge = document.getElementById("health-db");
      if (dbBadge) {
        dbBadge.className = data.database?.ok ? "status-badge badge-success" : "status-badge badge-danger";
        dbBadge.textContent = data.database?.ok ? "Conectado" : "Erro";
      }

      const tgBadge = document.getElementById("health-tg");
      if (tgBadge) {
        tgBadge.className = data.services?.telegram_configured ? "status-badge badge-success" : "status-badge badge-warning";
        tgBadge.textContent = data.services?.telegram_configured ? "Configurado" : "Pendente";
      }

      const geminiBadge = document.getElementById("health-gemini");
      if (geminiBadge) {
        geminiBadge.className = data.services?.gemini_configured ? "status-badge badge-success" : "status-badge badge-warning";
        geminiBadge.textContent = data.services?.gemini_configured ? "Configurado" : "Pendente";
      }

      const igBadge = document.getElementById("health-ig");
      if (igBadge) {
        igBadge.className = data.services?.instagram_configured ? "status-badge badge-success" : "status-badge badge-warning";
        igBadge.textContent = data.services?.instagram_configured ? "Configurado" : "Pendente";
      }
    } catch (e) {
      systemHealthDot.className = "pulse-dot";
      systemHealthLabel.textContent = "Desconectado";
    }
  }

  if (btnRefreshStatus) {
    btnRefreshStatus.addEventListener("click", checkSystemHealth);
  }

  // Inicialização
  loadConfig();
  loadProfiles();
  checkSystemHealth();
});
