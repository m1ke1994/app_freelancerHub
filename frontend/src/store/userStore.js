// src/store/userStore.js
import { defineStore } from 'pinia'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    loading: false,
    error: null,
    // храним копию токенов в памяти (источник истины — localStorage)
    access: localStorage.getItem('access') || null,
    refresh: localStorage.getItem('refresh') || null,
  }),

  getters: {
    isAuth: (s) => !!s.access && !!s.user,
    fullName: (s) => s.user ? `${s.user.first_name || ''} ${s.user.last_name || ''}`.trim() : '',
  },

  actions: {
    _setTokens({ access, refresh }) {
      if (access) {
        this.access = access
        localStorage.setItem('access', access)
      }
      if (refresh) {
        this.refresh = refresh
        localStorage.setItem('refresh', refresh)
      }
    },

    _clearTokens() {
      this.access = null
      this.refresh = null
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
    },

    setUser(user) {
      this.user = user
    },

    logout() {
      this.user = null
      this._clearTokens()
    },

    /** Инициализация стора при старте приложения */
    async init() {
      if (this.access && !this.user) {
        await this.fetchProfile()
      }
    },

    /** Рефреш access-токена */
    async refreshAccessToken() {
      if (!this.refresh) throw new Error('No refresh token')

      const resp = await fetch(`${baseURL}/api/accounts/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: this.refresh }),
      })

      if (!resp.ok) {
        this.logout()
        throw new Error('Refresh failed')
      }

      const data = await resp.json()
      if (!data.access) {
        this.logout()
        throw new Error('No access in refresh response')
      }
      this._setTokens({ access: data.access })
      return data.access
    },

    /** Базовый helper: делает fetch с авторизацией и 1 попыткой рефреша при 401 */
    async _authedFetch(url, options = {}, tryRefresh = true) {
      const headers = new Headers(options.headers || {})
      if (!(options.body instanceof FormData)) {
        // не ставим Content-Type вручную для FormData
        headers.set('Content-Type', headers.get('Content-Type') || 'application/json')
      }
      if (this.access) headers.set('Authorization', `Bearer ${this.access}`)

      const resp = await fetch(url, { ...options, headers })

      if (resp.status === 401 && tryRefresh && this.refresh) {
        // пробуем рефреш и повторяем запрос один раз
        try {
          await this.refreshAccessToken()
          const h2 = new Headers(options.headers || {})
          if (!(options.body instanceof FormData)) {
            h2.set('Content-Type', h2.get('Content-Type') || 'application/json')
          }
          h2.set('Authorization', `Bearer ${this.access}`)
          return await fetch(url, { ...options, headers: h2 })
        } catch {
          this.logout()
        }
      }
      return resp
    },

    /** Загрузка профиля */
    async fetchProfile() {
      if (!this.access) {
        this.user = null
        return
      }
      this.loading = true
      this.error = null
      try {
        const resp = await this._authedFetch(`${baseURL}/api/accounts/profile/`)
        if (!resp.ok) {
          // если после рефреша всё ещё ошибка — очищаем
          this.user = null
          if (resp.status === 401) this._clearTokens()
          return
        }
        const data = await resp.json()
        this.user = data
      } catch (e) {
        this.user = null
        this._clearTokens()
        this.error = 'Не удалось получить профиль'
      } finally {
        this.loading = false
      }
    },

    /** Логин (пример) */
  /** Логин (SimpleJWT): username = email */
async login({ email, password }) {
  this.loading = true
  this.error = null
  try {
    const resp = await fetch(`${baseURL}/api/accounts/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      // ВАЖНО: SimpleJWT ждёт username, а не email
      body: JSON.stringify({ username: email, password }),
    })
    if (!resp.ok) {
      this.logout()
      throw new Error('Auth failed')
    }
    const data = await resp.json()
    this._setTokens({ access: data.access, refresh: data.refresh })
    await this.fetchProfile()
    return true
  } catch (e) {
    this.error = 'Неверные учётные данные'
    return false
  } finally {
    this.loading = false
  }
},


    /** Обновление анкеты (PATCH JSON) */
    async updateProfile(payload) {
      // payload должен соответствовать твоей DRF-схеме
      // пример: { title, bio, location, gender, education, status, categories, skills, rate_type, hourly_rate, project_rate, availability, links, socials, portfolio }
      const resp = await this._authedFetch(`${baseURL}/api/accounts/profile/`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      })
      if (!resp.ok) {
        throw new Error('Profile update failed')
      }
      const data = await resp.json()
      this.user = data
      return data
    },

    /** Отдельная загрузка аватара (multipart/form-data) */
    async uploadAvatar(file) {
      const fd = new FormData()
      fd.append('avatar', file)

      const resp = await this._authedFetch(`${baseURL}/api/accounts/profile/avatar/`, {
        method: 'PATCH',
        body: fd, // заголовок Content-Type формируется автоматически
      })
      if (!resp.ok) {
        throw new Error('Avatar upload failed')
      }
      const data = await resp.json()
      // предполагаем, что сервер вернёт обновлённый профиль с avatar_url
      this.user = data
      return data
    },
  },
})
