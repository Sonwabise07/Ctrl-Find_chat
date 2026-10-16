/** `asset_no` becomes `Asset no`. */
export const humanise = (key: string) => {
  const words = key.replace(/_/g, ' ');
  return words.charAt(0).toUpperCase() + words.slice(1);
};
