import React, { useEffect, useState } from 'react';
import { 
  User, 
  GraduationCap, 
  Building2, 
  IndianRupee, 
  ShieldCheck, 
  CheckCircle2, 
  Info,
  Save
} from 'lucide-react';
import { api, ProfileData } from '../api/client';

interface ProfilePageProps {
  onProfileUpdated?: (updated: ProfileData) => void;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ onProfileUpdated }) => {
  const [profile, setProfile] = useState<ProfileData>({
    full_name: '',
    state_code: '',
    education_level: 'Undergraduate',
    course: '',
    study_year: 1,
    institution_name: '',
    annual_family_income: 0,
    caste_category: 'General',
    gender: 'Male',
    is_differently_abled: false
  });

  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    async function load() {
      const data = await api.getProfile();
      setProfile(data);
    }
    load();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    const updated = await api.updateProfile(profile);
    setProfile(updated);
    if (onProfileUpdated) onProfileUpdated(updated);
    setSaving(false);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <User className="w-6 h-6 text-blue-600" />
          Student Citizen Profile
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          CivicPilot uses your demographic and academic details solely to evaluate deterministic scheme eligibility and calculate means-tested scholarships.
        </p>
      </div>

      {saveSuccess && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <span>Profile saved successfully. Deterministic scheme recommendations updated!</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
        {/* Section 1: Personal & Geographic Details */}
        <div className="space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <Building2 className="w-4 h-4 text-slate-400" />
            1. Identity & Domicile
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Full Legal Name (as per Aadhaar / 10th Certificate)
              </label>
              <input
                type="text"
                required
                value={profile.full_name || ''}
                onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                placeholder="e.g. Aarav Sharma"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                State / UT of Domicile
              </label>
              <select
                value={profile.state_code || ''}
                onChange={(e) => setProfile({ ...profile, state_code: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              >
                <option value="">Select State / UT</option>
                <option value="Gujarat">Gujarat</option>
                <option value="Maharashtra">Maharashtra</option>
                <option value="Delhi">Delhi</option>
                <option value="Rajasthan">Rajasthan</option>
                <option value="Tamil Nadu">Tamil Nadu</option>
                <option value="Karnataka">Karnataka</option>
                <option value="Kerala">Kerala</option>
                <option value="Uttar Pradesh">Uttar Pradesh</option>
                <option value="Madhya Pradesh">Madhya Pradesh</option>
                <option value="West Bengal">West Bengal</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Gender
              </label>
              <select
                value={profile.gender || 'Male'}
                onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="flex items-center gap-3 pt-6">
              <input
                type="checkbox"
                id="disability"
                checked={profile.is_differently_abled || false}
                onChange={(e) => setProfile({ ...profile, is_differently_abled: e.target.checked })}
                className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300"
              />
              <label htmlFor="disability" className="text-xs font-medium text-slate-700">
                Person with Disability (UDID / 40%+ benchmark disability)
              </label>
            </div>
          </div>
        </div>

        {/* Section 2: Academic Program */}
        <div className="space-y-4 pt-6 border-t border-slate-100">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <GraduationCap className="w-4 h-4 text-slate-400" />
            2. Academic Qualifications & Enrollment
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Current Education Stage
              </label>
              <select
                value={profile.education_level || 'Undergraduate'}
                onChange={(e) => setProfile({ ...profile, education_level: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
              >
                <option value="Class 10">Class 10 (Secondary)</option>
                <option value="Class 11-12">Class 11 / 12 (Higher Secondary)</option>
                <option value="Diploma / ITI">Diploma / Polytechnic / ITI</option>
                <option value="Undergraduate">Undergraduate (B.Tech / B.Sc / BA / MBBS)</option>
                <option value="Postgraduate">Postgraduate (M.Tech / M.Sc / MA / MD)</option>
                <option value="PhD">Doctorate / Ph.D.</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Course / Program Name
              </label>
              <input
                type="text"
                value={profile.course || ''}
                onChange={(e) => setProfile({ ...profile, course: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200"
                placeholder="e.g. Bachelor of Technology (CSE)"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Institution / University Name (Must have AISHE / UDISE code)
              </label>
              <input
                type="text"
                value={profile.institution_name || ''}
                onChange={(e) => setProfile({ ...profile, institution_name: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200"
                placeholder="e.g. Gujarat Technological University"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Year of Study
              </label>
              <select
                value={profile.study_year || 1}
                onChange={(e) => setProfile({ ...profile, study_year: Number(e.target.value) })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
              >
                <option value={1}>1st Year (Fresh Application)</option>
                <option value={2}>2nd Year (Renewal)</option>
                <option value={3}>3rd Year (Renewal)</option>
                <option value={4}>4th Year (Renewal)</option>
                <option value={5}>5th Year (Integrated Degree)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Section 3: Financial & Means Testing */}
        <div className="space-y-4 pt-6 border-t border-slate-100">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
              <IndianRupee className="w-4 h-4 text-slate-400" />
              3. Means & Social Category
            </h2>
            <span className="text-[11px] text-slate-400 font-mono flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-blue-500" /> Private & Stored Locally
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Total Annual Family Gross Income (INR)
              </label>
              <input
                type="number"
                value={profile.annual_family_income || ''}
                onChange={(e) => setProfile({ ...profile, annual_family_income: Number(e.target.value) })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200"
                placeholder="e.g. 220000"
              />
              <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1">
                <Info className="w-3 h-3 text-slate-400" /> Must match current Revenue Tehsildar Income Certificate.
              </p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Social / Caste Category
              </label>
              <select
                value={profile.caste_category || 'General'}
                onChange={(e) => setProfile({ ...profile, caste_category: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
              >
                <option value="General">General / Unreserved</option>
                <option value="OBC">Other Backward Class (OBC - Non-Creamy Layer)</option>
                <option value="SC">Scheduled Caste (SC)</option>
                <option value="ST">Scheduled Tribe (ST)</option>
                <option value="EWS">Economically Weaker Section (EWS)</option>
                <option value="Minority">Minority Community (Muslim, Christian, Sikh, Buddhist, Jain, Parsi)</option>
              </select>
              <p className="text-[11px] text-slate-500 mt-1 flex items-center gap-1">
                <Info className="w-3 h-3 text-slate-400" /> Used to identify reserved scholarship quotas.
              </p>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-6 border-t border-slate-100 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Profile updates automatically sync with the eligibility rules engine.
          </span>
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold shadow-xs transition-all"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Saving Profile...' : 'Save Profile Changes'}
          </button>
        </div>
      </form>
    </div>
  );
};

