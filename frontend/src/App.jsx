import { useState } from 'react';
import { Header } from './components/Header';
import { LoginPage } from './pages/LoginPage';
import { HomePage } from './pages/HomePage';
import { IntroPage } from './pages/IntroPage';
import MapPage from './pages/MapPage';
import QAPage from './pages/QAPage';
import ReportPage from './pages/ReportPage';
import WordCloud from './pages/WordCloud';

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(true);
  const [currentPage, setCurrentPage] = useState('home');

  if (!isLoggedIn) {
    return <LoginPage onLogin={() => setIsLoggedIn(true)} />;
  }

  return (
    <div>
      <Header
        currentPage={currentPage}
        onNavigate={setCurrentPage}
        onLogout={() => setIsLoggedIn(false)}
      />
      <main>
        {currentPage === 'home' && <HomePage onNavigate={setCurrentPage} />}
        {currentPage === 'intro' && <IntroPage />}
        {currentPage === 'gis' && <MapPage />}
        {currentPage === 'qa' && <QAPage />}
        {currentPage === 'report' && <ReportPage />}
        {currentPage === 'wordcloud' && <WordCloud />}
      </main>
    </div>
  );
}