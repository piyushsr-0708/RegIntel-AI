import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Suspense, lazy, createContext, useState } from "react";
import Topbar from "./components/Topbar";
import Sidebar from "./components/Sidebar";
import { AnalysisSessionProvider } from "./context/AnalysisSession";
import { AuthProvider, useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";

export const DemoContext = createContext({ isDemo: false, toggleDemo: () => {} });

const Dashboard = lazy(() => import("./pages/Dashboard"));
const Pipeline = lazy(() => import("./pages/Pipeline"));
const Maps = lazy(() => import("./pages/Maps"));
const MapDetail = lazy(() => import("./pages/MapDetail"));
const Departments = lazy(() => import("./pages/Departments"));
const Requirements = lazy(() => import("./pages/Requirements"));
const Graph = lazy(() => import("./pages/Graph"));
const AssignmentCenter = lazy(() => import("./pages/AssignmentCenter"));
const DepartmentWorkspace = lazy(() => import("./pages/DepartmentWorkspace"));

const Loader = () => (
  <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "50vh", color: "#10b981", fontSize: 14, fontWeight: 600 }}>
    Loading module...
  </div>
);

// Authenticated layout wrapper
function AuthenticatedLayout({ children }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#111827", fontFamily: "'Inter','Segoe UI',system-ui,sans-serif" }}>
      <Sidebar />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <Topbar />
        <main style={{ flex: 1, padding: "32px", overflow: "auto" }}>
          {children}
        </main>
      </div>
    </div>
  );
}

function AppRoutes() {
  const [isDemo, setIsDemo] = useState(false);
  const toggleDemo = () => setIsDemo(d => !d);
  const { isAuthenticated, loading } = useAuth();

  console.log('[APP_ROUTES] Rendering - isAuthenticated:', isAuthenticated, 'loading:', loading);

  // Show loading while checking auth
  if (loading) {
    console.log('[APP_ROUTES] Auth loading, showing loading screen');
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          background: '#111827',
          color: '#10b981',
          fontSize: '14px',
          fontWeight: '600',
        }}
      >
        Verifying authentication...
      </div>
    );
  }

  console.log('[APP_ROUTES] Auth check complete, rendering routes');
  return (
    <DemoContext.Provider value={{ isDemo, toggleDemo }}>
      <Routes>
        {/* Public route */}
        <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} />

        {/* Protected routes */}
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <AuthenticatedLayout>
                <Suspense fallback={<Loader />}>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/pipeline" element={<Pipeline />} />
                    <Route path="/pipeline/analysis/maps" element={<Maps />} />
                    <Route path="/pipeline/analysis/graph" element={<Graph />} />
                    <Route path="/pipeline/analysis/department/:deptId" element={<Departments />} />
                    <Route path="/maps" element={<Maps />} />
                    <Route path="/maps/:id" element={<MapDetail />} />
                    <Route path="/departments" element={<Departments />} />
                    <Route path="/requirements" element={<Requirements />} />
                    <Route path="/graph" element={<Graph />} />
                    <Route path="/assignment-center" element={<AssignmentCenter />} />
                    <Route path="/workspace" element={<DepartmentWorkspace />} />
                  </Routes>
                </Suspense>
              </AuthenticatedLayout>
            </ProtectedRoute>
          }
        />
      </Routes>
    </DemoContext.Provider>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AnalysisSessionProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AnalysisSessionProvider>
    </AuthProvider>
  );
}
