import React, { useState, useEffect } from 'react';

const CATEGORIES = {
  "Common": ["fever", "headache", "cough", "fatigue", "shortness of breath", "nausea", "dizziness", "chest pain"],
  "Respiratory": ["cough", "shortness of breath", "wheezing", "sore throat", "runny nose", "chest tightness", "nasal congestion"],
  "Neurological": ["headache", "dizziness", "insomnia", "confusion", "numbness", "seizures", "anxiety and nervousness"],
  "Digestive": ["nausea", "vomiting", "diarrhea", "abdominal pain", "loss of appetite", "indigestion", "constipation"],
  "Skin": ["skin rash", "itching", "redness", "skin lesion", "blisters", "skin peeling", "abnormal appearing skin"],
  "Cardiovascular": ["chest pain", "sharp chest pain", "palpitations", "irregular heartbeat", "high blood pressure", "swelling in legs"]
};

export default function SymptomSelector({ allSymptoms, selectedSymptoms, setSelectedSymptoms }) {
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');

  const normalizedSelected = new Set(selectedSymptoms.map(s => s.toLowerCase().strip ? s.toLowerCase().strip() : s.toLowerCase()));

  const filteredSymptoms = allSymptoms.filter(sym => {
    const matchesSearch = sym.toLowerCase().includes(search.toLowerCase());
    if (activeCategory === 'All') return matchesSearch;
    const catList = CATEGORIES[activeCategory] || [];
    return matchesSearch && catList.some(c => sym.toLowerCase().includes(c));
  });

  const toggleSymptom = (sym) => {
    if (selectedSymptoms.includes(sym)) {
      setSelectedSymptoms(selectedSymptoms.filter(s => s !== sym));
    } else {
      setSelectedSymptoms([...selectedSymptoms, sym]);
    }
  };

  const clearAll = () => setSelectedSymptoms([]);

  const selectCategory = (catName) => {
    setActiveCategory(catName);
  };

  return (
    <div className="symptom-selector-container">
      <div className="selector-header">
        <div>
          <h3 className="selector-title">Select Present Symptoms</h3>
          <p className="selector-subtitle">Choose from {allSymptoms.length} clinical symptom indicators</p>
        </div>
        <div className="selector-actions">
          <span className="selected-badge">{selectedSymptoms.length} Selected</span>
          {selectedSymptoms.length > 0 && (
            <button type="button" onClick={clearAll} className="btn-secondary btn-sm">
              Clear All
            </button>
          )}
        </div>
      </div>

      <div className="search-bar-wrapper">
        <input
          type="text"
          placeholder="Search symptoms (e.g. fever, headache, chest pain)..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="search-input"
        />
        {search && (
          <button type="button" className="search-clear-btn" onClick={() => setSearch('')}>
            &times;
          </button>
        )}
      </div>

      <div className="category-chips">
        <button
          type="button"
          className={`chip ${activeCategory === 'All' ? 'chip-active' : ''}`}
          onClick={() => selectCategory('All')}
        >
          All Symptoms
        </button>
        {Object.keys(CATEGORIES).map(cat => (
          <button
            key={cat}
            type="button"
            className={`chip ${activeCategory === cat ? 'chip-active' : ''}`}
            onClick={() => selectCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      {selectedSymptoms.length > 0 && (
        <div className="selected-symptoms-tags">
          <span className="tags-label">Active Symptoms:</span>
          <div className="tags-flex">
            {selectedSymptoms.map(sym => (
              <span key={sym} className="symptom-tag">
                {sym}
                <button type="button" onClick={() => toggleSymptom(sym)} className="tag-remove">&times;</button>
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="symptoms-grid">
        {filteredSymptoms.slice(0, 80).map(sym => {
          const isSelected = selectedSymptoms.includes(sym);
          return (
            <button
              key={sym}
              type="button"
              className={`symptom-card ${isSelected ? 'symptom-card-selected' : ''}`}
              onClick={() => toggleSymptom(sym)}
            >
              <div className="checkbox-indicator">{isSelected ? '✓' : ''}</div>
              <span className="symptom-name">{sym}</span>
            </button>
          );
        })}
      </div>
      {filteredSymptoms.length > 80 && (
        <p className="grid-more-notice">Showing top 80 matches. Type in search bar to refine list.</p>
      )}
    </div>
  );
}
