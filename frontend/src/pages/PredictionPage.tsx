import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { predictionsApi, patientsApi } from '../services/api'

export default function PredictionPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const preselectedPatient = searchParams.get('patient')
  
  const [patientId, setPatientId] = useState(preselectedPatient || '')
  const [diseaseType, setDiseaseType] = useState('both')

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
              onChange={(e) => setPatientId(e.target.value)}
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

