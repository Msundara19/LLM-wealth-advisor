import React from 'react';
import { Link } from 'react-router-dom';

const About: React.FC = () => {
  return (
    <div>
      {/* Hero Section */}
      <section className="gradient-navy text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl lg:text-5xl font-bold mb-4">
              About Wallet Wealth LLP
            </h1>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              SEBI Registered Investment Advisor committed to helping you achieve 
              your financial goals through expert guidance and innovative technology.
            </p>
          </div>
        </div>
      </section>

      {/* About Content */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-ww-navy mb-6">Our Mission</h2>
              <p className="text-gray-600 mb-4">
                At Wallet Wealth LLP, we believe that everyone deserves access to 
                quality financial advice. Our mission is to democratize wealth 
                management by combining the expertise of SEBI-registered advisors 
                with cutting-edge AI technology.
              </p>
              <p className="text-gray-600 mb-4">
                We are committed to providing personalized, unbiased investment 
                recommendations that align with your unique financial goals, 
                risk tolerance, and life circumstances.
              </p>
              <div className="bg-gray-50 rounded-xl p-6 mt-6">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-ww-gold/20 rounded-full flex items-center justify-center">
                    <span className="text-3xl">🏆</span>
                  </div>
                  <div>
                    <p className="font-bold text-ww-navy">SEBI Registered</p>
                    <p className="text-sm text-gray-500">Registration No: INA200015440</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="card text-center">
                <div className="text-4xl font-bold text-ww-gold mb-2">500+</div>
                <p className="text-gray-600">Happy Clients</p>
              </div>
              <div className="card text-center">
                <div className="text-4xl font-bold text-ww-gold mb-2">₹50Cr+</div>
                <p className="text-gray-600">Assets Advised</p>
              </div>
              <div className="card text-center">
                <div className="text-4xl font-bold text-ww-gold mb-2">10+</div>
                <p className="text-gray-600">Years Experience</p>
              </div>
              <div className="card text-center">
                <div className="text-4xl font-bold text-ww-gold mb-2">24/7</div>
                <p className="text-gray-600">AI Support</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* AI Advisor Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-ww-navy mb-4">
              AI-Powered Financial Advisory
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our AI advisor combines machine learning with financial expertise 
              to provide instant, accurate guidance.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="card">
              <div className="w-14 h-14 bg-ww-navy rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">🧠</span>
              </div>
              <h3 className="text-xl font-bold text-ww-navy mb-3">
                Advanced AI Model
              </h3>
              <p className="text-gray-600">
                Powered by state-of-the-art language models trained on financial 
                data and investment principles specific to Indian markets.
              </p>
            </div>

            <div className="card">
              <div className="w-14 h-14 bg-ww-gold rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">📈</span>
              </div>
              <h3 className="text-xl font-bold text-ww-navy mb-3">
                Real-Time Data
              </h3>
              <p className="text-gray-600">
                Access live market data, stock prices, and portfolio analytics 
                integrated directly into your conversations.
              </p>
            </div>

            <div className="card">
              <div className="w-14 h-14 bg-ww-navy rounded-lg flex items-center justify-center mb-4">
                <span className="text-2xl">🔒</span>
              </div>
              <h3 className="text-xl font-bold text-ww-navy mb-3">
                Secure & Private
              </h3>
              <p className="text-gray-600">
                Your conversations and financial data are encrypted and never 
                shared with third parties.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-ww-navy mb-4">Our Values</h2>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            {[
              {
                icon: '🎯',
                title: 'Client First',
                desc: 'Your financial goals are our priority',
              },
              {
                icon: '📊',
                title: 'Transparency',
                desc: 'Clear fee structure, no hidden charges',
              },
              {
                icon: '🔬',
                title: 'Research-Driven',
                desc: 'Data-backed investment recommendations',
              },
              {
                icon: '🤝',
                title: 'Trust',
                desc: 'Building long-term relationships',
              },
            ].map((value, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl">{value.icon}</span>
                </div>
                <h3 className="font-bold text-ww-navy mb-2">{value.title}</h3>
                <p className="text-gray-600 text-sm">{value.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 gradient-navy text-white">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">
            Ready to Start Your Financial Journey?
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            Whether you prefer AI assistance or human expertise, we're here to help.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/chat" className="btn-gold">
              Try AI Advisor
            </Link>
            <Link to="/appointment" className="btn-outline border-white text-white hover:bg-white hover:text-ww-navy">
              Book Consultation
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
