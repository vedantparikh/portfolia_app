# SymbolSearch Component Usage Examples

## Basic Usage

```javascript
import { SymbolSearch } from "../shared";

const MyComponent = () => {
  const [symbol, setSymbol] = useState("");

  const handleSymbolChange = (value) => {
    setSymbol(value);
  };

  const handleSymbolSelect = (suggestion) => {
    console.log("Selected:", suggestion);
    setSymbol(suggestion.symbol);
  };

  return (
    <div>
      <label>Search Symbol:</label>
      <SymbolSearch
        value={symbol}
        onChange={handleSymbolChange}
        onSelect={handleSymbolSelect}
        placeholder="Enter symbol..."
      />
    </div>
  );
};
```

## Advanced Usage with Form Integration

```javascript
import { SymbolSearch } from "../shared";

const TransactionForm = () => {
  const [formData, setFormData] = useState({
    symbol: "",
    name: "",
    quantity: "",
    price: "",
    currency: "USD",
  });

  const handleSymbolChange = (value) => {
    setFormData((prev) => ({
      ...prev,
      symbol: value,
    }));
  };

  const handleSymbolSelect = (suggestion) => {
    setFormData((prev) => ({
      ...prev,
      symbol: suggestion.symbol,
      name: suggestion.longname || suggestion.shortname || suggestion.name,
      currency: "USD", // Could be enhanced to detect from exchange
    }));
  };

  return (
    <form>
      <div className="form-group">
        <label>Symbol *</label>
        <SymbolSearch
          value={formData.symbol}
          onChange={handleSymbolChange}
          onSelect={handleSymbolSelect}
          placeholder="e.g., AAPL, MSFT"
          showSuggestions={true}
        />
      </div>

      <div className="form-group">
        <label>Asset Name</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) =>
            setFormData((prev) => ({ ...prev, name: e.target.value }))
          }
          placeholder="Auto-filled from symbol search"
        />
      </div>

      {/* Other form fields... */}
    </form>
  );
};
```

## Usage in Portfolio Management

```javascript
import { SymbolSearch } from "../shared";

const PortfolioAssetAllocation = () => {
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [allocation, setAllocation] = useState("");

  const handleSymbolSelect = (suggestion) => {
    setSelectedSymbol(suggestion.symbol);
    // Could automatically fetch current price, market cap, etc.
  };

  return (
    <div className="portfolio-allocation">
      <h3>Add Asset to Portfolio</h3>

      <div className="form-group">
        <label>Select Asset</label>
        <SymbolSearch
          value={selectedSymbol}
          onChange={setSelectedSymbol}
          onSelect={handleSymbolSelect}
          placeholder="Search for assets to add..."
          showSuggestions={true}
        />
      </div>

      {selectedSymbol && (
        <div className="form-group">
          <label>Allocation %</label>
          <input
            type="number"
            value={allocation}
            onChange={(e) => setAllocation(e.target.value)}
            placeholder="Enter allocation percentage"
          />
        </div>
      )}
    </div>
  );
};
```

## Usage in Watchlist with Popular Symbols

```javascript
import { SymbolSearch } from "../shared";

const WatchlistAddSymbol = () => {
  const [symbol, setSymbol] = useState("");
  const [popularSymbols] = useState(["AAPL", "GOOGL", "MSFT", "TSLA"]);

  const handleSymbolSelect = (suggestion) => {
    // Automatically add to watchlist
    addToWatchlist(suggestion);
    setSymbol("");
  };

  const handlePopularClick = (symbol) => {
    setSymbol(symbol);
    // Could trigger search or add directly
  };

  return (
    <div>
      <div className="form-group">
        <label>Add Symbol to Watchlist</label>
        <SymbolSearch
          value={symbol}
          onChange={setSymbol}
          onSelect={handleSymbolSelect}
          placeholder="Search symbols..."
          showSuggestions={true}
        />
      </div>

      <div className="popular-symbols">
        <h4>Popular Symbols</h4>
        <div className="symbol-grid">
          {popularSymbols.map((sym) => (
            <button
              key={sym}
              onClick={() => handlePopularClick(sym)}
              className="symbol-button"
            >
              {sym}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
```

