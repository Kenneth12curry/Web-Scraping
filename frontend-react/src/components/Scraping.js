import React, { useState, useEffect } from 'react';
import { scrapingService, validateUrl, formatError } from '../services/api';
import Navigation from './Navigation'; // Import Navigation

const Scraping = () => {
  const [url, setUrl] = useState('');
  const [method, setMethod] = useState('scrapedo');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [success, setSuccess] = useState('');
  const [progress, setProgress] = useState(0);
  const [scrapingHistory, setScrapingHistory] = useState([]);
  const [maxArticles, setMaxArticles] = useState(20);
  const [maxIaSummaries, setMaxIaSummaries] = useState(10);
  const [currentStep, setCurrentStep] = useState('');
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    const history = localStorage.getItem('scrapingHistory');
    if (history) {
      setScrapingHistory(JSON.parse(history));
    }
    
    const savedResults = localStorage.getItem('scrapingResults');
    if (savedResults) {
      try {
        const parsedResults = JSON.parse(savedResults);
        setResults(parsedResults);
        setShowResults(true);
      } catch (e) {
        console.error('Erreur lors du chargement des résultats:', e);
        localStorage.removeItem('scrapingResults');
      }
    }
  }, []);

  useEffect(() => {
    if (results && showResults) {
      localStorage.setItem('scrapingResults', JSON.stringify(results));
    } else {
      localStorage.removeItem('scrapingResults');
    }
  }, [results, showResults]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateUrl(url)) {
      setError('URL invalide. Veuillez entrer une URL valide.');
      return;
    }
    setLoading(true);
    setError('');
    setSuccess('');
    setResults(null);
    setProgress(0);
    setCurrentStep('Initialisation...');
    setShowResults(false);
    
    const steps = [
      'Connexion au site...',
      'Analyse de la structure...',
      'Extraction des articles...',
      'Génération des résumés IA (peut prendre 1-2 minutes)...',
      'Finalisation...'
    ];
    let stepIndex = 0;
    
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        const newProgress = prev + 15;
        if (newProgress > stepIndex * 20 && stepIndex < steps.length - 1) {
          stepIndex++;
          setCurrentStep(steps[stepIndex]);
        }
        return newProgress;
      });
    }, 800);

    try {
      const response = await scrapingService.extractArticles(url, method, maxArticles, maxIaSummaries);
      clearInterval(progressInterval);
      setProgress(100);
      setCurrentStep('Terminé !');
      
      if (response.data.success) {
        setResults(response.data);
        setSuccess('Scraping terminé avec succès !');
        setShowResults(true);
        
        const newHistoryItem = {
          id: Date.now(),
          url: url,
          method: method,
          timestamp: new Date().toISOString(),
          articlesCount: response.data.total_articles || 0,
          domain: response.data.domain || new URL(url).hostname,
          processingTime: response.data.processing_time || 'N/A',
          articlesWithSummaries: response.data.articles_with_summaries || 0
        };
        
        const updatedHistory = [newHistoryItem, ...scrapingHistory.slice(0, 9)];
        setScrapingHistory(updatedHistory);
        localStorage.setItem('scrapingHistory', JSON.stringify(updatedHistory));
      } else {
        setError(response.data.message || 'Erreur lors du scraping');
      }
    } catch (error) {
      clearInterval(progressInterval);
      setProgress(0);
      setCurrentStep('');
      setError(formatError(error));
    } finally {
      setLoading(false);
      setTimeout(() => {
        setProgress(0);
        setCurrentStep('');
      }, 2000);
    }
  };

  const exportResults = (format) => {
    if (!results) return;
    let content = '';    let filename = `scraping_results_${new Date().toISOString().split('T')[0]}`;
    
    if (format === 'json') {
      content = JSON.stringify(results, null, 2);
      filename += '.json';
    } else if (format === 'csv') {
      let csvContent = 'Title,URL,Content,Resume,Date\n';
      results.articles.forEach(article => {
        const title = article.title ? `"${article.title.replace(/"/g, '""')}"` : '';
        const url = article.url ? `"${article.url}"` : '';
        const content = article.content ? `"${article.content.replace(/"/g, '""')}"` : '';
        const resume = article.resume ? `"${article.resume.replace(/"/g, '""')}"` : '';
        const date = article.date ? `"${article.date}"` : '';
        csvContent += `${title},${url},${content},${resume},${date}\n`;
      });
      content = csvContent;
      filename += '.csv';
    }
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const retryFromHistory = (historyItem) => {
    setShowResults(false);
    setResults(null);
    setUrl(historyItem.url);
    setMethod(historyItem.method);
    setMaxArticles(historyItem.articlesCount > 30 ? 50 : historyItem.articlesCount > 20 ? 30 : 20);
  };

  const clearHistory = () => {
    setScrapingHistory([]);
    localStorage.removeItem('scrapingHistory');
  };

  const clearResults = () => {
    setResults(null);
    setShowResults(false);
    setSuccess('');
  };

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

  const renderDashboard = () => (
    <>
      <Navigation />
      <div className="scraping-hero-layout">
        <div className="scraping-hero-header">
          <div className="hero-title-row">
            <h1 className="hero-title">
              <i className="fas fa-spider"></i>
              <span>Extraction de Données IA</span>
            </h1>
            <div className="hero-badges">
              <span className="hero-badge"><i className="fas fa-rocket"></i> Multi-méthodes</span>
              <span className="hero-badge"><i className="fas fa-brain"></i> IA Groq/Llama3</span>
              <span className="hero-badge"><i className="fas fa-clock"></i> 2-5 secondes</span>
            </div>
          </div>
          <div className="hero-subtitle">
            Extrayez des articles et des données depuis n'importe quel site web avec l'intelligence artificielle.
          </div>
        </div>
        <main className="scraping-main-2col">
          <div className="scraping-main-left">
            <div className="scraping-card scraping-config-card">
              <h2 className="scraping-card-title"><i className="fas fa-cog"></i> Configuration</h2>
              <form onSubmit={handleSubmit} className="scraping-form">
                <div className="form-group">
                  <label htmlFor="url" className="form-label">URL du site</label>
                  <input
                    type="url"
                    id="url"
                    className="form-input"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="https://example.com"
                    required
                    disabled={loading}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="method" className="form-label">Méthode d'extraction</label>
                  <select
                    id="method"
                    className="form-select"
                    value={method}
                    onChange={(e) => setMethod(e.target.value)}
                    disabled={loading}
                  >
                    <option value="scrapedo">Scrape.do (Recommandé)</option>
                    <option value="requests">Requests standard</option>
                  </select>
                </div>
                <div className="form-group form-advanced-toggle">
                  <input
                    type="checkbox"
                    id="showAdvanced"
                    className="form-checkbox"
                    checked={showAdvanced}
                    onChange={(e) => setShowAdvanced(e.target.checked)}
                    disabled={loading}
                  />
                  <label htmlFor="showAdvanced" className="checkbox-label">Options avancées</label>
                </div>
                {showAdvanced && (
                  <div className="advanced-section">
                    <div className="form-group">
                      <label className="form-label">Nombre d'articles</label>
                      <select 
                        className="form-select" 
                        value={maxArticles} 
                        onChange={e => setMaxArticles(Number(e.target.value))} 
                        disabled={loading}
                      >
                        <option value={10}>10 articles</option>
                        <option value={20}>20 articles</option>
                        <option value={30}>30 articles</option>
                        <option value={50}>50 articles</option>
                        <option value={100}>100 articles</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label className="form-label">Limite IA (résumés IA)</label>
                      <select
                        className="form-select"
                        value={maxIaSummaries}
                        onChange={e => setMaxIaSummaries(Number(e.target.value))}
                        disabled={loading}
                      >
                        <option value={1}>1 article</option>
                        <option value={3}>3 articles</option>
                        <option value={5}>5 articles</option>
                        <option value={10}>10 articles</option>
                        <option value={20}>20 articles</option>
                        <option value={30}>30 articles</option>
                        <option value={50}>50 articles</option>
                        <option value={100}>100 articles</option>
                      </select>
                    </div>
                  </div>
                )}
                {loading && (
                  <div className="progress-section">
                    <div className="progress-info">
                      <span className="progress-step">{currentStep}</span>
                      <span className="progress-percentage">{progress}%</span>
                    </div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
                <button
                  type="submit"
                  className="scraping-main-btn"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <i className="fas fa-spinner fa-spin"></i>
                      <span>Extraction en cours...</span>
                    </>
                  ) : (
                    <>
                      <i className="fas fa-play"></i>
                      <span>Démarrer l'extraction</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
          <div className="scraping-main-right">
            <div className="scraping-card scraping-info-card">
              <div className="scraping-card-title"><i className="fas fa-info-circle"></i> Informations système</div>
              <div className="info-list">
                <div className="info-item"><i className="fas fa-check-circle status-icon success"></i> Scrape.do configuré</div>
                <div className="info-item"><i className="fas fa-brain status-icon primary"></i> IA Groq/Llama3 active</div>
                <div className="info-item"><i className="fas fa-clock status-icon warning"></i> Délai moyen : 2-5s</div>
                <div className="info-item"><i className="fas fa-shield-alt status-icon info"></i> Protection anti-bot</div>
                <div className="info-item"><i className="fas fa-database status-icon success"></i> Stockage sécurisé</div>
                <div className="info-item"><i className="fas fa-sync-alt status-icon primary"></i> Fallback automatique</div>
              </div>
            </div>
            <div className="scraping-card scraping-history-card">
              <div className="scraping-card-title"><i className="fas fa-history"></i> Historique récent</div>
              <div className="history-list">
                {scrapingHistory.slice(0, 5).map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="history-content">
                      <div className="history-domain">{item.domain}</div>
                      <div className="history-details">
                        <span className="history-date"><i className="fas fa-calendar"></i> {formatDate(item.timestamp)}</span>
                        <span className="history-count"><i className="fas fa-file-alt"></i> {item.articlesCount} articles</span>
                        {item.processingTime && <span className="history-time"><i className="fas fa-clock"></i> {item.processingTime}</span>}
                      </div>
                    </div>
                    <button className="retry-btn" onClick={() => retryFromHistory(item)} disabled={loading} title="Réutiliser cette configuration"><i className="fas fa-redo"></i></button>
                  </div>
                ))}
              </div>
              {scrapingHistory.length > 0 && <button className="clear-btn" onClick={clearHistory} title="Effacer l'historique"><i className="fas fa-trash"></i> Effacer l'historique</button>}
            </div>
          </div>
        </main>
      </div>
    </>
  );

  const renderResults = () => (
    <div className="scraping-results-layout">
      <div className="scraping-hero-header">
        <div className="hero-title-row">
          <h1 className="hero-title">
            <i className="fas fa-check-circle"></i>
            <span>Résultats de l'Extraction</span>
          </h1>
        </div>
        <div className="hero-subtitle">
          Voici les données extraites pour : <strong>{results.domain}</strong>
        </div>
      </div>
      <main className="scraping-results-container">
        <div className="scraping-card scraping-results-card">
          <div className="results-summary">
            <div className="summary-item"><span>Articles extraits</span><b>{results.total_articles}</b></div>
            <div className="summary-item"><span>Méthode</span><b>{results.method_used}</b></div>
            <div className="summary-item"><span>Temps</span><b>{results.processing_time}</b></div>
            <div className="summary-item"><span>Résumés IA</span><b>{results.articles_with_summaries}</b></div>
          </div>
          <div className="results-actions">
            <button className="action-btn" onClick={() => exportResults('json')}><i className="fas fa-download"></i> JSON</button>
            <button className="action-btn" onClick={() => exportResults('csv')}><i className="fas fa-download"></i> CSV</button>
            <button className="action-btn action-btn-clear" onClick={clearResults}><i className="fas fa-arrow-left"></i> Nouvelle Extraction</button>
          </div>
          <div className="articles-list">
            {results.articles.map((article, index) => (
              <div key={index} className="article-item" id={`article-${index}`}>
                <div className="article-header">
                  <h3 className="article-title">
                    <a href={article.url} target="_blank" rel="noopener noreferrer">{article.title}</a>
                  </h3>
                  {article.date && <span className="article-date"><i className="fas fa-calendar"></i> {article.date}</span>}
                </div>
                <div className="article-content">
                  <div className="content-preview">
                    {article.content.length > 500 ? (
                      <>
                        <div className="content-text">
                          {article.content.substring(0, 500)}...
                        </div>
                        <button 
                          className="show-more-btn"
                          onClick={(e) => {
                            const contentDiv = e.target.previousElementSibling;
                            const btn = e.target;
                            if (contentDiv.innerHTML.includes('...')) {
                              contentDiv.innerHTML = article.content;
                              btn.innerHTML = '<i class="fas fa-chevron-up"></i> Voir moins';
                            } else {
                              contentDiv.innerHTML = article.content.substring(0, 500) + '...';
                              btn.innerHTML = '<i class="fas fa-chevron-down"></i> Voir plus';
                            }
                          }}
                        >
                          <i className="fas fa-chevron-down"></i> Voir plus
                        </button>
                      </>
                    ) : (
                      <div className="content-text">{article.content}</div>
                    )}
                  </div>
                  <div className="content-stats">
                    <span className="content-length">
                      <i className="fas fa-text-width"></i> {article.content.length} caractères
                    </span>
                    <span className="content-words">
                      <i className="fas fa-words"></i> {article.content.split(' ').length} mots
                    </span>
                  </div>
                </div>
                {article.resume && (
                  <div className="article-resume">
                    <div className="resume-header">
                      <i className="fas fa-brain"></i> Résumé IA
                    </div>
                    <p>{article.resume}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );

  return (
    <>
      {showResults && results ? renderResults() : renderDashboard()}
    </>
  );
};

export default Scraping;