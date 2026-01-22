'use client';
import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/components/AuthProvider';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { LogOut, User as UserIcon, Send, Sparkles, ShoppingBag, Heart, Search } from 'lucide-react';

export default function Home() {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [input, setInput] = useState('');
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { isAuthenticated, logout, token } = useAuth();
  const router = useRouter();
  const [isMounted, setIsMounted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (isMounted) {
      const storedToken = localStorage.getItem('token');
      if (!isAuthenticated && !storedToken) {
          router.push('/login');
      }
    }
  }, [isAuthenticated, router, isMounted]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;
    const newMsg = { role: 'user', content: input };
    setMessages([...messages, newMsg]);
    setInput('');
    setIsLoading(true);

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
    } finally {
        setIsLoading(false);
    }
  };

  if (!isMounted) return null;

  if (!isAuthenticated && !localStorage.getItem('token')) {
      return (
        <div className="flex h-screen items-center justify-center bg-slate-950 text-white">
            <div className="animate-pulse flex flex-col items-center gap-4">
                <div className="w-12 h-12 rounded-full border-4 border-blue-500 border-t-transparent animate-spin"></div>
                <p className="text-blue-200 font-medium tracking-wide">Initializing Deep Agent...</p>
            </div>
        </div>
      );
  }

  return (
    <main className="flex h-screen overflow-hidden text-slate-100 bg-slate-950 relative selection:bg-blue-500/30">
      {/* Background Ambient Glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[-20%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-blue-600/10 blur-[120px]"></div>
          <div className="absolute bottom-[-20%] right-[-10%] w-[50vw] h-[50vw] rounded-full bg-indigo-600/10 blur-[120px]"></div>
      </div>

      {/* Column 1: Chat Interface */}
      <div className="w-1/4 glass border-r border-white/5 flex flex-col z-10 relative">
        <div className="p-5 border-b border-white/5 flex justify-between items-center bg-white/5 backdrop-blur-xl">
            <span className="flex items-center gap-3 font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">
                <Sparkles size={20} className="text-blue-400" />
                Deep Agent
            </span>
            <button onClick={logout} className="text-slate-400 hover:text-white p-2 rounded-full hover:bg-white/10 transition-all duration-300" title="Logout">
                <LogOut size={18} />
            </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth custom-scrollbar">
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed shadow-lg backdrop-blur-sm ${
                    m.role === 'user'
                    ? 'bg-gradient-to-br from-blue-600 to-indigo-600 text-white rounded-tr-none'
                    : 'bg-white/10 border border-white/5 text-slate-200 rounded-tl-none'
                }`}>
                    {m.content}
                </div>
            </div>
          ))}

          {isLoading && (
              <div className="flex justify-start">
                  <div className="bg-white/5 border border-white/5 p-4 rounded-2xl rounded-tl-none flex items-center gap-2">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-0"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-150"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-300"></div>
                  </div>
              </div>
          )}

          <div ref={messagesEndRef} />

          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-4 opacity-50">
                <Sparkles size={48} />
                <p className="text-sm">How can I help you shop today?</p>
            </div>
          )}
        </div>

        <div className="p-4 bg-white/5 border-t border-white/5 backdrop-blur-xl">
          <div className="relative">
            <input
                className="w-full glass-input pr-12 text-sm shadow-inner"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendMessage()}
                placeholder="Ask me to find products..."
                disabled={isLoading}
            />
            <button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg text-slate-400 hover:text-blue-400 hover:bg-white/10 transition-all disabled:opacity-50 disabled:hover:bg-transparent"
            >
                <Send size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Column 2: Product Grid */}
      <div className="w-2/4 p-8 overflow-y-auto relative z-0 custom-scrollbar">
        <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                Discover
            </h2>
            <div className="flex gap-2">
                <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-slate-400">Electronics</span>
                <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-slate-400">Laptops</span>
            </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map(i => (
            <div
                key={i}
                onClick={() => setSelectedProduct({id: i, name: `MacBook Pro ${i}`, price: 1299.00 + (i*100)})}
                className="group glass-card cursor-pointer relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="p-2 bg-black/50 backdrop-blur-md rounded-full text-white hover:text-red-400 transition">
                      <Heart size={16} />
                  </div>
              </div>

              <div className="h-48 mb-6 rounded-xl bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center group-hover:scale-105 transition-transform duration-500">
                  <ShoppingBag className="text-slate-600 group-hover:text-blue-500/50 transition duration-500" size={48} />
              </div>

              <div className="space-y-2">
                  <h3 className="font-bold text-lg text-slate-100 group-hover:text-blue-400 transition-colors">MacBook Pro M{i}</h3>
                  <div className="flex justify-between items-end">
                    <div>
                        <p className="text-slate-400 text-xs mb-1">Apple Inc.</p>
                        <p className="text-xl font-bold text-white">${1299.00 + (i*100)}</p>
                    </div>
                    <button className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-xs font-semibold transition text-slate-300">
                        View
                    </button>
                  </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Column 3: Product Details */}
      <div className="w-1/4 glass border-l border-white/5 p-8 overflow-y-auto z-10 custom-scrollbar">
        {selectedProduct ? (
          <div className="space-y-8 animate-in fade-in slide-in-from-right-8 duration-500">
            <div className="relative">
                <div className="aspect-square rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 flex items-center justify-center shadow-2xl border border-white/5">
                    <ShoppingBag className="text-slate-700" size={64} />
                </div>
                <div className="absolute -bottom-4 -right-4 bg-blue-600 text-white px-4 py-2 rounded-xl font-bold shadow-lg shadow-blue-600/30">
                    ${selectedProduct.price}
                </div>
            </div>

            <div>
                <h3 className="text-3xl font-bold text-white mb-2 leading-tight">{selectedProduct.name}</h3>
                <div className="flex gap-2 mb-4">
                    {[1,2,3,4,5].map(star => (
                        <span key={star} className="text-yellow-500 text-sm">★</span>
                    ))}
                    <span className="text-slate-500 text-xs ml-2">(128 reviews)</span>
                </div>
                <p className="text-slate-400 leading-relaxed font-light">
                  Experience the power of the new {selectedProduct.name}.
                  Featuring a stunning retina display and all-day battery life, it's perfect for pros.
                </p>
            </div>

            <div className="space-y-3 pt-4">
                <button className="btn-primary w-full flex items-center justify-center gap-2 group">
                    <ShoppingBag size={18} className="group-hover:animate-bounce" />
                    Add to Cart
                </button>
                <button className="btn-secondary w-full">
                    Save to Wishlist
                </button>
            </div>

            <div className="pt-8 border-t border-white/5">
                <h4 className="text-sm font-semibold text-slate-300 mb-4">Specs</h4>
                <div className="space-y-2 text-sm text-slate-400">
                    <div className="flex justify-between">
                        <span>Processor</span>
                        <span className="text-slate-200">M{selectedProduct.id} Pro</span>
                    </div>
                    <div className="flex justify-between">
                        <span>Memory</span>
                        <span className="text-slate-200">16 GB</span>
                    </div>
                    <div className="flex justify-between">
                        <span>Storage</span>
                        <span className="text-slate-200">512 GB SSD</span>
                    </div>
                </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-6">
            <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center border border-white/10 shadow-inner">
                <Search size={32} className="opacity-50" />
            </div>
            <div className="text-center space-y-2">
                <p className="font-medium text-slate-300">No Product Selected</p>
                <p className="text-xs max-w-[200px] mx-auto opacity-60">Click on a product card to view detailed specifications and purchasing options.</p>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
