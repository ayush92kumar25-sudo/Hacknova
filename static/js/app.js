// EcoPulse Waste Management System - Frontend Application Logic

const API_BASE = "/api";

// Application State
let currentUser = null;
let currentToken = null;
let awarenessData = [];

// Initialize application on DOM loaded
document.addEventListener("DOMContentLoaded", () => {
  initAuth();
  bindNavigation();
  bindForms();
  bindLocationDetector();
  bindWasteSearch();
  bindEcoAIAssistant();
  bindAIIssueClassifier();
  bindEcoAIVisionScanner();
  bindAIRouteOptimizer();
  bindSwachhataAcademy();
  bindGitHubHeatmap();
  loadInitialData();
});

// ================= AUTHENTICATION & SESSION =================
function initAuth() {
  const savedToken = localStorage.getItem("cleanwaste_token");
  const savedUser = localStorage.getItem("cleanwaste_user");

  if (savedToken && savedUser) {
    try {
      currentToken = savedToken;
      currentUser = JSON.parse(savedUser);
      updateUserUI();
    } catch (e) {
      logout();
    }
  } else {
    // Auto-login with default demo citizen on fresh start for seamless demo
    quickLogin("citizen@cleanwaste.org", "citizen123");
  }

  // Bind Auth Modal triggers
  const btnOpenLogin = document.getElementById("btn-open-login");
  const btnCloseAuthModal = document.getElementById("btn-close-auth-modal");
  const btnLogout = document.getElementById("btn-logout");
  const btnQuickDemoAdmin = document.getElementById("btn-quick-demo-admin");

  if (btnOpenLogin) btnOpenLogin.addEventListener("click", () => openAuthModal("login"));
  if (btnCloseAuthModal) btnCloseAuthModal.addEventListener("click", closeAuthModal);
  if (btnLogout) btnLogout.addEventListener("click", logout);
  if (btnQuickDemoAdmin) {
    btnQuickDemoAdmin.addEventListener("click", () => {
      quickLogin("admin@cleanwaste.org", "admin123");
    });
  }

  // Tab toggling inside Auth Modal
  const authTabLogin = document.getElementById("auth-tab-login");
  const authTabRegister = document.getElementById("auth-tab-register");
  const formLogin = document.getElementById("form-login");
  const formRegister = document.getElementById("form-register");

  if (authTabLogin && authTabRegister) {
    authTabLogin.addEventListener("click", () => {
      authTabLogin.classList.add("active");
      authTabRegister.classList.remove("active");
      formLogin.style.display = "flex";
      formRegister.style.display = "none";
    });

    authTabRegister.addEventListener("click", () => {
      authTabRegister.classList.add("active");
      authTabLogin.classList.remove("active");
      formLogin.style.display = "none";
      formRegister.style.display = "flex";
    });
  }

  // Demo Credentials Fillers
  const btnDemoCitizen = document.getElementById("btn-demo-fill-citizen");
  const btnDemoAdmin = document.getElementById("btn-demo-fill-admin");

  if (btnDemoCitizen) {
    btnDemoCitizen.addEventListener("click", () => {
      document.getElementById("login-email").value = "citizen@cleanwaste.org";
      document.getElementById("login-password").value = "citizen123";
    });
  }

  if (btnDemoAdmin) {
    btnDemoAdmin.addEventListener("click", () => {
      document.getElementById("login-email").value = "admin@cleanwaste.org";
      document.getElementById("login-password").value = "admin123";
    });
  }

  // Bind Submit handlers for Login & Register
  if (formLogin) {
    formLogin.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("login-email").value;
      const password = document.getElementById("login-password").value;
      await handleLogin(email, password);
    });
  }

  if (formRegister) {
    formRegister.addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("reg-name").value;
      const email = document.getElementById("reg-email").value;
      const password = document.getElementById("reg-password").value;
      const role = document.getElementById("reg-role").value;
      const phone = document.getElementById("reg-phone").value;
      const address = document.getElementById("reg-address").value;
      await handleRegister({ name, email, password, role, phone, address });
    });
  }
}

async function quickLogin(email, password) {
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (res.ok) {
      currentToken = data.token;
      currentUser = data.user;
      localStorage.setItem("cleanwaste_token", currentToken);
      localStorage.setItem("cleanwaste_user", JSON.stringify(currentUser));
      updateUserUI();
      showToast(`Welcome back, ${currentUser.name}! (${currentUser.role})`, "success");
      loadInitialData();
    }
  } catch (err) {
    console.error("Auto login error:", err);
  }
}

async function handleLogin(email, password) {
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || "Login failed.", "error");
      return;
    }
    currentToken = data.token;
    currentUser = data.user;
    localStorage.setItem("cleanwaste_token", currentToken);
    localStorage.setItem("cleanwaste_user", JSON.stringify(currentUser));
    updateUserUI();
    closeAuthModal();
    showToast(`Logged in successfully as ${currentUser.name} (${currentUser.role})`, "success");
    loadInitialData();

    if (currentUser.role === "Administrator") {
      switchTab("tab-admin");
    }
  } catch (err) {
    showToast("Server connection error during login.", "error");
  }
}

async function handleRegister(payload) {
  try {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.error || "Registration failed.", "error");
      return;
    }
    currentToken = data.token;
    currentUser = data.user;
    localStorage.setItem("cleanwaste_token", currentToken);
    localStorage.setItem("cleanwaste_user", JSON.stringify(currentUser));
    updateUserUI();
    closeAuthModal();
    showToast(`Account created! Welcome, ${currentUser.name}`, "success");
    loadInitialData();
  } catch (err) {
    showToast("Error creating account.", "error");
  }
}

function logout() {
  currentToken = null;
  currentUser = null;
  localStorage.removeItem("cleanwaste_token");
  localStorage.removeItem("cleanwaste_user");
  updateUserUI();
  showToast("Logged out successfully.", "success");
  switchTab("tab-overview");
}

function updateUserUI() {
  const guestControls = document.getElementById("auth-guest-controls");
  const userProfile = document.getElementById("auth-user-profile");
  const navAdmin = document.getElementById("nav-tab-admin");

  if (currentUser) {
    if (guestControls) guestControls.style.display = "none";
    if (userProfile) userProfile.style.display = "flex";
    
    document.getElementById("user-display-name").textContent = currentUser.name;
    document.getElementById("user-display-email").textContent = currentUser.email;
    
    const roleBadge = document.getElementById("user-badge-role");
    roleBadge.textContent = currentUser.role;
    if (currentUser.role === "Administrator") {
      roleBadge.classList.add("admin");
      if (navAdmin) navAdmin.style.display = "flex";
    } else {
      roleBadge.classList.remove("admin");
      if (navAdmin) navAdmin.style.display = "none";
    }
  } else {
    if (guestControls) guestControls.style.display = "flex";
    if (userProfile) userProfile.style.display = "none";
    if (navAdmin) navAdmin.style.display = "none";
  }
}

function openAuthModal(mode = "login") {
  const modal = document.getElementById("modal-auth");
  if (modal) modal.style.display = "flex";
  if (mode === "login") {
    document.getElementById("auth-tab-login").click();
  } else {
    document.getElementById("auth-tab-register").click();
  }
}

function closeAuthModal() {
  const modal = document.getElementById("modal-auth");
  if (modal) modal.style.display = "none";
}

// ================= NAVIGATION =================
function bindNavigation() {
  const navBtns = document.querySelectorAll(".nav-btn");
  navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      switchTab(targetTab);
    });
  });

  const btnBrand = document.getElementById("btn-brand-home");
  if (btnBrand) {
    btnBrand.addEventListener("click", () => switchTab("tab-overview"));
  }
}

