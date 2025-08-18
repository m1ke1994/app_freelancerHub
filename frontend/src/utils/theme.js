const THEME_KEY = 'theme'; // 'dark' | 'light'

export function getInitialTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved === 'dark' || saved === 'light') return saved;
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  return prefersDark ? 'dark' : 'light';
}

export function applyTheme(theme) {
  const root = document.documentElement;
  root.classList.toggle('dark', theme === 'dark');
  localStorage.setItem(THEME_KEY, theme);
}

export function toggleTheme() {
  const isDark = document.documentElement.classList.contains('dark');
  const next = isDark ? 'light' : 'dark';
  applyTheme(next);
  return next;
}

/** Опционально: подхватывать смену системной темы, если пользователь НИКОГДА не выбирал вручную */
export function watchSystemTheme() {
  const mq = window.matchMedia?.('(prefers-color-scheme: dark)');
  if (!mq) return () => {};
  const handler = (e) => {
    if (!localStorage.getItem(THEME_KEY)) {
      applyTheme(e.matches ? 'dark' : 'light');
    }
  };
  mq.addEventListener('change', handler);
  return () => mq.removeEventListener('change', handler);
}
