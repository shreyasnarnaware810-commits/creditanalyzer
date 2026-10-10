import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Navbar } from "./components/Navbar";
import { Sidebar } from "./components/Sidebar";
import { DisclaimerBanner } from "./components/DisclaimerBanner";
import { LoginPage } from "./pages/LoginPage";
import { OverviewDashboard } from "./pages/OverviewDashboard";
import { NewAnalysisPage } from "./pages/NewAnalysisPage";
import { ApplicationDetailPage } from "./pages/ApplicationDetailPage";
import { DecisionHistoryPage } from "./pages/DecisionHistoryPage";
import { FairnessModelPage } from "./pages/FairnessModelPage";
import { SettingsPage } from "./pages/SettingsPage";
import siteBackground from "./assets/site-background.jpg";

const ProtectedLayout: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-navy-950 flex items-center justify-center text-xs text-slate-400">
        Loading Credence AI Session...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div
      className="relative min-h-screen bg-[#F7F1E8] flex flex-col overflow-hidden"
      style={{
        backgroundImage: `url(${siteBackground})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
      }}
    >
      <div className="absolute inset-0 bg-[#F7F1E8]/80" aria-hidden="true" />
      <div className="relative z-10 min-h-screen flex flex-col">
        <Navbar />
        <DisclaimerBanner />
        <div className="flex flex-1">
          <Sidebar />
          <main className="flex-1 p-6 overflow-y-auto max-w-7xl bg-white/15">
            <Routes>
              <Route path="/overview" element={<OverviewDashboard />} />
              <Route path="/new-analysis" element={<NewAnalysisPage />} />
              <Route path="/applications" element={<OverviewDashboard />} />
              <Route path="/applications/:id" element={<ApplicationDetailPage />} />
              <Route path="/decision-history" element={<DecisionHistoryPage />} />
              <Route path="/fairness-model" element={<FairnessModelPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="*" element={<Navigate to="/overview" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </div>
  );
};

export const AppContent: React.FC = () => {
  const { user } = useAuth();
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/overview" replace /> : <LoginPage />} />
      <Route path="/*" element={<ProtectedLayout />} />
    </Routes>
  );
};

export const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
};

export default App;
