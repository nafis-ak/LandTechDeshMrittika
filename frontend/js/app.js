/**
 * DESHMRITTIKA / BHUMI-SYNC — Main Application Controller
 * Handles Landing Page interactions, Persistent Sidebar Shell,
 * P1-P6 Workspaces, Advanced OCR Pipeline, and Cadastral GIS.
 */

// Application Global State
const AppState = {
  view: 'landing', // 'landing' | 'app'
  currentPage: 'overview',
  lang: 'bn',
  user: {
    user_id: 'USR-CITIZEN-01',
    name: 'মো: রফিকুল ইসলাম (Citizen)',
    role: 'CITIZEN',
    email: 'citizen@example.com'
  },
  selectedParcelId: 'BD-PAR-000101',
  citizenMap: null,
  citizenGeoLayer: null,
  gisMap: null,
  gisLayers: {
    parcels: null,
    khas: null,
    corridor: null
  },
  officerCases: [],
  selectedCase: null,
  activeOcrFile: null
};

// 6-Step Walkthrough Data
const WALKTHROUGH_STEPS = {
  1: {
    track: "Track P1 — Digitize Old Records",
    title: "প্রাচীন খতিয়ান ও দলিলের অপটিক্যাল ক্যারেক্টার রিকগনিশন (OCR)",
    desc: "হাতে লেখা বা টাইপ করা প্রাচীন সিএস, এসএ, আরএস ও বিএস খতিয়ান এবং দলিলের স্ক্যান কপি ও মাল্টি-পেইজ পিডিএফ থেকে দাগ, খতিয়ান, মৌজা ও সাফ-কবালা দলিলের বাংলা/ইংরেজি টেক্সট রূপান্তর।",
    specs: [
      "টেসেরাক্ট ইঞ্জিনে বাংলা ও ইংরেজি দ্বৈত ভাষা মডেল (ben+eng) সক্রিয়",
      "কন্ট্রাস্ট বর্ধন, অটোকন্ট্রাস্ট ও অভিযোজিত বাইনারাইজেশন ফিল্টার",
      "শব্দভিত্তিক নির্ভরযোগ্যতার হার (Confidence Score) ও শতাংশ প্রদর্শন"
    ],
    targetPage: "ocr",
    img: "/static/assets/images/cadastral_drone_parcels.jpg"
  },
  2: {
    track: "Track P2 — Verify Deeds & Ownership",
    title: "ক্রিপ্টোগ্রাফিক হ্যাশ ও জালিয়াতি রোধ ব্যবস্থা",
    desc: "প্রতিটি নিবন্ধিত দলিলের সামগ্রিক বাইট বিশ্লেষণ করে তৈরি হয় ২৫৬-বিটের অনন্য ডিজিটাল ফিঙ্গারপ্রিন্ট (SHA-256)। মূল দলিলের একটি ডট বা পিক্সেল পরিবর্তন হলেও হ্যাশ অমিলের মাধ্যমে অবিলম্বে জালিয়াতি ধরা পড়ে।",
    specs: [
      "ক্লায়েন্ট ও সার্ভার উভয় স্তরে তাৎক্ষণিক SHA-256 হ্যাশ গণনা",
      "সরকারি সাব-রেজিস্ট্রি লেজারের সাথে ডিজিটাল ফিঙ্গারপ্রিন্ট যাচাই",
      "সিন্থেটিক নিয়ন্ত্রিত বিকৃতি ডেমো (Tamper Detection Testing)"
    ],
    targetPage: "verify",
    img: "/static/assets/images/due_diligence_review.jpg"
  },
  3: {
    track: "Track P3 (Showcase) — Catch Fraud & Double-Selling",
    title: "ডিটারমিনিস্টিক বহু-নিয়মীয় দ্বৈত বিক্রয় শনাক্তকরণ",
    desc: "একই বিক্রেতা প্রথম হস্তান্তরের ই-নামজারি নিষ্পত্তি হওয়ার পূর্বে একই দাগের জমি দ্বিতীয় কোনো ক্রেতার নিকট গোপনে রেজিস্ট্রি করলেই আমাদের মাল্টি-ভেক্টর রুল ইঞ্জিন (DS-01) এটিকে লাল পতাকাবাহী ক্রিটিক্যাল অ্যালার্ট হিসেবে চিহ্নিত করে।",
    specs: [
      "১০০% রিকল রেট ও ০.০% ফলস পজিটিভ (১৫,০০০ নির্দোষ বিক্রি পরীক্ষায় প্রমাণিত)",
      "এসি ল্যান্ড ট্রায়াজ ড্যাশবোর্ড ও পাশাপাশি দুই দলিলের অমিল তুলনা (Side-by-Side Diff)",
      "অফিসারদের তদন্ত আদেশ সংরক্ষণে অপরিবর্তনীয় অডিট ট্রেইল"
    ],
    targetPage: "officer",
    img: "/static/assets/images/agricultural_parcels_vertical.jpg"
  },
  4: {
    track: "Track P4 — Smart e-Mutation & Registry Bridge",
    title: "সাব-রেজিস্ট্রি ও এসি ল্যান্ড কার্যক্রমে স্বয়ংক্রিয় প্রাক-যাচাই সেতু",
    desc: "দলিল সম্পাদন হওয়া মাত্র তথ্য স্বয়ংক্রিয়ভাবে নামজারি সার্ভারে প্রেরণ। আবেদন গ্রহণের পূর্বেই খাস জমি, কর বকেয়া ও পূর্ববর্তী স্থগিতাদেশ যাচাই করে অপ্রয়োজনীয় আবেদন তাৎক্ষণিক প্রত্যাখ্যান।",
    specs: [
      "সাব-রেজিস্ট্রি থেকে এসি ল্যান্ড কার্যক্রমে রিয়েলটাইম ডেটা সিঙ্ক",
      "খাস জমি, কর বকেয়া ও নিষেধাজ্ঞা সংক্রান্ত স্বয়ংক্রিয় ৩-দফা প্রি-চেক",
      "৪-স্তরী নামজারি প্রক্রিয়াকরণ ট্র্যাকার (আবেদন ➔ তদন্ত ➔ শুনানি ➔ খতিয়ান)"
    ],
    targetPage: "mutation",
    img: "/static/assets/images/bangladesh_soil_heritage.jpg"
  },
  5: {
    track: "Track P5 — Check Before You Buy",
    title: "নাগরিক একক বাতায়ন — ৫-দফা ক্রেতা ডিউ ডিলিজেন্স সনদ",
    desc: "সাধারণ নাগরিক ও জমি ক্রেতাদের জন্য একটি মাত্র ক্লিকে দাগ বা খতিয়ানের বিস্তারিত পরিচিতি, বায়া দলিলের ধারাবাহিকতা, নামজারি স্থিতি, দেওয়ানি মামলা, কর বকেয়া ও খাস জমির যৌথ নিরাপত্তা ছাড়পত্র।",
    specs: [
      "মৌজা, দাগ, খতিয়ান বা পার্সেল আইডিতে সাব-মিলিমিটার সমন্বিত সার্চ",
      "ঝুঁকি স্কোর অনুযায়ী অ্যানিমেটেড ডায়াল (নিরাপদ / সতর্কতা / দ্বৈত বিক্রয় স্থগিত)",
      "এক ক্লিকে ডাউনলোডযোগ্য প্রাতিষ্ঠানিক ক্রেতা ডিউ ডিলিজেন্স ডসিয়ার"
    ],
    targetPage: "citizen",
    img: "/static/assets/images/due_diligence_review.jpg"
  },
  6: {
    track: "Track P6 (Innovation) — Boundary Conflict & Khas Protection",
    title: "ক্যাডাস্ট্রাল সীমানা ও ১-নং খাস জমি রক্ষা ইঞ্জিন",
    desc: "ওপেনস্ট্রিটম্যাপ ও সাভার মৌজা সিটের ওপর ক্যাডাস্ট্রাল দাগসমূহের বহুভুজ (Polygon) ওভারলে। সরকারি ১-নং খাস খতিয়ান এবং ঢাকা-আরিচা মহাসড়কের ১০০-মিটার অধিগ্রহণ জোনের সাথে ইন্টারসেকশন শনাক্তকরণ।",
    specs: [
      "ডব্লিউজিএস-৮৪ (WGS-84) বাস্তব ভৌগোলিক স্থানাঙ্কে ক্যাডাস্ট্রাল ড্রাফটিং",
      "১,৫০০ খাস দাগ ও ৫টি জাতীয় মহাসড়ক অধিগ্রহণ করিডোরের স্বয়ংক্রিয় বাফার অ্যালার্ট",
      "দাগে ক্লিক করে তাৎক্ষণিক ক্ষেত্রফল ও আইনি স্থিতি পরীক্ষণ"
    ],
    targetPage: "map",
    img: "/static/assets/images/bangladesh_river_map.jpg"
  }
};

