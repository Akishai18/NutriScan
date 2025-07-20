import { useState } from 'react'

function App() {
  // Placeholder chat state
  const [messages, setMessages] = useState([
    { from: 'bot', text: 'Welcome to NutriScan! Ask me about your food.' },
  ]);
  const [input, setInput] = useState('');

  // Button state: scan enabled, cancel disabled initially
  const [scanActive, setScanActive] = useState(true);
  const [cancelActive, setCancelActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // API base URLs
  const API_BASE_URL = 'http://localhost:5000/api';
  const NUTRITION_API_BASE_URL = 'http://localhost:5001/api'; // Nutrition search server
  const SEARCH_API_BASE_URL = 'http://localhost:5002/api'; // Search server

  // Send user message to search API and display results
  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMessage = input.trim();
    setMessages(prev => [...prev, { from: 'user', text: userMessage }]);
    setInput('');
    setMessages(prev => [...prev, { from: 'bot', text: 'Searching for your query...' }]);
    try {
      const response = await fetch(`${SEARCH_API_BASE_URL}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage })
      });
      const data = await response.json();
      if (data.status === 'success' && Array.isArray(data.summaries)) {
        for (const summaryObj of data.summaries) {
          setMessages(prev => [...prev, {
            from: 'bot',
            text: `(${summaryObj.collection}) ${summaryObj.summary}`
          }]);
        }
      } else {
        setMessages(prev => [...prev, { from: 'bot', text: 'No results found for your query.' }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { from: 'bot', text: 'Error searching for your query.' }]);
    }
  };

  // Start detection
  const handleScan = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/start-detection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setScanActive(false);
        setCancelActive(true);
        setMessages(prev => [...prev, { from: 'bot', text: 'Detection started! Point your camera at food items.' }]);
      } else {
        setMessages(prev => [...prev, { from: 'bot', text: `Error: ${data.message}` }]);
      }
    } catch (error) {
      console.error('Error starting detection:', error);
      setMessages(prev => [...prev, { from: 'bot', text: 'Error connecting to detection service. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch nutrition info for a food item (from separate server)
  const fetchNutritionInfo = async (food) => {
    setMessages(prev => [...prev, { from: 'bot', text: `Searching nutrition info for ${food}...` }]);
    try {
      const response = await fetch(`${NUTRITION_API_BASE_URL}/get-nutrition`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ food_item: food })
      });
      const data = await response.json();
      if (data.status === 'success' && data.nutrition_info) {
        setMessages(prev => [...prev, { from: 'bot', text: `Nutrition info for ${food}: ${data.nutrition_info}` }]);
      } else {
        setMessages(prev => [...prev, { from: 'bot', text: `No nutrition info found for ${food}.` }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { from: 'bot', text: `Error fetching nutrition info for ${food}.` }]);
    }
  };

  // Stop detection and get results
  const handleCancel = async () => {
    setIsLoading(true);
    try {
      // Stop detection
      const stopResponse = await fetch(`${API_BASE_URL}/stop-detection`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const stopData = await stopResponse.json();
      
      if (stopData.status === 'success') {
        setScanActive(true);
        setCancelActive(false);
        setMessages(prev => [...prev, { from: 'bot', text: 'Detection stopped. Getting results...' }]);
        
        // Get detection results
        const resultsResponse = await fetch(`${API_BASE_URL}/detection-results`);
        const resultsData = await resultsResponse.json();
        
        if (resultsData.status === 'success' && resultsData.results.length > 0) {
          const detectedFoods = resultsData.results.map(item => item.food);
          const uniqueFoods = [...new Set(detectedFoods)];
          
          if (uniqueFoods.length > 0) {
            setMessages(prev => [...prev, { 
              from: 'bot', 
              text: `Detected foods: ${uniqueFoods.join(', ')}. I'll help you find nutrition information!` 
            }]);
            // Fetch nutrition info for each detected food
            for (const food of uniqueFoods) {
              await fetchNutritionInfo(food);
            }
          } else {
            setMessages(prev => [...prev, { from: 'bot', text: 'No food items detected. Please try again.' }]);
          }
        } else {
          setMessages(prev => [...prev, { from: 'bot', text: 'No detection results found.' }]);
        }
      } else {
        setMessages(prev => [...prev, { from: 'bot', text: `Error: ${stopData.message}` }]);
      }
    } catch (error) {
      console.error('Error stopping detection:', error);
      setMessages(prev => [...prev, { from: 'bot', text: 'Error stopping detection. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  function formatBotMessage(text) {
    // Try to parse as JSON object
    let parsed;
    try {
      parsed = typeof text === 'string' ? JSON.parse(text) : text;
    } catch {
      parsed = null;
    }
    // If it's an object, render as a list
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      return (
        <ul className="list-disc ml-6">
          {Object.entries(parsed).map(([key, value]) => (
            <li key={key}><b>{key}:</b> {value}</li>
          ))}
        </ul>
      );
    }
    if (typeof text === 'string' && text.includes(':') && text.includes('\n')) {
      const lines = text.split(/\n|\\n/).filter(Boolean);
      if (lines.length > 1) {
        return (
          <ul className="list-disc ml-6">
            {lines.map((line, idx) => {
              const [k, ...v] = line.split(':');
              return <li key={idx}><b>{k.trim()}:</b> {v.join(':').trim()}</li>;
            })}
          </ul>
        );
      }
    }
    return text;
  }

  return (
    <div className="min-h-screen flex flex-col px-2" style={{ fontFamily: "'Inter', 'system-ui', 'sans-serif'" }}>
      {/* Title */}
      <header className="py-8 flex flex-col items-center">
        {/* Pixel-style icon (using emoji for now, can be replaced with SVG) */}
        <span className="text-5xl mb-2 drop-shadow-lg">🍃</span>
        <h1 className="text-5xl md:text-7xl text-center font-bold text-green-700 arcade-outline tracking-widest mb-2 select-none font-arcade">
          NutriScan
        </h1>
      </header>
      {/* Main Split Layout */}
      <main className="flex-1 flex flex-col md:flex-row gap-8 max-w-5xl mx-auto w-full pb-8">
        {/* Left: Chatbot */}
        <section className="flex-1 bg-overlay rounded-3xl border-4 border-green-800 shadow-xl flex flex-col p-4 md:p-8 pixel-border-green min-h-[400px]">
          <h2 className="text-xl font-bold text-green-800 mb-2 tracking-wide">Chatbot</h2>
          <div className="flex-1 overflow-y-auto mb-4 bg-green-50 rounded-xl p-3 border border-green-200" style={{ fontFamily: "'Inter', 'system-ui', 'sans-serif'" }}>
            {messages.map((msg, idx) => (
              <div key={idx} className={`mb-2 flex ${msg.from === 'user' ? 'justify-end' : 'justify-start'}`}>                <span className={`inline-block px-3 py-2 rounded-2xl text-xs md:text-base ${msg.from === 'user' ? 'bg-yellow-200 text-right' : 'bg-green-200 text-left'} shadow`}>
                  {msg.from === 'bot' ? formatBotMessage(msg.text) : msg.text}
                </span>
              </div>
            ))}
          </div>
          <form onSubmit={handleSend} className="flex gap-2">
            <input
              className="flex-1 rounded-xl border-2 border-green-400 px-3 py-2 text-base focus:outline-none focus:ring-2 focus:ring-green-400 font-mono"
              type="text"
              placeholder="Type your message..."
              value={input}
              onChange={e => setInput(e.target.value)}
            />
            <button type="submit" className="bg-yellow-400 hover:bg-yellow-500 text-green-900 font-bold px-4 py-2 rounded-xl border-2 border-yellow-600 shadow active:scale-95 transition font-arcade">Send</button>
          </form>
        </section>
        {/* Right: Actions */}
        <section className="flex-1 bg-overlay rounded-3xl border-4 border-yellow-600 shadow-xl flex flex-col items-center justify-center p-4 md:p-8 pixel-border-yellow min-h-[400px]">
          <h2 className="text-xl font-bold text-yellow-700 mb-6 tracking-wide">Actions</h2>
          <div className="flex flex-col gap-4 w-full max-w-xs">
            <button
              className={`arcade-outline py-3 rounded-xl border-4 border-green-800 shadow-lg text-lg font-bold transition-all duration-150 font-arcade ${scanActive && !isLoading ? 'bg-green-500 hover:bg-green-600 text-white active:scale-95 cursor-pointer' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
              onClick={handleScan}
              disabled={!scanActive || isLoading}
            >
              {isLoading ? 'Starting...' : 'Scan Food'}
            </button>
            <button
              className={`arcade-outline py-3 rounded-xl border-4 border-gray-500 shadow-lg text-lg font-bold transition-all duration-150 font-arcade ${cancelActive && !isLoading ? 'bg-red-500 hover:bg-red-600 text-white active:scale-95 cursor-pointer border-red-800' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
              onClick={handleCancel}
              disabled={!cancelActive || isLoading}
            >
              {isLoading ? 'Stopping...' : 'Cancel'}
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
