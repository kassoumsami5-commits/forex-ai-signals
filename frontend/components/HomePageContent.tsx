'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import axios from 'axios';
import { 
  TrendingUp, 
  TrendingDown,
  Shield, 
  Zap, 
  Users, 
  Star, 
  ArrowRight,
  CheckCircle,
  LineChart,
  Bell,
  Crown,
  RefreshCw,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import Navigation from '@/components/Navigation';

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

const features = [
  {
    icon: <LineChart className="text-gold-400" size={32} />,
    title: 'تحليل فني متقدم',
    description: 'نستخدم مؤشرات متعددة تشمل EMA و RSI و MACD لتوليد إشارات دقيقة'
  },
  {
    icon: <Shield className="text-success-500" size={32} />,
    title: 'إدارة المخاطر',
    description: 'حاسبة لوت ذكية تساعدك على تحديد حجم الصفقة الأمثل بناءً على رصيدك ومخاطرك'
  },
  {
    icon: <Zap className="text-primary-400" size={32} />,
    title: 'إشعارات فورية',
    description: 'احصل على إشعارات فورية عند توليد إشارات جديدة عبر Telegram'
  },
  {
    icon: <Users className="text-secondary-400" size={32} />,
    title: 'دعم متعدد المنصات',
    description: 'مزامنة مع TradingView وتلقي إشاراتك مباشرة من إعداداتك'
  }
];

const pricingPlans = [
  {
    name: 'مجاني',
    nameAr: 'مجاني',
    price: '0',
    period: '/شهر',
    features: ['إشارة واحدة يومياً', 'الذهب فقط', 'إطار زمني واحد', 'دعم أساسي'],
    button: 'ابدأ مجاناً',
    tier: 'free',
    popular: false
  },
  {
    name: 'Pro',
    nameAr: 'احترافي',
    price: '49.99',
    period: '/شهر',
    features: ['إشارات غير محدودة', 'جميع الأزواج', '4 أطر زمنية', 'دعم متقدم', 'سجل 30 يوم', 'إشعارات Telegram'],
    button: 'اشترك الآن',
    tier: 'pro',
    popular: true
  },
  {
    name: 'VIP',
    nameAr: 'مميز',
    price: '99.99',
    period: '/شهر',
    features: ['كل مميزات Pro', 'العملات المشفرة', 'جميع الأطر الزمنية', 'دعم VIP', 'سجل غير محدود', 'إشارات VIP حصرية'],
    button: 'اشترك VIP',
    tier: 'vip',
    popular: false
  }
];

export default function HomePageContent() {
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
    <div className="min-h-screen bg-dark-900">
      <Navigation />
      
      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="container mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 mb-6">
            <Star className="text-primary-400" size={16} />
            <span className="text-primary-400 text-sm font-medium">منصة إشارات التداول الأولى في العالم العربي</span>
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight">
            إشارات تداول ذكية
            <br />
            <span className="gradient-text">بالذكاء الاصطناعي</span>
          </h1>
          
          <p className="text-xl text-dark-300 max-w-2xl mx-auto mb-10">
            احصل على إشارات تداول دقيقة ومؤتمتة باستخدام أحدث تقنيات الذكاء الاصطناعي والتحليل الفني المتقدم
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/register" className="btn-gold text-lg px-8 py-4 flex items-center gap-2">
              <span>ابدأ مجاناً</span>
              <ArrowRight size={20} />
            </Link>
            <Link href="/demo" className="btn-secondary text-lg px-8 py-4">
              شاهد العرض التوضيحي
            </Link>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 max-w-3xl mx-auto mt-16">
            <div>
              <div className="text-4xl font-bold text-gold-400">95%+</div>
              <div className="text-dark-400 mt-1">دقة الإشارات</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-400">500+</div>
              <div className="text-dark-400 mt-1">مستخدم نشط</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-success-500">10K+</div>
              <div className="text-dark-400 mt-1">إشارة generated</div>
            </div>
          </div>
        </div>
      </section>
      
      {/* Market Overview - Live Data */}
      <section className="py-16 px-4 bg-dark-800/50">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-4">
              <h2 className="text-3xl font-bold text-white">أداء السوق</h2>
              <button
                onClick={() => fetchMarketData(true)}
                disabled={isRefreshing}
                className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors"
                title="تحديث البيانات"
              >
                <RefreshCw 
                  size={20} 
                  className={`text-dark-300 ${isRefreshing ? 'animate-spin' : ''}`} 
                />
              </button>
            </div>
            <p className="text-dark-300">تابع أسعار أهم الأدوات المالية مباشرة</p>
            {globalError && (
              <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-danger-500/20 border border-danger-500/30 text-danger-400 text-sm">
                <AlertCircle size={16} />
                {globalError}
              </div>
            )}
            <p className="text-dark-500 text-xs mt-2">
              التحديث التلقائي كل 5 ثوانٍ
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
                const trendText = isPositive ? 'صاعد' : 'هابط';
                
                return (
                  <div key={market.symbol} className="card card-hover group relative overflow-hidden">
                    {market.error && (
                      <div className="absolute top-2 left-2 z-10">
                        <span className="px-2 py-1 rounded text-xs bg-warning-500/20 text-warning-400 border border-warning-500/30">
                          بيانات تقريبية
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
                      <span>آخر تحديث</span>
                      {market.lastUpdate ? (
                        <span>
                          {market.lastUpdate.toLocaleTimeString('ar-SA', {
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit',
                          })}
                        </span>
                      ) : (
                        <span>جاري التحميل...</span>
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
      
      {/* Features */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">لماذا Forex AI Signals؟</h2>
            <p className="text-dark-300 max-w-2xl mx-auto">
              نقدم لك مجموعة متكاملة من الأدوات والخدمات لتمكينك من اتخاذ قرارات تداول مدروسة
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <div key={index} className="card card-hover text-center">
                <div className="w-16 h-16 rounded-2xl bg-dark-700 flex items-center justify-center mx-auto mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                <p className="text-dark-400 text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* Pricing */}
      <section className="py-20 px-4 bg-dark-800/50">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white mb-4">خطط الاشتراك</h2>
            <p className="text-dark-300">اختر الخطة المناسبة لاحتياجاتك</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {pricingPlans.map((plan) => (
              <div 
                key={plan.tier} 
                className={`card relative ${plan.popular ? 'border-2 border-gold-500 shadow-glow-lg' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 right-1/2 translate-x-1/2">
                    <span className="px-4 py-1 rounded-full bg-gold-500 text-dark-900 text-sm font-bold">
                      الأكثر شعبية
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-6">
                  <div className="w-12 h-12 rounded-xl bg-dark-700 flex items-center justify-center mx-auto mb-4">
                    {plan.tier === 'vip' ? (
                      <Crown className="text-gold-400" size={24} />
                    ) : plan.tier === 'pro' ? (
                      <Star className="text-primary-400" size={24} />
                    ) : (
                      <CheckCircle className="text-success-500" size={24} />
                    )}
                  </div>
                  <h3 className="text-xl font-bold text-white">{plan.nameAr}</h3>
                  <div className="mt-2">
                    <span className="text-4xl font-bold text-white">${plan.price}</span>
                    <span className="text-dark-400">{plan.period}</span>
                  </div>
                </div>
                
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-center gap-3 text-dark-300">
                      <CheckCircle className="text-success-500 flex-shrink-0" size={18} />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Link 
                  href={plan.tier === 'free' ? '/register' : `/register?tier=${plan.tier}`}
                  className={`block text-center py-3 px-6 rounded-xl font-semibold transition-all ${
                    plan.popular 
                      ? 'btn-gold' 
                      : 'bg-dark-700 text-white hover:bg-dark-600 border border-dark-600'
                  }`}
                >
                  {plan.button}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* CTA */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="bg-gradient-to-r from-primary-600/20 to-secondary-600/20 rounded-3xl p-12 text-center border border-primary-500/20">
            <Bell className="w-16 h-16 text-gold-400 mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-white mb-4">جاهز للبدء؟</h2>
            <p className="text-dark-300 mb-8 max-w-xl mx-auto">
              انضم إلى آلاف المتداولين الذين يستخدمون Forex AI Signals يومياً
            </p>
            <Link href="/register" className="btn-gold text-lg px-8 py-4 inline-flex items-center gap-2">
              <span>ابدأ الآن مجاناً</span>
              <ArrowRight size={20} />
            </Link>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="py-12 px-4 border-t border-dark-700">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gold-500 to-gold-600 flex items-center justify-center">
                <Crown className="text-dark-900" size={20} />
              </div>
              <div>
                <h3 className="font-bold gradient-text">Forex AI Signals</h3>
                <p className="text-dark-400 text-sm">إشارات الذكاء الاصطناعي</p>
              </div>
            </div>
            
            <div className="flex items-center gap-6 text-dark-400 text-sm">
              <Link href="/privacy" className="hover:text-white transition-colors">سياسة الخصوصية</Link>
              <Link href="/terms" className="hover:text-white transition-colors">الشروط والأحكام</Link>
              <Link href="/contact" className="hover:text-white transition-colors">تواصل معنا</Link>
            </div>
          </div>
          
          <div className="text-center mt-8 text-dark-500 text-sm">
            © 2024 Forex AI Signals. جميع الحقوق محفوظة.
          </div>
        </div>
      </footer>
    </div>
  );
}
