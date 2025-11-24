export const formatTons = (n: number) => n.toLocaleString('th-TH');

export const deterministicAmount = (provinceThai: string, cropKey: string) => {
  let hash = 0;
  const key = provinceThai + '|' + cropKey;
  for (let i = 0; i < key.length; i++) {
    hash = (hash * 31 + key.charCodeAt(i)) >>> 0;
  }
  const base = 500; // tons
  const variance = 2000; // tons
  return base + (hash % variance);
};


