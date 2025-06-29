import axios from 'axios';
import config from '../config';

// Configuration d'axios
const api = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: config.REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
});

console.log('🔧 Configuration API - Timeout:', config.REQUEST_TIMEOUT, 'ms');

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les réponses et erreurs
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Gestion des erreurs d'authentification
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Supprimer le token expiré
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Rediriger vers la page de connexion
      window.location.href = '/';
      return Promise.reject(error);
    }

    // Gestion des erreurs de réseau
    if (!error.response) {
      console.error('Erreur de réseau:', error.message);
      return Promise.reject({
        message: config.ERROR_MESSAGES.NETWORK_ERROR,
        originalError: error
      });
    }

    // Gestion des autres erreurs HTTP
    const errorMessage = error.response?.data?.message || getErrorMessage(error.response.status);
    return Promise.reject({
      message: errorMessage,
      status: error.response.status,
      originalError: error
    });
  }
);

// Fonction pour obtenir le message d'erreur selon le code de statut
function getErrorMessage(status) {
  switch (status) {
    case 400:
      return 'Requête invalide';
    case 401:
      return config.ERROR_MESSAGES.UNAUTHORIZED;
    case 403:
      return config.ERROR_MESSAGES.FORBIDDEN;
    case 404:
      return config.ERROR_MESSAGES.NOT_FOUND;
    case 500:
      return config.ERROR_MESSAGES.SERVER_ERROR;
    default:
      return config.ERROR_MESSAGES.UNKNOWN_ERROR;
  }
}

// Fonction pour retry automatique
async function retryRequest(requestFn, maxRetries = config.MAX_RETRIES) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn();
    } catch (error) {
      if (i === maxRetries - 1) {
        throw error;
      }
      
      // Attendre avant de retry
      await new Promise(resolve => setTimeout(resolve, config.RETRY_DELAY * (i + 1)));
    }
  }
}

// Service d'authentification
export const authService = {
  async register(userData) {
    return retryRequest(() => 
      api.post('/auth/register', {
        username: userData.username,
        password: userData.password,
        email: userData.email
      })
    );
  },

  async login(username, password) {
    return retryRequest(() => 
      api.post('/auth/login', { username, password })
    );
  },

  async logout() {
    return retryRequest(() => 
      api.post('/auth/logout')
    );
  }
};

// Service du dashboard
export const dashboardService = {
  async getStats() {
    return retryRequest(() => 
      api.get('/dashboard/stats')
    );
  },

  async getAnalytics() {
    return retryRequest(() => 
      api.get('/dashboard/analytics')
    );
  }
};

// Service de scraping
export const scrapingService = {
  async extractArticles(url, method = 'scrapedo', maxArticles = 20, maxIaSummaries = 10) {
    console.log('🚀 Service API - Début extraction:', { url, method, maxArticles, maxIaSummaries });
    console.log('⏱️ Service API - Timeout configuré:', config.REQUEST_TIMEOUT, 'ms');
    
    return retryRequest(() => {
      console.log('📡 Service API - Envoi requête au backend avec timeout 3min...');
      return api.post('/scraping/extract', { 
        url, 
        method, 
        max_articles: maxArticles,
        max_ia_summaries: maxIaSummaries
      }, {
        timeout: 180000 // 3 minutes spécifiquement pour le scraping
      });
    });
  }
};

// Service de santé
export const healthService = {
  async checkHealth() {
    return retryRequest(() => 
      api.get('/health')
    );
  }
};

// Fonction utilitaire pour valider les URLs
export const validateUrl = (url) => {
  if (!url) return false;
  
  // Ajouter le protocole si manquant
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'https://' + url;
  }
  
  return config.VALIDATION.URL_PATTERN.test(url);
};

// Fonction utilitaire pour formater les erreurs
export const formatError = (error) => {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error.message) {
    return error.message;
  }
  
  if (error.originalError?.message) {
    return error.originalError.message;
  }
  
  return config.ERROR_MESSAGES.UNKNOWN_ERROR;
};

export default api; 