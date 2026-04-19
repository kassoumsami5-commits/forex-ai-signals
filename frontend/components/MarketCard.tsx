'use client';

import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface MarketCardProps {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  onClick?: () => void;
  isLoading?: boolean;
  lastUpdate?: Date | null;
  hasError?: boolean;
}

export default function MarketCard({
  symbol,
  name,
  price,
  change,
  changePercent,
  onClick,
  isLoading = false,
  lastUpdate,
  hasError = false
}: MarketCardProps) {
  const isPositive = change >= 0;
  const TrendIcon = isPositive ? TrendingUp : TrendingDown;
  const trendColor = isPositive ? 'success' : 'danger';
  const trendText = isPositive ? 'صاعد' : 'هابط';

  const formatPrice = (price: number, symbol: string) => {
    if (symbol === 'EURUSD') {
      return price.toFixed(5);
    }
    if (symbol === 'BTCUSD') {
      return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    return price.toFixed(2);
  };

  const getSymbolEmoji = (symbol: string) => {
    if (symbol.startsWith('XAU')) return '🥇';
    if (symbol.startsWith('BTC')) return '₿';
    if (symbol.startsWith('EUR')) return '💱';
    return '📊';
  };

  return (
    <div 
      onClick={onClick}
      className={`card card-hover group cursor-pointer relative overflow-hidden ${isLoading ? 'opacity-70' : ''}`}
    >
      {/* Error badge */}
      {hasError && (
        <div className="absolute top-2 left-2 z-10">
          <span className="px-2 py-1 rounded text-xs bg-warning-500/20 text-warning-400 border border-warning-500/30">
            بيانات تقريبية
          </span>
        </div>
      )}
      
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-white">{symbol}</span>
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium badge-${trendColor}`}>
              <TrendIcon size={12} />
              {isLoading ? '...' : trendText}
            </span>
          </div>
          <p className="text-dark-400 text-sm mt-1">{name}</p>
        </div>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center bg-${trendColor}-500/20`}>
          <span className="text-2xl">{getSymbolEmoji(symbol)}</span>
        </div>
      </div>
      
      <div className="space-y-2">
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-white">
            {isLoading ? '...' : formatPrice(price, symbol)}
          </span>
          <span className="text-dark-400 text-sm">USD</span>
        </div>
        <div className={`flex items-center gap-2 text-${trendColor}-500`}>
          <span className="text-sm font-medium">
            {isLoading ? '...' : `${isPositive ? '+' : ''}${change.toFixed(2)}`}
          </span>
          <span className="text-sm">
            {isLoading ? '' : `(${isPositive ? '+' : ''}${changePercent.toFixed(2)}%)`}
          </span>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-dark-700 flex items-center justify-between text-xs text-dark-400">
        <span>آخر تحديث</span>
        {lastUpdate ? (
          <span>
            {lastUpdate.toLocaleTimeString('ar-SA', {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            })}
          </span>
        ) : (
          <span>{isLoading ? 'جاري التحميل...' : 'الآن'}</span>
        )}
      </div>
      
      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-dark-800/50 flex items-center justify-center rounded-2xl">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-dark-600 border-t-primary-500"></div>
        </div>
      )}
      
      {/* Hover effect */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-primary-500/5 to-secondary-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
    </div>
  );
}
