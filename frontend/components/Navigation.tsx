'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  LineChart, 
  Calculator, 
  CreditCard, 
  LogOut, 
  User,
  Menu,
  X,
  Crown
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  { label: 'لوحة التحكم', href: '/dashboard', icon: <LayoutDashboard size={20} /> },
  { label: 'توليد الإشارات', href: '/signals', icon: <LineChart size={20} /> },
  { label: 'حاسبة اللوت', href: '/calculator', icon: <Calculator size={20} /> },
  { label: 'الاشتراكات', href: '/pricing', icon: <CreditCard size={20} /> },
];

export default function Navigation() {
  const pathname = usePathname();
  const { user, logout, isAuthenticated } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <nav className="fixed top-0 right-0 left-0 z-50 bg-dark-900/95 backdrop-blur-xl border-b border-dark-700">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gold-500 to-gold-600 flex items-center justify-center">
              <Crown className="text-dark-900" size={24} />
            </div>
            <div>
              <h1 className="text-lg font-bold gradient-text">Forex AI Signals</h1>
              <p className="text-xs text-dark-400">إشارات الذكاء الاصطناعي</p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-2">
            {isAuthenticated ? (
              <>
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`nav-link ${pathname === item.href ? 'nav-link-active' : ''}`}
                  >
                    {item.icon}
                    <span>{item.label}</span>
                  </Link>
                ))}
              </>
            ) : null}
          </div>

          {/* User Section */}
          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <div className="hidden md:flex items-center gap-4">
                {user?.subscription_tier === 'vip' && (
                  <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r from-gold-500/20 to-gold-600/20 border border-gold-500/30">
                    <Crown size={16} className="text-gold-400" />
                    <span className="text-sm font-semibold text-gold-400">VIP</span>
                  </div>
                )}
                
                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-dark-800 border border-dark-700">
                  <User size={18} className="text-primary-400" />
                  <span className="text-sm font-medium">{user?.full_name}</span>
                </div>

                <button
                  onClick={logout}
                  className="p-2 rounded-xl text-dark-400 hover:text-white hover:bg-dark-700 transition-all"
                  title="تسجيل الخروج"
                >
                  <LogOut size={20} />
                </button>
              </div>
            ) : (
              <div className="hidden md:flex items-center gap-3">
                <Link href="/login" className="btn-secondary text-sm">
                  تسجيل الدخول
                </Link>
                <Link href="/register" className="btn-primary text-sm">
                  إنشاء حساب
                </Link>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-xl text-dark-400 hover:text-white hover:bg-dark-700 transition-all"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-dark-700">
            <div className="flex flex-col gap-2">
              {isAuthenticated ? (
                <>
                  {navItems.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className={`nav-link ${pathname === item.href ? 'nav-link-active' : ''}`}
                    >
                      {item.icon}
                      <span>{item.label}</span>
                    </Link>
                  ))}
                  <button
                    onClick={() => {
                      logout();
                      setMobileMenuOpen(false);
                    }}
                    className="nav-link text-danger-500"
                  >
                    <LogOut size={20} />
                    <span>تسجيل الخروج</span>
                  </button>
                </>
              ) : (
                <>
                  <Link href="/login" onClick={() => setMobileMenuOpen(false)} className="nav-link">
                    تسجيل الدخول
                  </Link>
                  <Link href="/register" onClick={() => setMobileMenuOpen(false)} className="nav-link">
                    إنشاء حساب
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}