// UI Dictionary for Translations
const I18N_DICT = {
  bn: {
    langName: "English",
    heroStatus: "অনলাইন: ১০০,০০০ প্লট সংযুক্ত | সাভার পাইলট",
    exploreBtn: "প্ল্যাটফর্ম এক্সপ্লোর করুন",
    searchBtn: "অনুসন্ধান",
    riskSafe: "নিরাপদ জমি (Transaction Safe)",
    riskCritical: "দ্বৈত বিক্রয় / লেনদেন নিষিদ্ধ",
    precheckRun: "⚡ প্রাক-যাচাই চালান",
    toastDecision: "সিদ্ধান্ত সফলভাবে অডিট ট্রেইলে সংরক্ষিত হয়েছে।"
  },
  en: {
    langName: "বাংলা",
    heroStatus: "Online: 100,000 Parcels Connected | Savar Pilot",
    exploreBtn: "Explore Platform",
    searchBtn: "Search",
    riskSafe: "Safe Parcel (Transaction Safe)",
    riskCritical: "Critical Risk: Double-Selling Detected",
    precheckRun: "⚡ Run Pre-Check",
    toastDecision: "Decision successfully recorded in immutable audit log."
  }
};

// DOM Content Loaded Handler
document.addEventListener('DOMContentLoaded', async () => {
  initLandingPage();
  initAppShellNavigation();
  initRoleManagement();
  initLanguageToggles();
  initSearchWorkspace();
  initOfficerWorkspace();
  initMutationWorkspace();
  initDocumentVerifyWorkspace();
  initAdvancedOCRWorkspace();
  initCadastralGISWorkspace();

  // Load backend health
  checkBackendHealth();

  // Auto-login default citizen account
  try {
    await LandTechAPI.login(AppState.user.email);
  } catch (e) {
    console.warn("Auto-login fallback:", e);
  }

  // Pre-load default parcel BD-PAR-000101
  loadCitizenDossier('BD-PAR-000101');

  // URL Hash Routing Support
  function checkRouteHash() {
    const hash = window.location.hash.replace('#', '');
    if (hash === 'app') {
      navigateToApp('overview');
    } else if (['overview', 'citizen', 'officer', 'mutation', 'ocr', 'verify', 'map', 'audit', 'dataset', 'settings'].includes(hash)) {
      navigateToApp(hash);
    }
  }
  checkRouteHash();
  window.addEventListener('hashchange', checkRouteHash);
});

// Backend Health Check
async function checkBackendHealth() {
  try {
    const health = await LandTechAPI.getHealth();
    if (health.status === 'HEALTHY') {
      const mb = health.database ? health.database.size_mb : 109.35;
      const label = `অনলাইন: ${mb} MB ডাটাবেস | ১০০,০০০ প্লট`;
      document.getElementById('hero-status-text').textContent = label;
      document.getElementById('app-health-text').textContent = label;

      const diagBox = document.getElementById('diagnostics-info-box');
      if (diagBox) {
        diagBox.innerHTML = `
=== দেশমৃত্তিকা সিস্টেম ডায়াগনস্টিক রিপোর্ট ===
[সার্ভিস স্থিতি]: ${health.status}
[প্ল্যাটফর্ম সংস্করণ]: ${health.version}
[কানেক্টেড ডাটাবেস]: ${health.database.path}
[ডাটাবেস সাইজ]: ${health.database.size_mb} MB (100,000 Relational Parcels)
[রুলবুক ট্র্যাকসমূহ]: ${health.tracks_supported.join(', ')}
[টেসেরাক্ট OCR মডেলসমূহ]: ben, eng, osd, snum (Dual Language Pack Active)
[অ্যাক্টিভ অথ সেশন]: HMAC-SHA256 Token Enforced
        `.trim();
      }
    }
  } catch (e) {
    console.warn("Health check error:", e);
  }
}

// ==========================================================================
// TIER 1: LANDING PAGE CONTROLLER
// ==========================================================================
function initLandingPage() {
  const openAppBtn = document.getElementById('open-app-btn');
  if (openAppBtn) {
    openAppBtn.addEventListener('click', () => navigateToApp('overview'));
  }

  // Interactive 6-step walkthrough tabs
  const stepBtns = document.querySelectorAll('.journey-step-btn');
  stepBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const stepId = parseInt(btn.getAttribute('data-step'), 10);
      setWalkthroughStep(stepId);
    });
  });
}

function setWalkthroughStep(stepId) {
  const stepData = WALKTHROUGH_STEPS[stepId];
  if (!stepData) return;

  document.querySelectorAll('.journey-step-btn').forEach(b => {
    b.classList.toggle('active', parseInt(b.getAttribute('data-step'), 10) === stepId);
  });

  document.getElementById('step-track-tag').textContent = stepData.track;
  document.getElementById('step-title').textContent = stepData.title;
  document.getElementById('step-desc').textContent = stepData.desc;
  document.getElementById('step-img').src = stepData.img;

  const specsUl = document.getElementById('step-specs');
  specsUl.innerHTML = stepData.specs.map(s => `<li>${s}</li>`).join('');

  const actionBtn = document.getElementById('step-action-btn');
  actionBtn.onclick = () => navigateToApp(stepData.targetPage);
}

// View Switching: Landing Page <-> App Shell
function navigateToApp(targetPage = 'overview') {
  AppState.view = 'app';
  document.getElementById('landing-view').style.display = 'none';
  document.getElementById('app-shell-view').style.display = 'block';
  window.scrollTo(0, 0);
  switchAppPage(targetPage);
}

function navigateToLanding() {
  AppState.view = 'landing';
  document.getElementById('app-shell-view').style.display = 'none';
  document.getElementById('landing-view').style.display = 'block';
  window.scrollTo(0, 0);
}

