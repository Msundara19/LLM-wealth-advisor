import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div>
      {/* Hero Section */}
      <section className="gradient-navy text-white py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl lg:text-5xl font-bold leading-tight mb-6">
                Your happiness depends on the smile of the faces who depend on you.
                <span className="text-ww-gold"> Create wealth that lasts.</span>
              </h1>
              <p className="text-xl text-gray-300 mb-8">
                Get personalized financial advice powered by AI. Our intelligent advisor 
                helps you make informed investment decisions tailored to your goals.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/chat" className="btn-gold text-center">
                  🤖 Talk to AI Advisor
                </Link>
                <Link to="/appointment" className="btn-outline border-white text-white hover:bg-white hover:text-ww-navy text-center">
                  📅 Book Consultation
                </Link>
              </div>
            </div>
            <div className="hidden lg:block">
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
                <div className="text-center">
                  <div className="text-6xl mb-4">💼</div>
                  <h3 className="text-2xl font-bold mb-2">SEBI Registered</h3>
                  <p className="text-gray-300">Investment Advisor</p>
                  <p className="text-ww-gold font-semibold mt-2">INA200015440</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-ww-navy mb-4">
              Why Choose Our AI Advisor?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Combining the expertise of SEBI-registered advisors with cutting-edge AI technology
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="card text-center hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-ww-navy/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-3xl">🎯</span>
              </div>
              <h3 className="text-xl font-bold text-ww-navy mb-3">Personalized Advice</h3>
              <p className="text-gray-600">
                Get investment recommendations tailored to your risk profile, 
                goals, and financial situation.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="card text-center hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-ww-gold/20 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-3xl">⚡</span>
              </div>
              <h3 className="text-xl font-bold text-ww-navy mb-3">Instant Responses</h3>
              <p className="text-gray-600">
                No waiting for appointments. Get answers to your financial 
                questions instantly, 24/7.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="card text-center hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-ww-navy/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-3xl">📊</span>
              </div>
              <h3 className="text-xl font-bold text-ww-navy mb-3">Market Insights</h3>
              <p className="text-gray-600">
                Access real-time market data, stock prices, and portfolio 
                analysis at your fingertips.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-ww-navy mb-4">
              Our Services
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: '📈', title: 'Mutual Funds', desc: 'Expert fund selection and SIP planning' },
              { icon: '💰', title: 'Wealth Management', desc: 'Comprehensive portfolio management' },
              { icon: '🏦', title: 'Tax Planning', desc: 'Optimize your tax savings legally' },
              { icon: '🎯', title: 'Goal Planning', desc: 'Achieve your financial milestones' },
            ].map((service, index) => (
              <div key={index} className="bg-white rounded-xl p-6 shadow-md hover:shadow-lg transition-shadow border-t-4 border-ww-gold">
                <span className="text-4xl">{service.icon}</span>
                <h3 className="text-lg font-bold text-ww-navy mt-4 mb-2">{service.title}</h3>
                <p className="text-gray-600 text-sm">{service.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 gradient-navy text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl lg:text-4xl font-bold mb-6">
            Ready to Start Your Investment Journey?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Talk to our AI advisor now or schedule a consultation with our experts.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/chat" className="btn-gold">
              Start AI Chat Now
            </Link>
            <Link to="/appointment" className="btn-outline border-white text-white hover:bg-white hover:text-ww-navy">
              Schedule Human Consultation
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
