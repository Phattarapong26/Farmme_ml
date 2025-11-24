import { useState, useRef, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send, User, Bot, Loader2, Sparkles, MessageCircle, Zap, Droplets, Sprout, TrendingUp, TrendingDown, Minus, Calendar } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useUserProfile } from '@/hooks/useUserProfile';
import { useToast } from '@/hooks/use-toast';
import ChartMessage from '@/components/chat/ChartMessage';

const API_BASE_URL = 'http://localhost:8000';

interface ChartData {
  type: 'price_forecast';
  data: {
    historical: Array<{ date: string; price: number }>;
    forecast: Array<{
      date: string;
      price: number;
      confidence_low: number;
      confidence_high: number;
    }>;
    metadata: {
      crop_type: string;
      province: string;
      days_ahead: number;
      model_used: string;
      confidence: number;
      price_trend: string;
    };
  };
}

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  functionCalled?: string;
  functionResult?: any;
  chartData?: ChartData;
}

const ChatAI = () => {
  const { user } = useAuth();
  const { data: userProfile } = useUserProfile(user?.id);
  const { toast } = useToast();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Welcome message with personalization
    const userName = userProfile?.full_name || user?.username || 'คุณเกษตรกร';
    const welcomeMessage: Message = {
      id: 'welcome',
      type: 'bot',
      content: `สวัสดีครับคุณ${userName}! ยินดีต้อนรับสู่ระบบ AI ผู้ช่วยด้านการเกษตร 🌱\n\n**ผมสามารถช่วยคุณได้ในเรื่อง:**\n\n• 🌤️ วิเคราะห์สภาพอากาศและพยากรณ์อากาศ\n• 🌾 แนะนำการปลูกพืชที่เหมาะสมกับพื้นที่\n• 💧 คำแนะนำการจัดการน้ำและดิน\n• 📊 ทำนายราคาและแนวโน้มตลาด\n• 🐛 การจัดการศัตรูพืชและโรคพืช\n• 📅 วางแผนการเกษตรตามฤดูกาล\n\n**วิธีใช้งาน:**\nเพียงพิมพ์คำถามของคุณ ผมจะตอบด้วยข้อมูลที่เข้าใจง่ายและใช้งานได้จริง!\n\nมีอะไรให้ผมช่วยไหมครับ? 😊`,
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, [user, userProfile]);



  const handleSendMessage = async () => {
    if (inputMessage.trim() === '' || isTyping) return;

    const newUserMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newUserMessage]);
    const userInput = inputMessage;
    setInputMessage('');
    setIsTyping(true);

    try {
      // Get crop_id from user profile or default to 1
      let cropId = 1;
      if (userProfile?.experience_crops && Array.isArray(userProfile.experience_crops) && userProfile.experience_crops.length > 0) {
        // Try to parse as number if it's a string
        const firstCrop = userProfile.experience_crops[0];
        cropId = typeof firstCrop === 'number' ? firstCrop : parseInt(firstCrop) || 1;
      }

      // Call local backend chat endpoint with user profile
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userInput,
          user_id: user?.id || null,  // Send user ID for personalization
          crop_id: cropId,  // Use user's crop preference
          price_history: [100, 105, 103, 108, 110],
          weather: [50, 25],
          crop_info: [3, 60, 2],
          calendar: [0, 1, 2]
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Chat API Error:', response.status, errorData);
        throw new Error(`Failed to get chat response: ${response.status}`);
      }

      const data = await response.json();

      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: data?.gemini_answer || data?.response || 'ขออภัย เกิดข้อผิดพลาดในการประมวลผล',
        timestamp: new Date(),
        functionCalled: data?.function_called || undefined,
        functionResult: data?.function_result || undefined,
        chartData: data?.chart_data || undefined
      };
      
      setMessages(prev => [...prev, botResponse]);
      
      // Show toast if using cached data
      if (data?.cached_data_used) {
        toast({
          title: "⚡ ใช้ข้อมูลแคช",
          description: "ตอบสนองไวเร็วขึ้นด้วยข้อมูลที่บันทึกไว้",
          duration: 2000,
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: 'ขออภัยครับ เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาลองใหม่อีกครั้ง',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorResponse]);
      toast({
        title: "❌ เกิดข้อผิดพลาด",
        description: "ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ กรุณาลองอีกครั้ง",
        variant: "destructive",
        duration: 3000,
      });
    } finally {
      setIsTyping(false);
      inputRef.current?.focus();
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('th-TH', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  const formatMessageContent = (content: string) => {
    // Format message content for better readability
    // Replace markdown-style bold with styled spans
    const formattedContent = content
      .split('\n')
      .map((line, index) => {
        // Check if line is a header (starts with **)
        if (line.trim().startsWith('**') && line.trim().endsWith('**')) {
          const headerText = line.trim().replace(/\*\*/g, '');
          return (
            <div key={index} className="font-semibold text-base mt-3 mb-2 first:mt-0">
              {headerText}
            </div>
          );
        }
        // Check if line is a bullet point
        else if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
          const bulletText = line.trim().replace(/^[•-]\s*/, '');
          return (
            <div key={index} className="flex gap-2 ml-2 mb-1">
              <span className="text-green-500 flex-shrink-0">•</span>
              <span>{bulletText}</span>
            </div>
          );
        }
        // Regular line
        else if (line.trim()) {
          return (
            <div key={index} className="mb-2">
              {line}
            </div>
          );
        }
        // Empty line for spacing
        else {
          return <div key={index} className="h-2" />;
        }
      });
    
    return <>{formattedContent}</>;
  };

  return (
    <div className="min-h-screen bg-white">
      {/* MapNavbar is now added in App.tsx */}
      
      <div className="max-w-5xl mx-auto p-4 sm:p-6 ">
        {/* Header */}
        <div className="text-center mb-6 sm:mb-8 mt-8">
          <div className="flex items-center justify-center  mb-1">
            <div className="relative flex items-center ">
              <img 
                src="/logo.png" 
                alt="FarmTime Logo" 
                className="h-16 w-auto"
              />
              <div className="bg-gradient-to-r from-green-500 to-green-600 text-white px-3 py-1 rounded-full text-sm font-medium shadow-lg inline-flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                AI
              </div>
            </div>
          </div>
          <p className="text-gray-600 ml-8 text-base sm:text-lg font-medium">เพื่อนคู่คิดเกษตรกรไทย</p>
          <p className="text-gray-500 text-sm mt-2">ปรึกษาเรื่องการเกษตร สภาพอากาศ และการปลูกพืช</p>
        </div>

        {/* Chat Container */}
        <Card className="h-[70vh] sm:h-[600px] flex flex-col shadow-xl border-0 bg-white/80 backdrop-blur-sm overflow-hidden">
          <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
            {/* Chat Header */}
            <div className="border-b bg-gradient-to-r from-green-500 to-green-600 text-white p-4 rounded-t-lg">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                    <MessageCircle className="w-5 h-5" />
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white animate-pulse"></div>
                </div>
                <div className="flex-1">
                  <span className="font-semibold">Farm AI Assistant</span>
                  <p className="text-green-100 text-sm">พร้อมให้คำปรึกษาตลอด 24 ชั่วโมง</p>
                </div>
                {isTyping && (
                  <div className="flex items-center gap-1 text-green-100 text-sm">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>กำลังพิมพ์...</span>
                  </div>
                )}
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto overflow-x-hidden p-4 space-y-6 bg-gray-50/50">
              {messages.length === 0 && (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <MessageCircle className="w-8 h-8 text-green-500" />
                    </div>
                    <p className="text-gray-500">เริ่มต้นการสนทนากับ AI ของเรา</p>
                  </div>
                </div>
              )}
              
              {messages.map((message, index) => (
                <div key={message.id} className={`flex gap-3 animate-in slide-in-from-bottom-2 duration-500 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`} style={{ animationDelay: `${index * 100}ms` }}>
                  {message.type === 'bot' && (
                    <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  )}
                  
                  <div className={`min-w-0 flex-1 ${message.type === 'user' ? 'order-2 flex justify-end' : ''}`}>
                    {message.type === 'bot' && (
                      <div className="text-xs text-green-600 mb-2 flex items-center gap-1 font-medium">
                        <span>🤖 Farm AI Assistant</span>
                      </div>
                    )}
                    
                    <div className={`max-w-[85%] rounded-2xl p-4 shadow-sm transition-all hover:shadow-md ${message.type === 'user' 
                        ? 'bg-gradient-to-r from-green-500 to-green-600 text-white ml-auto' 
                        : 'bg-white text-gray-800 border border-gray-100'
                    }`}>
                      {/* ML Model Badge */}
                      {message.type === 'bot' && message.functionCalled && (
                        <div className="flex items-center gap-1 mb-2 pb-2 border-b border-gray-100">
                          <Zap className="w-3 h-3 text-purple-500" />
                          <span className="text-xs text-purple-600 font-medium">ใช้ ML Model</span>
                          <span className="text-xs text-gray-400">
                            ({message.functionCalled === 'get_price_prediction' ? 'ทำนายราคา' : 
                              message.functionCalled === 'get_crop_recommendations' ? 'แนะนำพืช' : 'จัดการน้ำ'})
                          </span>
                        </div>
                      )}
                      
                      {/* Render with chart if available */}
                      {message.type === 'bot' && message.chartData ? (
                        <ChartMessage 
                          chartData={message.chartData}
                          textResponse={message.content}
                        />
                      ) : (
                        <div className="text-sm leading-relaxed break-words hyphens-auto whitespace-pre-wrap">
                          {formatMessageContent(message.content)}
                        </div>
                      )}
                      
                      {/* Function Result Display removed - LLM formats everything now */}
                      
                      <div className={`text-xs mt-3 ${message.type === 'user' ? 'text-green-100' : 'text-gray-400'
                      }`}>
                        {formatTimestamp(message.timestamp)}
                      </div>
                    </div>
                  </div>

                  {message.type === 'user' && (
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0 order-3 shadow-md">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>
              ))}
              
              {isTyping && (
                <div className="flex gap-3 justify-start animate-in slide-in-from-bottom-2">
                  <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-md">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t bg-white p-4">
              <div className="flex gap-3">
                <div className="flex-1 relative">
                  <Input
                    ref={inputRef}
                    placeholder="พิมพ์คำถามของคุณที่นี่... 🌱"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                    disabled={isTyping}
                    className="pr-12 py-3 border-2 border-gray-200 focus:border-green-400 rounded-xl transition-colors"
                  />
                  {inputMessage && (
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      <span className="text-xs text-gray-400">{inputMessage.length}</span>
                    </div>
                  )}
                </div>
                <Button 
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim() || isTyping}
                  className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white px-6 py-3 rounded-xl shadow-lg transition-all hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isTyping ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
              
              {/* Quick suggestions */}
              <div className="flex flex-wrap gap-2 mt-3">
                {[
                  { icon: '📊', text: 'ทำนายราคาพริก 30 วันข้างหน้า' },
                  { icon: '🌾', text: 'แนะนำพืชที่เหมาะสมกับพื้นที่ของฉัน' },
                  { icon: '💧', text: 'ควรรดน้ำบ่อยแค่ไหน' },
                  { icon: '📅', text: 'ปลูกอะไรช่วงไหนดี' }
                ].map((suggestion) => (
                  <button
                    key={suggestion.text}
                    onClick={() => setInputMessage(suggestion.text)}
                    className="px-3 py-1.5 bg-gray-100 hover:bg-green-100 text-gray-600 hover:text-green-600 rounded-full text-xs transition-colors font-medium"
                    disabled={isTyping}
                  >
                    {suggestion.icon} {suggestion.text}
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ChatAI;