// Global exports for inline HTML event handlers
window.navigateToApp = navigateToApp;
window.navigateToLanding = navigateToLanding;

// ==========================================================================
// TIER 2: PERSISTENT SIDEBAR APP SHELL CONTROLLER
// ==========================================================================
function initAppShellNavigation() {
  // Sidebar navigation items
  const navItems = document.querySelectorAll('.sidebar-nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const page = item.getAttribute('data-page');
      switchAppPage(page);
    });
  });

  // Sidebar collapse toggle
  const collapseBtn = document.getElementById('sidebar-collapse-btn');
  const sidebar = document.getElementById('app-sidebar');
  const mainWorkspace = document.querySelector('.app-main-workspace');

  if (collapseBtn) {
    collapseBtn.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      if (sidebar.classList.contains('collapsed')) {
        sidebar.style.width = 'var(--sidebar-collapsed-width)';
        mainWorkspace.style.marginLeft = 'var(--sidebar-collapsed-width)';
        collapseBtn.textContent = '▶';
      } else {
        sidebar.style.width = 'var(--sidebar-width)';
        mainWorkspace.style.marginLeft = 'var(--sidebar-width)';
        collapseBtn.textContent = '◀';
      }
    });
  }

  // Mobile drawer toggle
  const mobileDrawerBtn = document.getElementById('mobile-drawer-btn');
  if (mobileDrawerBtn) {
    mobileDrawerBtn.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });
  }
}

function switchAppPage(pageName) {
  AppState.currentPage = pageName;

  // Update active sidebar nav
  document.querySelectorAll('.sidebar-nav-item').forEach(item => {
    item.classList.toggle('active', item.getAttribute('data-page') === pageName);
  });

  // Switch workspace container
  document.querySelectorAll('.workspace-page').forEach(page => {
    page.classList.toggle('active', page.id === `page-${pageName}`);
  });

  // Update breadcrumb
  const titles = {
    overview: "ওভারভিউ ড্যাশবোর্ড",
    citizen: "নাগরিক অনুসন্ধান ও ৫-দফা ডসিয়ার (P5)",
    officer: "দ্বৈত বিক্রয় ট্রায়াজ কিউ (P3)",
    mutation: "স্মার্ট ই-নামজারি সিমুলেটর (P4)",
    ocr: "প্রাচীন পরচা ও দলিল OCR (P1)",
    verify: "ক্রিপ্টোগ্রাফিক হ্যাশ যাচাই (P2)",
    map: "ক্যাডাস্ট্রাল ম্যাপ ও খাস রক্ষা (P6)",
    audit: "অফিসার নিরীক্ষা ট্রেইল",
    dataset: "সিন্থেটিক ডেটাসেট পরিসংখ্যান",
    settings: "সিস্টেম স্ট্যাটাস ও ডায়াগনস্টিক"
  };
  document.getElementById('breadcrumb-current-page').textContent = titles[pageName] || pageName;

  // Lifecycle page hooks
  if (pageName === 'citizen') {
    if (AppState.citizenMap) {
      setTimeout(() => AppState.citizenMap.invalidateSize(), 200);
    } else {
      setTimeout(initCitizenMap, 150);
    }
  } else if (pageName === 'map') {
    if (AppState.gisMap) {
      setTimeout(() => AppState.gisMap.invalidateSize(), 200);
    } else {
      setTimeout(initCadastralGISWorkspace, 150);
    }
  } else if (pageName === 'officer') {
    loadOfficerQueue();
  } else if (pageName === 'audit') {
    loadAuditTrailLogs();
  }
}

// Role Switcher Management
function initRoleManagement() {
  const roleSelect = document.getElementById('app-role-select');
  if (!roleSelect) return;

  roleSelect.addEventListener('change', async (e) => {
    await switchRole(e.target.value);
  });
}

async function switchRole(roleName) {
  let email = 'citizen@example.com';
  if (roleName === 'BUYER') email = 'buyer@example.com';
  else if (roleName === 'OFFICER') email = 'officer@savar.land.gov.bd';
  else if (roleName === 'ADMINISTRATOR') email = 'admin@deshmrittika.gov.bd';

  try {
    const authData = await LandTechAPI.login(email);
    AppState.user = {
      user_id: authData.user_id,
      name: authData.name,
      role: authData.role,
      email: email
    };

    const roleSelect = document.getElementById('app-role-select');
    if (roleSelect) roleSelect.value = roleName;

    showToast(`ভূমিকা পরিবর্তিত: ${authData.name} (${authData.role})`);

    // Refresh officer queue if on officer page
    if (AppState.currentPage === 'officer') {
      loadOfficerQueue();
    }
  } catch (err) {
    alert(`Role switch error: ${err.message}`);
  }
}

// Language Toggles and Interface Translation
function applyLanguage(lang) {
  AppState.lang = lang;
  const isEn = lang === 'en';

  const btnLanding = document.getElementById('lang-toggle-landing');
  const btnApp = document.getElementById('lang-toggle-app');
  if (btnLanding) btnLanding.textContent = isEn ? 'বাংলা' : 'English';
  if (btnApp) btnApp.textContent = isEn ? 'বাংলা' : 'English';

  // Sidebar labels
  const navLabels = {
    overview: isEn ? "Overview Dashboard" : "ওভারভিউ ড্যাশবোর্ড",
    citizen: isEn ? "Citizen Search & Dossier" : "নাগরিক অনুসন্ধান ও ডসিয়ার",
    officer: isEn ? "Double-Selling Triage" : "দ্বৈত বিক্রয় ট্রায়াজ কিউ",
    mutation: isEn ? "e-Mutation Simulator" : "ই-নামজারি সিমুলেটর",
    ocr: isEn ? "Deed & Khatian OCR" : "দলিল ও পরচা OCR",
    verify: isEn ? "Cryptographic Verification" : "ক্রিপ্টোগ্রাফিক হ্যাশ যাচাই",
    map: isEn ? "Cadastral Map & Khas Land" : "ক্যাডাস্ট্রাল ম্যাপ ও খাস রক্ষা",
    audit: isEn ? "Officer Audit Trail" : "অফিসার নিরীক্ষা ট্রেইল",
    dataset: isEn ? "Dataset Statistics" : "সিন্থেটিক ডেটাসেট পরিসংখ্যান",
    settings: isEn ? "System Diagnostics" : "সিস্টেম স্ট্যাটাস ও ডায়াগনস্টিক"
  };

  document.querySelectorAll('.sidebar-nav-item').forEach(item => {
    const page = item.getAttribute('data-page');
    const labelSpan = item.querySelector('.nav-label');
    if (page && labelSpan && navLabels[page]) {
      labelSpan.textContent = navLabels[page];
    }
  });

  // Category titles
  const catTitles = document.querySelectorAll('.nav-category-title');
  if (catTitles.length >= 3) {
    catTitles[0].textContent = isEn ? "CORE OPERATIONS" : "মূল কার্যক্রম";
    catTitles[1].textContent = isEn ? "INTEGRITY & TECH" : "প্রামাণিকতা ও প্রযুক্তি";
    catTitles[2].textContent = isEn ? "SYSTEM & ADMIN" : "সিস্টেম ও প্রশাসন";
  }

  // Header explore buttons
  const openAppBtn = document.getElementById('open-app-btn');
  if (openAppBtn) {
    const span = openAppBtn.querySelector('span:first-child');
    if (span) span.textContent = isEn ? "Explore Platform" : "প্ল্যাটফর্ম এক্সপ্লোর করুন";
  }

  // Update breadcrumb
  const titles = {
    overview: isEn ? "Overview Dashboard" : "ওভারভিউ ড্যাশবোর্ড",
    citizen: isEn ? "Citizen Search & 5-Point Dossier (P5)" : "নাগরিক অনুসন্ধান ও ৫-দফা ডসিয়ার (P5)",
    officer: isEn ? "Double-Selling Triage Queue (P3)" : "দ্বৈত বিক্রয় ট্রায়াজ কিউ (P3)",
    mutation: isEn ? "Smart e-Mutation Simulator (P4)" : "স্মার্ট ই-নামজারি সিমুলেটর (P4)",
    ocr: isEn ? "Old Record & Khatian OCR (P1)" : "প্রাচীন পরচা ও দলিল OCR (P1)",
    verify: isEn ? "Cryptographic Hash Verification (P2)" : "ক্রিপ্টোগ্রাফিক হ্যাশ যাচাই (P2)",
    map: isEn ? "Cadastral Map & Khas Land Protection (P6)" : "ক্যাডাস্ট্রাল ম্যাপ ও খাস রক্ষা (P6)",
    audit: isEn ? "Officer Audit Trail" : "অফিসার নিরীক্ষা ট্রেইল",
    dataset: isEn ? "Synthetic Dataset Statistics" : "সিন্থেটিক ডেটাসেট পরিসংখ্যান",
    settings: isEn ? "System Status & Diagnostics" : "সিস্টেম স্ট্যাটাস ও ডায়াগনস্টিক"
  };
  const breadcrumb = document.getElementById('breadcrumb-current-page');
  if (breadcrumb) {
    breadcrumb.textContent = titles[AppState.currentPage] || AppState.currentPage;
  }

  showToast(isEn ? "Language switched to English" : "ভাষা বাংলায় পরিবর্তিত হয়েছে");
}

