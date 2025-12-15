import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <footer className="bg-ww-navy text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="col-span-1 md:col-span-2">
            <h3 className="text-2xl font-bold mb-2">WALLET WEALTH LLP</h3>
            <p className="text-ww-gold font-semibold mb-4">The Winners Choice</p>
            <p className="text-gray-300 mb-4">
              SEBI Registered Investment Advisor providing personalized financial 
              guidance and AI-powered investment recommendations.
            </p>
            <div className="flex space-x-4">
              <a href="mailto:sridharan@walletwealth.co.in" className="text-gray-300 hover:text-ww-gold transition-colors">
                📧 sridharan@walletwealth.co.in
              </a>
            </div>
            <div className="mt-2">
              <a href="tel:9940116967" className="text-gray-300 hover:text-ww-gold transition-colors">
                📞 9940116967
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-ww-gold">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-gray-300 hover:text-white transition-colors">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/chat" className="text-gray-300 hover:text-white transition-colors">
                  AI Advisor
                </Link>
              </li>
              <li>
                <Link to="/appointment" className="text-gray-300 hover:text-white transition-colors">
                  Book Appointment
                </Link>
              </li>
              <li>
                <a 
                  href="https://www.walletwealth.co.in" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  Main Website
                </a>
              </li>
            </ul>
          </div>

          {/* Services */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-ww-gold">Services</h4>
            <ul className="space-y-2">
              <li className="text-gray-300">Mutual Fund Advisory</li>
              <li className="text-gray-300">Portfolio Management</li>
              <li className="text-gray-300">Financial Planning</li>
              <li className="text-gray-300">Tax Planning</li>
              <li className="text-gray-300">Retirement Planning</li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-700 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm">
              © {new Date().getFullYear()} Wallet Wealth LLP. All rights reserved.
            </p>
            <p className="text-gray-400 text-sm mt-2 md:mt-0">
              SEBI Registered Investment Advisor | INA200015440
            </p>
          </div>
          <p className="text-gray-500 text-xs mt-4 text-center">
            Disclaimer: Mutual Fund investments are subject to market risks. 
            Please read all scheme related documents carefully before investing.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
