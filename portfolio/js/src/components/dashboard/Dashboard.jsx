import {
    BarChart3,
    Bell,
    Bookmark,
    LogOut,
    Menu,
    Settings,
    TrendingUp,
    User,
    Wallet,
    X
} from 'lucide-react';
import React, { useState } from 'react';
import toast from 'react-hot-toast';
import { useAuth } from '../../contexts/AuthContext';

const Dashboard = () => {
    const { user, logout } = useAuth();
    const { profile } = useAuth();
    const [sidebarOpen, setSidebarOpen] = useState(true);

    const handleLogout = async () => {
        try {
            await logout();
            toast.success('Logged out successfully');
        } catch (error) {
            toast.error('Logout failed');
        }
    };

    const toggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };

    return (
        <div className="min-h-screen gradient-bg flex">
            {/* Mobile sidebar overlay */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
                    onClick={toggleSidebar}
                />
            )}

            {/* Left Sidebar */}
            <div className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 bg-dark-900 border-r border-dark-700 
        transform transition-transform duration-300 ease-in-out lg:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
                {/* Sidebar Header */}
                <div className="flex items-center justify-between p-6 border-b border-dark-700">
                    <h1 className="text-2xl font-bold text-gradient">Portfolia</h1>
                    <button
                        onClick={toggleSidebar}
                        className="lg:hidden p-2 rounded-lg hover:bg-dark-800 transition-colors"
                    >
                        <X size={20} className="text-gray-400" />
                    </button>
                </div>

                {/* User Profile Section */}
                <div className="p-6 border-b border-dark-700">
                    <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center">
                            <User size={20} className="text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-100 truncate">
                                {profile?.first_name} {profile?.last_name}
                            </p>
                            <p className="text-xs text-gray-400 truncate">
                                @{user?.username}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Navigation Menu */}
                <nav className="flex-1 p-4 space-y-2">
                    <a
                        href="#dashboard"
                        className="flex items-center space-x-3 px-3 py-2 rounded-lg bg-primary-600/20 text-primary-400 hover:bg-primary-600/30 transition-colors"
                    >
                        <BarChart3 size={18} />
                        <span>Dashboard</span>
                    </a>

                    <a
                        href="#portfolio"
                        className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-dark-800 transition-colors"
                    >
                        <TrendingUp size={18} />
                        <span>Portfolio</span>
                    </a>

                    <a
                        href="#assets"
                        className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-dark-800 transition-colors"
                    >
                        <Wallet size={18} />
                        <span>Assets</span>
                    </a>
                    <a
                        href="/watchlist"
                        className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-dark-800 transition-colors"
                    >
                        <Bookmark size={18} />
                        <span>Watchlist</span>
                    </a>
                    <a
                        href="#settings"
                        className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-300 hover:bg-dark-800 transition-colors"
                    >
                        <Settings size={18} />
                        <span>Settings</span>
                    </a>
                </nav>

                {/* Logout Button */}
                <div className="p-4 border-t border-dark-700">
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center justify-center space-x-3 px-4 py-2 rounded-lg bg-danger-600/20 text-danger-400 hover:bg-danger-600/30 transition-colors"
                    >
                        <LogOut size={18} />
                        <span>Logout</span>
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col">
                {/* Top Header */}
                <header className="bg-dark-900/80 backdrop-blur-sm border-b border-dark-700 px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <button
                                onClick={toggleSidebar}
                                className="lg:hidden p-2 rounded-lg hover:bg-dark-800 transition-colors"
                            >
                                <Menu size={20} className="text-gray-400" />
                            </button>
                            <h2 className="text-xl font-semibold text-gray-100">Dashboard</h2>
                        </div>

                        <div className="flex items-center space-x-4">
                            <button className="p-2 rounded-lg hover:bg-dark-800 transition-colors relative">
                                <Bell size={20} className="text-gray-400" />
                                <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full"></span>
                            </button>

                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                                    <User size={16} className="text-white" />
                                </div>
                                <span className="text-sm text-gray-300 hidden md:block">
                                    {profile?.first_name} {profile?.last_name}
                                </span>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Main Dashboard Content */}
                <main className="flex-1 p-6 overflow-auto">
                    <div className="max-w-7xl mx-auto">
                        {/* Welcome Section */}
                        <div className="mb-8">
                            <h1 className="text-3xl font-bold text-gray-100 mb-2">
                                Welcome back, {profile?.first_name}! 👋
                            </h1>
                            <p className="text-gray-400">
                                Here's what's happening with your portfolio today.
                            </p>
                        </div>

                        {/* Stats Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                            <div className="card p-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-gray-400">Total Value</p>
                                        <p className="text-2xl font-bold text-gray-100">$125,430.50</p>
                                    </div>
                                    <div className="w-12 h-12 bg-primary-600/20 rounded-lg flex items-center justify-center">
                                        <TrendingUp size={24} className="text-primary-400" />
                                    </div>
                                </div>
                                <div className="mt-4 flex items-center text-sm">
                                    <span className="text-success-400">+2.5%</span>
                                    <span className="text-gray-400 ml-2">vs yesterday</span>
                                </div>
                            </div>

                            <div className="card p-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-gray-400">Daily P&L</p>
                                        <p className="text-2xl font-bold text-success-400">+$3,245.80</p>
                                    </div>
                                    <div className="w-12 h-12 bg-success-600/20 rounded-lg flex items-center justify-center">
                                        <BarChart3 size={24} className="text-success-400" />
                                    </div>
                                </div>
                                <div className="mt-4 flex items-center text-sm">
                                    <span className="text-success-400">+2.7%</span>
                                    <span className="text-gray-400 ml-2">vs yesterday</span>
                                </div>
                            </div>

                            <div className="card p-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-gray-400">Holdings</p>
                                        <p className="text-2xl font-bold text-gray-100">24</p>
                                    </div>
                                    <div className="w-12 h-12 bg-warning-600/20 rounded-lg flex items-center justify-center">
                                        <Wallet size={24} className="text-warning-400" />
                                    </div>
                                </div>
                                <div className="mt-4 flex items-center text-sm">
                                    <span className="text-gray-400">Active positions</span>
                                </div>
                            </div>

                            <div className="card p-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-gray-400">Cash</p>
                                        <p className="text-2xl font-bold text-gray-100">$15,230.45</p>
                                    </div>
                                    <div className="w-12 h-12 bg-gray-600/20 rounded-lg flex items-center justify-center">
                                        <Wallet size={24} className="text-gray-400" />
                                    </div>
                                </div>
                                <div className="mt-4 flex items-center text-sm">
                                    <span className="text-gray-400">Available for trading</span>
                                </div>
                            </div>
                        </div>

                        {/* Portfolio Overview */}
                        <div className="card p-6">
                            <h3 className="text-lg font-semibold text-gray-100 mb-4">Portfolio Overview</h3>
                            <p className="text-gray-400">
                                This is where we'll build the TradingView-like interface with charts,
                                portfolio breakdown, and real-time market data.
                            </p>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
};

export default Dashboard;