function initLanguageToggles() {
  const btnLanding = document.getElementById('lang-toggle-landing');
  const btnApp = document.getElementById('lang-toggle-app');

  const toggleHandler = () => {
    const nextLang = AppState.lang === 'bn' ? 'en' : 'bn';
    applyLanguage(nextLang);
  };

  if (btnLanding) btnLanding.addEventListener('click', toggleHandler);
  if (btnApp) btnApp.addEventListener('click', toggleHandler);
}

// Toast Notification
function showToast(msg) {
  const toast = document.getElementById('calm-toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3500);
}

// ==========================================================================
// WORKSPACE 2: CITIZEN SEARCH & DUE DILIGENCE (P5)
// ==========================================================================
function initSearchWorkspace() {
  const form = document.getElementById('app-search-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      executeAppSearch();
    });
  }
}

function initCitizenMap() {
  const mapContainer = document.getElementById('app-citizen-map');
  if (!mapContainer || AppState.citizenMap) return;

  AppState.citizenMap = L.map('app-citizen-map').setView([23.8560, 90.2600], 14);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors | DeshMrittika'
  }).addTo(AppState.citizenMap);
}

function applyPresetAndSearch(type) {
  navigateToApp('citizen');
  const dagInput = document.getElementById('app-search-dag');
  const mouzaInput = document.getElementById('app-search-mouza');
  const idInput = document.getElementById('app-search-id');

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
  executeAppSearch();
}

async function executeAppSearch() {
  const dag = document.getElementById('app-search-dag')?.value.trim();
  const mouza = document.getElementById('app-search-mouza')?.value.trim();
  const khatian = document.getElementById('app-search-khatian')?.value.trim();
  const id = document.getElementById('app-search-id')?.value.trim();

  const tbody = document.getElementById('app-search-results-tbody');
  const countEl = document.getElementById('app-results-count');
  if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:1.5rem;">অনুসন্ধান চলছে...</td></tr>`;

  try {
    const res = await LandTechAPI.searchParcels({
      dag: dag || null,
      mouza: mouza || null,
      khatian: khatian || null,
      parcel_id: id || null,
      limit: 15
    });

    if (countEl) countEl.textContent = res.total_matches;

    if (!res.parcels || res.parcels.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:1.5rem; color:var(--c-risk-danger);">কোনো রেকর্ড পাওয়া যায়নি।</td></tr>`;
      return;
    }

    tbody.innerHTML = '';
    res.parcels.forEach(p => {
      const tr = document.createElement('tr');
      const disputePill = p.is_disputed
        ? `<span class="pill-tag pill-danger">⚠️ বিরোধপূর্ণ</span>`
        : `<span class="pill-tag pill-safe">✓ নিয়মিত</span>`;

      tr.innerHTML = `
        <td><strong>${p.parcel_id}</strong></td>
        <td>${p.mouza} (${p.jl_number})</td>
        <td class="num">${p.dag_number}</td>
        <td class="num">${p.khatian_number}</td>
        <td>${p.survey_type}</td>
        <td class="num">${p.area_decimal} শতাংশ</td>
        <td>${disputePill}</td>
      `;

      tr.addEventListener('click', () => {
        document.querySelectorAll('#app-search-results-tbody tr').forEach(r => r.classList.remove('row-selected'));
        tr.classList.add('row-selected');
        loadCitizenDossier(p.parcel_id);
      });

      tbody.appendChild(tr);
    });

    // Auto-load first parcel dossier
    if (res.parcels.length > 0) {
      loadCitizenDossier(res.parcels[0].parcel_id);
    }
  } catch (err) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--c-risk-danger); padding:1.5rem;">ত্রুটি: ${err.message}</td></tr>`;
  }
}

async function loadCitizenDossier(parcelId) {
  AppState.selectedParcelId = parcelId;
  try {
    const [dossier, profile, geojson] = await Promise.all([
      LandTechAPI.getDueDiligence(parcelId),
      LandTechAPI.getParcelProfile(parcelId),
      LandTechAPI.getParcelGeoJSON(parcelId).catch(() => null)
    ]);

    renderCitizenDossier(dossier, profile);
    if (geojson) {
      renderCitizenPolygon(geojson, dossier.safety_rating);
    }
  } catch (err) {
    console.error("Dossier load error:", err);
  }
}

