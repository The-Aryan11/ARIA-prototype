'use client';

import { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  User,
  ShoppingBag,
  MessageCircle,
  Sparkles,
  Zap,
  Shirt,
  TrendingUp,
  Palette
} from 'lucide-react';
import axios from 'axios';

// Point this to your live backend
const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'https://aria-api-1o1d.onrender.com';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface SessionInfo {
  channels_used: string[];
  channel_switches: number;
  cart_count: number;
  has_style_dna: boolean;
}

interface Product {
  id: string;
  name: string;
  brand: string;
  price: number;
  description: string;
  image: string;
}

const sampleProducts: Product[] = [
  {
    id: 'LP001',
    name: 'Louis Philippe Luxury Shirt',
    brand: 'Louis Philippe',
    price: 2499,
    description: 'Wrinkle-free cotton, perfect for boardroom meetings.',
    image: 'https://via.placeholder.com/100x120/0f172a/ffffff?text=LP'
  },
  {
    id: 'VH001',
    name: 'Van Heusen Slim Blazer',
    brand: 'Van Heusen',
    price: 5999,
    description: 'Modern cut blazer in navy blue. Essential formal wear.',
    image: 'https://via.placeholder.com/100x120/1e293b/ffffff?text=VH'
  },
  {
    id: 'AS001',
    name: 'Allen Solly Polo',
    brand: 'Allen Solly',
    price: 1299,
    description: 'Signature color-block polo for weekend vibes.',
    image: 'https://via.placeholder.com/100x120/334155/ffffff?text=AS'
  },
  {
    id: 'PAN001',
    name: 'Pantaloons Festive Set',
    brand: 'Pantaloons',
    price: 2999,
    description: 'Embroidered kurta set for wedding season.',
    image: 'https://via.placeholder.com/100x120/475569/ffffff?text=Ethnic'
  }
];

