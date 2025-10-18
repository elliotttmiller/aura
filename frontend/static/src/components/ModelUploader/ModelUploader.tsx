import { useState, useRef, useCallback } from 'react'
import './ModelUploader.css'

interface ModelUploaderProps {
  onUploadSuccess: (modelUrl: string, modelName: string) => void
  onUploadError: (error: string) => void
}

interface UploadProgress {
  filename: string
  progress: number
  status: 'uploading' | 'processing' | 'success' | 'error'
  error?: string
  modelUrl?: string
}

export default function ModelUploader({ onUploadSuccess, onUploadError }: ModelUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return

    const file = files[0]
    
    // Validate file type
    const allowedTypes = ['.glb', '.gltf', '.obj', '.stl', '.3dm', '.ply']
    const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    
    if (!allowedTypes.includes(fileExt)) {
      onUploadError(`Invalid file type. Allowed: ${allowedTypes.join(', ')}`)
      return
    }

    // Validate file size (50MB)
    const maxSizeMB = 50
    const fileSizeMB = file.size / (1024 * 1024)
    if (fileSizeMB > maxSizeMB) {
      onUploadError(`File too large. Maximum size: ${maxSizeMB}MB`)
      return
    }

    uploadFile(file)
  }, [onUploadError])

  const uploadFile = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    setUploadProgress({
      filename: file.name,
      progress: 0,
      status: 'uploading'
    })

    try {
      const response = await fetch('/api/upload/model', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Upload failed')
      }

      const result = await response.json()

      if (result.success) {
        setUploadProgress({
          filename: file.name,
          progress: 100,
          status: result.status === 'ready' ? 'success' : 'processing',
          modelUrl: result.model_url
        })

        if (result.status === 'ready' && result.model_url) {
          // Model is ready to use
          onUploadSuccess(result.model_url, file.name)
        } else {
          // Model needs conversion
          setUploadProgress(prev => prev ? {
            ...prev,
            status: 'processing'
          } : null)
        }
      } else {
        throw new Error(result.error || 'Upload failed')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed'
      setUploadProgress({
        filename: file.name,
        progress: 0,
        status: 'error',
        error: errorMessage
      })
      onUploadError(errorMessage)
    }
  }

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    handleFileSelect(e.dataTransfer.files)
  }, [handleFileSelect])

  const handleClick = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(e.target.files)
  }, [handleFileSelect])

  return (
    <div className="model-uploader">
      <div
        className={`upload-dropzone ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".glb,.gltf,.obj,.stl,.3dm,.ply"
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />
        
        {!uploadProgress && (
          <>
            <div className="upload-icon">📁</div>
            <div className="upload-text">
              <strong>Drop 3D model here or click to browse</strong>
              <p>Supported formats: GLB, GLTF, OBJ, STL, 3DM, PLY (max 50MB)</p>
            </div>
          </>
        )}

        {uploadProgress && (
          <div className="upload-progress">
            <div className="progress-filename">{uploadProgress.filename}</div>
            
            {uploadProgress.status === 'uploading' && (
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${uploadProgress.progress}%` }}
                />
              </div>
            )}

            {uploadProgress.status === 'processing' && (
              <div className="progress-status">
                <div className="spinner" />
                <span>Converting to GLB format...</span>
              </div>
            )}

            {uploadProgress.status === 'success' && (
              <div className="progress-status success">
                <span>✓ Upload successful!</span>
              </div>
            )}

            {uploadProgress.status === 'error' && (
              <div className="progress-status error">
                <span>✗ {uploadProgress.error}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
