import React, { useState } from 'react';
import './App.css';

function App() {
  const [activeNav, setActiveNav] = useState('home');

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    element?.scrollIntoView({ behavior: 'smooth' });
    setActiveNav(id);
  };

  return (
    <div className="App">
      {/* HEADER */}
      <header className="header">
        <nav className="nav">
          <div className="logo">essensia</div>
          <ul className="nav-links">
            <li><a href="#features" onClick={() => scrollToSection('features')}>Vad vi gör</a></li>
            <li><a href="#philosophy" onClick={() => scrollToSection('philosophy')}>Filosofi</a></li>
            <li><a href="#timeline" onClick={() => scrollToSection('timeline')}>Vad händer</a></li>
            <li><a href="#cta" className="nav-cta" onClick={() => scrollToSection('cta')}>Bli medlem</a></li>
          </ul>
        </nav>
      </header>

      {/* HERO */}
      <section className="hero">
        <div className="hero-container">
          <h1>Din personliga guide</h1>
          <p>Essensia hjälper dig bygga något som varar - med tydlig strategi, rätt verktyg och stöd när du behöver det.</p>
          <button 
            className="hero-cta"
            onClick={() => scrollToSection('cta')}
          >
            Bli bland de första
          </button>
        </div>
      </section>

      {/* FEATURES */}
      <section className="features" id="features">
        <div className="features-container">
          <h2 className="section-title">Vad Essensia gör</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Strategi</h3>
              <p>Klara mål och en väg framåt. Vi hjälper dig fokusera på det som verkligen spelar roll.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🛠</div>
              <h3>Verktyg</h3>
              <p>Allt på en plats. Ingen röra med tio olika appar - bara det du behöver.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Insikter</h3>
              <p>Se vad som fungerar. Förstå dina siffror. Ta beslut baserat på data.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🤝</div>
              <h3>Stöd</h3>
              <p>Du är aldrig ensam. Vi är här när du behöver vägledning eller bara ett snack.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📈</div>
              <h3>Tillväxt</h3>
              <p>Väx på dina villkor. Med system som skalas tillsammans med dig.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">💪</div>
              <h3>Uthållighet</h3>
              <p>Bygga något som varar. Inte bara snabba wins, utan långsiktig framgång.</p>
            </div>
          </div>
        </div>
      </section>

      {/* PHILOSOPHY */}
      <section className="philosophy" id="philosophy">
        <div className="philosophy-container">
          <h2>Filosofi</h2>
          <p className="philosophy-subtitle">Vad vi tror på</p>
          <div className="philosophy-content">
            <p>Vi tror att var och en har potentialen att bygga något meningsfullt. Men det räcker inte med bara vilja - du behöver rätt förutsättningar.</p>
            <p>Essensia är byggd på tanken att framgång inte är en slump. Det är resultatet av tydlig strategi, rätt verktyg och stöd när vägen blir krokig.</p>
            <p>Vi bygger inte för att göra allting enklare - vi bygger för att göra det möjligt att fokusera på det som spelar roll. Din tid är värdefull. Dina idéer är värdefulla. Och du förtjänar ett verktyg som förstår det.</p>
          </div>
        </div>
      </section>

      {/* TIMELINE */}
      <section className="timeline" id="timeline">
        <div className="timeline-container">
          <h2>Vad som händer nu</h2>
          <div className="timeline-grid">
            <div className="timeline-item">
              <div className="timeline-number">1</div>
              <h4>Juni - Juli</h4>
              <p>Vi slutför Essensia tillsammans med våra första members.</p>
            </div>
            <div className="timeline-item">
              <div className="timeline-number">2</div>
              <h4>Juli - Augusti</h4>
              <p>Ni formar systemet. Vi lyssnar och anpassar baserat på vad ni behöver.</p>
            </div>
            <div className="timeline-item">
              <div className="timeline-number">3</div>
              <h4>September</h4>
              <p>Essensia lanseras officiellt. Den version ni hjälpte forma är redan här.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section" id="cta">
        <div className="cta-container">
          <h2>Bli en av de första</h2>
          <p>Vi öppnar platserna långsamt - så att vi kan ge varje medlem vad de behöver. Om detta resonerar med dig, anmäl dig nu.</p>
          <a href="https://links.hereis.se/widget/form/EssensiaPriorityAccess" className="cta-button">Ansök för early access</a>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-links">
            <a href="#top">Hem</a>
            <a href="mailto:hello@essensiadesign.se">Kontakt</a>
            <a href="#">Privacy Policy</a>
            <a href="#">Villkor</a>
          </div>
          <div className="footer-copyright">
            &copy; 2026 Essensia. Byggd för att du ska kunna bygga något som varar.
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

