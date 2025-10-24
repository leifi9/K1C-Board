import axios, { AxiosInstance } from 'axios';
import type { GenerationRequest, GenerationResponse, GenerationProgress } from '@app-types/index';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      timeout: 300000, // 5 minutes for long-running operations
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async generateModel(request: GenerationRequest): Promise<GenerationResponse> {
    try {
      const response = await this.api.post<GenerationResponse>('/generate', request);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || error.message);
      }
      throw error;
    }
  }

  async getProgress(jobId: string): Promise<GenerationProgress> {
    try {
      const response = await this.api.get<GenerationProgress>(`/progress/${jobId}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || error.message);
      }
      throw error;
    }
  }

  async uploadFile(file: File): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await this.api.post<{ path: string }>('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data.path;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || error.message);
      }
      throw error;
    }
  }
}

export default new ApiService();