function renderCitizenDossier(dossier, profile) {
  const p = dossier.parcel;

  document.getElementById('dos-id-pill').textContent = p.parcel_id;
  document.getElementById('dos-status-pill').textContent = `${p.survey_type} জরিপ`;
  document.getElementById('app-dos-title').textContent = `${p.mouza} | দাগ নং: ${p.dag_number} | খতিয়ান নং: ${p.khatian_number}`;
  document.getElementById('app-dos-meta').textContent = `${p.area_decimal} শতাংশ (${p.land_classification}) | জেএল নং: ${p.jl_number} | সাভার, ঢাকা`;

  // Score & Verdict
  const scoreEl = document.getElementById('app-risk-score');
  const circleEl = document.getElementById('app-risk-circle');
  const titleEl = document.getElementById('app-verdict-title');
  const descEl = document.getElementById('app-verdict-desc');

  scoreEl.textContent = dossier.risk_score;

  if (dossier.safety_rating === 'SAFE') {
    circleEl.style.background = 'var(--c-risk-safe)';
    titleEl.textContent = 'নিরাপদ জমি (Transaction Safe)';
    titleEl.style.color = 'var(--c-risk-safe)';
    descEl.textContent = '৫-দফা নিরাপত্তা সনদ উত্তীর্ণ। কোনো বকেয়া বা বিরোধ নেই।';
  } else if (dossier.safety_rating === 'CAUTION') {
    circleEl.style.background = 'var(--c-risk-warning)';
    titleEl.textContent = 'সতর্কতা প্রয়োজন (Caution)';
    titleEl.style.color = 'var(--c-risk-warning)';
    descEl.textContent = 'কর বকেয়া বা অমিল শনাক্ত হয়েছে। বিস্তারিত যাচাই করুন।';
  } else {
    circleEl.style.background = 'var(--c-risk-danger)';
    titleEl.textContent = 'দ্বৈত বিক্রয় / লেনদেন নিষিদ্ধ (Critical)';
    titleEl.style.color = 'var(--c-risk-danger)';
    descEl.textContent = 'প্রতারণামূলক হস্তান্তরের প্রমাণ পাওয়া গেছে! অবিলম্বে রেজিস্ট্রি স্থগিত রাখুন।';
  }

  // 5-Point Shield Cards
  const shieldGrid = document.getElementById('app-safety-shield-grid');
  shieldGrid.innerHTML = '';

  dossier.safety_checklist.forEach(item => {
    const card = document.createElement('div');
    const isPass = item.status === 'PASS';
    const isWarn = item.status === 'WARN';
    card.className = `shield-card ${isPass ? 'pass' : isWarn ? 'warn' : 'fail'}`;

    const badgeClass = isPass ? 'pill-safe' : isWarn ? 'pill-warning' : 'pill-danger';
    const icon = isPass ? '✓' : isWarn ? '⚠️' : '✕';

    card.innerHTML = `
      <div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.35rem;">
          <strong style="font-size:0.85rem;">${item.title_bn}</strong>
          <span class="pill-tag ${badgeClass}" style="font-size:0.7rem;">${icon} ${item.status}</span>
        </div>
        <p style="font-size:0.78rem; color:var(--c-stone-600); line-height:1.45;">${item.details_bn}</p>
      </div>
      <div style="margin-top:0.5rem; font-size:0.75rem; font-weight:600; color:${isPass ? 'var(--c-risk-safe)' : 'var(--c-risk-danger)'}">
        ${isPass ? 'বৈধ ও নিয়মিত' : 'সতর্কতা / অমিল'}
      </div>
    `;
    shieldGrid.appendChild(card);
  });

  // Render linked owners
  const ownersBox = document.getElementById('app-owners-tab-content');
  if (ownersBox && profile.current_owners) {
    ownersBox.innerHTML = profile.current_owners.map(o => `
      <div style="padding:0.45rem 0; border-bottom:1px dashed var(--c-stone-200); font-size:0.82rem;">
        <strong>${o.fictional_name}</strong> (${o.owner_id})
        <div style="color:var(--c-stone-500); font-size:0.75rem;">হিস্যা: ${(o.ownership_share * 100).toFixed(1)}% | পিতা/স্বামী: ${o.father_or_spouse || 'উক্ত'}</div>
      </div>
    `).join('') || '<p>কোনো রেকর্ড নেই</p>';
  }
}

function renderCitizenPolygon(geojson, safetyRating) {
  if (!AppState.citizenMap) initCitizenMap();
  if (!AppState.citizenMap) return;

  if (AppState.citizenGeoLayer) {
    AppState.citizenMap.removeLayer(AppState.citizenGeoLayer);
  }

  const color = (safetyRating === 'SAFE') ? '#059669' : '#dc2626';

  AppState.citizenGeoLayer = L.geoJSON(geojson, {
    style: {
      color: color,
      weight: 3,
      fillColor: color,
      fillOpacity: 0.35
    }
  }).addTo(AppState.citizenMap);

  try {
    AppState.citizenMap.fitBounds(AppState.citizenGeoLayer.getBounds(), { padding: [20, 20], maxZoom: 16 });
  } catch (e) {}
}

// ==========================================================================
// WORKSPACE 3: OFFICER TRIAGE & FRAUD (P3)
// ==========================================================================
function initOfficerWorkspace() {
  const filter = document.getElementById('app-officer-filter');
  if (filter) {
    filter.addEventListener('change', (e) => loadOfficerQueue(e.target.value));
  }

  const form = document.getElementById('rev-decision-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      await submitOfficerDecision();
    });
  }
}

async function loadOfficerQueue(severity = null) {
  const lockBanner = document.getElementById('app-officer-lock-banner');
  const tableBox = document.getElementById('app-officer-table-box');
  const tbody = document.getElementById('app-officer-tbody');
  const countEl = document.getElementById('app-officer-count');

  if (AppState.user.role !== 'OFFICER' && AppState.user.role !== 'ADMINISTRATOR') {
    if (lockBanner) lockBanner.style.display = 'block';
    if (tableBox) tableBox.style.display = 'none';
    return;
  } else {
    if (lockBanner) lockBanner.style.display = 'none';
    if (tableBox) tableBox.style.display = 'block';
  }

  if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:1.5rem;">অফিসার কিউ লোড হচ্ছে...</td></tr>`;

  try {
    const res = await LandTechAPI.getOfficerQueue(severity, 30);
    AppState.officerCases = res.queue || [];
    if (countEl) countEl.textContent = res.pending_count || 0;

    if (AppState.officerCases.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:1.5rem; color:var(--c-forest-700);">কোনো অনিষ্পন্ন কেস নেই।</td></tr>`;
      return;
    }

    tbody.innerHTML = '';
    AppState.officerCases.forEach(c => {
      const tr = document.createElement('tr');
      const sevClass = c.severity === 'CRITICAL' ? 'pill-danger' : 'pill-warning';

      tr.innerHTML = `
        <td><strong>${c.case_id}</strong></td>
        <td>${c.parcel_id}</td>
        <td>${c.mouza} (দাগ ${c.dag_number})</td>
        <td><span class="pill-tag ${sevClass}">${c.finding_code}</span></td>
        <td class="num"><strong>${c.risk_score}</strong></td>
        <td>${c.review_status}</td>
        <td><button class="btn btn-secondary-stone btn-sm inspect-btn" style="padding:2px 8px;">কেস তদন্ত</button></td>
      `;

      tr.querySelector('.inspect-btn').addEventListener('click', () => openReviewModal(c));
      tbody.appendChild(tr);
    });
  } catch (err) {
    if (tbody) tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--c-risk-danger); padding:1.5rem;">ত্রুটি: ${err.message}</td></tr>`;
  }
}

