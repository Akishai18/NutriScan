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

  // Placeholder send handler
  const handleSend = (e) => {
    e.preventDefault();
    if (input.trim()) {
      setMessages([...messages, { from: 'user', text: input }]);
      setInput('');
    }
  };

  // Scan and Cancel button handlers
  const handleScan = () => {
    setScanActive(false);
    setCancelActive(true);
    // Add scan logic here
  };
  const handleCancel = () => {
    setScanActive(true);
    setCancelActive(false);
    // Add cancel logic here
  };

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
              <div key={idx} className={`mb-2 flex ${msg.from === 'user' ? 'justify-end' : 'justify-start'}`}>
                <span className={`inline-block px-3 py-2 rounded-2xl text-xs md:text-base ${msg.from === 'user' ? 'bg-yellow-200 text-right' : 'bg-green-200 text-left'} shadow`}>{msg.text}</span>
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
              className={`arcade-outline py-3 rounded-xl border-4 border-green-800 shadow-lg text-lg font-bold transition-all duration-150 font-arcade ${scanActive ? 'bg-green-500 hover:bg-green-600 text-white active:scale-95 cursor-pointer' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}
              onClick={handleScan}
              disabled={!scanActive}
            >
              Scan Food
            </button>
            <button
              className={`arcade-outline py-3 rounded-xl border-4 border-gray-500 shadow-lg text-lg font-bold transition-all duration-150 font-arcade ${cancelActive ? 'bg-red-500 hover:bg-red-600 text-white active:scale-95 cursor-pointer border-red-800' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}
              onClick={handleCancel}
              disabled={!cancelActive}
            >
              Cancel
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
