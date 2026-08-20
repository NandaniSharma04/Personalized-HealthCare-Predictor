import React, { useState } from 'react';
import { ALL_CLINICAL_SYMPTOMS } from '../constants/symptoms';

const CATEGORIES = {
  "Common": ["fever", "headache", "cough", "fatigue", "shortness of breath", "nausea", "dizziness", "chest pain"],
  "Respiratory": ["cough", "shortness of breath", "wheezing", "sore throat", "runny nose", "chest tightness", "nasal congestion", "coryza", "abnormal breathing sounds"],
  "Neurological": ["headache", "dizziness", "insomnia", "confusion", "numbness", "seizures", "anxiety and nervousness", "depression", "loss of sensation", "paresthesia"],
  "Digestive": ["nausea", "vomiting", "diarrhea", "abdominal pain", "loss of appetite", "indigestion", "constipation", "decreased appetite", "heartburn", "stomach bloating"],
  "Skin": ["skin rash", "itching", "redness", "skin lesion", "blisters", "skin peeling", "abnormal appearing skin", "acne or pimples", "skin growth", "skin moles", "diaper rash"],
  "Cardiovascular": ["chest pain", "sharp chest pain", "palpitations", "irregular heartbeat", "decreased heart rate", "increased heart rate", "peripheral edema", "swelling in legs"]
};

export default function SymptomSelector({ allSymptoms, selectedSymptoms, setSelectedSymptoms }) {
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');

  // Fallback to full 230 symptoms if allSymptoms prop is missing or empty
  const symptomsVocabulary = (allSymptoms && allSymptoms.length > 0) ? allSymptoms : ALL_CLINICAL_SYMPTOMS;

  const normalize = (str) => (str || '').toString().trim().toLowerCase();

  const isSelected = (sym) => {
    const target = normalize(sym);
    return selectedSymptoms.some(s => normalize(s) === target);
  };

  const toggleSymptom = (sym) => {
    if (isSelected(sym)) {
      const target = normalize(sym);
      setSelectedSymptoms(selectedSymptoms.filter(s => normalize(s) !== target));
    } else {
      setSelectedSymptoms([...selectedSymptoms, sym]);
    }
  };

  const clearAll = () => setSelectedSymptoms([]);

  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearch(val);
    if (val && activeCategory !== 'All') {
      setActiveCategory('All'); // Auto-switch to All when searching
    }
  };

  const filteredSymptoms = symptomsVocabulary.filter(sym => {
    const matchesSearch = normalize(sym).includes(normalize(search));
    if (!search && activeCategory !== 'All') {
      const catList = CATEGORIES[activeCategory] || [];
      return catList.some(c => normalize(sym).includes(normalize(c)));
    }
    return matchesSearch;
  });

  return (
    <div className="symptom-selector-container">
      <div className="selector-header">
        <div>
          <h3 className="selector-title">Select Present Symptoms</h3>
          <p className="selector-subtitle">Choose from {symptomsVocabulary.length} clinical symptom indicators</p>
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
          placeholder="Search symptoms (e.g. fever, headache, decreased heart rate)..."
          value={search}
          onChange={handleSearchChange}
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
          onClick={() => setActiveCategory('All')}
        >
          All Symptoms ({symptomsVocabulary.length})
        </button>
        {Object.keys(CATEGORIES).map(cat => (
          <button
            key={cat}
            type="button"
            className={`chip ${activeCategory === cat ? 'chip-active' : ''}`}
            onClick={() => {
              setActiveCategory(cat);
              setSearch(''); // Clear search when switching category
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      {selectedSymptoms.length > 0 && (
        <div className="selected-symptoms-tags">
          <span className="tags-label">Active Symptoms ({selectedSymptoms.length}):</span>
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
        {filteredSymptoms.length === 0 ? (
          <div style={{ gridColumn: "1 / -1", textAlign: "center", padding: "20px", color: "#94a3b8" }}>
            No symptoms match "{search}". Try searching for another term or click "All Symptoms".
          </div>
        ) : (
          filteredSymptoms.map(sym => {
            const active = isSelected(sym);
            return (
              <button
                key={sym}
                type="button"
                className={`symptom-card ${active ? 'symptom-card-selected' : ''}`}
                onClick={() => toggleSymptom(sym)}
                style={{
                  background: active ? 'rgba(59, 130, 246, 0.25)' : 'rgba(30, 41, 59, 0.6)',
                  border: active ? '1px solid #3b82f6' : '1px solid rgba(255, 255, 255, 0.08)'
                }}
              >
                <div className="checkbox-indicator">{active ? '✓' : ''}</div>
                <span className="symptom-name" style={{ color: active ? '#ffffff' : '#cbd5e1' }}>{sym}</span>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
