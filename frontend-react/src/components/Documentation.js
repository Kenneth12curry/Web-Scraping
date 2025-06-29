import React, { useState } from 'react';

const Documentation = () => {
  const [activeTab, setActiveTab] = useState('guide');
  const [expandedFaq, setExpandedFaq] = useState(null);

  const faqData = [
    {
      id: 1,
      question: "Comment fonctionne le scraping ?",
      answer: "Le scraping utilise l'API Scrape.do pour contourner les protections anti-bot et extraire le contenu des sites web. En cas d'échec, il bascule automatiquement sur la méthode requests standard, puis Selenium et Playwright si nécessaire."
    },
    {
      id: 2,
      question: "Quels types de sites puis-je scraper ?",
      answer: "Vous pouvez scraper la plupart des sites web publics. Les sites avec des protections anti-bot avancées peuvent nécessiter l'utilisation de Scrape.do pour un meilleur taux de succès. L'application supporte les sites d'actualités, blogs, e-commerce et sites d'entreprise."
    },
    {
      id: 3,
      question: "Y a-t-il des limites d'utilisation ?",
      answer: "Oui, il y a des limites de rate limiting : 10 scrapings par minute et 200 requêtes par jour. Ces limites protègent nos serveurs et respectent les conditions d'utilisation des APIs. Les utilisateurs premium bénéficient de limites plus élevées."
    },
    {
      id: 4,
      question: "Comment exporter mes données ?",
      answer: "Après un scraping réussi, vous pouvez exporter vos données au format JSON ou CSV en utilisant les boutons d'export dans la section des résultats. Les données incluent les titres, URLs, contenus et résumés générés par l'IA."
    },
    {
      id: 5,
      question: "Mes données sont-elles sécurisées ?",
      answer: "Oui, toutes les communications sont chiffrées en HTTPS, et les tokens d'authentification sont stockés de manière sécurisée. Nous ne conservons que les métadonnées des scrapings et respectons le RGPD."
    },
    {
      id: 6,
      question: "Puis-je automatiser mes scrapings ?",
      answer: "Actuellement, les scrapings doivent être initiés manuellement. Une fonctionnalité de planification et d'API webhook est prévue dans les prochaines versions pour permettre l'automatisation complète."
    },
    {
      id: 7,
      question: "Comment fonctionne l'IA pour les résumés ?",
      answer: "L'application utilise l'API Groq avec le modèle Llama3-8b pour générer des résumés automatiques des articles extraits. Les résumés sont concis et capturent les points essentiels du contenu."
    },
    {
      id: 8,
      question: "Que faire si un scraping échoue ?",
      answer: "En cas d'échec, l'application essaie automatiquement différentes méthodes (Scrape.do, requests, Selenium, Playwright). Si toutes échouent, vérifiez l'URL et les paramètres, puis réessayez. Contactez le support si le problème persiste."
    }
  ];

  const apiExamples = [
    {
      title: "Extraction d'articles",
      description: "Extraire des articles d'un site web avec résumés IA",
      method: "POST",
      endpoint: "/api/scraping/extract",
      request: {
        url: "https://example.com",
        method: "scrapedo",
        max_articles: 20
      },
      response: {
        success: true,
        articles: [
          {
            title: "Titre de l'article",
            url: "https://example.com/article",
            content: "Contenu de l'article...",
            resume: "Résumé généré par l'IA...",
            date: "2024-01-01"
          }
        ],
        total_articles: 1,
        method_used: "scrapedo+ia-fallback",
        domain: "example.com",
        processing_time: "2.34s"
      }
    },
    {
      title: "Statistiques du dashboard",
      description: "Récupérer les statistiques utilisateur complètes",
      method: "GET",
      endpoint: "/api/dashboard/stats",
      request: {},
      response: {
        success: true,
        user_stats: {
          general: {
            total_requests: 150,
            successful_requests: 145,
            failed_requests: 5
          },
          endpoints: [
            {
              endpoint: "/api/scraping/extract",
              count: 50,
              success_count: 48
            }
          ],
          scraping: {
            total_scraping: 25,
            successful_scraping: 23,
            total_articles: 450
          }
        },
        api_config: {
          has_scrapedo: true,
          has_groq: true
        }
      }
    },
    {
      title: "Analytics détaillées",
      description: "Récupérer les analytics complètes avec historique",
      method: "GET",
      endpoint: "/api/dashboard/analytics",
      request: {},
      response: {
        success: true,
        domain_stats: [
          {
            domain: "example.com",
            status_code: 200,
            requests_count: 50
          }
        ],
        scraping_history: [
          {
            url: "https://example.com",
            method: "scrapedo",
            articles_count: 10,
            status: "success",
            timestamp: "2024-01-01T12:00:00Z"
          }
        ]
      }
    },
    {
      title: "Authentification",
      description: "Se connecter et obtenir un token JWT",
      method: "POST",
      endpoint: "/api/auth/login",
      request: {
        username: "admin",
        password: "admin123"
      },
      response: {
        success: true,
        access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        user: {
          username: "admin",
          role: "admin",
          email: "admin@findata.com"
        }
      }
    }
  ];

  const renderApiExample = (example) => (
    <div key={example.title} className="api-example mb-4">
      <h4 className="api-title">
        <span className={`badge bg-${example.method === 'GET' ? 'success' : 'primary'} me-2`}>
          {example.method}
        </span>
        {example.title}
      </h4>
      <p className="text-muted mb-2">{example.description}</p>
      
      <div className="api-endpoint mb-3">
        <code className="bg-light p-2 rounded d-block">
          {example.endpoint}
        </code>
      </div>

      <div className="row">
        <div className="col-md-6">
          <h6>Request</h6>
          <pre className="bg-dark text-light p-3 rounded">
            <code>{JSON.stringify(example.request, null, 2)}</code>
          </pre>
        </div>
        <div className="col-md-6">
          <h6>Response</h6>
          <pre className="bg-dark text-light p-3 rounded">
            <code>{JSON.stringify(example.response, null, 2)}</code>
          </pre>
        </div>
      </div>
    </div>
  );

  return (
    <div className="dashboard-container">
      {/* Header amélioré */}
      <div className="dashboard-header animate-fade-in-down">
        <h1 className="dashboard-title">
          <i className="fas fa-book me-3 text-primary"></i>
          Documentation Complète
        </h1>
        <p className="dashboard-subtitle">
          Guide d'utilisation, référence API et support technique
        </p>
        <div className="documentation-meta">
          <span className="meta-item">
            <i className="fas fa-clock me-1"></i>
            Dernière mise à jour : {new Date().toLocaleDateString('fr-FR')}
          </span>
          <span className="meta-item">
            <i className="fas fa-code me-1"></i>
            Version API : 1.0.0
          </span>
        </div>
      </div>

      {/* Navigation des onglets améliorée */}
      <div className="documentation-nav mb-4">
        <div className="btn-group" role="group">
          <button
            type="button"
            className={`btn btn-outline-primary ${activeTab === 'guide' ? 'active' : ''}`}
            onClick={() => setActiveTab('guide')}
          >
            <i className="fas fa-user-guide me-2"></i>
            Guide d'utilisation
          </button>
          <button
            type="button"
            className={`btn btn-outline-primary ${activeTab === 'api' ? 'active' : ''}`}
            onClick={() => setActiveTab('api')}
          >
            <i className="fas fa-code me-2"></i>
            Référence API
          </button>
          <button
            type="button"
            className={`btn btn-outline-primary ${activeTab === 'faq' ? 'active' : ''}`}
            onClick={() => setActiveTab('faq')}
          >
            <i className="fas fa-question-circle me-2"></i>
            FAQ ({faqData.length})
          </button>
        </div>
      </div>

      {/* Contenu des onglets */}
      <div className="documentation-content">
        {/* Guide d'utilisation amélioré */}
        {activeTab === 'guide' && (
          <div className="dashboard-card animate-slide-in-up">
            <div className="card-title">
              <i className="fas fa-user-guide card-icon"></i>
              Guide d'utilisation complet
            </div>
            
            <div className="guide-section mb-4">
              <h3>🚀 Premiers pas</h3>
              <p>Bienvenue dans FinData IA-M.K ! Cette application vous permet d'extraire des données de sites web de manière professionnelle et sécurisée avec l'aide de l'intelligence artificielle.</p>
              
              <div className="step-list">
                <div className="step-item">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <h5>Connexion</h5>
                    <p>Connectez-vous avec vos identifiants (admin / admin123 pour la démo) ou créez un nouveau compte.</p>
                  </div>
                </div>
                
                <div className="step-item">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <h5>Navigation</h5>
                    <p>Utilisez la barre de navigation pour accéder aux différentes fonctionnalités : Dashboard, Scraping, Analytics, Documentation.</p>
                  </div>
                </div>
                
                <div className="step-item">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <h5>Scraping</h5>
                    <p>Allez dans l'onglet "Scraping" pour commencer à extraire des données avec l'aide de l'IA.</p>
                  </div>
                </div>

                <div className="step-item">
                  <div className="step-number">4</div>
                  <div className="step-content">
                    <h5>Analytics</h5>
                    <p>Consultez vos performances et analyses dans l'onglet "Analytics" pour optimiser vos extractions.</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="guide-section mb-4">
              <h3>🕷️ Extraction de données avancée</h3>
              <p>L'extraction de données se fait en plusieurs étapes avec des méthodes de fallback intelligentes :</p>
              
              <div className="feature-grid">
                <div className="feature-item">
                  <i className="fas fa-link fa-2x text-primary mb-3"></i>
                  <h5>1. Saisie de l'URL</h5>
                  <p>Entrez l'URL du site que vous souhaitez scraper. L'application ajoutera automatiquement le protocole HTTPS si nécessaire et validera l'URL.</p>
                </div>
                
                <div className="feature-item">
                  <i className="fas fa-cog fa-2x text-primary mb-3"></i>
                  <h5>2. Configuration avancée</h5>
                  <p>Choisissez la méthode d'extraction : Scrape.do (recommandé), Requests standard, Selenium ou Playwright. Configurez le nombre maximum d'articles.</p>
                </div>
                
                <div className="feature-item">
                  <i className="fas fa-play fa-2x text-primary mb-3"></i>
                  <h5>3. Lancement intelligent</h5>
                  <p>Cliquez sur "Démarrer l'extraction" et suivez la progression en temps réel avec fallback automatique en cas d'échec.</p>
                </div>
                
                <div className="feature-item">
                  <i className="fas fa-brain fa-2x text-primary mb-3"></i>
                  <h5>4. Traitement IA</h5>
                  <p>L'IA génère automatiquement des résumés pour chaque article extrait, améliorant la qualité des données.</p>
                </div>
                
                <div className="feature-item">
                  <i className="fas fa-download fa-2x text-primary mb-3"></i>
                  <h5>5. Export flexible</h5>
                  <p>Téléchargez vos résultats au format JSON ou CSV avec toutes les métadonnées pour une utilisation ultérieure.</p>
                </div>

                <div className="feature-item">
                  <i className="fas fa-chart-line fa-2x text-primary mb-3"></i>
                  <h5>6. Analytics</h5>
                  <p>Analysez vos performances, consultez l'historique et optimisez vos stratégies d'extraction.</p>
                </div>
              </div>
            </div>

            <div className="guide-section mb-4">
              <h3>📊 Monitoring et Analytics</h3>
              <p>Surveillez vos performances et analysez vos données en temps réel :</p>
              
              <div className="monitoring-grid">
                <div className="monitoring-item">
                  <i className="fas fa-tachometer-alt text-success"></i>
                  <h5>Dashboard</h5>
                  <p>Vue d'ensemble de vos statistiques, performances et indicateurs clés en temps réel.</p>
                </div>
                
                <div className="monitoring-item">
                  <i className="fas fa-chart-bar text-info"></i>
                  <h5>Analytics</h5>
                  <p>Graphiques détaillés, tendances et analyses approfondies de vos données d'extraction.</p>
                </div>
                
                <div className="monitoring-item">
                  <i className="fas fa-history text-warning"></i>
                  <h5>Historique</h5>
                  <p>Suivi complet de tous vos scrapings précédents avec filtres et recherche avancée.</p>
                </div>
                
                <div className="monitoring-item">
                  <i className="fas fa-file-export text-primary"></i>
                  <h5>Exports</h5>
                  <p>Téléchargement de rapports personnalisés et exports programmés de vos données.</p>
                </div>
              </div>
            </div>

            <div className="guide-section">
              <h3>🔧 Fonctionnalités avancées</h3>
              <p>Découvrez les fonctionnalités avancées de FinData IA-M.K :</p>
              
              <div className="advanced-features">
                <div className="feature-highlight">
                  <h5><i className="fas fa-robot text-primary me-2"></i>Intelligence Artificielle</h5>
                  <ul>
                    <li>Génération automatique de résumés avec Groq/Llama3</li>
                    <li>Extraction intelligente de contenu pertinent</li>
                    <li>Détection automatique de la structure des pages</li>
                  </ul>
                </div>
                
                <div className="feature-highlight">
                  <h5><i className="fas fa-shield-alt text-success me-2"></i>Sécurité et Performance</h5>
                  <ul>
                    <li>Chiffrement HTTPS pour toutes les communications</li>
                    <li>Rate limiting intelligent pour respecter les sites</li>
                    <li>Gestion des sessions et authentification JWT</li>
                  </ul>
                </div>
                
                <div className="feature-highlight">
                  <h5><i className="fas fa-sync-alt text-info me-2"></i>Fallback automatique</h5>
                  <ul>
                    <li>Basculement automatique entre les méthodes d'extraction</li>
                    <li>Gestion intelligente des erreurs et retry</li>
                    <li>Optimisation continue des performances</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Référence API améliorée */}
        {activeTab === 'api' && (
          <div className="dashboard-card animate-slide-in-up">
            <div className="card-title">
              <i className="fas fa-code card-icon"></i>
              Référence API complète
            </div>
            
            <div className="api-intro mb-4">
              <p>L'API FinData IA-M.K est une API RESTful moderne qui permet d'intégrer les fonctionnalités de scraping dans vos applications avec support complet de l'IA.</p>
              
              <div className="api-info-grid">
                <div className="info-item">
                  <strong>Base URL :</strong> 
                  <code>http://localhost:8080/api</code>
                </div>
                <div className="info-item">
                  <strong>Authentification :</strong> 
                  <span className="badge bg-primary">JWT Bearer Token</span>
                </div>
                <div className="info-item">
                  <strong>Format :</strong> 
                  <span className="badge bg-success">JSON</span>
                </div>
                <div className="info-item">
                  <strong>Rate Limiting :</strong> 
                  <span className="badge bg-warning">10 req/min scraping</span>
                </div>
                <div className="info-item">
                  <strong>Version :</strong> 
                  <span className="badge bg-info">1.0.0</span>
                </div>
                <div className="info-item">
                  <strong>Support IA :</strong> 
                  <span className="badge bg-success">Groq/Llama3</span>
                </div>
              </div>
            </div>

            <div className="api-authentication mb-4">
              <h4><i className="fas fa-key me-2"></i>Authentification</h4>
              <p>Toutes les requêtes API nécessitent un token JWT obtenu via l'endpoint de connexion :</p>
              <pre className="bg-light p-3 rounded">
                <code>Authorization: Bearer &lt;your_jwt_token&gt;</code>
              </pre>
            </div>

            <div className="api-examples">
              <h4><i className="fas fa-code me-2"></i>Exemples d'utilisation</h4>
              {apiExamples.map(renderApiExample)}
            </div>

            <div className="api-error-codes mt-4">
              <h4><i className="fas fa-exclamation-triangle me-2"></i>Codes d'erreur</h4>
              <div className="error-codes-grid">
                <div className="error-item">
                  <code>400</code>
                  <span>Requête invalide</span>
                </div>
                <div className="error-item">
                  <code>401</code>
                  <span>Non authentifié</span>
                </div>
                <div className="error-item">
                  <code>403</code>
                  <span>Accès refusé</span>
                </div>
                <div className="error-item">
                  <code>429</code>
                  <span>Rate limit dépassé</span>
                </div>
                <div className="error-item">
                  <code>500</code>
                  <span>Erreur serveur</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* FAQ améliorée */}
        {activeTab === 'faq' && (
          <div className="dashboard-card animate-slide-in-up">
            <div className="card-title">
              <i className="fas fa-question-circle card-icon"></i>
              Questions fréquemment posées
            </div>
            
            <div className="faq-intro mb-4">
              <p>Trouvez rapidement des réponses aux questions les plus courantes sur l'utilisation de FinData IA-M.K.</p>
            </div>
            
            <div className="faq-list">
              {faqData.map((faq) => (
                <div key={faq.id} className="faq-item">
                  <button
                    className="faq-question"
                    onClick={() => setExpandedFaq(expandedFaq === faq.id ? null : faq.id)}
                  >
                    <span>{faq.question}</span>
                    <i className={`fas fa-chevron-${expandedFaq === faq.id ? 'up' : 'down'}`}></i>
                  </button>
                  {expandedFaq === faq.id && (
                    <div className="faq-answer">
                      <p>{faq.answer}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="support-section mt-4">
              <h4><i className="fas fa-headset me-2"></i>Besoin d'aide supplémentaire ?</h4>
              <p>Si vous ne trouvez pas la réponse à votre question, n'hésitez pas à nous contacter :</p>
              <div className="support-options">
                <div className="support-option">
                  <i className="fas fa-envelope"></i>
                  <span>Email : support@findata.com</span>
                </div>
                <div className="support-option">
                  <i className="fas fa-comments"></i>
                  <span>Chat en ligne : Disponible 24/7</span>
                </div>
                <div className="support-option">
                  <i className="fas fa-book"></i>
                  <span>Documentation technique : GitHub</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Documentation; 