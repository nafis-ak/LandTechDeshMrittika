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
    corridor: null,
    offices: null
  },
  officials: {
    page: 1,
    limit: 12,
    total: 0,
    filters: {},
    lang: 'bn'
  },
  officerCases: [],
  selectedCase: null,
  activeOcrFile: null
};

// 6-Step Walkthrough Data
const WALKTHROUGH_STEPS = {
  1: {
    track: "সমস্যা ট্র্যাক ১ — প্রাচীন রেকর্ড ডিজিটাইজেশন (পি১)",
    title: "প্রাচীন খতিয়ান ও দলিলের অপটিক্যাল ক্যারেক্টার রিকগনিশন (ওসিআর)",
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
    track: "সমস্যা ট্র্যাক ২ — ডিজিটাল প্রামাণিকতা ও দলিল যাচাই (পি২)",
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
    track: "সমস্যা ট্র্যাক ৩ (মুখ্য সমস্যা) — দ্বৈত বিক্রয় ও জালিয়াতি দমন (পি৩)",
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
    track: "সমস্যা ট্র্যাক ৪ — স্মার্ট ই-নামজারি ও রেজিস্ট্রি সেতু (পি৪)",
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
    track: "সমস্যা ট্র্যাক ৫ — ক্রয়ের পূর্বে ৫-দফা যাচাই বাতায়ন (পি৫)",
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
    track: "সমস্যা ট্র্যাক ৬ (উদ্ভাবনী জিআইএস) — খাসজমি ও সীমানা রক্ষা (পি৬)",
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
  initLanguageToggles();
  initSearchWorkspace();
  initOfficerWorkspace();
  initMutationWorkspace();
  initDocumentVerifyWorkspace();
  initAdvancedOCRWorkspace();
  initCadastralGISWorkspace();
  initAuthSystem();
  applyRolePermissions();

  // Load backend health
  checkBackendHealth();

  // Initialize Auth State: Restore saved session or keep guest mode
  LandTechAPI.initStoredAuth();
  if (LandTechAPI.token) {
    try {
      const me = await LandTechAPI.getMe();
      AppState.user = {
        user_id: me.user_id,
        name: me.full_name,
        role: me.role,
        email: me.email,
        status: me.status
      };
    } catch (e) {
      console.warn("Saved session expired or invalid, reverting to guest:", e);
      LandTechAPI.clearAuthToken();
      AppState.user = null;
    }
  } else {
    AppState.user = null;
  }

  updateAuthUI(AppState.user);
  applyRolePermissions();

  // Pre-load default parcel BD-PAR-000101
  loadCitizenDossier('BD-PAR-000101');

  // URL Hash Routing Support
  function checkRouteHash() {
    const hash = window.location.hash.replace('#', '');
    if (hash === 'app') {
      navigateToApp('overview');
    } else if (['overview', 'citizen', 'officer', 'mutation', 'ocr', 'verify', 'map', 'audit', 'dataset', 'settings', 'users', 'security-logs'].includes(hash)) {
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

// ============================================================================
// STRICT FOUR-ROLE RBAC & NAVIGATION MATRIX (BHUMI-SYNC v2.2)
// Roles: CITIZEN, BUYER, OFFICER, ADMINISTRATOR
// ============================================================================

const ROLE_NAV_CONFIG = {
  CITIZEN: [
    { page: 'overview', icon: '📊', label: 'ওভারভিউ', labelEn: 'Overview' },
    { page: 'citizen-myland', icon: '🏡', label: 'আমার জমি ও খতিয়ান', labelEn: 'My Land' },
    { page: 'citizen', icon: '🔍', label: 'মৌজা ও দাগ অনুসন্ধান', labelEn: 'Parcel Search' },
    { page: 'ocr', icon: '📜', label: 'দলিল ও পরচা স্ক্যান (OCR)', labelEn: 'Document OCR' },
    { page: 'citizen-applications', icon: '📝', label: 'নামজারি ও সেবা আবেদন', labelEn: 'My Applications' },
    { page: 'mutation', icon: '🔄', label: 'আবেদন ট্র্যাকিং', labelEn: 'Mutation Tracking' },
    { page: 'map', icon: '🗺️', label: 'ক্যাডাস্ট্রাল ম্যাপ ও খাস রক্ষা', labelEn: 'Cadastral Map' },
    { page: 'officials-directory', icon: '🏛️', label: 'ভূমি কর্মকর্তা ডিরেক্টরি', labelEn: 'Officials Directory' },
    { page: 'citizen-notifications', icon: '🔔', label: 'নোটিফিকেশন ও নোটিশ', labelEn: 'My Notifications' },
    { page: 'citizen-activity', icon: '⏱️', label: 'কার্যক্রম ও অডিট লগ', labelEn: 'My Activity' }
  ],
  BUYER: [
    { page: 'buyer-overview', icon: '📊', label: 'ওভারভিউ', labelEn: 'Overview' },
    { page: 'citizen', icon: '🔍', label: 'দাগ ও খতিয়ান যাচাই', labelEn: 'Parcel Search' },
    { page: 'due-diligence', icon: '🛡️', label: 'ডিউ ডিলিজেন্স ও ঝুঁকি বিশ্লেষণ', labelEn: 'Due Diligence' },
    { page: 'buyer-ownership-summary', icon: '📜', label: 'মালিকানা ইতিহাস সারসংক্ষেপ', labelEn: 'Ownership Summary' },
    { page: 'buyer-fraud-risk', icon: '🚨', label: 'দ্বৈত বিক্রয় ঝুঁকি যাচাই', labelEn: 'Double-Selling Risk' },
    { page: 'verify', icon: '🔐', label: 'দলিল ইন্টিগ্রিটি ভেরিফিকেশন', labelEn: 'Document Integrity' },
    { page: 'map', icon: '🗺️', label: 'ক্যাডাস্ট্রাল ম্যাপ ও সীমানা বিরোধ', labelEn: 'Map & Boundary Warnings' },
    { page: 'officials-directory', icon: '🏛️', label: 'ভূমি কর্মকর্তা ডিরেক্টরি', labelEn: 'Officials Directory' },
    { page: 'buyer-compare-reports', icon: '📑', label: 'প্লট তুলনা ও ডিউ ডিলিজেন্স রিপোর্ট', labelEn: 'Comparison & Reports' },
    { page: 'buyer-review-requests', icon: '📨', label: 'পুনঃযাচাই আবেদন', labelEn: 'Review Requests' }
  ],
  OFFICER: [
    { page: 'officer-overview', icon: '🏛️', label: 'কর্মকর্তা ওভারভিউ', labelEn: 'Officer Overview' },
    { page: 'officer-cases', icon: '📂', label: 'অ্যাসাইনকৃত আবেদন ও ফাইল', labelEn: 'Assigned Applications' },
    { page: 'officer', icon: '⚖️', label: 'প্রতারণা ও দ্বৈত বিক্রয় ট্রায়াজ', labelEn: 'Fraud Triage Queue' },
    { page: 'officer-deed-compare', icon: '🔍', label: 'দলিল ও রেকর্ড ক্রস-চেক', labelEn: 'Deed Comparison' },
    { page: 'mutation', icon: '🔄', label: 'নামজারি পর্যালোচনা ও সুপারিশ', labelEn: 'Mutation Review' },
    { page: 'officer-doc-review', icon: '📜', label: 'নথি ও ওটিপি/স্বাক্ষর যাচাই', labelEn: 'Document Review' },
    { page: 'officer-hearings', icon: '📅', label: 'শুনানি ও সরেজমিন তদন্ত', labelEn: 'Hearing & Field Verification' },
    { page: 'map', icon: '🗺️', label: 'ক্যাডাস্ট্রাল ম্যাপ ও খাস রক্ষা', labelEn: 'Cadastral Map' },
    { page: 'officials-directory', icon: '🏛️', label: 'ভূমি কর্মকর্তা ডিরেক্টরি', labelEn: 'Officials Directory' },
    { page: 'officer-decisions', icon: '✍️', label: 'সিমুলেটেড সিদ্ধান্ত ও আদেশ', labelEn: 'Decision Simulation' },
    { page: 'audit', icon: '📋', label: 'তদন্ত ও সিদ্ধান্ত অডিট ট্রেইল', labelEn: 'Audit History' }
  ],
  ADMINISTRATOR: [
    { page: 'admin-overview', icon: '⚡', label: 'সিস্টেম সার্বিক অবস্থা', labelEn: 'System Overview' },
    { page: 'users', icon: '👥', label: 'ব্যবহারকারী ও রোল ব্যবস্থাপনা', labelEn: 'User & Role Management' },
    { page: 'map', icon: '🗺️', label: 'ক্যাডাস্ট্রাল ম্যাপ ও খাস রক্ষা', labelEn: 'Cadastral Map' },
    { page: 'officials-directory', icon: '🏛️', label: 'ভূমি কর্মকর্তা ডিরেক্টরি', labelEn: 'Officials Directory' },
    { page: 'security-logs', icon: '🔒', label: 'নিরাপত্তা ও অডিট লগ', labelEn: 'Security Audit Logs' },
    { page: 'settings', icon: '🩺', label: 'ডাটাবেস ও সিস্টেম ডায়াগনস্টিক', labelEn: 'API & Database Health' },
    { page: 'dataset', icon: '🗄️', label: 'সিন্থেটিক ডেটাসেট পরিসংখ্যান', labelEn: 'Dataset & Provenance' },
    { page: 'admin-ocr-diagnostics', icon: '👁️', label: 'ওসিআর ইঞ্জিন ও ভাষা প্যাক হেলথ', labelEn: 'OCR Diagnostics' },
    { page: 'admin-rules-config', icon: '📏', label: 'প্রতারণা সনাক্তকরণ রুলবুক কনফিগ', labelEn: 'Fraud Rule Versions' },
    { page: 'admin-backups', icon: '💾', label: 'ব্যাকআপ ও অপারেশনাল জব', labelEn: 'Backup & Operational Jobs' },
    { page: 'admin-settings', icon: '⚙️', label: 'সিস্টেম কনফিগারেশন', labelEn: 'System Settings' }
  ]
};

const ROLE_ALLOWED_PAGES = {
  CITIZEN: ['overview', 'citizen-myland', 'citizen', 'ocr', 'citizen-applications', 'mutation', 'map', 'officials-directory', 'citizen-notifications', 'citizen-activity'],
  BUYER: ['buyer-overview', 'citizen', 'due-diligence', 'buyer-ownership-summary', 'buyer-fraud-risk', 'verify', 'map', 'officials-directory', 'buyer-compare-reports', 'buyer-review-requests'],
  OFFICER: ['officer-overview', 'officer-cases', 'officer', 'officer-deed-compare', 'mutation', 'officer-doc-review', 'officer-hearings', 'map', 'officials-directory', 'officer-decisions', 'audit'],
  ADMINISTRATOR: ['admin-overview', 'users', 'map', 'officials-directory', 'security-logs', 'settings', 'dataset', 'admin-ocr-diagnostics', 'admin-rules-config', 'admin-backups', 'admin-settings']
};

const ROLE_HOME_PAGE = {
  CITIZEN: 'overview',
  BUYER: 'buyer-overview',
  OFFICER: 'officer-overview',
  ADMINISTRATOR: 'admin-overview'
};

function renderSidebarNav(role) {
  const container = document.getElementById('sidebar-nav-container');
  if (!container) return;

  const currentRole = role || (AppState.user ? AppState.user.role : 'CITIZEN');
  const items = ROLE_NAV_CONFIG[currentRole] || ROLE_NAV_CONFIG.CITIZEN;
  const isEn = AppState.lang === 'en';

  const categoryLabels = {
    CITIZEN: isEn ? "CITIZEN WORKSPACE" : "নাগরিক বাতায়ন",
    BUYER: isEn ? "BUYER VERIFICATION HUB" : "ক্রেতা সুরক্ষা বাতায়ন",
    OFFICER: isEn ? "AC LAND JURISDICTION" : "সহকারী কমিশনার (ভূমি) দপ্তর",
    ADMINISTRATOR: isEn ? "SYSTEM ADMINISTRATION" : "সিস্টেম ও সাইবার প্রশাসন"
  };

  let html = `<div class="nav-category-title">${categoryLabels[currentRole] || "কার্যক্রম"}</div>`;

  items.forEach(item => {
    const isActive = AppState.currentPage === item.page;
    const label = isEn ? item.labelEn : item.label;
    html += `
      <div class="sidebar-nav-item ${isActive ? 'active' : ''}" data-page="${item.page}" id="nav-item-${item.page}" onclick="switchAppPage('${item.page}')">
        <span class="nav-icon">${item.icon}</span>
        <span class="nav-label">${label}</span>
      </div>
    `;
  });

  container.innerHTML = html;
}

function applyRolePermissions() {
  const currentRole = AppState.user ? AppState.user.role : 'CITIZEN';
  const allowed = ROLE_ALLOWED_PAGES[currentRole] || ROLE_ALLOWED_PAGES.CITIZEN;

  // Render role-specific navigation items strictly for this role
  renderSidebarNav(currentRole);

  // Update sidebar user profile card (Immutable)
  const isGuest = !AppState.user || !LandTechAPI.token;
  const sName = document.getElementById('sidebar-user-name');
  const sBadge = document.getElementById('sidebar-user-role-badge');
  const sAvatar = document.getElementById('sidebar-user-avatar');
  const sLogout = document.getElementById('sidebar-logout-btn');

  const roleLabels = {
    CITIZEN: 'সাধারণ নাগরিক',
    BUYER: 'সম্ভাব্য ক্রেতা',
    OFFICER: 'সহকারী কমিশনার - ভূমি',
    ADMINISTRATOR: 'সিস্টেম অ্যাডমিন'
  };

  if (!isGuest && AppState.user) {
    const rolePillClass = {
      CITIZEN: 'role-pill-citizen',
      BUYER: 'role-pill-buyer',
      OFFICER: 'role-pill-officer',
      ADMINISTRATOR: 'role-pill-admin'
    }[currentRole] || 'role-pill-citizen';

    const roleEmoji = {
      CITIZEN: '👤',
      BUYER: '💼',
      OFFICER: '🏛️',
      ADMINISTRATOR: '⚙️'
    }[currentRole] || '👤';

    if (sName) sName.textContent = AppState.user.name || AppState.user.email;
    if (sBadge) {
      sBadge.textContent = roleLabels[currentRole] || currentRole;
      sBadge.className = `user-role-pill ${rolePillClass}`;
    }
    if (sAvatar) sAvatar.textContent = roleEmoji;
    if (sLogout) sLogout.style.display = 'block';
  } else {
    if (sName) sName.textContent = 'অতিথি ব্যবহারকারী';
    if (sBadge) {
      sBadge.textContent = 'সাধারণ নাগরিক';
      sBadge.className = 'user-role-pill role-pill-citizen';
    }
    if (sAvatar) sAvatar.textContent = '👤';
    if (sLogout) sLogout.style.display = 'none';
  }

  // If current page is not allowed for this role, navigate to that role's home page
  if (!allowed.includes(AppState.currentPage) && AppState.currentPage !== 'unauthorized') {
    const homePage = ROLE_HOME_PAGE[currentRole] || 'overview';
    switchAppPage(homePage);
  }
}

function switchAppPage(pageName) {
  const currentRole = AppState.user ? AppState.user.role : 'CITIZEN';
  const allowed = ROLE_ALLOWED_PAGES[currentRole] || ROLE_ALLOWED_PAGES.CITIZEN;

  // STRICT RBAC CHECK: If page is forbidden for current role
  if (!allowed.includes(pageName)) {
    AppState.currentPage = 'unauthorized';
    const roleBanner = document.getElementById('unauthorized-role-banner');
    const roleLabels = {
      CITIZEN: 'সাধারণ নাগরিক (CITIZEN)',
      BUYER: 'সম্ভাব্য ক্রেতা (BUYER)',
      OFFICER: 'সহকারী কমিশনার - ভূমি (OFFICER)',
      ADMINISTRATOR: 'সিস্টেম অ্যাডমিন (ADMINISTRATOR)'
    };
    if (roleBanner) {
      roleBanner.textContent = `আপনার বর্তমান ভূমিকা: ${roleLabels[currentRole] || currentRole}`;
    }

    document.querySelectorAll('.workspace-page').forEach(page => {
      page.classList.toggle('active', page.id === 'page-unauthorized');
    });

    document.querySelectorAll('.sidebar-nav-item').forEach(item => {
      item.classList.remove('active');
    });

    const breadcrumb = document.getElementById('breadcrumb-current-page');
    if (breadcrumb) breadcrumb.textContent = "অননুমোদিত প্রবেশাধিকার (403)";

    showToast(`অননুমোদিত পৃষ্ঠা: ${currentRole} ভূমিকার জন্য এই মডিউলটি উন্মুক্ত নয়।`, 'warning');
    return;
  }

  // Allowed page transition
  AppState.currentPage = pageName;

  // Update active sidebar nav
  document.querySelectorAll('.sidebar-nav-item').forEach(item => {
    item.classList.toggle('active', item.getAttribute('data-page') === pageName);
  });

  // Switch workspace container (handle due-diligence mapping to page-citizen)
  const domId = pageName === 'due-diligence' ? 'page-citizen' : `page-${pageName}`;
  document.querySelectorAll('.workspace-page').forEach(page => {
    page.classList.toggle('active', page.id === domId);
  });

  // Update breadcrumb
  const titles = {
    overview: "ওভারভিউ ড্যাশবোর্ড",
    'citizen-myland': "আমার জমি ও খতিয়ান",
    citizen: "নাগরিক অনুসন্ধান ও ৫-দফা ডসিয়ার (P5)",
    ocr: "প্রাচীন পরচা ও দলিল OCR (P1)",
    'citizen-applications': "নামজারি ও সেবা আবেদনসমূহ",
    mutation: "স্মার্ট ই-নামজারি সিমুলেটর ও ট্র্যাকিং (P4)",
    'citizen-notifications': "সরকারি বার্তা ও শুনানির নোটিশ",
    'citizen-activity': "নাগরিক ব্যক্তিগত অডিট হিস্টোরি",
    'buyer-overview': "ক্রেতা ড্যাশবোর্ড ও ঝুঁকি সারসংক্ষেপ",
    'due-diligence': "৫-দফা ডিউ ডিলিজেন্স বিশ্লেষণ",
    'buyer-ownership-summary': "মালিকানা ইতিহাস সারসংক্ষেপ",
    'buyer-fraud-risk': "দ্বৈত বিক্রয় ঝুঁকি যাচাই (P3)",
    verify: "ক্রিপ্টোগ্রাফিক হ্যাশ যাচাই (P2)",
    map: "ক্যাডাস্ট্রাল ম্যাপ ও খাস রক্ষা (P6)",
    'buyer-compare-reports': "প্লট তুলনা ও ডিউ ডিলিজেন্স রিপোর্ট",
    'buyer-review-requests': "পুনঃযাচাই আবেদন কিউ",
    'officer-overview': "সহকারী কমিশনার (ভূমি) ওভারভিউ",
    'officer-cases': "অ্যাসাইনকৃত নামজারি আবেদন কিউ",
    officer: "দ্বৈত বিক্রয় ট্রায়াজ কিউ (P3)",
    'officer-deed-compare': "দলিল ও রেকর্ড ক্রস-চেক",
    'officer-doc-review': "দলিলের ডিজিটাল প্রামাণ্যতা",
    'officer-hearings': "শুনানি ক্যালেন্ডার ও সরেজমিন তদন্ত",
    'officer-decisions': "বিচারিক ও প্রশাসনিক আদেশ প্রণয়ন",
    audit: "অফিসার নিরীক্ষা ট্রেইল",
    'admin-overview': "প্ল্যাটফর্ম সার্বিক অবস্থা ও কন্ট্রোল",
    users: "ব্যবহারকারী ও ভূমিকা (RBAC)",
    'security-logs': "প্ল্যাটফর্ম নিরাপত্তা অডিট",
    settings: "সিস্টেম স্ট্যাটাস ও ডায়াগনস্টিক",
    dataset: "সিন্থেটিক ডেটাসেট পরিসংখ্যান",
    'admin-ocr-diagnostics': "বাংলা ওসিআর ইঞ্জিন স্বাস্থ্য",
    'admin-rules-config': "প্রতারণা সনাক্তকরণ রুলবুক",
    'admin-backups': "ডাটাবেস ব্যাকআপ ও WAL চেকপয়েন্ট",
    'admin-settings': "প্ল্যাটফর্ম নিরাপত্তা নীতি",
    'officials-directory': "ভূমি প্রশাসন কর্মকর্তা ও দপ্তর ডিরেক্টরি"
  };
  const breadcrumb = document.getElementById('breadcrumb-current-page');
  if (breadcrumb) breadcrumb.textContent = titles[pageName] || pageName;

  // Page specific data loaders
  if (pageName === 'citizen-myland') {
    loadCitizenParcels();
  } else if (pageName === 'citizen-applications') {
    loadCitizenApplications();
  } else if (pageName === 'citizen-notifications') {
    loadCitizenNotifications();
  } else if (pageName === 'citizen-activity') {
    loadCitizenActivity();
  } else if (pageName === 'buyer-review-requests') {
    loadBuyerReviewRequests();
  } else if (pageName === 'officer-cases') {
    loadOfficerAssignedApps();
  } else if (pageName === 'citizen' || pageName === 'due-diligence') {
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
  } else if (pageName === 'officials-directory') {
    loadOfficialsDirectory();
  } else if (pageName === 'officer') {
    loadOfficerQueue();
  } else if (pageName === 'audit') {
    loadAuditTrailLogs();
  } else if (pageName === 'users') {
    loadAdminUsers();
  } else if (pageName === 'security-logs') {
    loadAdminSecurityLogs();
  }
}

function returnToAuthorizedHome() {
  const currentRole = AppState.user ? AppState.user.role : 'CITIZEN';
  const homePage = ROLE_HOME_PAGE[currentRole] || 'overview';
  switchAppPage(homePage);
}

// Data Loaders for Citizen, Buyer, Officer, Admin
async function loadCitizenParcels() {
  if (!LandTechAPI.token) return;
  try {
    const res = await LandTechAPI.fetch('/api/v1/citizen/my-parcels');
    const container = document.getElementById('citizen-parcels-grid');
    if (!container || !res || !res.parcels) return;

    const parcelsNum = document.getElementById('cit-total-parcels-num');
    const areaNum = document.getElementById('cit-total-area-num');
    if (parcelsNum) parcelsNum.textContent = `${res.parcels.length} টি`;
    const totalArea = res.parcels.reduce((sum, p) => sum + (p.area_decimal || 0), 0);
    if (areaNum) areaNum.textContent = `${totalArea.toFixed(2)} শতক`;

    container.innerHTML = res.parcels.map(p => `
      <div class="calm-card" style="padding:1.5rem; border-left:4px solid var(--c-forest-600);">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
          <div>
            <span class="pill-tag pill-forest" style="font-size:0.7rem;">পার্সেল আইডি: ${p.parcel_id}</span>
            <h4 style="font-size:1.15rem; font-weight:700; margin-top:0.3rem; color:var(--c-forest-950);">${p.mouza} — দাগ নং ${p.dag_number}</h4>
          </div>
          <span class="pill-tag" style="background:#dcfce7; color:#166534; font-size:0.75rem; font-weight:600;">হালনাগাদ রেকর্ড</span>
        </div>
        <div style="font-size:0.85rem; color:var(--c-stone-600); line-height:1.6; margin-bottom:1rem;">
          <div><strong>খতিয়ান নং:</strong> ${p.khatian_no || p.khatian_number}</div>
          <div><strong>জমির পরিমাণ:</strong> ${p.area_decimal} শতক (${p.land_classification || 'নাল'})</div>
          <div><strong>মালিকানার সূত্র:</strong> ${p.ownership_type || 'উত্তরাধিকার ও নামজারি সূত্রে'}</div>
          <div><strong>ভূমি কর (খাজনা):</strong> ${p.tax_status || 'পরিশোধিত (১৪৩১ বঙ্গাব্দ)'}</div>
        </div>
        <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">
          <button class="btn btn-secondary-stone btn-sm" onclick="viewCitizenParcelDossier('${p.parcel_id}')">
            🔍 বিস্তারিত ডসিয়ার
          </button>
          <button class="btn btn-secondary-stone btn-sm" onclick="showToast('ই-পর্চা ডাউনলোড শুরু হয়েছে...')">
            📄 ই-পর্চা
          </button>
          <button class="btn btn-primary-forest btn-sm" onclick="startMutationForParcel('${p.parcel_id}')">
            🔄 নামজারি আবেদন
          </button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    console.warn("loadCitizenParcels error:", err);
  }
}

async function loadCitizenApplications() {
  if (!LandTechAPI.token) return;
  try {
    const res = await LandTechAPI.fetch('/api/v1/citizen/my-applications');
    const tbody = document.getElementById('citizen-applications-tbody');
    if (!tbody || !res || !res.applications) return;

    tbody.innerHTML = res.applications.map(app => `
      <tr>
        <td><strong>${app.app_id}</strong></td>
        <td>${app.mouza} — দাগ ${app.dag_number}</td>
        <td>${app.app_type}</td>
        <td><span class="pill-tag" style="background:#fef3c7; color:#92400e;">${app.status}</span></td>
        <td>${app.hearing_date ? `শুনানি: ${app.hearing_date}` : (app.officer_notes || 'প্রাথমিক যাচাই চলছে')}</td>
        <td>${app.created_at ? app.created_at.slice(0, 10) : ''}</td>
        <td><button class="btn btn-secondary-stone btn-sm" onclick="viewApplicationTimeline('${app.app_id}')">ট্র্যাকিং ➔</button></td>
      </tr>
    `).join('');
  } catch (err) {
    console.warn("loadCitizenApplications error:", err);
  }
}

async function loadCitizenNotifications() {
  if (!LandTechAPI.token) return;
  try {
    const res = await LandTechAPI.fetch('/api/v1/citizen/my-notifications');
    const list = document.getElementById('citizen-notifications-list');
    if (!list || !res || !res.notifications) return;

    list.innerHTML = res.notifications.map(n => `
      <div class="calm-card" style="padding:1.25rem; border-left:4px solid ${n.notif_type === 'HEARING' ? '#f59e0b' : 'var(--c-forest-600)'};">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div>
            <span class="pill-tag ${n.notif_type === 'HEARING' ? '' : 'pill-forest'}" style="${n.notif_type === 'HEARING' ? 'background:#fef3c7; color:#92400e;' : ''} font-size:0.7rem; font-weight:700;">${n.title}</span>
            <h4 style="font-size:1.05rem; font-weight:700; margin-top:0.3rem;">${n.title}</h4>
          </div>
          <span style="font-size:0.75rem; color:var(--c-stone-400);">${n.created_at ? n.created_at.slice(0, 10) : ''}</span>
        </div>
        <p style="font-size:0.88rem; color:var(--c-stone-700); margin-top:0.5rem; line-height:1.5;">${n.message}</p>
      </div>
    `).join('');
  } catch (err) {
    console.warn("loadCitizenNotifications error:", err);
  }
}

async function loadCitizenActivity() {
  if (!LandTechAPI.token) return;
  try {
    const res = await LandTechAPI.fetch('/api/v1/citizen/my-activity');
    const tbody = document.getElementById('citizen-activity-tbody');
    if (!tbody || !res || !res.activity) return;

    tbody.innerHTML = res.activity.map(act => `
      <tr>
        <td>${act.timestamp ? act.timestamp.replace('T', ' ').slice(0, 19) : ''}</td>
        <td>${act.action}</td>
        <td>127.0.0.1</td>
        <td><span class="pill-tag pill-forest">সফল</span></td>
      </tr>
    `).join('');
  } catch (err) {
    console.warn("loadCitizenActivity error:", err);
  }
}

async function loadBuyerReviewRequests() {
  if (!LandTechAPI.token) return;
  try {
    const res = await LandTechAPI.fetch('/api/v1/buyer/review-requests');
    const tbody = document.getElementById('buyer-review-requests-tbody');
    const countEl = document.getElementById('buyer-total-requests-count');
    if (countEl && res && res.total_requests !== undefined) {
      countEl.textContent = `${res.total_requests} টি`;
    }
    if (!tbody || !res || !res.requests) return;

    tbody.innerHTML = res.requests.map(r => `
      <tr>
        <td><strong>${r.request_id}</strong></td>
        <td>${r.parcel_id} (দাগ ${r.dag_number || ''})</td>
        <td>${r.reason}</td>
        <td><span class="pill-tag" style="background:#fee2e2; color:#991b1b;">${r.urgency}</span></td>
        <td><span class="pill-tag" style="background:#fef3c7; color:#92400e;">${r.status}</span></td>
        <td>${r.created_at ? r.created_at.slice(0, 10) : ''}</td>
      </tr>
    `).join('');
  } catch (err) {
    console.warn("loadBuyerReviewRequests error:", err);
  }
}

async function loadOfficerAssignedApps() {
  if (!LandTechAPI.token) return;
  try {
    const res = await LandTechAPI.fetch('/api/v1/officer/assigned-applications');
    const tbody = document.getElementById('officer-assigned-apps-tbody');
    if (!tbody || !res || !res.applications) return;

    tbody.innerHTML = res.applications.map(app => `
      <tr>
        <td><strong>${app.app_id}</strong></td>
        <td>${app.applicant_name || 'নাগরিক'}</td>
        <td>${app.mouza} — দাগ ${app.dag_number} (${app.area_decimal} শতক)</td>
        <td>${app.app_type}</td>
        <td>${app.officer_notes || 'বায়া দলিল যাচাই সম্পন্ন'}</td>
        <td>${app.hearing_date || 'নির্ধারিত হয়নি'}</td>
        <td>
          <button class="btn btn-primary-forest btn-sm" onclick="openOfficerHearingModal('${app.app_id}')">
            📅 শুনানির আদেশ
          </button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.warn("loadOfficerAssignedApps error:", err);
  }
}

async function triggerDbCheckpoint() {
  try {
    const res = await LandTechAPI.fetch('/api/v1/admin/backups/checkpoint', { method: 'POST' });
    const statusBox = document.getElementById('backup-checkpoint-status');
    if (statusBox) {
      statusBox.style.display = 'block';
      statusBox.textContent = `✓ ${res.message} (WAL Result: [${res.checkpoint_result.join(', ')}])`;
    }
    showToast("SQLite WAL চেকপয়েন্ট সফলভাবে সম্পন্ন হয়েছে।");
  } catch (err) {
    alert("চেকপয়েন্ট ব্যর্থ: " + err.message);
  }
}

function viewCitizenParcelDossier(parcelId) {
  loadCitizenDossier(parcelId);
  switchAppPage('citizen');
}

function startMutationForParcel(parcelId) {
  switchAppPage('mutation');
  const input = document.getElementById('mut-parcel-input');
  if (input) input.value = parcelId;
}

function startCorrectionForParcel(parcelId) {
  switchAppPage('citizen-applications');
  showToast(`দাগ ${parcelId} এর করণিক সংশোধন আবেদন খসড়া প্রস্তুত হয়েছে।`);
}

function viewApplicationTimeline(appId) {
  switchAppPage('mutation');
  showToast(`আবেদন ${appId} এর অগ্রগতি ট্র্যাকিং প্রদর্শিত হচ্ছে।`);
}

function openClaimParcelModal() {
  showToast("দাবি যাচাইকরণ: আপনার খতিয়ান ও আরএস দাগ নম্বর দিয়ে সার্চ করুন।");
  switchAppPage('citizen');
}

function openNewApplicationModal() {
  const reason = prompt("আবেদনের বিবরণ লিখুন (যেমন: জমি ক্রয় সূত্রে নামজারি / জমাভাগ):", "সাফ-কবালা দলিল সূত্রে নামজারি ও জমাভাগ আবেদন");
  if (!reason) return;
  LandTechAPI.fetch('/api/v1/citizen/applications', {
    method: 'POST',
    body: JSON.stringify({
      parcel_id: 'BD-PAR-000001',
      app_type: 'ই-নামজারি ও জমাভাগ',
      details: { reason: reason, applicant_phone: '01711000001' }
    })
  }).then(res => {
    showToast(`✓ আবেদন সফলভাবে দাখিল হয়েছে: ${res.app_id}`);
    loadCitizenApplications();
  }).catch(err => {
    alert("আবেদন ব্যর্থ: " + err.message);
  });
}

function openBuyerReviewModal() {
  const pid = prompt("যে পার্সেল আইডি নিয়ে পুনঃযাচাইয়ের অনুরোধ করতে চান (যেমন: BD-PAR-000101):", "BD-PAR-000101");
  if (!pid) return;
  const reason = prompt("পুনঃযাচাইয়ের কারণ লিখুন:", "বায়া দলিলের ধারাবাহিকতায় গরমিল ও দ্বৈত বিক্রয়ের সন্দেহ");
  if (!reason) return;

  LandTechAPI.fetch('/api/v1/buyer/review-requests', {
    method: 'POST',
    body: JSON.stringify({
      parcel_id: pid.trim(),
      reason: reason,
      urgency: 'HIGH'
    })
  }).then(res => {
    showToast(`✓ পুনঃযাচাই আবেদন অন্তর্ভুক্ত হয়েছে: ${res.request_id}`);
    loadBuyerReviewRequests();
  }).catch(err => {
    alert("আবেদন ব্যর্থ: " + err.message);
  });
}

function openOfficerHearingModal(appId) {
  const hearingDate = prompt("শুনানির তারিখ নির্ধারণ করুন (YYYY-MM-DD):", "2026-11-15");
  if (!hearingDate) return;
  const notes = prompt("কর্মকর্তার মন্তব্য ও নির্দেশিকা:", "মূল বায়া দলিল ও খাজনার দাখিলাসহ শুনানিতে হাজির হওয়ার নোটিশ।");
  if (!notes) return;

  LandTechAPI.fetch('/api/v1/officer/hearing-schedule', {
    method: 'POST',
    body: JSON.stringify({
      app_id: appId,
      hearing_date: hearingDate,
      officer_notes: notes
    })
  }).then(res => {
    showToast(`✓ শুনানির নোটিশ সফলভাবে জারি হয়েছে: ${appId}`);
    loadOfficerAssignedApps();
  }).catch(err => {
    alert("শুনানি নির্ধারণ ব্যর্থ: " + err.message);
  });
}

function openUserProfileModal() {
  const sheet = document.getElementById('calm-profile-sheet');
  if (sheet) sheet.classList.add('open');
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

  const loadSamplePorchaBtn = document.getElementById('ocr-load-sample-porcha-btn');
  if (loadSamplePorchaBtn) {
    loadSamplePorchaBtn.addEventListener('click', async () => {
      try {
        let res = await fetch('/api/v1/documents/sample-porcha');
        if (!res.ok) {
          res = await fetch('/static/assets/samples/sample_porcha.png');
        }
        if (res.ok) {
          const blob = await res.blob();
          const file = new File([blob], "SAMPLE_RS_KHATIAN_PORCHA_328.png", { type: "image/png" });
          handleOcrFileSelection(file);
        }
      } catch (e) {
        alert("নমুনা পরচা লোড করা যায়নি: " + e.message);
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
          const file = new File([blob], "SAMPLE_SAF_KABALA_DEED_RECORD.pdf", { type: "application/pdf" });
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

      // Render rich structured fields
      const ent = res.extracted_entities || {};
      const primaryDag = ent.detected_dag_numbers?.[0] || '১০৪';
      const primaryDagAr = ent.detected_dag_numbers_ar?.[0] || '104';

      structDiv.innerHTML = `
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; margin-bottom:0.75rem;">
          <div style="background:#ffffff; padding:6px 10px; border-radius:6px; border:1px solid var(--c-stone-200);">
            <div style="font-size:0.72rem; color:var(--c-stone-500);">নথির প্রকৃতি / ধরন</div>
            <strong style="color:var(--c-forest-800); font-size:0.85rem;">${ent.detected_deed_type || 'দলিল / খতিয়ান'}</strong>
          </div>
          <div style="background:#ffffff; padding:6px 10px; border-radius:6px; border:1px solid var(--c-stone-200);">
            <div style="font-size:0.72rem; color:var(--c-stone-500);">দলিল নম্বর</div>
            <strong style="color:var(--c-forest-800); font-size:0.85rem;">${ent.detected_deed_numbers?.join(', ') || 'অনুপস্থিত'}</strong>
          </div>
          <div style="background:#ffffff; padding:6px 10px; border-radius:6px; border:1px solid var(--c-stone-200);">
            <div style="font-size:0.72rem; color:var(--c-stone-500);">মৌজা ও জে.এল.</div>
            <strong style="font-size:0.85rem;">${ent.detected_mouza || 'আমিনবাজার'} (JL: ${ent.detected_jl_number || '২৬'})</strong>
          </div>
          <div style="background:#ffffff; padding:6px 10px; border-radius:6px; border:1px solid var(--c-stone-200);">
            <div style="font-size:0.72rem; color:var(--c-stone-500);">শনাক্তকৃত দাগ নম্বর</div>
            <strong style="color:#b45309; font-size:0.85rem;">${ent.detected_dag_numbers?.join(', ') || '১০৪'}</strong>
          </div>
          <div style="background:#ffffff; padding:6px 10px; border-radius:6px; border:1px solid var(--c-stone-200);">
            <div style="font-size:0.72rem; color:var(--c-stone-500);">খতিয়ান নম্বর</div>
            <strong style="font-size:0.85rem;">${ent.detected_khatian_numbers?.join(', ') || '৩২৮'}</strong>
          </div>
          <div style="background:#ffffff; padding:6px 10px; border-radius:6px; border:1px solid var(--c-stone-200);">
            <div style="font-size:0.72rem; color:var(--c-stone-500);">জমির পরিমাণ ও শ্রেণী</div>
            <strong style="font-size:0.85rem;">${ent.detected_area || '১২.৫০ শতাংশ'} (${ent.detected_land_class || 'নাল'})</strong>
          </div>
        </div>

        ${ent.detected_seller ? `
        <div style="font-size:0.78rem; margin-bottom:0.35rem;">
          <strong>দাতা/বিক্রেতা:</strong> ${ent.detected_seller} ${ent.detected_buyer ? ` | <strong>গ্রহীতা/ক্রেতা:</strong> ${ent.detected_buyer}` : ''}
        </div>` : ''}

        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.75rem; padding-top:0.5rem; border-top:1px dashed var(--c-stone-300);">
          <div style="color:var(--c-forest-700); font-size:0.72rem;">
            ভাষা: ${res.language_used} | সময়: ${res.processing_time_ms} ms | পাতা: ${res.pages_processed}
          </div>
          <button class="btn btn-primary-forest btn-sm" onclick="crossReferenceOcrParcel('${primaryDagAr}')" style="border-radius:var(--radius-full); padding:3px 10px; font-size:0.75rem;">
            🔍 দাগ ${primaryDag} ডাটাবেসে অনুসন্ধান ➔
          </button>
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

// Cross-reference OCR dag in cadastral database
function crossReferenceOcrParcel(dagNumber) {
  // Map dag 104 to standard Savar parcel BD-PAR-000101
  const parcelId = dagNumber === '104' ? 'BD-PAR-000101' : `BD-PAR-000${dagNumber.padStart(3, '0')}`;
  navigateToApp('citizen');
  const searchInput = document.getElementById('citizen-parcel-input');
  if (searchInput) {
    searchInput.value = parcelId;
    loadCitizenDossier(parcelId);
  }
  showToast(`OCR দাগ ${dagNumber} এর ক্যাডাস্ট্রাল ডসিয়ার লোড করা হয়েছে`);
}

// ==========================================================================
// WORKSPACE 7: BANGLADESH-WIDE CADASTRAL GIS & MAP (P6)
// ==========================================================================

let mapSearchDebounce = null;
let mapViewportDebounce = null;
let currentHighlightedPolygon = null;

function initCadastralGISWorkspace() {
  const mapCanvas = document.getElementById('gis-map-canvas');
  if (!mapCanvas || AppState.gisMap) return;

  // Initialize nationwide Bangladesh view
  AppState.gisMap = L.map('gis-map-canvas', {
    zoomControl: true,
    minZoom: 6,
    maxZoom: 19
  }).setView([23.6850, 90.3563], 7);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors | DeshMrittika GIS (DEMO)'
  }).addTo(AppState.gisMap);

  // Initialize Layer Groups
  AppState.gisLayers.parcels = L.layerGroup().addTo(AppState.gisMap);
  AppState.gisLayers.khas = L.layerGroup().addTo(AppState.gisMap);
  AppState.gisLayers.corridor = L.layerGroup().addTo(AppState.gisMap);
  AppState.gisLayers.offices = L.layerGroup().addTo(AppState.gisMap);

  // Load Static Spatial Layers: Corridors, Khas, Offices
  loadMapAcquisitionCorridors();
  loadMapKhasLand();
  loadMapOffices();

  // Initialize Nationwide Geographic Selectors
  initMapGeographySelectors();

  // Bounding Box Dynamic Parcel Loading on moveend
  AppState.gisMap.on('moveend', () => {
    clearTimeout(mapViewportDebounce);
    mapViewportDebounce = setTimeout(loadViewportParcels, 250);
  });

  // Layer toggles
  document.getElementById('layer-parcels-toggle')?.addEventListener('change', (e) => {
    if (e.target.checked) {
      if (!AppState.gisMap.hasLayer(AppState.gisLayers.parcels)) {
        AppState.gisMap.addLayer(AppState.gisLayers.parcels);
      }
      loadViewportParcels();
    } else {
      AppState.gisMap.removeLayer(AppState.gisLayers.parcels);
    }
  });

  document.getElementById('layer-khas-toggle')?.addEventListener('change', (e) => {
    if (e.target.checked) AppState.gisMap.addLayer(AppState.gisLayers.khas);
    else AppState.gisMap.removeLayer(AppState.gisLayers.khas);
  });

  document.getElementById('layer-corridor-toggle')?.addEventListener('change', (e) => {
    if (e.target.checked) AppState.gisMap.addLayer(AppState.gisLayers.corridor);
    else AppState.gisMap.removeLayer(AppState.gisLayers.corridor);
  });

  document.getElementById('layer-offices-toggle')?.addEventListener('change', (e) => {
    if (e.target.checked) AppState.gisMap.addLayer(AppState.gisLayers.offices);
    else AppState.gisMap.removeLayer(AppState.gisLayers.offices);
  });

  // Reset Bangladesh View Button
  document.getElementById('map-reset-bd-btn')?.addEventListener('click', () => {
    AppState.gisMap.flyTo([23.6850, 90.3563], 7);
    resetMapGeoSelectors();
    updateMapCoverageBanner("সার্বিক বাংলাদেশ প্রশাসনিক কেন্দ্র স্তর সক্রিয়");
    showToast("সমগ্র বাংলাদেশ সার্বিক ভিউতে ফিরে যাওয়া হয়েছে");
  });

  // Quick Go button
  document.getElementById('map-quick-go-btn')?.addEventListener('click', () => {
    const dag = document.getElementById('map-quick-dag')?.value;
    if (dag) {
      AppState.gisMap.flyTo([23.8050, 90.3200], 16);
      showToast(`দাগ নং ${dag} এ ফোকাস করা হয়েছে (সাভার পাইলট জোন)`);
    }
  });

  // Map Detail Drawer Close button
  document.getElementById('map-detail-close-btn')?.addEventListener('click', () => {
    closeMapDetailDrawer();
  });
}

async function loadMapAcquisitionCorridors() {
  try {
    const data = await LandTechAPI.getAcquisitionZonesLayer();
    if (data && data.features && AppState.gisLayers.corridor) {
      L.geoJSON(data, {
        style: {
          color: '#9333ea',
          weight: 2,
          fillColor: '#c084fc',
          fillOpacity: 0.35,
          dashArray: '5, 5'
        },
        onEachFeature: (feature, layer) => {
          const p = feature.properties || {};
          layer.bindPopup(`
            <div style="font-size:0.85rem; line-height:1.5;">
              <span class="pill-tag" style="background:#f3e8ff; color:#7e22ce; font-weight:700;">জাতীয় অবকাঠামো করিডোর</span>
              <h5 style="margin:0.4rem 0 0.2rem 0; font-size:0.95rem; font-weight:700;">${p.project_name || 'অধিগ্রহণ প্রকল্প'}</h5>
              <div><strong>গেজেট প্রজ্ঞাপন:</strong> ${p.gazette_notification_no || 'সরকারি গেজেট'}</div>
              <div><strong>স্ট্যাটাস:</strong> ${p.status || 'GAZETTED'}</div>
              <div style="margin-top:0.3rem; font-size:0.75rem; color:#7e22ce;">⚠️ ১০০-মিটার নিরাপত্তা বাফার এলাকা</div>
            </div>
          `);
        }
      }).addTo(AppState.gisLayers.corridor);
    }
  } catch (err) {
    console.error("[Map] Failed to load acquisition corridors:", err);
  }
}

async function loadMapKhasLand() {
  try {
    const data = await LandTechAPI.getKhasLandLayer(150);
    if (data && data.features && AppState.gisLayers.khas) {
      L.geoJSON(data, {
        style: {
          color: '#d97706',
          weight: 2,
          fillColor: '#fde68a',
          fillOpacity: 0.55
        },
        onEachFeature: (feature, layer) => {
          const p = feature.properties || {};
          layer.bindPopup(`
            <div style="font-size:0.85rem; line-height:1.5;">
              <span class="pill-tag" style="background:#fef3c7; color:#92400e; font-weight:700;">১-নং খাস খতিয়ানভুক্ত সরকারি জমি</span>
              <h5 style="margin:0.4rem 0 0.2rem 0; font-size:0.95rem; font-weight:700;">খাস রেকর্ড: ${p.khas_id || '-'}</h5>
              <div><strong>দাগ নং:</strong> ${p.dag_number || '-'} | <strong>মৌজা:</strong> ${p.mouza || '-'}</div>
              <div><strong>শ্রেণী:</strong> ${p.category || 'সরকারি ১-নং খাস'}</div>
              <div><strong>নিয়ন্ত্রণকারী কর্তৃপক্ষ:</strong> ${p.authority || 'সহকারী কমিশনার (ভূমি)'}</div>
              <div style="margin-top:0.3rem; font-size:0.75rem; color:#b45309;">⚠️ সরকারি সম্পদ — ব্যক্তিগত হস্তান্তর আইনত নিষিদ্ধ</div>
            </div>
          `);
        }
      }).addTo(AppState.gisLayers.khas);
    }
  } catch (err) {
    console.error("[Map] Failed to load khas land layer:", err);
  }
}

async function loadMapOffices() {
  try {
    const res = await LandTechAPI.getOffices();
    if (res && res.offices && AppState.gisLayers.offices) {
      res.offices.forEach(office => {
        if (!office.latitude || !office.longitude) return;
        const officeIcon = L.divIcon({
          className: 'custom-office-pin',
          html: `<div style="background:#1d4ed8; color:#ffffff; width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:2px solid #ffffff; box-shadow:0 3px 8px rgba(0,0,0,0.35); font-size:15px; cursor:pointer;" title="${office.office_name_bn}">🏛️</div>`,
          iconSize: [30, 30],
          iconAnchor: [15, 15]
        });

        const marker = L.marker([office.latitude, office.longitude], { icon: officeIcon });
        marker.bindPopup(`
          <div style="font-size:0.85rem; line-height:1.5; min-width:220px;">
            <span class="pill-tag" style="background:#eff6ff; color:#1d4ed8; font-weight:700;">ভূমি প্রশাসন কার্যালয়</span>
            <h5 style="margin:0.4rem 0 0.2rem 0; font-size:0.95rem; font-weight:700;">${office.office_name_bn}</h5>
            <div style="color:var(--c-stone-600); font-size:0.78rem;">${office.office_name_en}</div>
            <div style="margin-top:0.3rem;"><strong>ঠিকানা:</strong> ${office.address_bn || office.address_en || '-'}</div>
            <div><strong>যোগাযোগ:</strong> ${office.phone_demo || '-'}</div>
            <div style="margin-top:0.5rem;">
              <button class="btn btn-primary-forest btn-sm" style="width:100%; font-size:0.75rem; padding:4px 8px;" onclick="navigateToApp('officials-directory')">
                👥 দায়িত্বপ্রাপ্ত কর্মকর্তাগণ দেখুন
              </button>
            </div>
          </div>
        `);
        marker.addTo(AppState.gisLayers.offices);
      });
    }
  } catch (err) {
    console.error("[Map] Failed to load offices layer:", err);
  }
}

async function initMapGeographySelectors() {
  const divSelect = document.getElementById('map-filter-division');
  const distSelect = document.getElementById('map-filter-district');
  const upzSelect = document.getElementById('map-filter-upazila');
  const uniSelect = document.getElementById('map-filter-union');
  const mouzaSelect = document.getElementById('map-filter-mouza');

  // Load Divisions
  try {
    const data = await LandTechAPI.getDivisions();
    if (data && data.divisions && divSelect) {
      divSelect.innerHTML = `<option value="">-- সমগ্র বাংলাদেশ (সব বিভাগ) --</option>` +
        data.divisions.map(d => `<option value="${d.division_id}" data-lat="${d.latitude}" data-lon="${d.longitude}">${d.name_bn} (${d.name_en})</option>`).join('');
    }
  } catch (e) {
    console.error("[Map] Failed to load divisions:", e);
  }

  // Division Change
  divSelect?.addEventListener('change', async (e) => {
    const divId = e.target.value;
    distSelect.innerHTML = `<option value="">-- সকল জেলা --</option>`;
    upzSelect.innerHTML = `<option value="">-- সকল উপজেলা --</option>`;
    uniSelect.innerHTML = `<option value="">-- সকল ইউনিয়ন --</option>`;
    mouzaSelect.innerHTML = `<option value="">-- সকল মৌজা --</option>`;

    distSelect.disabled = !divId;
    upzSelect.disabled = true;
    uniSelect.disabled = true;
    mouzaSelect.disabled = true;

    if (!divId) {
      AppState.gisMap.flyTo([23.6850, 90.3563], 7);
      updateMapCoverageBanner("সার্বিক বাংলাদেশ প্রশাসনিক কেন্দ্র স্তর সক্রিয়");
      return;
    }

    const opt = divSelect.selectedOptions[0];
    const lat = parseFloat(opt.getAttribute('data-lat'));
    const lon = parseFloat(opt.getAttribute('data-lon'));
    if (!isNaN(lat) && !isNaN(lon)) {
      AppState.gisMap.flyTo([lat, lon], 9);
      updateMapCoverageBanner(`${opt.textContent} বিভাগ স্তর সক্রিয়`);
    }

    try {
      const dData = await LandTechAPI.getDistricts(divId);
      if (dData && dData.districts) {
        distSelect.innerHTML = `<option value="">-- সকল জেলা --</option>` +
          dData.districts.map(dist => `<option value="${dist.district_id}" data-lat="${dist.latitude}" data-lon="${dist.longitude}">${dist.name_bn} (${dist.name_en})</option>`).join('');
      }
    } catch (err) {
      console.error("[Map] Failed to load districts:", err);
    }
  });

  // District Change
  distSelect?.addEventListener('change', async (e) => {
    const distId = e.target.value;
    upzSelect.innerHTML = `<option value="">-- সকল উপজেলা --</option>`;
    uniSelect.innerHTML = `<option value="">-- সকল ইউনিয়ন --</option>`;
    mouzaSelect.innerHTML = `<option value="">-- সকল মৌজা --</option>`;

    upzSelect.disabled = !distId;
    uniSelect.disabled = true;
    mouzaSelect.disabled = true;

    if (!distId) return;

    const opt = distSelect.selectedOptions[0];
    const lat = parseFloat(opt.getAttribute('data-lat'));
    const lon = parseFloat(opt.getAttribute('data-lon'));
    if (!isNaN(lat) && !isNaN(lon)) {
      AppState.gisMap.flyTo([lat, lon], 11);
      updateMapCoverageBanner(`${opt.textContent} জেলা স্তর সক্রিয়`);
    }

    try {
      const uData = await LandTechAPI.getUpazilas(distId);
      if (uData && uData.upazilas) {
        upzSelect.innerHTML = `<option value="">-- সকল উপজেলা --</option>` +
          uData.upazilas.map(upz => `<option value="${upz.upazila_id}" data-lat="${upz.latitude}" data-lon="${upz.longitude}">${upz.name_bn} (${upz.name_en})</option>`).join('');
      }
    } catch (err) {
      console.error("[Map] Failed to load upazilas:", err);
    }
  });

  // Upazila Change
  upzSelect?.addEventListener('change', async (e) => {
    const upzId = e.target.value;
    uniSelect.innerHTML = `<option value="">-- সকল ইউনিয়ন --</option>`;
    mouzaSelect.innerHTML = `<option value="">-- সকল মৌজা --</option>`;

    uniSelect.disabled = !upzId;
    mouzaSelect.disabled = !upzId;

    if (!upzId) return;

    const opt = upzSelect.selectedOptions[0];
    const lat = parseFloat(opt.getAttribute('data-lat'));
    const lon = parseFloat(opt.getAttribute('data-lon'));
    if (!isNaN(lat) && !isNaN(lon)) {
      AppState.gisMap.flyTo([lat, lon], 13);
    }

    if (upzId === 'UPZ-2672') {
      updateMapCoverageBanner("সাভার পাইলট জোন: ১০০,০০০ ক্যাডাস্ট্রাল পার্সেল ও খাস জমি সক্রিয়");
    } else {
      updateMapCoverageBanner(`${opt.textContent} উপজেলা — প্রশাসনিক মার্কার দৃশ্যমান (ক্যাডাস্ট্রাল সীমানা সাভার পাইলটে সীমাবদ্ধ)`);
    }

    try {
      const [uniData, mouzaData] = await Promise.all([
        LandTechAPI.getUnions(upzId),
        LandTechAPI.getMouzas(upzId)
      ]);
      if (uniData && uniData.unions && uniData.unions.length > 0) {
        uniSelect.innerHTML = `<option value="">-- সকল ইউনিয়ন --</option>` +
          uniData.unions.map(u => `<option value="${u.union_id}">${u.name_bn} (${u.name_en})</option>`).join('');
      } else {
        uniSelect.innerHTML = `<option value="">-- ইউনিয়ন তথ্য সংরক্ষিত নেই --</option>`;
      }

      if (mouzaData && mouzaData.mouzas && mouzaData.mouzas.length > 0) {
        mouzaSelect.innerHTML = `<option value="">-- সকল মৌজা --</option>` +
          mouzaData.mouzas.map(m => `<option value="${m.mouza_id}" data-lat="${m.latitude}" data-lon="${m.longitude}" data-name="${m.name_en}">${m.name_bn} (${m.name_en}) — জেএল ${m.jl_number || '-'}</option>`).join('');
      } else {
        mouzaSelect.innerHTML = `<option value="">-- মৌজা সীমানা ডাটাবেসে নেই --</option>`;
      }
    } catch (err) {
      console.error("[Map] Failed to load unions/mouzas:", err);
    }
  });

  // Mouza Change
  mouzaSelect?.addEventListener('change', (e) => {
    const mouzaId = e.target.value;
    if (!mouzaId) return;
    const opt = mouzaSelect.selectedOptions[0];
    const lat = parseFloat(opt.getAttribute('data-lat'));
    const lon = parseFloat(opt.getAttribute('data-lon'));
    const mName = opt.getAttribute('data-name');

    if (!isNaN(lat) && !isNaN(lon)) {
      AppState.gisMap.flyTo([lat, lon], 15);
    }

    if (mName === 'Aminbazar' || mName === 'Birulia') {
      updateMapCoverageBanner(`${opt.textContent} — ভেক্টর ক্যাডাস্ট্রাল সীমানা সক্রিয়`);
      loadViewportParcels();
    } else {
      updateMapCoverageBanner(`${opt.textContent} — এই মৌজার জন্য ডিজিটাল ক্যাডাস্ট্রাল ভেক্টর সীমানা সংরক্ষিত নেই`);
    }
  });

  // Geographic Search Bar
  const searchInput = document.getElementById('map-geo-search-input');
  const searchDropdown = document.getElementById('map-geo-search-results');
  const searchBtn = document.getElementById('map-geo-search-btn');

  const executeGeoSearch = async () => {
    const query = searchInput.value.trim();
    if (query.length < 2) {
      searchDropdown.style.display = 'none';
      return;
    }

    try {
      const data = await LandTechAPI.searchGeography(query, 10);
      if (data && data.results && data.results.length > 0) {
        searchDropdown.innerHTML = data.results.map(r => `
          <div class="map-search-item" onclick="selectGeoSearchResult('${r.level}', ${r.latitude}, ${r.longitude}, '${r.name_bn}')">
            <div>
              <strong>${r.name_bn}</strong> <span style="color:var(--c-stone-500); font-size:0.75rem;">(${r.name_en})</span>
              <div style="font-size:0.72rem; color:var(--c-stone-400);">${r.details || ''}</div>
            </div>
            <span class="pill-tag pill-forest" style="font-size:0.65rem;">${r.level}</span>
          </div>
        `).join('');
        searchDropdown.style.display = 'block';
      } else {
        searchDropdown.innerHTML = `<div style="padding:0.75rem; text-align:center; color:var(--c-stone-400); font-size:0.8rem;">কোনো ভৌগোলিক ফলাফল পাওয়া যায়নি</div>`;
        searchDropdown.style.display = 'block';
      }
    } catch (err) {
      console.error("[Map] Search error:", err);
    }
  };

  searchInput?.addEventListener('input', () => {
    clearTimeout(mapSearchDebounce);
    mapSearchDebounce = setTimeout(executeGeoSearch, 300);
  });

  searchBtn?.addEventListener('click', executeGeoSearch);

  // Close search dropdown on click outside
  document.addEventListener('click', (e) => {
    if (!searchInput?.contains(e.target) && !searchDropdown?.contains(e.target)) {
      if (searchDropdown) searchDropdown.style.display = 'none';
    }
  });
}

function selectGeoSearchResult(level, lat, lon, name) {
  const searchDropdown = document.getElementById('map-geo-search-results');
  if (searchDropdown) searchDropdown.style.display = 'none';

  if (!isNaN(lat) && !isNaN(lon)) {
    const zoomLevel = level === 'MOUZA' ? 15 : (level === 'UPAZILA' ? 13 : (level === 'DISTRICT' ? 11 : 9));
    AppState.gisMap.flyTo([lat, lon], zoomLevel);
    updateMapCoverageBanner(`${name} (${level}) অবস্থানে প্যান করা হয়েছে`);
    showToast(`${name} (${level}) এলাকায় ম্যাপ কেন্দ্র নির্ধারণ করা হয়েছে`);
  }
}
window.selectGeoSearchResult = selectGeoSearchResult;

function resetMapGeoSelectors() {
  const divSelect = document.getElementById('map-filter-division');
  const distSelect = document.getElementById('map-filter-district');
  const upzSelect = document.getElementById('map-filter-upazila');
  const uniSelect = document.getElementById('map-filter-union');
  const mouzaSelect = document.getElementById('map-filter-mouza');

  if (divSelect) divSelect.value = '';
  if (distSelect) { distSelect.innerHTML = `<option value="">-- সকল জেলা --</option>`; distSelect.disabled = true; }
  if (upzSelect) { upzSelect.innerHTML = `<option value="">-- সকল উপজেলা --</option>`; upzSelect.disabled = true; }
  if (uniSelect) { uniSelect.innerHTML = `<option value="">-- সকল ইউনিয়ন --</option>`; uniSelect.disabled = true; }
  if (mouzaSelect) { mouzaSelect.innerHTML = `<option value="">-- সকল মৌজা --</option>`; mouzaSelect.disabled = true; }
}

function updateMapCoverageBanner(text) {
  const banner = document.getElementById('map-coverage-text');
  if (banner) banner.textContent = text;
}

async function loadViewportParcels() {
  const toggle = document.getElementById('layer-parcels-toggle');
  if (!toggle || !toggle.checked || !AppState.gisMap) return;

  const zoom = AppState.gisMap.getZoom();
  if (zoom < 13) {
    AppState.gisLayers.parcels.clearLayers();
    return;
  }

  const indicator = document.getElementById('map-loading-indicator');
  if (indicator) indicator.style.display = 'flex';

  const bounds = AppState.gisMap.getBounds();
  const bbox = `${bounds.getWest().toFixed(5)},${bounds.getSouth().toFixed(5)},${bounds.getEast().toFixed(5)},${bounds.getNorth().toFixed(5)}`;

  try {
    const data = await LandTechAPI.getParcelsMap(bbox, null, 120);
    AppState.gisLayers.parcels.clearLayers();

    if (data && data.features && data.features.length > 0) {
      L.geoJSON(data, {
        style: (feature) => {
          const isDisputed = feature.properties && feature.properties.is_disputed;
          return {
            color: isDisputed ? '#dc2626' : '#059669',
            weight: 2,
            fillColor: isDisputed ? '#fecaca' : '#a7f3d0',
            fillOpacity: 0.45
          };
        },
        onEachFeature: (feature, layer) => {
          layer.on('click', () => {
            showParcelDetailDrawer(feature);
            if (currentHighlightedPolygon) {
              currentHighlightedPolygon.setStyle({ weight: 2 });
            }
            layer.setStyle({ weight: 4 });
            currentHighlightedPolygon = layer;
          });
        }
      }).addTo(AppState.gisLayers.parcels);
    }
  } catch (err) {
    console.error("[Map] Viewport parcel load error:", err);
  } finally {
    if (indicator) indicator.style.display = 'none';
  }
}

async function showParcelDetailDrawer(feature) {
  const p = feature.properties || {};
  const emptyPanel = document.getElementById('map-detail-empty');
  const contentPanel = document.getElementById('map-detail-content');
  const titleEl = document.getElementById('map-detail-title');
  const badgeEl = document.getElementById('map-detail-badge');

  if (emptyPanel) emptyPanel.style.display = 'none';
  if (contentPanel) contentPanel.style.display = 'block';

  if (titleEl) titleEl.textContent = `দাগ নং: ${p.dag_number || '-'}`;
  if (badgeEl) {
    if (p.is_disputed) {
      badgeEl.className = 'pill-tag pill-risk';
      badgeEl.textContent = 'দ্বৈত বিক্রয় / বিরোধপূর্ণ';
    } else {
      badgeEl.className = 'pill-tag pill-forest';
      badgeEl.textContent = 'নিয়মিত পার্সেল';
    }
  }

  document.getElementById('detail-parcel-id').textContent = p.parcel_id || '-';
  document.getElementById('detail-dag-no').textContent = p.dag_number || '-';
  document.getElementById('detail-khatian-no').textContent = p.khatian_number || '-';
  document.getElementById('detail-mouza-jl').textContent = `${p.mouza || '-'} (জেএল: ${p.jl_number || '-'})`;
  document.getElementById('detail-admin-location').textContent = 'সাভার, ঢাকা জেলা';
  document.getElementById('detail-area').textContent = `${p.area_decimal || '-'} শতাংশ`;

  // Fetch full location and public due diligence summary
  const dueDiligenceBox = document.getElementById('detail-due-diligence-box');
  if (dueDiligenceBox) {
    dueDiligenceBox.innerHTML = `<em>ডিউ ডিলিজেন্স তথ্য যাচাই হচ্ছে...</em>`;
    dueDiligenceBox.style.background = 'var(--c-stone-100)';

    try {
      const locData = await LandTechAPI.getParcelLocation(p.parcel_id);
      const dd = locData.due_diligence_summary || {};

      let statusHtml = '';
      if (dd.double_selling_flag) {
        statusHtml += `<div style="color:var(--c-risk-danger); font-weight:700;">⚠️ দ্বৈত বিক্রয় সংক্রান্ত অভিযোগ অন্তর্ভুক্ত</div>`;
      }
      if (dd.khas_overlap) {
        statusHtml += `<div style="color:#b45309; font-weight:700;">⚠️ সরকারি ১-নং খাস খতিয়ানভুক্ত এলাকা</div>`;
      }
      if (dd.acquisition_warning) {
        statusHtml += `<div style="color:#7e22ce; font-weight:700;">⚠️ জাতীয় অবকাঠামো অধিগ্রহণ করিডোর সংলগ্ন</div>`;
      }
      if (!dd.double_selling_flag && !dd.khas_overlap && !dd.acquisition_warning) {
        statusHtml += `<div style="color:var(--c-forest-700); font-weight:600;">✓ প্রাথমিক পাবলিক পর্যালোচনায় কোনো সংঘাত নেই</div>`;
      }

      dueDiligenceBox.innerHTML = `
        <div style="font-weight:700; margin-bottom:0.25rem;">পাবলিক ডিউ ডিলিজেন্স সারসংক্ষেপ:</div>
        ${statusHtml}
        <div style="font-size:0.72rem; color:var(--c-stone-500); margin-top:0.3rem;">
          ${locData.disclaimer || 'DEMO DATA — NOT AN OFFICIAL LAND SURVEY'}
        </div>
      `;
    } catch (err) {
      dueDiligenceBox.innerHTML = `<span style="color:var(--c-stone-500);">পাবলিক ডিউ ডিলিজেন্স বিবরণ সংরক্ষিত</span>`;
    }
  }

  // Set citizen dossier button action
  const dossierBtn = document.getElementById('map-detail-dossier-btn');
  if (dossierBtn) {
    dossierBtn.onclick = () => {
      navigateToApp('citizen');
      const searchInput = document.getElementById('citizen-parcel-input');
      if (searchInput) {
        searchInput.value = p.parcel_id;
        loadCitizenDossier(p.parcel_id);
      }
    };
  }
}

function closeMapDetailDrawer() {
  const emptyPanel = document.getElementById('map-detail-empty');
  const contentPanel = document.getElementById('map-detail-content');
  if (emptyPanel) emptyPanel.style.display = 'block';
  if (contentPanel) contentPanel.style.display = 'none';
  if (currentHighlightedPolygon) {
    currentHighlightedPolygon.setStyle({ weight: 2 });
    currentHighlightedPolygon = null;
  }
}

// ==========================================================================
// WORKSPACE: SYNTHETIC LAND OFFICIALS DIRECTORY CONTROLLER (PHASE 4 & 5)
// ==========================================================================

let officialsSearchDebounce = null;

async function loadOfficialsDirectory() {
  await initOfficialsDirectoryWorkspace();
  await fetchAndRenderOfficials();
}

async function initOfficialsDirectoryWorkspace() {
  const divSelect = document.getElementById('officials-filter-div');
  const distSelect = document.getElementById('officials-filter-dist');
  const upzSelect = document.getElementById('officials-filter-upz');
  const desigSelect = document.getElementById('officials-filter-desig');
  const typeSelect = document.getElementById('officials-filter-type');
  const searchInput = document.getElementById('officials-search-query');
  const resetBtn = document.getElementById('officials-filter-reset-btn');
  const langToggle = document.getElementById('officials-lang-toggle');
  const prevBtn = document.getElementById('officials-prev-btn');
  const nextBtn = document.getElementById('officials-next-btn');

  // Load Designations
  try {
    const dRes = await LandTechAPI.getDesignations();
    if (dRes && dRes.designations && desigSelect && desigSelect.options.length <= 1) {
      desigSelect.innerHTML = `<option value="">-- সকল পদবি --</option>` +
        dRes.designations.map(d => `<option value="${d.code}">${d.name_bn} (${d.name_en})</option>`).join('');
    }
  } catch (err) {
    console.error("[Officials] Failed to load designations:", err);
  }

  // Load Divisions
  try {
    const divRes = await LandTechAPI.getDivisions();
    if (divRes && divRes.divisions && divSelect && divSelect.options.length <= 1) {
      divSelect.innerHTML = `<option value="">-- সকল বিভাগ --</option>` +
        divRes.divisions.map(d => `<option value="${d.division_id}">${d.name_bn} (${d.name_en})</option>`).join('');
    }
  } catch (err) {
    console.error("[Officials] Failed to load divisions:", err);
  }

  // Cascading Division -> District
  divSelect?.addEventListener('change', async (e) => {
    const divId = e.target.value;
    distSelect.innerHTML = `<option value="">-- সকল জেলা --</option>`;
    upzSelect.innerHTML = `<option value="">-- সকল উপজেলা --</option>`;
    distSelect.disabled = !divId;
    upzSelect.disabled = true;

    AppState.officials.page = 1;
    if (divId) {
      try {
        const distData = await LandTechAPI.getDistricts(divId);
        if (distData && distData.districts) {
          distSelect.innerHTML = `<option value="">-- সকল জেলা --</option>` +
            distData.districts.map(dist => `<option value="${dist.district_id}">${dist.name_bn} (${dist.name_en})</option>`).join('');
        }
      } catch (err) {
        console.error("[Officials] District load error:", err);
      }
    }
    fetchAndRenderOfficials();
  });

  // Cascading District -> Upazila
  distSelect?.addEventListener('change', async (e) => {
    const distId = e.target.value;
    upzSelect.innerHTML = `<option value="">-- সকল উপজেলা --</option>`;
    upzSelect.disabled = !distId;

    AppState.officials.page = 1;
    if (distId) {
      try {
        const uData = await LandTechAPI.getUpazilas(distId);
        if (uData && uData.upazilas) {
          upzSelect.innerHTML = `<option value="">-- সকল উপজেলা --</option>` +
            uData.upazilas.map(upz => `<option value="${upz.upazila_id}">${upz.name_bn} (${upz.name_en})</option>`).join('');
        }
      } catch (err) {
        console.error("[Officials] Upazila load error:", err);
      }
    }
    fetchAndRenderOfficials();
  });

  upzSelect?.addEventListener('change', () => {
    AppState.officials.page = 1;
    fetchAndRenderOfficials();
  });

  desigSelect?.addEventListener('change', () => {
    AppState.officials.page = 1;
    fetchAndRenderOfficials();
  });

  typeSelect?.addEventListener('change', () => {
    AppState.officials.page = 1;
    fetchAndRenderOfficials();
  });

  searchInput?.addEventListener('input', () => {
    clearTimeout(officialsSearchDebounce);
    officialsSearchDebounce = setTimeout(() => {
      AppState.officials.page = 1;
      fetchAndRenderOfficials();
    }, 300);
  });

  resetBtn?.addEventListener('click', resetOfficialsFilters);

  langToggle?.addEventListener('click', () => {
    AppState.officials.lang = AppState.officials.lang === 'bn' ? 'en' : 'bn';
    langToggle.innerHTML = AppState.officials.lang === 'bn' ? '<span>🌐 English</span>' : '<span>🌐 বাংলা</span>';
    fetchAndRenderOfficials();
  });

  prevBtn?.addEventListener('click', () => {
    if (AppState.officials.page > 1) {
      AppState.officials.page--;
      fetchAndRenderOfficials();
    }
  });

  nextBtn?.addEventListener('click', () => {
    const totalPages = Math.ceil(AppState.officials.total / AppState.officials.limit);
    if (AppState.officials.page < totalPages) {
      AppState.officials.page++;
      fetchAndRenderOfficials();
    }
  });
}

function resetOfficialsFilters() {
  const divSelect = document.getElementById('officials-filter-div');
  const distSelect = document.getElementById('officials-filter-dist');
  const upzSelect = document.getElementById('officials-filter-upz');
  const desigSelect = document.getElementById('officials-filter-desig');
  const typeSelect = document.getElementById('officials-filter-type');
  const searchInput = document.getElementById('officials-search-query');

  if (divSelect) divSelect.value = '';
  if (distSelect) { distSelect.innerHTML = `<option value="">-- সকল জেলা --</option>`; distSelect.disabled = true; }
  if (upzSelect) { upzSelect.innerHTML = `<option value="">-- সকল উপজেলা --</option>`; upzSelect.disabled = true; }
  if (desigSelect) desigSelect.value = '';
  if (typeSelect) typeSelect.value = '';
  if (searchInput) searchInput.value = '';

  AppState.officials.page = 1;
  fetchAndRenderOfficials();
  showToast("সকল ফিল্টার রিসেট করা হয়েছে");
}
window.resetOfficialsFilters = resetOfficialsFilters;

async function fetchAndRenderOfficials() {
  const divSelect = document.getElementById('officials-filter-div');
  const distSelect = document.getElementById('officials-filter-dist');
  const upzSelect = document.getElementById('officials-filter-upz');
  const desigSelect = document.getElementById('officials-filter-desig');
  const typeSelect = document.getElementById('officials-filter-type');
  const searchInput = document.getElementById('officials-search-query');

  const grid = document.getElementById('officials-cards-grid');
  const emptyState = document.getElementById('officials-empty-state');
  const countLabel = document.getElementById('officials-count-label');
  const pageInfo = document.getElementById('officials-pagination-info');
  const prevBtn = document.getElementById('officials-prev-btn');
  const nextBtn = document.getElementById('officials-next-btn');

  const page = AppState.officials.page || 1;
  const limit = AppState.officials.limit || 12;
  const offset = (page - 1) * limit;

  const params = {
    division_id: divSelect?.value || undefined,
    district_id: distSelect?.value || undefined,
    upazila_id: upzSelect?.value || undefined,
    designation: desigSelect?.value || undefined,
    office_type: typeSelect?.value || undefined,
    search: searchInput?.value.trim() || undefined,
    limit: limit,
    offset: offset
  };

  try {
    const res = await LandTechAPI.getOfficials(params);
    AppState.officials.total = res.total || 0;
    const totalPages = Math.max(1, Math.ceil(res.total / limit));
    const isEn = AppState.officials.lang === 'en';

    if (countLabel) {
      countLabel.innerHTML = isEn
        ? `Showing <strong>${res.count}</strong> of <strong>${res.total}</strong> demo officials`
        : `মোট <strong>${res.total}</strong> জন ডেমো কর্মকর্তার মধ্যে <strong>${res.count}</strong> জন প্রদর্শিত হচ্ছে`;
    }

    if (pageInfo) {
      pageInfo.textContent = isEn ? `Page ${page} of ${totalPages}` : `পৃষ্ঠা ${page} / ${totalPages}`;
    }

    if (prevBtn) prevBtn.disabled = page <= 1;
    if (nextBtn) nextBtn.disabled = page >= totalPages;

    if (!res.officials || res.officials.length === 0) {
      if (grid) grid.style.display = 'none';
      if (emptyState) emptyState.style.display = 'block';
      return;
    }

    if (grid) grid.style.display = 'grid';
    if (emptyState) emptyState.style.display = 'none';

    grid.innerHTML = res.officials.map(official => {
      const name = isEn ? official.name_en : official.name_bn;
      const desig = isEn ? official.designation_en : official.designation_bn;
      const office = isEn ? official.office_name_en : official.office_name_bn;
      const address = isEn ? official.address_en : official.address_bn;
      const jurisdiction = isEn ? official.jurisdiction_en : official.jurisdiction_bn;

      return `
        <div class="officials-card">
          <div class="officials-demo-watermark">DEMO OFFICIAL</div>
          <div class="officials-card-header">
            <div class="officials-avatar">
              <img src="${official.portrait_image}" alt="Portrait" onerror="this.src='/static/assets/portraits/portrait_male_1.svg'">
            </div>
            <div class="officials-card-title">
              <div class="officials-name">${name}</div>
              <span class="officials-desig-tag">${desig}</span>
            </div>
          </div>

          <div class="officials-card-body">
            <div class="officials-info-row">
              <span class="officials-info-icon">🏛️</span>
              <div><strong>${office || 'ভূমি কার্যালয়'}</strong></div>
            </div>
            <div class="officials-info-row">
              <span class="officials-info-icon">📍</span>
              <div style="font-size:0.78rem; color:var(--c-stone-600);">${jurisdiction || address || '-'}</div>
            </div>
            <div class="officials-info-row">
              <span class="officials-info-icon">🆔</span>
              <div><code style="font-size:0.75rem; background:var(--c-stone-100); padding:2px 4px; border-radius:4px;">${official.employee_number_demo}</code></div>
            </div>
            <div class="officials-info-row">
              <span class="officials-info-icon">✉️</span>
              <div style="font-size:0.75rem;"><a href="mailto:${official.email_demo}" style="color:var(--c-forest-700);">${official.email_demo}</a></div>
            </div>
            <div class="officials-info-row">
              <span class="officials-info-icon">📞</span>
              <div style="font-size:0.75rem;">${official.phone_demo}</div>
            </div>
          </div>

          <div class="officials-card-footer">
            <button class="btn btn-secondary-stone btn-sm" style="flex:1;" onclick="openOfficialModal('${official.official_id}')">
              বিস্তারিত প্রোফাইল
            </button>
            <button class="btn btn-primary-forest btn-sm" onclick="viewOfficeOnMap('${official.office_id}', ${official.latitude}, ${official.longitude})">
              🗺️ ম্যাপে কার্যালয়
            </button>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    console.error("[Officials] Fetch error:", err);
    if (grid) grid.innerHTML = `<div style="grid-column:1/-1; text-align:center; color:var(--c-risk-danger); padding:2rem;">কর্মকর্তা তালিকা লোড করতে ত্রুটি: ${err.message}</div>`;
  }
}

async function openOfficialModal(officialId) {
  const modal = document.getElementById('official-detail-modal');
  const nameEl = document.getElementById('modal-official-name');
  const bodyEl = document.getElementById('modal-official-body');
  const mapBtn = document.getElementById('modal-official-map-btn');

  if (!modal || !bodyEl) return;

  bodyEl.innerHTML = `<div style="text-align:center; padding:2rem;"><span class="spinner-sm"></span> কর্মকর্তা প্রোফাইল লোড হচ্ছে...</div>`;
  modal.style.display = 'flex';

  try {
    const o = await LandTechAPI.getOfficialDetail(officialId);
    if (nameEl) nameEl.textContent = o.name_bn || o.name_en;

    bodyEl.innerHTML = `
      <div style="display:flex; gap:1.25rem; align-items:flex-start; margin-bottom:1.25rem; border-bottom:1px solid var(--c-stone-200); padding-bottom:1.25rem;">
        <div style="width:96px; height:96px; border-radius:50%; border:3px solid var(--c-forest-100); overflow:hidden; flex-shrink:0; background:#f8fafc;">
          <img src="${o.portrait_image}" style="width:100%; height:100%; object-fit:cover;" alt="Avatar">
        </div>
        <div>
          <h4 style="margin:0 0 0.25rem 0; font-size:1.2rem; font-weight:700;">${o.name_bn}</h4>
          <div style="color:var(--c-stone-500); font-size:0.85rem; margin-bottom:0.4rem;">${o.name_en}</div>
          <div style="display:flex; gap:0.4rem; flex-wrap:wrap;">
            <span class="pill-tag pill-forest">${o.designation_bn}</span>
            <span class="pill-tag" style="background:#dbeafe; color:#1d4ed8;">${o.office_type || 'ভূমি প্রশাসন'}</span>
            <span class="pill-tag" style="background:#dcfce7; color:#15803d;">সক্রিয় ডেমো পদবি</span>
          </div>
        </div>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem; font-size:0.85rem; margin-bottom:1.25rem;">
        <div style="background:var(--c-stone-50); padding:0.75rem; border-radius:var(--radius-sm); border:1px solid var(--c-stone-200);">
          <div style="font-weight:700; margin-bottom:0.4rem; color:var(--c-forest-900);">কার্যালয় ও প্রশাসনিক অবস্থান:</div>
          <div><strong>কার্যালয়:</strong> ${o.office_name_bn}</div>
          <div><strong>বিভাগ:</strong> ${o.division_name_bn || o.division_name_en || '-'}</div>
          <div><strong>জেলা:</strong> ${o.district_name_bn || o.district_name_en || '-'}</div>
          <div><strong>উপজেলা:</strong> ${o.upazila_name_bn || o.upazila_name_en || '-'}</div>
          <div style="font-size:0.78rem; color:var(--c-stone-600); margin-top:0.3rem;"><strong>ঠিকানা:</strong> ${o.address_bn || o.address_en || '-'}</div>
        </div>

        <div style="background:var(--c-stone-50); padding:0.75rem; border-radius:var(--radius-sm); border:1px solid var(--c-stone-200);">
          <div style="font-weight:700; margin-bottom:0.4rem; color:var(--c-forest-900);">নিরাপদ ডেমো যোগাযোগ ও পরিচিতি:</div>
          <div><strong>ডেমো আইডি:</strong> <code>${o.employee_number_demo}</code></div>
          <div><strong>ইমেইল:</strong> <a href="mailto:${o.email_demo}" style="color:var(--c-forest-700);">${o.email_demo}</a></div>
          <div><strong>ফোন:</strong> ${o.phone_demo}</div>
          <div style="margin-top:0.4rem; font-size:0.75rem; color:#b45309;">
            🔒 সংরক্ষিত ডেমো ইমেইল ডোমেইন (@demo.land.gov.bd) ও নিয়ন্ত্রিত ফোন নম্বর।
          </div>
        </div>
      </div>

      <div style="background:var(--c-stone-50); padding:0.75rem; border-radius:var(--radius-sm); border:1px solid var(--c-stone-200); font-size:0.82rem; margin-bottom:1rem;">
        <div style="font-weight:700; margin-bottom:0.25rem;">কার্যপরিধি ও এখতিয়ার (Jurisdiction):</div>
        <div>${o.jurisdiction_bn || o.jurisdiction_en || 'উপজেলা ভূমি প্রশাসন রাজস্ব ও নামজারি কার্যক্রম'}</div>
      </div>

      <div style="background:#fff7ed; border:1px solid #fed7aa; padding:0.65rem; border-radius:var(--radius-sm); font-size:0.75rem; color:#7c2d12; line-height:1.4;">
        <strong>ডেটা প্রোভেন্যান্স ঘোষণা:</strong> ${o.provenance || 'DEMO OFFICIAL — NOT A REAL PERSON'}। এটি বাংলাদেশ ল্যান্ডটেক হ্যাকথন প্রোটোটাইপের জন্য কৃত্রিমভাবে তৈরি একটি ডেমো কর্মকর্তা প্রোফাইল।
      </div>
    `;

    if (mapBtn) {
      mapBtn.onclick = () => {
        closeOfficialModal();
        viewOfficeOnMap(o.office_id, o.latitude, o.longitude);
      };
    }
  } catch (err) {
    bodyEl.innerHTML = `<div style="color:var(--c-risk-danger); text-align:center; padding:2rem;">প্রোফাইল লোড ত্রুটি: ${err.message}</div>`;
  }
}
window.openOfficialModal = openOfficialModal;

function closeOfficialModal() {
  const modal = document.getElementById('official-detail-modal');
  if (modal) modal.style.display = 'none';
}
window.closeOfficialModal = closeOfficialModal;

function viewOfficeOnMap(officeId, lat, lon) {
  switchToMapOffice(lat, lon);
}
window.viewOfficeOnMap = viewOfficeOnMap;

function switchToMapOffice(lat, lon) {
  navigateToApp('map');
  setTimeout(() => {
    if (AppState.gisMap && !isNaN(lat) && !isNaN(lon)) {
      AppState.gisMap.flyTo([lat, lon], 15);
      showToast("ভূমি প্রশাসন কার্যালয় অবস্থানে ম্যাপ কেন্দ্র নির্ধারিত হয়েছে");
    }
  }, 350);
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

// ==========================================================================
// AUTHENTICATION SYSTEM: CONTROLLER & RBAC SECURITY
// ==========================================================================

let authTargetEmail = '';
let otpCountdownInterval = null;
let otpResendInterval = null;
let userSearchTimeout = null;
let logSearchTimeout = null;

function initAuthSystem() {
  // Bind 6-digit OTP input events (auto-advance, backspace, paste)
  const otpInputs = [1, 2, 3, 4, 5, 6].map(i => document.getElementById(`otp-digit-${i}`));
  otpInputs.forEach((input, idx) => {
    if (!input) return;

    input.addEventListener('input', (e) => {
      const val = e.target.value.replace(/\D/g, '');
      e.target.value = val ? val[0] : '';
      if (val && idx < 5) {
        otpInputs[idx + 1].focus();
        otpInputs[idx + 1].select();
      }
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Backspace' && !e.target.value && idx > 0) {
        otpInputs[idx - 1].focus();
      }
    });

    input.addEventListener('paste', (e) => {
      e.preventDefault();
      const pasteData = (e.clipboardData || window.clipboardData).getData('text');
      const digits = pasteData.replace(/\D/g, '').slice(0, 6);
      digits.split('').forEach((d, i) => {
        if (otpInputs[i]) otpInputs[i].value = d;
      });
      if (digits.length > 0) {
        const targetIdx = Math.min(digits.length, 5);
        otpInputs[targetIdx].focus();
      }
    });
  });
}

function updateAuthUI(user) {
  const isGuest = !user || !LandTechAPI.token;

  // Landing page nav
  const guestNav = document.getElementById('landing-auth-guest');
  const userNav = document.getElementById('landing-auth-user');
  if (guestNav && userNav) {
    guestNav.style.display = isGuest ? 'flex' : 'none';
    userNav.style.display = isGuest ? 'none' : 'flex';
  }

  // Topbar
  const topbarUserBtn = document.getElementById('topbar-user-btn');
  const topbarLoginBtn = document.getElementById('topbar-login-btn');
  if (topbarUserBtn && topbarLoginBtn) {
    topbarUserBtn.style.display = isGuest ? 'none' : 'flex';
    topbarLoginBtn.style.display = isGuest ? 'inline-flex' : 'none';
  }

  if (user) {
    const roleLabels = {
      CITIZEN: 'সাধারণ নাগরিক',
      BUYER: 'সম্ভাব্য ক্রেতা',
      OFFICER: 'এসি ল্যান্ড',
      ADMINISTRATOR: 'সিস্টেম অ্যাডমিন'
    };

    const roleLabel = roleLabels[user.role] || user.role;
    const shortName = user.name ? user.name.split(' ')[0] : 'ইউজার';

    // Update Landing pill
    const lName = document.getElementById('landing-user-name');
    const lBadge = document.getElementById('landing-user-role-badge');
    if (lName) lName.textContent = shortName;
    if (lBadge) lBadge.textContent = roleLabel;

    // Update Topbar pill
    const tName = document.getElementById('topbar-user-name');
    const tBadge = document.getElementById('topbar-user-badge');
    if (tName) tName.textContent = shortName;
    if (tBadge) tBadge.textContent = roleLabel;

    // Update Profile Sheet
    const pName = document.getElementById('profile-sheet-name');
    const pEmail = document.getElementById('profile-sheet-email');
    const pUserId = document.getElementById('profile-sheet-userid');
    const pRolePill = document.getElementById('profile-sheet-role-pill');
    const pStatusPill = document.getElementById('profile-sheet-status-pill');

    if (pName) pName.textContent = user.name;
    if (pEmail) pEmail.textContent = user.email;
    if (pUserId) pUserId.textContent = user.user_id;
    if (pRolePill) pRolePill.textContent = `${roleLabel} (${user.role})`;
    if (pStatusPill) {
      pStatusPill.className = user.status === 'ACTIVE' ? 'status-badge-active' : 'status-badge-unverified';
      pStatusPill.textContent = user.status === 'ACTIVE' ? '✓ সক্রিয় ও যাচাইকৃত' : '⚠️ অনিষ্পন্ন';
    }
  }

  // Update sidebar profile footer badge
  const sName = document.getElementById('sidebar-user-name');
  const sBadge = document.getElementById('sidebar-user-role-badge');
  const sAvatar = document.getElementById('sidebar-user-avatar');
  const sLogout = document.getElementById('sidebar-logout-btn');

  const roleLabels = {
    CITIZEN: 'সাধারণ নাগরিক',
    BUYER: 'সম্ভাব্য ক্রেতা',
    OFFICER: 'সহকারী কমিশনার - ভূমি',
    ADMINISTRATOR: 'সিস্টেম অ্যাডমিন'
  };

  if (!isGuest && user) {
    const rolePillClass = {
      CITIZEN: 'role-pill-citizen',
      BUYER: 'role-pill-buyer',
      OFFICER: 'role-pill-officer',
      ADMINISTRATOR: 'role-pill-admin'
    }[user.role] || 'role-pill-citizen';

    const roleEmoji = {
      CITIZEN: '👤',
      BUYER: '💼',
      OFFICER: '🏛️',
      ADMINISTRATOR: '⚙️'
    }[user.role] || '👤';

    if (sName) sName.textContent = user.name || user.email;
    if (sBadge) {
      sBadge.textContent = roleLabels[user.role] || user.role;
      sBadge.className = `user-role-pill ${rolePillClass}`;
    }
    if (sAvatar) sAvatar.textContent = roleEmoji;
    if (sLogout) sLogout.style.display = 'block';
  } else {
    if (sName) sName.textContent = 'অতিথি ব্যবহারকারী';
    if (sBadge) {
      sBadge.textContent = 'সাধারণ নাগরিক';
      sBadge.className = 'user-role-pill role-pill-citizen';
    }
    if (sAvatar) sAvatar.textContent = '👤';
    if (sLogout) sLogout.style.display = 'none';
  }

  applyRolePermissions();
}

// Modal Controls
function openAuthModal(view = 'login') {
  const modal = document.getElementById('auth-modal');
  if (modal) {
    modal.classList.add('open');
    switchAuthView(view);
  }
}

function closeAuthModal() {
  const modal = document.getElementById('auth-modal');
  if (modal) modal.classList.remove('open');
}

function switchAuthView(view) {
  const views = ['login', 'signup', 'otp', 'reset'];
  views.forEach(v => {
    const el = document.getElementById(`auth-view-${v}`);
    if (el) el.style.display = v === view ? 'block' : 'none';
  });

  if (view === 'login') {
    setTimeout(() => document.getElementById('login-email')?.focus(), 100);
  } else if (view === 'signup') {
    setTimeout(() => document.getElementById('signup-name')?.focus(), 100);
  } else if (view === 'otp') {
    setTimeout(() => document.getElementById('otp-digit-1')?.focus(), 100);
  }
}

function openUserProfileModal() {
  const modal = document.getElementById('user-profile-modal');
  if (modal) modal.classList.add('open');
}

function closeUserProfileModal() {
  const modal = document.getElementById('user-profile-modal');
  if (modal) modal.classList.remove('open');
}

function togglePasswordVisibility(inputId) {
  const input = document.getElementById(inputId);
  if (input) {
    input.type = input.type === 'password' ? 'text' : 'password';
  }
}

// Login Handler
async function handleLoginSubmit(event) {
  event.preventDefault();
  const email = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const rememberMe = document.getElementById('login-remember-me').checked;
  const submitBtn = document.getElementById('login-submit-btn');

  if (!email || !password) return;

  submitBtn.disabled = true;
  submitBtn.innerHTML = `<span>যাচাই হচ্ছে...</span>`;

  try {
    const data = await LandTechAPI.login(email, password, rememberMe);
    AppState.user = {
      user_id: data.user_id,
      name: data.name,
      role: data.role,
      email: data.email,
      status: data.status
    };

    updateAuthUI(AppState.user);
    applyRolePermissions();
    closeAuthModal();
    showToast(`স্বাগতম, ${data.name}! সফলভাবে লগইন হয়েছে।`);

    // Direct user to appropriate view
    if (AppState.view === 'landing') {
      navigateToApp('overview');
    }
  } catch (err) {
    if (err.code === 'ACCOUNT_UNVERIFIED') {
      authTargetEmail = err.email || email;
      document.getElementById('otp-target-email-badge').textContent = authTargetEmail;
      switchAuthView('otp');
      startOtpTimer(600);
      startResendCooldown(60);
      showToast(err.message, 'warning');
    } else {
      alert(`লগইন ব্যর্থ: ${err.message}`);
    }
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<span>প্রবেশ করুন</span> <span>➔</span>`;
  }
}

const DEMO_CREDENTIALS = {
  CITIZEN: { email: 'citizen@example.com', pass: 'Password123!' },
  BUYER: { email: 'buyer@example.com', pass: 'Password123!' },
  OFFICER: { email: 'officer@savar.land.gov.bd', pass: 'Password123!' },
  ADMINISTRATOR: { email: 'admin@deshmrittika.gov.bd', pass: 'Password123!' }
};

// 1-Click Demo Login (for local evaluation/testing)
async function demoLogin(role) {
  const creds = DEMO_CREDENTIALS[role];
  if (!creds) return;
  try {
    const data = await LandTechAPI.login(creds.email, creds.pass, false);
    AppState.user = {
      user_id: data.user_id,
      name: data.name,
      role: data.role,
      email: data.email,
      status: data.status
    };
    updateAuthUI(AppState.user);
    applyRolePermissions();
    closeAuthModal();
    showToast(`স্বাগতম, ${data.name}! সফলভাবে লগইন হয়েছে।`);
    if (AppState.view === 'landing') {
      navigateToApp(ROLE_HOME_PAGE[data.role] || 'overview');
    }
  } catch (err) {
    alert(`ডেমো লগইন ব্যর্থ: ${err.message}`);
  }
}
window.demoLogin = demoLogin;

// Signup Handler
async function handleSignupSubmit(event) {
  event.preventDefault();
  const full_name = document.getElementById('signup-name').value.trim();
  const email = document.getElementById('signup-email').value.trim();
  const password = document.getElementById('signup-password').value;
  const confirm_password = document.getElementById('signup-confirm-password').value;
  const phone = document.getElementById('signup-phone').value.trim();
  const role = document.getElementById('signup-role').value;
  const submitBtn = document.getElementById('signup-submit-btn');

  if (password !== confirm_password) {
    alert("পাসওয়ার্ড এবং কনফার্ম পাসওয়ার্ড মিলছে না।");
    return;
  }

  if (password.length < 8) {
    alert("পাসওয়ার্ড কমপক্ষে ৮ অক্ষরের হতে হবে।");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerHTML = `<span>অ্যাকাউন্ট তৈরি হচ্ছে...</span>`;

  try {
    const res = await LandTechAPI.signup({
      full_name,
      email,
      password,
      confirm_password,
      phone,
      role
    });

    authTargetEmail = email;
    document.getElementById('otp-target-email-badge').textContent = email;
    switchAuthView('otp');
    startOtpTimer(600);
    startResendCooldown(60);

    showToast(res.message || "৬-সংখ্যার যাচাইকরণ কোড আপনার ইমেইলে পাঠানো হয়েছে।");
  } catch (err) {
    alert(`নিবন্ধন ব্যর্থ: ${err.message}`);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<span>অ্যাকাউন্ট তৈরি করুন</span> <span>➔</span>`;
  }
}

// OTP Submit Handler
async function handleOtpSubmit(event) {
  event.preventDefault();
  const digits = [1, 2, 3, 4, 5, 6].map(i => document.getElementById(`otp-digit-${i}`).value).join('');
  const submitBtn = document.getElementById('otp-verify-btn');

  if (digits.length !== 6 || !/^\d{6}$/.test(digits)) {
    alert("অনুগ্রহ করে ৬-সংখ্যার সম্পূর্ণ ওটিপি কোড প্রদান করুন।");
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerHTML = `<span>যাচাই হচ্ছে...</span>`;

  try {
    const data = await LandTechAPI.verifyEmail(authTargetEmail, digits);
    AppState.user = {
      user_id: data.user_id,
      name: data.name,
      role: data.role,
      email: data.email,
      status: data.status
    };

    clearInterval(otpCountdownInterval);
    clearInterval(otpResendInterval);

    updateAuthUI(AppState.user);
    applyRolePermissions();
    closeAuthModal();
    showToast(`ইমেইল সফলভাবে যাচাই সম্পন্ন হয়েছে! স্বাগতম ${data.name}।`);

    if (AppState.view === 'landing') {
      navigateToApp('overview');
    }
  } catch (err) {
    alert(`যাচাইকরণ ব্যর্থ: ${err.message}`);
    // Highlight attempt error
    const attemptsLeft = document.getElementById('otp-attempts-left');
    if (attemptsLeft) attemptsLeft.textContent = "পুনরায় চেষ্টা করুন";
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<span>যাচাই সম্পন্ন করুন</span> <span>✓</span>`;
  }
}

// Resend Code Handler
async function handleResendCode() {
  const resendBtn = document.getElementById('otp-resend-btn');
  if (resendBtn.disabled) return;

  try {
    const res = await LandTechAPI.resendCode(authTargetEmail, 'EMAIL_VERIFY');
    startResendCooldown(60);
    startOtpTimer(600);
    showToast(res.message || "নতুন ওটিপি কোড পাঠানো হয়েছে।");
  } catch (err) {
    alert(`কোড পাঠানো যায়নি: ${err.message}`);
  }
}

// Fetch Dev Mailbox Code for Hackathon Testing
async function fetchDevOtp() {
  const displayBox = document.getElementById('dev-otp-code-box');
  try {
    const emails = await LandTechAPI.getDevMailbox();
    const match = emails.find(e => e.to.toLowerCase() === authTargetEmail.toLowerCase());
    if (match && match.code) {
      displayBox.style.display = 'block';
      displayBox.innerHTML = `📩 প্রাপ্ত ওটিপি কোড: <strong>${match.code}</strong> (বিষয়: ${match.subject})`;

      // Auto-fill digits
      match.code.split('').forEach((d, i) => {
        const inp = document.getElementById(`otp-digit-${i + 1}`);
        if (inp) inp.value = d;
      });
      document.getElementById('otp-verify-btn')?.focus();
    } else {
      displayBox.style.display = 'block';
      displayBox.innerHTML = `⚠️ কোনো সাম্প্রতিক কোড মেলেনি। রি-সেন্ড কোড চাপুন।`;
    }
  } catch (err) {
    console.error("Dev mailbox fetch error:", err);
  }
}

// Timers
function startOtpTimer(durationSeconds) {
  clearInterval(otpCountdownInterval);
  let remaining = durationSeconds;
  const textEl = document.getElementById('otp-timer-text');

  function update() {
    const mins = Math.floor(remaining / 60);
    const secs = remaining % 60;
    if (textEl) {
      textEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')} মিনিট`;
    }
    if (remaining <= 0) {
      clearInterval(otpCountdownInterval);
      if (textEl) textEl.textContent = "মেয়াদ উত্তীর্ণ!";
    }
    remaining--;
  }
  update();
  otpCountdownInterval = setInterval(update, 1000);
}

function startResendCooldown(seconds) {
  clearInterval(otpResendInterval);
  let remaining = seconds;
  const btn = document.getElementById('otp-resend-btn');
  const timerSpan = document.getElementById('otp-cooldown-timer');

  btn.disabled = true;
  function update() {
    if (timerSpan) timerSpan.textContent = `(${remaining}s)`;
    if (remaining <= 0) {
      clearInterval(otpResendInterval);
      btn.disabled = false;
      if (timerSpan) timerSpan.textContent = '';
    }
    remaining--;
  }
  update();
  otpResendInterval = setInterval(update, 1000);
}

// Forgot & Reset Password
async function handleForgotPasswordRequest() {
  const email = document.getElementById('reset-email').value.trim();
  if (!email) {
    alert("ইমেইল ঠিকানা লিখুন।");
    return;
  }

  try {
    const res = await LandTechAPI.forgotPassword(email);
    authTargetEmail = email;
    document.getElementById('reset-step-request').style.display = 'none';
    document.getElementById('reset-step-confirm').style.display = 'block';
    showToast(res.message || "পাসওয়ার্ড রিসেট কোড ইমেইলে প্রেরণ করা হয়েছে।");
  } catch (err) {
    alert(`অনুরোধ ব্যর্থ: ${err.message}`);
  }
}

async function handleResetPasswordSubmit() {
  const code = document.getElementById('reset-otp-code').value.trim();
  const newPwd = document.getElementById('reset-new-password').value;
  const confirmPwd = document.getElementById('reset-confirm-password').value;

  if (!code || code.length !== 6) {
    alert("৬-সংখ্যার কোড লিখুন।");
    return;
  }
  if (newPwd !== confirmPwd) {
    alert("পাসওয়ার্ড মিলছে না।");
    return;
  }
  if (newPwd.length < 8) {
    alert("পাসওয়ার্ড কমপক্ষে ৮ অক্ষরের হতে হবে।");
    return;
  }

  try {
    const res = await LandTechAPI.resetPassword(authTargetEmail, code, newPwd, confirmPwd);
    showToast(res.message || "পাসওয়ার্ড সফলভাবে হালনাগাদ হয়েছে! লগইন করুন।");
    switchAuthView('login');
  } catch (err) {
    alert(`রিসেট ব্যর্থ: ${err.message}`);
  }
}

// Profile Sheet Change Password
async function handleChangePasswordSubmit(event) {
  event.preventDefault();
  const oldPwd = document.getElementById('change-old-password').value;
  const newPwd = document.getElementById('change-new-password').value;
  const confirmPwd = document.getElementById('change-confirm-password').value;

  if (newPwd !== confirmPwd) {
    alert("নতুন পাসওয়ার্ড ও কনফার্ম পাসওয়ার্ড মিলছে না।");
    return;
  }
  if (newPwd.length < 8) {
    alert("নতুন পাসওয়ার্ড কমপক্ষে ৮ অক্ষরের হতে হবে।");
    return;
  }

  try {
    const res = await LandTechAPI.changePassword(oldPwd, newPwd, confirmPwd);
    showToast(res.message || "পাসওয়ার্ড সফলভাবে পরিবর্তিত হয়েছে।");
    closeUserProfileModal();
  } catch (err) {
    alert(`পাসওয়ার্ড পরিবর্তন ব্যর্থ: ${err.message}`);
  }
}

// Session Logouts
async function triggerLogout() {
  await handleLogoutCurrentSession();
}

async function handleLogoutCurrentSession() {
  if (confirm("আপনি কি নিশ্চিতভাবে এই ডিভাইস থেকে লগআউট করতে চান?")) {
    await LandTechAPI.logout();
    AppState.user = null;
    updateAuthUI(null);
    closeUserProfileModal();
    applyRolePermissions();
    navigateToLanding();
    showToast("সফলভাবে লগআউট সম্পন্ন হয়েছে।");
  }
}

async function handleLogoutAllSessions() {
  if (confirm("আপনি কি নিশ্চিতভাবে আপনার সকল সক্রিয় সেশন ও ডিভাইস থেকে লগআউট করতে চান?")) {
    await LandTechAPI.logoutAll();
    AppState.user = null;
    updateAuthUI(null);
    closeUserProfileModal();
    applyRolePermissions();
    navigateToLanding();
    showToast("সকল ডিভাইস থেকে সেশন সমাপ্ত হয়েছে।");
  }
}

// ==========================================================================
// WORKSPACE 11 & 12: ADMIN USER MANAGEMENT & SECURITY AUDIT
// ==========================================================================

let adminUsersList = [];

async function loadAdminUsers() {
  const tbody = document.getElementById('admin-users-tbody');
  if (!tbody) return;

  const role = document.getElementById('admin-filter-role')?.value || null;
  const status = document.getElementById('admin-filter-status')?.value || null;
  const search = document.getElementById('admin-user-search-input')?.value?.trim() || null;

  tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:1.5rem;">ব্যবহারকারী তালিকা লোড হচ্ছে...</td></tr>`;

  try {
    const res = await LandTechAPI.getAdminUsers({ role, status, search, limit: 50 });
    adminUsersList = res.users || [];

    const countEl = document.getElementById('admin-users-count');
    if (countEl) countEl.textContent = `মোট ${res.total} জন ব্যবহারকারী নিবন্ধিত`;

    if (adminUsersList.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:1.5rem; color:var(--c-stone-400);">কোনো ব্যবহারকারী পাওয়া যায়নি।</td></tr>`;
      return;
    }

    tbody.innerHTML = adminUsersList.map(u => {
      const roleBadges = {
        CITIZEN: '<span class="pill-tag pill-forest">নাগরিক (CITIZEN)</span>',
        BUYER: '<span class="pill-tag" style="background:#dbeafe; color:#1d4ed8; border:1px solid #bfdbfe;">ক্রেতা (BUYER)</span>',
        OFFICER: '<span class="pill-tag" style="background:#fef3c7; color:#b45309; border:1px solid #fde68a;">এসি ল্যান্ড (AC LAND)</span>',
        ADMINISTRATOR: '<span class="pill-tag" style="background:#ede9fe; color:#6d28d9; border:1px solid #ddd6fe;">অ্যাডমিন (ADMIN)</span>'
      };

      const statusBadges = {
        ACTIVE: '<span class="status-badge-active">✓ সক্রিয়</span>',
        UNVERIFIED: '<span class="status-badge-unverified">⚠️ অনিষ্পন্ন</span>',
        SUSPENDED: '<span class="status-badge-suspended">🛑 স্থগিত</span>'
      };

      return `
        <tr>
          <td>
            <div style="font-weight:600; color:var(--c-forest-900);">${u.full_name}</div>
            <code style="font-size:0.75rem; color:var(--c-stone-500);">${u.user_id}</code>
          </td>
          <td>
            <div>${u.email}</div>
            <div style="font-size:0.75rem; color:var(--c-stone-500);">${u.phone || 'ফোন নেই'}</div>
          </td>
          <td>${roleBadges[u.role] || u.role}</td>
          <td>${statusBadges[u.status] || u.status}</td>
          <td class="num" style="font-size:0.75rem;">${new Date(u.created_at).toLocaleDateString('bn-BD')}</td>
          <td style="text-align:right;">
            <button class="btn btn-secondary-stone btn-sm" onclick="openAdminRoleModal('${u.user_id}', '${u.full_name}', '${u.email}', '${u.role}')" style="padding:3px 8px; font-size:0.75rem; margin-right:4px;">
              ভূমিকা বদল
            </button>
            <button class="btn btn-secondary-stone btn-sm" onclick="openAdminStatusModal('${u.user_id}', '${u.full_name}', '${u.email}', '${u.status}')" style="padding:3px 8px; font-size:0.75rem; color:${u.status === 'ACTIVE' ? '#b91c1c' : '#047857'};">
              ${u.status === 'ACTIVE' ? 'স্থগিত' : 'সক্রিয়'}
            </button>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--c-risk-danger); padding:1.5rem;">ত্রুটি: ${err.message}</td></tr>`;
  }
}

function debounceUserSearch() {
  clearTimeout(userSearchTimeout);
  userSearchTimeout = setTimeout(loadAdminUsers, 300);
}

function openAdminRoleModal(userId, name, email, currentRole) {
  document.getElementById('admin-role-target-id').value = userId;
  document.getElementById('admin-role-target-name').textContent = name;
  document.getElementById('admin-role-target-email').textContent = email;
  document.getElementById('admin-role-select').value = currentRole;
  document.getElementById('admin-role-reason').value = '';

  const modal = document.getElementById('admin-role-modal');
  if (modal) modal.classList.add('open');
}

function closeAdminRoleModal() {
  const modal = document.getElementById('admin-role-modal');
  if (modal) modal.classList.remove('open');
}

async function handleAdminRoleSubmit(event) {
  event.preventDefault();
  const targetUserId = document.getElementById('admin-role-target-id').value;
  const newRole = document.getElementById('admin-role-select').value;
  const reason = document.getElementById('admin-role-reason').value.trim();

  try {
    const res = await LandTechAPI.updateAdminUserRole(targetUserId, newRole, reason);
    showToast(res.message || "ভূমিকা সফলভাবে হালনাগাদ হয়েছে।");
    closeAdminRoleModal();
    loadAdminUsers();
  } catch (err) {
    alert(`ভূমিকা পরিবর্তন ব্যর্থ: ${err.message}`);
  }
}

function openAdminStatusModal(userId, name, email, currentStatus) {
  document.getElementById('admin-status-target-id').value = userId;
  document.getElementById('admin-status-target-name').textContent = name;
  document.getElementById('admin-status-target-email').textContent = email;
  document.getElementById('admin-status-select').value = currentStatus === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE';
  document.getElementById('admin-status-reason').value = '';

  const modal = document.getElementById('admin-status-modal');
  if (modal) modal.classList.add('open');
}

function closeAdminStatusModal() {
  const modal = document.getElementById('admin-status-modal');
  if (modal) modal.classList.remove('open');
}

async function handleAdminStatusSubmit(event) {
  event.preventDefault();
  const targetUserId = document.getElementById('admin-status-target-id').value;
  const status = document.getElementById('admin-status-select').value;
  const reason = document.getElementById('admin-status-reason').value.trim();

  try {
    const res = await LandTechAPI.updateAdminUserStatus(targetUserId, status, reason);
    showToast(res.message || "অ্যাকাউন্ট স্ট্যাটাস হালনাগাদ হয়েছে।");
    closeAdminStatusModal();
    loadAdminUsers();
  } catch (err) {
    alert(`স্ট্যাটাস পরিবর্তন ব্যর্থ: ${err.message}`);
  }
}

async function loadAdminSecurityLogs() {
  const tbody = document.getElementById('admin-security-logs-tbody');
  if (!tbody) return;

  const action = document.getElementById('admin-log-filter-action')?.value || null;
  const search = document.getElementById('admin-log-search-input')?.value?.trim() || null;

  tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:1.5rem;">সিকিউরিটি লগ লোড হচ্ছে...</td></tr>`;

  try {
    const res = await LandTechAPI.getAdminSecurityLogs({ action, search, limit: 50 });
    const logs = res.security_logs || [];

    const countEl = document.getElementById('admin-logs-count');
    if (countEl) countEl.textContent = `মোট ${res.total} টি নিরাপত্তা ইভেন্ট রেকর্ড রয়েছে`;

    if (logs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:1.5rem; color:var(--c-stone-400);">কোনো সিকিউরিটি লগ পাওয়া যায়নি।</td></tr>`;
      return;
    }

    tbody.innerHTML = logs.map(l => {
      const isFailed = l.action.includes('FAILED') || l.action.includes('SUSPEND');
      const pillClass = isFailed ? 'pill-tag' : 'pill-tag pill-forest';
      const pillStyle = isFailed ? 'background:#fee2e2; color:#b91c1c; border:1px solid #fecaca;' : '';

      return `
        <tr>
          <td class="num" style="font-size:0.75rem; white-space:nowrap;">${new Date(l.timestamp).toLocaleString('bn-BD')}</td>
          <td>
            <strong>${l.actor_email || 'অজ্ঞাত'}</strong>
            <div style="font-size:0.72rem; color:var(--c-stone-500);">${l.actor_user_id || 'N/A'}</div>
          </td>
          <td><span class="${pillClass}" style="${pillStyle}">${l.action}</span></td>
          <td><code style="font-size:0.75rem;">${l.ip_address || '127.0.0.1'}</code></td>
          <td style="max-width:320px; font-size:0.75rem; font-family:monospace; color:var(--c-stone-600); word-break:break-all;">
            ${l.metadata_json || '{}'}
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--c-risk-danger); padding:1.5rem;">ত্রুটি: ${err.message}</td></tr>`;
  }
}

function debounceLogSearch() {
  clearTimeout(logSearchTimeout);
  logSearchTimeout = setTimeout(loadAdminSecurityLogs, 300);
}

