/**
 * DESHMRITTIKA / BHUMI-SYNC — Main Application Controller
 * Handles UI interactions, multilingual localization, Leaflet mapping,
 * due diligence rendering, officer workflow, and document verifications.
 */

// Application State
const AppState = {
  lang: 'bn',
  user: {
    user_id: 'USR-CITIZEN-01',
    name: 'মো: রফিকুল ইসলাম',
    role: 'CITIZEN',
    email: 'citizen@example.com'
  },
  currentView: 'citizen',
  selectedParcelId: 'BD-PAR-000101',
  map: null,
  parcelGeoLayer: null,
  officerCases: [],
  selectedCase: null
};

// Demo Preset Identifiers
const DEMO_PRESETS = {
  ds1_fraud: { dag: 101, mouza: 'Aminbazar', label: 'প্রতারণামূলক দ্বৈত বিক্রয় (DS-01) - দাগ ১০১' },
  ds2_clean: { dag: 1001, mouza: 'Birulia', label: 'নির্দোষ ধারাবাহিক বিক্রয় (DS-02) - দাগ ১০০১' },
  khas_plot: { dag: 205, mouza: 'Aminbazar', label: '১-নং খাস খতিয়ানভুক্ত সরকারি জমি - দাগ ২০৫' },
  corridor: { dag: 310, mouza: 'Birulia', label: 'মহাসড়ক অধিগ্রহণ জোনভুক্ত দাগ ৩১০' }
};

// UI Localization Dictionary
const I18N = {
  bn: {
    appName: "দেশমৃত্তিকা",
    appSub: "স্মার্ট ক্যাডাস্ট্রাল ও ডিজিটাল ভূমি রেকর্ড প্ল্যাটফর্ম",
    tagline: "আপনার জমি, আমাদের দায়িত্ব",
    searchPlaceholder: "দাগ নম্বর লিখুন...",
    btnSearch: "অনুসন্ধান করুন",
    btnReset: "রিসেট",
    searchResults: "অনুসন্ধানের ফলাফল",
    viewProfile: "বিস্তারিত দেখুন",
    riskSafe: "নিরাপদ জমি",
    riskCaution: "সতর্কতামূলক",
    riskHigh: "উচ্চ ঝুঁকি",
    riskCritical: "লেনদেন ঝুঁকিপূর্ণ / স্থগিত",
    point1Title: "১. বায়া দলিলের ধারাবাহিকতা",
    point2Title: "২. নামজারি ও জমাভাগ স্থিতি",
    point3Title: "৩. আদালত নিষেধাজ্ঞা ও দেওয়ানি মামলা",
    point4Title: "৪. ভূমি উন্নয়ন কর ও দাখিলা",
    point5Title: "৫. খাস জমি ও অধিগ্রহণ জোন",
    printReport: "ডসিয়ার প্রিন্ট / সংরক্ষণ",
    officerQueue: "অফিসার ট্রায়াজ কিউ",
    caseSeverity: "ঝুঁকির মাত্রা",
    actionApprove: "বৈধ অনুমোদন",
    actionReject: "জালিয়াতি ফ্ল্যাগ",
    actionInspect: "সরেজমিন পরিদর্শন নির্দেশ",
    precheckBtn: "প্রাক-যাচাই চালান",
    authenticityValid: "প্রামাণ্য নথি (Authentic)",
    authenticityTampered: "জালিয়াতি / পরিবর্তন শনাক্ত (Tampered)"
  },
  en: {
    appName: "DeshMrittika",
    appSub: "Smart Cadastral Mapping & Land Record Verification",
    tagline: "Your Land, Our Responsibility",
    searchPlaceholder: "Enter Dag number...",
    btnSearch: "Search Records",
    btnReset: "Reset",
    searchResults: "Search Results",
    viewProfile: "View Dossier",
    riskSafe: "Safe Parcel",
    riskCaution: "Caution Required",
    riskHigh: "High Risk",
    riskCritical: "Critical Risk / Blocked",
    point1Title: "1. Chain of Title (Baya Deeds)",
    point2Title: "2. e-Mutation & Jamabhag Status",
    point3Title: "3. Court Injunctions & Civil Suits",
    point4Title: "4. Land Development Tax Compliance",
    point5Title: "5. 1-No Khas Land & Acquisition Buffer",
    printReport: "Print / Save Dossier",
    officerQueue: "Officer Triage Queue",
    caseSeverity: "Risk Severity",
    actionApprove: "Approve Legitimate",
    actionReject: "Flag Fraud Suspicion",
    actionInspect: "Order Physical Inspection",
    precheckBtn: "Run Pre-Check",
    authenticityValid: "Verified Authentic",
    authenticityTampered: "Tamper Detected / Unregistered"
  }
};

