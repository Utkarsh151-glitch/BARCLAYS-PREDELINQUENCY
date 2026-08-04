const BASE_URL = (import.meta.env.VITE_API_BASE_URL || "https://barclays-predelinquency.onrender.com").replace(/\/$/, "");

export async function analyzeCustomer(payload) {
  const response = await fetch(`${BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error("API Error");
  }

  return response.json();
}

export async function getPortfolioSummary() {
  const response = await fetch(`${BASE_URL}/portfolio-summary`);
  return response.json();
}

export async function getCustomers({ limit = 200, offset = 0, mode = "top_risk" } = {}) {
  const response = await fetch(`${BASE_URL}/customers?limit=${limit}&offset=${offset}&mode=${mode}`);
  if (!response.ok) throw new Error("Failed to fetch customers");
  return response.json();
}

export async function getAlerts() {
  const response = await fetch(`${BASE_URL}/alerts`);
  return response.json();
}

export async function getModelMetrics() {
  const response = await fetch(`${BASE_URL}/model-metrics`);
  if (!response.ok) throw new Error("Failed to fetch model metrics");
  return response.json();
}
export async function getCustomerById(id) {
  const response = await fetch(`${BASE_URL}/customers/${id}`);
  if (!response.ok) throw new Error("Failed to fetch customer");
  return response.json();
}
export async function getAggregator(customerId) {
  const response = await fetch(`${BASE_URL}/aggregator/${customerId}`);
  if (!response.ok) throw new Error("Failed to fetch aggregator data");
  return response.json();
}

/**
 * Placeholder for a future savings trend endpoint.
 * Intended contract:
 * GET /customers/:id/savings-trend?range=7D|30D|90D
 * Response shape:
 * {
 *   customer_id: string,
 *   range: "7D" | "30D" | "90D",
 *   points: [{ date: "YYYY-MM-DD", net_savings: number }]
 * }
 */
export async function getSavingsTrend(customerId, range = "30D") {
  void customerId;
  void range;
  return null;
}
