export interface ModelGenerationConfig {
  inputType: 'text' | 'image' | 'video' | 'cad';
  inputPath?: string;
  inputText?: string;
  outputFormat: 'stl' | 'step' | 'obj';
  outputPath: string;
  useWebSearch: boolean;
  useGitHub: boolean;
  useReddit: boolean;
}

export interface GenerationProgress {
  status: 'idle' | 'processing' | 'completed' | 'error';
  message: string;
  progress: number;
  outputFile?: string;
}

export interface GenerationRequest {
  config: ModelGenerationConfig;
}

export interface GenerationResponse {
  success: boolean;
  message: string;
  outputPath?: string;
  error?: string;
}

export interface FileInfo {
  name: string;
  path: string;
  size: number;
  type: string;
}
