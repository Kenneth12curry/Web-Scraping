import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeSection, setActiveSection] = useState('overview');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    fetchData();
    
    // Mettre à jour l'heure toutes les minutes
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);

    return () => clearInterval(timeInterval);
  }, []);

  const fetchData = async () => {
    try {
      setIsRefreshing(true);
      const [statsResponse, analyticsResponse] = await Promise.all([
        api.get('/dashboard/stats'),
        api.get('/dashboard/analytics')
      ]);

      if (statsResponse.data.success) {
        setStats(statsResponse.data.user_stats);
      }
      
      if (analyticsResponse.data.success) {
        setAnalytics({
          ...analyticsResponse.data,
          recent_requests: statsResponse.data.user_stats.recent_requests || []
        });
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
      setError('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'success';
      case 'error': return 'danger';
      case 'warning': return 'warning';
      default: return 'info';
    }
  };

  // Données simulées pour les graphiques
  const getChartData = () => {
    const days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];
    const requests = [45, 52, 38, 67, 89, 34, 56];
    const success = [42, 48, 35, 62, 84, 31, 52];
    
    return { days, requests, success };
  };

  // const chartData = getChartData();

  // Ajout d'une variable pour la description des échecs
  const failedDescription = stats && stats.total_requests
    ? `${((stats.failed_requests || 0) / stats.total_requests * 100).toFixed(1)}% d'échecs`
    : '0% d\'échecs';

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-container">
          <div className="loading-content">
            <div className="loading-spinner">
              <div className="spinner"></div>
            </div>
            <p className="loading-text">Chargement du tableau de bord...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Sidebar Navigation */}
      <div className={`dashboard-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <i className="fas fa-chart-line"></i>
            {!sidebarCollapsed && <span>FinData IA-M.K</span>}
          </div>
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          >
            <i className={`fas fa-${sidebarCollapsed ? 'chevron-right' : 'chevron-left'}`}></i>
          </button>
        </div>
        
        <nav className="sidebar-nav">
          <div className="nav-section">
            <div className="nav-section-title">
              {!sidebarCollapsed && <span>Tableau de Bord</span>}
            </div>
            <ul className="nav-list">
              <li className="nav-item">
                <button 
                  className={`nav-link ${activeSection === 'overview' ? 'active' : ''}`}
                  onClick={() => setActiveSection('overview')}
                >
                  <i className="fas fa-tachometer-alt"></i>
                  {!sidebarCollapsed && <span>Vue d'ensemble</span>}
                </button>
              </li>
              <li className="nav-item">
                <button 
                  className={`nav-link ${activeSection === 'analytics' ? 'active' : ''}`}
                  onClick={() => setActiveSection('analytics')}
                >
                  <i className="fas fa-chart-bar"></i>
                  {!sidebarCollapsed && <span>Analytics</span>}
                </button>
              </li>
              <li className="nav-item">
                <button 
                  className={`nav-link ${activeSection === 'scraping' ? 'active' : ''}`}
                  onClick={() => setActiveSection('scraping')}
                >
                  <i className="fas fa-spider"></i>
                  {!sidebarCollapsed && <span>Scraping</span>}
                </button>
              </li>
              <li className="nav-item">
                <button 
                  className={`nav-link ${activeSection === 'exports' ? 'active' : ''}`}
                  onClick={() => setActiveSection('exports')}
                >
                  <i className="fas fa-file-export"></i>
                  {!sidebarCollapsed && <span>Exports</span>}
                </button>
              </li>
            </ul>
          </div>
          
          <div className="nav-section">
            <div className="nav-section-title">
              {!sidebarCollapsed && <span>Outils</span>}
            </div>
            <ul className="nav-list">
              <li className="nav-item">
                <Link to="/documentation" className="nav-link">
                  <i className="fas fa-book"></i>
                  {!sidebarCollapsed && <span>Documentation</span>}
                </Link>
              </li>
              <li className="nav-item">
                <Link to="/account" className="nav-link">
                  <i className="fas fa-user-cog"></i>
                  {!sidebarCollapsed && <span>Mon Compte</span>}
                </Link>
              </li>
            </ul>
          </div>
        </nav>
      </div>

      {/* Main Content */}
      <div className="dashboard-main">
        <div className="dashboard-content">
          {/* Message d'erreur */}
          {error && (
            <div className="alert alert-danger" role="alert">
              <i className="fas fa-exclamation-triangle me-2"></i>
              {error}
              <button 
                className="btn btn-sm btn-outline-danger ms-3"
                onClick={fetchData}
              >
                <i className="fas fa-redo me-1"></i>
                Réessayer
              </button>
            </div>
          )}

          {/* Titre et sous-titre de section */}
          <div className="dashboard-section-header mb-4">
            <h1 className="page-title">
              {activeSection === 'overview' && "Vue d'ensemble"}
              {activeSection === 'analytics' && 'Analytics'}
              {activeSection === 'scraping' && 'Scraping'}
              {activeSection === 'exports' && 'Exports'}
            </h1>
            <p className="page-subtitle">
              {activeSection === 'overview' && "Vue d'ensemble de vos performances et statistiques"}
              {activeSection === 'analytics' && 'Analysez vos données avec des graphiques interactifs'}
              {activeSection === 'scraping' && 'Gérez vos tâches de scraping et surveillance'}
              {activeSection === 'exports' && 'Exportez vos données dans différents formats'}
            </p>
            <div className="dashboard-header-actions mt-3">
              <div className="time-display">
                <i className="fas fa-clock"></i>
                <span>{currentTime.toLocaleTimeString('fr-FR', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}</span>
              </div>
              <button 
                className={`btn btn-primary refresh-btn ${isRefreshing ? 'loading' : ''}`}
                onClick={fetchData}
                disabled={isRefreshing}
                title="Actualiser les données"
              >
                <i className={`fas ${isRefreshing ? 'fa-spinner fa-spin' : 'fa-sync-alt'}`}></i>
                {!isRefreshing && <span>Actualiser</span>}
              </button>
            </div>
          </div>

          {/* Stats Cards professionnelles */}
          {stats && activeSection === 'overview' && (
            <div className="row">
              <div className="col-lg-3 col-md-6 mb-4">
                <div className="stat-card h-100">
                  <div className="stat-header">
                    <div className="stat-icon">
                      <i className="fas fa-rocket"></i>
                    </div>
                    <div className="stat-trend positive">
                      <i className="fas fa-arrow-up"></i>
                      +12.5%
                    </div>
                  </div>
                  <div className="stat-content">
                    <div className="stat-number">{formatNumber(stats.total_requests || 0)}</div>
                    <div className="stat-label">Requêtes Total</div>
                    <div className="stat-description">
                      {stats.weekly_history?.length > 0 ? `${stats.weekly_history[stats.weekly_history.length - 1].count} aujourd'hui` : 'Aucune donnée récente'}
                    </div>
                  </div>
                  <div className="stat-progress">
                    <div className="progress">
                      <div className="progress-bar" style={{ width: '75%' }}></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-lg-3 col-md-6 mb-4">
                <div className="stat-card h-100">
                  <div className="stat-header">
                    <div className="stat-icon success">
                      <i className="fas fa-check-circle"></i>
                    </div>
                    <div className="stat-trend positive">
                      <i className="fas fa-arrow-up"></i>
                      +8.2%
                    </div>
                  </div>
                  <div className="stat-content">
                    <div className="stat-number">{formatNumber(stats.successful_requests || 0)}</div>
                    <div className="stat-label">Succès</div>
                    <div className="stat-description">
                      {stats.success_rate ? `${stats.success_rate.toFixed(1)}% de réussite` : '0% de réussite'}
                    </div>
                  </div>
                  <div className="stat-progress">
                    <div className="progress">
                      <div className="progress-bar bg-success" style={{ width: `${stats.success_rate || 0}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-lg-3 col-md-6 mb-4">
                <div className="stat-card h-100">
                  <div className="stat-header">
                    <div className="stat-icon warning">
                      <i className="fas fa-exclamation-triangle"></i>
                    </div>
                    <div className="stat-trend negative">
                      <i className="fas fa-arrow-down"></i>
                      -5.1%
                    </div>
                  </div>
                  <div className="stat-content">
                    <div className="stat-number">{formatNumber(stats.failed_requests || 0)}</div>
                    <div className="stat-label">Échecs</div>
                    <div className="stat-description">
                      {failedDescription}
                    </div>
                  </div>
                  <div className="stat-progress">
                    <div className="progress">
                      <div className="progress-bar bg-warning" style={{ width: `${Math.min((stats.failed_requests || 0) / Math.max(stats.total_requests || 1, 1) * 100, 100)}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="col-lg-3 col-md-6 mb-4">
                <div className="stat-card h-100">
                  <div className="stat-header">
                    <div className="stat-icon info">
                      <i className="fas fa-tachometer-alt"></i>
                    </div>
                    <div className="stat-trend positive">
                      <i className="fas fa-arrow-up"></i>
                      +15.3%
                    </div>
                  </div>
                  <div className="stat-content">
                    <div className="stat-number">{(stats.success_rate || 0).toFixed(1)}%</div>
                    <div className="stat-label">Performance</div>
                    <div className="stat-description">
                      {stats.total_requests
                        ? `${stats.successful_requests || 0}/${stats.total_requests} requêtes`
                        : '0/0 requêtes'}
                    </div>
                  </div>
                  <div className="stat-progress">
                    <div className="progress">
                      <div className="progress-bar bg-info" style={{ width: `${(stats.success_rate || 0) * 100}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;