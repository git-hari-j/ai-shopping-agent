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
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (isMounted) {
      const storedToken = localStorage.getItem('token');
      if (!isAuthenticated && !storedToken) {
          router.push('/login');
      }
    }
  }, [isAuthenticated, router, isMounted]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMsg = { role: 'user', content: input };
    setMessages([...messages, newMsg]);
    setInput('');

    try {
      const res = await axios.post('http://localhost:5000/api/chat', {
        message: input,
        history: messages
      });
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    } catch (e: any) {
      if (e.response?.status === 401) {
        logout();
      }
      console.error(e);
      setMessages(prev => [...prev, { role: 'assistant', content: "Error: " + (e.response?.data?.detail || e.message) }]);
    }
  };

  // Prevent hydration mismatch by not rendering conditional logic based on client state until mounted
  if (!isMounted) {
    return null; // or a generic skeleton that matches server output effectively
  }

  // After mount, we can safely check client storage or auth state for rendering
  if (!isAuthenticated && !localStorage.getItem('token')) {
      return <div className="flex h-screen items-center justify-center bg-slate-900 text-white">Loading...</div>;
  }

  return (
    <main className="flex h-screen overflow-hidden bg-slate-900 text-slate-100">
      {/* Column 1: Chat History & Input */}
      <div className="w-1/4 bg-slate-800 border-r border-slate-700 flex flex-col">
        <div className="p-4 bg-slate-900 font-bold flex justify-between items-center border-b border-slate-700">
            <span className="flex items-center gap-2"><UserIcon size={18}/> AI Assistant</span>
            <button onClick={logout} className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-700 transition" title="Logout">
                <LogOut size={18} />
            </button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`p-3 rounded-lg text-sm ${m.role === 'user' ? 'bg-blue-600 ml-auto max-w-[85%]' : 'bg-slate-700 mr-auto max-w-[85%]'}`}>
              {m.content}
            </div>
          ))}
          {messages.length === 0 && (
            <p className="text-slate-500 text-center text-sm mt-10">Start chatting to find products...</p>
          )}
        </div>
        <div className="p-4 border-t border-slate-700">
          <input
            className="w-full bg-slate-900 p-3 rounded-lg text-white border border-slate-700 focus:border-blue-500 outline-none transition"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
            placeholder="Ask me to buy something..."
          />
        </div>
      </div>

      {/* Column 2: Results / Response */}
      <div className="w-2/4 bg-slate-900 p-6 overflow-y-auto border-r border-slate-700">
        <h2 className="text-2xl font-bold mb-6">Results</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
          {/* Example static products - connect to agent structured output in future */}
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="group bg-slate-800 p-4 rounded-xl border border-slate-700 hover:border-blue-500 cursor-pointer transition-all hover:shadow-lg hover:shadow-blue-900/20" onClick={() => setSelectedProduct({id: i, name: `Demo Product ${i}`, price: 99.99})}>
              <div className="h-48 bg-slate-700 mb-4 rounded-lg flex items-center justify-center text-slate-500 group-hover:bg-slate-600 transition">Product Image</div>
              <h3 className="font-bold text-lg mb-1">Demo Product {i}</h3>
              <div className="flex justify-between items-center">
                <p className="text-blue-400 font-mono font-bold">$99.99</p>
                <span className="text-xs text-slate-500 bg-slate-900 px-2 py-1 rounded">In Stock</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Column 3: Details */}
      <div className="w-1/4 bg-slate-800 p-6 overflow-y-auto">
        <h2 className="text-xl font-bold mb-6">Details</h2>
        {selectedProduct ? (
          <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-300">
            <div className="h-56 bg-slate-700 rounded-xl flex items-center justify-center text-slate-500">
                Large Image
            </div>
            <div>
                <h3 className="text-2xl font-bold mb-2">{selectedProduct.name}</h3>
                <p className="text-3xl text-blue-400 font-bold">${selectedProduct.price}</p>
            </div>

            <div className="space-y-2">
                <h4 className="font-semibold text-slate-300">Description</h4>
                <p className="text-slate-400 text-sm leading-relaxed">
                  This is a high-quality product selected by your AI assistant.
                  It features state-of-the-art specs and integrates perfectly with your workflow.
                </p>
            </div>

            <div className="pt-4 space-y-3">
                <button className="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded-lg font-bold text-white transition shadow-lg shadow-blue-900/20 flex items-center justify-center gap-2">
                    Add to Cart
                </button>
                <button className="w-full bg-slate-700 hover:bg-slate-600 py-3 rounded-lg font-semibold text-white transition">
                    Save to Favorites
                </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-4">
            <div className="w-16 h-16 rounded-full bg-slate-700/50 flex items-center justify-center">
                <span className="text-2xl">?</span>
            </div>
            <p className="text-center italic">Select a product to view details.</p>
          </div>
        )}
      </div>
    </main>
  )
}
