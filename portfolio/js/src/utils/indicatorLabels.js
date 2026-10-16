// Outputs that are 0/1 flags, not values to plot
const FLAG_OUTPUTS = new Set([
  "bb_bbhi",
  "bb_bbli",
  "keltner_channel_hband_indicator",
  "keltner_channel_lband_indicator",
  "psar_up_indicator",
  "psar_down_indicator",
]);

const outputOf = (series) => series.display_name?.match(/\(([^)]+)\)\s*$/)?.[1] || "";

export const isFlagSeries = (series) => FLAG_OUTPUTS.has(outputOf(series));

/** "macd_indicator (signal)" → "MACD signal"; "rsi_indicator (rsi)" → "RSI". */
export const seriesLabel = (series) => {
  const base = (series.indicator_name || "").replace(/_indicator$/, "");
  const output = outputOf(series);
  const name = base.replace(/_/g, " ").toUpperCase();
  if (!output || output === base) return name;
  const suffix = output.startsWith(`${base}_`) ? output.slice(base.length + 1) : output;
  return `${name} ${suffix.replace(/_/g, " ")}`;
};
