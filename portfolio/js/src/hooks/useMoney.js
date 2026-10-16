import { createContext, useContext, useMemo } from "react";
import { formatCurrency, formatPrice } from "../utils/formatters.jsx";

export const CurrencyContext = createContext("USD");

/** Money formatters bound to the surrounding portfolio's currency (`CurrencyProvider`). */
export const useMoney = () => {
  const currency = useContext(CurrencyContext);
  return useMemo(() => {
    const money = (amount, options = {}) => formatCurrency(amount, { currency, ...options });
    money.currency = currency;
    money.price = (price) => formatPrice(price, currency);
    return money;
  }, [currency]);
};
