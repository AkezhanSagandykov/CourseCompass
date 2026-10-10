// All calls to the Django REST API go through this file.
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
const TOKEN_KEY = "cc_token";

// Moderation happens in the Django admin, next to the API
export const ADMIN_URL = API_URL.replace(/\/api\/?$/, "/admin/");

export const tokenStorage = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

// Turns DRF error responses ({"detail": ...} or {"field": ["..."]}) into one readable sentence.
function errorMessage(data) {
  if (!data) return "The server did not respond. Check that the API is running.";
  if (typeof data.detail === "string") return data.detail;
  return Object.entries(data)
    .map(([field, messages]) => {
      const text = [].concat(messages).join(" ");
      return field === "non_field_errors" ? text : `${field.replace("_", " ")}: ${text}`;
    })
    .join(" ");
}

export async function api(path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = tokenStorage.get();
  if (token) headers.Authorization = `Token ${token}`;

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError("Cannot reach the API. Is the Django server running on port 8000?", 0, null);
  }

  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(errorMessage(data), response.status, data);
  return data;
}
