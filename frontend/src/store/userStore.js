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
    // Если тебе нужно считать авторизованным уже при наличии access — можешь упростить до !!s.access
    isAuth: (s) => !!s.access && !!s.user,
    fullName: (s) => (s.user ? `${s.user.first_name || ''} ${s.user.last_name || ''}`.trim() : ''),
    role: (s) => s.user?.role || null,
  },

  actions: {
    /* ==============================
       INTERNAL UTILS
    ============================== */
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

    _redirectPathByRole() {
      // Настрой эти пути под свои реальные роуты
      const EXECUTOR_PATH = '/freelancer/profile'
      const CUSTOMER_PATH = '/customer/profile'
      const r = this.role
      if (r === 'executor') return EXECUTOR_PATH
      if (r === 'customer') return CUSTOMER_PATH
      return '/' // запасной вариант
    },

    async _authedFetch(url, options = {}, tryRefresh = true) {
      const headers = new Headers(options.headers || {})
      const isFormData = options.body instanceof FormData
      if (!isFormData) {
        headers.set('Content-Type', headers.get('Content-Type') || 'application/json')
      }
      if (this.access) headers.set('Authorization', `Bearer ${this.access}`)

      const doFetch = () => fetch(url, { ...options, headers })
      let resp = await doFetch()

      // refresh on 401
      if (resp.status === 401 && tryRefresh && this.refresh) {
        try {
          await this.refreshAccessToken()
          const h2 = new Headers(options.headers || {})
          if (!(options.body instanceof FormData)) {
            h2.set('Content-Type', h2.get('Content-Type') || 'application/json')
          }
          if (this.access) h2.set('Authorization', `Bearer ${this.access}`)
          resp = await fetch(url, { ...options, headers: h2 })
        } catch {
          this.logout()
        }
      }
      return resp
    },

    /* ==============================
       SESSION BOOTSTRAP
    ============================== */
    async init() {
      // Синхронизация вкладок
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

    /* ==============================
       PROFILE
    ============================== */
    async fetchProfile() {
      if (!this.access) { this.user = null; return null }
      this.loading = true
      this.error = null
      try {
        const resp = await this._authedFetch(`${baseURL}/api/accounts/profile/`)
        if (!resp.ok) {
          this.user = null
          if (resp.status === 401) this._clearTokens()
          return null
        }
        const data = await resp.json()
        this.user = data
        return data
      } catch {
        this.user = null
        this._clearTokens()
        this.error = 'Не удалось получить профиль'
        return null
      } finally {
        this.loading = false
      }
    },

    async updateProfile(payload) {
      // Сохранение анкеты (личного кабинета)
      // payload: любые поля профиля (gender, education, status, bio, skills и т.п.)
      const resp = await this._authedFetch(`${baseURL}/api/accounts/profile/`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      })
      if (!resp.ok) {
        // попробуем достать текст ошибки от DRF
        let msg = 'Profile update failed'
        try {
          const data = await resp.json()
          msg = data?.detail || data?.error || JSON.stringify(data)
        } catch {}
        throw new Error(msg)
      }
      const data = await resp.json()
      this.user = data
      return data
    },

    async uploadAvatar(file) {
      const fd = new FormData()
      fd.append('avatar', file)

      const resp = await this._authedFetch(`${baseURL}/api/accounts/profile/avatar/`, {
        method: 'PATCH',
        body: fd,
      })

      const data = await resp.json().catch(() => null)

      if (!resp.ok) {
        const msg =
          (data && (data.avatar?.[0] || data.detail || data.error || JSON.stringify(data))) ||
          'Avatar upload failed'
        throw new Error(msg)
      }

      // cache-busting для аватарки
      if (data?.avatar_url) {
        data.avatar_url = `${data.avatar_url}${data.avatar_url.includes('?') ? '&' : '?'}t=${Date.now()}`
      }
      this.user = data
      return data
    },

    /* ==============================
       AUTH
    ============================== */
    async login({ email, password }, { onRedirect } = {}) {
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

        // 🔁 Редирект по роли сразу после логина
        if (typeof onRedirect === 'function') {
          onRedirect(this._redirectPathByRole())
        }
        return true
      } catch {
        this.error = 'Ошибка соединения'
        return false
      } finally {
        this.loading = false
      }
    },

    async loginWithTokens({ access, refresh }, { onRedirect } = {}) {
      this._setTokens({ access, refresh })
      await this.fetchProfile()
      if (this.user && typeof onRedirect === 'function') {
        onRedirect(this._redirectPathByRole())
      }
      return !!this.user
    },

    // Регистрация с автологином и редиректом по роли
    async register(payload, { onRedirect } = {}) {
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
          confirm: password2 ?? password, // API ожидает confirm
          password2: password2 ?? password,
        }

        const resp = await fetch(`${baseURL}/api/accounts/register/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        })

        const data = await resp.json().catch(() => ({}))
        if (!resp.ok) {
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

        // Автологин → загрузка профиля → редирект по роли
        const ok = await this.login({ email: body.email, password }, { onRedirect })
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