function switchTab(tabId) {
  // If user tries to open admin tab without admin role, inform them or quick switch
  if (tabId === "tab-admin" && (!currentUser || currentUser.role !== "Administrator")) {
    showToast("Admin portal requires Administrator privileges. Click 'Demo Admin' in the header to switch.", "error");
    return;
  }

  const allPanes = document.querySelectorAll(".tab-pane");
  allPanes.forEach(pane => pane.classList.remove("active"));

  const targetPane = document.getElementById(tabId);
  if (targetPane) targetPane.classList.add("active");

  const allNavBtns = document.querySelectorAll(".nav-btn");
  allNavBtns.forEach(btn => {
    if (btn.getAttribute("data-tab") === tabId) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Trigger data refreshes on tab switch
  if (tabId === "tab-overview") {
    loadGitHubHeatmap();
    loadWardLeaderboard();
  }
  if (tabId === "tab-academy") loadSwachhataLessons();
  if (tabId === "tab-tracking") loadComplaints();
  if (tabId === "tab-pickup") loadPickups();
  if (tabId === "tab-admin") {
    loadAdminDashboard();
    loadAIRouteOptimizer();
  }
  if (tabId === "tab-awareness") {
    loadAwarenessGuides();
    loadEcoAIVisionScanner();
    loadGreenFestivals();
  }
}

// ================= DATA LOADING =================
async function loadInitialData() {
  await loadComplaints();
  await loadPickups();
  await loadAwarenessGuides();
  await loadGitHubHeatmap();
  await loadSwachhataLessons();
  await loadWardLeaderboard();
  await loadGreenFestivals();
  if (currentUser && currentUser.role === "Administrator") {
    await loadAdminDashboard();
  }
}

// ================= COMPLAINTS & REPORTING =================
async function loadComplaints() {
  if (!currentToken) return;

  try {
    const res = await fetch(`${API_BASE}/complaints`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (!res.ok) return;

    const data = await res.json();
    renderComplaints(data.complaints || []);
    updateOverviewStats(data.complaints || []);
  } catch (err) {
    console.error("Error loading complaints:", err);
  }
}

function updateOverviewStats(complaints) {
  const total = complaints.length;
  const resolved = complaints.filter(c => c.status === "Resolved").length;
  const rate = total > 0 ? Math.round((resolved / total) * 100) : 0;

  const heroTotal = document.getElementById("hero-total-complaints");
  const heroRate = document.getElementById("hero-resolved-rate");
  
  if (heroTotal) heroTotal.textContent = total;
  if (heroRate) heroRate.textContent = `${rate}%`;
}

function renderComplaints(complaints) {
  const container = document.getElementById("complaints-list-container");
  if (!container) return;

  const filterSelect = document.getElementById("tracking-filter-status");
  const currentFilter = filterSelect ? filterSelect.value : "ALL";

  const filtered = currentFilter === "ALL" 
    ? complaints 
    : complaints.filter(c => c.status === currentFilter);

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 3rem; background: var(--bg-card); border-radius: var(--radius-lg); border: 1px dashed var(--border-color);">
        <p style="color: var(--text-muted); font-size: 1.1rem; margin-bottom: 1rem;">No waste complaints found for this view.</p>
        <button class="btn btn-primary" onclick="switchTab('tab-report')">Submit a New Complaint</button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(c => {
    const statusClass = {
      "Pending": "badge-pending",
      "Assigned": "badge-assigned",
      "In Progress": "badge-progress",
      "Resolved": "badge-resolved"
    }[c.status] || "badge-pending";

    // Progress timeline status flags
    const steps = ["Pending", "Assigned", "In Progress", "Resolved"];
    const currentIndex = steps.indexOf(c.status);

    const timelineHtml = steps.map((step, idx) => {
      let stateClass = "";
      if (idx < currentIndex) stateClass = "completed";
      else if (idx === currentIndex) stateClass = "current";

      return `
        <div class="timeline-step ${stateClass}">
          <div class="step-circle">${idx < currentIndex ? '✓' : (idx + 1)}</div>
          <span class="step-label">${step}</span>
        </div>
      `;
    }).join("");

    const photoUrl = c.image_url || "https://images.unsplash.com/photo-1605600659908-0ef719419d41?auto=format&fit=crop&w=400&q=80";

    return `
      <div class="complaint-card">
        <div class="complaint-top">
          <div class="complaint-title-group">
            <h3>${escapeHtml(c.title)}</h3>
            <div class="complaint-meta">
              <span>📍 ${escapeHtml(c.location_text)}</span>
              <span>•</span>
              <span>🏷️ ${escapeHtml(c.category)}</span>
              <span>•</span>
              <span>🕒 ${new Date(c.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
              ${c.citizen_name ? `<span>• 👤 ${escapeHtml(c.citizen_name)}</span>` : ''}
            </div>
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
            <button type="button" class="btn-upvote" onclick="handleUpvote(${c.id}, this)">
              👍 Support (${c.upvotes || 0})
            </button>
            <span class="badge ${statusClass}">● ${c.status}</span>
          </div>
        </div>

        <div class="complaint-body">
          <div class="complaint-desc">
            <p>${escapeHtml(c.description)}</p>
            ${c.assigned_team ? `
              <div style="margin-top: 0.75rem; font-size: 0.85rem; color: #93c5fd;">
                <strong>Assigned Unit:</strong> ${escapeHtml(c.assigned_team)}
              </div>
            ` : ''}
            ${c.admin_notes ? `
              <div class="admin-field-note" style="margin-top: 0.65rem;">
                <strong>Field Note:</strong> ${escapeHtml(c.admin_notes)}
              </div>
            ` : ''}
          </div>
          <img src="${photoUrl}" alt="Waste incident photo" class="complaint-thumb" onerror="this.src='https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?auto=format&fit=crop&w=400&q=80'">
        </div>

        <!-- 4-Step Milestone Timeline -->
        <div class="timeline-track">
          ${timelineHtml}
        </div>

        <!-- Before / After Resolution Photo Proof (EcoTrack Inspired) -->
        ${c.status === 'Resolved' && c.resolved_image_url ? `
          <div class="before-after-container">
            <div class="before-after-header">
              <span>📸 फ़ोटो प्रमाण &bull; Resolution Proof Verified by EcoAI</span>
              <span class="badge badge-resolved">100% Cleared</span>
            </div>
            <div class="comparison-slider-wrap">
              <div class="before-box">
                <img src="${photoUrl}" alt="Before cleanup">
                <span class="img-label before">BEFORE</span>
              </div>
              <div class="after-box">
                <img src="${c.resolved_image_url}" alt="After cleanup" onerror="this.src='https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=400&q=80'">
                <span class="img-label after">AFTER CLEANUP</span>
              </div>
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }).join("");
}

// Community Civic Support Upvoting (EcoTrack Inspired)
async function handleUpvote(complaintId, btn) {
  if (!currentToken) {
    showToast("Please sign in to upvote neighborhood issues.", "info");
    openAuthModal("login");
    return;
  }
  btn.disabled = true;
  try {
    const res = await fetch(`${API_BASE}/complaints/${complaintId}/upvote`, {
      method: "POST",
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    const data = await res.json();
    if (res.ok) {
      btn.innerHTML = `👍 Supported (${data.upvotes})`;
      btn.style.color = "#34d399";
      btn.style.borderColor = "#10b981";
      showToast(data.message, "success");
      if (currentUser) {
        currentUser.karma_points = (currentUser.karma_points || 340) + 5;
        localStorage.setItem("cleanwaste_user", JSON.stringify(currentUser));
        updateUserUI();
      }
    } else {
      showToast(data.error || "Could not upvote.", "error");
    }
  } catch (err) {
    showToast("Error recording upvote.", "error");
  } finally {
    btn.disabled = false;
  }
}

// Bind Filter select in Tracking page
const trackingFilter = document.getElementById("tracking-filter-status");
if (trackingFilter) {
  trackingFilter.addEventListener("change", () => loadComplaints());
}

// ================= REPORT SUBMISSION =================
function bindForms() {
  // Landmark Quick Helper Chips (EcoTrack Inspired)
  const landmarkChips = document.querySelectorAll(".btn-landmark-chip");
  landmarkChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const locInput = document.getElementById("report-location");
      if (locInput) {
        const prefix = chip.getAttribute("data-prefix");
        if (!locInput.value.includes(prefix)) {
          locInput.value = prefix + locInput.value;
        }
        locInput.focus();
      }
    });
  });

  const formReport = document.getElementById("form-report-complaint");
  if (formReport) {
    formReport.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!currentToken) {
        showToast("Please sign in to submit a complaint.", "error");
        openAuthModal("login");
        return;
      }

      const title = document.getElementById("report-title").value.trim();
      const category = document.getElementById("report-category").value;
      const location_text = document.getElementById("report-location").value.trim();
      const description = document.getElementById("report-description").value.trim();
      const image_url = document.getElementById("report-image-url").value.trim();
      
      const lat = window.currentDetectedLat || 40.7128;
      const lng = window.currentDetectedLng || -74.0060;

      const submitBtn = document.getElementById("btn-submit-complaint");
      submitBtn.disabled = true;
      submitBtn.textContent = "Submitting...";

      try {
        const res = await fetch(`${API_BASE}/complaints`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${currentToken}`
          },
          body: JSON.stringify({
            title,
            category,
            location_text,
            description,
            image_url,
            latitude: lat,
            longitude: lng
          })
        });

        const data = await res.json();
        if (res.ok) {
          showToast("Waste issue reported successfully!", "success");
          formReport.reset();
          document.getElementById("coords-row").style.display = "none";
          await loadComplaints();
          switchTab("tab-tracking");
        } else {
          showToast(data.error || "Failed to submit report.", "error");
        }
      } catch (err) {
        showToast("Network error submitting complaint.", "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit Waste Report →";
      }
    });
  }

  // Bulk Pickup Form
  const formPickup = document.getElementById("form-pickup-request");
  if (formPickup) {
    // Set default pickup date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 2);
    const dateInput = document.getElementById("pickup-date");
    if (dateInput) dateInput.value = tomorrow.toISOString().split("T")[0];

    formPickup.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!currentToken) {
        showToast("Please sign in to schedule a pickup.", "error");
        openAuthModal("login");
        return;
      }

      const request_type = document.getElementById("pickup-request-type").value;
      const waste_type = document.getElementById("pickup-waste-type").value.trim();
      const estimated_volume = document.getElementById("pickup-volume").value;
      const pickup_date = document.getElementById("pickup-date").value;
      const address = document.getElementById("pickup-address").value.trim();
      const contact_number = document.getElementById("pickup-contact").value.trim();
      const special_instructions = document.getElementById("pickup-instructions").value.trim();

      const submitBtn = document.getElementById("btn-submit-pickup");
      submitBtn.disabled = true;
      submitBtn.textContent = "Scheduling...";

      try {
        const res = await fetch(`${API_BASE}/pickups`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${currentToken}`
          },
          body: JSON.stringify({
            request_type,
            waste_type,
            estimated_volume,
            pickup_date,
            address,
            contact_number,
            special_instructions
          })
        });

        const data = await res.json();
        if (res.ok) {
          showToast("Special bulk pickup successfully scheduled!", "success");
          formPickup.reset();
          await loadPickups();
        } else {
          showToast(data.error || "Could not schedule pickup.", "error");
        }
      } catch (err) {
        showToast("Network error booking pickup.", "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Confirm & Schedule Pickup →";
      }
    });
  }

  // Admin Update Status Form
  const formUpdateStatus = document.getElementById("form-update-status");
  if (formUpdateStatus) {
    formUpdateStatus.addEventListener("submit", async (e) => {
      e.preventDefault();
      const complaintId = document.getElementById("modal-complaint-id").value;
      const status = document.getElementById("modal-status-select").value;
      const assigned_team = document.getElementById("modal-team-input").value.trim();
      const admin_notes = document.getElementById("modal-notes-input").value.trim();
      const resolvedImgInput = document.getElementById("modal-resolved-img-input");
      const resolved_image_url = resolvedImgInput ? resolvedImgInput.value.trim() : null;

      try {
        const res = await fetch(`${API_BASE}/complaints/${complaintId}`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${currentToken}`
          },
          body: JSON.stringify({ 
            status, 
            assigned_team, 
            admin_notes,
            resolved_image_url: resolved_image_url || null
          })
        });
        if (res.ok) {
          showToast("Status & resolution photo proof updated!", "success");
          closeStatusModal();
          await loadAdminDashboard();
          await loadComplaints();
        } else {
          const errData = await res.json();
          showToast(errData.error || "Failed to update complaint.", "error");
        }
      } catch (err) {
        showToast("Error updating status.", "error");
      }
    });
  }

  // Modal Cancel/Close buttons
  const btnCloseModal = document.getElementById("btn-close-modal");
  const btnCancelModal = document.getElementById("btn-cancel-modal");
  if (btnCloseModal) btnCloseModal.addEventListener("click", closeStatusModal);
  if (btnCancelModal) btnCancelModal.addEventListener("click", closeStatusModal);
}

// Geolocation detector
function bindLocationDetector() {
  const btn = document.getElementById("btn-detect-location");
  if (!btn) return;

  btn.addEventListener("click", () => {
    btn.textContent = "Locating...";
    btn.disabled = true;

    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude.toFixed(4);
          const lng = pos.coords.longitude.toFixed(4);
          window.currentDetectedLat = pos.coords.latitude;
          window.currentDetectedLng = pos.coords.longitude;

          const locationInput = document.getElementById("report-location");
          if (!locationInput.value) {
            locationInput.value = `Sector 4, GPS Zone [${lat}, ${lng}]`;
          }

          document.getElementById("coords-row").style.display = "block";
          document.getElementById("coords-display").textContent = `Lat: ${lat}, Long: ${lng}`;

          btn.textContent = "✓ Location Set";
          btn.disabled = false;
          showToast("Coordinates detected successfully!", "success");
        },
        (err) => {
          // Fallback realistic simulation
          window.currentDetectedLat = 40.7128;
          window.currentDetectedLng = -74.0060;
          document.getElementById("coords-row").style.display = "block";
          document.getElementById("coords-display").textContent = `Lat: 40.7128, Long: -74.0060 (Simulated GPS)`;
          btn.textContent = "📍 Detect GPS";
          btn.disabled = false;
          showToast("Simulated GPS location set.", "success");
        }
      );
    }
  });
}

// ================= PICKUP REQUESTS =================
async function loadPickups() {
  if (!currentToken) return;

  try {
    const res = await fetch(`${API_BASE}/pickups`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (!res.ok) return;

    const data = await res.json();
    renderPickups(data.pickups || []);
    const heroPickups = document.getElementById("hero-active-pickups");
    if (heroPickups) heroPickups.textContent = (data.pickups || []).length;
  } catch (err) {
    console.error("Error loading pickups:", err);
  }
}

function renderPickups(pickups) {
  const container = document.getElementById("user-pickups-container");
  if (!container) return;

  if (pickups.length === 0) {
    container.innerHTML = `<p style="color: var(--text-muted); grid-column: 1/-1;">No bulk pickup requests currently on schedule.</p>`;
    return;
  }

  container.innerHTML = pickups.map(p => {
    return `
      <div class="pickup-card">
        <div class="pickup-card-top">
          <span class="pickup-title">${escapeHtml(p.request_type)}</span>
          <span class="badge ${p.status === 'Completed' ? 'badge-resolved' : 'badge-assigned'}">${p.status}</span>
        </div>
        <div class="pickup-details-row">
          <span><strong>Material:</strong> ${escapeHtml(p.waste_type)}</span>
          <span><strong>Volume:</strong> ${escapeHtml(p.estimated_volume)}</span>
          <span><strong>Target Date:</strong> 📅 ${p.pickup_date}</span>
          <span><strong>Address:</strong> 📍 ${escapeHtml(p.address)}</span>
          ${p.special_instructions ? `<span><strong>Notes:</strong> ${escapeHtml(p.special_instructions)}</span>` : ''}
        </div>
      </div>
    `;
  }).join("");
}

// ================= ADMIN DASHBOARD =================
async function loadAdminDashboard() {
  if (!currentToken || !currentUser || currentUser.role !== "Administrator") return;

  try {
    // 1. Load Analytics
    const res = await fetch(`${API_BASE}/admin/analytics`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (res.ok) {
      const data = await res.json();
      renderAnalytics(data);
    }

    // 2. Load All Complaints for Admin Table
    const compRes = await fetch(`${API_BASE}/complaints`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });
    if (compRes.ok) {
      const compData = await compRes.json();
      renderAdminTable(compData.complaints || []);
    }
  } catch (err) {
    console.error("Admin dashboard fetch error:", err);
  }
}

function renderAnalytics(data) {
  const ov = data.overview;
  document.getElementById("kpi-total").textContent = ov.total_complaints;
  document.getElementById("kpi-pending").textContent = ov.pending;
  document.getElementById("kpi-in-progress").textContent = ov.in_progress;
  document.getElementById("kpi-resolved").textContent = ov.resolved;
  document.getElementById("kpi-rate").textContent = `${ov.resolution_rate}% Resolved`;

  // Render Hotspots List
  const hotspotsContainer = document.getElementById("hotspots-list");
  if (hotspotsContainer) {
    if (!data.hotspots || data.hotspots.length === 0) {
      hotspotsContainer.innerHTML = `<p style="color: var(--text-muted);">No hotspots calculated yet.</p>`;
    } else {
      hotspotsContainer.innerHTML = data.hotspots.map((h, i) => `
        <div class="hotspot-row">
          <div>
            <div class="hotspot-loc">#${i + 1} &bull; ${escapeHtml(h.location_text)}</div>
            <div class="hotspot-issues">Recurring: ${escapeHtml(h.recurring_issues || "General")}</div>
          </div>
          <div class="hotspot-count-pill">${h.report_count} Reports</div>
        </div>
      `).join("");
    }
  }

  // Render Category Breakdown Bars
  const catContainer = document.getElementById("category-distribution-container");
  if (catContainer && data.category_distribution) {
    const totalReports = ov.total_complaints || 1;
    catContainer.innerHTML = data.category_distribution.map(cat => {
      const percentage = Math.round((cat.count / totalReports) * 100);
      return `
        <div class="cat-bar-item">
          <div class="cat-bar-header">
            <span>${escapeHtml(cat.category)}</span>
            <span>${cat.count} (${percentage}%)</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" style="width: ${percentage}%"></div>
          </div>
        </div>
      `;
    }).join("");
  }
}

function renderAdminTable(complaints) {
  const tbody = document.getElementById("admin-complaints-tbody");
  if (!tbody) return;

  const statusFilter = document.getElementById("admin-status-filter").value;
  const filtered = statusFilter ? complaints.filter(c => c.status === statusFilter) : complaints;

  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2rem;">No matching complaints in record.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(c => `
    <tr>
      <td><strong>#${c.id}</strong></td>
      <td>
        <div style="font-weight: 600;">${escapeHtml(c.citizen_name || 'Anonymous')}</div>
        <div style="font-size: 0.75rem; color: var(--text-muted);">${escapeHtml(c.citizen_email || '')}</div>
      </td>
      <td><span style="font-size: 0.82rem;">${escapeHtml(c.category)}</span></td>
      <td><span style="font-size: 0.82rem;">${escapeHtml(c.location_text)}</span></td>
      <td><span class="badge ${getStatusBadgeClass(c.status)}">${c.status}</span></td>
      <td><span style="font-size: 0.82rem; color: #93c5fd;">${escapeHtml(c.assigned_team || 'Unassigned')}</span></td>
      <td>
        <button class="btn btn-secondary-sm" onclick="openStatusModal(${c.id}, '${c.status}', '${escapeHtml(c.assigned_team || '')}', '${escapeHtml(c.admin_notes || '')}', '${escapeHtml(c.resolved_image_url || '')}')">
          ⚙️ Dispatch / Update
        </button>
      </td>
    </tr>
  `).join("");
}

const adminFilter = document.getElementById("admin-status-filter");
if (adminFilter) {
  adminFilter.addEventListener("change", () => loadAdminDashboard());
}

function getStatusBadgeClass(status) {
  switch (status) {
    case "Pending": return "badge-pending";
    case "Assigned": return "badge-assigned";
    case "In Progress": return "badge-progress";
    case "Resolved": return "badge-resolved";
    default: return "badge-pending";
  }
}

function openStatusModal(id, currentStatus, currentTeam, currentNotes, resolvedImg) {
  document.getElementById("modal-complaint-id").value = id;
  document.getElementById("modal-status-select").value = currentStatus;
  document.getElementById("modal-team-input").value = currentTeam || "";
  document.getElementById("modal-notes-input").value = currentNotes || "";
  const resolvedImgInput = document.getElementById("modal-resolved-img-input");
  if (resolvedImgInput) resolvedImgInput.value = resolvedImg || "";
  document.getElementById("modal-title").textContent = `Update Complaint #${id}`;
  document.getElementById("modal-update-status").style.display = "flex";
}

function closeStatusModal() {
  document.getElementById("modal-update-status").style.display = "none";
}

// ================= WASTE AWARENESS & SEARCH =================
async function loadAwarenessGuides() {
  try {
    const res = await fetch(`${API_BASE}/awareness`);
    if (!res.ok) return;
    const data = await res.json();
    awarenessData = data.guides || [];
    renderAwarenessCards(awarenessData);
  } catch (err) {
    console.error("Error loading awareness guides:", err);
  }
}

function renderAwarenessCards(guides) {
  const container = document.getElementById("awareness-cards-grid");
  if (!container) return;

  container.innerHTML = guides.map(g => `
    <div class="awareness-card ${g.color}">
      <span class="bin-tag ${g.color}">${g.binColor}</span>
      <h3>${g.category}</h3>
      <p class="awareness-desc">${g.description}</p>
      
      <div class="examples-box">
        <strong>Common Examples:</strong>
        <ul>
          ${g.examples.map(ex => `<li>${ex}</li>`).join("")}
        </ul>
      </div>

      <div style="font-size: 0.8rem; margin-top: 0.5rem;">
        <span style="color: #34d399; font-weight: 700;">DO:</span> ${g.dosAndDonts.dos[0]}<br>
        <span style="color: #f87171; font-weight: 700;">DON'T:</span> ${g.dosAndDonts.donts[0]}
      </div>
    </div>
  `).join("");
}

// Interactive Disposal Search
function bindWasteSearch() {
  const searchInput = document.getElementById("waste-item-search");
  const resultPill = document.getElementById("quick-search-result");
  if (!searchInput || !resultPill) return;

  const itemDisposalDirectory = [
    { query: "banana", bin: "Green Bin (Wet / Biodegradable)", advice: "Compostable. Decomposes naturally into nutrient rich soil." },
    { query: "apple", bin: "Green Bin (Wet / Biodegradable)", advice: "Put in wet waste or household vermicompost." },
    { query: "peel", bin: "Green Bin (Wet / Biodegradable)", advice: "Kitchen organic waste. Keep unmixed from plastic." },
    { query: "food", bin: "Green Bin (Wet / Biodegradable)", advice: "Drain liquids, dispose in compost/green bin." },
    { query: "pizza", bin: "Blue Bin (if clean) or Red/Trash (if grease soaked)", advice: "Greasy pizza cardboard cannot be recycled; tear off clean lid for recycling, greasy bottom in general waste." },
    { query: "plastic bottle", bin: "Blue Bin (Dry Recyclable)", advice: "Empty, rinse out liquids, squash flat, and replace cap." },
    { query: "bottle", bin: "Blue Bin (Dry Recyclable)", advice: "Rinse container clean before depositing." },
    { query: "battery", bin: "Grey Bin / E-Waste or Hazardous Center", advice: "Contains heavy toxic lithium/lead. NEVER throw in common garbage!" },
    { query: "medicine", bin: "Red Bin (Domestic Hazardous)", advice: "Expired medication contaminates water tables. Deposit at pharmacy return drives." },
    { query: "laptop", bin: "Special Bulk E-Waste Pickup", advice: "Schedule a dedicated pickup from our 'Bulk Pickup' tab." },
    { query: "paper", bin: "Blue Bin (Dry Recyclable)", advice: "Keep clean and dry. Flatten sheets and newspapers." },
    { query: "can", bin: "Blue Bin (Dry Recyclable)", advice: "Aluminum & tin cans have infinite recycling recyclability." }
  ];

  searchInput.addEventListener("input", (e) => {
    const val = e.target.value.trim().toLowerCase();
    if (!val) {
      resultPill.style.display = "none";
      return;
    }

    const match = itemDisposalDirectory.find(item => val.includes(item.query) || item.query.includes(val));
    if (match) {
      resultPill.style.display = "block";
      resultPill.innerHTML = `<strong>Disposal Result for "${val}":</strong> Destination: <span style="color:#6ee7b7; font-weight:700;">${match.bin}</span> &mdash; ${match.advice}`;
    } else {
      resultPill.style.display = "block";
      resultPill.innerHTML = `<strong>Result for "${val}":</strong> If organic/kitchen item &rarr; Green Bin. If dry plastic/paper &rarr; Blue Bin. If chemical/electronic &rarr; Schedule E-Waste Pickup.`;
    }
  });
}

// ================= UTILITIES =================
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : (type === 'error' ? '⚠️' : 'ℹ️')}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ================= ECO-AI ASSISTANT (CHAT COPILOT) =================
function bindEcoAIAssistant() {
  const btnOpen = document.getElementById("btn-open-ai-chat");
  const btnClose = document.getElementById("btn-close-ai-chat");
  const btnClear = document.getElementById("btn-clear-ai-chat");
  const drawer = document.getElementById("ai-chat-drawer");
  const form = document.getElementById("ai-chat-form");
  const input = document.getElementById("ai-user-input");
  const chipsContainer = document.getElementById("ai-quick-chips");

  if (!btnOpen || !drawer) return;

  // Toggle Chat Drawer
  btnOpen.addEventListener("click", () => {
    const isHidden = drawer.style.display === "none";
    drawer.style.display = isHidden ? "flex" : "none";
    if (isHidden && input) input.focus();
  });

  if (btnClose) {
    btnClose.addEventListener("click", () => {
      drawer.style.display = "none";
    });
  }

  // Clear Chat History
  if (btnClear) {
    btnClear.addEventListener("click", () => {
      const messagesContainer = document.getElementById("ai-messages-list");
      if (messagesContainer) {
        messagesContainer.innerHTML = `
          <div class="ai-msg bot">
            <div class="ai-bubble">
              Chat history cleared. How can I assist with your civic waste management today?
            </div>
          </div>
        `;
      }
    });
  }

  // Quick Suggestion Chips
  if (chipsContainer) {
    chipsContainer.addEventListener("click", (e) => {
      const chip = e.target.closest(".ai-chip");
      if (chip) {
        const prompt = chip.getAttribute("data-prompt");
        if (prompt) {
          sendAIMessage(prompt);
        }
      }
    });
  }

  // Submit User Message
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const msg = input.value.trim();
      if (!msg) return;
      input.value = "";
      sendAIMessage(msg);
    });
  }
}

