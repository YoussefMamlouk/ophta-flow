import React from 'react';

interface MachineSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const MachineSelector: React.FC<MachineSelectorProps> = ({ value, onChange }) => {
  return (
    <div className="mb-6">
      <label htmlFor="machine-type" className="block text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
        <span className="text-lg">🔧</span>
        Type de Machine
      </label>
      <select
        id="machine-type"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-5 py-3 border-2 border-gray-200 rounded-xl shadow-sm bg-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 text-gray-700 font-medium cursor-pointer hover:border-blue-300"
      >
        <option value="IOL700">IOL700</option>
      </select>
    </div>
  );
};

export default MachineSelector;

