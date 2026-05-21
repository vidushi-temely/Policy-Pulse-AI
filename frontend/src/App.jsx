import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Map, Brain, BarChart2, TrendingUp, AlertTriangle, CheckCircle2, MessageSquare, X, Send, Sparkles, Activity, ShieldAlert, Volume2, VolumeX } from 'lucide-react';
import Sidebar from './components/Sidebar';
import MetricsCard from './components/MetricsCard';
import GeoMap from './components/GeoMap';
import Charts from './components/Charts';
import Predictive from './components/Predictive';
import ForensicAudit from './components/ForensicAudit';

function App() {
  const [schemes, setSchemes] = useState([]);
  const [states, setStates] = useState([]);
  const [selectedScheme, setSelectedScheme] = useState('');
  const [selectedState, setSelectedState] = useState('');
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState('geo');
  
  // Executive Alerts State
  const [alerts, setAlerts] = useState([]);
  
  // Chatbot State
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [messages, setMessages] = useState([
    { sender: 'bot', text: '### 🤖 Welcome to PulseCopilot AI Policy Advisor!\n\nI can analyze central scheme data to give you high-fidelity policy briefs and governance breakdowns.\n\nAsk me about a state, a scheme, or to compare them!' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [speakingIndex, setSpeakingIndex] = useState(null);
  const messageEndRef = useRef(null);

  // Stop talking when window closes or changes
  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel();
    };
  }, []);

  // Load initial schemes and alerts
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/schemes').then(res => {
      setSchemes(res.data.schemes);
      if (res.data.schemes.length > 0) setSelectedScheme(res.data.schemes[0]);
    }).catch(err => console.error("Error loading schemes", err));

    axios.get('http://127.0.0.1:8000/api/ai/alerts').then(res => {
      setAlerts(res.data.alerts);
    }).catch(err => console.error("Error loading alerts", err));
  }, []);

  // Load states when scheme changes
  useEffect(() => {
    if (!selectedScheme) return;
    axios.get(`http://127.0.0.1:8000/api/states?scheme=${encodeURIComponent(selectedScheme)}`).then(res => {
      setStates(res.data.states);
      if (res.data.states.length > 0) setSelectedState(res.data.states[0]);
    }).catch(err => console.error("Error loading states", err));
  }, [selectedScheme]);

  // Load data for selected scheme & state
  useEffect(() => {
    if (!selectedScheme || !selectedState) return;
    axios.get(`http://127.0.0.1:8000/api/data?scheme=${encodeURIComponent(selectedScheme)}&state=${encodeURIComponent(selectedState)}`)
      .then(res => {
        setData(res.data);
      }).catch(err => console.error("Error loading data", err));
  }, [selectedScheme, selectedState]);

  // Auto-scroll chatbot to bottom
  useEffect(() => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping]);

  const handleAlertClick = (alert) => {
    // Select scheme
    setSelectedScheme(alert.scheme);
    
    // Select state
    // We should wait briefly for the new state options to load, but we can set it immediately too
    setSelectedState(alert.state);
    
    // Scroll smoothly to metrics grid
    setTimeout(() => {
      const target = document.querySelector('.metrics-grid');
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
  };

  const handleSendMessage = (e, textOverride = '') => {
    if (e) e.preventDefault();
    const queryText = textOverride || chatInput;
    if (!queryText.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { sender: 'user', text: queryText }]);
    if (!textOverride) setChatInput('');
    setIsTyping(true);

    axios.post('http://127.0.0.1:8000/api/ai/chat', { message: queryText })
      .then(res => {
        setIsTyping(false);
        setMessages(prev => [...prev, { sender: 'bot', text: res.data.reply }]);
      })
      .catch(err => {
        setIsTyping(false);
        console.error("Chat error", err);
        setMessages(prev => [...prev, { sender: 'bot', text: 'Sorry, I encountered an issue connecting to the AI policy service.' }]);
      });
  };

  const handleSpeak = (text, index) => {
    if (speakingIndex === index) {
      window.speechSynthesis.cancel();
      setSpeakingIndex(null);
      return;
    }
    
    window.speechSynthesis.cancel();
    
    const cleanText = text
      .replace(/[#*`⚠️🤖🏥🏠🌾👷🔬🛡️⚡🏆🏆🥇🥈🥉]/g, '')
      .replace(/&rarr;/g, 'leads to')
      .trim();
      
    const utterance = new SpeechSynthesisUtterance(cleanText);
    
    const voices = window.speechSynthesis.getVoices();
    const premiumVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Microsoft')));
    if (premiumVoice) utterance.voice = premiumVoice;
    
    utterance.onend = () => setSpeakingIndex(null);
    utterance.onerror = () => setSpeakingIndex(null);
    
    setSpeakingIndex(index);
    window.speechSynthesis.speak(utterance);
  };

  const getDynamicSuggestions = () => {
    if (!selectedScheme || !selectedState) {
      return ["Compare all schemes", "Run leakage audit", "Analyze best performing state"];
    }
    return [
      `Analyze ${selectedState}`,
      `${selectedScheme} leakage audit`,
      `Compare ${selectedScheme} details`
    ];
  };

  // Convert simple markdown headings & lists inside bubbles
  const renderMessageContent = (text) => {
    const lines = text.split('\n');
    return lines.map((line, i) => {
      if (line.startsWith('### ')) {
        return <h3 key={i}>{line.replace('### ', '')}</h3>;
      }
      if (line.startsWith('- ')) {
        return <li key={i} style={{ marginLeft: '1rem', listStyleType: 'disc', margin: '0.2rem 0' }}>{line.replace('- ', '')}</li>;
      }
      if (line.startsWith('**') && line.endsWith('**')) {
        return <p key={i}><strong>{line.replace(/\*\*/g, '')}</strong></p>;
      }
      return <p key={i} style={{ margin: '0.4rem 0' }}>{line}</p>;
    });
  };

  if (!schemes.length) {
    return (
      <div className="loader-container">
        <div className="loader"></div>
        <p style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Initializing PolicyPulse AI Corporate Command Center...</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      <Sidebar 
        schemes={schemes}
        states={states}
        selectedScheme={selectedScheme}
        selectedState={selectedState}
        onSchemeChange={setSelectedScheme}
        onStateChange={setSelectedState}
        data={data}
      />

      <div className="main-content">
        <div className="content-wrapper">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div>
            <h1>⚡ PolicyPulse AI</h1>
            <p className="subtitle" style={{ marginBottom: 0 }}>Multi-Scheme Corporate Governance Platform</p>
          </div>
          <div className="glass" style={{ padding: '0.6rem 1.2rem', display: 'flex', alignItems: 'center', gap: '0.6rem', border: '1px solid #cbd5e1' }}>
            <Activity color="var(--accent)" size={18} />
            <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#475569' }}>
              SYSTEM STATUS: <span style={{ color: 'var(--success)' }}>ONLINE</span>
            </span>
          </div>
        </div>

        {data && (
          <div className="metrics-grid">
            <MetricsCard 
              title={`${selectedScheme} Beneficiaries`} 
              value={data.metrics.beneficiaries.toLocaleString('en-IN')} 
              subtitle={selectedState} 
            />
            <MetricsCard 
              title="Fund Utilization" 
              value={`${data.metrics.utilization.toFixed(1)}%`} 
              subtitle="Financial Health" 
            />
            <MetricsCard 
              title="Funds Allocated" 
              value={`₹${data.metrics.funds_allocated.toLocaleString('en-IN', {maximumFractionDigits:0})} Cr`} 
              subtitle="Total Budget" 
            />
            <MetricsCard 
              title="Funds Spent" 
              value={`₹${data.metrics.funds_spent.toLocaleString('en-IN', {maximumFractionDigits:0})} Cr`} 
              subtitle="Deployed" 
            />
          </div>
        )}

        <div className="dashboard-grid">
          {/* Left Column: Visual Modules */}
          <div className="dashboard-main-col">
            <div className="tabs-container" style={{ marginTop: 0 }}>
              <div className="tabs-header" style={{ marginTop: 0, marginBottom: '1.5rem' }}>
                <button className={`tab-btn ${activeTab === 'geo' ? 'active' : ''}`} onClick={() => setActiveTab('geo')}>
                  <Map size={18} /> Geo-Intelligence
                </button>
                <button className={`tab-btn ${activeTab === 'ai' ? 'active' : ''}`} onClick={() => setActiveTab('ai')}>
                  <Brain size={18} /> AI Diagnostics
                </button>
                <button className={`tab-btn ${activeTab === 'charts' ? 'active' : ''}`} onClick={() => setActiveTab('charts')}>
                  <BarChart2 size={18} /> Cross-Scheme Analytics
                </button>
                <button className={`tab-btn ${activeTab === 'predictive' ? 'active' : ''}`} onClick={() => setActiveTab('predictive')}>
                  <TrendingUp size={18} /> Predictive Impact Solver
                </button>
                <button className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`} onClick={() => setActiveTab('audit')}>
                  <ShieldAlert size={18} /> Forensic Integrity Guard
                </button>
              </div>

              <div className="tab-content">
                {activeTab === 'geo' && <GeoMap scheme={selectedScheme} />}
                {activeTab === 'ai' && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '2rem' }}>
                    <div className="card" style={{ padding: '2rem', background: '#ffffff', border: '1px solid #cbd5e1', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '2px solid var(--accent)', paddingBottom: '0.8rem' }}>
                        <Brain size={24} color="var(--accent)" />
                        <h3 style={{ color: 'var(--accent)', margin: 0, fontFamily: 'Outfit', fontWeight: 800 }}>🔬 AI Policy Diagnostics</h3>
                      </div>
                      <div style={{ padding: '0.5rem 0' }}>
                        <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '1.2rem', fontWeight: 600 }}>
                          Real-time performance audit for <strong>{selectedState}</strong> under the <strong>{selectedScheme}</strong> program:
                        </p>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                          {(data?.ai_brief || '').split('\n').filter(line => line.trim().length > 0).map((line, i) => {
                            let cleanLine = line.replace(/\*\*/g, '');
                            let emoji = '';
                            if (cleanLine.includes('🔴')) { emoji = '🔴'; cleanLine = cleanLine.replace('🔴', ''); }
                            else if (cleanLine.includes('🟠')) { emoji = '🟠'; cleanLine = cleanLine.replace('🟠', ''); }
                            else if (cleanLine.includes('🟢')) { emoji = '🟢'; cleanLine = cleanLine.replace('🟢', ''); }
                            else if (cleanLine.includes('📈')) { emoji = '📈'; cleanLine = cleanLine.replace('📈', ''); }
                            else if (cleanLine.includes('🎯')) { emoji = '🎯'; cleanLine = cleanLine.replace('🎯', ''); }
                            else if (cleanLine.includes('🏥')) { emoji = '🏥'; cleanLine = cleanLine.replace('🏥', ''); }
                            else if (cleanLine.includes('🏠')) { emoji = '🏠'; cleanLine = cleanLine.replace('🏠', ''); }
                            else if (cleanLine.includes('🌾')) { emoji = '🌾'; cleanLine = cleanLine.replace('🌾', ''); }
                            else if (cleanLine.includes('💧')) { emoji = '💧'; cleanLine = cleanLine.replace('💧', ''); }
                            else if (cleanLine.includes('👷')) { emoji = '👷'; cleanLine = cleanLine.replace('👷', ''); }
                            
                            let borderCol = '#e2e8f0';
                            if (emoji === '🔴' || cleanLine.toLowerCase().includes('critical') || cleanLine.toLowerCase().includes('bottleneck')) borderCol = '#ef4444';
                            else if (emoji === '🟠' || cleanLine.toLowerCase().includes('opportunity') || cleanLine.toLowerCase().includes('moderate')) borderCol = '#f59e0b';
                            else if (emoji === '🟢' || cleanLine.toLowerCase().includes('high efficiency') || cleanLine.toLowerCase().includes('excellent')) borderCol = '#10b981';
                            
                            return (
                              <div key={i} className="glass" style={{ padding: '1rem', borderLeft: `4px solid ${borderCol}`, borderRadius: '6px', background: 'rgba(255,255,255,0.4)', display: 'flex', gap: '0.8rem', alignItems: 'flex-start' }}>
                                {emoji && <span style={{ fontSize: '1.2rem', lineHeight: '1.2' }}>{emoji}</span>}
                                <span style={{ color: '#1e293b', fontSize: '0.9rem', lineHeight: 1.5, fontWeight: 500 }}>{cleanLine.trim()}</span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                    <Charts scheme={selectedScheme} mode="ai" />
                  </div>
                )}
                {activeTab === 'charts' && <Charts scheme={selectedScheme} mode="cross" />}
                {activeTab === 'predictive' && <Predictive scheme={selectedScheme} state={selectedState} />}
                {activeTab === 'audit' && <ForensicAudit scheme={selectedScheme} />}
              </div>
            </div>
          </div>

          {/* Right Column: Live Feed & Intelligence */}
          <div className="dashboard-side-col">
            {/* Live AI Alerts */}
            {alerts.length > 0 && (
              <div className="alerts-section" style={{ marginBottom: '1.5rem' }}>
                <div className="alerts-header" style={{ padding: 0, marginBottom: '1rem' }}>
                  <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem' }}>
                    <Sparkles size={18} color="var(--danger)" />
                    Live AI Alerts
                  </h3>
                  <span className="alerts-badge">{alerts.length}</span>
                </div>
                <div className="alerts-feed">
                  {alerts.map((alert, idx) => (
                    <div 
                      key={idx} 
                      className={`alert-card ${alert.type}`}
                      onClick={() => handleAlertClick(alert)}
                      style={{ flex: 'unset', width: '100%' }}
                    >
                      <div className="alert-card-title">
                        <span>{alert.title}</span>
                        {alert.type === 'danger' && <AlertTriangle size={14} color="var(--danger)" />}
                        {alert.type === 'warning' && <AlertTriangle size={14} color="var(--warning)" />}
                        {alert.type === 'success' && <CheckCircle2 size={14} color="var(--success)" />}
                      </div>
                      <p className="alert-card-msg">{alert.message}</p>
                      <div className="alert-card-action">
                        Investigate State &rarr;
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Diagnostic Report Panel */}
            <div className="card" style={{ padding: '1.5rem', background: '#ffffff', border: '1px solid #cbd5e1' }}>
              <h3 style={{ color: 'var(--accent)', marginBottom: '1rem', fontFamily: 'Outfit', fontWeight: 700, fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span>🔬</span> Live Diagnostic Brief
              </h3>
              <div style={{ maxHeight: '350px', overflowY: 'auto', paddingRight: '4px' }}>
                {(data?.ai_brief || '').split('\n').map((line, i) => (
                  <p key={i} style={{ marginBottom: '0.65rem', color: '#1e293b', lineHeight: 1.6, fontWeight: 500, fontSize: '0.85rem' }}>{line}</p>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div style={{ textAlign: 'center', marginTop: '4rem', padding: '2rem 0', color: 'var(--text-secondary)', borderTop: '1px solid #e2e8f0', fontWeight: 500 }}>
          PolicyPulse AI Engine | Powered by data.gov.in
        </div>
      </div>
    </div>

      {/* Floating PulseCopilot Button */}
      <div className="copilot-trigger" onClick={() => setIsChatOpen(!isChatOpen)}>
        <Brain size={28} />
      </div>

      {/* PulseCopilot Chat Window */}
      {isChatOpen && (
        <div className="copilot-chat-window">
          <div className="copilot-header">
            <div>
              <h4 style={{ color: '#ffffff' }}>
                <Sparkles size={16} color="#fbbf24" style={{ marginRight: '0.3rem' }} />
                PulseCopilot AI Advisor
              </h4>
              <p>Active Central Schemes Expert</p>
            </div>
            <button className="copilot-close" onClick={() => setIsChatOpen(false)}>
              <X size={18} />
            </button>
          </div>

          <div className="copilot-messages">
            {messages.map((msg, i) => (
              <div 
                key={i} 
                className={`message-bubble ${msg.sender}`} 
                style={{ 
                  position: 'relative', 
                  paddingRight: msg.sender === 'bot' ? '2.2rem' : '1rem' 
                }}
              >
                {renderMessageContent(msg.text)}
                {msg.sender === 'bot' && (
                  <button 
                    onClick={() => handleSpeak(msg.text, i)}
                    style={{ 
                      position: 'absolute', 
                      right: '0.5rem', 
                      top: '0.5rem', 
                      background: 'none', 
                      border: 'none', 
                      color: speakingIndex === i ? 'var(--accent)' : '#94a3b8', 
                      cursor: 'pointer',
                      padding: '0.2rem',
                      borderRadius: '4px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'color 0.2s ease'
                    }}
                    title={speakingIndex === i ? "Stop narration" : "Read aloud"}
                  >
                    {speakingIndex === i ? <VolumeX size={14} /> : <Volume2 size={14} />}
                  </button>
                )}
              </div>
            ))}
            {isTyping && (
              <div className="message-bubble bot" style={{ display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                <span className="loader" style={{ width: '12px', height: '12px', border: '2px solid #e2e8f0', borderTop: '2px solid var(--accent)' }}></span>
                <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Parsing data model...</span>
              </div>
            )}
            <div ref={messageEndRef} />
          </div>

          {/* Quick Suggestions Box */}
          <div className="copilot-suggestions">
            {getDynamicSuggestions().map((sug, idx) => (
              <button key={idx} className="suggestion-pill" onClick={() => handleSendMessage(null, sug)}>
                {sug}
              </button>
            ))}
          </div>

          <form className="copilot-input-area" onSubmit={handleSendMessage}>
            <input 
              type="text" 
              placeholder="Ask about schemes, budgets, states..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
            />
            <button type="submit" className="copilot-send">
              <Send size={16} />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default App;