// Initialize Application on DOM Ready
document.addEventListener('DOMContentLoaded', async () => {
  initNavigation();
  initRoleSwitcher();
  initLanguageToggle();
  initSearch();
  initMap();
  initMutationSimulator();
  initDocumentVerifier();
  initOfficerWorkflow();

  // Load initial health status
  const health = await LandTechAPI.getHealth();
  updateHealthIndicator(health);

  // Auto-login citizen by default
  try {
    await LandTechAPI.login(AppState.user.email);
  } catch (e) {
    console.warn("Initial login fallback:", e);
  }

  // Load initial sample parcel BD-PAR-000101
  loadParcelDossier('BD-PAR-000101');
});

function updateHealthIndicator(health) {
  const el = document.getElementById('system-status');
  if (el) {
    if (health.status === 'HEALTHY') {
      const mb = health.database ? health.database.size_mb : 109.35;
      el.innerHTML = `<span class="status-dot"></span> <span>অনলাইন (${mb} MB ডেটাবেস | ১০০,০০০ প্লট)</span>`;
    } else {
      el.innerHTML = `<span class="status-dot" style="background:#ef4444"></span> <span>অফলাইন</span>`;
    }
  }
}

// Navigation between portals
function initNavigation() {
  const tabs = document.querySelectorAll('.nav-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      const targetView = tab.getAttribute('data-view');
      switchView(targetView);
    });
  });
}

function switchView(viewName) {
  AppState.currentView = viewName;
  document.querySelectorAll('.nav-tab').forEach(t => {
    t.classList.toggle('active', t.getAttribute('data-view') === viewName);
  });
  document.querySelectorAll('.view-section').forEach(sec => {
    sec.classList.toggle('active', sec.id === `view-${viewName}`);
  });

  // Refresh view specific components
  if (viewName === 'citizen' && AppState.map) {
    setTimeout(() => AppState.map.invalidateSize(), 200);
  } else if (viewName === 'officer') {
    loadOfficerQueue();
  }
}

// Role Switcher
function initRoleSwitcher() {
  const select = document.getElementById('role-selector');
  if (!select) return;

  select.addEventListener('change', async (e) => {
    const role = e.target.value;
    let email = 'citizen@example.com';
    if (role === 'BUYER') email = 'buyer@example.com';
    else if (role === 'OFFICER') email = 'officer@savar.land.gov.bd';
    else if (role === 'ADMINISTRATOR') email = 'admin@deshmrittika.gov.bd';

    try {
      const authData = await LandTechAPI.login(email);
      AppState.user = {
        user_id: authData.user_id,
        name: authData.name,
        role: authData.role,
        email: email
      };
      showToast(`ভূমিকা পরিবর্তিত: ${authData.name} (${authData.role})`);

      // If user switched to officer and on officer tab, refresh queue
      if (AppState.currentView === 'officer') {
        loadOfficerQueue();
      }
    } catch (err) {
      alert(`Role change failed: ${err.message}`);
    }
  });
}

// Language Toggle
function initLanguageToggle() {
  const btn = document.getElementById('lang-toggle');
  if (!btn) return;

  btn.addEventListener('click', () => {
    AppState.lang = AppState.lang === 'bn' ? 'en' : 'bn';
    btn.textContent = AppState.lang === 'bn' ? 'English' : 'বাংলা';
    applyTranslations();
  });
}

function applyTranslations() {
  const dict = I18N[AppState.lang];
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) el.textContent = dict[key];
  });
}

// Toast Notifications
function showToast(msg) {
  let toast = document.getElementById('toast-notice');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast-notice';
    toast.style.cssText = `
      position: fixed; bottom: 24px; right: 24px; z-index: 9999;
      background: #0f172a; color: #ffffff; padding: 12px 20px;
      border-radius: 8px; font-size: 14px; font-weight: 500;
      box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);
      transition: all 0.3s ease; opacity: 0; transform: translateY(10px);
    `;
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.opacity = '1';
  toast.style.transform = 'translateY(0)';
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
  }, 3500);
}

// Map Initialization
function initMap() {
  const mapContainer = document.getElementById('leaflet-map');
  if (!mapContainer || AppState.map) return;

  // Center on Savar Upazila, Dhaka coordinates
  AppState.map = L.map('leaflet-map').setView([23.8560, 90.2600], 14);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors | DeshMrittika Cadastre'
  }).addTo(AppState.map);
}

