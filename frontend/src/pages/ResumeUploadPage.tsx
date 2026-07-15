import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { resumeApi } from '../services/api'
import { Upload, CheckCircle, AlertCircle, Loader2, FileText, Eye, Trash2, Sparkles } from 'lucide-react'

export default function ResumeUploadPage() {
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [result, setResult] = useState<{ id: string; filename: string; status: string; extracted_name?: string; extracted_phone?: string; extracted_email?: string } | null>(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const STEPS = [
    { id: 'upload', label: '上传文件', icon: Upload },
    { id: 'parse', label: '解析内容', icon: FileText },
    { id: 'extract', label: '提取信息', icon: Sparkles },
    { id: 'complete', label: '完成', icon: CheckCircle },
  ]

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) {
      setSelectedFile(file)
      await upload(file)
    }
  }, [])

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      await upload(file)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const upload = async (file: File) => {
    setUploading(true)
    setUploadProgress(0)
    setError('')
    setCurrentStep('upload')

    try {
      setUploadProgress(20)
      setCurrentStep('parse')
      setUploadProgress(50)

      const res = await resumeApi.upload(file)
      
      setUploadProgress(80)
      setCurrentStep('extract')
      setUploadProgress(90)

      setResult(res.data)
      setCurrentStep('complete')
      setUploadProgress(100)
    } catch (err: any) {
      setError(err.response?.data?.detail || '上传失败')
    } finally {
      setUploading(false)
    }
  }

  const resetUpload = () => {
    setSelectedFile(null)
    setResult(null)
    setError('')
    setUploadProgress(0)
    setCurrentStep('')
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">上传简历</h1>
        <p className="text-gray-500 mt-2">AI 将自动解析您的简历，提取关键信息并进行智能诊断</p>
      </div>

      {/* 进度条 */}
      {uploading && (
        <div className="mb-6">
          <div className="flex justify-between text-xs text-gray-500 mb-2">
            {STEPS.map((step) => (
              <div key={step.id} className={`flex items-center gap-1 ${currentStep === step.id ? 'text-primary-600 font-medium' : ''}`}>
                <step.icon className="w-3.5 h-3.5" />
                <span>{step.label}</span>
              </div>
            ))}
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-primary-500 to-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-2xl p-10 text-center transition-all ${
          dragOver ? 'border-primary-500 bg-primary-50 shadow-lg' : 'border-gray-300 bg-white hover:border-primary-400'
        }`}
      >
        {uploading ? (
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center mb-4">
              <Loader2 className="w-8 h-8 text-primary-600 animate-spin" />
            </div>
            <p className="text-gray-900 font-medium text-lg">正在{STEPS.find(s => s.id === currentStep)?.label || '处理'}...</p>
            <p className="text-sm text-gray-500 mt-2">请稍候，AI 正在分析您的简历内容</p>
          </div>
        ) : result ? (
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <p className="text-gray-900 font-semibold text-lg">{result.filename}</p>
            <p className="text-sm text-gray-500 mt-1">解析完成</p>
            
            {/* 提取信息预览 */}
            {result.extracted_name || result.extracted_phone || result.extracted_email ? (
              <div className="mt-6 p-4 bg-gray-50 rounded-xl w-full max-w-xs">
                <p className="text-xs text-gray-500 mb-3 font-medium">提取的信息</p>
                <div className="space-y-2 text-sm">
                  {result.extracted_name && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">姓名</span>
                      <span className="text-gray-900 font-medium">{result.extracted_name}</span>
                    </div>
                  )}
                  {result.extracted_phone && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">电话</span>
                      <span className="text-gray-900 font-medium">{result.extracted_phone}</span>
                    </div>
                  )}
                  {result.extracted_email && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">邮箱</span>
                      <span className="text-gray-900 font-medium">{result.extracted_email}</span>
                    </div>
                  )}
                </div>
              </div>
            ) : null}

            <div className="mt-6 flex space-x-3">
              <button onClick={() => navigate('/diagnosis', { state: { resumeId: result.id } })} className="btn-primary">
                <Eye className="w-4 h-4 mr-2" />
                查看诊断报告
              </button>
              <button onClick={resetUpload} className="btn-secondary flex items-center">
                <Trash2 className="w-4 h-4 mr-2" />
                重新上传
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-4">
              <Upload className="w-8 h-8 text-gray-400" />
            </div>
            <p className="text-gray-600 mb-2">拖拽简历到这里，或点击上传</p>
            <p className="text-xs text-gray-400 mb-6">支持 PDF、Word、TXT 格式，最大 10MB</p>
            <label className="btn-primary cursor-pointer inline-flex items-center">
              <input type="file" className="hidden" onChange={handleFile} accept=".pdf,.docx,.txt,.png,.jpg,.jpeg" />
              <FileText className="w-4 h-4 mr-2" />
              选择文件
            </label>
          </>
        )}
      </div>

      {selectedFile && !uploading && !result && (
        <div className="mt-4 p-3 bg-gray-50 rounded-xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900 truncate max-w-xs">{selectedFile.name}</p>
              <p className="text-xs text-gray-500">{formatFileSize(selectedFile.size)}</p>
            </div>
          </div>
          <button onClick={resetUpload} className="text-gray-400 hover:text-red-500">
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-50 rounded-xl flex items-center text-red-500">
          <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}
    </div>
  )
}
