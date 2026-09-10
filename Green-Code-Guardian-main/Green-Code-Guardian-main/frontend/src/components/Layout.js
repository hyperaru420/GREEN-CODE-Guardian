import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import {
  LayoutDashboard, History, Award, Settings, LogOut,
  Leaf, Menu, X, ChevronRight, Activity, Sun, Moon, Trophy, Users, Bell
} from 'lucide-react';

const navItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/history', icon: History, label: 'Project History' },
  { path: '/certificates', icon: Award, label: 'Certificates' },
  { path: '/leaderboard', icon: Trophy, label: 'Leaderboard' },
  { path: '/teams', icon: Users, label: 'Teams' },
  { path: '/notifications', icon: Bell, label: 'Notifications' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="min-h-screen dark:bg-dark-950 bg-green-50 bg-grid flex">
      {/* Sidebar */}
      <aside className={`${collapsed ? 'w-16' : 'w-60'} flex-shrink-0 transition-all duration-300 dark:bg-dark-900 bg-white dark:border-r dark:border-green-900/30 border-r border-green-500/30 flex flex-col`}>
        {/* Logo */}
        <div className="h-16 flex items-center px-4 dark:border-b dark:border-green-900/30 border-b border-green-500/30 gap-3">
          <div className="w-8 h-8 rounded-lg dark:bg-green-500/10 bg-green-100 dark:border dark:border-green-500/30 border border-green-600/30 flex items-center justify-center flex-shrink-0">
            <Leaf size={16} className="dark:text-green-400 text-green-700" />
          </div>
          {!collapsed && (
            <div>
              <div className="font-bold dark:text-green-400 text-green-800 text-sm font-mono leading-none">GreenCode</div>
              <div className="dark:text-green-600 text-green-600 text-xs font-mono">Guardian</div>
            </div>
          )}
          <div className="ml-auto flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="dark:text-green-600 text-green-500 dark:hover:text-green-400 hover:text-green-700 transition-colors p-1 rounded dark:hover:bg-green-500/5 hover:bg-green-100"
              title={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
            >
              {isDark ? <Sun size={14} /> : <Moon size={14} />}
            </button>
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="dark:text-green-600 text-green-500 dark:hover:text-green-400 hover:text-green-700 transition-colors"
            >
              {collapsed ? <ChevronRight size={14} /> : <X size={14} />}
            </button>
          </div>
        </div>

        {/* Status indicator */}
        {!collapsed && (
          <div className="mx-3 mt-3 px-3 py-2 rounded-lg dark:bg-green-500/5 bg-green-50 dark:border dark:border-green-500/10 border border-green-200 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="dark:text-green-500 text-green-600 text-xs font-mono">Monitoring Active</span>
          </div>
        )}

        {/* Nav */}
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navItems.map(({ path, icon: Icon, label }) => {
            const active = location.pathname === path;
            return (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group
                  ${active
                    ? 'dark:bg-green-500/10 bg-green-100 dark:text-green-400 text-green-800 dark:border dark:border-green-500/20 border border-green-300'
                    : 'dark:text-green-700 text-green-600 dark:hover:text-green-400 hover:text-green-800 dark:hover:bg-green-500/5 hover:bg-green-50'
                  }`}
              >
                <Icon size={16} className={active ? 'dark:text-green-400 text-green-800' : 'dark:text-green-600 text-green-500 dark:group-hover:text-green-400 group-hover:text-green-700'} />
                {!collapsed && <span className="text-sm font-medium">{label}</span>}
                {active && !collapsed && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full dark:bg-green-400 bg-green-600" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* User / Logout */}
        <div className="dark:border-t dark:border-green-900/30 border-t border-green-500/30 p-3">
          {!collapsed && (
            <div className="px-3 py-2 mb-2">
              <div className="dark:text-green-300 text-green-900 text-xs font-mono truncate">{user?.email}</div>
              <div className="dark:text-green-600 text-green-500 text-xs">Administrator</div>
            </div>
          )}
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg dark:text-green-700 text-green-600 dark:hover:text-red-400 hover:text-red-600 dark:hover:bg-red-500/5 hover:bg-red-50 transition-all duration-200"
          >
            <LogOut size={16} />
            {!collapsed && <span className="text-sm">Sign Out</span>}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="min-h-full">
          {children}
        </div>
      </main>
    </div>
  );
}
