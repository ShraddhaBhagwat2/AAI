import React from 'react';
import Navbar from '../components/Navbar';
import CitizenNav from '../components/CitizenNav';

export default function CitizenStatus(){
  const sample = {id:'GR-2024-99', progress:3, steps:['Received','Triaged','Assigned','In-Field Action','Resolved']};
  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <div className="max-w-4xl mx-auto p-6">
        <CitizenNav />
        <h2 className="text-xl font-bold mb-4">Status Tracker</h2>
        <div className="bg-white p-6 rounded-xl border border-slate-100">
          <div className="text-sm text-slate-500">Ticket ID: {sample.id}</div>
          <div className="mt-4">
            <div className="flex items-center justify-between text-xs text-slate-500 mb-2">
              {sample.steps.map((s,i)=>(<div key={s} className={`flex-1 text-center ${i<=sample.progress? 'text-slate-900 font-bold':''}`}>{s}</div>))}
            </div>
            <div className="relative h-2 bg-slate-200 rounded-full overflow-hidden">
              <div className="absolute left-0 top-0 bottom-0 bg-orange-500 rounded-full" style={{width:`${((sample.progress+1)/sample.steps.length)*100}%`}} />
            </div>
          </div>
          <div className="mt-4 text-sm text-slate-600">Current stage: <strong>{sample.steps[sample.progress]}</strong></div>
        </div>
      </div>
    </div>
  );
}
