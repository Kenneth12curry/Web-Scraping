import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService, formatError } from '../services/api';
import config from '../config';

const Login = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [success, setSuccess] = useState('');
  const [showSuccessAnimation, setShowSuccessAnimation] = useState(false);
  const [formValid, setFormValid] = useState(false);
  const navigate = useNavigate();

  // Vérifier la validité du formulaire
  useEffect(() => {
    setFormValid(credentials.username.trim() !== '' && credentials.password.trim() !== '');
  }, [credentials]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await authService.login(credentials.username, credentials.password);
      
      if (response.data.success) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
        
        // Déclencher un événement personnalisé pour notifier l'App.js
        window.dispatchEvent(new CustomEvent('authChange'));
        
        setSuccess(config.SUCCESS_MESSAGES.LOGIN);
        setShowSuccessAnimation(true);
        
        // Redirection après 2 secondes
        setTimeout(() => {
          navigate('/dashboard');
        }, 2000);
      }
    } catch (error) {
      setError(formatError(error));
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setCredentials(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="auth-container">
      <div className="auth-split-left">
        <div className="brand-logo">
          <i className="fas fa-chart-line"></i>
        </div>
        <h1 className="brand-title">FinData IA-M.K</h1>
        <p className="brand-subtitle">Accédez à des analyses de données financières de pointe grâce à l'IA.</p>
      </div>
      <div className="auth-split-right">
        <div className="form-container">
          {/* Animation de succès */}
          {showSuccessAnimation && (
            <div className="modal-overlay">
              <div className="modal-content">
                <div className="success-message">
                  <div className="success-icon">
                    <i className="fas fa-check-circle"></i>
                  </div>
                  <div className="success-content">
                    <div className="success-title">Connexion réussie !</div>
                    <div className="success-description">Redirection vers le dashboard...</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="form-card">
            <div className="form-header">
              <h1 className="form-title">Connexion</h1>
              <p className="form-subtitle">Connectez-vous à votre compte</p>
            </div>

            {success && !showSuccessAnimation && (
              <div className="success-message">
                <div className="success-icon">
                  <i className="fas fa-check-circle"></i>
                </div>
                <div className="success-content">
                  <div className="success-title">Succès !</div>
                  <div className="success-description">{success}</div>
                </div>
              </div>
            )}

            {error && (
              <div className="alert alert-danger" role="alert">
                <i className="fas fa-exclamation-triangle me-2"></i>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="form-body">
              <div className="form-group">
                <label htmlFor="username" className="form-label">
                  <i className="fas fa-user me-2"></i>
                  Nom d'utilisateur
                </label>
                <input
                  type="text"
                  id="username"
                  className="form-control"
                  value={credentials.username}
                  onChange={(e) => handleInputChange('username', e.target.value)}
                  required
                  placeholder="Entrez votre nom d'utilisateur"
                  autoComplete="username"
                />
              </div>

              <div className="form-group">
                <label htmlFor="password" className="form-label">
                  <i className="fas fa-lock me-2"></i>
                  Mot de passe
                </label>
                <div className="password-input-wrapper">
                  <input
                    type={showPassword ? "text" : "password"}
                    id="password"
                    className="form-control"
                    value={credentials.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    required
                    placeholder="Entrez votre mot de passe"
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword(!showPassword)}
                    title={showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
                  >
                    <i className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                  </button>
                </div>
              </div>

              <div className="form-options">
                <div className="form-check">
                  <input
                    type="checkbox"
                    id="rememberMe"
                    className="form-check-input"
                  />
                  <label htmlFor="rememberMe" className="form-check-label">
                    Se souvenir de moi
                  </label>
                </div>
                <Link to="/forgot-password" className="form-link">
                  Mot de passe oublié ?
                </Link>
              </div>

              <button
                type="submit"
                className={`btn btn-primary w-100 ${!formValid ? 'btn-disabled' : ''}`}
                disabled={loading || !formValid}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                    Connexion en cours...
                  </>
                ) : (
                  <>
                    <i className="fas fa-sign-in-alt me-2"></i>
                    Se connecter
                  </>
                )}
              </button>
            </form>

            <div className="form-footer">
              <p className="text-center">
                Pas encore de compte ? <Link to="/register" className="form-link">S'inscrire</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login; 