## Conditional Usage Based on Authentication

```javascript
import { SymbolSearch } from "../shared";
import { useAuth } from "../../contexts/AuthContext";

const ConditionalSymbolSearch = () => {
  const { isAuthenticated } = useAuth();
  const [symbol, setSymbol] = useState("");

  return (
    <div>
      <label>Symbol Search</label>
      <SymbolSearch
        value={symbol}
        onChange={setSymbol}
        onSelect={(suggestion) => console.log(suggestion)}
        placeholder="Search symbols..."
        showSuggestions={isAuthenticated} // Only show suggestions when logged in
        disabled={!isAuthenticated} // Disable when not logged in
      />

      {!isAuthenticated && (
        <p className="text-warning">Please log in to search for symbols</p>
      )}
    </div>
  );
};
```

## Custom Styling

```javascript
import { SymbolSearch } from "../shared";

const CustomStyledSearch = () => {
  const [symbol, setSymbol] = useState("");

  return (
    <div>
      <label>Custom Styled Search</label>
      <SymbolSearch
        value={symbol}
        onChange={setSymbol}
        onSelect={(suggestion) => console.log(suggestion)}
        placeholder="Custom placeholder..."
        className="custom-search-class"
        showSuggestions={true}
      />
    </div>
  );
};
```

## Props Reference

| Prop              | Type     | Default           | Description                        |
| ----------------- | -------- | ----------------- | ---------------------------------- |
| `value`           | string   | ''                | Current input value                |
| `onChange`        | function | -                 | Called when input changes          |
| `onSelect`        | function | -                 | Called when suggestion is selected |
| `placeholder`     | string   | "e.g., AAPL, BTC" | Input placeholder text             |
| `className`       | string   | ""                | Additional CSS classes             |
| `disabled`        | boolean  | false             | Disable input                      |
| `showSuggestions` | boolean  | true              | Enable/disable suggestions         |
| `autoFocus`       | boolean  | false             | Auto-focus input                   |

## Suggestion Object Structure

When a suggestion is selected, the `onSelect` callback receives an object with this structure:

```javascript
{
    symbol: "AAPL",                    // Stock symbol
    longname: "Apple Inc.",           // Full company name
    shortname: "Apple Inc.",          // Short company name
    name: "Apple Inc.",               // Alternative name
    exchDisp: "NASDAQ",               // Exchange display name
    typeDisp: "Equity",               // Asset type display
    sector: "Technology",             // Industry sector
    industry: "Consumer Electronics", // Industry classification
    exchange: "NMS",                  // Exchange code
    quoteType: "EQUITY",              // Quote type
    isYahooFinance: true              // Yahoo Finance flag
}
```

## Best Practices

1. **Always handle both onChange and onSelect** - onChange for typing, onSelect for selection
2. **Use showSuggestions conditionally** - Only enable when user is authenticated
3. **Provide meaningful placeholders** - Help users understand what to search for
4. **Handle loading states** - Show loading indicators during search
5. **Validate selected symbols** - Ensure selected symbols are valid for your use case
6. **Clear form after selection** - Reset form state after successful selection
7. **Provide fallback options** - Show popular symbols or manual entry options

## Common Patterns

### Pattern 1: Form Integration

- Use SymbolSearch for symbol input
- Auto-populate other fields on selection
- Validate required fields before submission

### Pattern 2: Quick Add

- Use SymbolSearch with immediate action on selection
- Provide popular symbols for quick access
- Clear input after successful addition

### Pattern 3: Search and Select

- Use SymbolSearch for searching
- Show additional details before selection
- Allow multiple selections or single selection

### Pattern 4: Conditional Search

- Enable/disable based on user state
- Show different placeholders based on context
- Provide alternative input methods when disabled
