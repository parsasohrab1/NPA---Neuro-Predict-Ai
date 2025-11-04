import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { patientsApi, predictionsApi, analyticsApi } from '../services/api'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function LongitudinalPage() {
  const [selectedPatient, setSelectedPatient] = useState<string>('')

  const { data: patients = [] } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientsApi.getAll(0, 1000),
  })

  const { data: predictions = [] } = useQuery({
    queryKey: ['predictions', selectedPatient],
    queryFn: () => predictionsApi.getAll(selectedPatient ? Number(selectedPatient) : undefined, 0, 1000),
    enabled: !!selectedPatient,
  })

  // Fetch longitudinal data from API
  const { data: longitudinalData } = useQuery({
    queryKey: ['longitudinal', selectedPatient],
    queryFn: () => analyticsApi.getLongitudinalData(Number(selectedPatient)),
    enabled: !!selectedPatient,
  })

  // Transform API timeline data
  const timelineData = longitudinalData?.timeline?.map((item: any) => ({
    date: new Date(item.date).toLocaleDateString(),
    event: `Prediction #${item.prediction_id}`,
    type: 'prediction',
    alzheimer: item.alzheimer_risk_score || 0,
    parkinson: item.parkinson_risk_score || 0,
  })) || []

  const trendData = longitudinalData?.timeline?.map((item: any) => ({
    date: new Date(item.date).toLocaleDateString(),
    alzheimer: item.alzheimer_risk_score || 0,
    parkinson: item.parkinson_risk_score || 0,
  })) || []

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📅 Longitudinal Tracking</h1>
        <p className="text-gray-600">Track patient progress over time</p>
      </div>

      {/* Patient Selection */}
      <div className="card mb-6">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Select Patient:</label>
          <select
            value={selectedPatient}
            onChange={(e) => setSelectedPatient(e.target.value)}
            className="flex-1 max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">-- Select a patient --</option>
            {patients.map((patient: any) => (
              <option key={patient.id} value={patient.id}>
                {patient.first_name} {patient.last_name} ({patient.patient_id})
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedPatient ? (
        <>
          {/* Timeline */}
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-4">Progress Timeline</h2>
            <div className="relative">
              {timelineData.map((item, index) => (
                <div key={index} className="flex items-start mb-6">
                  <div className="flex flex-col items-center mr-4">
                    <div className={`w-4 h-4 rounded-full ${
                      item.type === 'visit' ? 'bg-blue-500' : 'bg-green-500'
                    }`} />
                    {index < timelineData.length - 1 && (
                      <div className="w-0.5 h-full bg-gray-300 mt-2" />
                    )}
                  </div>
                  <div className="flex-1 pb-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-gray-900">{item.event}</p>
                        <p className="text-sm text-gray-500">{item.date}</p>
                      </div>
                                                <div className="flex space-x-4 text-sm">
                            {item.alzheimer !== undefined && (
                              <span className={`px-2 py-1 rounded text-xs ${
                                item.alzheimer > 0.7 ? 'bg-red-100 text-red-800' : 
                                item.alzheimer > 0.4 ? 'bg-yellow-100 text-yellow-800' : 
                                'bg-green-100 text-green-800'
                              }`}>
                                Alzheimer: {(item.alzheimer * 100).toFixed(0)}%
                              </span>
                            )}
                            {item.parkinson !== undefined && (
                              <span className={`px-2 py-1 rounded text-xs ${
                                item.parkinson > 0.7 ? 'bg-red-100 text-red-800' : 
                                item.parkinson > 0.4 ? 'bg-yellow-100 text-yellow-800' : 
                                'bg-green-100 text-green-800'
                              }`}>
                                Parkinson: {(item.parkinson * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Trend Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Cognitive Scores Trend</h3>
                                <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Area type="monotone" dataKey="alzheimer" stroke="#ef4444" fill="#ef4444" name="Alzheimer Risk Score" />
                      <Area type="monotone" dataKey="parkinson" stroke="#fbbf24" fill="#fbbf24" name="Parkinson Risk Score" />
                    </AreaChart>
                  </ResponsiveContainer>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Risk Score Progression</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={predictions.map((p: any) => ({
                  date: new Date(p.created_at).toLocaleDateString(),
                  alzheimer: p.alzheimer_risk_score || 0,
                  parkinson: p.parkinson_risk_score || 0,
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="alzheimer" stroke="#ef4444" name="Alzheimer Risk" />
                  <Line type="monotone" dataKey="parkinson" stroke="#fbbf24" name="Parkinson Risk" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Progress Summary */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Progress Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-gray-600">Total Predictions</p>
                <p className="text-2xl font-bold text-blue-600">
                  {longitudinalData?.total_predictions || predictions.length}
                </p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm text-gray-600">Last Update</p>
                <p className="text-sm font-medium text-green-600">
                  {timelineData.length > 0 
                    ? timelineData[timelineData.length - 1]?.date
                    : 'N/A'
                  }
                </p>
              </div>
              <div className="p-4 bg-yellow-50 rounded-lg">
                <p className="text-sm text-gray-600">Tracking Period</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {timelineData.length > 0 
                    ? timelineData.length
                    : '0'
                  } events
                </p>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="card">
          <div className="text-center py-12">
            <p className="text-gray-600">Please select a patient to view longitudinal tracking data</p>
          </div>
        </div>
      )}
    </div>
  )
}
