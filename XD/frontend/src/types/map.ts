export type CropKey = 'rice' | 'sugarcane' | 'cassava' | 'rubber' | 'corn' | 'mixed';

export interface ProvinceData {
  id: string;
  name: string; // Thai name for display
  paths: string[]; // SVG path d values (one province may consist of multiple paths)
  colors: string[]; // optional default colors for paths when using inline data
  supply: number;
  demand: number;
  price: number; // average price per kg
  description?: string;
}

export interface HoverInfo {
  show: boolean;
  x: number;
  y: number;
  provinceThai: string;
  cropKey: CropKey;
  amountTons: number;
}