async function sendAIMessage(text) {
  const messagesContainer = document.getElementById("ai-messages-list");
  if (!messagesContainer) return;

  // 1. Render User Message
  const userDiv = document.createElement("div");
  userDiv.className = "ai-msg user";
  userDiv.innerHTML = `<div class="ai-bubble">${escapeHtml(text)}</div>`;
  messagesContainer.appendChild(userDiv);

  // 2. Render Loading Indicator
  const botDiv = document.createElement("div");
  botDiv.className = "ai-msg bot";
  botDiv.innerHTML = `
    <div class="ai-bubble" style="color: var(--text-muted); font-style: italic;">
      ✨ EcoAI is thinking...
    </div>
  `;
  messagesContainer.appendChild(botDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  try {
    const headers = { "Content-Type": "application/json" };
    if (currentToken) headers["Authorization"] = `Bearer ${currentToken}`;

    const res = await fetch(`${API_BASE}/ai/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify({ message: text })
    });

    const data = await res.json();
    let replyHtml = formatAIMarkdown(data.reply || "I am processing your sanitation query.");

    // Action button if target tab specified
    if (data.action_type === "navigate_tab" && data.target_tab) {
      replyHtml += `
        <div style="margin-top: 0.85rem;">
          <button class="btn btn-primary-sm" onclick="switchTab('${data.target_tab}'); document.getElementById('ai-chat-drawer').style.display='none';">
            🚀 Open ${data.target_tab.replace('tab-', '').toUpperCase()} &rarr;
          </button>
        </div>
      `;
    }

    botDiv.innerHTML = `<div class="ai-bubble">${replyHtml}</div>`;
  } catch (err) {
    botDiv.innerHTML = `
      <div class="ai-bubble" style="color: #fca5a5;">
        ⚠️ Sorry, I could not connect to the AI engine. Please verify the server is running.
      </div>
    `;
  }

  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function formatAIMarkdown(text) {
  if (!text) return "";
  let html = text
    .replace(/^### (.*$)/gim, '<h4 style="margin: 0.4rem 0; color: #fff;">$1</h4>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code style="background: rgba(16,185,129,0.15); color: #6ee7b7; padding: 2px 6px; border-radius: 4px; font-family: monospace;">$1</code>')
    .replace(/\n- (.*$)/gim, '<li style="margin-left: 1.2rem; list-style-type: disc;">$1</li>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>');
  return html;
}

// ================= AI ISSUE AUTO-CLASSIFIER =================
function bindAIIssueClassifier() {
  const btnClassify = document.getElementById("btn-ai-classify-report");
  if (!btnClassify) return;

  btnClassify.addEventListener("click", async () => {
    const descInput = document.getElementById("report-description");
    const titleInput = document.getElementById("report-title");
    const categorySelect = document.getElementById("report-category");
    const badge = document.getElementById("ai-classify-badge");

    const textToClassify = (descInput.value || titleInput.value || "").trim();
    if (!textToClassify) {
      showToast("Please type a rough observation into the description or title first.", "info");
      descInput.focus();
      return;
    }

    btnClassify.disabled = true;
    btnClassify.textContent = "Analyzing...";

    try {
      const res = await fetch(`${API_BASE}/ai/classify`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textToClassify })
      });

      if (!res.ok) throw new Error("Classification failed");
      const data = await res.json();

      // Auto update inputs
      if (categorySelect && data.category) {
        categorySelect.value = data.category;
      }

      if (titleInput && (!titleInput.value || titleInput.value.length < 15)) {
        titleInput.value = data.suggested_title;
      }

      if (descInput) {
        descInput.value = data.enhanced_description;
      }

      // Render Feedback Badge
      if (badge) {
        badge.style.display = "block";
        badge.innerHTML = `
          <strong>✨ AI Classification Result:</strong><br>
          • <strong>Category:</strong> ${data.category}<br>
          • <strong>Priority Grade:</strong> <span style="color: ${data.urgency.includes('High') ? '#f87171' : '#6ee7b7'}; font-weight: 700;">${data.urgency}</span><br>
          • <strong>Estimated Volume:</strong> ${data.estimated_volume}
        `;
      }

      showToast("Issue auto-classified into " + data.category + "!", "success");
    } catch (err) {
      showToast("AI classification unavailable.", "error");
    } finally {
      btnClassify.disabled = false;
      btnClassify.textContent = "✨ AI Auto-Classify";
    }
  });
}

// ================= ECO-AI VISION WASTE SCANNER =================
function bindEcoAIVisionScanner() {
  const presetButtons = document.querySelectorAll(".btn-preset");
  presetButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      presetButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const sample = btn.getAttribute("data-sample");
      loadEcoAIVisionScanner(sample);
    });
  });
}

async function loadEcoAIVisionScanner(sampleType = "plastic_bottle") {
  const resultBox = document.getElementById("scanner-result-box");
  if (!resultBox) return;

  resultBox.innerHTML = `
    <div style="text-align: center; padding: 2rem; color: var(--accent-cyan);">
      <div style="font-size: 1.5rem; margin-bottom: 0.5rem; animation: pulse 1s infinite;">🔍</div>
      <strong>EcoAI Neural Vision Analyzing Molecular & Physical Components...</strong>
    </div>
  `;

  try {
    const res = await fetch(`${API_BASE}/ai/scan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_type: sampleType })
    });

    const data = await res.json();

    resultBox.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
        <div>
          <span class="bin-tag ${data.bin_color}">Target: ${data.bin}</span>
          <h4 style="font-size: 1.35rem; color: #fff; margin: 0.5rem 0 0.25rem 0;">${escapeHtml(data.detected_item)}</h4>
          <span style="font-size: 0.82rem; color: var(--text-muted);">${escapeHtml(data.category)}</span>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 1.6rem; font-weight: 800; color: #34d399; font-family: var(--font-mono);">${data.confidence}%</div>
          <span style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-muted);">AI Confidence</span>
        </div>
      </div>

      <div class="scanner-stats-grid">
        <div class="scanner-stat-box">
          <span class="scanner-stat-val text-success">${data.recyclability_score}%</span>
          <span class="scanner-stat-lbl">Recyclability Index</span>
        </div>
        <div class="scanner-stat-box">
          <span class="scanner-stat-val text-accent">+${data.carbon_saved_kg} kg</span>
          <span class="scanner-stat-lbl">CO2 Avoided vs Landfill</span>
        </div>
        <div class="scanner-stat-box">
          <span class="scanner-stat-val" style="color: #a78bfa;">${data.bin.split(' ')[0]}</span>
          <span class="scanner-stat-lbl">Prescribed Bin Color</span>
        </div>
      </div>

      <div class="examples-box" style="margin-top: 1rem;">
        <strong>Recommended Segregation Procedure:</strong>
        <ul>
          ${data.instructions.map(inst => `<li>${escapeHtml(inst)}</li>`).join("")}
        </ul>
      </div>
    `;
  } catch (err) {
    resultBox.innerHTML = `<p style="color: #f87171;">Error performing AI vision scan.</p>`;
  }
}

// ================= AI FLEET & ROUTE OPTIMIZER =================
function bindAIRouteOptimizer() {
  const btnRefresh = document.getElementById("btn-refresh-ai-route");
  if (btnRefresh) {
    btnRefresh.addEventListener("click", () => {
      loadAIRouteOptimizer();
      showToast("Recalculating optimal dispatch trajectory...", "info");
    });
  }
}

async function loadAIRouteOptimizer() {
  const container = document.getElementById("ai-route-content");
  if (!container || !currentToken) return;

  container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.9rem;">Crunching spatial clusters and transit distance matrices...</p>`;

  try {
    const res = await fetch(`${API_BASE}/ai/route-optimizer`, {
      headers: { "Authorization": `Bearer ${currentToken}` }
    });

    if (!res.ok) {
      container.innerHTML = `<p style="color: var(--text-muted);">Sign in as Administrator to view fleet route optimization.</p>`;
      return;
    }

    const data = await res.json();

    if (!data.recommended_route || data.recommended_route.length === 0) {
      container.innerHTML = `
        <div style="background: rgba(15,23,42,0.6); padding: 1.5rem; border-radius: var(--radius-md); text-align: center;">
          <p style="color: var(--text-muted);">No pending complaints requiring immediate dispatch routing. All clear!</p>
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div class="route-meta-banner">
        <div class="route-meta-item">
          <span class="route-meta-val">${data.total_stops} Incidents</span>
          <span class="route-meta-lbl">Sequenced Stops</span>
        </div>
        <div class="route-meta-item">
          <span class="route-meta-val text-success">-${data.estimated_fuel_saved_liters} L</span>
          <span class="route-meta-lbl">Fuel Saved (AI Transit Routing)</span>
        </div>
        <div class="route-meta-item">
          <span class="route-meta-val text-accent">-${data.co2_emissions_avoided_kg} kg</span>
          <span class="route-meta-lbl">Carbon Emitted Avoided</span>
        </div>
        <div class="route-meta-item" style="margin-left: auto;">
          <span class="badge badge-progress">Assigned: ${escapeHtml(data.vehicle_id)}</span>
        </div>
      </div>

      <div class="route-stops-list">
        ${data.recommended_route.map(stop => `
          <div class="route-stop-item">
            <div class="stop-num">${stop.stop_number}</div>
            <div class="stop-info">
              <div class="stop-loc">${escapeHtml(stop.location)}</div>
              <div class="stop-cat">${escapeHtml(stop.category)} &bull; ${escapeHtml(stop.title)}</div>
            </div>
            <div>
              <span class="badge ${stop.priority.includes('Urgent') ? 'badge-pending' : 'badge-assigned'}">Priority ${stop.priority}</span>
            </div>
            <div class="stop-eta">~${stop.eta_minutes} mins</div>
          </div>
        `).join("")}
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<p style="color: #f87171;">Could not compute route optimization.</p>`;
  }
}

