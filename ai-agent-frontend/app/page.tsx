'use client';
import { useState } from 'react';

export default function Home() {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [input, setInput] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMsg = { role: 'user', content: input };
    setMessages([...messages, newMsg]);
    setInput('');

    try {
      const res = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer MOCK_TOKEN' }, // Needs real auth
        body: JSON.stringify({ message: input, history: messages })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <main className="flex h-screen overflow-hidden">
      {/* Column 1: Chat History & Input */}
      <div className="w-1/4 bg-slate-800 border-r border-slate-700 flex flex-col">
        <div className="p-4 bg-slate-900 font-bold">AI Assistant</div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`p-3 rounded-lg ${m.role === 'user' ? 'bg-blue-600 ml-auto' : 'bg-slate-700 mr-auto'}`}>
              {m.content}
            </div>
          ))}
        </div>
        <div className="p-4 border-t border-slate-700">
          <input
            className="w-full bg-slate-900 p-2 rounded text-white"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
            placeholder="Ask me to buy something..."
          />
        </div>
      </div>

      {/* Column 2: Results / Response */}
      <div className="w-2/4 bg-slate-900 p-6 overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">Results</h2>
        {/* Mock Product Grid - Real implementation would parse structured data from agent */}
        <div className="grid grid-cols-2 gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-slate-800 p-4 rounded hover:bg-slate-700 cursor-pointer" onClick={() => setSelectedProduct({id: i, name: `Product ${i}`})}>
              <div className="h-40 bg-slate-600 mb-2 rounded"></div>
              <h3 className="font-bold">Demo Product {i}</h3>
              <p className="text-blue-400">$99.99</p>
            </div>
          ))}
        </div>
      </div>

      {/* Column 3: Details */}
      <div className="w-1/4 bg-slate-800 border-l border-slate-700 p-6">
        <h2 className="text-xl font-bold mb-4">Details</h2>
        {selectedProduct ? (
          <div>
            <h3 className="text-2xl mb-2">{selectedProduct.name}</h3>
            <p className="text-slate-400">Detailed specifications and AI analysis would appear here.</p>
            <button className="mt-4 w-full bg-green-600 py-2 rounded font-bold">Add to Cart</button>
          </div>
        ) : (
          <p className="text-slate-500 italic">Select a product to view details.</p>
        )}
      </div>
    </main>
  )
}