// Universal Search
function initSearch() {
  const form = document.getElementById('search-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      executeSearch();
    });
  }

  // Preset Buttons
  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const type = btn.getAttribute('data-preset');
      applyPresetSearch(type);
    });
  });
}

function applyPresetSearch(type) {
  const dagInput = document.getElementById('search-dag');
  const mouzaInput = document.getElementById('search-mouza');
  const idInput = document.getElementById('search-id');

  if (type === 'ds1') {
    if (dagInput) dagInput.value = '101';
    if (mouzaInput) mouzaInput.value = 'Aminbazar';
    if (idInput) idInput.value = '';
  } else if (type === 'ds2') {
    if (dagInput) dagInput.value = '1001';
    if (mouzaInput) mouzaInput.value = 'Birulia';
    if (idInput) idInput.value = '';
  } else if (type === 'khas') {
    if (dagInput) dagInput.value = '205';
    if (mouzaInput) mouzaInput.value = 'Aminbazar';
    if (idInput) idInput.value = '';
  }
  executeSearch();
}

async function executeSearch() {
  const dagVal = document.getElementById('search-dag')?.value.trim();
  const mouzaVal = document.getElementById('search-mouza')?.value.trim();
  const khatianVal = document.getElementById('search-khatian')?.value.trim();
  const idVal = document.getElementById('search-id')?.value.trim();

  const resultsArea = document.getElementById('search-results-tbody');
  const countSpan = document.getElementById('results-count');
  if (resultsArea) {
    resultsArea.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem;">অনুসন্ধান করা হচ্ছে...</td></tr>`;
  }

  try {
    const res = await LandTechAPI.searchParcels({
      dag: dagVal || null,
      mouza: mouzaVal || null,
      khatian: khatianVal || null,
      parcel_id: idVal || null,
      limit: 15
    });

    if (countSpan) countSpan.textContent = res.total_matches;

    if (!res.parcels || res.parcels.length === 0) {
      resultsArea.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem; color:#ef4444;">কোন রেকর্ড পাওয়া যায়নি। ভিন্ন মান দিয়ে চেষ্টা করুন।</td></tr>`;
      return;
    }

    resultsArea.innerHTML = '';
    res.parcels.forEach(p => {
      const tr = document.createElement('tr');
      const disputeBadge = p.is_disputed
        ? `<span class="badge badge-danger">⚠️ বিরোধপূর্ণ</span>`
        : `<span class="badge badge-success">✓ নিয়মিত</span>`;

      tr.innerHTML = `
        <td><strong>${p.parcel_id}</strong></td>
        <td>${p.mouza} (${p.jl_number})</td>
        <td>${p.dag_number}</td>
        <td>${p.khatian_number}</td>
        <td>${p.survey_type}</td>
        <td>${p.area_decimal} শতাংশ</td>
        <td>${disputeBadge}</td>
      `;

      tr.addEventListener('click', () => {
        document.querySelectorAll('#search-results-tbody tr').forEach(r => r.classList.remove('selected-row'));
        tr.classList.add('selected-row');
        loadParcelDossier(p.parcel_id);
      });

      resultsArea.appendChild(tr);
    });

    // Auto-load first parcel
    if (res.parcels.length > 0) {
      loadParcelDossier(res.parcels[0].parcel_id);
    }
  } catch (err) {
    if (resultsArea) {
      resultsArea.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#ef4444; padding:2rem;">অনুসন্ধানে সমস্যা: ${err.message}</td></tr>`;
    }
  }
}

// Load and Render Due Diligence Dossier
async function loadParcelDossier(parcelId) {
  AppState.selectedParcelId = parcelId;
  const dossierContainer = document.getElementById('dossier-view-container');
  if (!dossierContainer) return;

  try {
    const [dossier, profile, geojson] = await Promise.all([
      LandTechAPI.getDueDiligence(parcelId),
      LandTechAPI.getParcelProfile(parcelId),
      LandTechAPI.getParcelGeoJSON(parcelId).catch(() => null)
    ]);

    renderDossierView(dossier, profile);
    if (geojson && AppState.map) {
      renderGeoJSONOnMap(geojson, dossier.safety_rating);
    }
  } catch (err) {
    console.error("Dossier load error:", err);
    showToast(`ডসিয়ার লোড করতে ব্যর্থ: ${err.message}`);
  }
}

