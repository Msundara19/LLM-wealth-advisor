import React, { useState } from 'react';

interface FormData {
  name: string;
  email: string;
  phone: string;
  date: string;
  time: string;
  serviceType: string;
  message: string;
}

// EmailJS Configuration
const EMAILJS_SERVICE_ID = process.env.REACT_APP_EMAILJS_SERVICE_ID || '';
const EMAILJS_TEMPLATE_ID = process.env.REACT_APP_EMAILJS_TEMPLATE_ID || '';
const EMAILJS_PUBLIC_KEY = process.env.REACT_APP_EMAILJS_PUBLIC_KEY || '';

const Appointment: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    phone: '',
    date: '',
    time: '',
    serviceType: '',
    message: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const sendEmailNotification = async () => {
    try {
      const response = await fetch('https://api.emailjs.com/api/v1.0/email/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          service_id: EMAILJS_SERVICE_ID,
          template_id: EMAILJS_TEMPLATE_ID,
          user_id: EMAILJS_PUBLIC_KEY,
          template_params: {
            name: formData.name,
            email: formData.email,
            phone: formData.phone,
            service_type: formData.serviceType,
            preferred_date: formData.date,
            preferred_time: formData.time,
            message: formData.message || 'No additional message',
            to_email: 'sridharan@walletwealth.co.in',
          },
        }),
      });

      if (response.ok) {
        console.log('Email notification sent successfully');
      } else {
        console.log('Email notification failed, but appointment was saved');
      }
    } catch (error) {
      console.log('Email service error:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    const API_URL = process.env.REACT_APP_API_URL || '';
    try {
      // 1. Save to backend
      const response = await fetch(`${API_URL}/api/appointments/book`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
          service_type: formData.serviceType,
          preferred_date: formData.date,
          preferred_time: formData.time,
          message: formData.message,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to book appointment');
      }

      // 2. Send email notification
      await sendEmailNotification();

      console.log('Appointment booked successfully');
      setIsSubmitting(false);
      setIsSubmitted(true);
    } catch (error) {
      console.error('Error booking appointment:', error);

      // Fallback to mailto if API fails
      const subject = `Appointment Request - ${formData.serviceType}`;
      const body = `
Name: ${formData.name}
Email: ${formData.email}
Phone: ${formData.phone}
Preferred Date: ${formData.date}
Preferred Time: ${formData.time}
Service Type: ${formData.serviceType}

Message:
${formData.message}
      `;

      window.location.href = `mailto:sridharan@walletwealth.co.in?subject=${encodeURIComponent(
        subject
      )}&body=${encodeURIComponent(body)}`;

      setIsSubmitting(false);
      setIsSubmitted(true);
    }
  };

  const serviceTypes = [
    'Mutual Fund Advisory',
    'Portfolio Review',
    'Financial Planning',
    'Tax Planning',
    'Retirement Planning',
    'Goal-based Investment',
    'Insurance Planning',
    'Other',
  ];

  const timeSlots = [
    '10:00 AM',
    '11:00 AM',
    '12:00 PM',
    '2:00 PM',
    '3:00 PM',
    '4:00 PM',
    '5:00 PM',
  ];

  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  if (isSubmitted) {
    return (
      <div className="min-h-[calc(100vh-80px)] bg-gray-50 flex items-center justify-center">
        <div className="max-w-md mx-auto px-4 text-center">
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">✅</span>
            </div>
            <h2 className="text-2xl font-bold text-ww-navy mb-4">
              Appointment Request Sent!
            </h2>
            <p className="text-gray-600 mb-6">
              Thank you for your interest. Our team will contact you within 24 hours to confirm your appointment.
            </p>
            <p className="text-gray-500 text-sm mb-6">
              For urgent queries, call us at{' '}
              <a href="tel:9940116967" className="text-ww-gold font-semibold">
                9940116967
              </a>
            </p>
            <button
              onClick={() => {
                setIsSubmitted(false);
                setFormData({
                  name: '',
                  email: '',
                  phone: '',
                  date: '',
                  time: '',
                  serviceType: '',
                  message: '',
                });
              }}
              className="btn-primary"
            >
              Book Another Appointment
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-80px)] bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-ww-navy mb-4">
            Book an Appointment
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Schedule a consultation with our SEBI-registered investment advisors
            for personalized financial guidance.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <div className="bg-ww-navy text-white rounded-2xl p-6 sticky top-24">
              <h3 className="text-xl font-bold mb-6">Contact Information</h3>

              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">📍</span>
                  <div>
                    <p className="font-semibold">Office Address</p>
                    <p className="text-gray-300 text-sm">Chennai, Tamil Nadu, India</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <span className="text-2xl">📞</span>
                  <div>
                    <p className="font-semibold">Phone</p>
                    <a href="tel:9940116967" className="text-ww-gold hover:underline">
                      9940116967
                    </a>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <span className="text-2xl">📧</span>
                  <div>
                    <p className="font-semibold">Email</p>
                    <a href="mailto:sridharan@walletwealth.co.in" className="text-ww-gold hover:underline text-sm">
                      sridharan@walletwealth.co.in
                    </a>
                  </div>
                </div>

                <div className="flex items-start space-x-3">
                  <span className="text-2xl">🕐</span>
                  <div>
                    <p className="font-semibold">Business Hours</p>
                    <p className="text-gray-300 text-sm">Mon - Sat: 10:00 AM - 6:00 PM</p>
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t border-white/20">
                <p className="text-sm text-gray-300">
                  💡 Prefer instant answers? Try our{' '}
                  <a href="/chat" className="text-ww-gold hover:underline font-semibold">
                    AI Advisor
                  </a>{' '}
                  for quick financial guidance.
                </p>
              </div>
            </div>
          </div>

          <div className="lg:col-span-2">
            <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-8">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    required
                    className="input-field"
                    placeholder="Your full name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    required
                    className="input-field"
                    placeholder="Your phone number"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    className="input-field"
                    placeholder="your.email@example.com"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Service Type *
                  </label>
                  <select
                    name="serviceType"
                    value={formData.serviceType}
                    onChange={handleChange}
                    required
                    className="input-field"
                  >
                    <option value="">Select a service</option>
                    {serviceTypes.map((service) => (
                      <option key={service} value={service}>
                        {service}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Preferred Date *
                  </label>
                  <input
                    type="date"
                    name="date"
                    value={formData.date}
                    onChange={handleChange}
                    required
                    min={getMinDate()}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Preferred Time *
                  </label>
                  <select
                    name="time"
                    value={formData.time}
                    onChange={handleChange}
                    required
                    className="input-field"
                  >
                    <option value="">Select a time slot</option>
                    {timeSlots.map((time) => (
                      <option key={time} value={time}>
                        {time}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Additional Message (Optional)
                  </label>
                  <textarea
                    name="message"
                    value={formData.message}
                    onChange={handleChange}
                    rows={4}
                    className="input-field resize-none"
                    placeholder="Tell us more about what you'd like to discuss..."
                  />
                </div>
              </div>

              <div className="mt-8">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full btn-gold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isSubmitting ? (
                    <>
                      <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Sending...
                    </>
                  ) : (
                    <>📅 Request Appointment</>
                  )}
                </button>
              </div>

              <p className="text-xs text-gray-500 mt-4 text-center">
                By submitting this form, you agree to be contacted by Wallet Wealth LLP
                regarding your appointment request.
              </p>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Appointment;