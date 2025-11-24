/**
 * Reset intro flag - useful for testing
 * Call this in browser console: window.resetIntro()
 */
export const resetIntro = () => {
  localStorage.removeItem('hasSeenIntro');
  window.location.href = '/intro';
};

// Make it available globally for testing
if (typeof window !== 'undefined') {
  (window as any).resetIntro = resetIntro;
}
