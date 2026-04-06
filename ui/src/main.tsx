import { createRoot } from 'react-dom/client'
import App from './App.tsx'

import '@blueprintjs/core/lib/css/blueprint.css'
import '@blueprintjs/icons/lib/css/blueprint-icons.css'
import './index.css'
import { NotificationProvider } from './hooks/useNotification.tsx'

createRoot(document.getElementById('root')!).render(
  <NotificationProvider>
    <App />
  </NotificationProvider>

)