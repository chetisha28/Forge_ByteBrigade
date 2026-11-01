import React, { useEffect, useState } from 'react';
import { 
  GraduationCap, 
  FileCheck2, 
  Bot, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  ExternalLink,
  Sparkles,
  ShieldCheck,
  Building2,
  Banknote
} from 'lucide-react';
import { api, ProfileData, SchemeItem, UserDocument } from '../api/client';

interface DashboardProps {
  onNavigate: (tab: string, schemeSlug?: string) => void;
  profile?: ProfileData;
}

export const DashboardPage: React.FC<DashboardProps> = ({ onNavigate, profile: initialProfile }) => {
  const [profile, setProfile] = useState<ProfileData | null>(initialProfile || null);
  const [schemes, setSchemes] = useState<SchemeItem[]>([]);
  const [documents, setDocuments] = useState<UserDocument[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const [profData, schemesData, docsData] = await Promise.all([
        initialProfile ? Promise.resolve(initialProfile) : api.getProfile(),
        api.listSchemes({ level: 'Central Government' }),
        api.listDocuments()
      ]);
      setProfile(profData);
      setSchemes(schemesData.items.slice(0, 3));
      setDocuments(docsData);
      setLoading(false);
    }
    load();
  }, [initialProfile]);

  const hasIncome = profile?.annual_family_income !== undefined && profile?.annual_family_income !== null;
  const incomeValue = profile?.annual_family_income || 0;
  const isIncomeWithinLimit = hasIncome && incomeValue <= 250000;

  return (
    <div className="space-y-8">
      {/* Top Banner / Hero */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-2xl p-6 sm:p-8 shadow-sm border border-slate-700 relative overflow-hidden">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs font-medium text-emerald-400 mb-4">
            <ShieldCheck className="w-3.5 h-3.5" />
            National Citizen Welfare & Scholarship Registry
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mb-2">
            Welcome back, {profile?.full_name || 'Citizen'}
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed mb-6">
            CivicPilot connects citizens to 850+ official Indian government scholarships and welfare schemes. 
            Evaluate your eligibility deterministically against Gazette guidelines, query official notifications, and prepare verified applications.
          </p>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('discovery')}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold transition-all shadow-sm"
            >
              <GraduationCap className="w-4 h-4" />
              Discover Scholarships
            </button>
            <button
              onClick={() => onNavigate('assistant')}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-semibold transition-all"
            >
              <Bot className="w-4 h-4 text-blue-400" />
              Policy Guidelines Explainer
            </button>
          </div>

        </div>
      </div>

      {/* Profile Overview & Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Student Profile</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-medium border border-emerald-200">
                {profile?.completeness_percentage || (profile?.full_name ? 15 : 0)}% Complete
              </span>
            </div>
            <div className="text-lg font-bold text-slate-900">{profile?.course || 'Degree / Course Not Set'}</div>
            <p className="text-xs text-slate-500 mt-1">{profile?.institution_name || 'Institution details pending'}</p>
          </div>
          <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between text-xs">
            <span className="text-slate-500">{profile?.state_code || 'Domicile not set'} • {profile?.caste_category || 'General'}</span>
            <button 
              onClick={() => onNavigate('profile')} 
              className="font-medium text-blue-600 hover:text-blue-700"
            >
              Edit Profile →
            </button>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Means & Income Status</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium border ${hasIncome ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                {hasIncome ? 'Means-Tested' : 'Not Declared'}
              </span>
            </div>
            <div className="text-lg font-bold text-slate-900">
              {hasIncome ? `₹${Number(profile?.annual_family_income).toLocaleString('en-IN')} / year` : 'Income Not Set'}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {hasIncome 
                ? 'Evaluated against Gazette scholarship ceilings' 
                : 'Add annual income to evaluate means-tested eligibility'}
            </p>
          </div>
          <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between text-xs">
            <span className="text-slate-500">Cap: ≤ ₹2.5L / ₹4.5L</span>
            {hasIncome ? (
              <span className={`font-medium flex items-center gap-1 ${isIncomeWithinLimit ? 'text-emerald-600' : 'text-amber-600'}`}>
                <CheckCircle2 className="w-3.5 h-3.5" /> {isIncomeWithinLimit ? 'Within Limits' : 'Above Basic Cap'}
              </span>
            ) : (
              <button 
                onClick={() => onNavigate('profile')} 
                className="font-medium text-blue-600 hover:text-blue-700"
              >
                Set Income →
              </button>
            )}
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Document Readiness</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium border ${documents.length > 0 ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-amber-50 text-amber-700 border-amber-200'}`}>
                {documents.length} / 4 Ready
              </span>
            </div>
            <div className="text-lg font-bold text-slate-900">
              {documents.length > 0 ? `${documents.length} Document${documents.length > 1 ? 's' : ''} in Vault` : 'Vault is Empty'}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {documents.length > 0 
                ? 'Verified certificates ready for application mapping' 
                : 'Upload Aadhaar & Income Certificate to verify'}
            </p>
          </div>
          <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between text-xs">
            <span className="text-slate-500">{documents.length > 0 ? 'Private & Encrypted' : 'Verification Pending'}</span>
            <button 
              onClick={() => onNavigate('documents')} 
              className="font-medium text-blue-600 hover:text-blue-700"
            >
              Upload Docs →
            </button>
          </div>
        </div>
      </div>

      {/* Recommended Schemes Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-500" />
              Recommended Schemes for Your Profile
            </h2>
            <p className="text-xs text-slate-500">Derived deterministically from your education level, income bracket, and social category.</p>
          </div>
          <button
            onClick={() => onNavigate('discovery')}
            className="text-xs sm:text-sm font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            View all 852 scholarships <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {schemes.map((scheme) => (
            <div
              key={scheme.id}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-slate-300 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                    {scheme.level}
                  </span>
                  <span className="text-[11px] text-slate-400 font-mono">
                    Verified {scheme.last_verified_at}
                  </span>
                </div>
                <h3 className="font-semibold text-slate-900 text-sm sm:text-base line-clamp-2 mb-2">
                  {scheme.name}
                </h3>
                <p className="text-xs text-slate-600 line-clamp-3 mb-3 leading-relaxed">
                  {scheme.summary}
                </p>

                {scheme.recommendation_reason && (
                  <div className="bg-emerald-50/60 border border-emerald-100 rounded-lg p-2.5 mb-4 text-[11px] text-emerald-800 flex items-start gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span><strong>Match Reason:</strong> {scheme.recommendation_reason}</span>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <button
                  onClick={() => onNavigate('detail', scheme.slug)}
                  className="text-xs font-semibold text-blue-600 hover:text-blue-800"
                >
                  View Details & Criteria
                </button>
                <button
                  onClick={() => onNavigate('assistant', scheme.slug)}
                  className="text-xs font-medium text-slate-500 hover:text-slate-800 flex items-center gap-1"
                >
                  <Bot className="w-3.5 h-3.5 text-blue-500" /> Ask AI
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Trust & Provenance Notice */}
      <div className="p-4 rounded-xl bg-slate-100/80 border border-slate-200 text-xs text-slate-600 flex items-start gap-3">
        <Building2 className="w-5 h-5 text-slate-500 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-800">Public Information Notice & Provenance:</strong> CivicPilot is an independent civic discovery tool developed to assist citizens. 
          All scheme rules, eligibility caps, benefits, and guidelines are mirrored directly from official gazette sources (including <a href="https://scholarships.gov.in" target="_blank" rel="noreferrer" className="text-blue-600 underline">scholarships.gov.in</a> and <a href="https://www.myscheme.gov.in" target="_blank" rel="noreferrer" className="text-blue-600 underline">myScheme.gov.in</a>). 
          CivicPilot does not grant or guarantee welfare benefits.
        </div>
      </div>
    </div>
  );
};