function renderDossierView(dossier, profile) {
  const p = dossier.parcel;

  // Basic Meta
  document.getElementById('dos-parcel-id').textContent = p.parcel_id;
  document.getElementById('dos-mouza-dag').textContent = `${p.mouza} | দাগ নং: ${p.dag_number} | খতিয়ান নং: ${p.khatian_number}`;
  document.getElementById('dos-area').textContent = `${p.area_decimal} শতাংশ (${p.land_classification})`;
  document.getElementById('dos-survey').textContent = `${p.survey_type} জরিপ | জেএল নং: ${p.jl_number}`;

  // Gauge & Overall Verdict
  const gaugeEl = document.getElementById('safety-gauge');
  const verdictTitle = document.getElementById('verdict-title');
  const verdictDesc = document.getElementById('verdict-desc');

  gaugeEl.className = 'gauge-circle';
  gaugeEl.querySelector('.score-num').textContent = dossier.risk_score;

  if (dossier.safety_rating === 'SAFE') {
    gaugeEl.classList.add('score-safe');
    verdictTitle.textContent = 'নিরাপদ জমি (Transaction Safe)';
    verdictTitle.style.color = 'var(--success-700)';
    verdictDesc.textContent = '৫-দফা নিরাপত্তা যাচাইয়ে কোনো বিরোধ বা দ্বৈত বিক্রয় পাওয়া যায়নি।';
  } else if (dossier.safety_rating === 'CAUTION') {
    gaugeEl.classList.add('score-caution');
    verdictTitle.textContent = 'সতর্কতা প্রয়োজন (Caution)';
    verdictTitle.style.color = 'var(--warning-700)';
    verdictDesc.textContent = 'বকেয়া কর বা প্রাথমিক অমিল শনাক্ত হয়েছে। বিস্তারিত যাচাই করুন।';
  } else if (dossier.safety_rating === 'HIGH_RISK') {
    gaugeEl.classList.add('score-high');
    verdictTitle.textContent = 'উচ্চ ঝুঁকিপূর্ণ জমি (High Risk)';
    verdictTitle.style.color = '#ea580c';
    verdictDesc.textContent = 'অনিষ্পন্ন হস্তান্তর বা দেওয়ানি নিষেধাজ্ঞার সম্ভাবনা রয়েছে।';
  } else {
    gaugeEl.classList.add('score-critical');
    verdictTitle.textContent = 'দ্বৈত বিক্রয় / লেনদেন নিষিদ্ধ (Critical Risk)';
    verdictTitle.style.color = 'var(--danger-700)';
    verdictDesc.textContent = 'প্রতারণামূলক হস্তান্তরের প্রমাণ পাওয়া গেছে! অবিলম্বে রেজিস্ট্রি স্থগিত রাখুন।';
  }

  // 5-Point Safety Shield Cards
  const shieldGrid = document.getElementById('safety-shield-grid');
  shieldGrid.innerHTML = '';

  dossier.safety_checklist.forEach(item => {
    const card = document.createElement('div');
    const isPass = item.status === 'PASS';
    const isWarn = item.status === 'WARN';
    card.className = `safety-check-card ${isPass ? 'check-pass' : isWarn ? 'check-warn' : 'check-fail'}`;

    const icon = isPass ? '✓' : isWarn ? '⚠️' : '✕';
    const badgeClass = isPass ? 'badge-success' : isWarn ? 'badge-warning' : 'badge-danger';

    card.innerHTML = `
      <div>
        <div class="check-header">
          <span class="check-title">${item.title_bn}</span>
          <span class="badge ${badgeClass}">${icon} ${item.status}</span>
        </div>
        <p class="check-desc">${item.details_bn}</p>
      </div>
      <div class="check-status-text" style="color: ${isPass ? 'var(--success-700)' : 'var(--danger-700)'}">
        ${isPass ? 'যাচাইকৃত বৈধ' : 'অসঙ্গতি শনাক্ত'}
      </div>
    `;
    shieldGrid.appendChild(card);
  });

  // Render Linked Profile Tabs (Owners, Historical Deeds, Tax, Mutations)
  renderProfileTabs(profile);
}

