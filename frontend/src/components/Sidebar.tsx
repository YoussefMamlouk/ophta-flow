import React from 'react';

interface SidebarProps {
  selectedMachine: string;
  onMachineChange: (machine: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ selectedMachine, onMachineChange }) => {
  const machines = [
    { id: 'IOL700', name: 'IOL700', icon: '🔬', disabled: false },
    { id: 'Pentacam', name: 'Pentacam', icon: '📐', disabled: true }
  ];

  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-gradient-to-b from-blue-900 via-blue-800 to-indigo-900 shadow-2xl z-10 flex flex-col">
      {/* Logo and Title */}
      <div className="p-6 border-b border-blue-700/50">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center shadow-lg">
            <span className="text-2xl">👁️</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Ophta Flow</h1>
            <p className="text-xs text-blue-200/80">Data Extraction</p>
          </div>
        </div>
      </div>

      {/* Machine Selection */}
      <div className="flex-1 p-6 overflow-y-auto">
        <h2 className="text-xs font-semibold text-blue-200/60 uppercase tracking-wider mb-4">
          Machines
        </h2>
        <div className="space-y-2">
          {machines.map((machine) => (
            <button
              key={machine.id}
              onClick={() => !machine.disabled && onMachineChange(machine.id)}
              disabled={machine.disabled}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                machine.disabled
                  ? 'text-blue-200/40 cursor-not-allowed opacity-50'
                  : selectedMachine === machine.id
                  ? 'bg-white/20 text-white shadow-lg backdrop-blur-sm border border-white/30'
                  : 'text-blue-100 hover:bg-white/10 hover:text-white'
              }`}
            >
              <span className="text-xl">{machine.icon}</span>
              <span className="font-medium">{machine.name}</span>
              {machine.disabled && (
                <span className="ml-auto text-xs bg-white/10 px-2 py-1 rounded-full">Soon</span>
              )}
              {!machine.disabled && selectedMachine === machine.id && (
                <span className="ml-auto text-xs bg-white/20 px-2 py-1 rounded-full">✓</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-blue-700/50">
        <p className="text-xs text-blue-200/60 text-center">
          © 2025 Ophta Flow
        </p>
      </div>
    </div>
  );
};

export default Sidebar;

