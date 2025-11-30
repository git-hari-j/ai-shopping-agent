'use client';
import { useState, useEffect } from 'react';
import { useAuth } from '@/components/AuthProvider';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { LogOut, User as UserIcon } from 'lucide-react';

export default function Home() {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [input, setInput] = useState('');
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const { isAuthenticated, logout, token } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Protect route
    if (!isAuthenticated && !localStorage.getItem('token')) {
        // Allow brief render to avoid hydration mismatch or wait for context
        // But ideally redirect.
        router.push('/login');
    }
  }, [isAuthenticated, router]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMsg = { role: 'user', content: input };
    setMessages([...messages, newMsg]);
    setInput('');

    try {
      // Token is already set in axios default headers by AuthProvider
      const res = await axios.post('http://localhost:5000/api/chat', {
        message: input,
        history: messages
      });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    } catch (e: any) {
      if (e.response?.status === 401) {
        logout(); // Token expired
      }
      console.error(e);
      setMessages(prev => [...prev, { role: 'assistant', content: "Error: " + (e.response?.data?.detail || e.message) }]);
    }
  };

  if (!isAuthenticated && typeof window !== 'undefined' && !localStorage.getItem('token')) {
      return <div className="flex h-screen items-center justify-center bg-slate-900 text-white">Loading...</div>;
  }

  return (
    <main className="flex h-screen overflow-hidden">
      {/* Column 1: Chat History & Input */}
      <div className="w-1/4 bg-slate-800 border-r border-slate-700 flex flex-col">
        <div className="p-4 bg-slate-900 font-bold flex justify-between items-center">
            <span>AI Assistant</span>
            <button onClick={logout} className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-700">
                <LogOut size={18} />
            </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`p-3 rounded-lg ${m.role === 'user' ? 'bg-blue-600 ml-auto max-w-[80%]' : 'bg-slate-700 mr-auto max-w-[80%]'}`}>
              {m.content}
            </div>
          ))}
        </div>
        <div className="p-4 border-t border-slate-700">
          <input
            className="w-full bg-slate-900 p-2 rounded text-white border border-slate-700 focus:border-blue-500 outline-none"
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
        {/* Placeholder for results - would populate based on agent response if structured */}
        <div className="grid grid-cols-2 gap-4">
          {/* Example static products for UI demo - replace with dynamic data later */}
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="bg-slate-800 p-4 rounded-xl border border-slate-700 hover:border-blue-500 cursor-pointer transition" onClick={() => setSelectedProduct({id: i, name: `Demo Product ${i}`, price: 99.99})}>
              <div className="h-40 bg-slate-700 mb-3 rounded-lg flex items-center justify-center text-slate-500">Image</div>
              <h3 className="font-bold text-lg">Demo Product {i}</h3>
              <p className="text-blue-400 font-mono">$99.99</p>
            </div>
          ))}
        </div>
      </div>

      {/* Column 3: Details */}
      <div className="w-1/4 bg-slate-800 border-l border-slate-700 p-6 overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Details</h2>
        {selectedProduct ? (
          <div className="space-y-4">
            <div className="h-48 bg-slate-700 rounded-xl mb-4"></div>
            <h3 className="text-2xl font-bold">{selectedProduct.name}</h3>
            <p className="text-3xl text-blue-400 font-bold">${selectedProduct.price}</p>
            <p className="text-slate-400 leading-relaxed">
              This is a high-quality product selected by your AI assistant.
              It features state-of-the-art specs and integrates perfectly with your workflow.
            </p>
            <div className="pt-4 space-y-2">
                <button className="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded-lg font-bold text-white transition shadow-lg shadow-blue-900/20">
                    Add to Cart
                </button>
                <button className="w-full bg-slate-700 hover:bg-slate-600 py-3 rounded-lg font-semibold text-white transition">
                    Save to Favorites
                </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 text-slate-500">
            <p className="text-center italic">Select a product to view details.</p>
          </div>
        )}
      </div>
    </main>
  )
}