// ================= GITHUB STYLE SWACHHATA ACTIVITY HEATMAP =================
let cachedHeatmapData = null;

function bindGitHubHeatmap() {
  // Bind any heatmap hover or interaction
}

async function loadGitHubHeatmap() {
  const grid = document.getElementById("heatmap-grid");
  if (!grid) return;

  try {
    const headers = {};
    if (currentToken) headers["Authorization"] = `Bearer ${currentToken}`;

    const res = await fetch(`${API_BASE}/user/heatmap`, { headers });
    let data;
    if (res.ok) {
      data = await res.json();
      cachedHeatmapData = data;
    } else {
      // Fallback generator for guest view
      data = generateFallbackHeatmap();
    }

    renderHeatmap(data);
  } catch (err) {
    renderHeatmap(generateFallbackHeatmap());
  }
}

function generateFallbackHeatmap() {
  const squares = [];
  const today = new Date();
  for (let i = 111; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().split("T")[0];
    const h = (i * 7 + 3) % 10;
    const count = h === 1 ? 2 : (h === 2 ? 3 : (h === 4 ? 1 : 0));
    squares.push({
      date: dateStr,
      count,
      level: Math.min(count, 4)
    });
  }
  return {
    total_contributions: 42,
    streak_days: 14,
    karma_points: 340,
    squares
  };
}

