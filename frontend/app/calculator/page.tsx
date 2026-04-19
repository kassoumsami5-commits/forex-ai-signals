'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Calculator, Info, RefreshCw, DollarSign, Percent, Target } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import Navigation from '@/components/Navigation';

const SYMBOLS = [
  { value: 'XAUUSD', label: 'الذهب (XAUUSD)', pipSize: 0.01, lotSize: 100 },
  { value: 'EURUSD', label: 'اليورو/دولار (EURUSD)', pipSize: 0.0001, lotSize: 100000 },
  { value: 'GBPUSD', label: 'الإسترليني/دولار (GBPUSD)', pipSize: 0.0001, lotSize: 100000 },
  { value: 'USDJPY', label: 'الدولار/ين (USDJPY)', pipSize: 0.01, lotSize: 100000 },
  { value: 'BTCUSD', label: 'البيتكوين (BTCUSD)', pipSize: 0.1, lotSize: 1 },
];

export default function CalculatorPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  
  const [symbol, setSymbol] = useState('XAUUSD');
  const [balance, setBalance] = useState(10000);
  const [riskPercent, setRiskPercent] = useState(2);
  const [stopLossPips, setStopLossPips] = useState(50);
  const [result, setResult] = useState<any>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  React.useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  const calculateLotSize = () => {
    setIsCalculating(true);
    
    const selectedSymbol = SYMBOLS.find(s => s.value === symbol) || SYMBOLS[0];
    const riskAmount = balance * (riskPercent / 100);
    
    // Calculate pip value in USD
    const pipValue = selectedSymbol.pipSize * selectedSymbol.lotSize;
    
    // Calculate lot size
    const lotSize = riskAmount / (stopLossPips * pipValue);
    
    // Round appropriately
    let roundedLot = Math.max(0.01, Math.min(lotSize, 100));
    if (symbol === 'BTCUSD') {
      roundedLot = Math.round(roundedLot * 1000) / 1000;
    } else {
      roundedLot = Math.round(roundedLot * 100) / 100;
    }
    
    // Calculate actual risk
    const actualRisk = stopLossPips * pipValue * roundedLot;
    
    setResult({
      lotSize: roundedLot,
      riskAmount: riskAmount,
      actualRisk: actualRisk,
      pipValue: pipValue,
      riskReward: 1.5, // Default ratio
      message: lotSize < 0.01 ? 'حجم اللوت أقل من الحد الأدنى. تم تعيينه إلى 0.01' : 
               lotSize > 100 ? 'حجم اللوت أعلى من الحد الأقصى. تم تعيينه إلى 100' : 
               'تم حساب حجم اللوت بنجاح'
    });
    
    setIsCalculating(false);
  };

  React.useEffect(() => {
    if (isAuthenticated && balance > 0 && riskPercent > 0 && stopLossPips > 0) {
      calculateLotSize();
    }
  }, [symbol, balance, riskPercent, stopLossPips, isAuthenticated]);

  if (authLoading) {
    return (
      <div className="min-h-screen bg-dark-900 flex items-center justify-center">
        <div className="spinner w-12 h-12" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-900">
      <Navigation />
      
      <main className="pt-24 pb-12 px-4">
        <div className="container mx-auto max-w-4xl">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-12 h-12 rounded-xl bg-gold-500/20 flex items-center justify-center">
                <Calculator className="text-gold-400" size={24} />
              </div>
              <h1 className="text-3xl font-bold text-white">حاسبة حجم اللوت</h1>
            </div>
            <p className="text-dark-400">احسب حجم الصفقة الأمثل بناءً على إدارة المخاطر</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Calculator Form */}
            <div className="card">
              <h2 className="text-xl font-bold text-white mb-6">إعدادات الحساب</h2>
              
              <div className="space-y-6">
                {/* Symbol */}
                <div>
                  <label className="input-label">رمز السوق</label>
                  <select
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                    className="input-field"
                  >
                    {SYMBOLS.map((s) => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                </div>

                {/* Balance */}
                <div>
                  <label className="input-label">رصيد الحساب (USD)</label>
                  <div className="relative">
                    <DollarSign className="absolute right-4 top-1/2 -translate-y-1/2 text-dark-400" size={18} />
                    <input
                      type="number"
                      value={balance}
                      onChange={(e) => setBalance(Number(e.target.value))}
                      className="input-field pr-12"
                      min="100"
                      step="100"
                    />
                  </div>
                </div>

                {/* Risk Percent */}
                <div>
                  <label className="input-label">نسبة المخاطر (%)</label>
                  <div className="relative">
                    <Percent className="absolute right-4 top-1/2 -translate-y-1/2 text-dark-400" size={18} />
                    <input
                      type="number"
                      value={riskPercent}
                      onChange={(e) => setRiskPercent(Number(e.target.value))}
                      className="input-field pr-12"
                      min="0.1"
                      max="10"
                      step="0.1"
                    />
                  </div>
                  <div className="mt-2 flex items-center gap-2 text-dark-400 text-sm">
                    <Info size={16} />
                    <span>المعدل الموصى به: 1-2%</span>
                  </div>
                </div>

                {/* Stop Loss Pips */}
                <div>
                  <label className="input-label">مسافة وقف الخسارة (نقاط)</label>
                  <div className="relative">
                    <Target className="absolute right-4 top-1/2 -translate-y-1/2 text-dark-400" size={18} />
                    <input
                      type="number"
                      value={stopLossPips}
                      onChange={(e) => setStopLossPips(Number(e.target.value))}
                      className="input-field pr-12"
                      min="1"
                      max="1000"
                      step="1"
                    />
                  </div>
                </div>
              </div>

              {/* Info Box */}
              <div className="mt-6 p-4 rounded-xl bg-dark-700/50 border border-dark-600">
                <h3 className="text-white font-semibold mb-2">كيفية الحساب:</h3>
                <p className="text-dark-400 text-sm">
                  حجم اللوت = (الرصيد × نسبة المخاطر) / (النقاط × قيمة النقطة)
                </p>
              </div>
            </div>

            {/* Result */}
            <div>
              <h2 className="text-xl font-bold text-white mb-6">النتيجة</h2>
              
              {result && (
                <div className="card border-2 border-gold-500/30">
                  <div className="text-center mb-6">
                    <p className="text-dark-400 mb-2">حجم اللوت الموصى به</p>
                    <p className="text-5xl font-bold text-gold-400">{result.lotSize.toFixed(2)}</p>
                    <p className="text-dark-400 mt-2">لوت</p>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-dark-700/50 rounded-xl p-4 text-center">
                      <p className="text-dark-400 text-sm mb-1">مبلغ المخاطرة</p>
                      <p className="text-xl font-bold text-danger-400">${result.riskAmount.toFixed(2)}</p>
                    </div>
                    <div className="bg-dark-700/50 rounded-xl p-4 text-center">
                      <p className="text-dark-400 text-sm mb-1">قيمة النقطة</p>
                      <p className="text-xl font-bold text-primary-400">${result.pipValue.toFixed(2)}</p>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-dark-700/50 mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-dark-400">نسبة المخاطرة/المكافأة</span>
                      <span className="text-lg font-bold text-success-400">1:{result.riskReward}</span>
                    </div>
                    <div className="h-2 bg-dark-600 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-danger-500 to-success-500 rounded-full w-1/3" />
                    </div>
                  </div>

                  <p className="text-center text-dark-400 text-sm">{result.message}</p>
                </div>
              )}

              {/* Example Trade */}
              <div className="card mt-6">
                <h3 className="text-lg font-bold text-white mb-4">مثال على صفقة</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-dark-400">الدخول</span>
                    <span className="text-white">2300.00</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-dark-400">وقف الخسارة</span>
                    <span className="text-danger-400">2250.00 (-{stopLossPips} نقطة)</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-dark-400">جني الأرباح</span>
                    <span className="text-success-400">2400.00 (+{Math.round(stopLossPips * 1.5)} نقطة)</span>
                  </div>
                  <div className="pt-3 border-t border-dark-700 flex items-center justify-between">
                    <span className="text-dark-400">حجم اللوت</span>
                    <span className="text-gold-400 font-bold">{result?.lotSize.toFixed(2) || '0.00'} لوت</span>
                  </div>
                </div>
              </div>

              {/* Risk Warning */}
              <div className="mt-6 p-4 rounded-xl bg-warning-500/10 border border-warning-500/20">
                <div className="flex items-start gap-3">
                  <Info className="text-warning-500 flex-shrink-0 mt-0.5" size={20} />
                  <div>
                    <h4 className="text-warning-500 font-semibold mb-1">تنبيه مهم</h4>
                    <p className="text-dark-300 text-sm">
                      إدارة المخاطر أمر حاسم في التداول. لا تخاطر بأكثر مما يمكنك تحمل خسارته. 
                      النتائج السابقة لا تضمن النتائج المستقبلية.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}