import React, { useState, useEffect } from 'react';
import LoginPage    from './pages/LoginPage.jsx';
import WorkspacePage from './pages/WorkspacePage.jsx';
import './index.css';

export default function App() {
  const [dark,      setDark]      = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userName,   setUserName]   = useState('Alex');

  /* Sync dark class on <html> */
  useEffect(() => {
    const root = document.documentElement;
    if (dark) root.classList.add('dark');
    else       root.classList.remove('dark');
  }, [dark]);

  const handleLogin = (name, _token) => {
    setUserName(name || 'Alex');
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserName('Alex');
  };

  if (!isLoggedIn) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <WorkspacePage
      dark={dark}
      onToggleDark={() => setDark((d) => !d)}
      userName={userName}
      onLogout={handleLogout}
    />
  );
}