function renderProfileTabs(profile) {
  // Owners List
  const ownersEl = document.getElementById('tab-owners-content');
  if (ownersEl && profile.current_owners) {
    ownersEl.innerHTML = profile.current_owners.map(o => `
      <div style="padding: 0.5rem 0; border-bottom: 1px solid var(--slate-200);">
        <strong>${o.fictional_name}</strong> (${o.owner_id})
        <div style="font-size:0.8rem; color:var(--slate-600)">অংশ (Share): ${(o.ownership_share * 100).toFixed(1)}% | পিতা/স্বামী: ${o.father_or_spouse || 'উক্ত'}</div>
      </div>
    `).join('') || '<p>কোন তথ্য নেই</p>';
  }

  // Historical Deeds
  const deedsEl = document.getElementById('tab-deeds-content');
  if (deedsEl && profile.historical_deeds) {
    deedsEl.innerHTML = profile.historical_deeds.map(d => `
      <div style="padding: 0.5rem 0; border-bottom: 1px solid var(--slate-200);">
        <strong>দলিল নং: ${d.deed_number}</strong> (${d.registration_date})
        <div style="font-size:0.8rem; color:var(--slate-600)">বিক্রেতা: ${d.seller_name} ➔ ক্রেতা: ${d.buyer_name}</div>
        <div style="font-size:0.75rem; color:var(--primary-700)">হস্তান্তরিত জমি: ${d.declared_area} শতাংশ | স্থিতি: ${d.deed_status}</div>
      </div>
    `).join('') || '<p>কোন দলিল নেই</p>';
  }

  // Tax Status
  const taxEl = document.getElementById('tab-tax-content');
  if (taxEl && profile.tax_status) {
    const t = profile.tax_status;
    taxEl.innerHTML = `
      <div style="padding: 0.5rem 0;">
        <p><strong>হোল্ডিং নং:</strong> ${t.holding_number}</p>
        <p><strong>কর স্থিতি:</strong> <span class="badge ${t.arrear_amount > 0 ? 'badge-danger' : 'badge-success'}">${t.tax_status}</span></p>
        <p><strong>সর্বশেষ দাখিলা অর্থবছর:</strong> ${t.last_payment_fiscal_year}</p>
        <p><strong>বকেয়া পরিমাণ:</strong> ৳${t.arrear_amount}</p>
      </div>
    `;
  }
}

function renderGeoJSONOnMap(geojson, safetyRating) {
  if (!AppState.map) return;
  if (AppState.parcelGeoLayer) {
    AppState.map.removeLayer(AppState.parcelGeoLayer);
  }

  const color = (safetyRating === 'SAFE') ? '#10b981' : '#ef4444';

  AppState.parcelGeoLayer = L.geoJSON(geojson, {
    style: {
      color: color,
      weight: 3,
      opacity: 0.9,
      fillColor: color,
      fillOpacity: 0.35
    },
    onEachFeature: (feature, layer) => {
      layer.bindPopup(`
        <strong>দাগ নং: ${feature.properties.dag_number}</strong><br>
        মৌজা: ${feature.properties.mouza}<br>
        পার্সেল আইডি: ${feature.properties.parcel_id}
      `);
    }
  }).addTo(AppState.map);

  try {
    AppState.map.fitBounds(AppState.parcelGeoLayer.getBounds(), { padding: [20, 20], maxZoom: 16 });
  } catch (e) {
    console.warn("Map bounds error:", e);
  }
}

// Officer Triage Workflow
function initOfficerWorkflow() {
  const filterSelect = document.getElementById('officer-severity-filter');
  if (filterSelect) {
    filterSelect.addEventListener('change', (e) => {
      loadOfficerQueue(e.target.value);
    });
  }

  const decisionForm = document.getElementById('officer-decision-form');
  if (decisionForm) {
    decisionForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      await submitDecision();
    });
  }
}

async function loadOfficerQueue(severity = null) {
  const queueTbody = document.getElementById('officer-queue-tbody');
  const countSpan = document.getElementById('officer-pending-count');
  const lockNotice = document.getElementById('officer-lock-notice');
  const queueTable = document.getElementById('officer-queue-table');

  if (AppState.user.role !== 'OFFICER' && AppState.user.role !== 'ADMINISTRATOR') {
    if (lockNotice) lockNotice.style.display = 'block';
    if (queueTable) queueTable.style.display = 'none';
    return;
  } else {
    if (lockNotice) lockNotice.style.display = 'none';
    if (queueTable) queueTable.style.display = 'table';
  }

  if (queueTbody) {
    queueTbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem;">অফিসার কিউ লোড করা হচ্ছে...</td></tr>`;
  }

  try {
    const res = await LandTechAPI.getOfficerQueue(severity, 30);
    AppState.officerCases = res.queue || [];
    if (countSpan) countSpan.textContent = res.pending_count || 0;

    if (AppState.officerCases.length === 0) {
      queueTbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem; color:var(--success-700)">কোন অনিষ্পন্ন বিরোধ বা উচ্চ ঝুঁকির কেস নেই।</td></tr>`;
      return;
    }

    queueTbody.innerHTML = '';
    AppState.officerCases.forEach(c => {
      const tr = document.createElement('tr');
      const sevClass = c.severity === 'CRITICAL' ? 'badge-danger' : 'badge-warning';

      tr.innerHTML = `
        <td><strong>${c.case_id}</strong></td>
        <td>${c.parcel_id}</td>
        <td>${c.mouza} (দাগ: ${c.dag_number})</td>
        <td><span class="badge ${sevClass}">${c.finding_code}</span></td>
        <td><strong>${c.risk_score}</strong></td>
        <td>${c.review_status}</td>
        <td><button class="btn-secondary inspect-btn" style="padding:4px 8px; font-size:12px;">তদন্ত ও সিদ্ধান্ত</button></td>
      `;

      tr.querySelector('.inspect-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        openOfficerReviewModal(c);
      });

      queueTbody.appendChild(tr);
    });

    // Also load recent audit logs
    loadAuditTrail();
  } catch (err) {
    if (queueTbody) {
      queueTbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:#ef4444; padding:2rem;">ত্রুটি: ${err.message}</td></tr>`;
    }
  }
}

