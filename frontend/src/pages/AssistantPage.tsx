import React, { useState } from 'react';
import { 
  Bot, 
  Send, 
  Sparkles, 
  FileText, 
  ExternalLink, 
  AlertCircle, 
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  User,
  GraduationCap
} from 'lucide-react';
import { api, AssistantResponse, SourceCitation } from '../api/client';

interface AssistantPageProps {
  initialSchemeSlug?: string;
  onNavigate: (tab: string, schemeSlug?: string) => void;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  citations?: SourceCitation[];
  insufficientEvidence?: boolean;
  timestamp: string;
}

export const AssistantPage: React.FC<AssistantPageProps> = ({ initialSchemeSlug, onNavigate }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      sender: 'assistant',
      text: 'Namaste! I am CivicPilot. I answer policy and welfare questions strictly using official Gazette notifications and operational guidelines from the National Scholarship Portal and myScheme.gov.in.\n\nHow can I help you regarding scholarships, income limits, or documentation today?',
      citations: [
        {
          source_title: "National Scholarship Portal (NSP) — Official Operational Guidelines",
          source_url: "https://scholarships.gov.in/",
          section_title: "General Information",
          excerpt: "Single-window digital platform for delivery of scholarship schemes directly to student bank accounts via Direct Benefit Transfer (DBT)."
        }
      ],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);


  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedCitationId, setExpandedCitationId] = useState<string | null>(null);

  const samplePrompts = [
    "What is the maximum family income limit for scholarships?",
    "Can I receive two government scholarships at the same time?",
    "What documents are needed for One Time Registration (OTR)?",
    "How does Direct Benefit Transfer (DBT) disbursal work?"
  ];

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: textToSend.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const resp: AssistantResponse = await api.queryAssistant(textToSend, initialSchemeSlug);

      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: resp.answer,
        citations: resp.citations,
        insufficientEvidence: resp.insufficient_evidence,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          text: 'An error occurred while connecting to the assistant. Please try again or check your query.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <Bot className="w-5 h-5 text-blue-600" />
            Scheme & Policy Guidelines Explainer
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Grounded directly in authentic Government of India operational guidelines with verifiable clause citations.
          </p>
        </div>


        {initialSchemeSlug && (
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 border border-blue-200 text-xs font-medium text-blue-800">
            <GraduationCap className="w-3.5 h-3.5 text-blue-600" />
            Context: {initialSchemeSlug}
          </div>
        )}
      </div>

      {/* Suggested prompts */}
      <div className="flex flex-wrap gap-2">
        {samplePrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="text-xs px-3 py-1.5 rounded-full bg-white hover:bg-slate-50 border border-slate-200 text-slate-600 font-medium transition-all shadow-2xs hover:border-blue-300"
          >
            "{prompt}"
          </button>
        ))}
      </div>

      {/* Chat Messages Log */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs min-h-[420px] max-h-[580px] overflow-y-auto space-y-5">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
              msg.sender === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-slate-900 text-white'
            }`}>
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div className={`max-w-[85%] rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
              msg.sender === 'user'
                ? 'bg-blue-600 text-white rounded-tr-xs'
                : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-tl-xs'
            }`}>
              <div className="whitespace-pre-line">{msg.text}</div>

              {/* Insufficient Evidence Notice */}
              {msg.insufficientEvidence && (
                <div className="mt-3 p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <strong>Unverified Fact Boundary:</strong> To prevent AI hallucinations, CivicPilot does not answer questions outside official gazette documents.
                  </div>
                </div>
              )}

              {/* Citations Panel */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-200/60 space-y-2">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                    Verified Official Citations ({msg.citations.length})
                  </div>

                  {msg.citations.map((cite, cIdx) => {
                    const citeKey = `${msg.id}-${cIdx}`;
                    const isExpanded = expandedCitationId === citeKey;

                    return (
                      <div
                        key={cIdx}
                        className="bg-white rounded-lg border border-slate-200 p-2.5 text-xs text-slate-700 space-y-1.5"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-semibold text-slate-900 truncate">
                            {cite.source_title}
                          </span>
                          <button
                            onClick={() => setExpandedCitationId(isExpanded ? null : citeKey)}
                            className="text-[11px] font-medium text-blue-600 hover:text-blue-800 shrink-0 flex items-center gap-0.5"
                          >
                            {isExpanded ? 'Hide Excerpt' : 'View Excerpt'}
                            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                          </button>
                        </div>

                        <div className="text-[11px] text-slate-500 font-mono">
                          Section: {cite.section_title || 'General Guidelines'}
                        </div>

                        {isExpanded && (
                          <div className="mt-2 p-2 bg-slate-50 rounded border border-slate-100 text-[11px] text-slate-600 italic leading-relaxed">
                            "{cite.excerpt}"
                          </div>
                        )}

                        {cite.source_url && (
                          <div className="pt-1">
                            <a
                              href={cite.source_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-[10px] text-blue-600 underline inline-flex items-center gap-1"
                            >
                              Open Source Document <ExternalLink className="w-2.5 h-2.5" />
                            </a>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              <div className={`text-[10px] mt-2 font-mono ${msg.sender === 'user' ? 'text-blue-200' : 'text-slate-400'}`}>
                {msg.timestamp}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-slate-500 italic p-3 bg-slate-50 rounded-lg w-max border border-slate-200">
            <Bot className="w-4 h-4 animate-bounce text-blue-600" />
            Retrieving official guidelines and synthesizing grounded answer...
          </div>
        )}
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-2"
      >
        <input
          type="text"
          placeholder="Ask any question about scholarship eligibility, documents, or deadlines..."
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          disabled={loading}
          className="flex-1 px-4 py-3 text-xs sm:text-sm rounded-xl border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 shadow-xs transition-all"
        />
        <button
          type="submit"
          disabled={loading || !inputQuery.trim()}
          className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs sm:text-sm font-semibold flex items-center gap-2 transition-all shadow-xs"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </button>
      </form>

      <div className="text-center text-[11px] text-slate-400 font-mono">
        All responses are checked against authenticated Government of India policy documents. CivicPilot does not generate legal advice.
      </div>
    </div>
  );
};

