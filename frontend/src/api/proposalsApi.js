// frontend/src/api/proposalsApi.js
import { useUserStore } from "@/store/userStore.js"

function apiBase() {
  const raw =
    import.meta?.env?.VITE_API_BASE ||
    import.meta?.env?.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000"
  return String(raw).replace(/\/$/, "")
}

function authHeaders() {
  try {
    const store = useUserStore()
    const token = store?.access || localStorage.getItem("access") || ""
    return token ? { Authorization: `Bearer ${token}` } : {}
  } catch {
    const token = localStorage.getItem("access") || ""
    return token ? { Authorization: `Bearer ${token}` } : {}
  }
}

async function request(path, { method = "GET", body, headers = {} } = {}) {
  const url = `${apiBase()}/api${path.startsWith("/") ? "" : "/"}${path}`
  const res = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  })
  const text = await res.text()
  let data
  try {
    data = text ? JSON.parse(text) : null
  } catch {
    data = text
  }
  if (!res.ok) {
    const detail =
      (data && (data.detail || data.non_field_errors?.[0])) ||
      (typeof data === "string" ? data : "Request failed")
    throw new Error(detail)
  }
  return data
}

/* ====== ENDPOINTS ====== */

// Создать отклик (исполнитель)
export function createProposal({ job, cover_letter, bid_amount, days }) {
  return request(`/proposals/`, {
    method: "POST",
    body: { job, cover_letter, bid_amount, days },
  })
}

// Обновить свой отклик
export function updateProposal(id, { cover_letter, bid_amount, days }) {
  return request(`/proposals/${id}/`, {
    method: "PATCH",
    body: { cover_letter, bid_amount, days },
  })
}

// Получить один отклик
export function getProposal(id) {
  return request(`/proposals/${id}/`)
}

// Удалить свой отклик
export function deleteProposal(id) {
  return request(`/proposals/${id}/`, { method: "DELETE" })
}

// Список откликов на конкретное задание (если владелец задания) либо свой — если исполнитель
export function listProposals({ job, mine } = {}) {
  const q = new URLSearchParams()
  if (job) q.set("job", job)
  if (mine) q.set("mine", "1")
  const qs = q.toString() ? `?${q.toString()}` : ""
  return request(`/proposals/${qs}`)
}

// Действия владельца задания
export function shortlistProposal(id) {
  return request(`/proposals/${id}/shortlist/`, { method: "POST" })
}
export function acceptProposal(id) {
  return request(`/proposals/${id}/accept/`, { method: "POST" })
}
export function rejectProposal(id) {
  return request(`/proposals/${id}/reject/`, { method: "POST" })
}

// Статистика по откликам для задания (доступна владельцу задания)
export function proposalsStats(jobId) {
  return request(`/proposals/stats?job=${jobId}`)
}

// Назначения (прочитать свои / по моим задачам)
export function listAssignments() {
  return request(`/assignments/`)
}