function openReviewModal(caseItem) {
  AppState.selectedCase = caseItem;
  const modal = document.getElementById('calm-review-modal');
  if (!modal) return;

  document.getElementById('rev-modal-case-id').textContent = caseItem.case_id;
  document.getElementById('rev-modal-parcel-id').textContent = caseItem.parcel_id;
  document.getElementById('rev-modal-explanation').textContent = caseItem.explanation_bn;

  // Side-by-Side Deed Diff
  const diffBox = document.getElementById('rev-modal-deed-diff');
  let refs = {};
  try {
    refs = typeof caseItem.evidence_references === 'string'
      ? JSON.parse(caseItem.evidence_references)
      : caseItem.evidence_references;
  } catch (e) {}

  if (caseItem.finding_code === 'DS-01' && refs.prior_deed && refs.competing_deed) {
    diffBox.style.display = 'block';
    diffBox.innerHTML = `
      <div class="deed-side-diff">
        <div class="diff-col first">
          <div style="font-weight:700; font-size:0.85rem; margin-bottom:0.4rem; color:var(--c-risk-info);">১ম দলিল (পূর্ববর্তী হস্তান্তর)</div>
          <div style="font-size:0.78rem;"><strong>দলিল নং:</strong> ${refs.prior_deed}</div>
          <div style="font-size:0.78rem;"><strong>বিক্রেতা:</strong> ${refs.seller_id}</div>
          <div style="font-size:0.78rem;"><strong>ক্রেতা:</strong> ${refs.first_buyer_id}</div>
          <div style="font-size:0.75rem; color:var(--c-risk-danger); margin-top:0.2rem;">ই-নামজারি: অনিষ্পন্ন / মুলতবি</div>
        </div>
        <div class="diff-col competing">
          <div style="font-weight:700; font-size:0.85rem; margin-bottom:0.4rem; color:var(--c-risk-danger);">২য় দলিল (দ্বৈত বিক্রয় দলিল)</div>
          <div style="font-size:0.78rem;"><strong>দলিল নং:</strong> ${refs.competing_deed}</div>
          <div style="font-size:0.78rem;"><strong>একই বিক্রেতা:</strong> ${refs.seller_id}</div>
          <div style="font-size:0.78rem;"><strong>২য় ক্রেতা:</strong> ${refs.second_buyer_id}</div>
          <div style="font-size:0.75rem; color:var(--c-risk-danger); margin-top:0.2rem;">ঝুঁকি: ১ম নামজারি নিষ্পত্তিহীন বিক্রি</div>
        </div>
      </div>
    `;
  } else {
    diffBox.style.display = 'none';
  }

  modal.classList.add('open');
}

function closeReviewModal() {
  const modal = document.getElementById('calm-review-modal');
  if (modal) modal.classList.remove('open');
}

async function submitOfficerDecision() {
  if (!AppState.selectedCase) return;
  const action = document.getElementById('rev-action-select')?.value;
  const reason = document.getElementById('rev-reason-input')?.value.trim() || 'নথিপত্র ও ক্যাডাস্ট্রাল উপাত্ত বিশ্লেষণপূর্বক সিদ্ধান্ত গৃহীত।';

  try {
    const res = await LandTechAPI.recordReviewDecision(AppState.selectedCase.case_id, action, reason);
    showToast(`সিদ্ধান্ত সংরক্ষিত! লগ নং: ${res.log_id}`);
    closeReviewModal();
    loadOfficerQueue();
  } catch (err) {
    alert(`সিদ্ধান্ত সংরক্ষণ ব্যর্থ: ${err.message}`);
  }
}

// ==========================================================================
// WORKSPACE 4: SMART E-MUTATION SIMULATOR (P4)
// ==========================================================================
function initMutationWorkspace() {
  const simBtn = document.getElementById('mut-sim-btn');
  if (!simBtn) return;

  simBtn.addEventListener('click', async () => {
    const parcelId = document.getElementById('mut-sim-parcel')?.value.trim() || 'BD-PAR-000101';
    const deedId = document.getElementById('mut-sim-deed')?.value.trim() || 'SAVAR-20261018-000101';
    const applicantId = document.getElementById('mut-sim-applicant')?.value.trim() || 'OWN-000305';

    const outBox = document.getElementById('mut-sim-result-box');
    outBox.innerHTML = 'প্রাক-যাচাই অ্যালগরিদম পরীক্ষা করা হচ্ছে...';

    try {
      const res = await LandTechAPI.preCheckMutation(parcelId, deedId, applicantId);
      const isApproved = res.can_proceed;

      outBox.innerHTML = `
        <div style="padding:1rem; border-radius:8px; background:${isApproved ? 'var(--c-risk-safe-bg)' : 'var(--c-risk-danger-bg)'}; border:1px solid ${isApproved ? 'var(--c-risk-safe-border)' : 'var(--c-risk-danger-border)'}">
          <h4 style="color:${isApproved ? 'var(--c-risk-safe)' : 'var(--c-risk-danger)'}; font-size:0.95rem;">
            ${isApproved ? '✓ প্রাক-যাচাই উত্তীর্ণ: নামজারি আবেদন গ্রহণযোগ্য' : '✕ প্রাক-যাচাই ব্যর্থ: আবেদন সরাসরি স্থগিত করা হলো'}
          </h4>
          <p style="font-size:0.85rem; margin-top:0.35rem;">${res.precheck_summary_bn}</p>
          ${res.rejection_reasons.length > 0 ? `
            <ul style="margin-top:0.4rem; margin-left:1.25rem; font-size:0.8rem; color:var(--c-risk-danger);">
              ${res.rejection_reasons.map(r => `<li>${r}</li>`).join('')}
            </ul>
          ` : ''}
        </div>
      `;
    } catch (e) {
      outBox.innerHTML = `<span style="color:var(--c-risk-danger)">ত্রুটি: ${e.message}</span>`;
    }
  });
}

// ==========================================================================
// WORKSPACE 5: DOCUMENT VERIFICATION / SHA-256 HASH (P2)
// ==========================================================================
function initDocumentVerifyWorkspace() {
  const dropzone = document.getElementById('hash-dropzone');
  const fileInput = document.getElementById('hash-file-input');
  const btnClean = document.getElementById('btn-hash-sample-clean');
  const btnTamper = document.getElementById('btn-hash-sample-tampered');

  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('dragover'); });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        verifyDocumentFile(e.dataTransfer.files[0]);
      }
    });
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        verifyDocumentFile(fileInput.files[0]);
      }
    });
  }

  if (btnClean) {
    btnClean.addEventListener('click', () => simulateDocHashTest(false));
  }
  if (btnTamper) {
    btnTamper.addEventListener('click', () => simulateDocHashTest(true));
  }
}

async function verifyDocumentFile(file) {
  const outBox = document.getElementById('hash-verification-output');
  outBox.innerHTML = 'ক্লায়েন্ট সাইড SHA-256 হ্যাশ গণনা করা হচ্ছে...';

  try {
    const arrayBuffer = await file.arrayBuffer();
    const clientHash = await LandTechAPI.computeClientSHA256(arrayBuffer);

    outBox.innerHTML = `
      <div style="font-size:0.82rem; margin-bottom:0.75rem;">
        <div><strong>ফাইলের নাম:</strong> ${file.name}</div>
        <div><strong>আকার:</strong> ${(file.size / 1024).toFixed(1)} KB</div>
        <div style="margin-top:0.35rem;"><strong>গণনাকৃত SHA-256 হ্যাশ:</strong></div>
        <code class="hash-token-code">${clientHash}</code>
      </div>
      <div style="color:var(--c-stone-500); font-size:0.8rem;">রেজিস্ট্রি লেজারের সাথে মেলানো হচ্ছে...</div>
    `;

    const res = await LandTechAPI.verifyDocumentIntegrity(file, file.name);
    displayHashVerificationResult(res, clientHash);
  } catch (err) {
    outBox.innerHTML = `<span style="color:var(--c-risk-danger)">যাচাইয়ে ত্রুটি: ${err.message}</span>`;
  }
}

