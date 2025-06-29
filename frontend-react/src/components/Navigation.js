import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

const Navigation = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [notifications, setNotifications] = useState([
    { id: 1, message: 'Nouveau scraping terminé', type: 'success', time: '2 min' },
    { id: 2, message: 'Mise à jour disponible', type: 'info', time: '1 heure' },
    { id: 3, message: 'Quota API atteint à 80%', type: 'warning', time: '3 heures' }
  ]);
  const [user, setUser] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    const userData = localStorage.getItem('user');
    if (userData) setUser(JSON.parse(userData));
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLogout = async () => {
    if (isLoggingOut) return;
    setIsLoggingOut(true);
    try {
      await authService.logout();
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.dispatchEvent(new CustomEvent('authChange'));
      setUser(null);
      setShowUserMenu(false);
      setTimeout(() => navigate('/login', { replace: true }), 100);
    } catch (error) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.dispatchEvent(new CustomEvent('authChange'));
      setUser(null);
      setShowUserMenu(false);
      setTimeout(() => navigate('/login', { replace: true }), 100);
    } finally {
      setIsLoggingOut(false);
    }
  };

  const removeNotification = (id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success': return 'fas fa-check-circle';
      case 'warning': return 'fas fa-exclamation-triangle';
      case 'error': return 'fas fa-times-circle';
      case 'info': return 'fas fa-info-circle';
      default: return 'fas fa-bell';
    }
  };

  // Gestion du clic en dehors des dropdowns
  useEffect(() => {
    const handleClick = (e) => {
      if (!e.target.closest('.user-menu')) setShowUserMenu(false);
      if (!e.target.closest('.notification-dropdown-wrapper')) setShowNotifications(false);
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  return (
    <nav className={`navbar${isScrolled ? ' navbar-scrolled' : ''}`}> 
      <div className="navbar-container">
        {/* Logo et nom */}
        <Link className="navbar-brand" to="/">
          <i className="fas fa-chart-line me-2"></i>
          FinData IA-M.K
        </Link>
        {/* Navigation principale */}
        <ul className="navbar-nav">
          {user ? (
            // Navigation pour utilisateurs connectés
            <>
              <li>
                <Link className={`nav-link${location.pathname === '/dashboard' ? ' active' : ''}`} to="/dashboard">
                  <i className="fas fa-tachometer-alt me-2"></i>Dashboard
                </Link>
              </li>
              <li>
                <Link className={`nav-link${location.pathname === '/scraping' ? ' active' : ''}`} to="/scraping">
                  <i className="fas fa-spider me-2"></i>Scraping
                </Link>
              </li>
              <li>
                <Link className={`nav-link${location.pathname === '/analytics' ? ' active' : ''}`} to="/analytics">
                  <i className="fas fa-chart-bar me-2"></i>Analytics
                </Link>
              </li>
              <li>
                <Link className={`nav-link${location.pathname === '/documentation' ? ' active' : ''}`} to="/documentation">
                  <i className="fas fa-book me-2"></i>Documentation
                </Link>
              </li>
            </>
          ) : (
            // Navigation pour utilisateurs non connectés
            <>
              <li>
                <Link className={`nav-link${location.pathname === '/login' ? ' active' : ''}`} to="/login">
                  <i className="fas fa-sign-in-alt me-2"></i>Connexion
                </Link>
              </li>
              <li>
                <Link className={`nav-link${location.pathname === '/register' ? ' active' : ''}`} to="/register">
                  <i className="fas fa-user-plus me-2"></i>Inscription
                </Link>
              </li>
            </>
          )}
        </ul>
        {/* Actions utilisateur */}
        <div className="navbar-actions">
          {user ? (
            // Actions pour utilisateurs connectés
            <>
              {/* Notifications */}
              <div className="notification-dropdown-wrapper">
                <button className="nav-link" onClick={() => setShowNotifications(v => !v)} aria-label="Notifications">
                  <i className="fas fa-bell fa-lg"></i>
                  {notifications.length > 0 && (
                    <span className="badge bg-danger" style={{ position: 'absolute', top: 2, right: 2 }}>{notifications.length}</span>
                  )}
                </button>
                {showNotifications && (
                  <div className="dropdown-menu notification-dropdown animate-fade-in-down">
                    <div className="dropdown-header">
                      <span>Notifications</span>
                      <button className="btn btn-sm btn-outline-primary" onClick={() => setNotifications([])}>Tout marquer comme lu</button>
                    </div>
                    <div className="dropdown-divider"></div>
                    {notifications.length === 0 ? (
                      <div className="empty-state">
                        <i className="fas fa-inbox fa-2x"></i>
                        <div>Aucune notification</div>
                      </div>
                    ) : notifications.map(notif => (
                      <div key={notif.id} className="dropdown-item">
                        <i className={`${getNotificationIcon(notif.type)} me-2`}></i>
                        <span>{notif.message}</span>
                        <span className="ms-auto text-muted" style={{ fontSize: 11 }}>{notif.time}</span>
                        <button className="btn btn-xs btn-link ms-2" onClick={() => removeNotification(notif.id)} aria-label="Supprimer">
                          <i className="fas fa-times"></i>
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {/* Profil utilisateur */}
              <div className="user-menu">
                <button className="user-button" onClick={() => setShowUserMenu(v => !v)}>
                  <span className="user-avatar">
                    {user?.username ? user.username[0].toUpperCase() : <i className="fas fa-user"></i>}
                  </span>
                  <span className="user-name">{user?.username || 'Compte'}</span>
                  <i className="fas fa-chevron-down ms-1"></i>
                </button>
                {showUserMenu && (
                  <div className="user-dropdown animate-fade-in-down">
                    <Link className="dropdown-item" to="/account">
                      <i className="fas fa-user-cog me-2"></i>Mon compte
                    </Link>
                    <div className="dropdown-divider"></div>
                    <button className="dropdown-item" onClick={handleLogout} disabled={isLoggingOut}>
                      <i className="fas fa-sign-out-alt me-2"></i>Se déconnecter
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            // Actions pour utilisateurs non connectés (optionnel - peut être vide)
            <div className="navbar-actions-guest">
              <span className="text-muted">Bienvenue sur FinData IA-M.K</span>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navigation; 