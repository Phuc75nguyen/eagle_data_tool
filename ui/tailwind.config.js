/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      screens: {
        '3xl': '112rem',
      },
      boxShadow: {
        'elementName': 'rgb(204, 219, 232) 1px 1px 6px 0px inset, rgba(255, 255, 255, 0.5) -1px -1px 6px 0.5px inset',
      },
      fontFamily: {
        roboto: ['"Roboto"', 'sans-serif'],
      },
      spacing: {
        'tree-indent-base': '5px',
      },
      fontSize: {
        'rd-datamimic': '1.25rem',
        'rd-title-store-sm': '2.25rem',
        'rd-title-store-md': '3rem',
        'rd-demo-project': '1.5rem',
        'rd-demo-tag': '1rem',
        'rd-btn': '0.875rem',
        'rd-noti-title': '1rem',
        'rd-noti-message': '0.875rem',
        'rd-noti-icon': '1.5rem',
      },
      colors: {
        'primary-medium': '#3f4858',
        'primary-slight': '#394b59',
        'rd-darkblue': '#323E4F',
        'rd-turquoise': '#5E949F',
        'rd-lightgrey': '#B6C4C4',
        'rd-yellow': '#FDE74C',
        'rd-white': '#F3F6F9',
        'rd-orange': '#FA824C',
        'rd-blue': '#4177AC',
        'rd-copper': '#CE8964',
        'rd-amber': '#F09F0D',
        'rd-green': '#248232',
        'rd-flashgreen': '#C8EC37',
        'rd-flashred': '#F8333C',
        'rd-flashturq': '#47c9af',
        'rd-dark': 'var(--color-rd-dark, #09090b)',
      },
      animation: {
        'showNotiSm': 'showNotiSm 0.8s cubic-bezier(0.25, 1, 0.5, 1)',
        'showNotiMd': 'showNotiMd 0.8s cubic-bezier(0.25, 1, 0.5, 1)',
      },
      keyframes: {
        showNotiSm: {
          '0%': { opacity: '0', transform: 'translateY(-30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        showNotiMd: {
          '0%': { opacity: '0', transform: 'translateX(10%)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
    },
  },
  plugins: [],
}