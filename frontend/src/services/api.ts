const API_BASE_URL = "http://127.0.0.1:8000";

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem("credence_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    ...getAuthHeader(),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMsg = "An unexpected error occurred";
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errData.message || JSON.stringify(errData);
    } catch {
      errorMsg = `Server error ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorMsg);
  }

  return response.json();
}

export const api = {
  // Auth
  async login(username: string, password: string) {
    return request<any>("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
  },

  async signup(data: any) {
    return request<any>("/api/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
  },

  async logout() {
    return request<any>("/api/auth/logout", { method: "POST" });
  },

  async getMe() {
    return request<any>("/api/auth/me");
  },

  // Applications
  async getApplications() {
    return request<any[]>("/api/applications");
  },

  async getApplication(id: string) {
    return request<any>(`/api/applications/${id}`);
  },

  async createApplication(requestedAmount: number) {
    return request<any>("/api/applications", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ requested_amount: requestedAmount }),
    });
  },

  async recordDecision(id: string, data: { status: string; approved_amount?: number; override_reason?: string; notes?: string }) {
    return request<any>(`/api/applications/${id}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
  },

  // Analysis & Pipeline
  async previewPdf(pdfFile: File) {
    const formData = new FormData();
    formData.append("pdf_file", pdfFile);

    const token = localStorage.getItem("credence_token");
    const response = await fetch(`${API_BASE_URL}/api/analysis/preview-pdf`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });

    if (!response.ok) {
      let errorMsg = "Failed to extract PDF bank statement";
      try {
        const errData = await response.json();
        errorMsg = errData.detail || errData.message || JSON.stringify(errData);
      } catch {
        errorMsg = `Server error ${response.status}: ${response.statusText}`;
      }
      throw new Error(errorMsg);
    }

    return response.json();
  },

  async runAnalysis(applicationId: string, transactionsFile: File, utilityFile?: File) {
    const formData = new FormData();
    formData.append("application_id", applicationId);
    formData.append("transactions_file", transactionsFile);
    if (utilityFile) {
      formData.append("utility_file", utilityFile);
    }

    const token = localStorage.getItem("credence_token");
    const response = await fetch(`${API_BASE_URL}/api/analysis`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });

    if (!response.ok) {
      let errorMsg = "Failed to run analysis";
      try {
        const errData = await response.json();
        errorMsg = errData.detail || errData.message;
      } catch {}
      throw new Error(errorMsg);
    }

    return response.json();
  },

  async getAnalysisRun(runId: string) {
    return request<any>(`/api/analysis/${runId}`);
  },

  async getAnalysisExplanation(runId: string) {
    return request<any[]>(`/api/analysis/${runId}/explanation`);
  },

  async getAnalysisCounterfactuals(runId: string) {
    return request<any[]>(`/api/analysis/${runId}/counterfactuals`);
  },

  async runWhatIf(data: {
    analysis_run_id: string;
    stable_cash_flow?: number;
    utility_punctuality?: number;
    month_end_buffer?: number;
    requested_amount?: number;
  }) {
    return request<any>("/api/analysis/whatif", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
  },

  // Fairness
  async getFairness() {
    return request<any>("/api/fairness");
  },

  // Audit
  async getAuditHistory(applicationId: string) {
    return request<any[]>(`/api/audit/${applicationId}`);
  },

  // Demo
  async seedDemo() {
    return request<any>("/api/demo/seed", { method: "POST" });
  },

  getSampleCsvUrl(filename: string) {
    return `${API_BASE_URL}/api/demo/sample-csv/${filename}`;
  },

  // PDF Report Download
  async downloadReport(runId: string, filename: string = "Credence_AI_Assessment.pdf") {
    const token = localStorage.getItem("credence_token");
    const response = await fetch(`${API_BASE_URL}/api/analysis/${runId}/report`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });

    if (!response.ok) {
      throw new Error("Failed to download PDF report");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }
};

