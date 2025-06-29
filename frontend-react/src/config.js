// Configuration de l'application
const config = {
  // API Configuration
  API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8080/api',
  
  // Timeouts
  REQUEST_TIMEOUT: 30000, // 30 secondes
  
  // Retry configuration
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000, // 1 seconde
  
  // Pagination
  DEFAULT_PAGE_SIZE: 10,
  
  // Local storage keys
  STORAGE_KEYS: {
    TOKEN: 'token',
    USER: 'user',
    THEME: 'theme'
  },
  
  // Routes
  ROUTES: {
    DASHBOARD: '/dashboard',
    DOCUMENTATION: '/documentation',
    ACCOUNT: '/account',
    LOGIN: '/login'
  },
  
  // Error messages
  ERROR_MESSAGES: {
    NETWORK_ERROR: 'Erreur de connexion au serveur',
    UNAUTHORIZED: 'Session expirée, veuillez vous reconnecter',
    FORBIDDEN: 'Accès refusé',
    NOT_FOUND: 'Ressource non trouvée',
    SERVER_ERROR: 'Erreur interne du serveur',
    UNKNOWN_ERROR: 'Une erreur inattendue s\'est produite'
  },
  
  // Success messages
  SUCCESS_MESSAGES: {
    LOGIN: 'Connexion réussie',
    LOGOUT: 'Déconnexion réussie',
    SCRAPING_STARTED: 'Scraping démarré avec succès',
    DATA_LOADED: 'Données chargées avec succès'
  },
  
  // Validation
  VALIDATION: {
    URL_PATTERN: /^https?:\/\/.+/,
    MIN_PASSWORD_LENGTH: 6,
    MAX_URL_LENGTH: 2048
  }
};

export default config; 