import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="flex flex-col">
              <span className="text-2xl font-bold text-ww-navy">WALLET WEALTH</span>
              <span className="text-xs text-ww-gold font-semibold tracking-wider">LLP - The Winners Choice</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              to="/"
              className={`font-medium transition-colors ${
                isActive('/') ? 'text-ww-gold' : 'text-gray-700 hover:text-ww-navy'
              }`}
            >
              HOME
            </Link>
            <Link
              to="/chat"
              className={`font-medium transition-colors ${
                isActive('/chat') ? 'text-ww-gold' : 'text-gray-700 hover:text-ww-navy'
              }`}
            >
              AI ADVISOR
            </Link>
            <Link
              to="/about"
              className={`font-medium transition-colors ${
                isActive('/about') ? 'text-ww-gold' : 'text-gray-700 hover:text-ww-navy'
              }`}
            >
              ABOUT
            </Link>
            <a
              href="https://www.walletwealth.co.in"
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-gray-700 hover:text-ww-navy transition-colors"
            >
              MAIN WEBSITE
            </a>
          </div>

          {/* CTA Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <a
              href="tel:9940116967"
              className="text-ww-navy font-medium hover:text-ww-gold transition-colors"
            >
              📞 9940116967
            </a>
            <Link to="/appointment" className="btn-gold">
              Book Appointment
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
          >
            <svg
              className="w-6 h-6 text-ww-navy"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t">
            <div className="flex flex-col space-y-4">
              <Link
                to="/"
                className={`font-medium px-4 py-2 rounded-lg ${
                  isActive('/') ? 'bg-ww-navy text-white' : 'text-gray-700'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                HOME
              </Link>
              <Link
                to="/chat"
                className={`font-medium px-4 py-2 rounded-lg ${
                  isActive('/chat') ? 'bg-ww-navy text-white' : 'text-gray-700'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                AI ADVISOR
              </Link>
              <Link
                to="/about"
                className={`font-medium px-4 py-2 rounded-lg ${
                  isActive('/about') ? 'bg-ww-navy text-white' : 'text-gray-700'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                ABOUT
              </Link>
              <Link
                to="/appointment"
                className="btn-gold text-center"
                onClick={() => setIsMenuOpen(false)}
              >
                Book Appointment
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
