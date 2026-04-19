'use client';

import React from 'react';
import { ArrowUpRight, ArrowDownRight, Clock, Target, Shield, TrendingUp } from 'lucide-react';

interface SignalCardProps {
  id: number;
  symbol: string;
  signalType: 'BUY' | 'SELL' | 'NO_TRADE';
  entryPrice: number;
  stopLoss: number;
  takeProfit1: number;
  takeProfit2: number;
  lotSize: number;
  confidence: number;
  timeframe: string;
  status: string;
  trend?: string;
  createdAt: string;
  explanation?: string;
  onClick?: () => void;
}

export default function SignalCard({
  symbol,
  signalType,
  entryPrice,
  stopLoss,
  takeProfit1,
  takeProfit2,
  lotSize,
  confidence,
  timeframe,
  trend,
  createdAt,
  explanation
}: SignalCardProps) {
  const isBuy = signalType === 'BUY';
  const signalClass = isBuy ? 'signal-buy' : signalType === 'SELL' ? 'signal-sell' : 'signal-neutral';
  
  const date = new Date(createdAt);
  const formattedDate = date.toLocaleDateString('ar-SA', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  const calculateRiskReward = () => {
    if (stopLoss === 0) return '0';
    const risk = Math.abs(entryPrice - stopLoss);
    const reward = Math.abs(takeProfit1 - entryPrice);
    return (reward / risk).toFixed(2);
  };

  return (
    <div className={`card card-hover cursor-pointer border-l-4 ${isBuy ? 'border-l-success-500' : 'border-l-danger-500'}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
            isBuy ? 'bg-success-500/20' : 'bg-danger-500/20'
          }`}>
            {isBuy ? (
              <ArrowUpRight className="text-success-500" size={20} />
            ) : (
              <ArrowDownRight className="text-danger-500" size={20} />
            )}
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">{symbol}</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className={`badge ${signalClass}`}>
                {signalType === 'BUY' ? 'شراء' : signalType === 'SELL' ? 'بيع' : 'لا يوجد'}
              </span>
              <span className="text-dark-400 text-xs">{timeframe}</span>
            </div>
          </div>
        </div>
        
        {/* Confidence Badge */}
        <div className="flex flex-col items-end">
          <div className="flex items-center gap-1 text-sm">
            <TrendingUp size={14} className="text-primary-400" />
            <span className="font-semibold text-white">{confidence}%</span>
          </div>
          <div className="w-20 h-2 bg-dark-700 rounded-full mt-1 overflow-hidden">
            <div 
              className={`h-full rounded-full ${confidence >= 70 ? 'bg-success-500' : confidence >= 50 ? 'bg-warning-500' : 'bg-danger-500'}`}
              style={{ width: `${confidence}%` }}
            />
          </div>
        </div>
      </div>

      {/* Price Info */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-dark-700/50 rounded-xl p-3">
          <p className="text-dark-400 text-xs mb-1">سعر الدخول</p>
          <p className="text-xl font-bold text-white">{entryPrice.toFixed(5)}</p>
        </div>
        <div className="bg-dark-700/50 rounded-xl p-3">
          <p className="text-dark-400 text-xs mb-1">حجم اللوت</p>
          <p className="text-xl font-bold text-gold-400">{lotSize.toFixed(2)}</p>
        </div>
      </div>

      {/* Levels */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-danger-500/10 border border-danger-500/20 rounded-xl p-3 text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <Shield size={14} className="text-danger-500" />
            <p className="text-dark-400 text-xs">وقف الخسارة</p>
          </div>
          <p className="text-sm font-bold text-danger-400">{stopLoss.toFixed(5)}</p>
        </div>
        <div className="bg-success-500/10 border border-success-500/20 rounded-xl p-3 text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <Target size={14} className="text-success-500" />
            <p className="text-dark-400 text-xs">جني الأرباح 1</p>
          </div>
          <p className="text-sm font-bold text-success-400">{takeProfit1.toFixed(5)}</p>
        </div>
        <div className="bg-primary-500/10 border border-primary-500/20 rounded-xl p-3 text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <Target size={14} className="text-primary-400" />
            <p className="text-dark-400 text-xs">جني الأرباح 2</p>
          </div>
          <p className="text-sm font-bold text-primary-400">{takeProfit2.toFixed(5)}</p>
        </div>
      </div>

      {/* Risk/Reward */}
      <div className="flex items-center justify-between py-3 border-t border-dark-700">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-dark-400">نسبة المخاطرة/المكافأة:</span>
          <span className="font-bold text-gold-400">1:{calculateRiskReward()}</span>
        </div>
        {trend && (
          <span className={`badge ${trend === 'BULLISH' ? 'badge-success' : trend === 'BEARISH' ? 'badge-danger' : 'badge-warning'}`}>
            {trend === 'BULLISH' ? 'صاعد' : trend === 'BEARISH' ? 'هابط' : 'جانبي'}
          </span>
        )}
      </div>

      {/* Footer */}
      {explanation && (
        <div className="mt-3 p-3 bg-dark-700/50 rounded-xl">
          <p className="text-dark-300 text-sm line-clamp-2">{explanation.split('\n')[0]}</p>
        </div>
      )}
      
      <div className="flex items-center justify-between mt-3 text-xs text-dark-400">
        <div className="flex items-center gap-1">
          <Clock size={12} />
          <span>{formattedDate}</span>
        </div>
        <span>forex-ai-signals</span>
      </div>
    </div>
  );
}