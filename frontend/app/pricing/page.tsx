'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Check, X, Crown, Star, Zap, CreditCard, ArrowRight } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import Navigation from '@/components/Navigation';

interface Plan {
  tier: string;
  name: string;
  nameAr: string;
  price: number;
  priceMonthly: number;
  periodDays: number | null;
  features: string[];
  limits: {
    signalsPerDay: number;
    symbols: string[];
    timeframes: string[];
    historyDays: number;
  };
  popular?: boolean;
}

const PLANS: Plan[] = [
  {
    tier: 'free',
    name: 'Free',
    nameAr: 'مجاني',
    price: 0,
    priceMonthly: 0,
    periodDays: null,
    features: [
      'إشارة واحدة يومياً',
      'الذهب فقط (XAUUSD)',
      'إطار زمني واحد (1 ساعة)',
      'دعم أساسي',
      'مؤشرات أساسية (EMA, RSI)'
    ],
    limits: {
      signalsPerDay: 1,
      symbols: ['XAUUSD'],
      timeframes: ['1h'],
      historyDays: 0
    },
    popular: false
  },
  {
    tier: 'pro',
    name: 'Pro',
    nameAr: 'احترافي',
    price: 49.99,
    priceMonthly: 49.99,
    periodDays: 30,
    features: [
      'إشارات غير محدودة',
      'جميع أزواج العملات الرئيسية',
      '4 أطر زمنية متقدمة',
      'دعم متقدم',
      'سجل 30 يوم للإشارات',
      'إشعارات Telegram',
      'تحليل يومي للسوق',
      'مؤشرات متقدمة (MACD, ATR)'
    ],
    limits: {
      signalsPerDay: -1,
      symbols: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD'],
      timeframes: ['15min', '30min', '1h', '4h'],
      historyDays: 30
    },
    popular: true
  },
  {
    tier: 'vip',
    name: 'VIP',
    nameAr: 'مميز',
    price: 99.99,
    priceMonthly: 99.99,
    periodDays: 30,
    features: [
      'كل مميزات الباقة الاحترافية',
      'جميع الأدوات المالية',
      'العملات المشفرة (BTC, ETH)',
      'جميع الأطر الزمنية',
      'دعم VIP مخصص',
      'سجل غير محدود للإشارات',
      'إشارات VIP حصرية',
      'توصيات يدوية يومية',
      'تحليلات متقدمة للسوق'
    ],
    limits: {
      signalsPerDay: -1,
      symbols: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'BTCUSD', 'ETHUSD'],
      timeframes: ['5min', '15min', '30min', '1h', '4h', '1day'],
      historyDays: -1
    },
    popular: false
  }
];

