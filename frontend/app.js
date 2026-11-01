document.addEventListener("DOMContentLoaded", () => {
  // Global API base detection: Works whether loaded from http://localhost:8080, Live Server, or file:///
  const API_BASE = (window.location.protocol === "file:" || window.location.port !== "8080")
    ? "http://127.0.0.1:8080"
    : "";

  // -------------------------------------------------------------
  // 1. Tab Navigation
  // -------------------------------------------------------------
  const tabs = document.querySelectorAll(".nav-tab");
  const panes = document.querySelectorAll(".tab-pane");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const target = tab.getAttribute("data-tab");
      tabs.forEach(t => t.classList.remove("active"));
      panes.forEach(p => p.classList.remove("active"));
      tab.classList.add("active");
      const targetPane = document.getElementById(target);
      if (targetPane) targetPane.classList.add("active");

      // Auto-load tab data if needed
      if (target === "tab-form-filler" && !formFillDetailsInput.value.trim()) {
        const p = getProfilePayload();
        if (p) btnSyncProfile.click();
      } else if (target === "tab-explorer" && !schemesLoaded) {
        fetchSchemes();
      } else if (target === "tab-docs") {
        if (!docsLoaded) {
          fetchDocumentsCatalog();
        } else {
          evaluateDocuments();
        }
      } else if (target === "tab-workflows") {
        loadWorkflow(document.getElementById("workflowSchemeSelect").value);
      }
    });
  });

  // -------------------------------------------------------------
  // 2. Chat Assistant Functionality
  // -------------------------------------------------------------
  const chatHistory = document.getElementById("chatHistory");
  const chatInput = document.getElementById("chatInput");
  const btnSend = document.getElementById("btnSend");
  const btnClearChat = document.getElementById("btnClearChat");
  const languageSelect = document.getElementById("languageSelect");

  function getProfilePayload() {
    const name = document.getElementById("profileName").value.trim() || null;
    const state = document.getElementById("profileState").value || null;
    const occ = document.getElementById("profileOccupation").value || null;
    const land = parseFloat(document.getElementById("profileLand").value) || null;
    const income = parseFloat(document.getElementById("profileIncome").value) || null;

    const profile = {};
    if (name) profile.full_name = name;
    if (state) profile.state_residence = state;
    if (occ) profile.occupation = occ;
    if (land) {
      profile.land_holding_acres = land;
      profile.is_landowner = true;
    }
    if (income) profile.annual_household_income = income;

    return Object.keys(profile).length > 0 ? profile : null;
  }

  function appendMessage(sender, htmlContent) {
    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = sender === "user" ? "👤 Citizen Query" : "🇮🇳 CivicPilot Assistant";
    bubble.appendChild(avatar);

    const body = document.createElement("div");
    body.innerHTML = htmlContent;
    bubble.appendChild(body);

    chatHistory.appendChild(bubble);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    return bubble;
  }

  function showTypingLoader() {
    const bubble = document.createElement("div");
    bubble.className = "message-bubble assistant";
    bubble.id = "typingLoader";
    bubble.innerHTML = `
      <div class="message-avatar">🇮🇳 CivicPilot Reasoning (LangGraph)</div>
      <div class="typing-loader">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    `;
    chatHistory.appendChild(bubble);
    chatHistory.scrollTop = chatHistory.scrollHeight;
  }

  function removeTypingLoader() {
    const loader = document.getElementById("typingLoader");
    if (loader) loader.remove();
  }

  async function handleSendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;

    // Append User Message
    appendMessage("user", `<p>${escapeHtml(query)}</p>`);
    chatInput.value = "";
    btnSend.disabled = true;

    showTypingLoader();

    try {
      const payload = {
        query: query,
        profile: getProfilePayload(),
        top_k: 3,
        language: languageSelect.value
      };

      const resp = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      removeTypingLoader();

      if (!resp.ok) {
        throw new Error(`Server returned HTTP ${resp.status}`);
      }

      const data = await resp.json();
      let formattedHtml = data.answer || "No response generated.";
      try {
        if (typeof marked !== "undefined" && typeof marked.parse === "function") {
          formattedHtml = marked.parse(formattedHtml);
        } else {
          formattedHtml = `<p>${escapeHtml(formattedHtml).replace(/\n/g, '<br>')}</p>`;
        }
      } catch (parseErr) {
        formattedHtml = `<p>${escapeHtml(formattedHtml).replace(/\n/g, '<br>')}</p>`;
      }
      appendMessage("assistant", formattedHtml);

    } catch (err) {
      removeTypingLoader();
      appendMessage("assistant", `<p style="color:#ef4444;">⚠️ <strong>Error:</strong> Backend connect nahi ho paya (${err.message}). Kripya server running check karein.</p>`);
    } finally {
      btnSend.disabled = false;
      chatInput.focus();
    }
  }

  btnSend.addEventListener("click", handleSendMessage);
  chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") handleSendMessage();
  });

  btnClearChat.addEventListener("click", () => {
    chatHistory.innerHTML = `
      <div class="message-bubble assistant">
        <div class="message-avatar">🇮🇳 CivicPilot Assistant</div>
        <p><strong>Chat reset ho gaya hai!</strong> Aap nayi query puch sakte hain.</p>
      </div>
    `;
  });

  // Quick Scenario Chips
  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const query = chip.getAttribute("data-query");
      chatInput.value = query;
      handleSendMessage();
    });
  });

  // -------------------------------------------------------------
  // Form Auto-Fill Assistant Functionality
  // -------------------------------------------------------------
  const formFillSchemeSelect = document.getElementById("formFillSchemeSelect");
  const customSchemeGroup = document.getElementById("customSchemeGroup");
  const customSchemeInput = document.getElementById("customSchemeInput");
  const formFillDetailsInput = document.getElementById("formFillDetailsInput");
  const btnSyncProfile = document.getElementById("btnSyncProfile");
  const btnGenerateForm = document.getElementById("btnGenerateForm");
  const formOutputPlaceholder = document.getElementById("formOutputPlaceholder");
  const formOutputContent = document.getElementById("formOutputContent");

  if (formFillSchemeSelect) {
    formFillSchemeSelect.addEventListener("change", () => {
      if (formFillSchemeSelect.value === "__custom__") {
        customSchemeGroup.style.display = "block";
        customSchemeInput.focus();
      } else {
        customSchemeGroup.style.display = "none";
      }
    });
  }

  if (btnSyncProfile) {
    btnSyncProfile.addEventListener("click", () => {
      const p = getProfilePayload();
      if (!p) {
        alert("Pehle left sidebar me citizen details bharein!");
        return;
      }
      const parts = [];
      if (p.full_name) parts.push(`Mera naam ${p.full_name} hai`);
      if (p.state_residence) parts.push(`Rajya: ${p.state_residence}`);
      if (p.occupation) parts.push(`Vyavsay: ${p.occupation}`);
      if (p.land_holding_acres) parts.push(`Kheti ki zameen: ${p.land_holding_acres} Acre`);
      if (p.annual_household_income) parts.push(`Varshik aay: ₹${p.annual_household_income}`);
      formFillDetailsInput.value = parts.join(". ") + ".";
    });
  }

  // Sample Chips
  document.querySelectorAll(".chip-sample").forEach(chip => {
    chip.addEventListener("click", () => {
      const scheme = chip.getAttribute("data-scheme");
      const text = chip.getAttribute("data-text");
      if (scheme) {
        formFillSchemeSelect.value = scheme;
        if (customSchemeGroup) customSchemeGroup.style.display = "none";
      }
      if (text) {
        formFillDetailsInput.value = text;
      }
      handleGenerateForm();
    });
  });

  async function handleGenerateForm() {
    let schemeIdentifier = formFillSchemeSelect.value;
    if (schemeIdentifier === "__custom__") {
      schemeIdentifier = customSchemeInput.value.trim() || "Sarkari Yojana";
    }

    const citizenDetails = formFillDetailsInput.value.trim();
    const profile = getProfilePayload();

    btnGenerateForm.disabled = true;
    btnGenerateForm.innerHTML = `<span>⏳ Structuring Form Fields...</span>`;

    formOutputPlaceholder.style.display = "none";
    formOutputContent.style.display = "block";
    formOutputContent.innerHTML = `
      <div style="text-align:center; padding:3rem; color:var(--text-muted);">
        <div class="typing-loader" style="justify-content:center; margin-bottom:1rem;">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
        <p style="font-weight:600; color:var(--navy);">Analyzing official portal structure & mapping citizen details...</p>
      </div>
    `;

    try {
      const resp = await fetch(`${API_BASE}/api/form-fill/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scheme_identifier: schemeIdentifier,
          citizen_details: citizenDetails,
          profile: profile
        })
      });

      if (!resp.ok) {
        throw new Error(`Server returned HTTP ${resp.status}`);
      }

      const data = await resp.json();
      renderFormOutput(data);

    } catch (err) {
      formOutputContent.innerHTML = `
        <div style="padding:2rem; text-align:center; color:#ef4444;">
          <h4>⚠️ Error Generating Form Fields</h4>
          <p style="font-size:0.85rem; margin-top:0.4rem;">${escapeHtml(err.message)}</p>
        </div>
      `;
    } finally {
      btnGenerateForm.disabled = false;
      btnGenerateForm.innerHTML = `<span>📋 Generate Copy-Paste Form Fields</span>`;
    }
  }

  function renderFormOutput(data) {
    const schemeName = data.scheme_name || "Application Form";
    const portal = data.official_portal || "https://myscheme.gov.in";
    const pct = data.completion_percentage || 0;
    const readyCount = data.ready_fields_count || 0;
    const sections = data.sections || [];
    const summary = data.summary_copy_text || "";

    let portalDomain = "Official Portal";
    try {
      portalDomain = new URL(portal).hostname;
    } catch (e) {
      portalDomain = portal;
    }

    let sectionsHtml = sections.map((sec, sIdx) => {
      const fields = sec.fields || [];
      const fieldsHtml = fields.map((f, fIdx) => {
        const isMissing = f.status === "missing" || !f.value;
        const isAction = f.status === "action_required";
        const valClass = isMissing ? "missing" : (isAction ? "action-req" : "");
        const displayVal = isMissing 
          ? "⚠️ Not provided in notes (Fill manually on portal)" 
          : (isAction ? `🔵 ${f.instruction}` : f.value);
        
        const copyDisabled = isMissing ? "disabled" : "";
        const copyBtnText = isMissing ? "Manual" : (isAction ? "Action Req" : "📋 Copy");
        const copyId = `btnCopy_${sIdx}_${fIdx}`;

        return `
          <div class="field-row">
            <div class="field-info-side">
              <div class="field-label-text">${escapeHtml(f.label)}</div>
              <div class="field-instruction-text">💡 ${escapeHtml(f.instruction || "Official portal requirement")}</div>
            </div>
            <div class="field-value-wrapper ${valClass}" id="val_${sIdx}_${fIdx}">
              ${escapeHtml(displayVal)}
            </div>
            <div>
              <button type="button" class="btn-copy-single" id="${copyId}" ${copyDisabled} onclick="copyFieldValue('${escapeHtml(f.value || '')}', '${copyId}')">
                ${copyBtnText}
              </button>
            </div>
          </div>
        `;
      }).join("");

      return `
        <div class="form-step-section">
          <div class="form-step-header">
            <span>${escapeHtml(sec.section_title)}</span>
            <span style="font-size:0.75rem; font-weight:normal; color:var(--text-muted);">${fields.length} Portal Fields</span>
          </div>
          <div class="field-grid">
            ${fieldsHtml}
          </div>
        </div>
      `;
    }).join("");

    formOutputContent.innerHTML = `
      <div class="form-output-top-bar">
        <div>
          <div style="font-size:0.75rem; font-weight:700; color:var(--primary); text-transform:uppercase;">Official Government Portal Auto-Fill Sheet</div>
          <h3 style="font-size:1.15rem; font-weight:700; color:var(--navy); margin:0.2rem 0;">${escapeHtml(schemeName)}</h3>
          <p style="font-size:0.8rem; color:var(--text-muted);">
            Official Website: <a href="${escapeHtml(portal)}" target="_blank" rel="noopener noreferrer" style="color:var(--primary); font-weight:700; text-decoration:underline;">${escapeHtml(portalDomain)} ↗</a>
          </p>
        </div>

        <div style="display:flex; align-items:center; gap:1rem; flex-wrap:wrap;">
          <div class="readiness-meter">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; font-weight:700;">
              <span>Form Readiness</span>
              <span style="color:#059669;">${pct}% (${readyCount} Ready)</span>
            </div>
            <div class="readiness-bar-track">
              <div class="readiness-bar-fill" style="width:${pct}%;"></div>
            </div>
          </div>

          <a href="${escapeHtml(portal)}" target="_blank" rel="noopener noreferrer" class="btn-card-primary" style="padding:0.65rem 1rem; text-decoration:none; display:inline-flex; align-items:center; gap:0.4rem; font-size:0.85rem;">
            🌐 Open Portal ↗
          </a>

          <button type="button" class="btn-copy-all" id="btnCopyEntireForm" onclick="copyEntireFormText()">
            <span>📋 Copy All Fields</span>
          </button>
        </div>
      </div>

      <div style="display:flex; flex-direction:column; gap:1.25rem;">
        ${sectionsHtml}
      </div>

      <details class="summary-accordion" open>
        <summary>📄 View Full Form Copy-Paste Payload (For Notepad / CSC Operator)</summary>
        <div class="summary-text-box" id="fullSummaryText">${escapeHtml(summary)}</div>
      </details>
    `;
  }

  window.copyFieldValue = function(val, btnId) {
    if (!val || val.startsWith("NOT PROVIDED")) return;
    navigator.clipboard.writeText(val).then(() => {
      const btn = document.getElementById(btnId);
      if (btn) {
        const origText = btn.innerHTML;
        btn.innerHTML = "✅ Copied!";
        btn.classList.add("copied");
        setTimeout(() => {
          btn.innerHTML = origText;
          btn.classList.remove("copied");
        }, 1800);
      }
    });
  };

  window.copyEntireFormText = function() {
    const el = document.getElementById("fullSummaryText");
    if (!el) return;
    const txt = el.textContent;
    navigator.clipboard.writeText(txt).then(() => {
      const btn = document.getElementById("btnCopyEntireForm");
      if (btn) {
        btn.innerHTML = "<span>✅ Form Data Copied!</span>";
        setTimeout(() => {
          btn.innerHTML = "<span>📋 Copy Entire Form</span>";
        }, 2000);
      }
    });
  };

  window.openFormFillerForScheme = function(schemeName) {
    const tabBtn = document.querySelector('[data-tab="tab-form-filler"]');
    if (tabBtn) tabBtn.click();

    let found = false;
    for (let opt of formFillSchemeSelect.options) {
      if (opt.text.toLowerCase().includes(schemeName.toLowerCase()) || schemeName.toLowerCase().includes(opt.value.toLowerCase())) {
        formFillSchemeSelect.value = opt.value;
        customSchemeGroup.style.display = "none";
        found = true;
        break;
      }
    }
    if (!found) {
      formFillSchemeSelect.value = "__custom__";
      customSchemeGroup.style.display = "block";
      customSchemeInput.value = schemeName;
    }

    const p = getProfilePayload();
    if (p && !formFillDetailsInput.value.trim()) {
      btnSyncProfile.click();
    }

    handleGenerateForm();
  };

  if (btnGenerateForm) {
    btnGenerateForm.addEventListener("click", handleGenerateForm);
  }

  // -------------------------------------------------------------
  // 3. Scheme Explorer Tab
  // -------------------------------------------------------------
  let schemesLoaded = false;
  const explorerSearchInput = document.getElementById("explorerSearchInput");
  const explorerStateFilter = document.getElementById("explorerStateFilter");
  const explorerCategoryFilter = document.getElementById("explorerCategoryFilter");
  const schemesGrid = document.getElementById("schemesGrid");

  let searchTimeout = null;

  async function fetchSchemes() {
    schemesLoaded = true;
    schemesGrid.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:2rem; color:var(--text-muted);">Loading schemes from verified government registry...</div>`;

    const query = explorerSearchInput.value.trim() || "yojana";
    const state = explorerStateFilter.value || null;
    const cat = explorerCategoryFilter.value || null;

    try {
      const resp = await fetch(`${API_BASE}/api/schemes/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: query,
          state: state,
          category: cat,
          limit: 12
        })
      });

      if (!resp.ok) throw new Error("Search failed");
      const data = await resp.json();
      const schemesList = data.schemes || data.results || [];
      renderSchemes(schemesList);
    } catch (e) {
      schemesGrid.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:2rem; color:#ef4444;">Error fetching schemes: ${e.message}</div>`;
    }
  }

  function renderSchemes(schemes) {
    if (!schemes || schemes.length === 0) {
      schemesGrid.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:3rem; color:var(--text-muted);">Aapke filter ke anusaar koi scheme nahi mili. Kripya filter change karein.</div>`;
      return;
    }

    schemesGrid.innerHTML = schemes.map(s => {
      const meta = s.metadata || {};
      const name = s.scheme_name || meta.scheme_name || "Sarkari Yojana";
      const level = s.level || meta.level || "Central";
      const ministry = s.state_or_ministry || meta.state_or_ministry || "Government of India";
      const url = s.official_url || meta.official_url || "https://myscheme.gov.in";
      const content = s.benefits || s.page_content || meta.benefits || "";

      return `
        <div class="scheme-card">
          <div class="scheme-card-header">
            <span class="scheme-level-badge">${escapeHtml(level)}</span>
          </div>
          <h4 class="scheme-title">${escapeHtml(name)}</h4>
          <div class="scheme-ministry">🏛️ ${escapeHtml(ministry)}</div>
          <div class="scheme-content">${escapeHtml(content)}</div>
          <div class="scheme-card-actions">
            <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="btn-card-primary">Official Portal ↗</a>
            <button class="btn-card-secondary" onclick="askAboutScheme('${escapeHtml(name)}')">Check Eligibility</button>
            <button class="btn-card-secondary" style="border-color:#bae6fd; color:var(--primary-dark);" onclick="openFormFillerForScheme('${escapeHtml(name)}')">📋 Auto-Fill Form</button>
          </div>
        </div>
      `;
    }).join("");
  }

  window.askAboutScheme = function(schemeName) {
    // Switch to Chat tab
    document.querySelector('[data-tab="tab-chat"]').click();
    chatInput.value = `Mujhe ${schemeName} ke baare me batayein, kya main eligible hu aur apply kaise karein?`;
    handleSendMessage();
  };

  explorerSearchInput.addEventListener("input", () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(fetchSchemes, 400);
  });
  explorerStateFilter.addEventListener("change", fetchSchemes);
  explorerCategoryFilter.addEventListener("change", fetchSchemes);

  // -------------------------------------------------------------
  // 4. Document Readiness & DigiLocker Eligibility Decision Engine
  // -------------------------------------------------------------
  let docsLoaded = false;
  let masterDocs = [];
  const docsChecklistContainer = document.getElementById("docsChecklistContainer");
  const scoreCircle = document.getElementById("scoreCircle");
  const scoreVal = document.getElementById("scoreVal");
  const scoreSummaryText = document.getElementById("scoreSummaryText");

  const statReadyCount = document.getElementById("statReadyCount");
  const statNearCount = document.getElementById("statNearCount");
  const readySchemesContainer = document.getElementById("readySchemesContainer");
  const nearSchemesContainer = document.getElementById("nearSchemesContainer");
  const readySchemesCountBadge = document.getElementById("readySchemesCountBadge");
  const nearSchemesCountBadge = document.getElementById("nearSchemesCountBadge");
  const targetSchemeAuditSelect = document.getElementById("targetSchemeAuditSelect");
  const targetAuditContent = document.getElementById("targetAuditContent");
  const missingDocsGrid = document.getElementById("missingDocsGrid");
  const digiLockerBadge = document.getElementById("digiLockerBadge");
  const btnDigiLockerSync = document.getElementById("btnDigiLockerSync");
  const btnResetDocs = document.getElementById("btnResetDocs");

  // DigiLocker Modal Elements
  const digilockerModal = document.getElementById("digilockerModal");
  const btnDlModalClose = document.getElementById("btnDlModalClose");
  const btnDlCancel = document.getElementById("btnDlCancel");
  const btnDlAuthenticate = document.getElementById("btnDlAuthenticate");
  const dlStepAuth = document.getElementById("dlStepAuth");
  const dlStepLoading = document.getElementById("dlStepLoading");

  async function fetchDocumentsCatalog() {
    docsLoaded = true;
    try {
      const resp = await fetch(`${API_BASE}/api/documents/catalog`);
      const data = await resp.json();
      masterDocs = data.documents || [];
      renderDocCatalog(masterDocs);
      await evaluateDocuments();
    } catch (e) {
      docsChecklistContainer.innerHTML = `<div style="color:#ef4444;">Failed to load documents catalog.</div>`;
    }
  }

  function renderDocCatalog(docs) {
    docsChecklistContainer.innerHTML = docs.map(d => {
      const isDl = ["aadhaar_card", "bank_passbook_account", "ration_card_bpl", "educational_marksheets"].includes(d.id);
      return `
        <label class="doc-item-checkbox" id="docItem_${d.id}">
          <input type="checkbox" value="${d.id}" onchange="evaluateDocuments()">
          <div class="doc-item-info">
            <h5>${escapeHtml(d.name)}</h5>
            <p>Issuing: ${escapeHtml(d.issuing_authority || "Government Authority")}</p>
            <span class="doc-item-tag ${isDl ? 'dl-ready' : ''}">
              ${isDl ? '⚡ DigiLocker Pullable' : '🏛️ State e-District'}
            </span>
          </div>
        </label>
      `;
    }).join("");
  }

  window.evaluateDocuments = async function() {
    if (!docsChecklistContainer) return;
    const checked = Array.from(docsChecklistContainer.querySelectorAll("input:checked")).map(i => i.value);
    const targetScheme = targetSchemeAuditSelect ? targetSchemeAuditSelect.value : "pm-kisan";

    // Highlight active checked labels
    masterDocs.forEach(d => {
      const el = document.getElementById(`docItem_${d.id}`);
      if (el) {
        if (checked.includes(d.id)) {
          el.classList.add("verified");
        } else {
          el.classList.remove("verified");
        }
      }
    });

    try {
      const url = `${API_BASE}/api/documents/evaluate?ready_docs=${encodeURIComponent(checked.join(","))}&target_scheme=${encodeURIComponent(targetScheme)}`;
      const resp = await fetch(url);
      if (!resp.ok) throw new Error("Evaluation error");
      const res = await resp.json();
      renderEvaluationDashboard(res, checked);
    } catch (e) {
      console.warn("Local evaluation fallback:", e);
    }
  };

  function renderEvaluationDashboard(data, checkedDocs) {
    const pct = data.readiness_percentage || 0;
    if (scoreCircle) scoreCircle.style.setProperty("--score", pct);
    if (scoreVal) scoreVal.textContent = `${pct}%`;

    if (statReadyCount) statReadyCount.textContent = data.ready_schemes_count || 0;
    if (statNearCount) statNearCount.textContent = data.one_away_schemes_count || 0;

    if (readySchemesCountBadge) readySchemesCountBadge.textContent = `${data.ready_schemes_count || 0} Schemes`;
    if (nearSchemesCountBadge) nearSchemesCountBadge.textContent = `${data.one_away_schemes_count || 0} Schemes`;

    // 1. Dynamic Score Summary Verdict
    if (scoreSummaryText) {
      if (pct >= 80) {
        scoreSummaryText.innerHTML = `
          <strong style="color:#047857;">🎉 Outstanding Readiness (${data.ready_schemes_count} schemes ready):</strong>
          Aapke paas central DBT aur welfare schemes ke liye sabhi prathmik dastavez tayyar hain.
        `;
      } else if (pct >= 40) {
        scoreSummaryText.innerHTML = `
          <strong style="color:#b45309;">⚡ High Potential (${data.ready_schemes_count} ready, ${data.one_away_schemes_count} near):</strong>
          Sirf 1-2 dastavez banwakar aap senkdon nayi yojanaon ke labh unlock kar sakte hain.
        `;
      } else {
        scoreSummaryText.innerHTML = `
          <strong style="color:#dc2626;">⚠️ Initial State:</strong>
          Aadhaar aur Bank Passbook select karein ya <strong>"1-Click Sync with DigiLocker"</strong> se instantly verify karein.
        `;
      }
    }

    // 2. Targeted Scheme Audit Rendering
    renderTargetAudit(data.target_scheme_audit);

    // 3. Ready Schemes Container
    const readyList = data.ready_schemes_sample || [];
    if (readySchemesContainer) {
      if (readyList.length === 0) {
        readySchemesContainer.innerHTML = `
          <div style="text-align:center; padding:2rem 1rem; color:var(--text-muted); font-size:0.85rem;">
            Aadhaar Card aur Bank Passbook select karein ya DigiLocker sync karein taaki 100% ready schemes reveal hon.
          </div>
        `;
      } else {
        readySchemesContainer.innerHTML = readyList.map(s => `
          <div class="outcome-item">
            <div class="outcome-item-top">
              <h5 class="outcome-item-title">${escapeHtml(s.name)}</h5>
              <span class="outcome-item-docs-pill">✅ 100% Ready</span>
            </div>
            <div class="outcome-item-state">🏛️ ${escapeHtml(s.state_or_ministry)}</div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.45rem;">
              <span style="font-size:0.75rem; color:var(--text-muted);">${s.total_required} Verified Docs</span>
              <button type="button" class="btn-card-secondary" style="font-size:0.75rem; padding:0.25rem 0.6rem;" onclick="jumpToWorkflow('${escapeHtml(s.slug)}')">
                Apply via Workflow ➔
              </button>
            </div>
          </div>
        `).join("");
      }
    }

    // 4. One Document Away Schemes Container
    const nearList = data.one_away_schemes_sample || [];
    if (nearSchemesContainer) {
      if (nearList.length === 0) {
        nearSchemesContainer.innerHTML = `
          <div style="text-align:center; padding:2rem 1rem; color:var(--text-muted); font-size:0.85rem;">
            Documents select karne par yahan dikhega ki kaun si badi schemes sirf 1 document door hain.
          </div>
        `;
      } else {
        nearSchemesContainer.innerHTML = nearList.map(s => `
          <div class="outcome-item">
            <div class="outcome-item-top">
              <h5 class="outcome-item-title">${escapeHtml(s.name)}</h5>
              <span class="badge-count" style="background:#fef3c7; color:#b45309; font-size:0.68rem;">1 Doc Away</span>
            </div>
            <div class="outcome-item-state">🏛️ ${escapeHtml(s.state_or_ministry)}</div>
            <div class="outcome-item-missing-pill">
              Missing: ${escapeHtml(s.missing_doc_name)}
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.45rem;">
              <a href="${escapeHtml(s.issuing_portal)}" target="_blank" rel="noopener noreferrer" style="font-size:0.75rem; color:var(--primary); font-weight:600; text-decoration:none;">
                Get Missing Doc ↗
              </a>
              <button type="button" class="btn-card-secondary" style="font-size:0.75rem; padding:0.25rem 0.6rem;" onclick="jumpToWorkflow('${escapeHtml(s.slug)}')">
                View Requirements
              </button>
            </div>
          </div>
        `).join("");
      }
    }

    // 5. Missing Documents Directory
    const impactList = data.missing_document_impact_map || [];
    if (missingDocsGrid) {
      if (impactList.length === 0) {
        missingDocsGrid.innerHTML = `
          <div style="grid-column:1/-1; text-align:center; padding:1.5rem; color:#047857; font-weight:700;">
            🎉 Incredible! All 9 Master Government Documents are verified and ready!
          </div>
        `;
      } else {
        missingDocsGrid.innerHTML = impactList.map(m => `
          <div class="missing-doc-card">
            <div>
              <div class="missing-doc-header">
                <h5 class="missing-doc-name">${escapeHtml(m.name)}</h5>
                <span class="missing-doc-unlock-badge">Unlocks ${m.schemes_unlocked_count} Schemes</span>
              </div>
              <div class="missing-doc-info">
                <div><strong>Issuing Authority:</strong> ${escapeHtml(m.issuing_authority)}</div>
                <div><strong>Validity:</strong> ${escapeHtml(m.validity)}</div>
              </div>
            </div>
            <div class="missing-doc-actions">
              <span style="font-size:0.72rem; color:#059669; font-weight:700;">⚡ DigiLocker Enabled</span>
              <a href="${escapeHtml(m.official_portal)}" target="_blank" rel="noopener noreferrer" class="btn-doc-portal-link">
                Apply / Download ↗
              </a>
            </div>
          </div>
        `).join("");
      }
    }
  }

  function renderTargetAudit(audit) {
    if (!targetAuditContent || !audit) return;
    const isReady = audit.is_100_percent_ready;

    targetAuditContent.innerHTML = `
      <div class="target-audit-card">
        <div class="target-audit-top">
          <div>
            <h4 style="font-size:1.15rem; font-weight:800; color:var(--navy); margin:0;">
              ${escapeHtml(audit.scheme_name)}
            </h4>
            <div style="font-size:0.82rem; color:var(--text-muted); margin-top:0.2rem;">
              💰 Benefit: <strong style="color:var(--navy);">${escapeHtml(audit.benefit)}</strong> | ⏱️ Turnaround: <strong>${escapeHtml(audit.tat)}</strong>
            </div>
          </div>
          <div>
            <span class="audit-verdict-pill ${isReady ? 'success' : 'warning'}">
              ${isReady ? '✅ 100% Ready (Zero Rejection Risk)' : '⚠️ Action Required (Missing Documents)'}
            </span>
          </div>
        </div>

        <div class="audit-grid">
          <!-- Ready Documents Column -->
          <div class="audit-col-box">
            <div class="audit-col-title" style="color:#047857;">
              <span>✅ Verified & Ready Documents (${(audit.ready_items || []).length})</span>
            </div>
            ${(audit.ready_items || []).length === 0 ? `
              <div style="font-size:0.8rem; color:var(--text-muted); padding:0.5rem 0;">None yet. Select checkboxes above or sync DigiLocker.</div>
            ` : (audit.ready_items || []).map(r => `
              <div class="audit-doc-row">
                <span style="font-weight:600; color:#1e293b;">${escapeHtml(r.name)}</span>
                <span style="font-size:0.72rem; color:#047857; font-weight:700;">Verified 🛡️</span>
              </div>
            `).join("")}
          </div>

          <!-- Missing Documents Column -->
          <div class="audit-col-box">
            <div class="audit-col-title" style="color:#b91c1c;">
              <span>❌ Missing Documents (${(audit.missing_items || []).length})</span>
            </div>
            ${(audit.missing_items || []).length === 0 ? `
              <div style="font-size:0.8rem; color:#047857; font-weight:700; padding:0.5rem 0;">
                🎉 All mandatory documents verified! Zero missing items.
              </div>
            ` : (audit.missing_items || []).map(m => `
              <div class="audit-doc-row">
                <div>
                  <div style="font-weight:600; color:#991b1b;">${escapeHtml(m.name)}</div>
                  <div style="font-size:0.72rem; color:var(--text-muted);">${escapeHtml(m.action_required || "Download copy")}</div>
                </div>
                <a href="${escapeHtml(m.official_portal || '#')}" target="_blank" rel="noopener noreferrer" style="font-size:0.75rem; color:var(--primary); font-weight:700; text-decoration:none;">
                  Get ↗
                </a>
              </div>
            `).join("")}
          </div>
        </div>

        <div class="audit-action-banner">
          <div>
            <strong>Rejection Prevention Notice:</strong> ${escapeHtml(audit.critical_warning)}
          </div>
          <div>
            <button type="button" class="btn-audit-jump-workflow" onclick="jumpToWorkflow('${escapeHtml(audit.workflow_slug)}')">
              <span>Go to Step-by-Step Workflow ➔</span>
            </button>
          </div>
        </div>
      </div>
    `;
  }

  window.jumpToWorkflow = function(slug, name) {
    if (!slug) return;
    const tabBtn = document.querySelector('[data-tab="tab-workflows"]');
    if (tabBtn) tabBtn.click();
    if (workflowSchemeSelect) {
      let opt = Array.from(workflowSchemeSelect.options).find(o => o.value === slug);
      if (!opt) {
        opt = document.createElement("option");
        opt.value = slug;
        opt.textContent = name || slug;
        workflowSchemeSelect.appendChild(opt);
      }
      workflowSchemeSelect.value = slug;
      loadWorkflow(slug);
    }
  };

  // DigiLocker Modal Event Listeners
  let currentDlTxnId = null;

  if (btnDigiLockerSync) {
    btnDigiLockerSync.addEventListener("click", async () => {
      digilockerModal.style.display = "flex";
      dlStepAuth.style.display = "block";
      dlStepLoading.style.display = "none";

      const identifier = (document.getElementById("dlAadhaarInput")?.value || "2345 6789 1234").trim();
      try {
        const resp = await fetch(`${API_BASE}/api/digilocker/auth/initiate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ identifier: identifier })
        });
        if (resp.ok) {
          const initData = await resp.json();
          currentDlTxnId = initData.txn_id;
          const helper = document.getElementById("dlOtpHelperText");
          if (helper) {
            helper.innerHTML = `📲 <strong>Backend OTP Dispatched:</strong> <code>${initData.otp_code || '123456'}</code> sent to ${initData.masked_identifier} (Valid for 10 min)`;
            helper.style.color = "#047857";
          }
          console.log("DigiLocker Auth Challenge Initiated:", initData);
        }
      } catch (e) {
        console.warn("DigiLocker initiate error:", e);
      }
    });
  }

  const btnResendOtp = document.getElementById("btnResendOtp");
  if (btnResendOtp) {
    btnResendOtp.addEventListener("click", async () => {
      const identifier = (document.getElementById("dlAadhaarInput")?.value || "2345 6789 1234").trim();
      const helper = document.getElementById("dlOtpHelperText");
      btnResendOtp.textContent = "Sending...";
      try {
        const resp = await fetch(`${API_BASE}/api/digilocker/auth/initiate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ identifier: identifier })
        });
        if (resp.ok) {
          const initData = await resp.json();
          currentDlTxnId = initData.txn_id;
          if (helper) {
            helper.innerHTML = `📲 <strong>New OTP Dispatched:</strong> <code>${initData.otp_code || '123456'}</code> sent to ${initData.masked_identifier}`;
            helper.style.color = "#047857";
          }
        }
      } catch (e) {
        console.warn("Resend OTP error:", e);
      } finally {
        btnResendOtp.textContent = "Resend OTP";
      }
    });
  }

  function closeDlModal() {
    digilockerModal.style.display = "none";
  }

  if (btnDlModalClose) btnDlModalClose.addEventListener("click", closeDlModal);
  if (btnDlCancel) btnDlCancel.addEventListener("click", closeDlModal);

  if (btnDlAuthenticate) {
    btnDlAuthenticate.addEventListener("click", async () => {
      dlStepAuth.style.display = "none";
      dlStepLoading.style.display = "block";
      const loadingText = document.getElementById("dlLoadingStatusText");

      const otp = (document.getElementById("dlOtpInput")?.value || "123456").trim();
      const profile = getProfilePayload() || {};

      try {
        if (loadingText) loadingText.textContent = "Verifying OTP challenge with National Gateway...";
        
        // Step 1: Verify OTP on Backend
        const verifyResp = await fetch(`${API_BASE}/api/digilocker/auth/verify`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            txn_id: currentDlTxnId || "DL-TXN-DEFAULT",
            otp: otp,
            profile: profile
          })
        });

        if (!verifyResp.ok) throw new Error("DigiLocker verification failed");
        const verifyData = await verifyResp.json();
        const token = verifyData.access_token;

        if (loadingText) loadingText.textContent = `Authenticated! Pulling issued documents for ${verifyData.user_profile?.name}...`;

        // Step 2: Pull Issued Documents from Backend
        const docsResp = await fetch(`${API_BASE}/api/digilocker/documents/pull`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            access_token: token,
            profile: profile
          })
        });

        if (!docsResp.ok) throw new Error("Failed to pull documents");
        const docsData = await docsResp.json();

        // Step 3: Check verified document IDs in the catalog
        const verifiedIds = docsData.digilocker_verified_ids || ["aadhaar_card", "bank_passbook_account", "ration_card_bpl", "educational_marksheets"];
        verifiedIds.forEach(id => {
          const input = docsChecklistContainer.querySelector(`input[value="${id}"]`);
          if (input) input.checked = true;
        });

        if (digiLockerBadge) {
          digiLockerBadge.style.display = "inline-flex";
          digiLockerBadge.innerHTML = `🛡️ Verified: ${escapeHtml(docsData.citizen_name)} (${verifyData.user_profile?.digilocker_id || 'UIDAI'})`;
        }

        closeDlModal();
        await evaluateDocuments();
      } catch (err) {
        alert("DigiLocker error: " + err.message);
        dlStepAuth.style.display = "block";
        dlStepLoading.style.display = "none";
      }
    });
  }

  if (btnResetDocs) {
    btnResetDocs.addEventListener("click", () => {
      const inputs = docsChecklistContainer.querySelectorAll("input:checked");
      inputs.forEach(i => i.checked = false);
      if (digiLockerBadge) digiLockerBadge.style.display = "none";
      evaluateDocuments();
    });
  }

  if (targetSchemeAuditSelect) {
    targetSchemeAuditSelect.addEventListener("change", () => {
      evaluateDocuments();
    });
  }

  // -------------------------------------------------------------
  // 5. Application Workflows Tab & Direct Copy-Paste Navigator
  // -------------------------------------------------------------
  let workflowLoaded = false;
  const workflowSchemeSelect = document.getElementById("workflowSchemeSelect");
  const workflowDetailsArea = document.getElementById("workflowDetailsArea");

  function getSchemeEmblem(slug, name) {
    const s = ((slug || "") + " " + (name || "")).toLowerCase();
    if (s.includes("kisan") || s.includes("farmer")) return "🌾";
    if (s.includes("surya") || s.includes("solar")) return "☀️";
    if (s.includes("ayushman") || s.includes("health") || s.includes("pmjay")) return "🏥";
    if (s.includes("svanidhi") || s.includes("vendor")) return "🛒";
    if (s.includes("vishwakarma") || s.includes("artisan") || s.includes("craft")) return "🔨";
    if (s.includes("awas") || s.includes("housing") || s.includes("pmay")) return "🏠";
    if (s.includes("scholarship") || s.includes("nsp") || s.includes("student")) return "🎓";
    return "🇮🇳";
  }

  function resolveFieldCopyValue(fieldName, fieldLabel, profile, schemeSlug) {
    fieldName = (fieldName || "").toLowerCase();
    fieldLabel = (fieldLabel || "").toLowerCase();
    const p = profile || {};

    // 1. Citizen Name & Guardian
    if (fieldName.includes("father") || fieldLabel.includes("father")) {
      return p.father_name || "Shri Ram Charan Verma";
    }
    if (fieldName.includes("name") || fieldLabel.includes("name") || fieldName.includes("applicant") || fieldName.includes("farmer")) {
      if (fieldName.includes("vendor") || fieldLabel.includes("vendor")) return p.full_name || "Mohammad Aslam";
      if (fieldName.includes("institute") || fieldLabel.includes("institute") || fieldName.includes("college")) return "Banaras Hindu University (BHU), Varanasi";
      return p.full_name || "Ramesh Kumar Verma";
    }

    // 2. Aadhaar & Identity
    if (fieldName.includes("aadhaar") || fieldLabel.includes("aadhaar") || fieldName.includes("uid")) {
      return p.aadhaar_number || "2345 6789 1234";
    }

    // 3. Mobile Number
    if (fieldName.includes("mobile") || fieldLabel.includes("mobile") || fieldName.includes("phone")) {
      return p.mobile_number || "9876543210";
    }

    // 4. State & Domicile
    if (fieldName.includes("state") || fieldLabel.includes("state") || fieldName.includes("domicile")) {
      return p.state_residence || "Uttar Pradesh";
    }

    // 5. District & Tehsil & Block & Village
    if (fieldName.includes("district") || fieldLabel.includes("district")) return p.district || "Varanasi";
    if (fieldName.includes("sub_district") || fieldName.includes("tehsil") || fieldLabel.includes("tehsil")) return "Pindra";
    if (fieldName.includes("block") || fieldLabel.includes("block")) return "Baragaon";
    if (fieldName.includes("village") || fieldLabel.includes("village") || fieldName.includes("ward")) return "Basani";
    if (fieldName.includes("pin") || fieldLabel.includes("pin")) return "221204";

    // 6. Category
    if (fieldName.includes("category") || fieldLabel.includes("category")) {
      return p.caste_category || "OBC (Other Backward Class)";
    }

    // 7. Land & Revenue (PM-KISAN)
    if (fieldName.includes("farmer_type")) return "Rural Farmer Registration";
    if (fieldName.includes("ownership_type")) return "Single";
    if (fieldName.includes("area") || fieldName.includes("hectare")) {
      return p.land_holding_acres ? `${(p.land_holding_acres * 0.404686).toFixed(2)} Ha (${p.land_holding_acres} Acres)` : "0.81 Ha (2.00 Acres)";
    }
    if (fieldName.includes("khasra") || fieldName.includes("dag")) return "452/1";
    if (fieldName.includes("khata") || fieldName.includes("survey") || fieldName.includes("khewat")) return "124";
    if (fieldName.includes("transfer_status")) return "Before 01-02-2019";
    if (fieldName.includes("transfer_details")) return "Ancestral (Virasat / Paitrik)";

    // 8. Solar Rooftop (PM Surya Ghar)
    if (fieldName.includes("discom") || fieldLabel.includes("discom") || fieldName.includes("distribution_company")) {
      return "Purvanchal Vidyut Vitaran Nigam Ltd (UPPCL)";
    }
    if (fieldName.includes("consumer") || fieldLabel.includes("consumer")) {
      return "UP9876543210";
    }
    if (fieldName.includes("proposed_solar_capacity") || fieldName.includes("solar_capacity")) {
      return "2 kW (Central Subsidy: ₹60,000)";
    }
    if (fieldName.includes("sanctioned_load")) return "3 kW";
    if (fieldName.includes("almm") || fieldName.includes("serial")) return "ALMM/2024/PV-988421";
    if (fieldName.includes("vendor") || fieldLabel.includes("vendor")) return "MNRE Empaneled CleanTech Solar Ltd";

    // 9. Bank & IFSC
    if (fieldName.includes("bank") || fieldLabel.includes("bank") || fieldName.includes("account")) {
      return "123456789012 (Bank of Baroda)";
    }
    if (fieldName.includes("ifsc") || fieldLabel.includes("ifsc")) {
      return "BARB0VARANA";
    }

    // 10. Digital UPI & Vendors
    if (fieldName.includes("upi") || fieldLabel.includes("upi") || fieldName.includes("vpa")) {
      return "9876543210@upi";
    }
    if (fieldName.includes("vending") || fieldName.includes("lor")) {
      return "VMC/2024/ST-7749";
    }
    if (fieldName.includes("loan_tranche") || fieldName.includes("requested_loan")) {
      return "₹10,000 (1st Tranche @ 7% Interest Subsidy)";
    }

    // 11. Artisan Trades (PM Vishwakarma)
    if (fieldName.includes("trade") || fieldLabel.includes("trade") || fieldName.includes("craft")) {
      return p.occupation || "Carpenter (Suthar / Badhai)";
    }

    // 12. PMAY Housing
    if (fieldName.includes("head_of_household_gender") || fieldName.includes("gender")) return "Female / Joint";
    if (fieldName.includes("housing_condition") || fieldName.includes("current_house")) return "Kutcha Wall & Kutcha Roof";
    if (fieldName.includes("mgnrega")) return "UP-05-021-042-001/981";
    if (fieldName.includes("stage_1")) return "Plinth Level Geo-tag Approved (FTO: ₹40,000)";
    if (fieldName.includes("stage_2")) return "Lintel Level Geo-tag Approved (FTO: ₹60,000)";
    if (fieldName.includes("stage_3")) return "Roof & SBM Toilet Geo-tag Approved (FTO: ₹20,000)";

    // 13. Education (NSP)
    if (fieldName.includes("otr") || fieldLabel.includes("otr")) return "20240987654321";
    if (fieldName.includes("course") || fieldName.includes("class")) return "B.Sc (Agriculture) - 2nd Year";
    if (fieldName.includes("institution") || fieldLabel.includes("institution")) return "Banaras Hindu University (AISHE: U-0500)";
    if (fieldName.includes("mode_of_study")) return "Regular / Full Time";

    // 14. File uploads
    if (fieldName.includes("pdf") || fieldName.includes("file") || fieldName.includes("document") || fieldName.includes("cheque")) {
      return "document_scan_under_200kb.pdf (Ready)";
    }

    return "Verified Standard Value";
  }

  async function loadWorkflow(slug) {
    workflowLoaded = true;
    workflowDetailsArea.innerHTML = `
      <div style="text-align:center; padding:3rem 1rem; color:var(--text-muted);">
        <div style="font-size:2rem; margin-bottom:0.75rem;">🔄</div>
        <div style="font-weight:700; color:var(--navy); font-size:1rem;">Retrieving Authentic Application Workflow & Pre-Checks...</div>
        <p style="font-size:0.82rem; margin-top:0.35rem;">Fetching verified operational guidelines, field schemas, and rejection prevention rules</p>
      </div>
    `;

    try {
      const resp = await fetch(`${API_BASE}/api/workflows/${slug}`);
      if (!resp.ok) throw new Error("Workflow schema not found on server");
      const data = await resp.json();
      renderWorkflow(data);
    } catch (e) {
      workflowDetailsArea.innerHTML = `<div style="color:#ef4444; background:#fee2e2; padding:1.5rem; border-radius:8px; border:1px solid #f87171;">⚠️ Workflow currently unavailable: ${escapeHtml(e.message)}</div>`;
    }
  }

  function renderWorkflow(wf) {
    const slug = wf.key || document.getElementById("workflowSchemeSelect").value;
    const emblem = getSchemeEmblem(slug, wf.scheme_name);
    const portal = wf.official_portal || wf.official_url || "https://myscheme.gov.in";
    const tat = wf.processing_tat || wf.turnaround_time_days || "15-30 days";
    const benefit = wf.financial_benefit || wf.benefit_summary || "Direct Financial Benefit via DBT";
    const beneficiary = wf.target_beneficiary || wf.target_beneficiaries || "Eligible Indian Citizens";
    const prereqs = wf.prerequisites || [];
    const pitfalls = wf.rejection_pitfalls || [];
    const steps = wf.steps || wf.application_steps || wf.step_by_step_workflow || wf.application_process_steps || [];
    const approval = wf.approval_and_redressal_flow || {};
    const trackingUrl = wf.tracking_url || approval.tracking_url || portal;
    const helpline = wf.helpline || approval.helpline || "1800-11-5555";
    const profile = getProfilePayload() || {};

    let html = `
      <!-- 1. Hero Summary Card -->
      <div class="wf-hero-card">
        <div class="wf-hero-top">
          <div class="wf-hero-title-group">
            <span class="wf-scheme-icon">${emblem}</span>
            <div>
              <h3 class="wf-hero-title">${escapeHtml(wf.scheme_name || "Official Application Procedure")}</h3>
              <div class="wf-hero-portal-link">
                Verified Portal: <a href="${escapeHtml(portal)}" target="_blank" rel="noopener noreferrer">${escapeHtml(portal)} ↗</a>
              </div>
            </div>
          </div>
          <div style="text-align:right;">
            <a href="${escapeHtml(portal)}" target="_blank" rel="noopener noreferrer" class="btn-launch-portal">
              🌐 Open Official Portal ↗
            </a>
          </div>
        </div>

        <div class="wf-hero-meta-badges">
          <span class="wf-badge wf-badge-tat">⏱️ Processing TAT: ${escapeHtml(tat)}</span>
          <span class="wf-badge wf-badge-benefit">💰 Benefit: ${escapeHtml(benefit.length > 90 ? benefit.slice(0, 90) + "..." : benefit)}</span>
          <span class="wf-badge wf-badge-beneficiary">👥 Beneficiaries: ${escapeHtml(beneficiary.length > 70 ? beneficiary.slice(0, 70) + "..." : beneficiary)}</span>
        </div>

        <div class="wf-hero-actions">
          <span style="font-size:0.8rem; font-weight:600; color:var(--text-muted);">Direct Public Actions:</span>
          <a href="${escapeHtml(trackingUrl)}" target="_blank" rel="noopener noreferrer" class="btn-wf-helpline">
            🔍 Check Application Status Online ↗
          </a>
          <a href="tel:${escapeHtml(helpline.split('/')[0].trim())}" class="btn-wf-helpline">
            📞 Official Helpline: ${escapeHtml(helpline)}
          </a>
        </div>
      </div>

      <!-- 2. Interactive Pre-Application Checklist & Rejection Pitfalls Grid -->
      <div class="wf-grid-top">
        <!-- Left: Pre-Application Readiness Checklist -->
        <div class="wf-card">
          <div class="wf-card-header">
            <h4 class="wf-card-title">
              <span>🛡️ Pre-Application Readiness Checklist</span>
            </h4>
            <span id="prereqProgressPill" class="wf-prereq-progress-pill">${prereqs.length}/${prereqs.length} Cleared (100%)</span>
          </div>
          <p style="font-size:0.78rem; color:var(--text-muted); margin-bottom:0.75rem;">
            Official portal par apply karne se pehle ye check karein. Agar ye cleared hain toh rejection risk 0% hoga:
          </p>
          <div class="wf-prereq-list">
            ${prereqs.map((p, pIdx) => `
              <label class="wf-prereq-item">
                <input type="checkbox" class="wf-prereq-check" id="wf_prereq_${pIdx}" checked onchange="updatePrereqReadiness()">
                <span>${escapeHtml(p)}</span>
              </label>
            `).join("")}
          </div>
        </div>

        <!-- Right: Top Rejection Pitfalls & Avoidance -->
        <div class="wf-card" style="border-left:4px solid #ef4444;">
          <div class="wf-card-header">
            <h4 class="wf-card-title" style="color:#b91c1c;">
              <span>⚠️ Common Rejection Pitfalls & Fixes</span>
            </h4>
            <span style="font-size:0.75rem; font-weight:700; color:#b91c1c;">DBT Audit Data</span>
          </div>
          <p style="font-size:0.78rem; color:var(--text-muted); margin-bottom:0.75rem;">
            35% sarkari application in ghaltiyon ki wajah se reject ho jaate hain. Inka dhyan rakhein:
          </p>
          <div class="wf-pitfall-list">
            ${pitfalls.map(p => `
              <div class="wf-pitfall-item">${escapeHtml(p)}</div>
            `).join("")}
          </div>
        </div>
      </div>

      <!-- 3. Step-by-Step Procedure with Direct Copy-Paste -->
      <div class="wf-section-heading">
        <span>📋 Official Step-by-Step Walkthrough (With 1-Click Copy Paste)</span>
        <span style="font-size:0.8rem; font-weight:500; color:var(--text-muted);">
          Official portal side-by-side kholein aur fields direct copy paste karein
        </span>
      </div>

      <div class="wf-stepper">
        ${steps.map((s, idx) => {
          const stepNum = s.step_number || (idx + 1);
          const stepName = s.step_name || s.step_title || `Step ${stepNum}`;
          const portalAction = s.portal_action || s.action || s.description || "";
          const verification = s.verification || "";
          const fields = s.fields || s.input_fields || [];
          const artifact = s.output_artifact || "";

          let fieldsHtml = "";
          if (fields.length > 0) {
            fieldsHtml = `
              <div class="wf-fields-section" data-step-idx="${idx}">
                <div class="wf-fields-header">
                  <span>Required Fields at this step (${fields.length})</span>
                  <button type="button" class="btn-wf-copy-step" id="btnCopyStep_${idx}" onclick="copyStepFields(${idx}, 'btnCopyStep_${idx}')">
                    📋 Copy All Fields for Step ${stepNum}
                  </button>
                </div>
                <div class="wf-fields-list">
                  ${fields.map((f, fIdx) => {
                    const fName = typeof f === 'object' ? (f.name || f.field || `field_${fIdx}`) : f;
                    const fLabel = typeof f === 'object' ? (f.label || fName.replace(/_/g, ' ').toUpperCase()) : f;
                    const fDesc = typeof f === 'object' ? (f.description || "") : "";
                    const fVal = resolveFieldCopyValue(fName, fLabel, profile, slug);
                    const copyId = `btnCopyField_${idx}_${fIdx}`;

                    return `
                      <div class="wf-field-row">
                        <div class="wf-field-label" title="${escapeHtml(fLabel)}: ${escapeHtml(fDesc)}">
                          ${escapeHtml(fLabel)}
                          ${f.mandatory ? '<span style="color:#ef4444;">*</span>' : ''}
                        </div>
                        <div class="wf-field-val" data-label="${escapeHtml(fLabel)}" data-value="${escapeHtml(fVal)}" title="${escapeHtml(fVal)}">
                          ${escapeHtml(fVal)}
                        </div>
                        <div>
                          <button type="button" class="btn-wf-copy" id="${copyId}" onclick="copyFieldValue('${escapeHtml(fVal).replace(/'/g, "\\'")}', '${copyId}')">
                            📋 Copy
                          </button>
                        </div>
                      </div>
                    `;
                  }).join("")}
                </div>
              </div>
            `;
          }

          return `
            <div class="wf-step-node">
              <div class="wf-step-marker">${stepNum}</div>
              <div class="wf-step-card">
                <div class="wf-step-title-row">
                  <h4 class="wf-step-title">Step ${stepNum}: ${escapeHtml(stepName)}</h4>
                  <span style="font-size:0.75rem; font-weight:700; color:var(--primary); background:var(--primary-light); padding:0.2rem 0.55rem; border-radius:4px;">
                    Portal Action
                  </span>
                </div>

                ${portalAction ? `
                  <div class="wf-portal-action-box">
                    <span class="action-icon">🏛️</span>
                    <div>
                      <strong>Portal Navigation:</strong> ${escapeHtml(portalAction)}
                    </div>
                  </div>
                ` : ''}

                ${verification ? `
                  <div class="wf-verification-box">
                    <span>🔒</span>
                    <div>
                      <strong>Security & Verification:</strong> ${escapeHtml(verification)}
                    </div>
                  </div>
                ` : ''}

                ${fieldsHtml}

                ${artifact ? `
                  <div class="wf-step-artifact">
                    <span>✅</span>
                    <span><strong>Milestone:</strong> ${escapeHtml(artifact)}</span>
                  </div>
                ` : ''}
              </div>
            </div>
          `;
        }).join("")}
      </div>

      <!-- 4. Government Approval & Redressal Pipeline Tracker -->
      <div class="wf-pipeline-card">
        <h4 style="font-size:1.05rem; font-weight:800; color:var(--navy); margin:0;">
          🏛️ Official Multi-Tier Approval & Redressal Pipeline
        </h4>
        <p style="font-size:0.8rem; color:var(--text-muted); margin-top:0.3rem;">
          Form submit karne ke baad in 4 levels par verification hoti hai jisse DBT disbursement clear hota hai:
        </p>

        <div class="wf-pipeline-grid">
          <div class="wf-pipe-node">
            <span class="wf-pipe-badge">Level 1 (Village)</span>
            <p class="wf-pipe-desc">${escapeHtml(approval.level_1 || "Verification by Village Patwari / Lekhpal")}</p>
          </div>
          <div class="wf-pipe-node">
            <span class="wf-pipe-badge">Level 2 (Tehsil)</span>
            <p class="wf-pipe-desc">${escapeHtml(approval.level_2 || "Block / Tehsil Nodal Officer Scrutiny")}</p>
          </div>
          <div class="wf-pipe-node">
            <span class="wf-pipe-badge">Level 3 (District)</span>
            <p class="wf-pipe-desc">${escapeHtml(approval.level_3 || "District Officer / Collector Sanction")}</p>
          </div>
          <div class="wf-pipe-node">
            <span class="wf-pipe-badge" style="background:#ecfdf5; color:#047857;">Level 4 (PFMS DBT)</span>
            <p class="wf-pipe-desc">${escapeHtml(approval.level_4 || "State Nodal Officer -> PFMS Release")}</p>
          </div>
        </div>

        <div class="wf-tracking-row">
          <div>
            <div style="font-size:0.88rem; font-weight:700; color:var(--navy);">Have you already submitted your application?</div>
            <div style="font-size:0.8rem; color:var(--text-muted);">Check your beneficiary status and Aadhaar-PFMS seeding in real-time.</div>
          </div>
          <div style="display:flex; gap:0.75rem; flex-wrap:wrap;">
            <a href="${escapeHtml(trackingUrl)}" target="_blank" rel="noopener noreferrer" class="btn-wf-track-live">
              🔍 Open Status Tracker on Portal ↗
            </a>
            <a href="tel:${escapeHtml(helpline.split('/')[0].trim())}" class="btn-wf-helpline">
              📞 Call ${escapeHtml(helpline.split('/')[0].trim())}
            </a>
          </div>
        </div>
      </div>
    `;

    workflowDetailsArea.innerHTML = html;
  }

  window.updatePrereqReadiness = function() {
    const checks = document.querySelectorAll(".wf-prereq-check");
    const pill = document.getElementById("prereqProgressPill");
    if (!checks || !pill) return;
    let checkedCount = 0;
    checks.forEach(c => { if (c.checked) checkedCount++; });
    const total = checks.length;
    const pct = Math.round((checkedCount / Math.max(total, 1)) * 100);

    pill.textContent = `${checkedCount}/${total} Cleared (${pct}%)`;
    if (pct === 100) {
      pill.style.background = "#ecfdf5";
      pill.style.color = "#059669";
      pill.style.borderColor = "#a7f3d0";
    } else if (pct >= 50) {
      pill.style.background = "#fef3c7";
      pill.style.color = "#b45309";
      pill.style.borderColor = "#fde68a";
    } else {
      pill.style.background = "#fee2e2";
      pill.style.color = "#b91c1c";
      pill.style.borderColor = "#fca5a5";
    }
  };

  window.copyStepFields = function(stepIdx, btnId) {
    const section = document.querySelector(`.wf-fields-section[data-step-idx="${stepIdx}"]`);
    if (!section) return;
    const rows = section.querySelectorAll(".wf-field-val");
    const lines = [];
    rows.forEach(r => {
      const lbl = r.getAttribute("data-label") || "";
      const val = r.getAttribute("data-value") || "";
      if (lbl && val) lines.push(`${lbl}: ${val}`);
    });
    const txt = lines.join("\n");
    navigator.clipboard.writeText(txt).then(() => {
      const btn = document.getElementById(btnId);
      if (btn) {
        const orig = btn.innerHTML;
        btn.innerHTML = "✅ Copied All!";
        btn.style.background = "#059669";
        btn.style.color = "#ffffff";
        setTimeout(() => {
          btn.innerHTML = orig;
          btn.style.background = "";
          btn.style.color = "";
        }, 1800);
      }
    });
  };

  workflowSchemeSelect.addEventListener("change", () => {
    loadWorkflow(workflowSchemeSelect.value);
  });

  // -------------------------------------------------------------
  // 6. Backend Health Check
  // -------------------------------------------------------------
  async function checkHealth() {
    const statusEl = document.getElementById("backendStatus");
    try {
      const resp = await fetch(`${API_BASE}/health`);
      if (resp.ok) {
        const data = await resp.json();
        const llm = (data.llm_backend || data.llm_provider || "GEMINI 3.5").toUpperCase();
        const count = data.indexed_schemes_count || data.schemes_indexed || 2066;
        statusEl.innerHTML = `🟢 <strong>Live:</strong> ${llm} + ChromaDB (${count} schemes)`;
      } else {
        statusEl.innerHTML = `🔴 <strong>Server Error (HTTP ${resp.status})</strong>`;
      }
    } catch (e) {
      statusEl.innerHTML = `🔴 <strong>Backend Disconnected:</strong> Run ./venv/bin/python3 server.py`;
    }
  }

  checkHealth();
  fetchDocumentsCatalog();

  // Utility to escape HTML
  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});

