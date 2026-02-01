import { useQuery } from '@tanstack/react-query'
import { patientsApi, predictionsApi, reportsApi, backendHealthApi } from '../services/api'
import { Link } from 'react-router-dom'
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function DashboardPage() {
  // Backend connection status (refetch every 30s)
  const { data: health, isSuccess: backendConnected, isError: backendError } = useQuery({
    queryKey: ['backend-health'],
    queryFn: () => backendHealthApi.check(),
    refetchInterval: 30_000,
    retry: 1,
    staleTime: 10_000,
  })

  const { data: allPatients = [], isLoading: patientsLoading } = useQuery({
    queryKey: ['patients-all'],
    queryFn: () => patientsApi.getAll(0, 1000),
  })

  const { data: patients = [] } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientsApi.getAll(0, 10),
  })

  const { data: allPredictions = [], isLoading: predictionsLoading } = useQuery({
    queryKey: ['predictions-all'],
    queryFn: () => predictionsApi.getAll(undefined, 0, 1000),
  })

  const { data: predictions = [] } = useQuery({
    queryKey: ['predictions'],
    queryFn: () => predictionsApi.getAll(undefined, 0, 10),
  })

  // Fetch reports data for charts
  const { data: trendsData } = useQuery({
    queryKey: ['predictions-trend'],
    queryFn: () => reportsApi.getPredictionsTrend(7),
  })

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-danger-600 bg-danger-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'low': return 'text-success-600 bg-success-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  // Calculate statistics
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const newPatientsToday = allPatients.filter((p: any) => {
    const createdDate = new Date(p.created_at)
    createdDate.setHours(0, 0, 0, 0)
    return createdDate.getTime() === today.getTime()
  }).length

  const newPredictionsToday = allPredictions.filter((p: any) => {
    const createdDate = new Date(p.created_at)
    createdDate.setHours(0, 0, 0, 0)
    return createdDate.getTime() === today.getTime()
  }).length

  const highRiskCases = allPredictions.filter((p: any) => 
    p.alzheimer_risk_level === 'high' || 
    p.parkinson_risk_level === 'high' ||
    (p.alzheimer_prediction?.risk_level === 'high') ||
    (p.parkinson_prediction?.risk_level === 'high')
  )

  const alzheimerDiagnoses = allPredictions.filter((p: any) => 
    p.alzheimer_risk_level === 'high' || p.alzheimer_prediction?.risk_level === 'high'
  ).length

  const parkinsonDiagnoses = allPredictions.filter((p: any) => 
    p.parkinson_risk_level === 'high' || p.parkinson_prediction?.risk_level === 'high'
  ).length

  // Process data for time series charts (last 7 days)
  const getLast7Days = () => {
    const days = []
    for (let i = 6; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      date.setHours(0, 0, 0, 0)
      days.push(date)
    }
    return days
  }

  const dailyData = getLast7Days().map(date => {
    const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    const patientsOnDate = allPatients.filter((p: any) => {
      const createdDate = new Date(p.created_at)
      createdDate.setHours(0, 0, 0, 0)
      return createdDate.getTime() === date.getTime()
    }).length
    
    const predictionsOnDate = allPredictions.filter((p: any) => {
      const createdDate = new Date(p.created_at)
      createdDate.setHours(0, 0, 0, 0)
      return createdDate.getTime() === date.getTime()
    }).length

    return {
      date: dateStr,
      patients: patientsOnDate,
      predictions: predictionsOnDate,
    }
  })

  // Alerts (High risk patients)
  const alerts = highRiskCases.slice(0, 5).map((prediction: any) => ({
    id: prediction.id,
    type: 'high_risk',
    message: `High risk case detected for patient ${prediction.patient_id}`,
    severity: 'high',
    timestamp: prediction.created_at,
  }))

  // Recent Activity
  const recentActivity = [
    ...allPredictions.slice(0, 5).map((p: any) => ({
      id: p.id,
      type: 'prediction',
      message: `New prediction created for patient ${p.patient_id}`,
      timestamp: p.created_at,
    })),
    ...allPatients.slice(0, 3).map((p: any) => ({
      id: p.id,
      type: 'patient',
      message: `New patient registered: ${p.first_name} ${p.last_name}`,
      timestamp: p.created_at,
    })),
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()).slice(0, 8)

  const dataLoading = patientsLoading || predictionsLoading

  return (
    <div>
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📊 Dashboard</h1>
          <p className="text-gray-600">Overview of system activity and key metrics</p>
        </div>
        {/* Backend connection status */}
        <div className="flex items-center gap-2">
          {backendConnected && health?.status === 'healthy' && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-green-100 text-green-800">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              Backend connected
            </span>
          )}
          {(backendError || (health && health.status !== 'healthy')) && (
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium bg-amber-100 text-amber-800">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              Backend offline / mock data
            </span>
          )}
        </div>
      </div>

      {dataLoading && (
        <div className="mb-4 p-3 rounded-lg bg-blue-50 text-blue-800 text-sm flex items-center gap-2">
          <div className="inline-block animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent" />
          Loading dashboard data…
        </div>
      )}

      {/* Enhanced Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <div className="card bg-gradient-to-br from-primary-500 to-primary-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-primary-100 text-sm">Total Patients</p>
              <p className="text-3xl font-bold mt-1">{allPatients.length}</p>
              <p className="text-primary-200 text-xs mt-1">+{newPatientsToday} today</p>
            </div>
            <div className="text-4xl opacity-50">👥</div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-success-500 to-success-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-success-100 text-sm">Predictions</p>
              <p className="text-3xl font-bold mt-1">{allPredictions.length}</p>
              <p className="text-success-200 text-xs mt-1">+{newPredictionsToday} today</p>
            </div>
            <div className="text-4xl opacity-50">🔬</div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-danger-500 to-danger-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-danger-100 text-sm">High Risk</p>
              <p className="text-3xl font-bold mt-1">{highRiskCases.length}</p>
            </div>
            <div className="text-4xl opacity-50">⚠️</div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Alzheimer</p>
              <p className="text-3xl font-bold mt-1">{alzheimerDiagnoses}</p>
            </div>
            <div className="text-4xl opacity-50">🧠</div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-yellow-500 to-yellow-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm">Parkinson</p>
              <p className="text-3xl font-bold mt-1">{parkinsonDiagnoses}</p>
            </div>
            <div className="text-4xl opacity-50">🎯</div>
          </div>
        </div>
      </div>

      {/* Time Series Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Daily Data Entry (Last 7 Days)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="patients" stackId="1" stroke="#3b82f6" fill="#3b82f6" name="New Patients" />
              <Area type="monotone" dataKey="predictions" stackId="2" stroke="#10b981" fill="#10b981" name="New Predictions" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Daily Predictions Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="predictions" stroke="#10b981" strokeWidth={2} name="Daily Predictions" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alerts and Activity Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Alerts */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">🔔 Urgent Alerts</h2>
            {alerts.length > 0 && (
              <span className="px-2 py-1 bg-danger-100 text-danger-800 text-xs rounded-full">
                {alerts.length} alerts
              </span>
            )}
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {alerts.length > 0 ? (
              alerts.map((alert: any) => (
                <div
                  key={alert.id}
                  className="p-3 bg-danger-50 border-l-4 border-danger-500 rounded"
                >
                  <p className="text-sm font-medium text-danger-900">{alert.message}</p>
                  <p className="text-xs text-danger-600 mt-1">
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No urgent alerts</p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">🕐 Recent Activity</h2>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {recentActivity.length > 0 ? (
              recentActivity.map((activity: any) => (
                <div
                  key={activity.id}
                  className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
                >
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    activity.type === 'prediction' ? 'bg-green-500' : 'bg-blue-500'
                  }`} />
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">{activity.message}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(activity.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No recent activity</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Patients and Predictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Patients */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Recent Patients</h2>
            <Link to="/patients" className="text-primary-600 hover:text-primary-800 text-sm">
              View All →
            </Link>
          </div>
          <div className="space-y-3">
            {patients.length > 0 ? (
              patients.slice(0, 5).map((patient: any) => (
                <Link
                  key={patient.id}
                  to={`/patients/${patient.id}`}
                  className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">
                        {patient.first_name} {patient.last_name}
                      </p>
                      <p className="text-sm text-gray-500">{patient.patient_id}</p>
                    </div>
                    <p className="text-xs text-gray-400">
                      {new Date(patient.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </Link>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No patients yet</p>
              </div>
            )}
          </div>
        </div>

        {/* Recent Predictions */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Recent Predictions</h2>
            <Link to="/predictions/new" className="text-primary-600 hover:text-primary-800 text-sm">
              New Prediction →
            </Link>
          </div>
          <div className="space-y-3">
            {predictions.length > 0 ? (
              predictions.slice(0, 5).map((prediction: any) => (
                <Link
                  key={prediction.id}
                  to={`/predictions/${prediction.id}`}
                  className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">
                        Patient {prediction.patient_id}
                      </p>
                      <div className="flex items-center space-x-2 mt-1">
                        {(prediction.alzheimer_risk_level || prediction.alzheimer_prediction?.risk_level) && (
                          <span className={`px-2 py-1 text-xs rounded ${
                            getRiskColor(prediction.alzheimer_risk_level || prediction.alzheimer_prediction?.risk_level)
                          }`}>
                            Alzheimer: {prediction.alzheimer_risk_level || prediction.alzheimer_prediction?.risk_level}
                          </span>
                        )}
                        {(prediction.parkinson_risk_level || prediction.parkinson_prediction?.risk_level) && (
                          <span className={`px-2 py-1 text-xs rounded ${
                            getRiskColor(prediction.parkinson_risk_level || prediction.parkinson_prediction?.risk_level)
                          }`}>
                            Parkinson: {prediction.parkinson_risk_level || prediction.parkinson_prediction?.risk_level}
                          </span>
                        )}
                      </div>
                    </div>
                    <p className="text-xs text-gray-400">
                      {new Date(prediction.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </Link>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No predictions yet</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

