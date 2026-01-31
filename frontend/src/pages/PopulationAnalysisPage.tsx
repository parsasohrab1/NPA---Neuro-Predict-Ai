import { useQuery } from '@tanstack/react-query'
import { patientsApi, predictionsApi, analyticsApi } from '../services/api'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function PopulationAnalysisPage() {
  const { data: patients = [] } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientsApi.getAll(0, 1000),
  })

  const { data: predictions = [] } = useQuery({
    queryKey: ['predictions'],
    queryFn: () => predictionsApi.getAll(undefined, 0, 1000),
  })

  // Fetch analytics data from API
  const { data: ageDistribution } = useQuery({
    queryKey: ['age-distribution'],
    queryFn: () => analyticsApi.getAgeDistribution(),
  })

  const { data: genderDistribution } = useQuery({
    queryKey: ['gender-distribution'],
    queryFn: () => analyticsApi.getGenderDistribution(),
  })

  const { data: populationStats } = useQuery({
    queryKey: ['population-statistics'],
    queryFn: () => analyticsApi.getPopulationStatistics(),
  })

  // Use API data or fallback to local calculation
  const ageGroups = ageDistribution?.distribution || [
    { age_group: '40-50', count: 0 },
    { age_group: '50-60', count: 0 },
    { age_group: '60-70', count: 0 },
    { age_group: '70-80', count: 0 },
    { age_group: '80+', count: 0 },
  ]

  const genderData = genderDistribution?.distribution || [
    { gender: 'Male', value: 0, count: 0, percentage: 0 },
    { gender: 'Female', value: 0, count: 0, percentage: 0 },
  ]

  const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

  // Use API statistics or fallback
  const highRiskPatients = populationStats?.high_risk_cases || predictions.filter((p: any) => 
    p.alzheimer_risk_level === 'high' || p.parkinson_risk_level === 'high'
  ).length

  const prevalence = populationStats?.prevalence_percentage || (patients.length > 0 ? ((highRiskPatients / patients.length) * 100).toFixed(2) : '0')

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📊 Population Analysis</h1>
        <p className="text-gray-600">Statistical and epidemiological analysis of patient population</p>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">Total Population</p>
          <p className="text-3xl font-bold text-blue-600">{populationStats?.total_patients || patients.length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">Total Predictions</p>
          <p className="text-3xl font-bold text-green-600">{populationStats?.total_predictions || predictions.length}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">High Risk Cases</p>
          <p className="text-3xl font-bold text-red-600">{highRiskPatients}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-600 mb-1">Prevalence (%)</p>
          <p className="text-3xl font-bold text-purple-600">{prevalence}%</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Age Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Age Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={ageGroups}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="age_group" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Gender Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Gender Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
                              <PieChart>
                    <Pie
                      data={genderData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ gender, percentage }) => `${gender} ${percentage.toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {genderData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Epidemiological Analysis */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Epidemiological Analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-1">Prevalence</p>
            <p className="text-lg font-semibold text-blue-600">{prevalence}%</p>
            <p className="text-xs text-gray-500 mt-1">High risk patients</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-1">Average Age</p>
            <p className="text-lg font-semibold text-green-600">
              {patients.length > 0
                ? Math.round(
                    patients.reduce((sum: number, p: any) => {
                      const age = Math.floor((Date.now() - new Date(p.date_of_birth).getTime()) / (365.25 * 24 * 60 * 60 * 1000))
                      return sum + age
                    }, 0) / patients.length
                  )
                : '0'
              } years
            </p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700 mb-1">Predictions per Patient</p>
            <p className="text-lg font-semibold text-purple-600">
              {patients.length > 0 ? (predictions.length / patients.length).toFixed(1) : '0'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
