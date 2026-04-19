'use client';

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  TrendingUp, 
  TrendingDown,
  RefreshCw,
  AlertCircle,
  Loader2
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Market symbols configuration
const MARKET_SYMBOLS = [
  { symbol: 'XAUUSD', name: 'Gold', nameAr: 'الذهب' },
  { symbol: 'EURUSD', name: 'EUR/USD', nameAr: 'اليورو/دولار' },
  { symbol: 'BTCUSD', name: 'Bitcoin', nameAr: 'البيتكوين' },
];

// Fallback mock data for error states
const MOCK_DATA = {
  XAUUSD: { price: 2345.67, change: 25.43, changePercent: 1.09 },
  EURUSD: { price: 1.0845, change: -0.0012, changePercent: -0.11 },
  BTCUSD: { price: 67234.50, change: 1234.50, changePercent: 1.87 },
};

interface MarketData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  isLoading: boolean;
  error: string | null;
  lastUpdate: Date | null;
}

export default function MarketDataSection() {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [globalError, setGlobalError] = useState<string | null>(null);

  // Initialize market data state
  useEffect(() => {
    const initialData: MarketData[] = MARKET_SYMBOLS.map((s) => ({
      symbol: s.symbol,
      name: s.nameAr,
      price: 0,
      change: 0,
      changePercent: 0,
      isLoading: true,
      error: null,
      lastUpdate: null,
    }));
    setMarketData(initialData);
  }, []);

  // Fetch market data from API
  const fetchMarketData = useCallback(async (isBackgroundRefresh = false) => {
    if (!isBackgroundRefresh) {
      setIsInitialLoading(true);
    } else {
      setIsRefreshing(true);
    }
    setGlobalError(null);

    try {
      // Fetch price for each symbol
      const pricePromises = MARKET_SYMBOLS.map(async (s) => {
        try {
          const response = await axios.get(`${API_URL}/market/price/${s.symbol}`, {
            timeout: 10000,
          });
          return {
            symbol: s.symbol,
            name: s.nameAr,
            price: response.data.price || 0,
            change: response.data.change || 0,
            changePercent: response.data.change_percent || 0,
            isLoading: false,
            error: null,
            lastUpdate: new Date(),
          };
        } catch (err: any) {
          // Use mock data as fallback
          const mock = MOCK_DATA[s.symbol as keyof typeof MOCK_DATA];
          return {
            symbol: s.symbol,
            name: s.nameAr,
            price: mock?.price || 0,
            change: mock?.change || 0,
            changePercent: mock?.changePercent || 0,
            isLoading: false,
            error: 'Unable to fetch live data',
            lastUpdate: new Date(),
          };
        }
      });

      const results = await Promise.all(pricePromises);
      setMarketData(results);
    } catch (err: any) {
      setGlobalError('Error fetching market data');
      // Set all to error state with mock data
      const errorData: MarketData[] = MARKET_SYMBOLS.map((s) => {
        const mock = MOCK_DATA[s.symbol as keyof typeof MOCK_DATA];
        return {
          symbol: s.symbol,
          name: s.nameAr,
          price: mock?.price || 0,
          change: mock?.change || 0,
          changePercent: mock?.changePercent || 0,
          isLoading: false,
          error: 'Unable to fetch live data',
          lastUpdate: null,
        };
      });
      setMarketData(errorData);
    } finally {
      setIsInitialLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    fetchMarketData();
  }, [fetchMarketData]);

  // Auto refresh every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      fetchMarketData(true);
    }, 5000);

    return () => clearInterval(interval);
  }, [fetchMarketData]);

  const formatPrice = (price: number, symbol: string) => {
    if (symbol === 'EURUSD') {
      return price.toFixed(5);
    }
    if (symbol === 'BTCUSD') {
      return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    return price.toFixed(2);
  };

  return (
    <section className="py-16 px-4 bg-dark-800/50">
      <div className="container mx-auto">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <h2 className="text-3xl font-bold text-white">Market Performance</h2>
            <button
              onClick={() => fetchMarketData(true)}
              disabled={isRefreshing}
              className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors"
              title="Refresh data"
            >
              <RefreshCw 
                size={20} 
                className={`text-dark-300 ${isRefreshing ? 'animate-spin' : ''}`} 
              />
            </button>
          </div>
          <p className="text-dark-300">Track live prices of key financial instruments</p>
          {globalError && (
            <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-danger-500/20 border border-danger-500/30 text-danger-400 text-sm">
              <AlertCircle size={16} />
              {globalError}
            </div>
          )}
          <p className="text-dark-500 text-xs mt-2">
            Auto-refresh every 5 seconds
          </p>
        </div>
        
        {isInitialLoading ? (
          // Loading state
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {[1, 2, 3].map((i) => (
              <div key={i} className="card animate-pulse">
                <div className="flex items-start justify-between mb-4">
                  <div className="space-y-2">
                    <div className="h-5 w-20 bg-dark-700 rounded"></div>
                    <div className="h-4 w-16 bg-dark-700 rounded"></div>
                  </div>
                  <div className="w-12 h-12 bg-dark-700 rounded-xl"></div>
                </div>
                <div className="space-y-2">
                  <div className="h-8 w-32 bg-dark-700 rounded"></div>
                  <div className="h-4 w-20 bg-dark-700 rounded"></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          // Market data cards
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {marketData.map((market) => {
              const isPositive = market.change >= 0;
              const TrendIcon = isPositive ? TrendingUp : TrendingDown;
              const trendColor = isPositive ? 'success' : 'danger';
              const trendText = isPositive ? 'Bullish' : 'Bearish';
              
              return (
                <div key={market.symbol} className="card card-hover group relative overflow-hidden">
                  {market.error && (
                    <div className="absolute top-2 left-2 z-10">
                      <span className="px-2 py-1 rounded text-xs bg-warning-500/20 text-warning-400 border border-warning-500/30">
                        Estimated data
                      </span>
                    </div>
                  )}
                  
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-bold text-white">{market.symbol}</span>
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium badge-${trendColor}`}>
                          <TrendIcon size={12} />
                          {trendText}
                        </span>
                      </div>
                      <p className="text-dark-400 text-sm mt-1">{market.name}</p>
                    </div>
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center bg-${trendColor}-500/20`}>
                      {market.symbol === 'XAUUSD' && (
                        <span className="text-2xl">G</span>
                      )}
                      {market.symbol === 'EURUSD' && (
                        <span className="text-2xl">E</span>
                      )}
                      {market.symbol === 'BTCUSD' && (
                        <span className="text-2xl">B</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl font-bold text-white">
                        {formatPrice(market.price, market.symbol)}
                      </span>
                      <span className="text-dark-400 text-sm">USD</span>
                    </div>
                    <div className={`flex items-center gap-2 text-${trendColor}-500`}>
                      <span className="text-sm font-medium">
                        {isPositive ? '+' : ''}{market.change.toFixed(2)}
                      </span>
                      <span className="text-sm">
                        ({isPositive ? '+' : ''}{market.changePercent.toFixed(2)}%)
                      </span>
                    </div>
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-dark-700 flex items-center justify-between text-xs text-dark-400">
                    <span>Last update</span>
                    {market.lastUpdate ? (
                      <span>
                        {market.lastUpdate.toLocaleTimeString('en-US', {
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit',
                        })}
                      </span>
                    ) : (
                      <span>Loading...</span>
                    )}
                  </div>
                  
                  {/* Loading overlay */}
                  {market.isLoading && (
                    <div className="absolute inset-0 bg-dark-800/80 flex items-center justify-center rounded-2xl">
                      <Loader2 className="animate-spin text-primary-400" size={32} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}
