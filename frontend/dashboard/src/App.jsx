import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Suspense, lazy, createContext, useState } from "react";
import Topbar from "./components/Topbar";
import { AnalysisSessionProvider } from "./context/AnalysisSession";

export const DemoContext = createContext({ isDemo: false, toggleDemo: () => {} });

const Dashboard = lazy(() => import("./pages/Dashboard"));
const Pipeline = lazy(() => import("./pages/Pipeline"));
const Maps = lazy(() => import("./pages/Maps"));
const MapDetail = lazy(() => import("./pages/MapDetail"));
const Departments = lazy(() => import("./pages/Departments"));
const Requirements = lazy(() => import("./pages/Requirements"));
const Graph = lazy(() => import("./pages/Graph"));

const Loader = () => (
  <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "50vh", color: "#10b981", fontSize: 14, fontWeight: 600 }}>
    Loading module...
  </div>
);

export default function App() {
  const [isDemo, setIsDemo] = useState(false);
  const toggleDemo = () => setIsDemo(d => !d);

  return (
    <DemoContext.Provider value={{ isDemo, toggleDemo }}>
      <AnalysisSessionProvider>
        <BrowserRouter>
          <div style={{ minHeight: "100vh", background: "#111827", fontFamily: "'Inter','Segoe UI',system-ui,sans-serif" }}>
            <Topbar />
            <main style={{ maxWidth: 1400, margin: "0 auto", padding: "32px 32px 48px" }}>
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
                </Routes>
              </Suspense>
            </main>
          </div>
        </BrowserRouter>
      </AnalysisSessionProvider>
    </DemoContext.Provider>
  );
}
