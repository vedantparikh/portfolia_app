# Chart Component Documentation

## Overview

The Chart component is a highly configurable, shared React component that provides TradingView-powered charts for stock market data visualization and technical analysis. It's built using the `lightweight-charts` library and is designed to work with yfinance data.

## Features

- **Multiple Chart Types**: Candlestick, Line, Area, and Bar charts
- **Technical Analysis**: Built-in indicators (SMA, EMA, RSI, MACD)
- **Interval Selection**: Support for various time intervals (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
- **Volume Visualization**: Optional volume bars with color coding
- **Interactive Controls**: Refresh, fullscreen, and technical indicator toggles
- **Responsive Design**: Adapts to different screen sizes
- **Dark/Light Themes**: Configurable theme support
- **Real-time Updates**: Support for live data updates

## Installation

The component requires the `lightweight-charts` library:

```bash
npm install lightweight-charts
```

## Usage

### Basic Usage

```jsx
import { Chart } from "../shared";

const MyComponent = () => {
  const [data, setData] = useState([]);

  return <Chart data={data} symbol="AAPL" interval="1d" height={400} />;
};
```

### Advanced Usage with Technical Analysis

```jsx
import { Chart } from "../shared";

const AdvancedChart = () => {
  const [data, setData] = useState([]);
  const [interval, setInterval] = useState("1d");

  const handleIntervalChange = (newInterval) => {
    setInterval(newInterval);
    // Fetch new data based on interval
    fetchData(newInterval);
  };

  return (
    <Chart
      data={data}
      symbol="AAPL"
      interval={interval}
      onIntervalChange={handleIntervalChange}
      height={500}
      showVolume={true}
      showTechnicalIndicators={true}
      technicalIndicators={["SMA", "EMA", "RSI", "MACD"]}
      showControls={true}
      showIntervalSelector={true}
      showTechnicalToggle={true}
      chartType="candlestick"
      theme="dark"
      onRefresh={() => fetchData(interval)}
    />
  );
};
```

## Props

### Required Props

| Prop   | Type    | Description                 |
| ------ | ------- | --------------------------- |
| `data` | `Array` | Array of price data objects |

### Optional Props

| Prop                      | Type       | Default                                          | Description                      |
| ------------------------- | ---------- | ------------------------------------------------ | -------------------------------- |
| `symbol`                  | `string`   | `''`                                             | Stock symbol for display         |
| `interval`                | `string`   | `'1d'`                                           | Time interval for data           |
| `onIntervalChange`        | `function` | `undefined`                                      | Callback when interval changes   |
| `height`                  | `number`   | `400`                                            | Chart height in pixels           |
| `showVolume`              | `boolean`  | `true`                                           | Show volume bars                 |
| `showTechnicalIndicators` | `boolean`  | `false`                                          | Enable technical indicators      |
| `technicalIndicators`     | `Array`    | `['SMA', 'EMA']`                                 | Array of indicators to show      |
| `theme`                   | `string`   | `'dark'`                                         | Chart theme ('dark' or 'light')  |
| `className`               | `string`   | `''`                                             | Additional CSS classes           |
| `loading`                 | `boolean`  | `false`                                          | Show loading state               |
| `onRefresh`               | `function` | `undefined`                                      | Refresh callback                 |
| `showControls`            | `boolean`  | `true`                                           | Show control buttons             |
| `showIntervalSelector`    | `boolean`  | `true`                                           | Show interval selector           |
| `showTechnicalToggle`     | `boolean`  | `true`                                           | Show technical indicator toggles |
| `chartType`               | `string`   | `'candlestick'`                                  | Chart type                       |
| `timeFormat`              | `string`   | `'MMM dd, yyyy'`                                 | Time format for display          |
| `priceFormat`             | `object`   | `{ type: 'price', precision: 2, minMove: 0.01 }` | Price formatting                 |
| `volumeFormat`            | `object`   | `{ type: 'volume', precision: 0 }`               | Volume formatting                |

## Data Format

The component expects data in the following format:

```javascript
const data = [
  {
    date: "2024-01-01", // ISO date string
    open: "150.00", // Opening price
    high: "155.00", // High price
    low: "148.00", // Low price
    close: "152.00", // Closing price
    volume: 1000000, // Trading volume
  },
  // ... more data points
];
```

## Chart Types

### Candlestick Chart

```jsx
<Chart chartType="candlestick" />
```

- Shows open, high, low, close prices
- Green/red color coding for bullish/bearish candles
- Most detailed view for price action

### Line Chart

```jsx
<Chart chartType="line" />
```

- Simple line connecting closing prices
- Clean, minimal view
- Good for trend analysis

### Area Chart

```jsx
<Chart chartType="area" />
```

- Filled area under the line
- Emphasizes volume of price movement
- Good for overall trend visualization

### Bar Chart

```jsx
<Chart chartType="bar" />
```

- Histogram-style bars
- Alternative to candlestick
- Good for volume analysis

## Technical Indicators

### Simple Moving Average (SMA)

- Calculates average price over specified period
- Default period: 20
- Color: Orange

### Exponential Moving Average (EMA)

- Weighted average giving more weight to recent prices
- Default period: 20
- Color: Purple

### Relative Strength Index (RSI)

- Momentum oscillator (0-100)
- Default period: 14
- Color: Red
- Shows overbought/oversold conditions

### MACD (Moving Average Convergence Divergence)

- Trend-following momentum indicator
- Shows relationship between two moving averages
- Color: Green

## Intervals

Supported intervals for yfinance data:

- `1m` - 1 Minute
- `5m` - 5 Minutes
- `15m` - 15 Minutes
- `30m` - 30 Minutes
- `1h` - 1 Hour
- `1d` - 1 Day
- `1wk` - 1 Week
- `1mo` - 1 Month

## Styling

The component uses Tailwind CSS classes and supports custom styling through the `className` prop. The dark theme is optimized for the application's design system.

## Integration with AssetModal

The Chart component has been integrated into the AssetModal to replace the previous custom chart implementation. It provides:

- Better performance with TradingView's optimized rendering
- Professional chart appearance
- Technical analysis capabilities
- Interactive features
- Responsive design

## Examples

### Portfolio Dashboard

```jsx
<Chart
  data={portfolioData}
  symbol="Portfolio"
  height={300}
  showVolume={false}
  showTechnicalIndicators={false}
  showControls={false}
/>
```

### Detailed Asset Analysis

```jsx
<Chart
  data={assetData}
  symbol={asset.symbol}
  interval={selectedInterval}
  onIntervalChange={handleIntervalChange}
  height={500}
  showVolume={true}
  showTechnicalIndicators={true}
  technicalIndicators={["SMA", "EMA", "RSI"]}
  showControls={true}
  chartType="candlestick"
/>
```

### Mobile-Optimized Chart

```jsx
<Chart
  data={data}
  height={250}
  showControls={false}
  showIntervalSelector={false}
  showTechnicalToggle={false}
  chartType="line"
/>
```

## Performance Considerations

- The component uses `useMemo` for expensive calculations
- Charts are automatically resized on window resize
- Data updates are optimized to prevent unnecessary re-renders
- Technical indicators are calculated client-side for better performance

## Browser Support

The component supports all modern browsers that support:

- ES6+ features
- Canvas API
- CSS Grid/Flexbox

## Troubleshooting

### Common Issues

1. **Chart not rendering**: Ensure data is in the correct format
2. **Performance issues**: Reduce data points or disable technical indicators
3. **Styling conflicts**: Check for CSS conflicts with Tailwind classes
4. **Memory leaks**: Ensure proper cleanup in useEffect

### Debug Mode

Enable debug logging by setting `console.log` statements in the component for troubleshooting data flow and rendering issues.
