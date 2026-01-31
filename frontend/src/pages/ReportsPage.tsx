import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { patientsApi, predictionsApi, reportsApi } from '../services/api'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function ReportsPage() {
  const [reportType, setReportType] = useState<'clinical' | 'research' | 'administrative'>('clinical')
  const [selectedChart, setSelectedChart] = useState<'line' | 'bar' | 'pie'>('line')

  const { data: patients = [] } = useQuery({
    queryKey: ['patients'],
    queryFn: () => patientsApi.getAll(0, 1000),
  })

  const { data: predictions = [] } = useQuery({
    queryKey: ['predictions'],
    queryFn: () => predictionsApi.getAll(undefined, 0, 1000),
  })

  // Fetch reports data from API
  const { data: reportSummary } = useQuery({
    queryKey: ['report-summary', reportType],
    queryFn: () => reportsApi.getSummary(reportType),
  })

  const { data: trendData } = useQuery({
    queryKey: ['predictions-trend'],
    queryFn: () => reportsApi.getPredictionsTrend(30),
  })

  const { data: riskDistData } = useQuery({
    queryKey: ['risk-distribution'],
    queryFn: () => reportsApi.getRiskDistribution(),
  })

  // Process data for charts
  const predictionData = trendData?.data?.map((item: any) => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    count: item.count,
  })) || []

  const riskDistribution = riskDistData?.distribution ? [
    { name: 'Low', value: riskDistData.distribution.low },
    { name: 'Medium', value: riskDistData.distribution.medium },
    { name: 'High', value: riskDistData.distribution.high },
  ] : [
    { name: 'Low', value: 0 },
    { name: 'Medium', value: 0 },
    { name: 'High', value: 0 },
  ]

  const COLORS = ['#4ade80', '#fbbf24', '#ef4444']

  const handleExportPDF = () => {
    alert('PDF export functionality will be implemented')
  }

  const handleExportExcel = () => {
    alert('Excel export functionality will be implemented')
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📑 Reports & Visualization</h1>
        <p className="text-gray-600">Generate and view comprehensive reports</p>
      </div>

      {/* Report Type Selection */}
      <div className="card mb-6">
        <div className="flex items-center space-x-4">
          <label className="text-sm font-medium text-gray-700">Report Type:</label>
          <div className="flex space-x-2">
            <button
              onClick={() => setReportType('clinical')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                reportType === 'clinical'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Clinical
            </button>
            <button
              onClick={() => setReportType('research')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                reportType === 'research'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Research
            </button>
            <button
              onClick={() => setReportType('administrative')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                reportType === 'administrative'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Administrative
            </button>
          </div>
        </div>
      </div>

      {/* Export Buttons */}
      <div className="card mb-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Export Options</h2>
          <div className="flex space-x-3">
            <button
              onClick={handleExportPDF}
              className="btn btn-primary"
            >
              📄 Export PDF
            </button>
            <button
              onClick={handleExportExcel}
              className="btn btn-secondary"
            >
              📊 Export Excel
            </button>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Prediction Trends */}
        <div className="card">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold">Prediction Trends</h3>
            <select
              value={selectedChart}
              onChange={(e) => setSelectedChart(e.target.value as any)}
              className="px-3 py-1 border rounded-lg text-sm"
            >
              <option value="line">Line Chart</option>
              <option value="bar">Bar Chart</option>
              <option value="pie">Pie Chart</option>
            </select>
          </div>
                        <ResponsiveContainer width="100%" height={300}>
                {selectedChart === 'line' ? (
                  <LineChart data={predictionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="count" stroke="#10b981" name="Daily Predictions" />
                  </LineChart>
                ) : selectedChart === 'bar' ? (
                  <BarChart data={predictionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#10b981" name="Daily Predictions" />
                  </BarChart>
                ) : (
                  <PieChart>
                    <Pie
                      data={riskDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {riskDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                )}
              </ResponsiveContainer>
        </div>

        {/* Risk Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Risk Level Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {riskDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Report Summary */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Report Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-600">Total Patients</p>
            <p className="text-2xl font-bold text-blue-600">{reportSummary?.statistics?.total_patients || patients.length}</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <p className="text-sm text-gray-600">Total Predictions</p>
            <p className="text-2xl font-bold text-green-600">{reportSummary?.statistics?.total_predictions || predictions.length}</p>
          </div>
          <div className="p-4 bg-yellow-50 rounded-lg">
            <p className="text-sm text-gray-600">High Risk Cases</p>
            <p className="text-2xl font-bold text-yellow-600">
              {reportSummary?.statistics?.high_risk_cases || riskDistribution[2]?.value || 0}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