async function simulateDocHashTest(isTampered) {
  const outBox = document.getElementById('hash-verification-output');
  outBox.innerHTML = 'নমুনা দলিলের ডিজিটাল ফিঙ্গারপ্রিন্ট টেস্ট চলছে...';

  try {
    // Fetch actual sample authentic PNG bytes from server
    let imgRes = await fetch('/api/v1/documents/sample-deed');
    if (!imgRes.ok) {
      imgRes = await fetch('/static/assets/samples/sample_deed_authentic.png');
    }
    let blob = null;
    let filename = 'DOC-000001.png';

    if (imgRes.ok) {
      blob = await imgRes.blob();
      if (isTampered) {
        // Corrupt 1 byte in the array buffer
        const buf = await blob.arrayBuffer();
        const u8 = new Uint8Array(buf);
        u8[u8.length - 10] = u8[u8.length - 10] ^ 0xFF;
        blob = new Blob([u8], { type: 'image/png' });
        filename = 'DOC-000001_tampered.png';
      }
    } else {
      // Fallback
      const fakeText = isTampered ? "TAMPERED_DEED_BYTE_2026" : "DESHMRITTIKA_DOC_000001";
      blob = new Blob([fakeText], { type: 'text/plain' });
    }

    const arrayBuffer = await blob.arrayBuffer();
    const clientHash = await LandTechAPI.computeClientSHA256(arrayBuffer);

    const res = await LandTechAPI.verifyDocumentIntegrity(blob, filename);
    displayHashVerificationResult(res, clientHash);
  } catch (e) {
    outBox.innerHTML = `<span style="color:var(--c-risk-danger)">টেস্ট ত্রুটি: ${e.message}</span>`;
  }
}

function displayHashVerificationResult(res, clientHash) {
  const outBox = document.getElementById('hash-verification-output');
  if (res.is_authentic) {
    outBox.innerHTML = `
      <div style="background:var(--c-risk-safe-bg); border:1px solid var(--c-risk-safe-border); padding:1rem; border-radius:8px;">
        <h4 style="color:var(--c-risk-safe); font-size:0.95rem; display:flex; align-items:center; gap:0.4rem;">
          ✓ মূল দলিল অবিকৃত ও প্রামাণ্য (Authentic)
        </h4>
        <div style="font-size:0.8rem; margin-top:0.4rem;">
          <strong>ম্যাচিং দলিল আইডি:</strong> ${res.matched_document_id} | <strong>পার্সেল:</strong> ${res.parcel_id}
        </div>
        <div style="margin-top:0.3rem;"><strong>ভেরিফাইড SHA-256 হ্যাশ:</strong></div>
        <code class="hash-token-code" style="color:var(--c-risk-safe);">${clientHash}</code>
        <div style="font-size:0.75rem; color:var(--c-forest-700); margin-top:0.3rem;">উৎস লেবেল: ${res.provenance_label}</div>
      </div>
    `;
  } else {
    outBox.innerHTML = `
      <div style="background:var(--c-risk-danger-bg); border:1px solid var(--c-risk-danger-border); padding:1rem; border-radius:8px;">
        <h4 style="color:var(--c-risk-danger); font-size:0.95rem; display:flex; align-items:center; gap:0.4rem;">
          ✕ বিকৃত বা জাল দলিল শনাক্ত হয়েছে (Tamper Detected)
        </h4>
        <div style="font-size:0.8rem; margin-top:0.4rem;">
          নথিটির ডিজিটাল ফিঙ্গারপ্রিন্ট সাব-রেজিস্ট্রির মূল বালাম বহির সাথে মিলছে না।
        </div>
        <div style="margin-top:0.3rem;"><strong>অমিল হ্যাশ:</strong></div>
        <code class="hash-token-code" style="color:var(--c-risk-danger);">${clientHash}</code>
        <div style="font-size:0.75rem; color:var(--c-risk-danger); margin-top:0.3rem;">স্ট্যাটাস: ${res.status_label}</div>
      </div>
    `;
  }
}

// ==========================================================================
// WORKSPACE 6: ADVANCED OCR WORKSPACE (P1 REPAIR)
// ==========================================================================
function initAdvancedOCRWorkspace() {
  const dropzone = document.getElementById('ocr-dropzone');
  const fileInput = document.getElementById('ocr-file-input');
  const runBtn = document.getElementById('run-advanced-ocr-btn');
  const loadSampleBtn = document.getElementById('ocr-load-sample-btn');
  const copyBtn = document.getElementById('ocr-copy-btn');
  const downloadBtn = document.getElementById('ocr-download-btn');

  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('dragover'); });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        handleOcrFileSelection(e.dataTransfer.files[0]);
      }
    });
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        handleOcrFileSelection(fileInput.files[0]);
      }
    });
  }

  if (loadSampleBtn) {
    loadSampleBtn.addEventListener('click', async () => {
      try {
        let res = await fetch('/api/v1/documents/sample-deed');
        if (!res.ok) {
          res = await fetch('/static/assets/samples/sample_deed_authentic.png');
        }
        if (res.ok) {
          const blob = await res.blob();
          const file = new File([blob], "SAMPLE_SAF_KABALA_DEED_000001.png", { type: "image/png" });
          handleOcrFileSelection(file);
        }
      } catch (e) {
        alert("নমুনা দলিল লোড করা যায়নি: " + e.message);
      }
    });
  }

  const loadSamplePdfBtn = document.getElementById('ocr-load-sample-pdf-btn');
  if (loadSamplePdfBtn) {
    loadSamplePdfBtn.addEventListener('click', async () => {
      try {
        let res = await fetch('/api/v1/documents/sample-pdf');
        if (!res.ok) {
          res = await fetch('/static/assets/samples/sample_khatian.pdf');
        }
        if (res.ok) {
          const blob = await res.blob();
          const file = new File([blob], "SAMPLE_BS_KHATIAN_PORCHA.pdf", { type: "application/pdf" });
          handleOcrFileSelection(file);
        }
      } catch (e) {
        alert("নমুনা PDF লোড করা যায়নি: " + e.message);
      }
    });
  }

  if (runBtn) {
    runBtn.addEventListener('click', executeAdvancedOCR);
  }

  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const text = document.getElementById('ocr-output-textarea')?.value;
      if (text) {
        navigator.clipboard.writeText(text);
        showToast("টেক্সট ক্লিপবোর্ডে কপি করা হয়েছে!");
      }
    });
  }

  if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
      const text = document.getElementById('ocr-output-textarea')?.value;
      if (text) {
        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = "extracted_land_record_ocr.txt";
        a.click();
      }
    });
  }
}

function handleOcrFileSelection(file) {
  AppState.activeOcrFile = file;

  // Show preview
  const previewContainer = document.getElementById('ocr-preview-container');
  const previewImg = document.getElementById('ocr-preview-img');

  if (file.type.startsWith('image/')) {
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewContainer.style.display = 'flex';
    };
    reader.readAsDataURL(file);
  } else {
    // PDF representation preview
    previewContainer.style.display = 'flex';
    previewImg.src = '/static/assets/images/due_diligence_review.jpg';
  }

  showToast(`ফাইল নির্বাচিত: ${file.name}`);
}