function openOfficerReviewModal(caseItem) {
  AppState.selectedCase = caseItem;
  const modal = document.getElementById('officer-action-modal');
  if (!modal) return;

  document.getElementById('modal-case-id').textContent = caseItem.case_id;
  document.getElementById('modal-parcel-id').textContent = caseItem.parcel_id;
  document.getElementById('modal-explanation').textContent = caseItem.explanation_bn;

  // Render Competing Deeds side-by-side if DS-01
  const diffBox = document.getElementById('modal-deeds-diff');
  let refs = {};
  try {
    refs = typeof caseItem.evidence_references === 'string'
      ? JSON.parse(caseItem.evidence_references)
      : caseItem.evidence_references;
  } catch (e) {}

  if (caseItem.finding_code === 'DS-01' && refs.prior_deed && refs.competing_deed) {
    diffBox.style.display = 'block';
    diffBox.innerHTML = `
      <div class="deed-diff-grid">
        <div class="deed-col deed-first">
          <div class="deed-title">১ম দলিল (পূর্ববর্তী হস্তান্তর)</div>
          <div class="deed-field-row"><span class="lbl">দলিল নং:</span><span class="val">${refs.prior_deed}</span></div>
          <div class="deed-field-row"><span class="lbl">বিক্রেতা:</span><span class="val">${refs.seller_id}</span></div>
          <div class="deed-field-row"><span class="lbl">১ম ক্রেতা:</span><span class="val">${refs.first_buyer_id}</span></div>
          <div class="deed-field-row"><span class="lbl">ই-নামজারি স্থিতি:</span><span class="val" style="color:#ef4444">অনিষ্পন্ন / মুলতবি</span></div>
        </div>
        <div class="deed-col deed-second">
          <div class="deed-title">২য় দলিল (দ্বৈত বিক্রয় দলিল)</div>
          <div class="deed-field-row"><span class="lbl">দলিল নং:</span><span class="val">${refs.competing_deed}</span></div>
          <div class="deed-field-row"><span class="lbl">একই বিক্রেতা:</span><span class="val">${refs.seller_id}</span></div>
          <div class="deed-field-row"><span class="lbl">২য় ক্রেতা:</span><span class="val">${refs.second_buyer_id}</span></div>
          <div class="deed-field-row"><span class="lbl">ঝুঁকি যাচাই:</span><span class="val" style="color:#ef4444">১ম নামজারি ছাড়াই রেজিস্ট্রি</span></div>
        </div>
      </div>
    `;
  } else {
    diffBox.style.display = 'none';
  }

  modal.classList.add('show');
}

function closeOfficerReviewModal() {
  const modal = document.getElementById('officer-action-modal');
  if (modal) modal.classList.remove('show');
}

async function submitDecision() {
  if (!AppState.selectedCase) return;
  const actionSelect = document.getElementById('decision-action-select');
  const reasonInput = document.getElementById('decision-reason-input');

  const action = actionSelect.value;
  const reason = reasonInput.value.trim() || 'নথিপত্র ও ক্যাডাস্ট্রাল উপাত্ত বিশ্লেষণপূর্বক সিদ্ধান্ত গৃহীত।';

  try {
    const res = await LandTechAPI.recordReviewDecision(AppState.selectedCase.case_id, action, reason);
    showToast(`সিদ্ধান্ত সংরক্ষিত! লগ নং: ${res.log_id}`);
    closeOfficerReviewModal();
    loadOfficerQueue();
  } catch (err) {
    alert(`সিদ্ধান্ত জমা দিতে ব্যর্থ: ${err.message}`);
  }
}

