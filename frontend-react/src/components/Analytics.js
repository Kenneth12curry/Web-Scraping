import React, { useState, useEffect } from 'react';
import api from '../services/api';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState('all');

  useEffect(() => {
    fetchAnalytics();
  }, [selectedPeriod]);

  const fetchAnalytics = async () => {
    try {
      setIsRefreshing(true);
      const response = await api.get('/dashboard/analytics');
      
      if (response.data.success) {
        setAnalytics(response.data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des analytics:', error);
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

  /* const formatPercentage = (value, total) => {
    if (!total) return '0%';
    return ((value / total) * 100).toFixed(1) + '%';
  }; */

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Données simulées pour les graphiques
  const getChartData = () => {
    const periods = {
      week: {
        labels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
        requests: [45, 52, 38, 67, 89, 34, 56],
        success: [42, 48, 35, 62, 84, 31, 52],
        errors: [3, 4, 3, 5, 5, 3, 4]
      },
      month: {
        labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
        requests: [320, 450, 380, 520],
        success: [298, 418, 352, 485],
        errors: [22, 32, 28, 35]
      }
    };
    
    return periods[selectedPeriod] || periods.week;
  };

  const chartData = getChartData();

  // Filtrer l'historique selon le filtre sélectionné
  const filteredHistory = analytics?.scraping_history?.filter(item => {
    if (selectedFilter === 'all') return true;
    if (selectedFilter === 'success') return item.status === 'success';
    if (selectedFilter === 'error') return item.status !== 'success';
    return true;
  }) || [];

  if (loading) {
    return (
      <div className="analytics-container">
        <div className="loading-container">
          <div className="loading-content">
            <div className="loading-spinner">
              <div className="spinner"></div>
            </div>
            <p className="loading-text">Chargement des analytics...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-container">
      {/* Header professionnel amélioré */}
      <div className="analytics-header">
        <div className="header-content">
          <div className="header-left">
            <h1 className="analytics-title">
              <i className="fas fa-chart-line me-3"></i>
              Analytics Avancées
            </h1>
            <p className="analytics-subtitle">
              Analyse détaillée de vos performances et tendances en temps réel
            </p>
            <div className="analytics-meta">
              <span className="meta-item">
                <i className="fas fa-clock me-1"></i>
                Dernière mise à jour : {new Date().toLocaleTimeString('fr-FR')}
              </span>
              <span className="meta-item">
                <i className="fas fa-database me-1"></i>
                {analytics?.domain_stats?.length || 0} domaines analysés
              </span>
            </div>
          </div>
          <div className="header-right">
            <div className="period-selector">
              <label className="period-label">Période :</label>
              <select 
                className="period-select"
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
              >
                <option value="week">Cette semaine</option>
                <option value="month">Ce mois</option>
              </select>
            </div>
            <button 
              className={`btn btn-primary ${isRefreshing ? 'btn-loading' : ''}`}
              onClick={fetchAnalytics}
              disabled={isRefreshing}
            >
              <i className={`fas ${isRefreshing ? 'fa-spinner fa-spin' : 'fa-sync-alt'} me-2`}></i>
              {isRefreshing ? 'Actualisation...' : 'Actualiser'}
            </button>
          </div>
        </div>
      </div>

      {/* Message d'erreur amélioré */}
      {error && (
        <div className="alert alert-danger" role="alert">
          <i className="fas fa-exclamation-triangle me-2"></i>
          <strong>Erreur :</strong> {error}
          <button 
            className="btn btn-sm btn-outline-danger ms-3"
            onClick={fetchAnalytics}
          >
            <i className="fas fa-redo me-1"></i>
            Réessayer
          </button>
        </div>
      )}

      {/* Indicateurs de performance améliorés */}
      <div className="performance-indicators">
        <div className="indicator-card">
          <div className="indicator-header">
            <div className="indicator-icon">
              <i className="fas fa-tachometer-alt"></i>
            </div>
            <div className="indicator-trend positive">
              <i className="fas fa-arrow-up"></i>
              +15.2%
            </div>
          </div>
          <div className="indicator-content">
            <div className="indicator-number">98.5%</div>
            <div className="indicator-label">Taux de Réussite</div>
            <div className="indicator-description">
              Performance globale du système
            </div>
          </div>
          <div className="indicator-progress">
            <div className="progress">
              <div className="progress-bar bg-success" style={{ width: '98.5%' }}></div>
            </div>
          </div>
        </div>

        <div className="indicator-card">
          <div className="indicator-header">
            <div className="indicator-icon success">
              <i className="fas fa-clock"></i>
            </div>
            <div className="indicator-trend positive">
              <i className="fas fa-arrow-down"></i>
              -12.8%
            </div>
          </div>
          <div className="indicator-content">
            <div className="indicator-number">1.2s</div>
            <div className="indicator-label">Temps de Réponse</div>
            <div className="indicator-description">
              Moyenne des requêtes
            </div>
          </div>
          <div className="indicator-progress">
            <div className="progress">
              <div className="progress-bar bg-info" style={{ width: '85%' }}></div>
            </div>
          </div>
        </div>

        <div className="indicator-card">
          <div className="indicator-header">
            <div className="indicator-icon warning">
              <i className="fas fa-exclamation-triangle"></i>
            </div>
            <div className="indicator-trend negative">
              <i className="fas fa-arrow-up"></i>
              +3.1%
            </div>
          </div>
          <div className="indicator-content">
            <div className="indicator-number">1.5%</div>
            <div className="indicator-label">Taux d'Erreur</div>
            <div className="indicator-description">
              Requêtes échouées
            </div>
          </div>
          <div className="indicator-progress">
            <div className="progress">
              <div className="progress-bar bg-warning" style={{ width: '1.5%' }}></div>
            </div>
          </div>
        </div>

        <div className="indicator-card">
          <div className="indicator-header">
            <div className="indicator-icon info">
              <i className="fas fa-users"></i>
            </div>
            <div className="indicator-trend positive">
              <i className="fas fa-arrow-up"></i>
              +8.7%
            </div>
          </div>
          <div className="indicator-content">
            <div className="indicator-number">2.4K</div>
            <div className="indicator-label">Requêtes/Jour</div>
            <div className="indicator-description">
              Volume quotidien moyen
            </div>
          </div>
          <div className="indicator-progress">
            <div className="progress">
              <div className="progress-bar" style={{ width: '75%' }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Graphiques interactifs améliorés */}
      <div className="charts-section">
        <div className="row">
          <div className="col-lg-8">
            <div className="dashboard-card">
              <div className="card-header">
                <div className="card-title">
                  <i className="fas fa-chart-area me-2"></i>
                  Évolution des Requêtes
                </div>
                <div className="card-actions">
                  <div className="chart-legend">
                    <span className="legend-item">
                      <span className="legend-color requests"></span>
                      Total
                    </span>
                    <span className="legend-item">
                      <span className="legend-color success"></span>
                      Succès
                    </span>
                    <span className="legend-item">
                      <span className="legend-color errors"></span>
                      Erreurs
                    </span>
                  </div>
                </div>
              </div>
              <div className="chart-container">
                <div className="chart-bars">
                  {chartData.labels.map((label, index) => (
                    <div key={index} className="chart-column">
                      <div className="chart-bars-group">
                        <div 
                          className="chart-bar requests"
                          style={{ height: `${(chartData.requests[index] / Math.max(...chartData.requests)) * 100}%` }}
                          title={`Total: ${chartData.requests[index]} requêtes`}
                        ></div>
                        <div 
                          className="chart-bar success"
                          style={{ height: `${(chartData.success[index] / Math.max(...chartData.success)) * 100}%` }}
                          title={`Succès: ${chartData.success[index]} requêtes`}
                        ></div>
                        <div 
                          className="chart-bar errors"
                          style={{ height: `${(chartData.errors[index] / Math.max(...chartData.errors)) * 100}%` }}
                          title={`Erreurs: ${chartData.errors[index]} requêtes`}
                        ></div>
                      </div>
                      <div className="chart-label">{label}</div>
                      <div className="chart-values">
                        <div className="value requests">{chartData.requests[index]}</div>
                        <div className="value success">{chartData.success[index]}</div>
                        <div className="value errors">{chartData.errors[index]}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="col-lg-4">
            <div className="dashboard-card">
              <div className="card-header">
                <div className="card-title">
                  <i className="fas fa-chart-pie me-2"></i>
                  Répartition par Statut
                </div>
              </div>
              <div className="pie-chart-container">
                <div className="pie-chart">
                  <div className="pie-segment success" style={{ transform: 'rotate(0deg)' }}>
                    <div className="segment-label">Succès</div>
                    <div className="segment-value">98.5%</div>
                  </div>
                  <div className="pie-segment warning" style={{ transform: 'rotate(354deg)' }}>
                    <div className="segment-label">Erreurs</div>
                    <div className="segment-value">1.5%</div>
                  </div>
                </div>
                <div className="pie-legend">
                  <div className="legend-item">
                    <span className="legend-color success"></span>
                    <span className="legend-text">Succès (98.5%)</span>
                  </div>
                  <div className="legend-item">
                    <span className="legend-color warning"></span>
                    <span className="legend-text">Erreurs (1.5%)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tendances en temps réel améliorées */}
      <div className="trends-section">
        <div className="dashboard-card">
          <div className="card-header">
            <div className="card-title">
              <i className="fas fa-chart-line me-2"></i>
              Tendances Récentes
            </div>
            <div className="card-actions">
              <span className="trend-indicator">
                <span className="trend-dot"></span>
                En temps réel
              </span>
            </div>
          </div>
          <div className="trends-grid">
            <div className="trend-item positive">
              <div className="trend-icon">
                <i className="fas fa-arrow-up"></i>
              </div>
              <div className="trend-content">
                <div className="trend-label">Requêtes par heure</div>
                <div className="trend-value">+12.5%</div>
                <div className="trend-description">vs période précédente</div>
              </div>
            </div>

            <div className="trend-item positive">
              <div className="trend-icon">
                <i className="fas fa-arrow-up"></i>
              </div>
              <div className="trend-content">
                <div className="trend-label">Taux de réussite</div>
                <div className="trend-value">+2.1%</div>
                <div className="trend-description">amélioration continue</div>
              </div>
            </div>

            <div className="trend-item negative">
              <div className="trend-icon">
                <i className="fas fa-arrow-down"></i>
              </div>
              <div className="trend-content">
                <div className="trend-label">Temps de réponse</div>
                <div className="trend-value">-8.3%</div>
                <div className="trend-description">optimisation en cours</div>
              </div>
            </div>

            <div className="trend-item positive">
              <div className="trend-icon">
                <i className="fas fa-arrow-up"></i>
              </div>
              <div className="trend-content">
                <div className="trend-label">Utilisateurs actifs</div>
                <div className="trend-value">+15.7%</div>
                <div className="trend-description">croissance soutenue</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Top domaines amélioré */}
      {analytics && (
        <div className="domains-section">
          <div className="dashboard-card">
            <div className="card-header">
              <div className="card-title">
                <i className="fas fa-globe me-2"></i>
                Top Domaines Analysés
              </div>
              <div className="card-actions">
                <button className="btn btn-sm btn-outline-primary">
                  <i className="fas fa-external-link-alt me-1"></i>
                  Voir tout
                </button>
              </div>
            </div>
            <div className="domains-table">
              <div className="table-header">
                <div className="table-cell">Rang</div>
                <div className="table-cell">Domaine</div>
                <div className="table-cell">Requêtes</div>
                <div className="table-cell">Succès</div>
                <div className="table-cell">Taux</div>
                <div className="table-cell">Tendance</div>
              </div>
              {analytics.domain_stats?.slice(0, 10).map((domain, index) => (
                <div key={index} className="table-row">
                  <div className="table-cell">
                    <div className="rank-badge">#{index + 1}</div>
                  </div>
                  <div className="table-cell">
                    <div className="domain-info">
                      <div className="domain-name">{domain.domain}</div>
                      <div className="domain-url">{domain.domain}</div>
                    </div>
                  </div>
                  <div className="table-cell">
                    <div className="requests-count">{formatNumber(domain.requests_count)}</div>
                  </div>
                  <div className="table-cell">
                    <div className="success-count">
                      {formatNumber(domain.requests_count - (domain.requests_count * 0.02))}
                    </div>
                  </div>
                  <div className="table-cell">
                    <div className="success-rate">98.0%</div>
                  </div>
                  <div className="table-cell">
                    <div className="trend-indicator positive">
                      <i className="fas fa-arrow-up"></i>
                      +5.2%
                    </div>
                  </div>
                </div>
              ))}
              {(!analytics.domain_stats || analytics.domain_stats.length === 0) && (
                <div className="empty-state">
                  <i className="fas fa-globe fa-2x"></i>
                  <h4>Aucun domaine analysé</h4>
                  <p>Les domaines apparaîtront ici après vos premiers scrapings</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Historique des scraping amélioré */}
      <div className="history-section">
        <div className="dashboard-card">
          <div className="card-header">
            <div className="card-title">
              <i className="fas fa-history me-2"></i>
              Historique des Scraping
            </div>
            <div className="card-actions">
              <div className="status-filter">
                <button 
                  className={`filter-btn ${selectedFilter === 'all' ? 'active' : ''}`}
                  onClick={() => setSelectedFilter('all')}
                >
                  Tous ({analytics?.scraping_history?.length || 0})
                </button>
                <button 
                  className={`filter-btn ${selectedFilter === 'success' ? 'active' : ''}`}
                  onClick={() => setSelectedFilter('success')}
                >
                  Succès ({analytics?.scraping_history?.filter(item => item.status === 'success').length || 0})
                </button>
                <button 
                  className={`filter-btn ${selectedFilter === 'error' ? 'active' : ''}`}
                  onClick={() => setSelectedFilter('error')}
                >
                  Erreurs ({analytics?.scraping_history?.filter(item => item.status !== 'success').length || 0})
                </button>
              </div>
            </div>
          </div>
          <div className="history-list">
            {filteredHistory.slice(0, 15).map((item, index) => (
              <div key={index} className="history-item">
                <div className="history-icon">
                  <i className={`fas fa-${item.status === 'success' ? 'check' : 'times'}`}></i>
                </div>
                <div className="history-content">
                  <div className="history-title">{item.url}</div>
                  <div className="history-meta">
                    <span className="history-method">
                      <i className="fas fa-cog me-1"></i>
                      {item.method}
                    </span>
                    <span className="history-articles">
                      <i className="fas fa-file-alt me-1"></i>
                      {item.articles_count} articles
                    </span>
                    <span className="history-time">
                      <i className="fas fa-clock me-1"></i>
                      {formatDate(item.timestamp)}
                    </span>
                  </div>
                </div>
                <div className="history-status">
                  <span className={`badge bg-${item.status === 'success' ? 'success' : 'danger'}`}>
                    {item.status === 'success' ? 'Succès' : 'Erreur'}
                  </span>
                </div>
              </div>
            ))}
            {filteredHistory.length === 0 && (
              <div className="empty-state">
                <i className="fas fa-inbox fa-2x"></i>
                <h4>Aucun historique de scraping</h4>
                <p>Les opérations de scraping apparaîtront ici</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics; 