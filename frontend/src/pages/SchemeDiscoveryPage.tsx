import React, { useEffect, useState } from 'react';
import { 
  Search, 
  Filter, 
  GraduationCap, 
  ExternalLink, 
  Building2, 
  Bot, 
  CheckCircle2,
  ChevronRight,
  ShieldCheck,
  RotateCcw
} from 'lucide-react';
import { api, SchemeItem } from '../api/client';

interface SchemeDiscoveryProps {
  onNavigate: (tab: string, schemeSlug?: string) => void;
}

export const SchemeDiscoveryPage: React.FC<SchemeDiscoveryProps> = ({ onNavigate }) => {
  const [schemes, setSchemes] = useState<SchemeItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [selectedState, setSelectedState] = useState('');

  const fetchSchemes = async () => {
    setLoading(true);
    const data = await api.listSchemes({
      q: searchQuery || undefined,
      level: selectedLevel || undefined,
      state: selectedState || undefined,
    });
    setSchemes(data.items);
    setTotal(data.total);
    setLoading(false);
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchSchemes();
    }, 250);
    return () => clearTimeout(timer);
  }, [searchQuery, selectedLevel, selectedState]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <GraduationCap className="w-6 h-6 text-blue-600" />
          Government Schemes & Scholarships Discovery
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Explore authentic Central and State Government schemes extracted directly from myScheme and National Scholarship Portal.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by scheme name, keywords, or benefits..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm rounded-lg border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>

        <div className="flex flex-wrap w-full md:w-auto items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <Filter className="w-3.5 h-3.5 text-slate-400" /> Filters:
          </div>

          <select
            value={selectedLevel}
            onChange={(e) => setSelectedLevel(e.target.value)}
            className="px-3 py-2 text-xs rounded-lg border border-slate-200 bg-slate-50 text-slate-700 font-medium focus:outline-hidden focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="">All Government Levels</option>
            <option value="Central Government">Central Government</option>
            <option value="State">State Government</option>
          </select>

          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="px-3 py-2 text-xs rounded-lg border border-slate-200 bg-slate-50 text-slate-700 font-medium focus:outline-hidden focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="">All States & UTs</option>
            <option value="Gujarat">Gujarat</option>
            <option value="Maharashtra">Maharashtra</option>
            <option value="Delhi">Delhi</option>
            <option value="Rajasthan">Rajasthan</option>
            <option value="Tamil Nadu">Tamil Nadu</option>
            <option value="Kerala">Kerala</option>
            <option value="Uttar Pradesh">Uttar Pradesh</option>
          </select>

          {(searchQuery || selectedLevel || selectedState) && (
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedLevel('');
                setSelectedState('');
              }}
              className="px-2.5 py-1.5 text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" /> Reset
            </button>
          )}
        </div>
      </div>

      {/* Results Count Banner */}
      <div className="flex items-center justify-between text-xs text-slate-500 px-1">
        <span>Showing <strong>{schemes.length}</strong> of <strong>{total}</strong> verified government schemes</span>
        <span className="flex items-center gap-1 font-mono text-slate-400">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" /> Sourced from official gazettes
        </span>
      </div>

      {/* Scheme Cards Grid */}
      {loading ? (
        <div className="py-16 text-center text-slate-400 text-sm">
          Loading authentic government schemes...
        </div>
      ) : schemes.length === 0 ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200 text-center">
          <Building2 className="w-10 h-10 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-800">No schemes matched your search</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Try adjusting your search terms or clearing state filters to view national scholarships.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {schemes.map((scheme) => (
            <div
              key={scheme.id}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-blue-300 hover:shadow-sm transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[11px] font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                    {scheme.level}
                  </span>
                  <span className="text-[11px] text-slate-400 font-medium">
                    {scheme.state_or_ministry || 'Ministry of Education'}
                  </span>
                </div>

                <h3 className="font-semibold text-slate-900 text-sm sm:text-base leading-snug mb-2 line-clamp-2">
                  {scheme.name}
                </h3>

                <p className="text-xs text-slate-600 line-clamp-3 mb-3 leading-relaxed">
                  {scheme.summary}
                </p>

                {scheme.benefit_summary && (
                  <div className="bg-blue-50/60 border border-blue-100 rounded-lg p-2.5 mb-4 text-[11px] text-blue-900 leading-relaxed">
                    <strong>Benefits:</strong> {scheme.benefit_summary}
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                <button
                  onClick={() => onNavigate('detail', scheme.slug)}
                  className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 hover:bg-slate-800 text-white flex items-center gap-1 transition-all"
                >
                  View Details <ChevronRight className="w-3.5 h-3.5" />
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onNavigate('assistant', scheme.slug)}
                    className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:text-blue-600 hover:border-blue-200"
                    title="Ask AI Assistant about this scheme"
                  >
                    <Bot className="w-4 h-4" />
                  </button>
                  <a
                    href={scheme.official_url}
                    target="_blank"
                    rel="noreferrer"
                    className="p-1.5 rounded-lg border border-slate-200 text-slate-400 hover:text-slate-700"
                    title="Open official portal"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