function renderHeatmap(data) {
  const grid = document.getElementById("heatmap-grid");
  if (!grid) return;

  const streakPill = document.getElementById("heatmap-streak");
  const karmaPill = document.getElementById("heatmap-karma");
  const headerStreak = document.getElementById("user-streak-badge");
  const headerKarma = document.getElementById("user-karma-badge");

  if (streakPill) streakPill.textContent = `🔥 ${data.streak_days || 14}-Day Streak`;
  if (karmaPill) karmaPill.textContent = `🌟 ${data.karma_points || 340} Karma`;
  if (headerStreak) headerStreak.textContent = `🔥 ${data.streak_days || 14}d Streak`;
  if (headerKarma) headerKarma.textContent = `🌟 ${data.karma_points || 340} Karma`;

  grid.innerHTML = data.squares.map(sq => {
    const titleText = sq.count === 0 
      ? `No sanitation activity on ${sq.date}` 
      : `${sq.count} verified sanitation contribution${sq.count > 1 ? 's' : ''} on ${sq.date}`;
    return `<div class="heatmap-square lvl-${sq.level}" title="${titleText}" data-date="${sq.date}" data-count="${sq.count}"></div>`;
  }).join("");
}

// ================= AI SWACHHATA ACADEMY & CERTIFICATION =================
const DEFAULT_SWACHHATA_LESSONS = [
  {
    id: "lesson-1",
    number: "01",
    title: "The 2-Bin Revolution: Geela vs Sookha Kachra",
    hindiTitle: "हरा कूड़ादान बनाम नीला कूड़ादान - स्रोत पर पृथक्करण",
    category: "Foundation",
    readTime: "3 min",
    icon: "🌱",
    summary: "Why mixing kitchen wet waste with dry recyclables creates toxic landfill fires at Ghazipur and Deonar.",
    content: [
      { subheading: "1. What is Geela Kachra (Wet Waste)?", text: "All organic kitchen leftovers: vegetable peels (sabzi ke chilke), fruit rinds, stale rotis, used chai patti, eggshells, and temple flowers. If it can rot naturally, it belongs in the Green Bin (हरा कूड़ादान)." },
      { subheading: "2. What is Sookha Kachra (Dry Waste)?", text: "Clean cardboard cartons, plastic milk pouches, PET beverage bottles, metal cans, newspaper raddi, and glass containers. Keep it in the Blue Bin (नीला कूड़ादान)." },
      { subheading: "3. The Tragedy of Mixing Waste", text: "When wet dal or sabzi gets onto paper and cardboard, the paper pulp becomes unrecyclable. Trapped wet organic waste produces methane gas in open landfills, causing dangerous self-igniting landfill fires." }
    ],
    swachhTip: "Keep two separate small dustbins right under your kitchen sink. Segregation takes only 2 seconds!"
  },
  {
    id: "lesson-2",
    number: "02",
    title: "Nirmalya & Temple Floral Waste Upcycling",
    hindiTitle: "पवित्र निर्माल्य: फूलों से बनेगी अगरबत्ती व जैविक खाद",
    category: "Culture & Faith",
    readTime: "3 min",
    icon: "🌸",
    summary: "Transforming sacred puja flowers into natural organic incense and compost instead of suffocating holy rivers.",
    content: [
      { subheading: "1. The River Pollution Dilemma", text: "Every year, thousands of metric tons of puja flowers and garlands wrapped in non-biodegradable polythene bags are immersed into rivers like the Ganga, Yamuna, and Godavari, depleting oxygen levels for aquatic life." },
      { subheading: "2. The Nirmalya Upcycling Path", text: "Real flower petals (marigold, rose, jasmine) contain essential natural oils. When separated from plastic threads and golden foil, they are sun-dried and powdered into charcoal-free dhoop, holy vermicompost, and natural holi colors." },
      { subheading: "3. How You Can Do It at Home", text: "Keep a dedicated earthen pot for daily puja flowers. Allow them to dry naturally and crumble them into your home garden or Tulsi pot." }
    ],
    swachhTip: "Never throw polythene bags into rivers along with puja offerings. True devotion preserves Mother Nature."
  },
  {
    id: "lesson-3",
    number: "03",
    title: "The 100-Crore Milk Pouch Habit & Single-Use Plastic",
    hindiTitle: "दूध की थैली का कोना पूरा न काटें: एक छोटी आदत, बड़ा बदलाव",
    category: "Daily Habits",
    readTime: "2 min",
    icon: "🥛",
    summary: "How snipping milk pouches without detaching the tiny plastic corner avoids microplastic choking in cows & marine life.",
    content: [
      { subheading: "1. The Mystery of the Missing Corners", text: "India consumes over 100 million milk and oil pouches every single day. Most people snip off a small 1-centimeter triangle from the top corner and throw it into the trash." },
      { subheading: "2. Why Micro-Snips are Catastrophic", text: "These microscopic plastic triangles are too small for municipal waste sorting machines. They slip through grates, get washed into storm drains, end up in cow bellies, and pollute agricultural fields for 500 years." },
      { subheading: "3. The Simple Solution: Slit, Don't Snip!", text: "Cut a straight slit across the corner or leave the corner tip hanging connected to the main body of the pouch. That way, 100% of the plastic gets bundled and recycled into secondary plastic lumber." }
    ],
    swachhTip: "Always leave the cut corner attached to the pouch. Rinse and dry before placing in the Blue Bin."
  },
  {
    id: "lesson-4",
    number: "04",
    title: "Odorless Terrace & Balcony Composting (घर की खाद)",
    hindiTitle: "बालकनी में बदबू-रहित खाद बनाना सीखें",
    category: "Home Green",
    readTime: "4 min",
    icon: "🪴",
    summary: "Converting everyday dal, roti, and vegetable peels into nutrient-rich 'Black Gold' for Indian apartments.",
    content: [
      { subheading: "1. The 3-Tier Earthen Khamba System", text: "Terracotta pots allow natural air circulation, preventing bad odors. Place kitchen peels (Greens = Nitrogen) and cover them with a layer of dry crushed leaves or cocopeat (Browns = Carbon)." },
      { subheading: "2. Maintaining the Balance", text: "Never add large bones, thick plastic wrappers, or excessive oily gravies to home compost. Sprinkle a spoonful of sour buttermilk (chaach/dahi) or compost microbes once a week to speed up digestion." },
      { subheading: "3. Harvesting Black Gold", text: "In 30 to 45 days, the contents turn into a dark, earthy-smelling organic compost that will make your home vegetables, curry leaves, and flowering plants thrive naturally without synthetic chemicals." }
    ],
    swachhTip: "One household composting diverts over 300 kilograms of wet waste per year from city landfills!"
  },
  {
    id: "lesson-5",
    number: "05",
    title: "Dignity of Safai Mitras & The Red Cross Rule",
    hindiTitle: "सफाई मित्रों का सम्मान: सेनेटरी कचरे पर लाल बिंदी का नियम",
    category: "Human Dignity",
    readTime: "3 min",
    icon: "❤️",
    summary: "Protecting sanitation workers from biological infection through responsible newspaper wrapping and red-dot marking.",
    content: [
      { subheading: "1. The Unseen Heroes of Clean India", text: "Our Safai Mitras (sanitation workers) wake up at 5:00 AM daily to sweep our streets and collect waste. Handling unsegregated dirty pads, sharp shaving blades, and broken glass puts them at extreme risk of hepatitis, tetanus, and skin infections." },
      { subheading: "2. The Red Dot / Red Cross Protocol", text: "Wrap all used menstrual napkins, baby diapers, and adult sanitary pads in old newspaper or paper disposal envelopes. Using a red sketch pen or bindu, mark a bold red cross or dot on the outer packet." },
      { subheading: "3. Sharp Waste Precaution", text: "Place used razor blades, broken tubelights, and glass injection vials inside an empty cardboard box or thick plastic jar before discarding." }
    ],
    swachhTip: "Sanitation workers are the frontline guardians of our city's public health. Treat them with respect and gratitude."
  }
];

