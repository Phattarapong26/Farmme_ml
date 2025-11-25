import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import Intro from "./pages/Intro";
import Map from "./pages/Map";
import Forecast from "./pages/Forecast";
import ChatAI from "./pages/ChatAI";
import PlantingSchedule from "./pages/PlantingSchedule";
import DashboardOverview from "./pages/DashboardOverview";
import Profile from "./pages/Profile";
import LocalAuth from "./pages/LocalAuth";
import NotFound from "./pages/NotFound";
import MapNavbar from "./components/MapNavbar";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { ProvinceContext } from "./hooks/useProvinceContext";
import "./utils/resetIntro"; // Enable window.resetIntro() for testing

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
      refetchOnWindowFocus: false,
      refetchOnMount: false,
      refetchOnReconnect: false,
      retry: 1,
    },
  },
});

const App = () => {
  const [selectedProvince, setSelectedProvince] = useState<string | null>(null);
  const [hasSeenIntro, setHasSeenIntro] = useState<boolean>(false);

  useEffect(() => {
    // Check if user has seen intro
    const seen = localStorage.getItem('hasSeenIntro');
    setHasSeenIntro(seen === 'true');
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ProvinceContext.Provider value={{ selectedProvince, setSelectedProvince }}>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter basename="/Farmme_ml/XD/frontend/dist">
            <Routes>
              {/* Intro page - First time only */}
              <Route 
                path="/intro" 
                element={hasSeenIntro ? <Navigate to="/" replace /> : <Intro />} 
              />
              
              {/* Auth page - No navbar, no protection */}
              <Route path="/auth" element={<LocalAuth />} />
              
              {/* Debug route to reset intro */}
              <Route 
                path="/reset-intro" 
                element={
                  <div className="flex flex-col items-center justify-center h-screen bg-gray-50">
                    <h1 className="text-2xl font-bold mb-4">Reset Intro</h1>
                    <button
                      onClick={() => {
                        localStorage.removeItem('hasSeenIntro');
                        window.location.href = '/intro';
                      }}
                      className="px-6 py-3 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
                    >
                      Reset & Show Intro
                    </button>
                  </div>
                } 
              />
              
              {/* Root - Map page (no login required) */}
              <Route 
                path="/" 
                element={
                  hasSeenIntro ? (
                    <>
                      <MapNavbar />
                      <Map />
                    </>
                  ) : (
                    <Navigate to="/intro" replace />
                  )
                } 
              />
              
              {/* Protected routes with MapNavbar */}
              <Route path="/map" element={
                <ProtectedRoute>
                  <MapNavbar />
                  <Map />
                </ProtectedRoute>
              } />
              
              <Route path="/overview" element={
                <ProtectedRoute>
                  <MapNavbar />
                  <DashboardOverview />
                </ProtectedRoute>
              } />
              
              <Route path="/forecast" element={
                <ProtectedRoute>
                  <MapNavbar />
                  <Forecast />
                </ProtectedRoute>
              } />
              
              <Route path="/chatai" element={
                <ProtectedRoute>
                  <MapNavbar />
                  <ChatAI />
                </ProtectedRoute>
              } />
              
              <Route path="/planting-schedule" element={
                <ProtectedRoute>
                  <MapNavbar />
                  <PlantingSchedule />
                </ProtectedRoute>
              } />
              
              <Route path="/profile" element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              } />
              
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={
                <>
                  <MapNavbar />
                  <NotFound />
                </>
              } />
            </Routes>
          </BrowserRouter>
        </TooltipProvider>
      </ProvinceContext.Provider>
    </QueryClientProvider>
  );
};

export default App;
