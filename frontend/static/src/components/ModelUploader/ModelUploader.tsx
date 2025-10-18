import { useState, useRef, useCallback } from 'react'
import './ModelUploader.css'

interface ModelUploaderProps {
  onUploadSuccess: (modelUrl: string, modelName: string) => void
  onUploadError: (error: string) => void
}

type UploadPhase = 'idle' | 'uploading' | 'processing' | 'success' | 'error'

interface UploadState {
  phase: UploadPhase
  message?: string
  fileName?: string
}

const ACCEPTED_EXTENSIONS = ['.glb', '.gltf', '.obj', '.stl', '.3dm', '.ply']
const MAX_SIZE_MB = 50

export default function ModelUploader({ onUploadSuccess, onUploadError }: ModelUploaderProps) {
  const [uploadState, setUploadState] = useState<UploadState>({ phase: 'idle' })
  const fileInputRef = useRef<HTMLInputElement>(null)

  const resetState = useCallback(() => {
    setUploadState({ phase: 'idle' })
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }, [])

  const validateFile = useCallback((file: File) => {
    const extension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))
    if (!ACCEPTED_EXTENSIONS.includes(extension)) {
      throw new Error(`Unsupported format. Allowed: ${ACCEPTED_EXTENSIONS.join(', ')}`)
    }

    const sizeMb = file.size / (1024 * 1024)
    if (sizeMb > MAX_SIZE_MB) {
      throw new Error(`File too large. Maximum size is ${MAX_SIZE_MB}MB`)
    }
  }, [])

  const uploadFile = useCallback(async (file: File) => {
    try {
      validateFile(file)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Invalid file'
      setUploadState({ phase: 'error', message, fileName: file.name })
      onUploadError(message)
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    setUploadState({ phase: 'uploading', fileName: file.name })

    try {
      const response = await fetch('/api/upload/model', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}))
        throw new Error(errorBody.detail || 'Upload failed')
      }

      const result = await response.json()

      if (!result.success) {
        throw new Error(result.error || 'Upload failed')
      }

      if (result.status === 'ready' && result.model_url) {
        setUploadState({ phase: 'success', fileName: file.name, message: 'Upload complete' })
        onUploadSuccess(result.model_url, file.name)
      } else {
        setUploadState({ phase: 'processing', fileName: file.name, message: 'Converting model…' })
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed'
      setUploadState({ phase: 'error', message, fileName: file.name })
      onUploadError(message)
    }
  }, [onUploadError, onUploadSuccess, validateFile])

  const handleFileSelection = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) {
      return
    }
    uploadFile(files[0])
  }, [uploadFile])

  return (
    <div className="model-uploader">
      <div
        className="upload-dropzone"
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(',')}
          onChange={(event) => handleFileSelection(event.target.files)}
          hidden
        />

        {uploadState.phase === 'idle' && (
          <>
            <div className="upload-icon">📁</div>
            <div className="upload-text">
              <strong>Upload a 3D model</strong>
              <p>Supported: GLB, GLTF, OBJ, STL, 3DM, PLY (max {MAX_SIZE_MB}MB)</p>
            </div>
          </>
        )}

        {uploadState.phase === 'uploading' && (
          <div className="upload-status uploading">
            <span className="spinner" />
            <div>
              <strong>Uploading</strong>
              <p>{uploadState.fileName}</p>
            </div>
          </div>
        )}

        {uploadState.phase === 'processing' && (
          <div className="upload-status processing">
            <span className="spinner" />
            <div>
              <strong>Processing</strong>
              <p>{uploadState.message}</p>
            </div>
          </div>
        )}

        {uploadState.phase === 'success' && (
          <div className="upload-status success">
            <span>✅</span>
            <div>
              <strong>Ready to view</strong>
              <p>{uploadState.fileName}</p>
            </div>
          </div>
        )}

        {uploadState.phase === 'error' && (
          <div className="upload-status error">
            <span>⚠️</span>
            <div>
              <strong>Upload failed</strong>
              <p>{uploadState.message}</p>
            </div>
            <button className="retry-btn" type="button" onClick={resetState}>
              Try again
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
