import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { patientsApi, predictionsApi } from '../services/api'

export default function PatientDetailPage() {
  const { id } = useParams<{ id: string }>()
  
  const { data: patient, isLoading: patientLoading } = useQuery({
    queryKey: ['patient', id],
    queryFn: () => patientsApi.getById(Number(id)),
    enabled: !!id,
  })

  const { data: predictions = [] } = useQuery({
    queryKey: ['predictions', id],
    queryFn: () => predictionsApi.getAll(Number(id)),
    enabled: !!id,
  })

  if (patientLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary-600 border-t-transparent"></div>
        <p className="mt-2 text-gray-600">Loading patient details...</p>
      </div>
    )
  }

  if (!patient) {
    return <div className="text-center py-12">Patient not found</div>
  }

  const age = Math.floor(
    (Date.now() - new Date(patient.date_of_birth).getTime()) / (365.25 * 24 * 60 * 60 * 1000)
  )

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <Link to="/patients" className="text-primary-600 hover:text-primary-700 text-sm font-medium mb-4 inline-block">
          ← Back to Patients
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {patient.first_name} {patient.last_name}
            </h1>
            <p className="text-gray-600 mt-1">Patient ID: {patient.patient_id}</p>
          </div>
          <Link to={`/predictions/new?patient=${patient.id}`} className="btn btn-primary">
            🔬 New Prediction
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Patient Information */}
        <div className="lg:col-span-2 card">
          <h2 className="text-xl font-bold mb-4">Patient Information</h2>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Gender</p>
              <p className="font-medium capitalize">{patient.gender}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Age</p>
              <p className="font-medium">{age} years</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Date of Birth</p>
              <p className="font-medium">{new Date(patient.date_of_birth).toLocaleDateString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Education Years</p>
              <p className="font-medium">{patient.education_years || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Email</p>
              <p className="font-medium">{patient.email || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Phone</p>
              <p className="font-medium">{patient.phone || 'N/A'}</p>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Quick Stats</h2>
          
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">Total Predictions</p>
              <p className="text-2xl font-bold text-primary-600">{predictions.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Latest Prediction</p>
              <p className="text-sm font-medium">
                {predictions[0] 
                  ? new Date(predictions[0].created_at).toLocaleDateString()
                  : 'No predictions yet'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Predictions History */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Prediction History</h2>
        
        {predictions.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">No predictions yet for this patient</p>
            <Link to={`/predictions/new?patient=${patient.id}`} className="btn btn-primary">
              Create First Prediction
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {predictions.map((prediction) => (
              <Link
                key={prediction.id}
                to={`/predictions/${prediction.id}`}
                className="block p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">
                    {new Date(prediction.created_at).toLocaleString()}
                  </span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    prediction.is_reviewed ? 'bg-success-100 text-success-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {prediction.is_reviewed ? 'Reviewed' : 'Pending Review'}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  {prediction.alzheimer_prediction && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">Alzheimer's Risk</p>
                      <div className="flex items-center mt-1">
                        <span className={`text-lg font-bold ${
                          prediction.alzheimer_prediction.risk_level === 'high' ? 'text-danger-600' :
                          prediction.alzheimer_prediction.risk_level === 'medium' ? 'text-yellow-600' :
                          'text-success-600'
                        }`}>
                          {(prediction.alzheimer_prediction.risk_score * 100).toFixed(1)}%
                        </span>
                        <span className="ml-2 text-sm capitalize">
                          ({prediction.alzheimer_prediction.risk_level})
                        </span>
                      </div>
                    </div>
                  )}
                  
                  {prediction.parkinson_prediction && (
                    <div>
                      <p className="text-sm font-medium text-gray-700">Parkinson's Risk</p>
                      <div className="flex items-center mt-1">
                        <span className={`text-lg font-bold ${
                          prediction.parkinson_prediction.risk_level === 'high' ? 'text-danger-600' :
                          prediction.parkinson_prediction.risk_level === 'medium' ? 'text-yellow-600' :
                          'text-success-600'
                        }`}>
                          {(prediction.parkinson_prediction.risk_score * 100).toFixed(1)}%
                        </span>
                        <span className="ml-2 text-sm capitalize">
                          ({prediction.parkinson_prediction.risk_level})
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

