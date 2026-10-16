import { CurrencyContext } from "../hooks/useMoney";

export const CurrencyProvider = ({ currency, children }) => (
  <CurrencyContext.Provider value={currency || "USD"}>{children}</CurrencyContext.Provider>
);