export default function PricingPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading, user } = useAuth();
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [isSubscribing, setIsSubscribing] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  const handleSubscribe = async (tier: string) => {
    if (!isAuthenticated) {
      router.push('/register');
      return;
    }

    setIsSubscribing(true);
    setSelectedPlan(tier);

    // Simulate subscription process
    setTimeout(() => {
      setIsSubscribing(false);
      setSelectedPlan(null);
      alert(`تم الاشتراك في الباقة ${tier === 'free' ? 'المجانية' : tier === 'pro' ? 'الاحترافية' : 'المميزة'} بنجاح!`);
    }, 1500);
  };

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
        <div className="container mx-auto max-w-6xl">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gold-500/10 border border-gold-500/20 mb-6">
              <Crown className="text-gold-400" size={18} />
              <span className="text-gold-400 font-semibold">اختر خطتك</span>
            </div>

            <h1 className="text-4xl font-bold text-white mb-4">
              خطط الاشتراك
            </h1>

            <p className="text-dark-300 text-lg max-w-2xl mx-auto mb-8">
              اختر الباقة المناسبة لاحتياجاتك في التداول واحصل على إشارات ذكية ومتقدمة
            </p>

            {/* Billing Toggle */}
            <div className="flex items-center justify-center gap-4 mb-12">
              <button
                onClick={() => setBillingCycle('monthly')}
                className={`px-6 py-2 rounded-xl font-medium transition-all ${
                  billingCycle === 'monthly'
                    ? 'bg-primary-500 text-white'
                    : 'bg-dark-700 text-dark-300 hover:bg-dark-600'
                }`}
              >
                شهري
              </button>

              <button
                onClick={() => setBillingCycle('yearly')}
                className={`px-6 py-2 rounded-xl font-medium transition-all relative ${
                  billingCycle === 'yearly'
                    ? 'bg-primary-500 text-white'
                    : 'bg-dark-700 text-dark-300 hover:bg-dark-600'
                }`}
              >
                سنوي
                <span className="absolute -top-2 -right-2 px-2 py-0.5 rounded-full bg-success-500 text-dark-900 text-xs font-bold">
                  توفير 20%
                </span>
              </button>
            </div>
          </div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
            {PLANS.map((plan) => {
              const isCurrentPlan = user?.subscription_tier === plan.tier;
              const price = billingCycle === 'yearly' 
                ? plan.priceMonthly * 12 * 0.8 
                : plan.priceMonthly;
              const Icon = plan.tier === 'vip' ? Crown : plan.tier === 'pro' ? Star : Check;

              return (
                <div
                  key={plan.tier}
                  className={`card relative ${
                    plan.popular 
                      ? 'border-2 border-gold-500 shadow-glow-lg scale-105' 
                      : ''
                  }`}
                >
                  {/* Popular Badge */}
                  {plan.popular && (
                    <div className="absolute -top-4 right-1/2 translate-x-1/2">
                      <span className="px-4 py-1.5 rounded-full bg-gradient-to-r from-gold-500 to-gold-600 text-dark-900 text-sm font-bold shadow-glow">
                        الأكثر شعبية
                      </span>
                    </div>
                  )}

                  {/* Plan Header */}
                  <div className="text-center mb-6 pt-4">
                    <div className={`w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center ${
                      plan.tier === 'vip' 
                        ? 'bg-gradient-to-br from-gold-500/20 to-gold-600/20 border border-gold-500/30'
                        : plan.tier === 'pro'
                        ? 'bg-primary-500/20'
                        : 'bg-dark-700'
                    }`}>
                      <Icon 
                        size={32} 
                        className={plan.tier === 'vip' ? 'text-gold-400' : plan.tier === 'pro' ? 'text-primary-400' : 'text-dark-400'}
                      />
                    </div>

                    <h3 className="text-2xl font-bold text-white mb-1">{plan.nameAr}</h3>
                    <p className="text-dark-400 text-sm">{plan.name}</p>

                    <div className="mt-6">
                      <div className="flex items-baseline justify-center gap-1">
                        <span className="text-4xl font-bold text-white">${price.toFixed(2)}</span>
                        {plan.price > 0 && (
                          <span className="text-dark-400">
                            /{billingCycle === 'yearly' ? 'سنة' : 'شهر'}
                          </span>
                        )}
                      </div>
                      {billingCycle === 'yearly' && plan.price > 0 && (
                        <p className="text-success-500 text-sm mt-1">
                          وفر ${(plan.priceMonthly * 12 * 0.2).toFixed(2)} سنوياً
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Features */}
                  <div className="space-y-3 mb-8">
                    {plan.features.map((feature, index) => (
                      <div key={index} className="flex items-start gap-3">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${
                          plan.tier === 'vip' 
                            ? 'bg-gold-500/20' 
                            : plan.tier === 'pro' 
                            ? 'bg-primary-500/20' 
                            : 'bg-dark-700'
                        }`}>
                          <Check 
                            size={12} 
                            className={
                              plan.tier === 'vip' 
                                ? 'text-gold-400' 
                                : plan.tier === 'pro' 
                                ? 'text-primary-400' 
                                : 'text-dark-400'
                            }
                          />
                        </div>
                        <span className="text-dark-300 text-sm">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* Limits */}
                  <div className="p-4 rounded-xl bg-dark-700/50 mb-6">
                    <h4 className="text-white font-semibold mb-3">الحدود:</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-dark-400">الإشارات:</span>
                        <span className="text-white font-medium">
                          {plan.limits.signalsPerDay === -1 ? 'غير محدود' : `${plan.limits.signalsPerDay}/يوم`}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-dark-400">الأدوات:</span>
                        <span className="text-white font-medium">{plan.limits.symbols.length} أداة</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-dark-400">الأطر الزمنية:</span>
                        <span className="text-white font-medium">{plan.limits.timeframes.length} إطار</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-dark-400">سجل الإشارات:</span>
                        <span className="text-white font-medium">
                          {plan.limits.historyDays === -1 ? 'غير محدود' : `${plan.limits.historyDays} يوم`}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* CTA Button */}
                  <button
                    onClick={() => handleSubscribe(plan.tier)}
                    disabled={isSubscribing || isCurrentPlan}
                    className={`w-full py-3 px-6 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${
                      isCurrentPlan
                        ? 'bg-dark-600 text-dark-400 cursor-not-allowed'
                        : plan.popular
                        ? 'btn-gold'
                        : plan.tier === 'vip'
                        ? 'bg-gradient-to-r from-gold-500/20 to-gold-600/20 text-gold-400 border border-gold-500/30 hover:bg-gold-500/30'
                        : 'btn-secondary'
                    }`}
                  >
                    {isSubscribing && selectedPlan === plan.tier ? (
                      <div className="spinner w-5 h-5" />
                    ) : isCurrentPlan ? (
                      <>
                        <Check size={18} />
                        <span>الباقة الحالية</span>
                      </>
                    ) : plan.tier === 'free' ? (
                      <>
                        <span>ابدأ مجاناً</span>
                        <ArrowRight size={18} />
                      </>
                    ) : (
                      <>
                        <span>اشترك الآن</span>
                        <ArrowRight size={18} />
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>

          {/* Comparison Table */}
          <div className="card mb-12">
            <h2 className="text-2xl font-bold text-white text-center mb-8">مقارنة الباقات</h2>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-dark-700">
                    <th className="text-right py-4 px-4 text-dark-400 font-medium">الميزة</th>
                    <th className="text-center py-4 px-4 text-dark-300 font-medium">مجاني</th>
                    <th className="text-center py-4 px-4 text-primary-400 font-medium">احترافي</th>
                    <th className="text-center py-4 px-4 text-gold-400 font-medium">مميز</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { feature: 'الإشارات اليومية', free: '1', pro: '∞', vip: '∞' },
                    { feature: 'أزواج العملات', free: 'الذهب فقط', pro: '6 أزواج', vip: '8+ أزواج' },
                    { feature: 'الأطر الزمنية', free: '1 ساعة', pro: '4 أطر', vip: '6 أطر' },
                    { feature: 'سجل الإشارات', free: '×', pro: '30 يوم', vip: '∞' },
                    { feature: 'مؤشرات التحليل', free: 'أساسية', pro: 'متقدمة', vip: 'كاملة' },
                    { feature: 'إشعارات Telegram', free: '×', pro: '✓', vip: '✓' },
                    { feature: 'تحليل يومي', free: '×', pro: '✓', vip: '✓' },
                    { feature: 'دعم VIP', free: '×', pro: '×', vip: '✓' },
                    { feature: 'إشارات VIP حصرية', free: '×', pro: '×', vip: '✓' },
                    { feature: 'توصيات يدوية', free: '×', pro: '×', vip: '✓' },
                  ].map((row, index) => (
                    <tr key={index} className="border-b border-dark-700/50 hover:bg-dark-700/30">
                      <td className="py-4 px-4 text-white">{row.feature}</td>
                      <td className="py-4 px-4 text-center">
                        {row.free === '×' ? (
                          <X size={18} className="text-danger-500 mx-auto" />
                        ) : row.free === '✓' ? (
                          <Check size={18} className="text-success-500 mx-auto" />
                        ) : (
                          <span className="text-dark-300">{row.free}</span>
                        )}
                      </td>
                      <td className="py-4 px-4 text-center">
                        {row.pro === '×' ? (
                          <X size={18} className="text-danger-500 mx-auto" />
                        ) : row.pro === '✓' ? (
                          <Check size={18} className="text-success-500 mx-auto" />
                        ) : (
                          <span className="text-dark-300">{row.pro}</span>
                        )}
                      </td>
                      <td className="py-4 px-4 text-center">
                        {row.vip === '×' ? (
                          <X size={18} className="text-danger-500 mx-auto" />
                        ) : row.vip === '✓' ? (
                          <Check size={18} className="text-success-500 mx-auto" />
                        ) : (
                          <span className="text-gold-400 font-medium">{row.vip}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* FAQ Section */}
          <div className="card">
            <h2 className="text-2xl font-bold text-white text-center mb-8">الأسئلة الشائعة</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-white font-semibold mb-2">هل يمكنني تغيير باقتي؟</h3>
                <p className="text-dark-400 text-sm">
                  نعم، يمكنك الترقية أو التخفيض في أي وقت. سيتم تطبيق التغييرات فوراً.
                </p>
              </div>

              <div>
                <h3 className="text-white font-semibold mb-2">ما هي طرق الدفع المتاحة؟</h3>
                <p className="text-dark-400 text-sm">
                  نقبل حالياً البطاقات الائتمانية (Visa, Mastercard) وبوابات الدفع المحلية.
                </p>
              </div>

              <div>
                <h3 className="text-white font-semibold mb-2">هل يمكنني إلغاء اشتراكي؟</h3>
                <p className="text-dark-400 text-sm">
                  نعم، يمكنك إلغاء اشتراكك في أي وقت. ستظل قادراً على استخدام الخدمة حتى نهاية فترة الاشتراك.
                </p>
              </div>

              <div>
                <h3 className="text-white font-semibold mb-2">هل هناك ضمان استرداد الأموال؟</h3>
                <p className="text-dark-400 text-sm">
                  نعم، نقدم ضمان استرداد الأموال لمدة 7 أيام لجميع الباقات المدفوعة.
                </p>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div className="text-center mt-12">
            <p className="text-dark-300 mb-4">لديك أسئلة؟ تواصل معنا</p>
            <a 
              href="mailto:support@forexai.local" 
              className="inline-flex items-center gap-2 text-primary-400 hover:text-primary-300 font-medium"
            >
              <Zap size={18} />
              <span>support@forexai.local</span>
            </a>
          </div>
        </div>
      </main>
    </div>
  );
}