let cachedLessons = [...DEFAULT_SWACHHATA_LESSONS];
let quizSelectedAnswers = {};

function bindSwachhataAcademy() {
  // 1. Bind Quiz Option Button Clicks
  const quizForm = document.getElementById("form-swachh-quiz");
  if (quizForm) {
    quizForm.addEventListener("click", (e) => {
      const btn = e.target.closest(".quiz-opt-btn");
      if (!btn) return;

      const qid = btn.getAttribute("data-qid");
      const optIdx = parseInt(btn.getAttribute("data-opt"), 10);

      // Deselect siblings in the same question block
      const parentGrid = btn.closest(".quiz-options-grid");
      parentGrid.querySelectorAll(".quiz-opt-btn").forEach(b => b.classList.remove("selected"));

      // Select this button
      btn.classList.add("selected");
      quizSelectedAnswers[qid] = optIdx;
    });

    // 2. Bind Quiz Form Submit
    quizForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const answeredCount = Object.keys(quizSelectedAnswers).length;
      if (answeredCount < 4) {
        showToast(`Please answer all 4 questions before submitting (answered ${answeredCount}/4).`, "info");
        return;
      }

      const submitBtn = document.getElementById("btn-submit-quiz");
      submitBtn.disabled = true;
      submitBtn.textContent = "AI Evaluating Answers...";

      try {
        const userName = currentUser ? currentUser.name : "Aarav Sharma";
        const headers = { "Content-Type": "application/json" };
        if (currentToken) headers["Authorization"] = `Bearer ${currentToken}`;

        const res = await fetch(`${API_BASE}/ai/quiz`, {
          method: "POST",
          headers,
          body: JSON.stringify({ answers: quizSelectedAnswers, userName })
        });

        const data = await res.json();
        renderQuizEvaluation(data);
      } catch (err) {
        showToast("Error submitting quiz evaluation.", "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Submit Answers & Evaluate →";
      }
    });
  }

  // 3. Bind Lesson Modal Close Buttons
  const btnCloseLesson = document.getElementById("btn-close-lesson-modal");
  const btnDismissLesson = document.getElementById("btn-dismiss-lesson-modal");
  if (btnCloseLesson) btnCloseLesson.addEventListener("click", closeLessonModal);
  if (btnDismissLesson) btnDismissLesson.addEventListener("click", closeLessonModal);
}