function getSuggestedProductsForMessage(content: string): Product[] {
  const text = content.toLowerCase();
  if (text.includes('interview') || text.includes('formal')) return sampleProducts.filter(p => p.id === 'LP001');
  if (text.includes('blazer') || text.includes('meeting')) return sampleProducts.filter(p => p.id === 'VH001');
  if (text.includes('party') || text.includes('casual')) return sampleProducts.filter(p => p.id === 'AS001');
  if (text.includes('wedding') || text.includes('festive')) return sampleProducts.filter(p => p.id === 'PAN001');
  if (text.includes('trending')) return sampleProducts;
  return [];
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        "Hello! I'm ARIA, your ABFRL AI Stylist. ✨\n\nI can seamlessly help you across WhatsApp, In-Store, and here.\n\n• Looking for an outfit?\n• Need a Style DNA analysis?\n• Want to check trending items?\n\nHow can I help you look your best today?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionInfo, setSessionInfo] = useState<SessionInfo | null>(null);
  const [userId] = useState(() => `web-${Date.now()}`);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/v1/chat/message`, {
        user_id: userId,
        message: userMessage.content,
        channel: 'web'
      });

      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date()
      }]);

      if (response.data.session_info) {
        setSessionInfo(response.data.session_info);
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I'm connecting to the neural network... give me a moment! 🔌",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickReplies = [
    { icon: Shirt, label: 'Formal Wear', text: 'Show me formal shirts for an interview' },
    { icon: TrendingUp, label: 'Trending', text: "What's trending now?" },
    { icon: Palette, label: 'Style DNA', text: 'Analyze my Style DNA' },
  ];

  return (
    <div className="flex h-screen items-center justify-center p-4 sm:p-6">
      
      {/* Main Card Container - Floating Effect */}
      <div className="w-full max-w-4xl h-[85vh] bg-white rounded-3xl shadow-2xl overflow-hidden flex flex-col border border-white/50 relative">
        
        {/* Header - Deep Navy for Professional Look */}
        <div className="bg-[#0f172a] p-4 sm:p-5 flex items-center justify-between text-white shadow-md z-10">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">ARIA</h1>
              <p className="text-xs text-indigo-200 font-medium">ABFRL Intelligent Assistant</p>
            </div>
          </div>

          <div className="flex flex-col items-end gap-1">
            <div className="flex items-center gap-2 bg-white/10 px-3 py-1 rounded-full backdrop-blur-sm border border-white/10">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-[0_0_10px_rgba(74,222,128,0.5)]"></span>
              <span className="text-xs font-semibold tracking-wide">LIVE SYSTEM</span>
            </div>
            {sessionInfo && (
              <div className="flex gap-2 mt-1">
                <span className="text-[10px] text-gray-400 flex items-center gap-1">
                  <MessageCircle className="w-3 h-3" /> {sessionInfo.channels_used.length} Channels
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 bg-[#f8fafc] space-y-6">
          {messages.map((msg, idx) => {
            const isUser = msg.role === 'user';
            const suggested = !isUser ? getSuggestedProductsForMessage(msg.content) : [];

            return (
              <div key={idx} className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} message-animate`}>
                <div className={`flex max-w-[85%] sm:max-w-[75%] gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                  
                  {/* Avatar */}
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm ${
                    isUser ? 'bg-indigo-600 text-white' : 'bg-white text-indigo-600 border border-indigo-100'
                  }`}>
                    {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>

                  {/* Message Bubble */}
                  <div className="flex flex-col gap-2">
                    <div className={`px-5 py-3.5 rounded-2xl shadow-sm text-sm leading-relaxed ${
                      isUser 
                        ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-tr-none' 
                        : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none'
                    }`}>
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                      <span className={`text-[10px] mt-2 block ${isUser ? 'text-indigo-200' : 'text-gray-400'}`}>
                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>

                    {/* Product Cards Grid */}
                    {!isUser && suggested.length > 0 && (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-2">
                        {suggested.map(product => (
                          <div key={product.id} className="bg-white p-3 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow cursor-pointer group">
                            <div className="flex gap-3">
                              <img src={product.image} alt={product.name} className="w-16 h-20 object-cover rounded-lg bg-gray-100" />
                              <div className="flex-1 flex flex-col justify-between">
                                <div>
                                  <h4 className="font-semibold text-gray-900 text-xs line-clamp-2 group-hover:text-indigo-600 transition-colors">{product.name}</h4>
                                  <p className="text-[10px] text-gray-500 mt-0.5">{product.brand}</p>
                                </div>
                                <div className="flex items-center justify-between mt-2">
                                  <span className="text-sm font-bold text-gray-900">₹{product.price.toLocaleString()}</span>
                                  <div className="w-6 h-6 rounded-full bg-indigo-50 flex items-center justify-center group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                                    <ShoppingBag className="w-3 h-3" />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Typing Indicator */}
          {isLoading && (
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-white border border-indigo-100 flex items-center justify-center">
                <Bot className="w-4 h-4 text-indigo-600" />
              </div>
              <div className="bg-white border border-gray-100 px-4 py-3 rounded-2xl rounded-tl-none shadow-sm">
                <div className="flex gap-1.5">
                  <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full typing-dot"></div>
                  <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full typing-dot"></div>
                  <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full typing-dot"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-100 p-4">
          
          {/* Quick Replies (Only show if few messages) */}
          {messages.length < 3 && (
            <div className="flex gap-2 overflow-x-auto pb-3 mb-2 no-scrollbar">
              {quickReplies.map((qr, i) => (
                <button
                  key={i}
                  onClick={() => { setInput(qr.text); inputRef.current?.focus(); }}
                  className="flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-full text-xs font-medium hover:bg-indigo-100 transition-colors whitespace-nowrap border border-indigo-100"
                >
                  <qr.icon className="w-3.5 h-3.5" />
                  {qr.label}
                </button>
              ))}
            </div>
          )}

          <div className="relative flex items-center gap-3">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask ARIA about outfits, trends, or Style DNA..."
              className="flex-1 bg-gray-50 text-gray-900 placeholder-gray-400 border border-gray-200 rounded-xl px-5 py-3.5 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-sm"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="p-3.5 bg-[#0f172a] text-white rounded-xl hover:bg-[#1e293b] disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-gray-200"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <div className="text-center mt-3">
            <p className="text-[10px] text-gray-400 font-medium">
              Powered by <span className="text-indigo-600">ARIA AI Engine</span> • Session Secured
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}