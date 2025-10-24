import React, { useState, useCallback } from 'react';
import type { ModelGenerationConfig } from '@app-types/index';
import apiService from '@services/api';
import './App.css';

const App: React.FC = () => {
  const [config, setConfig] = useState<ModelGenerationConfig>({
    inputType: 'text',
    inputText: '',
    outputFormat: 'stl',
    outputPath: './output',
    useWebSearch: false,
    useGitHub: false,
    useReddit: false,
  });

  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [outputFile, setOutputFile] = useState<string | null>(null);

  const handleInputChange = useCallback((field: keyof ModelGenerationConfig, value: any) => {
    setConfig((prev) => ({ ...prev, [field]: value }));
  }, []);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setMessage('Uploading file...');
      const uploadedPath = await apiService.uploadFile(file);
      handleInputChange('inputPath', uploadedPath);
      setMessage(`File uploaded: ${file.name}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    setProgress(0);
    setMessage('Starting generation...');
    setOutputFile(null);

    try {
      const response = await apiService.generateModel({ config });
      
      if (response.success) {
        setProgress(100);
        setMessage('Model generated successfully!');
        setOutputFile(response.outputPath || null);
      } else {
        setError(response.error || 'Generation failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>K1C-Board 3D Model Generator</h1>
        <p>Generate 3D models from text, images, videos, or CAD files</p>
      </header>

      <main className="app-main">
        <div className="config-section">
          <h2>Input Configuration</h2>
          
          <div className="form-group">
            <label htmlFor="inputType">Input Type:</label>
            <select
              id="inputType"
              value={config.inputType}
              onChange={(e) => handleInputChange('inputType', e.target.value)}
              disabled={isGenerating}
            >
              <option value="text">Text Description</option>
              <option value="image">Image</option>
              <option value="video">Video</option>
              <option value="cad">CAD File</option>
            </select>
          </div>

          {config.inputType === 'text' ? (
            <div className="form-group">
              <label htmlFor="inputText">Description:</label>
              <textarea
                id="inputText"
                value={config.inputText}
                onChange={(e) => handleInputChange('inputText', e.target.value)}
                placeholder="Describe the 3D model you want to generate..."
                rows={4}
                disabled={isGenerating}
              />
            </div>
          ) : (
            <div className="form-group">
              <label htmlFor="inputFile">Input File:</label>
              <input
                id="inputFile"
                type="file"
                onChange={handleFileUpload}
                accept={
                  config.inputType === 'image' ? 'image/*' :
                  config.inputType === 'video' ? 'video/*' :
                  '.step,.stp,.stl,.obj'
                }
                disabled={isGenerating}
              />
              {config.inputPath && (
                <p className="file-info">Selected: {config.inputPath}</p>
              )}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="outputFormat">Output Format:</label>
            <select
              id="outputFormat"
              value={config.outputFormat}
              onChange={(e) => handleInputChange('outputFormat', e.target.value)}
              disabled={isGenerating}
            >
              <option value="stl">STL (3D Printing)</option>
              <option value="step">STEP (CAD)</option>
              <option value="obj">OBJ (General)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="outputPath">Output Path:</label>
            <input
              id="outputPath"
              type="text"
              value={config.outputPath}
              onChange={(e) => handleInputChange('outputPath', e.target.value)}
              placeholder="./output"
              disabled={isGenerating}
            />
          </div>

          <h3>Data Sources</h3>
          <div className="checkbox-group">
            <label>
              <input
                type="checkbox"
                checked={config.useWebSearch}
                onChange={(e) => handleInputChange('useWebSearch', e.target.checked)}
                disabled={isGenerating}
              />
              Use Web Search
            </label>
            <label>
              <input
                type="checkbox"
                checked={config.useGitHub}
                onChange={(e) => handleInputChange('useGitHub', e.target.checked)}
                disabled={isGenerating}
              />
              Search GitHub
            </label>
            <label>
              <input
                type="checkbox"
                checked={config.useReddit}
                onChange={(e) => handleInputChange('useReddit', e.target.checked)}
                disabled={isGenerating}
              />
              Search Reddit
            </label>
          </div>

          <button
            className="generate-button"
            onClick={handleGenerate}
            disabled={isGenerating || (config.inputType === 'text' && !config.inputText)}
          >
            {isGenerating ? 'Generating...' : 'Generate 3D Model'}
          </button>
        </div>

        {(message || error || outputFile) && (
          <div className="status-section">
            {isGenerating && (
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${progress}%` }}
                />
              </div>
            )}
            
            {message && !error && (
              <p className="status-message">{message}</p>
            )}
            
            {error && (
              <p className="error-message">{error}</p>
            )}
            
            {outputFile && (
              <div className="output-info">
                <h3>Generation Complete!</h3>
                <p>Output file: <code>{outputFile}</code></p>
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>K1C-Board v1.0.0 - Automated 3D Model Generation</p>
      </footer>
    </div>
  );
};

export default App;