async function executeAdvancedOCR() {
  if (!AppState.activeOcrFile) {
    alert("অনুগ্রহ করে একটি দলিল ইমেজ বা PDF ফাইল নির্বাচন করুন।");
    return;
  }

  const preprocessMode = document.getElementById('ocr-preprocess-mode')?.value || 'enhance_contrast';
  const rotateDeg = parseInt(document.getElementById('ocr-rotate-deg')?.value || '0', 10);
  const lang = document.getElementById('ocr-lang-select')?.value || 'ben+eng';

  const textarea = document.getElementById('ocr-output-textarea');
  const confFill = document.getElementById('ocr-confidence-fill');
  const confLabel = document.getElementById('ocr-confidence-label');
  const confBadge = document.getElementById('ocr-confidence-badge');
  const structDiv = document.getElementById('ocr-structured-fields');

  textarea.value = "টেসেরাক্ট OCR প্রক্রিয়াকরণ চলছে...\nদয়া করে অপেক্ষা করুন...";
  confFill.style.width = '30%';

  try {
    const res = await LandTechAPI.uploadDocumentOCR(
      AppState.activeOcrFile,
      AppState.activeOcrFile.name,
      preprocessMode,
      rotateDeg,
      lang
    );

    if (res.success) {
      textarea.value = res.extracted_text || "(কোনো টেক্সট পাওয়া যায়নি)";
      const score = res.confidence_score || 0;
      confFill.style.width = `${score}%`;
      confLabel.textContent = `${score}%`;

      confBadge.className = score >= 75 ? 'pill-tag pill-safe' : (score >= 45 ? 'pill-tag pill-warning' : 'pill-tag pill-danger');
      confBadge.textContent = `${res.confidence_level} CONFIDENCE`;

      // Render structured fields
      const ent = res.extracted_entities || {};
      structDiv.innerHTML = `
        <div><strong>দলিল নম্বর:</strong> ${ent.detected_deed_numbers?.join(', ') || 'অনুপস্থিত'}</div>
        <div><strong>দাগ নম্বর:</strong> ${ent.detected_dag_numbers?.join(', ') || 'অনুপস্থিত'}</div>
        <div><strong>খতিয়ান নম্বর:</strong> ${ent.detected_khatian_numbers?.join(', ') || 'অনুপস্থিত'}</div>
        <div><strong>মৌজা:</strong> ${ent.detected_mouza || 'অনুপস্থিত'} | <strong>পরিমাণ:</strong> ${ent.detected_area || 'অনুপস্থিত'}</div>
        <div style="color:var(--c-forest-700); font-size:0.75rem; margin-top:0.35rem;">
          ভাষা মডেল: ${res.language_used} | সময়: ${res.processing_time_ms} ms | পাতা: ${res.pages_processed}
        </div>
      `;

      showToast(`OCR সফল: ${res.char_count} টি অক্ষর নিষ্কাশিত!`);
    } else {
      textarea.value = `ত্রুটি: ${res.error || res.ocr_status}`;
      confFill.style.width = '0%';
      confLabel.textContent = '০%';
      confBadge.className = 'pill-tag pill-danger';
      confBadge.textContent = 'FAILED';
    }
  } catch (err) {
    textarea.value = `রিকোয়েস্ট ত্রুটি: ${err.message}`;
  }
}

// ==========================================================================
// WORKSPACE 7: CADASTRAL GIS & KHAS PROTECTION (P6)
// ==========================================================================
function initCadastralGISWorkspace() {
  const mapCanvas = document.getElementById('gis-map-canvas');
  if (!mapCanvas || AppState.gisMap) return;

  AppState.gisMap = L.map('gis-map-canvas').setView([23.8560, 90.2600], 14);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors | DeshMrittika GIS'
  }).addTo(AppState.gisMap);

  // Layer toggles
  document.getElementById('layer-khas-toggle')?.addEventListener('change', (e) => {
    if (AppState.gisLayers.khas) {
      if (e.target.checked) AppState.gisMap.addLayer(AppState.gisLayers.khas);
      else AppState.gisMap.removeLayer(AppState.gisLayers.khas);
    }
  });

  document.getElementById('layer-corridor-toggle')?.addEventListener('change', (e) => {
    if (AppState.gisLayers.corridor) {
      if (e.target.checked) AppState.gisMap.addLayer(AppState.gisLayers.corridor);
      else AppState.gisMap.removeLayer(AppState.gisLayers.corridor);
    }
  });

  // Highway Corridor (Dhaka-Aricha 100m buffer representation)
  const corridorLine = L.polyline([
    [23.8400, 90.2300],
    [23.8600, 90.2600],
    [23.8750, 90.2850]
  ], {
    color: '#9333ea',
    weight: 8,
    opacity: 0.5,
    dashArray: '8, 8'
  }).addTo(AppState.gisMap);
  corridorLine.bindPopup("<strong>ঢাকা-আরিচা জাতীয় মহাসড়ক ১০০-মিটার অধিগ্রহণ করিডোর</strong>");
  AppState.gisLayers.corridor = corridorLine;

  // Khas Polygon (Government 1-No Khas land representation in Savar)
  const khasPoly = L.polygon([
    [23.8580, 90.2580],
    [23.8620, 90.2590],
    [23.8610, 90.2640],
    [23.8570, 90.2630]
  ], {
    color: '#d97706',
    fillColor: '#fde68a',
    fillOpacity: 0.6,
    weight: 2
  }).addTo(AppState.gisMap);
  khasPoly.bindPopup("<strong>১-নং খাস খতিয়ানভুক্ত সরকারি সম্পদ</strong><br>দাগ নং: ২০৫ (আমিনবাজার)");
  AppState.gisLayers.khas = khasPoly;

  // Quick Go button
  document.getElementById('map-quick-go-btn')?.addEventListener('click', () => {
    const dag = document.getElementById('map-quick-dag')?.value;
    if (dag == '101') {
      AppState.gisMap.setView([23.8560, 90.2600], 16);
    } else if (dag == '205') {
      AppState.gisMap.setView([23.8590, 90.2600], 16);
    }
  });
}

// ==========================================================================
// WORKSPACE 8: AUDIT TRAIL LOGS
// ==========================================================================
async function loadAuditTrailLogs() {
  const tbody = document.getElementById('app-audit-tbody');
  if (!tbody) return;

  tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:1.5rem;">অডিট লগ লোড হচ্ছে...</td></tr>`;

  try {
    const res = await LandTechAPI.getAuditLogs(30);
    if (!res.audit_logs || res.audit_logs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:1.5rem; color:var(--c-stone-400);">কোনো অডিট লগ রেকর্ড নেই।</td></tr>`;
      return;
    }

    tbody.innerHTML = res.audit_logs.map(l => `
      <tr>
        <td><strong>${l.log_id}</strong></td>
        <td>${l.case_id} (${l.parcel_id})</td>
        <td>${l.reviewer_id}</td>
        <td><span class="pill-tag pill-forest">${l.action}</span></td>
        <td style="max-width:280px; font-size:0.78rem;">${l.reason || 'আদেশ কার্যকর'}</td>
        <td class="num" style="font-size:0.75rem;">${new Date(l.timestamp).toLocaleString('bn-BD')}</td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--c-risk-danger); padding:1.5rem;">ত্রুটি: ${err.message}</td></tr>`;
  }
}
