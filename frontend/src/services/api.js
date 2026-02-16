const BASE_URL = "http://127.0.0.1:8000";

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

export async function getCustomers() {
  const response = await fetch(`${BASE_URL}/customers`);
  return response.json();
}

export async function getAlerts() {
  const response = await fetch(`${BASE_URL}/alerts`);
  return response.json();
}
export async function getCustomerById(id) {
  const response = await fetch(`http://127.0.0.1:8000/customers/${id}`);
  if (!response.ok) throw new Error("Failed to fetch customer");
  return response.json();
}
export async function getAggregator(customerId) {
  const response = await fetch(`http://127.0.0.1:8000/aggregator/${customerId}`);
  if (!response.ok) throw new Error("Failed to fetch aggregator data");
  return response.json();
}
