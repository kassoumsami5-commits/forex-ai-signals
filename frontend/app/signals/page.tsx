'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  LineChart, 
  TrendingUp, 
  TrendingDown, 
  AlertCircle, 
  CheckCircle, 
  Loader2,
  RefreshCw,
  Info
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { signalsAPI } from '@/services/api';
import Navigation from '@/components/Navigation';
import SignalCard from '@/components/SignalCard';

const SYMBOLS = [
  { value: 'XAUUSD', label: 'الذهب (XAUUSD)' },
  { value: 'EURUSD', label: 'اليورو/دولار (EURUSD)' },
  { value: 'GBPUSD', label: 'الإسترليني/دولار (GBPUSD)' },
  { value: 'USDJPY', label: 'الدولار/ين (USDJPY)' },
  { value: 'BTCUSD', label: 'البيتكوين (BTCUSD)' },
];

const TIMEFRAMES = [
  { value: '5min', label: '5 دقائق' },
  { value: '15min', label: '15 دقيقة' },
  { value: '30min', label: '30 دقيقة' },
  { value: '1h', label: 'ساعة' },
  { value: '4h', label: '4 ساعات' },
  { value: '1day', label: 'يوم' },
];

export default function SignalsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  
  const [symbol, setSymbol] = useState('XAUUSD');
  const [timeframe, setTimeframe] = useState('1h');
  const [balance, setBalance] = useState(10000);
  const [riskPercent, setRiskPercent] = useState(2);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedSignal, setGeneratedSignal] = useState<any>(null);
  const [error, setError] = useState('');
  const [historySignals, setHistorySignals] = useState<any[]>([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchSignalHistory();
    }
  }, [isAuthenticated]);

  const fetchSignalHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const response = await signalsAPI.getHistory({ limit: 10 });
      setHistorySignals(response.data || []);
    } catch (err) {
      console.error('Error fetching history:', err);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleGenerateSignal = async () => {
    setError('');
    setGeneratedSignal(null);
    setIsGenerating(true);

    try {
      const response = await signalsAPI.generate({
        symbol,
        timeframe,
        balance,
        risk_percent: riskPercent,
        candle_count: 200
      });
      
      setGeneratedSignal(response.data);
      fetchSignalHistory();
    } catch (err: any) {
      console.error('Error generating signal:', err);
      setError(err.response?.data?.detail || 'فشل في توليد الإشارة. يرجى المحاولة مرة أخرى.');
    } finally {
      setIsGenerating(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner w-12 h-12 mx-auto mb-4" />
          <p className="text-dark-400">جاري تحميل البيانات...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-900">
      <Navigation />
      
      <main className="pt-24 pb-12 px-4">
        <div className="container mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">توليد الإشارات</h1>
            <p className="text-dark-400">قم بإنشاء إشارات تداول ذكية باستخدام التحليل الفني المتقدم</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Signal Generator Form */}
            <div className="card">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center">
                  <LineChart className="text-primary-400" size={24} />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">مولد الإشارات</h2>
                  <p className="text-dark-400 text-sm">أدخل البيانات المطلوبة</p>
                </div>
              </div>

              {error && (
                <div className="mb-6 p-4 rounded-xl bg-danger-500/10 border border-danger-500/20 flex items-center gap-3">
                  <AlertCircle className="text-danger-500 flex-shrink-0" size={20} />
                  <p className="text-danger-500 text-sm">{error}</p>
                </div>
              )}

              <div className="space-y-6">
                {/* Symbol Selection */}
                <div>
                  <label className="input-label">رمز السوق</label>
                  <select
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                    className="input-field"
                  >
                    {SYMBOLS.map((s) => (
                      <option key={s.value} value={s.value}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Timeframe Selection */}
                <div>
                  <label className="input-label">الإطار الزمني</label>
                  <select
                    value={timeframe}
                    onChange={(e) => setTimeframe(e.target.value)}
                    className="input-field"
                  >
                    {TIMEFRAMES.map((tf) => (
                      <option key={tf.value} value={tf.value}>
                        {tf.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Balance Input */}
                <div>
                  <label className="input-label">رصيد الحساب (USD)</label>
                  <input
                    type="number"
                    value={balance}
                    onChange={(e) => setBalance(Number(e.target.value))}
                    className="input-field"
                    min="100"
                    step="100"
                  />
                </div>

                {/* Risk Percentage */}
                <div>
                  <label className="input-label">نسبة المخاطر (%)</label>
                  <input
                    type="number"
                    value={riskPercent}
                    onChange={(e) => setRiskPercent(Number(e.target.value))}
                    className="input-field"
                    min="0.1"
                    max="10"
                    step="0.1"
                  />
                  <div className="mt-2 flex items-center gap-2 text-dark-400 text-sm">
                    <Info size={16} />
                    <span>نسبة مئوية من رصيدك للمخاطرة في كل صفقة</span>
                  </div>
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerateSignal}
                  disabled={isGenerating}
                  className="btn-gold w-full flex items-center justify-center gap-2"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="animate-spin" size={20} />
                      <span>جاري توليد الإشارة...</span>
                    </>
                  ) : (
                    <>
                      <LineChart size={20} />
                      <span>توليد الإشارة</span>
                    </>
                  )}
                </button>
              </div>

              {/* Info Box */}
              <div className="mt-6 p-4 rounded-xl bg-dark-700/50 border border-dark-600">
                <h3 className="text-white font-semibold mb-2">مؤشرات التحليل الفني المستخدمة:</h3>
                <ul className="text-dark-400 text-sm space-y-1">
                  <li>• EMA 20, EMA 50, EMA 200 (المتوسطات المتحركة)</li>
                  <li>• RSI (مؤشر القوة النسبية)</li>
                  <li>• MACD (تقارب وتباعد المتوسطات)</li>
                  <li>• ATR (متوسط المدى الحقيقي)</li>
                  <li>• مستويات الدعم والمقاومة</li>
                </ul>
              </div>
            </div>

            {/* Generated Signal */}
            <div>
              <h2 className="text-xl font-bold text-white mb-4">النتيجة</h2>
              
              {isGenerating ? (
                <div className="card text-center py-12">
                  <Loader2 className="animate-spin w-12 h-12 text-primary-400 mx-auto mb-4" />
                  <p className="text-dark-400">جاري تحليل السوق...</p>
                </div>
              ) : generatedSignal ? (
                <SignalCard
                  id={generatedSignal.id}
                  symbol={generatedSignal.symbol}
                  signalType={generatedSignal.signal_type}
                  entryPrice={generatedSignal.entry_price}
                  stopLoss={generatedSignal.stop_loss}
                  takeProfit1={generatedSignal.take_profit_1}
                  takeProfit2={generatedSignal.take_profit_2}
                  lotSize={generatedSignal.lot_size}
                  confidence={generatedSignal.confidence}
                  timeframe={generatedSignal.timeframe}
                  status={generatedSignal.status}
                  trend={generatedSignal.trend}
                  createdAt={generatedSignal.created_at}
                  explanation={generatedSignal.explanation}
                />
              ) : (
                <div className="card text-center py-12">
                  <LineChart className="w-12 h-12 text-dark-600 mx-auto mb-4" />
                  <p className="text-dark-400">قم بتعبئة البيانات واضغط على &quot;توليد الإشارة&quot;</p>
                </div>
              )}

              {/* Indicators Data */}
              {generatedSignal?.indicators && (
                <div className="card mt-6">
                  <h3 className="text-lg font-bold text-white mb-4">مؤشرات السوق</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-dark-700/50 rounded-xl p-3">
                      <p className="text-dark-400 text-xs mb-1">EMA 20</p>
                      <p className="text-lg font-bold text-white">{generatedSignal.indicators.ema_20?.toFixed(5)}</p>
                    </div>
                    <div className="bg-dark-700/50 rounded-xl p-3">
                      <p className="text-dark-400 text-xs mb-1">EMA 50</p>
                      <p className="text-lg font-bold text-white">{generatedSignal.indicators.ema_50?.toFixed(5)}</p>
                    </div>
                    <div className="bg-dark-700/50 rounded-xl p-3">
                      <p className="text-dark-400 text-xs mb-1">RSI</p>
                      <p className="text-lg font-bold text-white">{generatedSignal.indicators.rsi?.toFixed(2)}</p>
                    </div>
                    <div className="bg-dark-700/50 rounded-xl p-3">
                      <p className="text-dark-400 text-xs mb-1">MACD</p>
                      <p className="text-lg font-bold text-white">{generatedSignal.indicators.macd?.toFixed(5)}</p>
                    </div>
                    <div className="bg-dark-700/50 rounded-xl p-3 col-span-2">
                      <p className="text-dark-400 text-xs mb-1">ATR</p>
                      <p className="text-lg font-bold text-gold-400">{generatedSignal.indicators.atr?.toFixed(5)}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Signal History */}
          <div className="mt-12">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">سجل الإشارات</h2>
              <button
                onClick={fetchSignalHistory}
                className="btn-secondary flex items-center gap-2"
              >
                <RefreshCw size={18} />
                <span>تحديث</span>
              </button>
            </div>

            {isLoadingHistory ? (
              <div className="card text-center py-12">
                <Loader2 className="animate-spin w-12 h-12 text-primary-400 mx-auto mb-4" />
                <p className="text-dark-400">جاري تحميل السجل...</p>
              </div>
            ) : historySignals.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {historySignals.map((signal) => (
                  <SignalCard key={signal.id} {...signal} />
                ))}
              </div>
            ) : (
              <div className="card text-center py-12">
                <p className="text-dark-400">لا توجد إشارات سابقة</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}