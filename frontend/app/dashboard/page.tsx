'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Clock, 
  RefreshCw,
  AlertCircle,
  CheckCircle,
  XCircle,
  Crown
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { marketAPI, signalsAPI, subscriptionAPI } from '@/services/api';
import Navigation from '@/components/Navigation';
import MarketCard from '@/components/MarketCard';
import SignalCard from '@/components/SignalCard';

interface MarketData {
  symbol: string;
  price: number;
  change_percent?: number;
}

interface SignalData {
  id: number;
  symbol: string;
  signal_type: string;
  entry_price: number;
  stop_loss: number;
  take_profit_1: number;
  take_profit_2: number;
  lot_size: number;
  confidence: number;
  timeframe: string;
  status: string;
  trend?: string;
  explanation?: string;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [latestSignals, setLatestSignals] = useState<SignalData[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [subscription, setSubscription] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchDashboardData();
    }
  }, [isAuthenticated]);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError('');
    
    try {
      // Fetch market overview
      const marketResponse = await marketAPI.getOverview();
      setMarketData(marketResponse.data.data || []);
      
      // Fetch latest signals
      const signalsResponse = await signalsAPI.getLatest(5);
      setLatestSignals(signalsResponse.data || []);
      
      // Fetch signals stats
      const statsResponse = await signalsAPI.getStats();
      setStats(statsResponse.data);
      
      // Fetch subscription info
      const subResponse = await subscriptionAPI.getMySubscription();
      setSubscription(subResponse.data);
    } catch (err: any) {
      console.error('Dashboard fetch error:', err);
      setError('فشل في جلب البيانات. يرجى المحاولة مرة أخرى.');
      
      // Use mock data for demo
      setMarketData([
        { symbol: 'XAUUSD', price: 2345.67, change_percent: 1.09 },
        { symbol: 'EURUSD', price: 1.0845, change_percent: -0.11 },
        { symbol: 'BTCUSD', price: 67234.50, change_percent: 1.87 },
      ]);
      
      setStats({
        total_signals: 24,
        buy_signals: 12,
        sell_signals: 10,
        active_signals: 2,
        average_confidence: 78.5
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (authLoading || isLoading) {
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
          <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                مرحباً، {user?.full_name || 'متداول'}
              </h1>
              <div className="flex items-center gap-3">
                {subscription?.tier === 'vip' && (
                  <span className="badge badge-warning flex items-center gap-1">
                    <Crown size={14} />
                    VIP
                  </span>
                )}
                <span className="text-dark-400">
                  الخطة: {subscription?.name_ar || 'مجاني'}
                </span>
              </div>
            </div>
            
            <button
              onClick={fetchDashboardData}
              className="btn-secondary flex items-center gap-2"
            >
              <RefreshCw size={18} />
              <span>تحديث</span>
            </button>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-danger-500/10 border border-danger-500/20 flex items-center gap-3">
              <AlertCircle className="text-danger-500" size={20} />
              <p className="text-danger-500">{error}</p>
            </div>
          )}

          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <Activity className="text-primary-400" size={20} />
                <span className="text-dark-400 text-xs">إجمالي</span>
              </div>
              <p className="text-3xl font-bold text-white">{stats?.total_signals || 0}</p>
              <p className="text-dark-400 text-sm">إشارة generated</p>
            </div>
            
            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <TrendingUp className="text-success-500" size={20} />
                <span className="text-dark-400 text-xs">شراء</span>
              </div>
              <p className="text-3xl font-bold text-success-400">{stats?.buy_signals || 0}</p>
              <p className="text-dark-400 text-sm">إشارة شراء</p>
            </div>
            
            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <TrendingDown className="text-danger-500" size={20} />
                <span className="text-dark-400 text-xs">بيع</span>
              </div>
              <p className="text-3xl font-bold text-danger-400">{stats?.sell_signals || 0}</p>
              <p className="text-dark-400 text-sm">إشارة بيع</p>
            </div>
            
            <div className="card">
              <div className="flex items-center justify-between mb-2">
                <Clock className="text-gold-400" size={20} />
                <span className="text-dark-400 text-xs">نشط</span>
              </div>
              <p className="text-3xl font-bold text-gold-400">{stats?.active_signals || 0}</p>
              <p className="text-dark-400 text-sm">إشارة نشطة</p>
            </div>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Market Cards - Takes 2 columns */}
            <div className="lg:col-span-2">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-white">أداء السوق</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {marketData.length > 0 ? (
                  marketData.map((market) => (
                    <MarketCard
                      key={market.symbol}
                      symbol={market.symbol}
                      name={getSymbolName(market.symbol)}
                      price={market.price}
                      change={market.price * (market.change_percent || 0) / 100}
                      changePercent={market.change_percent || 0}
                    />
                  ))
                ) : (
                  <div className="col-span-2 text-center py-8 text-dark-400">
                    لا توجد بيانات متاحة حالياً
                  </div>
                )}
              </div>
            </div>

            {/* Latest Signals */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-white">آخر الإشارات</h2>
                <a href="/signals" className="text-primary-400 text-sm hover:underline">
                  عرض الكل
                </a>
              </div>
              
              <div className="space-y-4">
                {latestSignals.length > 0 ? (
                  latestSignals.map((signal) => (
                    <SignalCard 
                      key={signal.id} 
                      id={signal.id}
                      symbol={signal.symbol}
                      signalType={signal.signal_type as 'BUY' | 'SELL' | 'NO_TRADE'}
                      entryPrice={signal.entry_price}
                      stopLoss={signal.stop_loss}
                      takeProfit1={signal.take_profit_1}
                      takeProfit2={signal.take_profit_2}
                      lotSize={signal.lot_size}
                      confidence={signal.confidence}
                      timeframe={signal.timeframe}
                      status={signal.status}
                      trend={signal.trend}
                      createdAt={signal.created_at}
                      explanation={signal.explanation}
                    />
                  ))
                ) : (
                  <div className="card text-center py-8">
                    <p className="text-dark-400 mb-4">لا توجد إشارات حتى الآن</p>
                    <a href="/signals" className="btn-primary text-sm">
                      توليد إشارة جديدة
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mt-8">
            <h2 className="text-xl font-bold text-white mb-4">إجراءات سريعة</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <a href="/signals" className="card card-hover flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center">
                  <TrendingUp className="text-primary-400" size={24} />
                </div>
                <div>
                  <h3 className="font-bold text-white">توليد إشارة</h3>
                  <p className="text-dark-400 text-sm">قم بإنشاء إشارة جديدة</p>
                </div>
              </a>
              
              <a href="/calculator" className="card card-hover flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gold-500/20 flex items-center justify-center">
                  <Activity className="text-gold-400" size={24} />
                </div>
                <div>
                  <h3 className="font-bold text-white">حاسبة اللوت</h3>
                  <p className="text-dark-400 text-sm">احسب حجم الصفقة الأمثل</p>
                </div>
              </a>
              
              <a href="/pricing" className="card card-hover flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-success-500/20 flex items-center justify-center">
                  <Crown className="text-success-400" size={24} />
                </div>
                <div>
                  <h3 className="font-bold text-white">ترقية الاشتراك</h3>
                  <p className="text-dark-400 text-sm">احصل على ميزات إضافية</p>
                </div>
              </a>
            </div>
          </div>

          {/* Subscription Info */}
          {subscription && (
            <div className="mt-8 card">
              <h2 className="text-xl font-bold text-white mb-4">معلومات الاشتراك</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-dark-400 text-sm mb-1">الخطة الحالية</p>
                  <p className="text-lg font-bold text-white">{subscription.name_ar}</p>
                </div>
                {subscription.days_remaining !== null && (
                  <div>
                    <p className="text-dark-400 text-sm mb-1">الأيام المتبقية</p>
                    <p className="text-lg font-bold text-gold-400">{subscription.days_remaining} يوم</p>
                  </div>
                )}
                <div>
                  <p className="text-dark-400 text-sm mb-1">الحالة</p>
                  <span className={`badge ${
                    subscription.status === 'active' ? 'badge-success' : 'badge-warning'
                  }`}>
                    {subscription.status === 'active' ? 'نشط' : 'غير نشط'}
                  </span>
                </div>
              </div>
              
              {subscription.features && (
                <div className="mt-4 pt-4 border-t border-dark-700">
                  <p className="text-dark-400 text-sm mb-2">الميزات المتوفرة:</p>
                  <div className="flex flex-wrap gap-2">
                    {subscription.features.map((feature: string, index: number) => (
                      <span key={index} className="px-3 py-1 rounded-full bg-dark-700 text-dark-300 text-sm">
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function getSymbolName(symbol: string): string {
  const names: Record<string, string> = {
    'XAUUSD': 'الذهب',
    'EURUSD': 'اليورو/دولار',
    'GBPUSD': 'الإسترليني/دولار',
    'USDJPY': 'الدولار/ين',
    'BTCUSD': 'البيتكوين',
    'ETHUSD': 'الإيثيريوم',
  };
  return names[symbol] || symbol;
}