async function loadAuditTrail() {
  const auditList = document.getElementById('officer-audit-list');
  if (!auditList) return;

  try {
    const res = await LandTechAPI.getAuditLogs(10);
    if (!res.audit_logs || res.audit_logs.length === 0) {
      auditList.innerHTML = `<p style="color:var(--slate-400); font-size:0.8rem;">কোন অডিট লগ নেই</p>`;
      return;
    }

    auditList.innerHTML = res.audit_logs.map(l => `
      <div style="font-size:0.8rem; padding: 0.4rem 0; border-bottom: 1px dashed var(--slate-200);">
        <strong>${l.log_id}</strong> [${l.action}]
        <div style="color:var(--slate-600)">কেস: ${l.case_id} (${l.parcel_id}) | কর্মকর্তা: ${l.reviewer_id}</div>
        <div style="color:var(--slate-500); font-size:0.75rem;">${new Date(l.timestamp).toLocaleString('bn-BD')}</div>
      </div>
    `).join('');
  } catch (e) {
    console.warn("Audit logs error:", e);
  }
}

// Smart e-Mutation Simulator (P4)
function initMutationSimulator() {
  const preCheckBtn = document.getElementById('run-precheck-btn');
  if (!preCheckBtn) return;

  preCheckBtn.addEventListener('click', async () => {
    const parcelId = document.getElementById('mut-parcel-id')?.value.trim() || 'BD-PAR-000101';
    const deedId = document.getElementById('mut-deed-id')?.value.trim() || 'SAVAR-20261018-000101';
    const applicantId = document.getElementById('mut-applicant-id')?.value.trim() || 'OWN-000305';

    const outBox = document.getElementById('mutation-precheck-output');
    outBox.innerHTML = 'প্রাক-যাচাই অ্যালগরিদম পরীক্ষা করা হচ্ছে...';

    try {
      const res = await LandTechAPI.preCheckMutation(parcelId, deedId, applicantId);
      const isApproved = res.can_proceed;

      outBox.innerHTML = `
        <div style="padding: 1rem; border-radius: 8px; background: ${isApproved ? 'var(--success-50)' : 'var(--danger-50)'}; border: 1px solid ${isApproved ? 'var(--success-500)' : 'var(--danger-500)'}">
          <h4 style="color: ${isApproved ? 'var(--success-700)' : 'var(--danger-700)'}">
            ${isApproved ? '✓ প্রাক-যাচাই উত্তীর্ণ: নামজারি আবেদন প্রক্রিয়াকরণ সম্ভব' : '✕ প্রাক-যাচাই ব্যর্থ: আবেদন সরাসরি গ্রহণ অযোগ্য'}
          </h4>
          <p style="margin-top: 0.5rem; font-size: 0.9rem;">${res.precheck_summary_bn}</p>
          ${res.rejection_reasons.length > 0 ? `
            <ul style="margin-top: 0.5rem; margin-left: 1.5rem; font-size: 0.85rem; color: var(--danger-700);">
              ${res.rejection_reasons.map(r => `<li>${r}</li>`).join('')}
            </ul>
          ` : ''}
        </div>
      `;
    } catch (err) {
      outBox.innerHTML = `<span style="color:#ef4444">ত্রুটি: ${err.message}</span>`;
    }
  });
}

// Document Integrity & OCR (P1 & P2)
function initDocumentVerifier() {
  const verifyBtn = document.getElementById('doc-verify-btn');
  const fileInput = document.getElementById('doc-file-input');
  const loadSampleBtn = document.getElementById('load-sample-doc-btn');
  const loadTamperBtn = document.getElementById('load-tampered-doc-btn');

  if (loadSampleBtn) {
    loadSampleBtn.addEventListener('click', async () => {
      simulateDocVerification(false);
    });
  }

  if (loadTamperBtn) {
    loadTamperBtn.addEventListener('click', async () => {
      simulateDocVerification(true);
    });
  }

  if (verifyBtn && fileInput) {
    verifyBtn.addEventListener('click', async () => {
      if (!fileInput.files || fileInput.files.length === 0) {
        alert('অনুগ্রহ করে একটি দলিলের স্ক্যান কপি বা ইমেজ নির্বাচন করুন।');
        return;
      }
      runFileVerification(fileInput.files[0]);
    });
  }

  // OCR Upload Button
  const ocrBtn = document.getElementById('run-ocr-btn');
  const ocrFileInput = document.getElementById('ocr-file-input');
  if (ocrBtn && ocrFileInput) {
    ocrBtn.addEventListener('click', async () => {
      if (!ocrFileInput.files || ocrFileInput.files.length === 0) {
        alert('অনুগ্রহ করে ওল্ড পরচা বা দলিলের ছবি আপলোড করুন।');
        return;
      }
      runOCRUpload(ocrFileInput.files[0]);
    });
  }
}

