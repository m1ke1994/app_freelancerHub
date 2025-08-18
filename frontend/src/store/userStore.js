// src/store/userStore.js
import { defineStore } from 'pinia'

export const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    loading: false,
    error: null,
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
  }),

  getters: {
    isAuth: (s) => !!s.access && !!s.user,
    fullName: (s) => s.user ? `${s.user.first_name || ''} ${s.user.last_name || ''}`.trim() : '',
  },

  actions: {
    _setTokens({ access, refresh }) {
      if (access) { this.access = access; localStorage.setItem('access', access) }
      if (refresh) { this.refresh = refresh; localStorage.setItem('refresh', refresh) }
    },
    _clearTokens() {
      this.access = null
      this.refresh = null
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
    },
    setUser(user) { this.user = user },
    reset() { this.user = null; this.error = null; this._clearTokens() },
    logout() { this.reset() },

    async init() {
      window.addEventListener('storage', (e) => {
        if (e.key === 'access' || e.key === 'refresh') {
          this.access = localStorage.getItem('access')
          this.refresh = localStorage.getItem('refresh')
          if (this.access) this.fetchProfile().catch(() => this.reset())
          else this.user = null
        }
      })
      if (this.access && !this.user) {
        await this.fetchProfile().catch(() => this.reset())
      }
    },

    async refreshAccessToken() {
      if (!this.refresh) throw new Error('No refresh token')
      const resp = await fetch(`${baseURL}/api/accounts/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: this.refresh }),
      })
      if (!resp.ok) { this.logout(); throw new Error('Refresh failed') }
      const data = await resp.json()
      if (!data.access) { this.logout(); throw new Error('No access in refresh response') }
      this._setTokens({ access: data.access })
      return data.access
    },

    async _authedFetch(url, options = {}, tryRefresh = true) {
      const headers = new Headers(options.headers || {})
      const isFormData = options.body instanceof FormData
      if (!isFormData) {
        headers.set('Content-Type', headers.get('Content-Type') || 'application/json')
      }
      if (this.access) headers.set('Authorization', `Bearer ${this.access}`)
      const resp = await fetch(url, { ...options, headers })
      if (resp.status === 401 && tryRefresh && this.refresh) {
        try {
          await this.refreshAccessToken()
          const h2 = new Headers(options.headers || {})
          if (!(options.body instanceof FormData)) {
            h2.set('Content-Type', h2.get('Content-Type') || 'application/json')
          }
          h2.set('Authorization', `Bearer ${this.access}`)
          return await fetch(url, { ...options, headers: h2 })
        } catch { this.logout() }
      }
      return resp
    },

    async fetchProfile() {
      if (!this.access) { this.user = null; return }
      this.loading = true
      this.error = null
      try {
        const resp = await this._authedFetch(`${baseURL}/api/accounts/profile/`)
        if (!resp.ok) {
          this.user = null
          if (resp.status === 401) this._clearTokens()
          return
        }
        const data = await resp.json()
        this.user = data
      } catch {
        this.user = null
        this._clearTokens()
        this.error = 'Не удалось получить профиль'
      } finally {
        this.loading = false
      }
    },

    async login({ email, password }) {
      this.loading = true
      this.error = null
      try {
        const resp = await fetch(`${baseURL}/api/accounts/token/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password }),
        })
        const data = await resp.json().catch(() => ({}))
        if (!resp.ok) {
          // аккуратно покажем ответ DRF
          this.reset()
          this.error =
            data?.detail ||
            (Array.isArray(data?.email) ? data.email.join(' ') : data?.email) ||
            (Array.isArray(data?.password) ? data.password.join(' ') : data?.password) ||
            'Неверные учётные данные'
          return false
        }
        this._setTokens({ access: data.access, refresh: data.refresh })
        await this.fetchProfile()
        return true
      } catch {
        this.error = 'Ошибка соединения'
        return false
      } finally {
        this.loading = false
      }
    },

    async loginWithTokens({ access, refresh }) {
      this._setTokens({ access, refresh })
      await this.fetchProfile()
      return !!this.user
    },

    async updateProfile(payload) {
      const resp = await this._authedFetch(`${baseURL}/api/accounts/profile/`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      })
      if (!resp.ok) throw new Error('Profile update failed')
      const data = await resp.json()
      this.user = data
      return data
    },

async uploadAvatar(file) {
  const fd = new FormData();
  fd.append('avatar', file);

  const resp = await this._authedFetch(`${baseURL}/api/accounts/profile/avatar/`, {
    method: 'PATCH',
    body: fd,
  });

  // пытаемся прочесть тело вне зависимости от кода
  const data = await resp.json().catch(() => null);

  if (!resp.ok) {
    // достаем понятное сообщение
    const msg =
      (data && (data.avatar?.[0] || data.detail || data.error || JSON.stringify(data))) ||
      'Avatar upload failed';
    throw new Error(msg);
  }

  // успешно: в data пришёл актуальный профиль — кладём в стор
  // + небольшой cache-busting на случай, если браузер закешировал картинку
  if (data?.avatar_url) {
    data.avatar_url = `${data.avatar_url}${data.avatar_url.includes('?') ? '&' : '?'}t=${Date.now()}`;
  }
  this.user = data;
  return data;
},


    // 🔥 РЕГИСТРАЦИЯ: шлём confirm (и, при желании, password2 — но confirm обязателен для бэка)
    async register(payload) {
      this.loading = true
      this.error = null
      try {
        const {
          first_name, last_name, email, phone, role,
          password, password2,
        } = payload

        const body = {
          first_name: (first_name || '').trim(),
          last_name:  (last_name  || '').trim(),
          email:      (email      || '').trim().toLowerCase(),
          phone,
          role,
          password,
          confirm: password2 ?? password, // 👈 ключевое: бэку нужен confirm
          // можно послать и password2 на будущее, но confirm обязателен:
          password2: password2 ?? password,
        }

        const resp = await fetch(`${baseURL}/api/accounts/register/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        })

        const data = await resp.json().catch(() => ({}))
        if (!resp.ok) {
          // распарсим DRF-ошибки в удобный текст
          if (data && typeof data === 'object') {
            const chunks = []
            for (const [k, v] of Object.entries(data)) {
              const arr = Array.isArray(v) ? v : [String(v)]
              const label = (k === 'non_field_errors' || k === 'detail') ? 'Ошибка' : k
              chunks.push(`${label}: ${arr.join(' ')}`)
            }
            this.error = chunks.join('\n') || 'Ошибка регистрации'
          } else {
            this.error = 'Ошибка регистрации'
          }
          return false
        }

        // Автологин после успешной регистрации
        const ok = await this.login({ email: body.email, password })
        if (!ok) return false

        return true
      } catch {
        this.error = 'Нет связи с сервером'
        return false
      } finally {
        this.loading = false
      }
    },
  },
})
