import { createContext, useContext } from 'react';

interface ProvinceContextType {
  selectedProvince: string | null;
  setSelectedProvince: (province: string | null) => void;
}

export const ProvinceContext = createContext<ProvinceContextType>({
  selectedProvince: null,
  setSelectedProvince: () => {},
});

export const useProvinceContext = () => useContext(ProvinceContext);
