import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import '@fortawesome/fontawesome-free/css/all.min.css';
import './App.css';

// Components
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import Scraping from './components/Scraping';
import Analytics from './components/Analytics';
import Documentation from './components/Documentation';
import Account from './components/Account';

// Loading component
const LoadingScreen = () => (
  <div className="loading-screen">
    <div className="loading-content">
      <div className="loading-logo">
        <i className="fas fa-chart-line fa-3x text-primary mb-3"></i>
        <h2 className="gradient-text">FinData IA-M.K</h2>
      </div>
      <div className="loading-spinner">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Chargement...</span>
        </div>
      </div>
      <p className="text-muted mt-3">Chargement de l'application...</p>
    </div>
  </div>
);

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      if (token) {
        // Vérifier la validité du token (optionnel)
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(false);
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

// Main App component
const App = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Simuler un temps de chargement initial
    const timer = setTimeout(() => {
      const token = localStorage.getItem('token');
      setIsAuthenticated(!!token);
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, []);

  // Écouter les changements d'authentification
  useEffect(() => {
    const handleStorageChange = () => {
      const token = localStorage.getItem('token');
      setIsAuthenticated(!!token);
    };

    // Écouter les changements de localStorage
    window.addEventListener('storage', handleStorageChange);
    
    // Écouter les changements personnalisés
    const handleAuthChange = () => {
      const token = localStorage.getItem('token');
      setIsAuthenticated(!!token);
    };
    
    window.addEventListener('authChange', handleAuthChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('authChange', handleAuthChange);
    };
  }, []);

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Route publique - Page d'accueil */}
          <Route 
            path="/" 
            element={
              isAuthenticated ? (
                <>
                  <Navigation />
                  <Home />
                </>
              ) : (
                <Home />
              )
            } 
          />
          
          {/* Routes publiques */}
          <Route 
            path="/login" 
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Login />
              )
            } 
          />
          
          <Route 
            path="/register" 
            element={
              isAuthenticated ? (
                <Navigate to="/dashboard" replace />
              ) : (
                <Register />
              )
            } 
          />
          
          {/* Routes protégées sans Navigation */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/scraping"
            element={
              <ProtectedRoute>
                <Scraping />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <Analytics />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/documentation"
            element={
              <ProtectedRoute>
                <Documentation />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/account"
            element={
              <ProtectedRoute>
                <Account />
              </ProtectedRoute>
            }
          />
          
          {/* Route 404 */}
          <Route
            path="*"
            element={
              <div className="error-page">
                <div className="error-content">
                  <i className="fas fa-exclamation-triangle fa-4x text-warning mb-4"></i>
                  <h1 className="gradient-text">Page non trouvée</h1>
                  <p className="text-muted mb-4">
                    La page que vous recherchez n'existe pas ou a été déplacée.
                  </p>
                  <button 
                    className="btn btn-primary"
                    onClick={() => window.history.back()}
                  >
                    <i className="fas fa-arrow-left me-2"></i>
                    Retour
                  </button>
                </div>
              </div>
            }
          />
        </Routes>
      </div>
    </Router>
  );
};

export default App; 