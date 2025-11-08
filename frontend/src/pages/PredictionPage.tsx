import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import {
  predictionsApi,
  patientsApi,
  imagingApi,
  type DicomUploadResponse,
} from '../services/api'

export default function PredictionPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const preselectedPatient = searchParams.get('patient')
  
  const [patientId, setPatientId] = useState(preselectedPatient || '')
  const [diseaseType, setDiseaseType] = useState('both')
  const [dicomFile, setDicomFile] = useState<File | null>(null)
  const [uploadedStudy, setUploadedStudy] = useState<DicomUploadResponse | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)

  const { data: patients = [] } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientsApi.getAll(0, 1000),
  })

  const createPrediction = useMutation({
    mutationFn: predictionsApi.create,
    onSuccess: (data) => {
      navigate(`/predictions/${data.id}`)
    },
  })

  const uploadDicom = useMutation({
    mutationFn: (payload: { patientId: number; file: File }) => imagingApi.uploadDicom(payload),
    onSuccess: (data) => {
      setUploadedStudy(data)
      setUploadError(null)
    },
    onError: (error: any) => {
      setUploadError(error?.response?.data?.detail || 'Failed to upload DICOM file')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!patientId) {
      alert('Please select a patient')
      return
    }

    createPrediction.mutate({
      patient_id: Number(patientId),
      disease_type: diseaseType,
    })
  }

  const handleDicomUpload = () => {
    if (!patientId) {
      alert('Please select a patient before uploading imaging data')
      return
    }
    if (!dicomFile) {
      alert('Please choose a DICOM (.dcm) file to upload')
      return
    }
    uploadDicom.mutate({ patientId: Number(patientId), file: dicomFile })
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">New Prediction</h1>
        <p className="text-gray-600">Create a new disease risk assessment</p>
      </div>

      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="label">Select Patient *</label>
            <select
              value={patientId}
              onChange={(e) => {
                setPatientId(e.target.value)
                setDicomFile(null)
                setUploadedStudy(null)
                setUploadError(null)
              }}
              className="input"
              required
            >
              <option value="">Choose a patient...</option>
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.first_name} {patient.last_name} (ID: {patient.patient_id})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label">Disease Type *</label>
            <select
              value={diseaseType}
              onChange={(e) => setDiseaseType(e.target.value)}
              className="input"
              required
            >
              <option value="both">Both Alzheimer's & Parkinson's</option>
              <option value="alzheimer">Alzheimer's Disease Only</option>
              <option value="parkinson">Parkinson's Disease Only</option>
            </select>
          </div>

          <div className="card border border-primary-200 rounded-lg p-4 space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">MRI DICOM Upload</h3>
              <p className="text-sm text-gray-600">
                Attach the latest MRI study in DICOM format. The file will be stored securely and linked to the
                patient&apos;s record.
              </p>
            </div>

            <div>
              <label className="label">Choose DICOM file (.dcm)</label>
              <input
                type="file"
                accept=".dcm,application/dicom"
                className="input"
                onChange={(event) => {
                  const file = event.target.files?.[0]
                  setDicomFile(file ?? null)
                  setUploadedStudy(null)
                  setUploadError(null)
                }}
              />
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleDicomUpload}
                disabled={uploadDicom.isPending}
              >
                {uploadDicom.isPending ? 'Uploading DICOM...' : 'Upload DICOM'}
              </button>
              {dicomFile && <span className="text-sm text-gray-600">{dicomFile.name}</span>}
            </div>

            {uploadError && (
              <div className="bg-danger-50 border border-danger-200 text-danger-700 rounded-lg p-3 text-sm">
                {uploadError}
              </div>
            )}

            {uploadedStudy && (
              <div className="bg-primary-50 border border-primary-200 rounded-lg p-3 text-sm text-primary-900">
                <div className="font-medium">DICOM stored successfully</div>
                <ul className="mt-2 space-y-1 list-disc list-inside">
                  <li>Study UID: {uploadedStudy.study_id}</li>
                  <li>Modality: {String(uploadedStudy.metadata?.modality ?? 'N/A')}</li>
                  <li>Study date: {String(uploadedStudy.metadata?.study_date ?? 'N/A')}</li>
                </ul>
              </div>
            )}
          </div>

          <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
            <h3 className="font-medium text-primary-900 mb-2">📊 Data Sources</h3>
            <p className="text-sm text-primary-700">
              The prediction will use the patient's latest medical records including:
            </p>
            <ul className="text-sm text-primary-700 mt-2 space-y-1 ml-4 list-disc">
              <li>Cognitive assessment scores (MMSE, MoCA)</li>
              <li>Biomarker levels (Amyloid-beta, Tau, Dopamine)</li>
              <li>MRI volumetric features</li>
              <li>Genetic markers (APOE status)</li>
            </ul>
          </div>

          {createPrediction.error && (
            <div className="bg-danger-50 border border-danger-200 text-danger-700 rounded-lg p-4 text-sm">
              {(createPrediction.error as any).response?.data?.detail || 'Failed to create prediction'}
            </div>
          )}

          <div className="flex space-x-4">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="btn btn-secondary flex-1"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createPrediction.isPending}
              className="btn btn-primary flex-1 disabled:opacity-50"
            >
              {createPrediction.isPending ? (
                <span className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                  Running Analysis...
                </span>
              ) : (
                '🔬 Run Prediction'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

