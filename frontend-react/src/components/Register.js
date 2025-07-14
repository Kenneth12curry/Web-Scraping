import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService, formatError } from '../services/api';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    company: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  // const [success, setSuccess] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = () => {
    if (!formData.username || formData.username.length < 3) {
      setError('Le nom d\'utilisateur doit contenir au moins 3 caractères');
      return false;
    }

    if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('Veuillez entrer une adresse email valide');
      return false;
    }

    if (!formData.password || formData.password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return false;
    }

    if (!formData.firstName || !formData.lastName) {
      setError('Veuillez remplir votre nom et prénom');
      return false;
    }

    if (!agreedToTerms) {
      setError('Veuillez accepter les conditions d\'utilisation');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    try {
      // Appel à l'API d'inscription
      const response = await authService.register({
        username: formData.username,
        password: formData.password,
        email: formData.email,
        first_name: formData.firstName,
        last_name: formData.lastName,
        company: formData.company
      });

      if (response.data.success) {
        setSuccess('Inscription réussie ! Vous allez être redirigé vers la page de connexion.');
        setShowSuccessModal(true);
        
        // Redirection après 3 secondes
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else {
        setError(response.data.message || 'Erreur lors de l\'inscription');
      }

    } catch (error) {
      setError(formatError(error));
    } finally {
      setLoading(false);
    }
  };

  const getPasswordStrength = (password) => {
    if (!password) return { strength: 0, label: '', color: '' };
    
    let strength = 0;
    if (password.length >= 6) strength++;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;

    const labels = ['Très faible', 'Faible', 'Moyen', 'Bon', 'Très bon'];
    const colors = ['#ef4444', '#f59e0b', '#eab308', '#22c55e', '#16a34a'];
    
    return {
      strength: Math.min(strength, 4),
      label: labels[Math.min(strength, 4)],
      color: colors[Math.min(strength, 4)]
    };
  };

  const passwordStrength = getPasswordStrength(formData.password);

  return (
    <div className="auth-container">
      <div className="auth-split-left">
        <div className="brand-logo">
          <i className="fas fa-chart-line"></i>
        </div>
        <h1 className="brand-title">FinData IA-M.K</h1>
        <p className="brand-subtitle">Rejoignez notre plateforme pour transformer vos données financières en décisions stratégiques.</p>
      </div>
      <div className="auth-split-right">
        <div className="form-container">
          {/* Modal de succès */}
          {showSuccessModal && (
            <div className="modal-overlay">
              <div className="modal-content">
                <div className="success-message">
                  <div className="success-icon">
                    <i className="fas fa-check-circle"></i>
                  </div>
                  <div className="success-content">
                    <div className="success-title">🎉 Inscription réussie !</div>
                    <div className="success-description">
                      Votre compte a été créé avec succès. Vous allez être redirigé vers la page de connexion dans quelques secondes...
                    </div>
                    <button 
                      className="btn btn-primary mt-3"
                      onClick={() => navigate('/login')}
                    >
                      <i className="fas fa-sign-in-alt me-2"></i>
                      Aller à la connexion maintenant
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="form-card">
            <div className="form-header">
              <h1 className="form-title">Inscription</h1>
              <p className="form-subtitle">Créez votre compte pour accéder à la plateforme</p>
            </div>

            {error && (
              <div className="alert alert-danger" role="alert">
                <i className="fas fa-exclamation-triangle me-2"></i>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="form-body">
              <div className="row">
                <div className="col-md-6">
                  <div className="form-group">
                    <label htmlFor="firstName" className="form-label">
                      <i className="fas fa-user"></i>
                      Prénom
                    </label>
                    <input
                      type="text"
                      id="firstName"
                      name="firstName"
                      className="form-control"
                      value={formData.firstName}
                      onChange={handleInputChange}
                      required
                      placeholder="Votre prénom"
                    />
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="form-group">
                    <label htmlFor="lastName" className="form-label">
                      <i className="fas fa-user"></i>
                      Nom
                    </label>
                    <input
                      type="text"
                      id="lastName"
                      name="lastName"
                      className="form-control"
                      value={formData.lastName}
                      onChange={handleInputChange}
                      required
                      placeholder="Votre nom"
                    />
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="username" className="form-label">
                  <i className="fas fa-at"></i>
                  Nom d'utilisateur
                </label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  className="form-control"
                  value={formData.username}
                  onChange={handleInputChange}
                  required
                  placeholder="Choisissez un nom d'utilisateur unique"
                />
              </div>

              <div className="form-group">
                <label htmlFor="email" className="form-label">
                  <i className="fas fa-envelope"></i>
                  Adresse email
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  className="form-control"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  placeholder="votre.email@exemple.com"
                />
              </div>

              <div className="form-group">
                <label htmlFor="password" className="form-label">
                  <i className="fas fa-lock"></i>
                  Mot de passe
                </label>
                <div className="password-input-wrapper">
                  <input
                    type={showPassword ? "text" : "password"}
                    id="password"
                    name="password"
                    className="form-control"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                    placeholder="Créez un mot de passe sécurisé"
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
                {formData.password && (
                  <div className="password-strength">
                    <div className="strength-bar">
                      <div 
                        className="strength-fill" 
                        style={{ 
                          width: `${(passwordStrength.strength + 1) * 20}%`,
                          backgroundColor: passwordStrength.color 
                        }}
                      ></div>
                    </div>
                    <small className="strength-label" style={{ color: passwordStrength.color }}>
                      Force du mot de passe : {passwordStrength.label}
                    </small>
                  </div>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword" className="form-label">
                  <i className="fas fa-lock"></i>
                  Confirmer le mot de passe
                </label>
                <div className="password-input-wrapper">
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    id="confirmPassword"
                    name="confirmPassword"
                    className="form-control"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    required
                    placeholder="Confirmez votre mot de passe"
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    title={showConfirmPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
                  >
                    <i className={`fas ${showConfirmPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="company" className="form-label">
                  <i className="fas fa-building"></i>
                  Entreprise <small className="text-muted">(optionnel)</small>
                </label>
                <input
                  type="text"
                  id="company"
                  name="company"
                  className="form-control"
                  value={formData.company}
                  onChange={handleInputChange}
                  placeholder="Nom de votre entreprise ou organisation"
                />
              </div>

              <div className="form-check mb-4">
                <input
                  type="checkbox"
                  id="agreedToTerms"
                  className="form-check-input"
                  checked={agreedToTerms}
                  onChange={(e) => setAgreedToTerms(e.target.checked)}
                  required
                />
                <label htmlFor="agreedToTerms" className="form-check-label">
                  J'accepte les <Link to="/terms" className="form-link">conditions d'utilisation</Link> et la <Link to="/privacy" className="form-link">politique de confidentialité</Link> de FinData IA-M.K
                </label>
              </div>

              <button
                type="submit"
                className="btn btn-primary w-100"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                    Création du compte en cours...
                  </>
                ) : (
                  <>
                    <i className="fas fa-user-plus me-2"></i>
                    Créer mon compte
                  </>
                )}
              </button>
            </form>

            <div className="form-footer">
              <p>
                Vous avez déjà un compte ? <Link to="/login" className="form-link">Se connecter</Link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register; 