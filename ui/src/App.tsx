import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { NotificationDisplay } from './components/notification/NotificationDisplay';
import SignInComponent from './components/SignIn/SignInComponent';
import UserSignUpComponent from './components/UserSignUp/UserSignUpComponent';
import Dashboard from './components/Dashboard/Dashboard';
import DataViewerPage from './components/DataViewer/DataViewerPage';

// Initialize state management for API
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="app-container min-h-screen bg-rd-white text-rd-darkblue">
          <NotificationDisplay />
          <Routes>
            {/* Default redirect to Login */}
            <Route path="/" element={<Navigate to="/login" replace />} />

            {/* Login and Signup forms */}
            <Route path="/login" element={<SignInComponent />} />
            <Route path="/signup" element={<UserSignUpComponent />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/data-viewer" element={<DataViewerPage />} />
            {/* <Route path="/pdf-viewer" element={<InteractivePdfViewer />} /> */}
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;