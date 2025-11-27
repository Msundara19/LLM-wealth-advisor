import React, { useState } from 'react';

interface Holding {
  id: string;
  symbol: string;
  name: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  value: number;
  change: number;
  changePercent: number;
}

const Portfolio: React.FC = () => {
  const [holdings] = useState<Holding[]>([
    { id: '1', symbol: 'AAPL', name: 'Apple Inc.', quantity: 50, avgPrice: 150, currentPrice: 175.5, value: 8775, change: 1275, changePercent: 17 },
    { id: '2', symbol: 'GOOGL', name: 'Alphabet Inc.', quantity: 20, avgPrice: 2800, currentPrice: 2950, value: 59000, change: 3000, changePercent: 5.36 },
  ]);

  const totalValue = holdings.reduce((sum, h) => sum + h.value, 0);
  const totalChange = holdings.reduce((sum, h) => sum + h.change, 0);

  return (
    <div className="h-full overflow-y-auto p-6 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-2xl font-bold mb-6">Portfolio Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Value</p>
              <p className="text-3xl font-bold">${totalValue.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Gain/Loss</p>
              <p className={`text-3xl font-bold ${totalChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {totalChange >= 0 ? '+' : ''}${totalChange.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold">Holdings</h3>
          </div>
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Value</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Gain/Loss</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {holdings.map((h) => (
                <tr key={h.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4"><span className="font-semibold">{h.symbol}</span></td>
                  <td className="px-6 py-4 text-sm text-gray-600">{h.name}</td>
                  <td className="px-6 py-4 text-right font-medium">${h.value.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right">
                    <div className={h.change >= 0 ? 'text-green-600' : 'text-red-600'}>
                      {h.change >= 0 ? '+' : ''}${h.change.toFixed(2)} ({h.changePercent.toFixed(2)}%)
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Portfolio;
