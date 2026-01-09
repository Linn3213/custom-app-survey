import React, { useState } from 'react';
import './index.css';

const CustomAppSurvey = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [started, setStarted] = useState(false);

  const questions = [
    {
      id: 'business_type',
      type: 'single',
      question: 'Vad beskriver dig bäst?',
      subtitle: 'Välj det som passar',
      options: [
        { value: 'solopreneur', label: 'Soloentreprenör', description: 'Driver allt själv' },
        { value: 'small_business', label: 'Småföretagare', description: '1-10 anställda' },
        { value: 'coach_consultant', label: 'Coach eller konsult', description: 'Säljer kunskap och tid' },
        { value: 'creator', label: 'Kreatör eller influencer', description: 'Bygger publik och varumärke' },
        { value: 'team_leader', label: 'Teamledare', description: 'Leder ett team i ett större företag' },
        { value: 'startup', label: 'Startup-grundare', description: 'Bygger något nytt' }
      ]
    },
    {
      id: 'biggest_frustration',
      type: 'single',
      question: 'Vad tar mest av din tid och energi?',
      subtitle: 'Det som känns mest frustrerande',
      options: [
        { value: 'manual_tasks', label: 'Manuella uppgifter', description: 'Saker som borde gå automatiskt' },
        { value: 'scattered_tools', label: 'För många verktyg', description: 'Allt ligger på olika ställen' },
        { value: 'client_management', label: 'Hålla koll på kunder', description: 'Bokningar, uppföljning, kommunikation' },
        { value: 'content_creation', label: 'Skapa innehåll', description: 'Kommer aldrig ikapp' },
        { value: 'tracking_progress', label: 'Följa upp resultat', description: 'Vet inte vad som fungerar' },
        { value: 'team_coordination', label: 'Samordna teamet', description: 'Alla gör olika saker' }
      ]
    },
    {
      id: 'dream_app',
      type: 'multi',
      question: 'Om du hade en app byggd just för dig – vad skulle den göra?',
      subtitle: 'Välj allt som lockar',
      options: [
        { value: 'booking', label: 'Hantera bokningar' },
        { value: 'crm', label: 'Hålla koll på kunder' },
        { value: 'content', label: 'Planera innehåll' },
        { value: 'invoicing', label: 'Fakturor och betalningar' },
        { value: 'automation', label: 'Automatisera uppgifter' },
        { value: 'analytics', label: 'Visa statistik och resultat' },
        { value: 'communication', label: 'Kommunicera med kunder' },
        { value: 'project_management', label: 'Hantera projekt' },
        { value: 'team_tools', label: 'Verktyg för teamet' },
        { value: 'custom', label: 'Något helt unikt för mig' }
      ]
    },
    {
      id: 'current_solution',
      type: 'multi',
      question: 'Vad använder du idag för att hålla ihop allt?',
      subtitle: 'Välj alla du känner igen',
      options: [
        { value: 'spreadsheets', label: 'Excel / Google Sheets' },
        { value: 'notion', label: 'Notion' },
        { value: 'trello', label: 'Trello / Asana' },
        { value: 'calendar', label: 'Kalendern' },
        { value: 'paper', label: 'Papper och penna' },
        { value: 'crm_tool', label: 'CRM-verktyg' },
        { value: 'multiple_apps', label: 'Massa olika appar' },
        { value: 'memory', label: 'Huvudet (och hoppas på det bästa)' },
        { value: 'nothing', label: 'Ingenting strukturerat' }
      ]
    },
    {
      id: 'pain_level',
      type: 'single',
      question: 'Hur mycket påverkar detta din vardag?',
      subtitle: 'Var ärlig',
      options: [
        { value: 'critical', label: 'Det kostar mig pengar och kunder', description: 'Jag behöver en lösning nu' },
        { value: 'significant', label: 'Det tar timmar varje vecka', description: 'Tid jag kunde lagt på annat' },
        { value: 'annoying', label: 'Det är irriterande men hanterbart', description: 'Skulle vara skönt att lösa' },
        { value: 'minor', label: 'Mest en önskan', description: 'Inget akut' }
      ]
    },
    {
      id: 'tried_before',
      type: 'single',
      question: 'Har du försökt lösa detta tidigare?',
      subtitle: 'Ingen skam i att ha testat',
      options: [
        { value: 'many_tools', label: 'Ja, testat massa verktyg', description: 'Men inget passade riktigt' },
        { value: 'custom_attempt', label: 'Ja, försökt bygga något själv', description: 'Sheets, Notion, egna system' },
        { value: 'hired_help', label: 'Ja, anlitat någon', description: 'Men det blev inte som jag ville' },
        { value: 'not_really', label: 'Inte på allvar', description: 'Har inte hittat rätt lösning' }
      ]
    },
    {
      id: 'importance_features',
      type: 'ranking',
      question: 'Vad är viktigast för dig i ett verktyg?',
      subtitle: 'Välj topp 3 i ordning',
      options: [
        { value: 'ease_of_use', label: 'Enkelt att använda' },
        { value: 'customization', label: 'Anpassat efter mina behov' },
        { value: 'design', label: 'Snyggt och professionellt' },
        { value: 'automation', label: 'Sparar tid automatiskt' },
        { value: 'integration', label: 'Kopplas till annat jag använder' },
        { value: 'support', label: 'Bra support och hjälp' },
        { value: 'price', label: 'Prisvärt' },
        { value: 'mobile', label: 'Fungerar på mobilen' }
      ]
    },
    {
      id: 'investment',
      type: 'single',
      question: 'Vad skulle du investera i ett verktyg som löser detta?',
      subtitle: 'Tänk på vad det sparar dig i tid och pengar',
      options: [
        { value: 'under_500', label: 'Upp till 500 kr/mån', description: 'För något som verkligen hjälper' },
        { value: '500_1000', label: '500–1000 kr/mån', description: 'Om det ersätter flera verktyg' },
        { value: '1000_2500', label: '1000–2500 kr/mån', description: 'För en komplett lösning' },
        { value: '2500_plus', label: 'Över 2500 kr/mån', description: 'Om det transformerar min business' },
        { value: 'one_time', label: 'Hellre engångskostnad', description: 'Vill äga mitt verktyg' }
      ]
    },
    {
      id: 'timeline',
      type: 'single',
      question: 'När skulle du vilja ha en lösning?',
      subtitle: 'Var realistisk',
      options: [
        { value: 'asap', label: 'Så snart som möjligt', description: 'Jag är redo nu' },
        { value: 'quarter', label: 'Inom 3 månader', description: 'Planerar framåt' },
        { value: 'half_year', label: 'Inom 6 månader', description: 'Vill ha det på plats i år' },
        { value: 'exploring', label: 'Bara utforskar', description: 'Inget bråttom' }
      ]
    },
    {
      id: 'open_feedback',
      type: 'text',
      question: 'Om du kunde ha vilken app som helst – vad skulle den göra?',
      subtitle: 'Dröm stort. Beskriv din perfekta lösning.',
      placeholder: 'Berätta hur din drömapp skulle fungera och vad den skulle lösa för dig...'
    }
  ];

  const handleSingleAnswer = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
    setTimeout(() => {
      if (currentStep < questions.length - 1) {
        setCurrentStep(currentStep + 1);
      }
    }, 300);
  };

  const handleMultiAnswer = (questionId, value) => {
    setAnswers(prev => {
      const current = prev[questionId] || [];
      if (current.includes(value)) {
        return { ...prev, [questionId]: current.filter(v => v !== value) };
      } else {
        return { ...prev, [questionId]: [...current, value] };
      }
    });
  };

  const handleRankingAnswer = (questionId, value) => {
    setAnswers(prev => {
      const current = prev[questionId] || [];
      if (current.includes(value)) {
        return { ...prev, [questionId]: current.filter(v => v !== value) };
      } else if (current.length < 3) {
        return { ...prev, [questionId]: [...current, value] };
      }
      return prev;
    });
  };

  const handleTextAnswer = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
  };

  const handleNext = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Last question - redirect directly to GHL form
      const params = new URLSearchParams({
        business_type: answers.business_type || '',
        biggest_frustration: answers.biggest_frustration || '',
        dream_app: answers.dream_app?.join(', ') || '',
        current_solution: answers.current_solution?.join(', ') || '',
        pain_level: answers.pain_level || '',
        tried_before: answers.tried_before || '',
        top_3_priorities: answers.importance_features?.join(', ') || '',
        investment: answers.investment || '',
        timeline: answers.timeline || '',
        open_feedback: answers.open_feedback || ''
      });
      
      window.location.href = `https://links.hereis.se/widget/form/PxLuonGgDYQcEzsNwF8Y?${params.toString()}`;
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const question = questions[currentStep];
  const progress = ((currentStep + 1) / questions.length) * 100;
  const currentAnswer = answers[question?.id];

  const canProceed = () => {
    if (!question) return false;
    if (question.type === 'text') return true;
    if (question.type === 'single') return !!currentAnswer;
    if (question.type === 'multi') return currentAnswer && currentAnswer.length > 0;
    if (question.type === 'ranking') return currentAnswer && currentAnswer.length === 3;
    return false;
  };

  // ============================================
  // STYLES
  // ============================================
  
  const pageStyle = {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '24px',
    background: 'linear-gradient(180deg, #F7F3EE 0%, #EDE6DD 100%)'
  };

  const containerStyle = {
    maxWidth: '36rem',
    width: '100%',
    textAlign: 'center'
  };

  const headingStyle = {
    fontFamily: "'Cormorant Garamond', Georgia, serif",
    color: '#2D2621',
    letterSpacing: '0.03em'
  };

  const decorLineLeft = {
    height: '1px',
    width: '64px',
    background: 'linear-gradient(to right, transparent, rgba(107, 90, 77, 0.4))'
  };

  const decorLineRight = {
    height: '1px',
    width: '64px',
    background: 'linear-gradient(to left, transparent, rgba(107, 90, 77, 0.4))'
  };

  const labelStyle = {
    margin: '0 16px',
    color: '#5C4D42',
    fontSize: '0.7rem',
    letterSpacing: '0.3em',
    textTransform: 'uppercase'
  };

  // ============================================
  // START SCREEN
  // ============================================
  if (!started) {
    return (
      <div style={pageStyle}>
        <div style={containerStyle}>
          
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '40px' }}>
            <div style={decorLineLeft}></div>
            <div style={labelStyle}>Exklusiv Inbjudan</div>
            <div style={decorLineRight}></div>
          </div>

          <h1 style={{ ...headingStyle, fontSize: '2.5rem', fontWeight: '300', marginBottom: '8px', lineHeight: '1.2' }}>
            Tänk Om Du Hade
          </h1>
          <h2 style={{ 
            ...headingStyle, 
            fontSize: '2.8rem', 
            fontWeight: '300', 
            marginBottom: '32px',
            background: 'linear-gradient(135deg, #6B5A4D 0%, #8B7355 50%, #6B5A4D 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: '0.05em'
          }}>
            Din Egen App
          </h2>

          <p style={{ fontSize: '0.95rem', marginBottom: '24px', maxWidth: '26rem', marginLeft: 'auto', marginRight: 'auto', lineHeight: '1.8', color: '#3D352F' }}>
            En app byggd helt efter dina behov. Som gör precis det du vill. Utan kompromisser.
          </p>

          <p style={{ fontSize: '0.85rem', marginBottom: '48px', color: '#4A4039', fontStyle: 'italic' }}>
            Berätta vad du behöver – så visar vi vad som är möjligt.
          </p>

          <button
            onClick={() => setStarted(true)}
            style={{
              background: 'transparent',
              border: '1px solid rgba(107, 90, 77, 0.4)',
              color: '#5C4D42',
              padding: '16px 48px',
              fontSize: '0.75rem',
              letterSpacing: '0.2em',
              textTransform: 'uppercase',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = 'rgba(107, 90, 77, 0.08)';
              e.currentTarget.style.borderColor = 'rgba(107, 90, 77, 0.7)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.borderColor = 'rgba(107, 90, 77, 0.4)';
            }}
          >
            Berätta Vad Du Behöver
          </button>

          <p style={{ marginTop: '32px', fontSize: '0.75rem', color: '#5C4D42', letterSpacing: '0.1em' }}>
            10 frågor • 3 minuter
          </p>
        </div>
      </div>
    );
  }

  // ============================================
  // QUESTIONS
  // ============================================
  return (
    <div style={pageStyle}>
      <div style={{ ...containerStyle, maxWidth: '40rem' }}>
        
        {/* Progress */}
        <div style={{ marginBottom: '48px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#5C4D42', letterSpacing: '0.15em' }}>
              Fråga {currentStep + 1} av {questions.length}
            </span>
            <span style={{ fontSize: '0.75rem', color: '#6B5A4D', letterSpacing: '0.1em' }}>
              {Math.round(progress)}%
            </span>
          </div>
          <div style={{ height: '2px', width: '100%', background: 'rgba(107, 90, 77, 0.15)' }}>
            <div 
              style={{ 
                height: '100%', 
                width: `${progress}%`, 
                background: 'linear-gradient(90deg, #6B5A4D, #8B7355)',
                transition: 'width 0.5s ease'
              }}
            />
          </div>
        </div>

        {/* Question */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 style={{ ...headingStyle, fontSize: '1.5rem', fontWeight: '300', marginBottom: '12px', lineHeight: '1.4' }}>
            {question.question}
          </h2>
          <p style={{ fontSize: '0.8rem', color: '#5C4D42', letterSpacing: '0.05em' }}>
            {question.subtitle}
          </p>
        </div>

        {/* Options */}
        <div style={{ marginBottom: '40px' }}>
          
          {/* SINGLE CHOICE */}
          {question.type === 'single' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {question.options.map((option) => (
                <button
                  key={option.value}
                  onClick={() => handleSingleAnswer(question.id, option.value)}
                  style={{
                    width: '100%',
                    padding: '20px',
                    textAlign: 'left',
                    background: currentAnswer === option.value 
                      ? 'rgba(107, 90, 77, 0.12)' 
                      : 'rgba(255, 255, 255, 0.5)',
                    border: currentAnswer === option.value 
                      ? '1px solid rgba(107, 90, 77, 0.5)' 
                      : '1px solid rgba(107, 90, 77, 0.15)',
                    cursor: 'pointer',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <span style={{ display: 'block', fontSize: '0.9rem', marginBottom: '4px', color: '#2D2621' }}>
                    {option.label}
                  </span>
                  {option.description && (
                    <span style={{ display: 'block', fontSize: '0.75rem', color: '#5C4D42' }}>
                      {option.description}
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}

          {/* MULTI CHOICE */}
          {question.type === 'multi' && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px' }}>
              {question.options.map((option) => {
                const isSelected = currentAnswer?.includes(option.value);
                return (
                  <button
                    key={option.value}
                    onClick={() => handleMultiAnswer(question.id, option.value)}
                    style={{
                      padding: '16px',
                      textAlign: 'center',
                      background: isSelected 
                        ? 'rgba(107, 90, 77, 0.12)' 
                        : 'rgba(255, 255, 255, 0.5)',
                      border: isSelected 
                        ? '1px solid rgba(107, 90, 77, 0.5)' 
                        : '1px solid rgba(107, 90, 77, 0.15)',
                      cursor: 'pointer',
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <span style={{ fontSize: '0.85rem', color: isSelected ? '#4A3F37' : '#3D352F' }}>
                      {option.label}
                    </span>
                  </button>
                );
              })}
            </div>
          )}

          {/* RANKING */}
          {question.type === 'ranking' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {question.options.map((option) => {
                const rankIndex = currentAnswer?.indexOf(option.value);
                const isSelected = rankIndex !== undefined && rankIndex !== -1;
                return (
                  <button
                    key={option.value}
                    onClick={() => handleRankingAnswer(question.id, option.value)}
                    style={{
                      padding: '16px 20px',
                      textAlign: 'left',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '16px',
                      background: isSelected 
                        ? 'rgba(107, 90, 77, 0.12)' 
                        : 'rgba(255, 255, 255, 0.5)',
                      border: isSelected 
                        ? '1px solid rgba(107, 90, 77, 0.5)' 
                        : '1px solid rgba(107, 90, 77, 0.15)',
                      cursor: currentAnswer?.length >= 3 && !isSelected ? 'not-allowed' : 'pointer',
                      opacity: currentAnswer?.length >= 3 && !isSelected ? 0.5 : 1,
                      transition: 'all 0.3s ease'
                    }}
                  >
                    <span style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: isSelected ? '#6B5A4D' : 'rgba(107, 90, 77, 0.15)',
                      color: isSelected ? '#FFFFFF' : '#7A6E63',
                      fontSize: '0.8rem',
                      fontWeight: '500'
                    }}>
                      {isSelected ? rankIndex + 1 : ''}
                    </span>
                    <span style={{ fontSize: '0.9rem', color: isSelected ? '#4A3F37' : '#3D352F' }}>
                      {option.label}
                    </span>
                  </button>
                );
              })}
              <p style={{ fontSize: '0.75rem', color: '#5C4D42', marginTop: '8px', textAlign: 'center' }}>
                {currentAnswer?.length || 0} av 3 valda
              </p>
            </div>
          )}

          {/* TEXT INPUT */}
          {question.type === 'text' && (
            <textarea
              value={currentAnswer || ''}
              onChange={(e) => handleTextAnswer(question.id, e.target.value)}
              placeholder={question.placeholder}
              style={{
                width: '100%',
                minHeight: '150px',
                padding: '20px',
                background: 'rgba(255, 255, 255, 0.6)',
                border: '1px solid rgba(107, 90, 77, 0.2)',
                color: '#2D2621',
                fontSize: '0.9rem',
                lineHeight: '1.7',
                resize: 'vertical',
                outline: 'none',
                fontFamily: 'inherit',
                transition: 'all 0.3s ease'
              }}
              onFocus={(e) => e.currentTarget.style.borderColor = 'rgba(107, 90, 77, 0.5)'}
              onBlur={(e) => e.currentTarget.style.borderColor = 'rgba(107, 90, 77, 0.2)'}
            />
          )}
        </div>

        {/* Navigation */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button
            onClick={handleBack}
            style={{
              background: 'none',
              border: 'none',
              color: currentStep > 0 ? '#5C4D42' : 'transparent',
              fontSize: '0.8rem',
              cursor: currentStep > 0 ? 'pointer' : 'default',
              letterSpacing: '0.05em'
            }}
          >
            Tillbaka
          </button>

          {(question.type !== 'single' || !canProceed()) && (
            <button
              onClick={handleNext}
              disabled={!canProceed() && question.type !== 'text'}
              style={{
                background: canProceed() || question.type === 'text'
                  ? 'linear-gradient(135deg, rgba(107, 90, 77, 0.15) 0%, rgba(107, 90, 77, 0.08) 100%)'
                  : 'rgba(107, 90, 77, 0.05)',
                border: canProceed() || question.type === 'text'
                  ? '1px solid rgba(107, 90, 77, 0.5)'
                  : '1px solid rgba(107, 90, 77, 0.15)',
                color: canProceed() || question.type === 'text' ? '#4A3F37' : '#7A6E63',
                padding: '12px 32px',
                fontSize: '0.75rem',
                letterSpacing: '0.15em',
                textTransform: 'uppercase',
                cursor: canProceed() || question.type === 'text' ? 'pointer' : 'not-allowed'
              }}
            >
              {currentStep === questions.length - 1 ? 'Slutför' : 'Nästa'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CustomAppSurvey;
