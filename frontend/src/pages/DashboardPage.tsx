import { useQuery } from '@tanstack/react-query'
import { patientsApi, predictionsApi } from '../services/api'
import { Link } from 'react-router-dom'

export default function DashboardPage() {
  const { data: patients = [] } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientsApi.getAll(0, 10),
  })

  const { data: predictions = [] } = useQuery({
    queryKey: ['predictions'],
    queryFn: () => predictionsApi.getAll(undefined, 0, 10),
  })

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-danger-600 bg-danger-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'low': return 'text-success-600 bg-success-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Overview of recent patients and predictions</p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card bg-gradient-to-br from-primary-500 to-primary-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-primary-100 text-sm">Total Patients</p>
              <p className="text-3xl font-bold mt-1">{patients.length}</p>
            </div>
            <div className="text-4xl opacity-50">👥</div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-success-500 to-success-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-success-100 text-sm">Predictions</p>
              <p className="text-3xl font-bold mt-1">{predictions.length}</p>
            </div>
            <div className="text-4xl opacity-50">🔬</div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm">High Risk Cases</p>
              <p className="text-3xl font-bold mt-1">
                {predictions.filter(p => 
                  p.alzheimer_prediction?.risk_level === 'high' || 
                  p.parkinson_prediction?.risk_level === 'high'
                ).length}
              </p>
            </div>
            <div className="text-4xl opacity-50">⚠️</div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Pending Review</p>
              <p className="text-3xl font-bold mt-1">
                {predictions.filter(p => !p.is_reviewed).length}
              </p>
            </div>
            <div className="text-4xl opacity-50">📋</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Patients */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Recent Patients</h2>
            <Link to="/patients" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View All →
            </Link>
          </div>
          
          <div className="space-y-3">
            {patients.slice(0, 5).map((patient) => (
              <Link
                key={patient.id}
                to={`/patients/${patient.id}`}
                className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition-colors"
              >
                <div>
                  <p className="font-medium">{patient.first_name} {patient.last_name}</p>
                  <p className="text-sm text-gray-600">ID: {patient.patient_id}</p>
                </div>
                <span className="text-gray-400">→</span>
              </Link>
            ))}
            
            {patients.length === 0 && (
              <p className="text-gray-500 text-center py-8">No patients yet</p>
            )}
          </div>
        </div>

        {/* Recent Predictions */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Recent Predictions</h2>
            <Link to="/predictions/new" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              New Prediction →
            </Link>
          </div>
          
          <div className="space-y-3">
            {predictions.slice(0, 5).map((prediction) => (
              <Link
                key={prediction.id}
                to={`/predictions/${prediction.id}`}
                className="block p-3 hover:bg-gray-50 rounded-lg transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <p className="font-medium">Patient ID: {prediction.patient_id}</p>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    prediction.is_reviewed ? 'bg-success-100 text-success-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {prediction.is_reviewed ? 'Reviewed' : 'Pending'}
                  </span>
                </div>
                
                <div className="flex space-x-4 text-sm">
                  {prediction.alzheimer_prediction && (
                    <span className={`px-2 py-1 rounded-full ${getRiskColor(prediction.alzheimer_prediction.risk_level)}`}>
                      Alzheimer's: {prediction.alzheimer_prediction.risk_level}
                    </span>
                  )}
                  {prediction.parkinson_prediction && (
                    <span className={`px-2 py-1 rounded-full ${getRiskColor(prediction.parkinson_prediction.risk_level)}`}>
                      Parkinson's: {prediction.parkinson_prediction.risk_level}
                    </span>
                  )}
                </div>
              </Link>
            ))}
            
            {predictions.length === 0 && (
              <p className="text-gray-500 text-center py-8">No predictions yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

