import { useEffect, useMemo, useRef, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { cropColors, cropIcon, provinceDominantCrop, UI_CONSTANTS } from '@/constants/crops';
import { formatTons, deterministicAmount } from '@/utils/format';
import type { CropKey, HoverInfo, ProvinceData } from '@/types/map';
import { Brain, Calendar, Zap, X, Loader2 } from 'lucide-react';
import { useProvinceContext } from '@/hooks/useProvinceContext';
import { useCropData } from '@/hooks/useCropData';
import { useProvinceByName, useAllProvinces } from '@/hooks/useProvinceData';
import { useDominantCrops, mapCropTypeToKey } from '@/hooks/useDominantCrops';
import { useProvinceInfo } from '@/hooks/useProvinceInfo';
import { WeatherSection } from './ProvinceInfo/WeatherSection';
import { CultivationSection } from './ProvinceInfo/CultivationSection';
import { PricesSection } from './ProvinceInfo/PricesSection';
import { EconomicSection } from './ProvinceInfo/EconomicSection';

// Removed hardcoded province data - now fetched from API

const ThailandMap = () => {
  const { selectedProvince, setSelectedProvince } = useProvinceContext();
  const [selectedProvinceThai, setSelectedProvinceThai] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const { data: cropData } = useCropData(selectedProvinceThai || undefined);
  const [hoverInfo, setHoverInfo] = useState<HoverInfo>({ show: false, x: 0, y: 0, provinceThai: '', cropKey: 'mixed', amountTons: 0 });

  // Debug: Log selected province
  useEffect(() => {
    console.log('🗺️ Selected Province Thai:', selectedProvinceThai);
    console.log('🗺️ Selected Province ID:', selectedProvince);
  }, [selectedProvinceThai, selectedProvince]);

  // Fetch real province data from API
  const { data: allProvincesData } = useAllProvinces();
  const { data: selectedProvinceData } = useProvinceByName(selectedProvinceThai);
  const { data: dominantCropsData } = useDominantCrops();

  // Fetch comprehensive province information
  const {
    data: provinceInfo,
    isLoading: isLoadingProvinceInfo,
    isError: isErrorProvinceInfo,
    refetch: refetchProvinceInfo
  } = useProvinceInfo(selectedProvinceThai);

  // AI Analysis states
  const [showContextMenu, setShowContextMenu] = useState(false);
  const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });
  const [quickAnalysisMode, setQuickAnalysisMode] = useState(false);
  const [aiPopupVisible, setAiPopupVisible] = useState(false);
  const [aiMessage, setAiMessage] = useState('');
  const [customPlantingDate, setCustomPlantingDate] = useState<number | null>(null);
  const [isZoomedIn, setIsZoomedIn] = useState(false);
  const [zoomedProvince, setZoomedProvince] = useState<string | null>(null);
  const [isRightClickMode, setIsRightClickMode] = useState(false);
  // SVG transform string applied to inner <g> for accurate pan/zoom
  const [zoomTransformStr, setZoomTransformStr] = useState<string>('');
  // Keep current zoom params for animation
  const zoomParamsRef = useRef<{ cx: number; cy: number; scale: number }>({ cx: 300, cy: 350, scale: 1 });
  const zoomAnimRef = useRef<number | null>(null);
  const zoomLayerRef = useRef<SVGGElement | null>(null);

  // rAF-throttling for tooltip mouse move
  const hoverRafRef = useRef<number | null>(null);
  const latestHoverRef = useRef<{ x: number; y: number } | null>(null);

  // Close panels and zoom out when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      // Don't reset if clicking on popup or context menu
      if (containerRef.current && !containerRef.current.contains(event.target as Node) &&
        !aiPopupVisible && !showContextMenu) {
        resetMapView();
      }
    };

    // Add event listener when component mounts
    document.addEventListener('mousedown', handleClickOutside);

    // Clean up event listener when component unmounts
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [aiPopupVisible, showContextMenu]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [parsedProvinces, setParsedProvinces] = useState<Array<{ thaiName: string; paths: string[]; transform?: string }>>([]);
  const [svgViewBox, setSvgViewBox] = useState<string | null>(null);

  // Fallback dominant crop map (used when API data is not available)
  const fallbackCropMap: Record<string, CropKey> = {
    'กรุงเทพมหานคร': 'mixed', 'พระนครศรีอยุธยา': 'rice', 'อ่างทอง': 'rice',
    'สิงห์บุรี': 'rice', 'ลพบุรี': 'sugarcane', 'สระบุรี': 'sugarcane',
    'ปทุมธานี': 'rice', 'นนทบุรี': 'mixed', 'นครปฐม': 'rice',
    'สมุทรสาคร': 'mixed', 'สมุทรปราการ': 'mixed', 'สมุทรสงคราม': 'mixed',
    'ราชบุรี': 'sugarcane', 'กาญจนบุรี': 'sugarcane', 'สุพรรณบุรี': 'rice',
    'เพชรบุรี': 'mixed', 'ประจวบคีรีขันธ์': 'mixed', 'นครสวรรค์': 'rice',
    'อุทัยธานี': 'rice', 'ชัยนาท': 'rice', 'กำแพงเพชร': 'cassava',
    'พิษณุโลก': 'rice', 'พิจิตร': 'rice', 'สุโขทัย': 'rice', 'ตาก': 'mixed',
    'เพชรบูรณ์': 'corn', 'อุตรดิตถ์': 'rice', 'แพร่': 'rice', 'น่าน': 'rice',
    'พะเยา': 'rice', 'เชียงราย': 'rice', 'เชียงใหม่': 'rice', 'ลำปาง': 'corn',
    'ลำพูน': 'corn', 'แม่ฮ่องสอน': 'mixed', 'เลย': 'corn', 'นครราชสีมา': 'cassava',
    'บุรีรัมย์': 'cassava', 'สุรินทร์': 'cassava', 'ศรีสะเกษ': 'cassava',
    'อุบลราชธานี': 'cassava', 'ยโสธร': 'rice', 'ร้อยเอ็ด': 'rice',
    'มหาสารคาม': 'rice', 'ขอนแก่น': 'cassava', 'ชัยภูมิ': 'cassava',
    'กาฬสินธุ์': 'rice', 'สกลนคร': 'rice', 'นครพนม': 'rice', 'มุกดาหาร': 'cassava',
    'บึงกาฬ': 'cassava', 'หนองบัวลำภู': 'cassava', 'หนองคาย': 'rice',
    'อุดรธานี': 'cassava', 'อำนาจเจริญ': 'rice', 'ชลบุรี': 'mixed',
    'ระยอง': 'mixed', 'จันทบุรี': 'mixed', 'ตราด': 'mixed', 'ฉะเชิงเทรา': 'rice',
    'ปราจีนบุรี': 'cassava', 'สระแก้ว': 'cassava', 'ชุมพร': 'rubber',
    'ระนอง': 'rubber', 'สุราษฎร์ธานี': 'rubber', 'นครศรีธรรมราช': 'rubber',
    'พัทลุง': 'rubber', 'สงขลา': 'rubber', 'สตูล': 'rubber', 'ตรัง': 'rubber',
    'กระบี่': 'rubber', 'พังงา': 'rubber', 'ภูเก็ต': 'mixed', 'ยะลา': 'rubber',
    'นราธิวาส': 'rubber', 'ปัตตานี': 'rubber', 'อยุธยา': 'rice'
  };

  // Get dominant crop for a province from API data with fallback
  const getDominantCropKey = (provinceName: string): CropKey => {
    // Try API data first
    if (dominantCropsData?.provinces) {
      const cropInfo = dominantCropsData.provinces[provinceName];
      if (cropInfo) {
        const mappedKey = mapCropTypeToKey(cropInfo.crop_type, cropInfo.crop_category);
        // Only use API data if it's a main agricultural crop (not 'mixed')
        // This ensures vegetables don't override our regional crop data
        if (mappedKey !== 'mixed') {
          return mappedKey;
        }
      }
    }

    // Fallback to hardcoded map (covers all 77 provinces with proper regional crops)
    return fallbackCropMap[provinceName] || 'mixed';
  };

  // Create a map of province data by Thai name
  const provinceDataMap = useMemo(() => {
    if (!allProvincesData) return new Map();
    return new Map(allProvincesData.map(p => [p.name, p]));
  }, [allProvincesData]);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch('/UI_Home.html', { cache: 'no-store' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const html = await res.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const svg = doc.querySelector('#viz-main');
        const mapRoot = svg?.querySelector('#viz-map');
        if (!svg || !mapRoot) throw new Error('SVG structure not found');
        if (cancelled) return;
        const groups = Array.from(mapRoot.querySelectorAll(':scope > g[id]')) as SVGGElement[];
        const extracted = groups.map((g) => {
          const thaiName = g.id;
          const transform = g.getAttribute('transform') || undefined;
          const paths = Array.from(g.querySelectorAll('path'))
            .filter((p) => {
              const pid = (p as SVGPathElement).id || '';
              return !(pid.includes('.border') || pid.includes('.name'));
            })
            .map((p) => (p as SVGPathElement).getAttribute('d') || '')
            .filter(Boolean);
          return { thaiName, paths, transform };
        }).filter((item) => item.paths.length > 0);
        setParsedProvinces(extracted);
        const vb = svg.getAttribute('viewBox') ?? null;
        if (vb) setSvgViewBox(vb);
      } catch (err: any) {
        if (cancelled) return;
        setError(err?.message || 'โหลดแผนที่ไม่สำเร็จ');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const getProvinceInfo = (provinceId: string) => {
    // Find province by ID from API data
    return allProvincesData?.find(p => p.id === provinceId);
  };

  // Calculate province center for smart zoom
  const calculateProvinceCenter = (provinceName: string) => {
    const provinceElement = document.getElementById(provinceName) as unknown as SVGGraphicsElement;
    if (!provinceElement || !provinceElement.getBBox) return { x: 0, y: 0 };

    const bbox = provinceElement.getBBox();
    const centerX = bbox.x + bbox.width / 2;
    const centerY = bbox.y + bbox.height / 2;

    return { x: centerX, y: centerY };
  };

  const zoomToProvince = (provinceName: string) => {
    // Wait for next frame to ensure DOM is ready
    setTimeout(() => {
      const provinceElement = document.getElementById(provinceName) as unknown as SVGGraphicsElement;
      if (!provinceElement || !provinceElement.getBBox) return;

      // Determine viewBox (fallback to 600x700)
      const [vbX, vbY, vbW, vbH] = (svgViewBox ?? '0 0 600 700').split(' ').map(Number);
      const viewportW = vbW || 600;
      const viewportH = vbH || 700;

      const bbox = provinceElement.getBBox();
      const cx = bbox.x + bbox.width / 2;
      const cy = bbox.y + bbox.height / 2;

      // Compute dynamic scale so province roughly fills ~60% of viewport
      const desiredFill = 0.6; // 60% of viewport
      const scaleX = (viewportW * desiredFill) / bbox.width;
      const scaleY = (viewportH * desiredFill) / bbox.height;
      let scale = Math.min(scaleX, scaleY);
      // Clamp scale to reasonable range
      scale = Math.max(1.8, Math.min(scale, 5));

      // Animate to target params
      const start = { ...zoomParamsRef.current };
      const end = { cx, cy, scale };
      const duration = 550; // ms
      const startTime = performance.now();

      const easeInOutQuad = (t: number) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t);

      const step = (now: number) => {
        const t = Math.min(1, (now - startTime) / duration);
        const e = easeInOutQuad(t);
        const curCx = start.cx + (end.cx - start.cx) * e;
        const curCy = start.cy + (end.cy - start.cy) * e;
        const curScale = start.scale + (end.scale - start.scale) * e;
        zoomParamsRef.current = { cx: curCx, cy: curCy, scale: curScale };
        const transform = `translate(${viewportW / 2}, ${viewportH / 2}) scale(${curScale}) translate(${-curCx}, ${-curCy})`;
        // Imperatively update transform to avoid React re-render on each frame
        if (zoomLayerRef.current) {
          zoomLayerRef.current.setAttribute('transform', transform);
        }
        if (t < 1) {
          zoomAnimRef.current = requestAnimationFrame(step);
        } else {
          zoomAnimRef.current = null;
          // Save final state
          setZoomTransformStr(transform);
        }
      };

      if (zoomAnimRef.current) cancelAnimationFrame(zoomAnimRef.current);
      zoomAnimRef.current = requestAnimationFrame(step);
      setIsZoomedIn(true);
      setZoomedProvince(provinceName);
    }, 10);
  };

  // AI Analysis functions
  const handleMapRightClick = (event: React.MouseEvent, provinceName: string) => {
    event.preventDefault();
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;

    // Set context menu position relative to container
    setContextMenuPosition({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    });
    setShowContextMenu(true);

    // Smart zoom to province but don't show side panels yet
    zoomToProvince(provinceName);
    setIsRightClickMode(true);
    setSelectedProvinceThai(provinceName);
    const mapped = provinceDataMap.get(provinceName);
    setSelectedProvince(mapped?.id ?? null);
  };

  const handleQuickAnalysis = async () => {
    if (!selectedProvinceThai) {
      setAiMessage("⚠️ กรุณาเลือกจังหวัดก่อนค่ะ");
      setAiPopupVisible(true);
      setTimeout(() => setAiPopupVisible(false), 2000);
      return;
    }

    setQuickAnalysisMode(true);
    setShowContextMenu(false);
    setAiPopupVisible(true);
    setAiMessage("🗺️ กำลังวิเคราะห์ข้อมูลจังหวัด...");

    try {
      // Call real AI analysis API
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      console.log('🔗 API Base URL:', API_BASE_URL);
      console.log('🗺️ Analyzing province:', selectedProvinceThai);

      setAiMessage("🌾 กำลังรวบรวมข้อมูลพืช ราคา และสภาพอากาศ...");

      const response = await fetch(`${API_BASE_URL}/api/v2/province-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          province: selectedProvinceThai
        })
      });

      console.log('📡 Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Response error:', errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Response data:', data);

      if (data.success) {
        setAiMessage(data.ai_analysis);
        setQuickAnalysisMode(false);
      } else {
        throw new Error('Analysis failed');
      }

    } catch (error) {
      console.error('❌ Error calling AI analysis:', error);
      console.error('Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        province: selectedProvinceThai,
        timestamp: new Date().toISOString()
      });
      setAiMessage(`❌ ขออภัยค่ะ เกิดข้อผิดพลาดในการวิเคราะห์ข้อมูล\n\nข้อผิดพลาด: ${error instanceof Error ? error.message : 'ไม่ทราบสาเหตุ'}\n\nกรุณาลองใหม่อีกครั้งหรือเลือกจังหวัดอื่น`);
      setQuickAnalysisMode(false);
    }
  };

  const closeAiPopup = () => {
    setAiPopupVisible(false);
    setQuickAnalysisMode(false);
    setIsRightClickMode(false);
  };

  const resetMapView = () => {
    // Smoothly animate back to identity
    const [vbX, vbY, vbW, vbH] = (svgViewBox ?? '0 0 600 700').split(' ').map(Number);
    const viewportW = vbW || 600;
    const viewportH = vbH || 700;
    const start = { ...zoomParamsRef.current };
    const end = { cx: viewportW / 2, cy: viewportH / 2, scale: 1 };
    const duration = 400;
    const startTime = performance.now();
    const easeInOutQuad = (t: number) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t);
    const step = (now: number) => {
      const t = Math.min(1, (now - startTime) / duration);
      const e = easeInOutQuad(t);
      const curCx = start.cx + (end.cx - start.cx) * e;
      const curCy = start.cy + (end.cy - start.cy) * e;
      const curScale = start.scale + (end.scale - start.scale) * e;
      zoomParamsRef.current = { cx: curCx, cy: curCy, scale: curScale };
      const transform = `translate(${viewportW / 2}, ${viewportH / 2}) scale(${curScale}) translate(${-curCx}, ${-curCy})`;
      if (zoomLayerRef.current) {
        zoomLayerRef.current.setAttribute('transform', transform);
      }
      if (t < 1) {
        zoomAnimRef.current = requestAnimationFrame(step);
      } else {
        zoomAnimRef.current = null;
        // Finalize state
        setZoomTransformStr(curScale === 1 && Math.abs(curCx - viewportW / 2) < 0.5 && Math.abs(curCy - viewportH / 2) < 0.5 ? '' : transform);
      }
    };
    if (zoomAnimRef.current) cancelAnimationFrame(zoomAnimRef.current);
    zoomAnimRef.current = requestAnimationFrame(step);

    setIsZoomedIn(false);
    setZoomedProvince(null);
    setSelectedProvince(null);
    setSelectedProvinceThai(null);
    setShowContextMenu(false);
    setAiPopupVisible(false);
    setIsRightClickMode(false);
    setQuickAnalysisMode(false);
    setAiMessage('');
    // keep transformStr managed by animation above
  };

  return (
    <div className="min-h-screen bg-white ">
      <div className="container mx-auto p-4">
        {/* Desktop Layout */}
        <div className="hidden lg:block relative min-h-[800px] border-0 ring-0 outline-none">
          {/* Background Map Layer */}
          <div className="absolute inset-0 z-0">
            <Card className="h-full w-full bg-card/95 backdrop-blur-sm border-0 shadow-none">
              <CardContent className="p-6 h-full">
                <div
                  className="relative w-full h-full bg-white overflow-visible"
                  ref={containerRef}
                  onClick={(e) => e.stopPropagation()} // Prevent click from reaching document
                >
                  {/* Loading / Error states */}
                  {loading && (
                    <div className="absolute inset-0 grid place-items-center" role="status" aria-live="polite">
                      <div className="text-sm text-muted-foreground">กำลังโหลดแผนที่…</div>
                    </div>
                  )}
                  {!loading && error && (
                    <div className="absolute inset-0 grid place-items-center" role="alert">
                      <div className="text-sm text-destructive">โหลดแผนที่ไม่สำเร็จ: {error}</div>
                    </div>
                  )}


                  {/* Accessible, React-rendered interactive layer (fallback without injecting raw DOM) */}
                  <svg
                    className="w-full h-full"
                    viewBox={svgViewBox ?? '0 0 600 700'}
                    role="img"
                    aria-label="แผนที่ประเทศไทย"
                  >
                    {/* Zoom/Pan layer */}
                    <g
                      id="zoom-layer"
                      ref={zoomLayerRef}
                      transform={zoomTransformStr || undefined}
                    >
                      {parsedProvinces.map(({ thaiName, paths, transform }) => {
                        const cropKey: CropKey = getDominantCropKey(thaiName);
                        const fillColor = cropColors[cropKey];
                        const isSelected = selectedProvinceThai === thaiName;
                        const opacity = isSelected || !selectedProvinceThai ? 1 : UI_CONSTANTS.dimOpacity;
                        const mapped = provinceDataMap.get(thaiName);
                        return (
                          <g
                            key={thaiName}
                            id={thaiName}
                            tabIndex={0}
                            role="button"
                            aria-label={`จังหวัด ${thaiName}`}
                            className="outline-none focus:ring-2 focus:ring-primary cursor-pointer"
                            transform={transform}
                            onClick={() => {
                              setSelectedProvinceThai(thaiName);
                              setSelectedProvince(mapped?.id ?? null);
                              // Smart zoom to province on left-click
                              zoomToProvince(thaiName);
                              setIsRightClickMode(false); // Enable side panels for left-click
                            }}
                            onContextMenu={(e) => handleMapRightClick(e, thaiName)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                setSelectedProvinceThai(thaiName);
                                setSelectedProvince(mapped?.id ?? null);
                                // Smart zoom to province on keyboard selection
                                zoomToProvince(thaiName);
                                setIsRightClickMode(false); // Enable side panels
                              }
                            }}
                            onMouseEnter={(e) => {
                              const rect = containerRef.current?.getBoundingClientRect();
                              if (!rect) return;
                              const amount = deterministicAmount(thaiName, cropKey);
                              setHoverInfo({
                                show: true,
                                x: e.clientX - rect.left + UI_CONSTANTS.tooltipOffset.x,
                                y: e.clientY - rect.top + UI_CONSTANTS.tooltipOffset.y,
                                provinceThai: thaiName,
                                cropKey,
                                amountTons: amount,
                              });
                            }}
                            onMouseMove={(e) => {
                              const rect = containerRef.current?.getBoundingClientRect();
                              if (!rect) return;
                              latestHoverRef.current = {
                                x: e.clientX - rect.left + UI_CONSTANTS.tooltipOffset.x,
                                y: e.clientY - rect.top + UI_CONSTANTS.tooltipOffset.y,
                              };
                              if (hoverRafRef.current == null) {
                                hoverRafRef.current = requestAnimationFrame(() => {
                                  hoverRafRef.current = null;
                                  if (latestHoverRef.current) {
                                    const { x, y } = latestHoverRef.current;
                                    setHoverInfo((prev) => ({ ...prev, show: true, x, y }));
                                  }
                                });
                              }
                            }}
                            onMouseLeave={() => setHoverInfo((prev) => ({ ...prev, show: false }))}
                            style={{
                              transform: isSelected ? `translateY(${UI_CONSTANTS.selected.translateY}px) scale(${UI_CONSTANTS.selected.scale})` : undefined,
                              filter: isSelected ? `drop-shadow(${UI_CONSTANTS.selected.shadow})` : undefined,
                              transition: 'transform 200ms ease, filter 200ms ease',
                              opacity,
                            }}
                          >
                            {paths.map((d, idx) => (
                              <path key={idx} d={d} fill={fillColor} />
                            ))}
                          </g>
                        );
                      })}
                    </g>
                  </svg>

                  {hoverInfo.show && (
                    <div
                      className="absolute z-50 pointer-events-none select-none rounded-md border bg-background/95 p-2 shadow-lg backdrop-blur supports-[backdrop-filter]:bg-background/60"
                      style={{ left: hoverInfo.x, top: hoverInfo.y, transform: 'translate(-50%, -115%)', minWidth: 180 }}
                      role="tooltip"
                    >
                      <div className="flex items-center gap-2">
                        {(() => {
                          const Icon = cropIcon[hoverInfo.cropKey];
                          return <Icon className="h-5 w-5 text-foreground/80" />;
                        })()}
                        <div className="text-sm font-medium">{hoverInfo.provinceThai}</div>
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground">
                        พืชเด่น: <span className="font-medium text-foreground">{hoverInfo.cropKey}</span>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        ปริมาณโดยประมาณ: <span className="font-medium text-foreground">{formatTons(hoverInfo.amountTons)} ตัน</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* AI Analysis Popup */}
                {aiPopupVisible && (
                  <div
                    className="absolute inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50"
                    onClick={closeAiPopup}
                  >
                    <div
                      className="bg-white rounded-xl shadow-2xl p-6 max-w-2xl w-full mx-4 max-h-[85vh] overflow-y-auto border border-purple-200"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2 ">
                          <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
                            <Brain className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h3 className="font-bold text-lg text-gray-800">AI Province Analysis</h3>
                            <p className="text-xs text-gray-500">ระบบวิเคราะห์จังหวัด - {selectedProvinceThai}</p>
                          </div>
                        </div>
                        <button
                          onClick={closeAiPopup}
                          className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"
                        >
                          <X className="w-4 h-4 text-gray-500" />
                        </button>
                      </div>

                      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 mb-4">
                        <div className="flex items-start gap-2">
                          {quickAnalysisMode && (
                            <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 animate-bounce"></div>
                          )}
                          <div className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap w-full">
                            {aiMessage}
                          </div>
                        </div>
                      </div>

                      {quickAnalysisMode && (
                        <div className="flex justify-center mb-4">
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                            <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          </div>
                        </div>
                      )}

                      {!quickAnalysisMode && (
                        <div className="flex justify-end">
                          <button
                            onClick={closeAiPopup}
                            className="px-4 py-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg hover:from-purple-600 hover:to-blue-600 transition-all text-sm font-medium"
                          >
                            ปิด
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Right-click Context Menu */}
                {showContextMenu && (
                  <div
                    className="absolute z-50 bg-white border border-gray-200 rounded-lg shadow-lg py-2 min-w-48"
                    style={{
                      left: contextMenuPosition.x + 10,
                      top: contextMenuPosition.y + 10,
                    }}
                    onMouseLeave={() => setShowContextMenu(false)}
                  >
                    <div className="px-4 py-2 text-sm font-medium text-gray-700 border-b border-gray-100">
                      🗺️ การวิเคราะห์จังหวัด
                    </div>
                    <button
                      onClick={handleQuickAnalysis}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-purple-50 hover:text-purple-700 flex items-center gap-2"
                    >
                      <Zap className="w-4 h-4" />
                      วิเคราะห์จังหวัดด้วย AI
                    </button>
                    <button
                      onClick={() => {
                        setShowContextMenu(false);
                        // Add custom planting date functionality for provinces
                        setCustomPlantingDate(8); // September (current month)
                      }}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-blue-50 hover:text-blue-700 flex items-center gap-2"
                    >
                      <Calendar className="w-4 h-4" />
                      ตั้งค่าฤดูปลูก
                    </button>
                    <div className="border-t border-gray-100 mt-1 pt-1">
                      <div className="px-4 py-1 text-xs text-gray-500">
                        คลิกขวาที่จังหวัดเพื่อเข้าถึงเครื่องมือ
                      </div>
                    </div>
                  </div>
                )}

                {/* Click outside to close context menu and popup */}
                {(showContextMenu || aiPopupVisible) && (
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => {
                      if (showContextMenu) {
                        setShowContextMenu(false);
                      }
                      if (aiPopupVisible && !quickAnalysisMode) {
                        setAiPopupVisible(false);
                        setIsRightClickMode(false);
                      }
                    }}
                  />
                )}
              </CardContent>
            </Card>
          </div>
          {/* Balanced Two-Column Layout - Only show when a province is selected and not in right-click mode */}
          {(selectedProvince || selectedProvinceThai) && !isRightClickMode && (
            <div className="relative z-10 pointer-events-none h-full">
              {/* Left Side Panel - Weather & Economic */}
              <div className="absolute top-20 left-6 w-80 pointer-events-auto space-y-4 max-h-[calc(100vh-120px)] overflow-y-auto">
                {/* Province Header */}
                <Card className="shadow-xl">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-xl">{selectedProvinceThai || 'เลือกจังหวัด'}</CardTitle>
                    <CardDescription>ข้อมูลสภาพแวดล้อม</CardDescription>
                  </CardHeader>
                </Card>

                {isLoadingProvinceInfo ? (
                  <Card className="shadow-xl">
                    <CardContent className="p-8">
                      <div className="flex items-center justify-center">
                        <Loader2 className="w-6 h-6 animate-spin text-primary" />
                        <span className="ml-2 text-sm text-gray-600">กำลังโหลด...</span>
                      </div>
                    </CardContent>
                  </Card>
                ) : isErrorProvinceInfo ? (
                  <Card className="shadow-xl">
                    <CardContent className="p-4">
                      <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                        <p className="text-red-600 text-sm mb-2">ไม่สามารถโหลดข้อมูลได้</p>
                        <button
                          onClick={() => refetchProvinceInfo()}
                          className="text-sm text-red-700 underline hover:text-red-800"
                        >
                          ลองอีกครั้ง
                        </button>
                      </div>
                    </CardContent>
                  </Card>
                ) : provinceInfo ? (
                  <>
                    {/* Weather Section */}
                    <WeatherSection data={provinceInfo.data.weather} />

                    {/* Economic Section */}
                    <EconomicSection data={provinceInfo.data.economic} />
                  </>
                ) : null}
              </div>

              {/* Right Side Panel - Crops & Prices */}
              <div className="absolute top-20 right-6 w-80 pointer-events-auto space-y-4 max-h-[calc(100vh-120px)] overflow-y-auto">
                {/* Crop Recommendations */}
                

                {provinceInfo && (
                  <>
                    {/* Cultivation Section */}
                    <CultivationSection data={provinceInfo.data.cultivation} />

                    {/* Prices Section */}
                    <PricesSection data={provinceInfo.data.prices} />
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Mobile Layout */}
        <div className="lg:hidden">
          {/* Map Section */}
          <div className="relative h-[400px] mb-6">
            <Card className="h-full w-full bg-card/95 backdrop-blur-sm border-0 shadow-none">
              <CardContent className="p-4 h-full">
                <div
                  className="relative w-full h-full bg-white overflow-visible"
                  ref={containerRef}
                  onClick={(e) => e.stopPropagation()} // Prevent click from reaching document
                >
                  {/* Loading / Error states */}
                  {loading && (
                    <div className="absolute inset-0 grid place-items-center" role="status" aria-live="polite">
                      <div className="text-sm text-muted-foreground">กำลังโหลดแผนที่…</div>
                    </div>
                  )}
                  {!loading && error && (
                    <div className="absolute inset-0 grid place-items-center" role="alert">
                      <div className="text-sm text-destructive">โหลดแผนที่ไม่สำเร็จ: {error}</div>
                    </div>
                  )}

                  {/* Map SVG */}
                  <svg
                    className="w-full h-full"
                    viewBox={svgViewBox ?? '0 0 600 700'}
                    role="img"
                    aria-label="แผนที่ประเทศไทย"
                  >
                    {parsedProvinces.map(({ thaiName, paths, transform }) => {
                      const cropKey: CropKey = getDominantCropKey(thaiName);
                      const fillColor = cropColors[cropKey];
                      const isSelected = selectedProvinceThai === thaiName;
                      const opacity = isSelected || !selectedProvinceThai ? 1 : UI_CONSTANTS.dimOpacity;
                      const mapped = provinceDataMap.get(thaiName);
                      return (
                        <g
                          key={thaiName}
                          id={thaiName}
                          tabIndex={0}
                          role="button"
                          aria-label={`จังหวัด ${thaiName}`}
                          className="outline-none focus:ring-2 focus:ring-primary cursor-pointer"
                          transform={transform}
                          onClick={() => {
                            setSelectedProvinceThai(thaiName);
                            setSelectedProvince(mapped?.id ?? null);
                            // Smart zoom to province on left-click
                            zoomToProvince(thaiName);
                            setIsRightClickMode(false); // Enable side panels for left-click
                          }}
                          onContextMenu={(e) => handleMapRightClick(e, thaiName)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              e.preventDefault();
                              setSelectedProvinceThai(thaiName);
                              setSelectedProvince(mapped?.id ?? null);
                              // Smart zoom to province on keyboard selection
                              zoomToProvince(thaiName);
                              setIsRightClickMode(false); // Enable side panels
                            }
                          }}
                          onMouseEnter={(e) => {
                            const rect = containerRef.current?.getBoundingClientRect();
                            if (!rect) return;
                            const amount = deterministicAmount(thaiName, cropKey);
                            setHoverInfo({
                              show: true,
                              x: e.clientX - rect.left + UI_CONSTANTS.tooltipOffset.x,
                              y: e.clientY - rect.top + UI_CONSTANTS.tooltipOffset.y,
                              provinceThai: thaiName,
                              cropKey,
                              amountTons: amount,
                            });
                          }}
                          onMouseMove={(e) => {
                            const rect = containerRef.current?.getBoundingClientRect();
                            if (!rect) return;
                            setHoverInfo((prev) => ({ ...prev, show: true, x: e.clientX - rect.left + UI_CONSTANTS.tooltipOffset.x, y: e.clientY - rect.top + UI_CONSTANTS.tooltipOffset.y }));
                          }}
                          onMouseLeave={() => setHoverInfo((prev) => ({ ...prev, show: false }))}
                          style={{
                            transform: isSelected ? `translateY(${UI_CONSTANTS.selected.translateY}px) scale(${UI_CONSTANTS.selected.scale})` : undefined,
                            filter: isSelected ? `drop-shadow(${UI_CONSTANTS.selected.shadow})` : undefined,
                            transition: 'transform 200ms ease, filter 200ms ease',
                            opacity,
                          }}
                        >
                          {paths.map((d, idx) => (
                            <path key={idx} d={d} fill={fillColor} />
                          ))}
                        </g>
                      );
                    })}
                  </svg>

                  {hoverInfo.show && (
                    <div
                      className="absolute z-50 pointer-events-none select-none rounded-md border bg-background/95 p-2 shadow-lg backdrop-blur supports-[backdrop-filter]:bg-background/60"
                      style={{ left: hoverInfo.x, top: hoverInfo.y, transform: 'translate(-50%, -115%)', minWidth: 180 }}
                      role="tooltip"
                    >
                      <div className="flex items-center gap-2">
                        {(() => {
                          const Icon = cropIcon[hoverInfo.cropKey];
                          return <Icon className="h-5 w-5 text-foreground/80" />;
                        })()}
                        <div className="text-sm font-medium">{hoverInfo.provinceThai}</div>
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground">
                        พืชเด่น: <span className="font-medium text-foreground">{hoverInfo.cropKey}</span>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        ปริมาณโดยประมาณ: <span className="font-medium text-foreground">{formatTons(hoverInfo.amountTons)} ตัน</span>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Mobile Cards Grid - Balanced Layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Left Column - Environment */}
            <div className="space-y-4">
              {provinceInfo && (
                <>
                  <Card className="shadow-xl">
                    <CardHeader className="pb-3">
                      <CardTitle>{provinceInfo.province}</CardTitle>
                      <CardDescription>ข้อมูลสภาพแวดล้อม</CardDescription>
                    </CardHeader>
                  </Card>
                  <WeatherSection data={provinceInfo.data.weather} />
                  <EconomicSection data={provinceInfo.data.economic} />
                </>
              )}
              {!provinceInfo && !isLoadingProvinceInfo && (
                <Card className="shadow-xl">
                  <CardContent className="text-center text-muted-foreground py-8">
                    <div className="text-4xl mb-4">🗺️</div>
                    <p className="text-lg font-medium mb-2">เลือกจังหวัด</p>
                    <p className="text-sm">คลิกที่จังหวัดในแผนที่เพื่อดูข้อมูล</p>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Right Column - Crops & Prices */}
            <div className="space-y-4">
              
              {provinceInfo && (
                <>
                  <CultivationSection data={provinceInfo.data.cultivation} />
                  <PricesSection data={provinceInfo.data.prices} />
                </>
              )}
            </div>
          </div>

          {/* Loading State */}
          {isLoadingProvinceInfo && (
            <Card className="shadow-xl">
              <CardContent className="p-8">
                <div className="flex items-center justify-center">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                  <span className="ml-2 text-sm text-gray-600">กำลังโหลดข้อมูล...</span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Error State */}
          {isErrorProvinceInfo && (
            <Card className="shadow-xl">
              <CardContent className="p-4">
                <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                  <p className="text-red-600 text-sm mb-2">ไม่สามารถโหลดข้อมูลได้</p>
                  <button
                    onClick={() => refetchProvinceInfo()}
                    className="text-sm text-red-700 underline hover:text-red-800"
                  >
                    ลองอีกครั้ง
                  </button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Summary Statistics Card */}
          {provinceInfo && (
            <Card className="shadow-xl md:col-span-2">
              <CardHeader>
                <CardTitle>สถิติรวม</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-gradient-to-br from-primary/10 to-primary/5 rounded-lg">
                    <div className="text-xl font-bold text-primary">
                      {allProvincesData ? allProvincesData.reduce((sum, p) => sum + (p.supply || 0), 0).toLocaleString() : '0'}
                    </div>
                    <div className="text-xs text-muted-foreground">อุปทานรวม (ตัน)</div>
                  </div>
                  <div className="text-center p-3 bg-gradient-to-br from-accent/10 to-accent/5 rounded-lg">
                    <div className="text-xl font-bold text-accent">
                      {allProvincesData ? allProvincesData.reduce((sum, p) => sum + (p.demand || 0), 0).toLocaleString() : '0'}
                    </div>
                    <div className="text-xs text-muted-foreground">อุปสงค์รวม (ตัน)</div>
                  </div>
                </div>
                <div className="text-center p-3 bg-gradient-to-br from-secondary/20 to-secondary/10 rounded-lg">
                  <div className="text-xl font-bold text-foreground">
                    ฿{allProvincesData && allProvincesData.length > 0 ? Math.round(allProvincesData.reduce((sum, p) => sum + (p.price || 0), 0) / allProvincesData.length) : '0'}
                  </div>
                  <div className="text-xs text-muted-foreground">ราคาเฉลี่ยประเทศ/กก.</div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default ThailandMap;