async function loadSwachhataLessons() {
  const container = document.getElementById("academy-lessons-grid");
  if (!container) return;

  try {
    const res = await fetch(`${API_BASE}/ai/lessons`);
    if (!res.ok) return;

    const data = await res.json();
    cachedLessons = data.lessons || [];

    container.innerHTML = cachedLessons.map(l => `
      <div class="lesson-card" onclick="openLessonModal('${l.id}')">
        <div class="lesson-top-meta">
          <span class="lesson-num-badge">MODULE ${l.number}</span>
          <span class="lesson-read-time">🕒 ${l.readTime} read &bull; ${l.category}</span>
        </div>
        <div style="font-size: 1.5rem; margin-top: 0.25rem;">${l.icon}</div>
        <h3>${escapeHtml(l.title)}</h3>
        <div class="lesson-hindi-title">${escapeHtml(l.hindiTitle)}</div>
        <p class="lesson-summary">${escapeHtml(l.summary)}</p>
        <button type="button" class="lesson-action-btn">
          Read Illustrated Module &rarr;
        </button>
      </div>
    `).join("");
  } catch (err) {
    console.error("Error loading lessons:", err);
  }
}

function openLessonModal(lessonId) {
  const lesson = cachedLessons.find(l => l.id === lessonId);
  if (!lesson) return;

  document.getElementById("modal-lesson-cat").textContent = `Module ${lesson.number} &bull; ${lesson.category}`;
  document.getElementById("modal-lesson-title").textContent = `${lesson.icon} ${lesson.title}`;
  document.getElementById("modal-lesson-hindi").textContent = lesson.hindiTitle;

  const body = document.getElementById("modal-lesson-body");
  body.innerHTML = `
    ${lesson.content.map(sec => `
      <div class="lesson-section-block">
        <h4>${escapeHtml(sec.subheading)}</h4>
        <p>${escapeHtml(sec.text)}</p>
      </div>
    `).join("")}
    <div class="lesson-pro-tip">
      <strong>💡 Swachhata Pro Tip:</strong> ${escapeHtml(lesson.swachhTip)}
    </div>
  `;

  document.getElementById("modal-lesson").style.display = "flex";
}

