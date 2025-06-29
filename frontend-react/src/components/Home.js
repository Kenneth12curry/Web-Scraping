import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentFeature, setCurrentFeature] = useState(0);

  const features = [
    {
      icon: 'fas fa-robot',
      title: 'Intelligence Artificielle Avancée',
      description: 'Résumés automatiques et analyse intelligente des données avec l\'IA Groq. Obtenez des insights pertinents en quelques secondes.',
      color: 'primary',
      highlight: 'Nouveau'
    },
    {
      icon: 'fas fa-spider',
      title: 'Scraping Intelligent & Sécurisé',
      description: 'Extraction de données avancée avec protection anti-bot, rotation d\'IP et fallback automatique pour une fiabilité maximale.',
      color: 'success',
      highlight: 'Populaire'
    },
    {
      icon: 'fas fa-chart-line',
      title: 'Analytics en Temps Réel',
      description: 'Tableaux de bord interactifs avec graphiques dynamiques et métriques détaillées pour suivre vos performances instantanément.',
      color: 'warning',
      highlight: 'Pro'
    },
    {
      icon: 'fas fa-shield-alt',
      title: 'Sécurité Entreprise',
      description: 'Authentification JWT, rate limiting, chiffrement des données et conformité GDPR pour protéger vos informations sensibles.',
      color: 'danger',
      highlight: 'Sécurisé'
    },
    {
      icon: 'fas fa-download',
      title: 'Export Flexible & Complet',
      description: 'Exportez vos données en JSON, CSV ou Excel avec des options de formatage avancées pour une intégration facile.',
      color: 'info',
      highlight: 'Flexible'
    },
    {
      icon: 'fas fa-mobile-alt',
      title: 'Interface Responsive & Moderne',
      description: 'Interface utilisateur intuitive adaptée à tous les appareils : desktop, tablette et mobile pour une expérience optimale.',
      color: 'secondary',
      highlight: 'Mobile'
    }
  ];

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
    
    // Animation automatique des fonctionnalités
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % features.length);
    }, 3000);
    
    return () => clearInterval(interval);
  }, [features.length]);

  const stats = [
    { number: '99.9%', label: 'Taux de succès', icon: 'fas fa-check-circle', color: 'success' },
    { number: '< 2s', label: 'Temps de réponse', icon: 'fas fa-bolt', color: 'warning' },
    { number: '24/7', label: 'Disponibilité', icon: 'fas fa-server', color: 'info' },
    { number: '1000+', label: 'Sites supportés', icon: 'fas fa-globe', color: 'primary' }
  ];

  const testimonials = [
    {
      name: 'Marie Dubois',
      role: 'Data Analyst Senior',
      company: 'TechCorp Solutions',
      content: 'FinData IA-M.K a complètement transformé notre workflow d\'analyse. L\'IA génère des résumés exceptionnellement précis et l\'interface est d\'une simplicité remarquable. Nous avons réduit notre temps d\'analyse de 70%.',
      avatar: 'MD',
      rating: 5,
      verified: true
    },
    {
      name: 'Jean Martin',
      role: 'Lead Developer',
      company: 'InnovSoft Technologies',
      content: 'L\'API est parfaitement documentée et l\'intégration a été un jeu d\'enfant. Les performances sont exceptionnelles et la fiabilité du scraping est impressionnante. Un outil indispensable pour nos projets.',
      avatar: 'JM',
      rating: 5,
      verified: true
    },
    {
      name: 'Sophie Bernard',
      role: 'Directrice de Projet',
      company: 'DataFlow Analytics',
      content: 'Excellent outil pour l\'analyse de données financières. Les graphiques sont très informatifs et les exports sont parfaits pour nos rapports. Le support client est également remarquable.',
      avatar: 'SB',
      rating: 5,
      verified: true
    }
  ];

  const benefits = [
    {
      icon: 'fas fa-rocket',
      title: 'Démarrage Immédiat',
      description: 'Commencer en moins de 2 minutes avec notre interface intuitive. Aucune configuration complexe requise.'
    },
    {
      icon: 'fas fa-gift',
      title: 'Plan Gratuit Généreux',
      description: '30 requêtes par mois gratuitement, sans carte de crédit. Parfait pour tester et démarrer vos projets.'
    },
    {
      icon: 'fas fa-headset',
      title: 'Support Technique Premium',
      description: 'Support technique 24/7 avec réponse garantie sous 2 heures. Notre équipe d\'experts est là pour vous aider.'
    },
    {
      icon: 'fas fa-shield-check',
      title: 'Sécurité de Niveau Entreprise',
      description: 'Chiffrement AES-256, conformité GDPR et protection des données. Vos informations sont en sécurité avec nous.'
    }
  ];

  return (
    <div className="home-container">
      {/* Navbar */}
      <nav className="home-navbar">
        <div className="container navbar-content">
          <div className="navbar-brand">
            <i className="fas fa-chart-line me-2"></i>
            <span className="fw-bold">FinData IA-M.K</span>
          </div>
          <div className="navbar-actions">
            {isAuthenticated ? (
              <Link to="/dashboard" className="btn btn-primary btn-sm me-2">
                <i className="fas fa-tachometer-alt me-2"></i>
                Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" className="btn btn-outline-primary btn-sm me-2">
                  <i className="fas fa-sign-in-alt me-2"></i>
                  Se connecter
                </Link>
                <Link to="/register" className="btn btn-primary btn-sm">
                  <i className="fas fa-user-plus me-2"></i>
                  S'inscrire
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>
      {/* Hero Section */}
      <section className={`hero-section ${isAuthenticated ? 'with-navbar' : ''}`}>
        <div className="hero-background">
          <div className="hero-shapes">
            <div className="shape shape-1"></div>
            <div className="shape shape-2"></div>
            <div className="shape shape-3"></div>
          </div>
        </div>
        
        <div className="container">
          <div className={`row align-items-center ${isAuthenticated ? 'pt-5' : 'min-vh-100'}`}>
            <div className="col-lg-6">
              <div className="hero-content animate-fade-in-left">
                <div className="hero-badge">
                  <i className="fas fa-bolt me-2"></i>
                  <span>Solution Française d'IA Financière de Confiance</span>
                </div>
                <h1 className="hero-title">
                  <span className="gradient-text">FinData IA-M.K</span>
                  <br />
                  <span className="hero-slogan">Votre partenaire d'excellence pour l'analyse et la valorisation des données financières</span>
                </h1>
                <p className="hero-subtitle">
                  Plateforme professionnelle tout-en-un : extraction intelligente, analyse avancée, visualisation claire et conformité totale. 
                  Bénéficiez de la puissance de l'IA, d'une sécurité de niveau entreprise et d'un accompagnement humain pour accélérer vos décisions et booster votre performance.
                </p>
                <div className="hero-actions">
                  {isAuthenticated ? (
                    <Link to="/dashboard" className="btn btn-primary btn-lg me-3">
                      <i className="fas fa-tachometer-alt me-2"></i>
                      Accéder au Dashboard
                    </Link>
                  ) : (
                    <>
                      <Link to="/register" className="btn btn-primary btn-lg me-3">
                        <i className="fas fa-user-plus me-2"></i>
                        Commencer gratuitement
                      </Link>
                      <Link to="/login" className="btn btn-outline-primary btn-lg me-3">
                        <i className="fas fa-sign-in-alt me-2"></i>
                        Se connecter
                      </Link>
                      <a href="#demo" className="btn btn-outline-secondary btn-lg">
                        <i className="fas fa-play me-2"></i>
                        Voir la démo
                      </a>
                    </>
                  )}
                </div>
                <div className="hero-stats mt-4">
                  <div className="row">
                    {stats.map((stat, index) => (
                      <div key={index} className="col-6 col-md-3">
                        <div className="stat-item">
                          <i className={`${stat.icon} text-${stat.color}`}></i>
                          <div className="stat-number">{stat.number}</div>
                          <div className="stat-label">{stat.label}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            <div className="col-lg-6">
              <div className="hero-image animate-fade-in-right">
                <div className="dashboard-preview">
                  <div className="preview-header">
                    <div className="preview-dots">
                      <span className="dot red"></span>
                      <span className="dot yellow"></span>
                      <span className="dot green"></span>
                    </div>
                    <div className="preview-title">Dashboard FinData IA-M.K</div>
                  </div>
                  <div className="preview-content">
                    <div className="preview-chart">
                      <i className="fas fa-chart-line fa-3x text-primary"></i>
                      <div className="chart-label">Analytics en Temps Réel</div>
                    </div>
                    <div className="preview-stats">
                      <div className="preview-stat">
                        <div className="stat-bar" style={{ width: '95%' }}></div>
                        <span>Précision IA</span>
                      </div>
                      <div className="preview-stat">
                        <div className="stat-bar" style={{ width: '90%' }}></div>
                        <span>Vitesse Scraping</span>
                      </div>
                      <div className="preview-stat">
                        <div className="stat-bar" style={{ width: '85%' }}></div>
                        <span>Fiabilité</span>
                      </div>
                    </div>
                    <div className="preview-ai-badge">
                      <i className="fas fa-robot me-2"></i>
                      IA Groq Intégrée
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="benefits-section py-5">
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="section-title">Pourquoi Choisir FinData IA-M.K ?</h2>
            <p className="section-subtitle">
              Découvrez les avantages exclusifs qui font de notre plateforme la solution de référence 
              pour l'analyse de données financières
            </p>
          </div>
          
          <div className="row">
            {benefits.map((benefit, index) => (
              <div key={index} className="col-lg-3 col-md-6 mb-4">
                <div className="benefit-card animate-slide-in-up" style={{ animationDelay: `${index * 0.1}s` }}>
                  <div className="benefit-icon">
                    <i className={benefit.icon}></i>
                  </div>
                  <h3 className="benefit-title">{benefit.title}</h3>
                  <p className="benefit-description">{benefit.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section py-5">
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="section-title">Fonctionnalités Professionnelles</h2>
            <p className="section-subtitle">
              Découvrez notre suite complète d'outils conçus pour optimiser votre analyse de données 
              et vous faire gagner du temps dans vos projets
            </p>
          </div>
          
          <div className="row">
            {features.map((feature, index) => (
              <div key={index} className="col-lg-4 col-md-6 mb-4">
                <div className={`feature-card animate-slide-in-up ${currentFeature === index ? 'active' : ''}`} 
                     style={{ animationDelay: `${index * 0.1}s` }}>
                  {feature.highlight && (
                    <div className="feature-badge">{feature.highlight}</div>
                  )}
                  <div className={`feature-icon bg-${feature.color}`}>
                    <i className={feature.icon}></i>
                  </div>
                  <h3 className="feature-title">{feature.title}</h3>
                  <p className="feature-description">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section id="demo" className="demo-section py-5 bg-dark text-white">
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-6">
              <div className="demo-content">
                <div className="demo-badge">
                  <i className="fas fa-rocket me-2"></i>
                  Démo Interactive
                </div>
                <h2 className="section-title text-white">Découvrez FinData IA-M.K en Action</h2>
                <p className="section-subtitle text-light">
                  Explorez notre plateforme et voyez comment l'IA transforme votre analyse de données 
                  en insights actionnables en quelques clics
                </p>
                
                <div className="demo-features">
                  <div className="demo-feature">
                    <div className="feature-icon-small">
                      <i className="fas fa-shield-alt text-success"></i>
                    </div>
                    <div className="feature-content">
                      <h5>Scraping Intelligent</h5>
                      <p>Protection anti-bot avancée et extraction de données fiables</p>
                    </div>
                  </div>
                  
                  <div className="demo-feature">
                    <div className="feature-icon-small">
                      <i className="fas fa-brain text-info"></i>
                    </div>
                    <div className="feature-content">
                      <h5>IA Groq Intégrée</h5>
                      <p>Résumés automatiques et analyse contextuelle des données</p>
                    </div>
                  </div>
                  
                  <div className="demo-feature">
                    <div className="feature-icon-small">
                      <i className="fas fa-chart-line text-warning"></i>
                    </div>
                    <div className="feature-content">
                      <h5>Analytics Temps Réel</h5>
                      <p>Visualisations interactives et métriques en direct</p>
                    </div>
                  </div>
                  
                  <div className="demo-feature">
                    <div className="feature-icon-small">
                      <i className="fas fa-download text-primary"></i>
                    </div>
                    <div className="feature-content">
                      <h5>Export Flexible</h5>
                      <p>Formats multiples : JSON, CSV, Excel avec personnalisation</p>
                    </div>
                  </div>
                </div>
                
                <div className="demo-actions mt-4">
                  <Link to="/register" className="btn btn-primary btn-lg me-3">
                    <i className="fas fa-play me-2"></i>
                    Essayer gratuitement
                  </Link>
                  <Link to="/documentation" className="btn btn-outline-light btn-lg">
                    <i className="fas fa-book me-2"></i>
                    Voir la documentation
                  </Link>
                </div>
              </div>
            </div>
            <div className="col-lg-6">
              <div className="demo-preview">
                <div className="demo-screen">
                  <div className="demo-header">
                    <div className="demo-dots">
                      <span className="dot red"></span>
                      <span className="dot yellow"></span>
                      <span className="dot green"></span>
                    </div>
                    <div className="demo-title">FinData IA-M.K - Dashboard</div>
                  </div>
                  <div className="demo-tabs">
                    <span className="demo-tab active">
                      <i className="fas fa-spider me-1"></i>
                      Scraping
                    </span>
                    <span className="demo-tab">
                      <i className="fas fa-chart-bar me-1"></i>
                      Analytics
                    </span>
                    <span className="demo-tab">
                      <i className="fas fa-file-export me-1"></i>
                      Export
                    </span>
                  </div>
                  <div className="demo-content-area">
                    <div className="demo-chart-container">
                      <div className="demo-chart">
                        <i className="fas fa-chart-area fa-3x text-primary"></i>
                      </div>
                      <div className="demo-stats">
                        <div className="demo-stat">
                          <div className="stat-number">2,847</div>
                          <div className="stat-label">Données extraites</div>
                        </div>
                        <div className="demo-stat">
                          <div className="stat-number">98.5%</div>
                          <div className="stat-label">Précision IA</div>
                        </div>
                        <div className="demo-stat">
                          <div className="stat-number">3.2s</div>
                          <div className="stat-label">Temps moyen</div>
                        </div>
                      </div>
                    </div>
                    <div className="demo-info">
                      <h4>Résultats en Temps Réel</h4>
                      <p>Visualisez vos données extraites avec des graphiques interactifs et des métriques détaillées. Notre IA analyse automatiquement les tendances et génère des insights pertinents.</p>
                      <div className="demo-ai-badge">
                        <i className="fas fa-robot me-2"></i>
                        Analyse IA en cours...
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials-section py-5">
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="section-title">Témoignages de Nos Clients</h2>
            <p className="section-subtitle">
              Découvrez pourquoi des professionnels de renom font confiance à FinData IA-M.K 
              pour leurs analyses de données critiques
            </p>
          </div>
          
          <div className="row">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="col-lg-4 mb-4">
                <div className="testimonial-card animate-slide-in-up" style={{ animationDelay: `${index * 0.2}s` }}>
                  <div className="testimonial-rating">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <i key={i} className="fas fa-star text-warning"></i>
                    ))}
                    {testimonial.verified && (
                      <span className="verified-badge">
                        <i className="fas fa-check-circle text-success"></i>
                        Client vérifié
                      </span>
                    )}
                  </div>
                  <div className="testimonial-content">
                    <div className="quote-icon">
                      <i className="fas fa-quote-left"></i>
                    </div>
                    <p className="testimonial-text">{testimonial.content}</p>
                  </div>
                  <div className="testimonial-author">
                    <div className="author-avatar">
                      {testimonial.avatar}
                    </div>
                    <div className="author-info">
                      <h4 className="author-name">{testimonial.name}</h4>
                      <p className="author-role">{testimonial.role}</p>
                      <p className="author-company">{testimonial.company}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing-section py-5">
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="section-title">Plans Tarifaires Transparents</h2>
            <p className="section-subtitle">
              Des options flexibles adaptées à tous les besoins, de l'essai gratuit 
              aux solutions professionnelles
            </p>
          </div>
          
          <div className="row justify-content-center">
            <div className="col-lg-4 col-md-6 mb-4">
              <div className="pricing-card">
                <div className="pricing-header">
                  <h3 className="pricing-title">Essai Gratuit</h3>
                  <div className="pricing-price">
                    <span className="price">0€</span>
                    <span className="period">/mois</span>
                  </div>
                  <p className="pricing-subtitle">Parfait pour découvrir la plateforme</p>
                </div>
                <div className="pricing-features">
                  <div className="feature-item">
                    <i className="fas fa-check text-success me-2"></i>
                    <span>30 requêtes/mois</span>
                  </div>
                  <div className="feature-item">
                    <i className="fas fa-check text-success me-2"></i>
                    <span>Résumés IA basiques</span>
                  </div>
                  <div className="feature-item">
                    <i className="fas fa-check text-success me-2"></i>
                    <span>Export JSON</span>
                  </div>
                  <div className="feature-item">
                    <i className="fas fa-check text-success me-2"></i>
                    <span>Interface intuitive</span>
                  </div>
                  <div className="feature-item">
                    <i className="fas fa-check text-success me-2"></i>
                    <span>Support communautaire</span>
                  </div>
                </div>
                <div className="pricing-action">
                  <Link to="/register" className="btn btn-outline-primary btn-lg w-100">
                    <i className="fas fa-rocket me-2"></i>
                    Commencer l'essai gratuit
                  </Link>
                </div>
              </div>
            </div>
            
            <div className="col-lg-4 col-md-6 mb-4">
              <div className="pricing-card featured">
                <div className="pricing-badge">Recommandé</div>
                <div className="pricing-header">
                  <h3 className="pricing-title">Plan Pro</h3>
                  <div className="pricing-price">
                    <span className="price">29€</span>
                    <span className="period">/mois</span>
                  </div>
                  <p className="pricing-subtitle">Pour les professionnels et équipes</p>
                </div>
                <div className="pricing-features">
                  <div className="feature-item">
                    <i className="fas fa-check text-success me-2"></i>
                    <span>10 000 requêtes/mois</span>
                  </div>
                  <div className="feature-item">
                    <i className="fas fa-check text-success me-2"></i>
                    <span>Résumés IA avancés</span>
                  </div>
                  <div className="feature-item">
                    <i className="fas fa-check text-success me-2"></i>
                    <span>Export JSON, CSV & Excel</span>
                  </div>
                  <div className="feature-item">
                    <i className="fas fa-check text-success me-2"></i>
                    <span>Analytics avancées</span>
                  </div>
                  <div className="feature-item">
                    <i className="fas fa-check text-success me-2"></i>
                    <span>Support prioritaire 24/7</span>
                  </div>
                  <div className="feature-item">
                    <i className="fas fa-check text-success me-2"></i>
                    <span>API complète</span>
                  </div>
                </div>
                <div className="pricing-action">
                  <Link to="/register" className="btn btn-primary btn-lg w-100">
                    <i className="fas fa-crown me-2"></i>
                    Choisir le Plan Pro
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section py-5">
        <div className="container">
          <div className="cta-content text-center">
            <h2 className="cta-title">Prêt à Transformer Votre Analyse de Données ?</h2>
            <p className="cta-subtitle">
              Rejoignez des centaines de professionnels qui font confiance à FinData IA-M.K 
              pour leurs analyses critiques. Démarrez votre essai gratuit dès aujourd'hui !
            </p>
            <div className="cta-actions">
              {isAuthenticated ? (
                <Link to="/dashboard" className="btn btn-primary btn-lg">
                  <i className="fas fa-rocket me-2"></i>
                  Accéder à mon Dashboard
                </Link>
              ) : (
                <>
                  <Link to="/register" className="btn btn-primary btn-lg me-3">
                    <i className="fas fa-user-plus me-2"></i>
                    Commencer l'essai gratuit
                  </Link>
                  <Link to="/login" className="btn btn-outline-primary btn-lg me-3">
                    <i className="fas fa-sign-in-alt me-2"></i>
                    Se connecter
                  </Link>
                  <Link to="/documentation" className="btn btn-outline-secondary btn-lg">
                    <i className="fas fa-book me-2"></i>
                    Voir la documentation
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer py-4">
        <div className="container">
          <div className="row">
            <div className="col-md-6">
              <div className="footer-brand">
                <i className="fas fa-chart-line me-2"></i>
                <span className="fw-bold">FinData IA-M.K</span>
              </div>
              <p className="mt-2">
                Solution française d'Intelligence Artificielle pour l'analyse et la valorisation des données financières
              </p>
            </div>
            <div className="col-md-6 text-md-end">
              <div className="footer-links">
                <Link to="/documentation" className="me-3">Documentation</Link>
                <Link to="/login" className="me-3">Connexion</Link>
                <Link to="/register">Inscription</Link>
              </div>
              <p className="mt-2">
                © 2024 FinData IA-M.K. Tous droits réservés.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home; 