import { useThemeStore } from '../store/themeStore';

const ThemeToggle = () => {
  const { theme, toggleTheme } = useThemeStore();

  // Sun icon SVG for light mode
  const SunIcon = () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="w-5 h-5 transition-all duration-300"
    >
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v2" />
      <path d="M12 20v2" />
      <path d="m4.93 4.93 1.41 1.41" />
      <path d="m17.66 17.66 1.41 1.41" />
      <path d="M2 12h2" />
      <path d="M20 12h2" />
      <path d="m6.34 17.66-1.41 1.41" />
      <path d="m19.07 4.93-1.41 1.41" />
    </svg>
  );

  // Moon icon SVG for dark mode
  const MoonIcon = () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="w-5 h-5 transition-all duration-300"
    >
      <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
    </svg>
  );

  return (
    <button
      onClick={toggleTheme}
      aria-label="Toggle theme"
      className="
        relative
        w-11 h-11
        flex items-center justify-center
        rounded-lg
        bg-gray-200
        dark:bg-gray-700
        text-gray-800
        dark:text-yellow-300
        transition-all duration-300
        hover:bg-gray-300
        dark:hover:bg-gray-600
        hover:scale-110
        active:scale-95
        focus:outline-none
        focus:ring-2
        focus:ring-purple-500
        focus:ring-offset-2
        focus:ring-offset-white
        dark:focus:ring-offset-gray-900
      "
    >
      <div className="relative w-5 h-5">
        {/* Sun icon - visible in light mode */}
        <div
          className={`
            absolute inset-0
            transition-all duration-300
            ${theme === 'light' ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 rotate-90 scale-0'}
          `}
        >
          <SunIcon />
        </div>
        {/* Moon icon - visible in dark mode */}
        <div
          className={`
            absolute inset-0
            transition-all duration-300
            ${theme === 'dark' ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-90 scale-0'}
          `}
        >
          <MoonIcon />
        </div>
      </div>
    </button>
  );
};

export default ThemeToggle;

