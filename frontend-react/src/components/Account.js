import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Account = ({ user }) => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadAccountData();
  }, []);

  const loadAccountData = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      setError('Erreur lors du chargement des données du compte');
      console.error('Account error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading-spinner">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Chargement...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header fade-in">
        <h1 className="dashboard-title">Mon Compte</h1>
        <p className="dashboard-subtitle">
          Gérez vos informations personnelles et votre abonnement
        </p>
      </div>

      {error && (
        <div className="alert alert-danger fade-in" role="alert">
          {error}
        </div>
      )}

      <div className="row">
        {/* Informations utilisateur */}
        <div className="col-lg-6">
          <div className="dashboard-card fade-in">
            <h5 className="card-title">
              <i className="fas fa-user card-icon"></i>
              Informations utilisateur
            </h5>
            
            <div className="mb-3">
              <strong>Nom d'utilisateur :</strong>
              <span className="ms-2">{user?.username || 'Non défini'}</span>
            </div>
            
            <div className="mb-3">
              <strong>Rôle :</strong>
              <span className="badge bg-primary ms-2">{user?.role || 'Utilisateur'}</span>
            </div>
            
            <div className="mb-3">
              <strong>Email :</strong>
              <span className="ms-2">{stats?.subscription?.owner || 'Non défini'}</span>
            </div>
            
            <div className="mb-3">
              <strong>Date de création :</strong>
              <span className="ms-2">26.06.2025</span>
            </div>
            
            <div className="mb-3">
              <strong>Dernière connexion :</strong>
              <span className="ms-2">{new Date().toLocaleString('fr-FR')}</span>
            </div>
          </div>
        </div>

        {/* Abonnement */}
        <div className="col-lg-6">
          <div className="dashboard-card fade-in">
            <h5 className="card-title">
              <i className="fas fa-crown card-icon"></i>
              Détails de l'abonnement
            </h5>
            
            <div className="mb-3">
              <strong>Plan actuel :</strong>
              <span className="badge bg-success ms-2">{stats?.subscription?.plan || 'Free'}</span>
            </div>
            
            <div className="mb-3">
              <strong>Utilisation API :</strong>
              <div className="progress mt-2">
                <div 
                  className="progress-bar bg-primary" 
                  style={{ 
                    width: `${((stats?.subscription?.api_calls_used || 0) / (stats?.subscription?.api_calls_limit || 1000)) * 100}%` 
                  }}
                ></div>
              </div>
              <small className="text-muted">
                {stats?.subscription?.api_calls_used || 0} / {stats?.subscription?.api_calls_limit || 1000} appels utilisés
              </small>
            </div>
            
            <div className="mb-3">
              <strong>Appels simultanés :</strong>
              <div className="progress mt-2">
                <div 
                  className="progress-bar bg-info" 
                  style={{ 
                    width: `${((stats?.subscription?.concurrent_calls_used || 0) / (stats?.subscription?.concurrent_calls_limit || 5)) * 100}%` 
                  }}
                ></div>
              </div>
              <small className="text-muted">
                {stats?.subscription?.concurrent_calls_used || 0} / {stats?.subscription?.concurrent_calls_limit || 5} appels simultanés
              </small>
            </div>
            
            <div className="mb-3">
              <strong>Date de renouvellement :</strong>
              <span className="ms-2">{stats?.subscription?.renew_date}</span>
            </div>
            
            <div className="mb-3">
              <strong>Renouvellement automatique :</strong>
              <span className="badge bg-success ms-2">Activé</span>
            </div>
          </div>
        </div>
      </div>

      {/* Configuration API */}
      <div className="dashboard-card fade-in">
        <h5 className="card-title">
          <i className="fas fa-cog card-icon"></i>
          Configuration API
        </h5>
        
        <div className="row">
          <div className="col-md-6">
            <h6>Scrape.do</h6>
            <div className="mb-3">
              <strong>Statut :</strong>
              {stats?.api_config?.has_scrapedo ? (
                <span className="badge bg-success ms-2">Configuré</span>
              ) : (
                <span className="badge bg-danger ms-2">Non configuré</span>
              )}
            </div>
            
            {stats?.api_config?.scrapedo_token && (
              <div className="mb-3">
                <strong>Token :</strong>
                <code className="d-block mt-2 p-2 bg-light rounded">
                  {stats.api_config.scrapedo_token}
                </code>
              </div>
            )}
            
            <div className="mb-3">
              <strong>Fonctionnalités :</strong>
              <ul className="mt-2">
                <li>Contournement anti-bot</li>
                <li>Rendu JavaScript</li>
                <li>Proxies premium</li>
                <li>Gestion des timeouts</li>
              </ul>
            </div>
          </div>
          
          <div className="col-md-6">
            <h6>Groq AI</h6>
            <div className="mb-3">
              <strong>Statut :</strong>
              {stats?.api_config?.has_groq ? (
                <span className="badge bg-success ms-2">Configuré</span>
              ) : (
                <span className="badge bg-danger ms-2">Non configuré</span>
              )}
            </div>
            
            {stats?.api_config?.groq_token && (
              <div className="mb-3">
                <strong>Token :</strong>
                <code className="d-block mt-2 p-2 bg-light rounded">
                  {stats.api_config.groq_token}
                </code>
              </div>
            )}
            
            <div className="mb-3">
              <strong>Fonctionnalités :</strong>
              <ul className="mt-2">
                <li>Analyse de contenu IA</li>
                <li>Résumé automatique</li>
                <li>Extraction intelligente</li>
                <li>Classification d'articles</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Statistiques d'utilisation */}
      <div className="dashboard-card fade-in">
        <h5 className="card-title">
          <i className="fas fa-chart-bar card-icon"></i>
          Statistiques d'utilisation
        </h5>
        
        <div className="row">
          <div className="col-md-6">
            <h6>Requêtes totales</h6>
            <div className="stat-card">
              <div className="stat-number">{stats?.user_stats?.total_requests || 0}</div>
              <div className="stat-label">Requêtes effectuées</div>
            </div>
          </div>
          
          <div className="col-md-6">
            <h6>Requêtes réussies</h6>
            <div className="stat-card">
              <div className="stat-number">{stats?.user_stats?.successful_requests || 0}</div>
              <div className="stat-label">Requêtes réussies</div>
            </div>
          </div>
        </div>
        
        {stats?.user_stats?.top_domains && stats.user_stats.top_domains.length > 0 && (
          <div className="mt-4">
            <h6>Domaines les plus utilisés</h6>
            <div className="table-responsive">
              <table className="table">
                <thead>
                  <tr>
                    <th>Domaine</th>
                    <th>Requêtes</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.user_stats.top_domains.map((domain, index) => (
                    <tr key={index}>
                      <td>{domain.domain}</td>
                      <td>{domain.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Actions du compte */}
      <div className="dashboard-card fade-in">
        <h5 className="card-title">
          <i className="fas fa-tools card-icon"></i>
          Actions du compte
        </h5>
        
        <div className="row">
          <div className="col-md-4">
            <button className="btn btn-outline-primary w-100 mb-3">
              <i className="fas fa-key me-2"></i>
              Changer le mot de passe
            </button>
          </div>
          
          <div className="col-md-4">
            <button className="btn btn-outline-info w-100 mb-3">
              <i className="fas fa-download me-2"></i>
              Exporter mes données
            </button>
          </div>
          
          <div className="col-md-4">
            <button className="btn btn-outline-warning w-100 mb-3">
              <i className="fas fa-cog me-2"></i>
              Paramètres avancés
            </button>
          </div>
        </div>
        
        <div className="alert alert-info">
          <strong>Note :</strong> Pour modifier votre abonnement ou obtenir de l'aide, 
          contactez-nous à <strong>diandiallo974@gmail.com</strong>
        </div>
      </div>
    </div>
  );
};

export default Account; 