/**
 * Utility Formatters for Health Care AI Data
 */
export const formatPercentage = (value, decimals = 1) => {
  if (value === undefined || value === null) return '0%';
  const num = parseFloat(value);
  return `${num.toFixed(decimals)}%`;
};

export const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return dateStr;
  }
};

export const getRiskColorClass = (riskLevel) => {
  switch (riskLevel?.toLowerCase()) {
    case 'high': return 'risk-high';
    case 'medium': return 'risk-medium';
    case 'low': return 'risk-low';
    default: return 'risk-unknown';
  }
};
