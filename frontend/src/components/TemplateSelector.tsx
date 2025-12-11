import React from 'react';

interface TemplateSelectorProps {
  selectedTemplate: string;
  onSelectTemplate: (template: string) => void;
}

const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  selectedTemplate,
  onSelectTemplate,
}) => {
  const templates = ['modern', 'classic', 'creative'];

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Choose Template</h2>
      <div className="grid grid-cols-3 gap-4">
        {templates.map((template) => (
          <button
            key={template}
            onClick={() => onSelectTemplate(template)}
            className={`p-4 border-2 rounded-lg transition-all ${
              selectedTemplate === template
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <div className="text-sm font-medium capitalize">{template}</div>
            <div className="mt-2 text-xs text-gray-500">Preview coming soon</div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default TemplateSelector;

