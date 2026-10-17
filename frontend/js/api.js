/**
 * DESHMRITTIKA / BHUMI-SYNC — Frontend API Client Layer
 * Interfaces with FastAPI endpoints (/api/v1) with session token management.
 */

const API_BASE = window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1')
  ? `${window.location.origin}/api/v1`
  : 'http://127.0.0.1:8000/api/v1';

class LandTechAPI {
  static token = null;
  static currentUser = {
    user_id: 'USR-CITIZEN-01',
    name: 'মো: রফিকুল ইসলাম',
    role: 'CITIZEN'
  };

  static setAuthToken(token, user) {
    this.token = token;
    this.currentUser = user;
    localStorage.setItem('deshmrittika_token', token);
    localStorage.setItem('deshmrittika_user', JSON.stringify(user));
  }

  static getHeaders() {
    const headers = {
      'Accept': 'application/json'
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  static initStoredAuth() {
    const savedToken = localStorage.getItem('deshmrittika_token');
    const savedUser = localStorage.getItem('deshmrittika_user');
    if (savedToken && savedUser) {
      try {
        this.token = savedToken;
        this.currentUser = JSON.parse(savedUser);
      } catch (e) {
        this.clearAuthToken();
      }
    }
  }

  static clearAuthToken() {
    this.token = null;
    this.currentUser = null;
    localStorage.removeItem('deshmrittika_token');
    localStorage.removeItem('deshmrittika_user');
  }

  static async getHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`);
      return await res.json();
    } catch (e) {
      console.error('Health check failed', e);
      return { status: 'OFFLINE', database: { connected: false } };
    }
  }

  // === AUTHENTICATION & SECURITY ENDPOINTS ===

  static async signup({ full_name, email, password, confirm_password, phone = '', role = 'CITIZEN' }) {
    const res = await fetch(`${API_BASE}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({
        full_name,
        email,
        password,
        confirm_password,
        phone,
        role
      })
    });
    const data = await res.json();
    if (!res.ok) {
      const msg = typeof data.detail === 'string' ? data.detail : (data.detail?.[0]?.msg || 'নিবন্ধন ব্যর্থ হয়েছে');
      throw new Error(msg);
    }
    return data;
  }

  static async verifyEmail(email, code) {
    const res = await fetch(`${API_BASE}/auth/verify-email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ email, code })
    });
    const data = await res.json();
    if (!res.ok) {
      const msg = typeof data.detail === 'string' ? data.detail : (data.detail?.[0]?.msg || 'যাচাইকরণ ব্যর্থ হয়েছে');
      throw new Error(msg);
    }
    this.setAuthToken(data.access_token, {
      user_id: data.user_id,
      name: data.name,
      role: data.role,
      email: data.email,
      status: data.status
    });
    return data;
  }

  static async resendCode(email, purpose = 'EMAIL_VERIFY') {
    const res = await fetch(`${API_BASE}/auth/resend-code`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ email, purpose })
    });
    const data = await res.json();
    if (!res.ok) {
      const msg = typeof data.detail === 'string' ? data.detail : (data.detail?.[0]?.msg || 'কোড পাঠানো যায়নি');
      throw new Error(msg);
    }
    return data;
  }

  static async login(email, password = 'Password123!', rememberMe = false) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ email: email, password: password, remember_me: rememberMe })
    });
    const data = await res.json();
    if (!res.ok) {
      // Check for unverified error object
      if (res.status === 403 && data.detail && data.detail.code === 'ACCOUNT_UNVERIFIED') {
        const err = new Error(data.detail.message || 'অ্যাকাউন্ট যাচাই করা হয়নি');
        err.code = 'ACCOUNT_UNVERIFIED';
        err.email = data.detail.email;
        throw err;
      }
      const msg = typeof data.detail === 'string' ? data.detail : (data.detail?.[0]?.msg || 'লগইন ব্যর্থ হয়েছে');
      throw new Error(msg);
    }
    this.setAuthToken(data.access_token, {
      user_id: data.user_id,
      name: data.name,
      role: data.role,
      email: data.email,
      status: data.status
    });
    return data;
  }

  static async forgotPassword(email) {
    const res = await fetch(`${API_BASE}/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ email })
    });
    const data = await res.json();
    if (!res.ok) {
      const msg = typeof data.detail === 'string' ? data.detail : 'পাসওয়ার্ড পুনরুদ্ধারে সমস্যা হয়েছে';
      throw new Error(msg);
    }
    return data;
  }

  static async resetPassword(email, code, new_password, confirm_password) {
    const res = await fetch(`${API_BASE}/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ email, code, new_password, confirm_password })
    });
    const data = await res.json();
    if (!res.ok) {
      const msg = typeof data.detail === 'string' ? data.detail : 'পাসওয়ার্ড রিসেট ব্যর্থ হয়েছে';
      throw new Error(msg);
    }
    return data;
  }

  static async changePassword(old_password, new_password, confirm_password) {
    const res = await fetch(`${API_BASE}/auth/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...this.getHeaders()
      },
      body: JSON.stringify({ old_password, new_password, confirm_password })
    });
    const data = await res.json();
    if (!res.ok) {
      const msg = typeof data.detail === 'string' ? data.detail : 'পাসওয়ার্ড পরিবর্তন ব্যর্থ হয়েছে';
      throw new Error(msg);
    }
    return data;
  }

  static async getMe() {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: this.getHeaders()
    });
    if (!res.ok) {
      throw new Error('অধিবেশন মেয়াদোত্তীর্ণ হয়েছে');
    }
    const data = await res.json();
    this.currentUser = {
      user_id: data.user_id,
      name: data.full_name,
      role: data.role,
      email: data.email,
      status: data.status,
      created_at: data.created_at,
      last_login_at: data.last_login_at
    };
    localStorage.setItem('deshmrittika_user', JSON.stringify(this.currentUser));
    return data;
  }

  static async logout() {
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: 'POST',
        headers: this.getHeaders()
      });
    } catch (e) {
      console.warn('Logout API error:', e);
    } finally {
      this.clearAuthToken();
    }
  }

  static async logoutAll() {
    try {
      await fetch(`${API_BASE}/auth/logout-all`, {
        method: 'POST',
        headers: this.getHeaders()
      });
    } catch (e) {
      console.warn('Logout all API error:', e);
    } finally {
      this.clearAuthToken();
    }
  }

  static async getDevMailbox() {
    const res = await fetch(`${API_BASE}/auth/dev-mailbox`);
    if (!res.ok) return [];
    return await res.json();
  }

  // === ADMIN ENDPOINTS (RBAC PROTECTED) ===

  static async getAdminUsers({ role = null, status = null, search = null, limit = 50, offset = 0 } = {}) {
    const params = new URLSearchParams();
    if (role) params.append('role', role);
    if (status) params.append('status', status);
    if (search) params.append('search', search);
    params.append('limit', limit);
    params.append('offset', offset);

    const res = await fetch(`${API_BASE}/admin/users?${params.toString()}`, {
      headers: this.getHeaders()
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || 'ব্যবহারকারী তালিকা লোড করা যায়নি (অ্যাডমিন অনুমতি প্রয়োজন)');
    }
    return await res.json();
  }

  static async updateAdminUserRole(targetUserId, newRole, reason) {
    const res = await fetch(`${API_BASE}/admin/users/role`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...this.getHeaders()
      },
      body: JSON.stringify({
        target_user_id: targetUserId,
        new_role: newRole,
        reason: reason
      })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'ভূমিকা পরিবর্তন ব্যর্থ হয়েছে');
    }
    return data;
  }

  static async updateAdminUserStatus(targetUserId, status, reason) {
    const res = await fetch(`${API_BASE}/admin/users/status`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...this.getHeaders()
      },
      body: JSON.stringify({
        target_user_id: targetUserId,
        status: status,
        reason: reason
      })
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'অ্যাকাউন্ট স্ট্যাটাস পরিবর্তন ব্যর্থ হয়েছে');
    }
    return data;
  }

  static async getAdminSecurityLogs({ limit = 50, action = null, search = null } = {}) {
    const params = new URLSearchParams();
    params.append('limit', limit);
    if (action) params.append('action', action);
    if (search) params.append('search', search);

    const res = await fetch(`${API_BASE}/admin/security-logs?${params.toString()}`, {
      headers: this.getHeaders()
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || 'সিকিউরিটি লগ লোড করা সম্ভব হয়নি');
    }
    return await res.json();
  }

  static async searchParcels({ mouza, dag, khatian, parcel_id, deed_number, owner_name, limit = 20, offset = 0 }) {
    const params = new URLSearchParams();
    if (mouza) params.append('mouza', mouza);
    if (dag) params.append('dag', dag);
    if (khatian) params.append('khatian', khatian);
    if (parcel_id) params.append('parcel_id', parcel_id);
    if (deed_number) params.append('deed_number', deed_number);
    if (owner_name) params.append('owner_name', owner_name);
    params.append('limit', limit);
    params.append('offset', offset);

    const res = await fetch(`${API_BASE}/search?${params.toString()}`, {
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error('Search failed');
    return await res.json();
  }

  static async getParcelProfile(parcelId) {
    const res = await fetch(`${API_BASE}/parcels/${encodeURIComponent(parcelId)}`, {
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error(`Parcel ${parcelId} not found`);
    return await res.json();
  }

  static async getParcelGeoJSON(parcelId) {
    const res = await fetch(`${API_BASE}/parcels/${encodeURIComponent(parcelId)}/geojson`, {
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error(`Geometry not found for ${parcelId}`);
    return await res.json();
  }

  static async evaluateFraud(parcelId) {
    const res = await fetch(`${API_BASE}/verification/evaluate/${encodeURIComponent(parcelId)}`, {
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error(`Evaluation failed for ${parcelId}`);
    return await res.json();
  }

  static async getDueDiligence(parcelId) {
    const res = await fetch(`${API_BASE}/due-diligence/${encodeURIComponent(parcelId)}`, {
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error(`Due diligence report failed for ${parcelId}`);
    return await res.json();
  }

  static async preCheckMutation(parcelId, deedId, applicantId) {
    const res = await fetch(`${API_BASE}/mutations/pre-check`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getHeaders()
      },
      body: JSON.stringify({
        parcel_id: parcelId,
        deed_id: deedId,
        applicant_id: applicantId
      })
    });
    if (!res.ok) throw new Error('Mutation pre-check request failed');
    return await res.json();
  }

  static async verifyDocumentIntegrity(fileBytesOrBlob, filename = 'document.png') {
    const formData = new FormData();
    formData.append('file', fileBytesOrBlob, filename);

    const res = await fetch(`${API_BASE}/documents/verify-integrity`, {
      method: 'POST',
      headers: this.token ? { 'Authorization': `Bearer ${this.token}` } : {},
      body: formData
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Document verification failed');
    }
    return await res.json();
  }

  static async computeClientSHA256(arrayBuffer) {
    const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  static async uploadDocumentOCR(fileBytesOrBlob, filename = 'document.png', preprocessMode = 'enhance_contrast', rotateDeg = 0, langOverride = null) {
    const formData = new FormData();
    formData.append('file', fileBytesOrBlob, filename);
    formData.append('preprocess_mode', preprocessMode);
    formData.append('rotate_deg', rotateDeg);
    if (langOverride) {
      formData.append('lang_override', langOverride);
    }

    const res = await fetch(`${API_BASE}/documents/upload-ocr`, {
      method: 'POST',
      headers: this.token ? { 'Authorization': `Bearer ${this.token}` } : {},
      body: formData
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'OCR upload failed');
    }
    return await res.json();
  }

  static async getOfficerQueue(severity = null, limit = 50) {
    let url = `${API_BASE}/officer/queue?limit=${limit}`;
    if (severity) url += `&severity=${encodeURIComponent(severity)}`;

    const res = await fetch(url, {
      headers: this.getHeaders()
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to fetch officer queue (Check permissions)');
    }
    return await res.json();
  }

  static async recordReviewDecision(caseId, action, reason) {
    const res = await fetch(`${API_BASE}/officer/decision`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getHeaders()
      },
      body: JSON.stringify({
        case_id: caseId,
        action: action,
        reason: reason
      })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to record decision');
    }
    return await res.json();
  }

  static async getAuditLogs(limit = 20) {
    const res = await fetch(`${API_BASE}/officer/audit-logs?limit=${limit}`, {
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return await res.json();
  }

  // ==========================================
  // GEOGRAPHY API METHODS (PHASE 2)
  // ==========================================
  static async getDivisions() {
    const res = await fetch(`${API_BASE}/geography/divisions`);
    if (!res.ok) throw new Error('Failed to fetch divisions');
    return await res.json();
  }

  static async getDistricts(divisionId = null) {
    let url = `${API_BASE}/geography/districts`;
    if (divisionId) url += `?division_id=${encodeURIComponent(divisionId)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch districts');
    return await res.json();
  }

  static async getUpazilas(districtId = null, limit = 100, offset = 0) {
    let url = `${API_BASE}/geography/upazilas?limit=${limit}&offset=${offset}`;
    if (districtId) url += `&district_id=${encodeURIComponent(districtId)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch upazilas');
    return await res.json();
  }

  static async getUnions(upazilaId = null) {
    let url = `${API_BASE}/geography/unions`;
    if (upazilaId) url += `?upazila_id=${encodeURIComponent(upazilaId)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch unions');
    return await res.json();
  }

  static async getMouzas(upazilaId = null, unionId = null) {
    let url = `${API_BASE}/geography/mouzas?`;
    if (upazilaId) url += `upazila_id=${encodeURIComponent(upazilaId)}&`;
    if (unionId) url += `union_id=${encodeURIComponent(unionId)}&`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch mouzas');
    return await res.json();
  }

  static async searchGeography(query, limit = 20) {
    const res = await fetch(`${API_BASE}/geography/search?q=${encodeURIComponent(query)}&limit=${limit}`);
    if (!res.ok) throw new Error('Failed to search geography');
    return await res.json();
  }

  // ==========================================
  // LAND OFFICIALS DIRECTORY API METHODS (PHASE 4)
  // ==========================================
  static async getOfficials(params = {}) {
    const searchParams = new URLSearchParams();
    for (const [key, val] of Object.entries(params)) {
      if (val !== null && val !== undefined && val !== '') {
        searchParams.append(key, val);
      }
    }
    const res = await fetch(`${API_BASE}/officials?${searchParams.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch land officials');
    return await res.json();
  }

  static async getOfficialDetail(officialId) {
    const res = await fetch(`${API_BASE}/officials/${encodeURIComponent(officialId)}`);
    if (!res.ok) throw new Error('Failed to fetch official profile');
    return await res.json();
  }

  static async getDesignations() {
    const res = await fetch(`${API_BASE}/officials/meta/designations`);
    if (!res.ok) throw new Error('Failed to fetch designations');
    return await res.json();
  }

  static async getOffices(params = {}) {
    const searchParams = new URLSearchParams();
    for (const [key, val] of Object.entries(params)) {
      if (val !== null && val !== undefined && val !== '') {
        searchParams.append(key, val);
      }
    }
    const res = await fetch(`${API_BASE}/officials/offices?${searchParams.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch land offices');
    return await res.json();
  }

  static async getOfficeDetail(officeId) {
    const res = await fetch(`${API_BASE}/officials/offices/${encodeURIComponent(officeId)}`);
    if (!res.ok) throw new Error('Failed to fetch office detail');
    return await res.json();
  }

  // ==========================================
  // SPATIAL MAP & PARCEL LOCATION API (PHASE 3)
  // ==========================================
  static async getParcelsMap(bbox = null, mouza = null, limit = 100) {
    let url = `${API_BASE}/parcels/map?limit=${limit}`;
    if (bbox) url += `&bbox=${encodeURIComponent(bbox)}`;
    if (mouza) url += `&mouza=${encodeURIComponent(mouza)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch map parcels');
    return await res.json();
  }

  static async getParcelLocation(parcelId) {
    const res = await fetch(`${API_BASE}/parcels/${encodeURIComponent(parcelId)}/location`);
    if (!res.ok) throw new Error('Failed to fetch parcel location');
    return await res.json();
  }

  static async getAcquisitionZonesLayer() {
    const res = await fetch(`${API_BASE}/parcels/layers/acquisition-zones`);
    if (!res.ok) throw new Error('Failed to fetch acquisition zones layer');
    return await res.json();
  }

  static async getKhasLandLayer(limit = 100) {
    const res = await fetch(`${API_BASE}/parcels/layers/khas-land?limit=${limit}`);
    if (!res.ok) throw new Error('Failed to fetch khas land layer');
    return await res.json();
  }
}
