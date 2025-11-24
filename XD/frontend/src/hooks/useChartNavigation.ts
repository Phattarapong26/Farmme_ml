import { useState, useRef, useEffect } from 'react';

export const useChartNavigation = (dataLength: number, visibleMonths: number = 8) => {
  const [chartStartIndex, setChartStartIndex] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState(0);
  const [lastTouchX, setLastTouchX] = useState(0);
  const chartRef = useRef<HTMLDivElement>(null);

  // Smooth scrolling functions
  const updateChartIndex = (newIndex: number) => {
    const maxIndex = Math.max(0, dataLength - visibleMonths);
    const clampedIndex = Math.max(0, Math.min(maxIndex, newIndex));
    setChartStartIndex(clampedIndex);
  };

  // Mouse wheel handler
  const handleWheel = (e: WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 1 : -1;
    updateChartIndex(chartStartIndex + delta);
  };

  // Mouse drag handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setDragStart(e.clientX);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    const diff = e.clientX - dragStart;
    const threshold = 50; // pixels to drag before scrolling
    if (Math.abs(diff) > threshold) {
      const direction = diff > 0 ? -1 : 1;
      updateChartIndex(chartStartIndex + direction);
      setDragStart(e.clientX);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Touch handlers for mobile
  const handleTouchStart = (e: React.TouchEvent) => {
    setLastTouchX(e.touches[0].clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    const currentTouchX = e.touches[0].clientX;
    const diff = currentTouchX - lastTouchX;
    const threshold = 30;
    
    if (Math.abs(diff) > threshold) {
      const direction = diff > 0 ? -1 : 1;
      updateChartIndex(chartStartIndex + direction);
      setLastTouchX(currentTouchX);
    }
  };

  // Add event listeners
  useEffect(() => {
    const chartElement = chartRef.current;
    if (!chartElement) return;

    chartElement.addEventListener('wheel', handleWheel, { passive: false });
    
    return () => {
      chartElement.removeEventListener('wheel', handleWheel);
    };
  }, [chartStartIndex]);

  return {
    chartStartIndex,
    chartRef,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
    handleTouchStart,
    handleTouchMove,
  };
};