function closeLessonModal() {
  document.getElementById("modal-lesson").style.display = "none";
}

function renderQuizEvaluation(data) {
  const statusBadge = document.getElementById("quiz-status-badge");
  if (statusBadge) {
    statusBadge.textContent = `${data.correctCount}/${data.total} Correct (${data.percentage}%)`;
    statusBadge.className = data.passed ? "badge badge-resolved" : "badge badge-pending";
  }

  // Highlight correct/incorrect buttons
  data.feedback.forEach(item => {
    const qBlock = document.querySelectorAll(".quiz-q-block")[item.questionId - 1];
    if (qBlock) {
      const btns = qBlock.querySelectorAll(".quiz-opt-btn");
      btns.forEach((btn, idx) => {
        btn.classList.remove("selected", "correct", "wrong");
        if (idx === item.correctIndex) {
          btn.classList.add("correct");
        } else if (idx === item.userSelected && !item.isCorrect) {
          btn.classList.add("wrong");
        }
      });
    }
  });

  const certArea = document.getElementById("certificate-output-area");
  if (!certArea) return;

  if (data.passed && data.certificate) {
    const cert = data.certificate;
    certArea.style.display = "block";
    certArea.innerHTML = `
      <div class="certificate-display-card">
        <div class="cert-emblem">🇮🇳 🪷 🏛️</div>
        <div class="cert-heading">Swachh Bharat Citizen Certificate</div>
        <div class="cert-subheading">स्वच्छ नागरिक प्रमाण-पत्र &bull; Clean India Mission</div>
        <p style="font-size: 0.95rem; color: #cbd5e1; margin-bottom: 0.5rem;">This is proudly presented to</p>
        <div class="cert-citizen-name">${escapeHtml(cert.citizenName)}</div>
        <div class="cert-body-text">
          Having demonstrated exemplary waste segregation knowledge, environmental civic leadership, 
          and sacred upcycling consciousness under the guidance of the <strong>AI Swachhata Academy</strong>.
        </div>
        <div style="display: flex; justify-content: center; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
          <span class="badge badge-resolved">Grade: ${cert.grade}</span>
          <span class="badge badge-admin">Quiz Score: ${cert.score}</span>
          <span class="karma-pill">+50 Karma Points Awarded!</span>
        </div>
        <div class="cert-footer-row">
          <div>
            <span>Verified Certificate ID:</span><br>
            <span class="cert-id">${cert.certificateId}</span>
          </div>
          <div>
            <span>Issued on:</span> <strong>${cert.date}</strong>
          </div>
          <div>
            <span>Authority:</span> <strong>Nagar Nigam Sanitation Directorate</strong>
          </div>
        </div>
        <div style="margin-top: 1.75rem;">
          <button class="btn btn-primary" onclick="window.print()">
            🖨️ Print / Download Official Certificate
          </button>
        </div>
      </div>
    `;
    certArea.scrollIntoView({ behavior: "smooth" });
    showToast(`Congratulations ${cert.citizenName}! You earned the Swachh Nagrik Certificate! (+50 Karma Points)`, "success");
    loadGitHubHeatmap();
  } else {
    certArea.style.display = "block";
    certArea.innerHTML = `
      <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: var(--radius-md); padding: 1.5rem; text-align: center; margin-top: 1.5rem;">
        <h4 style="color: #f87171; font-size: 1.15rem; margin-bottom: 0.5rem;">Quiz Score: ${data.percentage}% (Need 75% to Qualify)</h4>
        <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 1rem;">
          Review the marked correct answers above or re-read Module 01 to Module 05, then try again to earn your certificate!
        </p>
      </div>
    `;
    showToast(`You scored ${data.percentage}%. Please review the modules and try again!`, "info");
  }
}

// ================= WARD CLEANLINESS LEADERBOARD (ECOTRACK INSPIRED) =================
async function loadWardLeaderboard() {
  const tbody = document.getElementById("ward-leaderboard-tbody");
  if (!tbody) return;

  try {
    const res = await fetch(`${API_BASE}/wards/leaderboard`);
    if (!res.ok) return;
    const data = await res.json();
    
    tbody.innerHTML = (data.leaderboard || []).map(w => {
      const rankBadgeClass = w.rank === 1 ? "rank-1" : (w.rank === 2 ? "rank-2" : (w.rank === 3 ? "rank-3" : "rank-other"));
      return `
        <tr>
          <td><span class="rank-badge ${rankBadgeClass}">#${w.rank}</span></td>
          <td>
            <strong>${escapeHtml(w.ward)}</strong>
          </td>
          <td>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <span style="font-weight: 800; color: #34d399;">${w.score}/100</span>
              <div class="progress-track" style="width: 80px; height: 6px;">
                <div class="progress-fill" style="width: ${w.score}%"></div>
              </div>
            </div>
          </td>
          <td><span class="badge badge-resolved">${escapeHtml(w.status)}</span></td>
          <td><span style="color: #93c5fd;">🚛 ${w.crews_active} Trucks</span></td>
          <td><span>⏱️ ~${w.avg_resolution_hrs} hrs (${w.resolved_pct}% resolved)</span></td>
        </tr>
      `;
    }).join("");
  } catch (err) {
    console.error("Error loading ward leaderboard:", err);
  }
}

// ================= HARIT TYOHAR / GREEN FESTIVALS (ECOTRACK INSPIRED) =================
async function loadGreenFestivals() {
  const container = document.getElementById("festivals-cards-grid");
  if (!container) return;

  try {
    const res = await fetch(`${API_BASE}/festivals`);
    if (!res.ok) return;
    const data = await res.json();
    
    container.innerHTML = (data.festivals || []).map(f => `
      <div class="festival-card">
        <div class="festival-card-top">
          <div class="festival-icon">${f.icon}</div>
          <div>
            <h4>${escapeHtml(f.name)}</h4>
            <div class="festival-tagline">${escapeHtml(f.tagline)}</div>
          </div>
        </div>
        <div class="festival-challenge">
          <strong>⚠️ Challenge:</strong> ${escapeHtml(f.challenge)}
        </div>
        <ul class="festival-solutions">
          ${f.greenSolutions.map(s => `<li>${escapeHtml(s)}</li>`).join("")}
        </ul>
        <span class="festival-badge-action">${escapeHtml(f.actionBadge)}</span>
      </div>
    `).join("");
  } catch (err) {
    console.error("Error loading green festivals:", err);
  }
}


