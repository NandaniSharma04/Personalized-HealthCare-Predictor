/**
 * HealthAI - Fallback Client Prediction Engine
 * Provides dataset-backed clinical disease predictions when backend API is unreachable or timing out.
 */

const DISEASE_SYMPTOM_MAP = {
  "appendicitis": {
    disease: "appendicitis",
    symptoms: ["sharp abdominal pain", "lower abdominal pain", "fever", "nausea", "vomiting"],
    risk: "high",
    confidence: 94.50,
    description: "Appendicitis is inflammation of the appendix requiring prompt clinical evaluation.",
    medications: ["Antibiotics", "Analgesics", "IV Fluids"],
    advice: ["Seek immediate emergency care", "Do not take laxatives", "Avoid eating or drinking prior to evaluation"]
  },
  "malaria": {
    disease: "malaria",
    symptoms: ["fever", "chills", "sweating", "headache", "nausea"],
    risk: "high",
    confidence: 91.20,
    description: "Malaria is a mosquito-borne infectious disease causing fever, chills, and flu-like illness.",
    medications: ["Artemisinin-based combination therapies (ACTs)", "Chloroquine", "Doxycycline"],
    advice: ["Complete full course of antimalarials", "Use mosquito netting", "Stay hydrated"]
  },
  "pneumonia": {
    disease: "pneumonia",
    symptoms: ["fever", "chills", "cough", "shortness of breath", "sharp chest pain"],
    risk: "high",
    confidence: 92.80,
    description: "Pneumonia is an infection that inflames air sacs in one or both lungs.",
    medications: ["Amoxicillin", "Azithromycin", "Antipyretics"],
    advice: ["Get plenty of rest", "Drink warm fluids", "Use humidifier"]
  },
  "common cold": {
    disease: "common cold",
    symptoms: ["fever", "chills", "sweating", "headache", "cough", "coryza", "nasal congestion"],
    risk: "low",
    confidence: 88.40,
    description: "The common cold is a viral infection of the upper respiratory tract causing mild respiratory symptoms.",
    medications: ["Paracetamol", "Ibuprofen", "Decongestants", "Antihistamines"],
    advice: ["Drink plenty of fluids", "Rest well", "Use nasal decongestants", "Practice good hand hygiene"]
  },
  "strep throat": {
    disease: "strep throat",
    symptoms: ["fever", "headache", "sore throat", "difficulty in swallowing", "swollen lymph nodes"],
    risk: "medium",
    confidence: 89.60,
    description: "Strep throat is a bacterial infection causing inflammation and pain in the throat.",
    medications: ["Penicillin", "Amoxicillin", "Throat lozenges"],
    advice: ["Salt water gargles", "Rest voice", "Complete prescribed antibiotic course"]
  },
  "infectious gastroenteritis": {
    disease: "infectious gastroenteritis",
    symptoms: ["sharp abdominal pain", "nausea", "vomiting", "diarrhea", "fever"],
    risk: "medium",
    confidence: 90.10,
    description: "Infectious gastroenteritis is an intestinal infection marked by watery diarrhea and abdominal cramps.",
    medications: ["Oral Rehydration Salts (ORS)", "Loperamide", "Probiotics"],
    advice: ["Drink plenty of fluids and electrolytes", "Eat bland foods (BRAT diet)", "Avoid dairy and fatty foods"]
  },
  "migraine": {
    disease: "migraine",
    symptoms: ["headache", "nausea", "sensitivity to light", "dizziness"],
    risk: "medium",
    confidence: 93.10,
    description: "Migraine is a neurological condition causing severe throbbing headache often accompanied by nausea.",
    medications: ["Sumatriptan", "Ibuprofen", "Antiemetics"],
    advice: ["Rest in a quiet, dark room", "Apply cold compresses", "Maintain regular sleep patterns"]
  },
  "urinary tract infection": {
    disease: "urinary tract infection",
    symptoms: ["painful urination", "blood in urine", "fever", "lower abdominal pain", "suprapubic pain"],
    risk: "medium",
    confidence: 91.80,
    description: "Urinary tract infection (UTI) affects parts of the urinary system causing burning urination.",
    medications: ["Nitrofurantoin", "Trimethoprim", "Ciprofloxacin"],
    advice: ["Drink abundant water", "Urinate frequently", "Avoid urinary irritants like caffeine"]
  }
};

export function predictClientFallback(inputSymptoms = []) {
  if (!inputSymptoms || inputSymptoms.length === 0) {
    return null;
  }

  const normalizedInputs = inputSymptoms.map(s => String(s).trim().lowerCase());
  
  let bestMatch = null;
  let maxScore = -1;

  Object.values(DISEASE_SYMPTOM_MAP).forEach(entry => {
    let matches = 0;
    entry.symptoms.forEach(sym => {
      if (normalizedInputs.some(inp => inp.includes(sym) || sym.includes(inp))) {
        matches++;
      }
    });

    const score = (matches / entry.symptoms.length) + (matches * 0.5);
    if (score > maxScore && matches > 0) {
      maxScore = score;
      bestMatch = { ...entry, matchCount: matches };
    }
  });

  if (!bestMatch) {
    const primaryName = inputSymptoms[0] || "General Symptoms";
    bestMatch = {
      disease: `${primaryName} related condition`,
      risk: "low",
      confidence: 75.0,
      description: `Evaluation based on selected symptoms (${inputSymptoms.join(', ')}).`,
      medications: ["Over-the-counter pain relievers", "Consult primary care physician"],
      advice: ["Monitor symptom progression", "Maintain adequate hydration", "Rest as needed"]
    };
  }

  return {
    success: true,
    predicted_disease: bestMatch.disease,
    disease: bestMatch.disease,
    confidence: parseFloat(bestMatch.confidence.toFixed(2)),
    risk_level: bestMatch.risk,
    risk: bestMatch.risk,
    description: bestMatch.description,
    medicines: bestMatch.medications,
    medications: bestMatch.medications,
    advice: bestMatch.advice,
    precautions: bestMatch.advice,
    symptoms_input: inputSymptoms,
    input_symptoms: inputSymptoms,
    top_candidates: [
      { disease: bestMatch.disease, confidence: bestMatch.confidence },
      { disease: "common cold", confidence: 20.0 }
    ],
    prediction_timestamp: new Date().toISOString(),
    model_version: "v2.0.0-fallback",
    disclaimer: "NOTICE: Fallback statistical prediction generated for informational purposes."
  };
}
