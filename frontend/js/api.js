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

  static async getHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`);
      return await res.json();
    } catch (e) {
      console.error('Health check failed', e);
      return { status: 'OFFLINE', database: { connected: false } };
    }
  }

  static async login(email) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, password: 'any' })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    const data = await res.json();
    this.setAuthToken(data.access_token, {
      user_id: data.user_id,
      name: data.name,
      role: data.role
    });
    return data;
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

  static async uploadDocumentOCR(fileBytesOrBlob, filename = 'document.png') {
    const formData = new FormData();
    formData.append('file', fileBytesOrBlob, filename);

    const res = await fetch(`${API_BASE}/documents/upload-ocr`, {
      method: 'POST',
      headers: this.token ? { 'Authorization': `Bearer ${this.token}` } : {},
      body: formData
    });
    if (!res.ok) throw new Error('OCR upload failed');
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
}
