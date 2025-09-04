import React, { useState } from 'react';
import SymbolSearch from './SymbolSearch';

const SymbolSearchTest = () => {
    const [selectedSymbol, setSelectedSymbol] = useState('');
    const [searchValue, setSearchValue] = useState('');

    const handleSymbolSelect = (suggestion) => {
        console.log('Selected symbol:', suggestion);
        setSelectedSymbol(suggestion.symbol);
    };

    const handleSymbolChange = (value) => {
        setSearchValue(value);
    };

    return (
        <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-100 mb-4">SymbolSearch Component Test</h3>
            <p className="text-sm text-gray-400 mb-4">
                Test the reusable SymbolSearch component
            </p>

            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                        Symbol Search
                    </label>
                    <SymbolSearch
                        value={searchValue}
                        onChange={handleSymbolChange}
                        onSelect={handleSymbolSelect}
                        placeholder="Search for symbols..."
                        showSuggestions={true}
                    />
                </div>

                {selectedSymbol && (
                    <div className="p-4 bg-dark-800 border border-dark-600 rounded-lg">
                        <h4 className="text-md font-medium text-gray-200 mb-2">Selected Symbol:</h4>
                        <p className="text-gray-300">{selectedSymbol}</p>
                    </div>
                )}

                <div className="p-4 bg-dark-800 border border-dark-600 rounded-lg">
                    <h4 className="text-md font-medium text-gray-200 mb-2">Current Search Value:</h4>
                    <p className="text-gray-300">{searchValue || 'No value'}</p>
                </div>
            </div>
        </div>
    );
};

export default SymbolSearchTest;