async function simulateDocVerification(isTampered) {
  const resultBox = document.getElementById('doc-verification-result');
  resultBox.innerHTML = 'ক্রিপ্টোগ্রাফিক হ্যাশ গণনা ও ডাটাবেস যাচাই করা হচ্ছে...';

  // Create a synthetic blob representing authentic vs tampered deed
  const textContent = isTampered
    ? "DESHMRITTIKA_TAMPERED_DEED_BYTE_CORRUPTION_SIMULATION"
    : "DESHMRITTIKA_AUTHENTIC_DOCUMENT_HASH_MATCH_DOC_000001";

  // If authentic, let's test using actual sample file if supported
  try {
    const fakeBlob = new Blob([textContent], { type: 'text/plain' });
    const res = await LandTechAPI.verifyDocumentIntegrity(fakeBlob, isTampered ? 'tampered.png' : 'DOC-000001.png');

    displayIntegrityResult(res, isTampered);
  } catch (e) {
    resultBox.innerHTML = `<span style="color:#ef4444">যাচাই ব্যর্থ: ${e.message}</span>`;
  }
}

async function runFileVerification(file) {
  const resultBox = document.getElementById('doc-verification-result');
  resultBox.innerHTML = 'SHA-256 ক্রিপ্টোগ্রাফিক হ্যাশ যাচাই চলছে...';

  try {
    const res = await LandTechAPI.verifyDocumentIntegrity(file, file.name);
    displayIntegrityResult(res, !res.is_authentic);
  } catch (e) {
    resultBox.innerHTML = `<span style="color:#ef4444">যাচাইয়ে ত্রুটি: ${e.message}</span>`;
  }
}

function displayIntegrityResult(res, isTampered) {
  const resultBox = document.getElementById('doc-verification-result');
  if (res.is_authentic) {
    resultBox.innerHTML = `
      <div style="background:var(--success-50); border: 1px solid var(--success-500); padding: 1.25rem; border-radius:8px;">
        <h4 style="color:var(--success-700)">✓ দলিলটি সম্পূর্ণ প্রামাণ্য ও অবিকৃত (Authentic)</h4>
        <p style="font-size:0.85rem; margin-top:0.35rem;">ম্যাচিং দলিল আইডি: <strong>${res.matched_document_id}</strong> | পার্সেল: ${res.parcel_id}</p>
        <p style="font-size:0.75rem; color:var(--slate-600)">উৎস লেবেল: ${res.provenance_label}</p>
      </div>
    `;
  } else {
    resultBox.innerHTML = `
      <div style="background:var(--danger-50); border: 1px solid var(--danger-500); padding: 1.25rem; border-radius:8px;">
        <h4 style="color:var(--danger-700)">✕ জালিয়াতি / বিকৃতি শনাক্ত হয়েছে (Tamper Detected)</h4>
        <p style="font-size:0.85rem; margin-top:0.35rem;">দলিলটির হ্যাশ সরকারি ডাটাবেসের মূল রেজিস্ট্রি রেকর্ডের সাথে মিলছে না।</p>
        <p style="font-size:0.75rem; color:var(--danger-600)">স্ট্যাটাস: ${res.status_label}</p>
      </div>
    `;
  }
}

async function runOCRUpload(file) {
  const ocrOutput = document.getElementById('ocr-output-text');
  const ocrStatus = document.getElementById('ocr-status-badge');
  ocrOutput.textContent = 'টেসেরাক্ট (Tesseract) অপটিক্যাল ক্যারেক্টার রিকগনিশন চলছে...';

  try {
    const res = await LandTechAPI.uploadDocumentOCR(file, file.name);
    if (res.success) {
      ocrStatus.className = 'badge badge-warning';
      ocrStatus.textContent = res.ocr_status;
      ocrOutput.textContent = res.extracted_text || '(কোন স্পষ্ট টেক্সট পড়া যায়নি)';
      showToast(`OCR সম্পন্ন: ${res.char_count} টি অক্ষর নিষ্কাশিত`);
    } else {
      ocrStatus.className = 'badge badge-danger';
      ocrStatus.textContent = res.ocr_status;
      ocrOutput.textContent = res.error || res.note;
    }
  } catch (e) {
    ocrOutput.textContent = `OCR ত্রুটি: ${e.message}`;
  }
}
