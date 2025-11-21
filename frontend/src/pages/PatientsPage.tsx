import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { patientsApi, predictionsApi } from '../services/api'
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
  UserGroupIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

interface PatientFilters {
  search: string
  gender: string
  ageMin: string
  ageMax: string
  riskLevel: string
  hasPredictions: string
  dateFrom: string
  dateTo: string
}

export default function PatientsPage() {
  const [search, setSearch] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedPatients, setSelectedPatients] = useState<Set<number>>(new Set())
  const [groupName, setGroupName] = useState('')
  const [filters, setFilters] = useState<PatientFilters>({
    search: '',
    gender: '',
    ageMin: '',
    ageMax: '',
    riskLevel: '',
    hasPredictions: '',
    dateFrom: '',
    dateTo: '',
  })

  const { data: patients = [], isLoading } = useQuery({
    queryKey: ['patients', search, filters],
    queryFn: () => patientsApi.getAll(0, 1000, search || undefined),
  })

  const { data: allPredictions = [] } = useQuery({
    queryKey: ['all-predictions'],
    queryFn: () => predictionsApi.getAll(undefined, 0, 10000),
  })

  // Filter patients
  const filteredPatients = patients.filter((patient) => {
    if (filters.gender && patient.gender !== filters.gender) return false

    // Age filter
    if (filters.ageMin || filters.ageMax) {
      const age = new Date().getFullYear() - new Date(patient.date_of_birth).getFullYear()
      if (filters.ageMin && age < Number(filters.ageMin)) return false
      if (filters.ageMax && age > Number(filters.ageMax)) return false
    }

    // Risk level filter
    if (filters.riskLevel) {
      const patientPredictions = allPredictions.filter((p) => p.patient_id === patient.id)
      const hasHighRisk = patientPredictions.some(
        (p) =>
          (p.alzheimer_prediction?.risk_level === 'high') ||
          (p.parkinson_prediction?.risk_level === 'high')
      )
      if (filters.riskLevel === 'high' && !hasHighRisk) return false
      if (filters.riskLevel === 'low' && hasHighRisk) return false
    }

    // Has predictions filter
    if (filters.hasPredictions === 'yes') {
      const hasPredictions = allPredictions.some((p) => p.patient_id === patient.id)
      if (!hasPredictions) return false
    } else if (filters.hasPredictions === 'no') {
      const hasPredictions = allPredictions.some((p) => p.patient_id === patient.id)
      if (hasPredictions) return false
    }

    return true
  })

  // Group patients
  const groupedPatients = filters.gender
    ? filteredPatients.reduce(
        (acc, patient) => {
          const key = patient.gender
          if (!acc[key]) acc[key] = []
          acc[key].push(patient)
          return acc
        },
        {} as Record<string, typeof filteredPatients>
      )
    : { All: filteredPatients }

  const handleExport = () => {
    const data = selectedPatients.size > 0
      ? filteredPatients.filter((p) => selectedPatients.has(p.id))
      : filteredPatients

    const csv = [
      ['Patient ID', 'First Name', 'Last Name', 'Gender', 'Date of Birth', 'Email', 'Phone'].join(','),
      ...data.map((p) =>
        [
          p.patient_id,
          p.first_name,
          p.last_name,
          p.gender,
          p.date_of_birth,
          p.email || '',
          p.phone || '',
        ].join(',')
      ),
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `patients_export_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  const importMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const response = await fetch('/api/v1/patients/import/csv', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      })
      if (!response.ok) {
        throw new Error('CSV import failed')
      }
      return response.json()
    },
    onSuccess: (data) => {
      alert(`Successfully imported ${data.imported} patients${data.errors > 0 ? ` (${data.errors} errors)` : ''}`)
      // Refresh patients list
      window.location.reload()
    },
    onError: (error) => {
      alert(`CSV import failed: ${error}`)
    },
  })

  const handleImport = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.csv'
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) {
        importMutation.mutate(file)
      }
    }
    input.click()
  }

  const handleCreateGroup = () => {
    if (!groupName || selectedPatients.size === 0) {
      alert('Please enter a group name and select patients')
      return
    }
    // TODO: Implement group creation
    alert(`Group "${groupName}" will be created with ${selectedPatients.size} patients`)
    setGroupName('')
    setSelectedPatients(new Set())
  }

  const togglePatientSelection = (patientId: number) => {
    const newSet = new Set(selectedPatients)
    if (newSet.has(patientId)) {
      newSet.delete(patientId)
    } else {
      newSet.add(patientId)
    }
    setSelectedPatients(newSet)
  }

  const toggleSelectAll = () => {
    if (selectedPatients.size === filteredPatients.length) {
      setSelectedPatients(new Set())
    } else {
      setSelectedPatients(new Set(filteredPatients.map((p) => p.id)))
    }
  }

  const clearFilters = () => {
    setFilters({
      search: '',
      gender: '',
      ageMin: '',
      ageMax: '',
      riskLevel: '',
      hasPredictions: '',
      dateFrom: '',
      dateTo: '',
    })
    setSearch('')
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Patients</h1>
        <p className="text-gray-600">Manage patient records and medical data</p>
      </div>

      {/* Search and Actions */}
      <div className="card mb-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex-1 max-w-md flex items-center gap-2">
            <div className="relative flex-1">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search patients by name or ID..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value)
                  setFilters({ ...filters, search: e.target.value })
                }}
                className="input pl-10"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`btn btn-secondary ${showFilters ? 'bg-primary-100' : ''}`}
            >
              <FunnelIcon className="h-5 w-5 mr-2" />
              Filters
            </button>
          </div>
          <div className="flex items-center gap-2">
            {selectedPatients.size > 0 && (
              <div className="flex items-center gap-2 mr-4">
                <span className="text-sm text-gray-600">{selectedPatients.size} selected</span>
                <button
                  onClick={handleCreateGroup}
                  className="btn btn-secondary text-sm"
                  disabled={!groupName}
                >
                  <UserGroupIcon className="h-4 w-4 mr-1" />
                  Create Group
                </button>
                {groupName && (
                  <input
                    type="text"
                    placeholder="Group name..."
                    value={groupName}
                    onChange={(e) => setGroupName(e.target.value)}
                    className="input text-sm w-32"
                  />
                )}
              </div>
            )}
            <button onClick={handleImport} className="btn btn-secondary">
              <ArrowUpTrayIcon className="h-5 w-5 mr-2" />
              Import
            </button>
            <button onClick={handleExport} className="btn btn-primary">
              <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
              Export
            </button>
            <button className="btn btn-primary">
              + Add Patient
            </button>
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200 grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <div>
              <label className="label text-sm">Gender</label>
              <select
                value={filters.gender}
                onChange={(e) => setFilters({ ...filters, gender: e.target.value })}
                className="input"
              >
                <option value="">All</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div>
              <label className="label text-sm">Age Min</label>
              <input
                type="number"
                value={filters.ageMin}
                onChange={(e) => setFilters({ ...filters, ageMin: e.target.value })}
                className="input"
                placeholder="Min age"
              />
            </div>
            <div>
              <label className="label text-sm">Age Max</label>
              <input
                type="number"
                value={filters.ageMax}
                onChange={(e) => setFilters({ ...filters, ageMax: e.target.value })}
                className="input"
                placeholder="Max age"
              />
            </div>
            <div>
              <label className="label text-sm">Risk Level</label>
              <select
                value={filters.riskLevel}
                onChange={(e) => setFilters({ ...filters, riskLevel: e.target.value })}
                className="input"
              >
                <option value="">All</option>
                <option value="high">High Risk</option>
                <option value="low">Low Risk</option>
              </select>
            </div>
            <div>
              <label className="label text-sm">Has Predictions</label>
              <select
                value={filters.hasPredictions}
                onChange={(e) => setFilters({ ...filters, hasPredictions: e.target.value })}
                className="input"
              >
                <option value="">All</option>
                <option value="yes">Yes</option>
                <option value="no">No</option>
              </select>
            </div>
            <div>
              <label className="label text-sm">Date From</label>
              <input
                type="date"
                value={filters.dateFrom}
                onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="label text-sm">Date To</label>
              <input
                type="date"
                value={filters.dateTo}
                onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
                className="input"
              />
            </div>
            <div className="flex items-end">
              <button onClick={clearFilters} className="btn btn-secondary w-full">
                <XMarkIcon className="h-4 w-4 mr-2" />
                Clear
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Patients Table */}
      <div className="card">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary-600 border-t-transparent"></div>
            <p className="mt-2 text-gray-600">Loading patients...</p>
          </div>
        ) : filteredPatients.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No patients found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4">
                    <input
                      type="checkbox"
                      checked={selectedPatients.size === filteredPatients.length && filteredPatients.length > 0}
                      onChange={toggleSelectAll}
                      className="rounded"
                    />
                  </th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Patient ID</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Name</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Gender</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Date of Birth</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Age</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Contact</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Predictions</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredPatients.map((patient) => {
                  const age = new Date().getFullYear() - new Date(patient.date_of_birth).getFullYear()
                  const patientPredictions = allPredictions.filter((p) => p.patient_id === patient.id)
                  const hasHighRisk = patientPredictions.some(
                    (p) =>
                      (p.alzheimer_prediction?.risk_level === 'high') ||
                      (p.parkinson_prediction?.risk_level === 'high')
                  )

                  return (
                    <tr
                      key={patient.id}
                      className={`border-b border-gray-100 hover:bg-gray-50 ${
                        selectedPatients.has(patient.id) ? 'bg-primary-50' : ''
                      }`}
                    >
                      <td className="py-3 px-4">
                        <input
                          type="checkbox"
                          checked={selectedPatients.has(patient.id)}
                          onChange={() => togglePatientSelection(patient.id)}
                          className="rounded"
                        />
                      </td>
                      <td className="py-3 px-4">
                        <span className="font-mono text-sm">{patient.patient_id}</span>
                      </td>
                      <td className="py-3 px-4">
                        <p className="font-medium">
                          {patient.first_name} {patient.last_name}
                        </p>
                      </td>
                      <td className="py-3 px-4">
                        <span className="capitalize">{patient.gender}</span>
                      </td>
                      <td className="py-3 px-4">
                        {new Date(patient.date_of_birth).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4">{age} years</td>
                      <td className="py-3 px-4 text-sm text-gray-600">
                        <div>{patient.email || '-'}</div>
                        <div>{patient.phone || '-'}</div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <span className="text-sm">{patientPredictions.length}</span>
                          {hasHighRisk && (
                            <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs">
                              High Risk
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <Link
                          to={`/patients/${patient.id}`}
                          className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                        >
                          View Details →
                        </Link>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Grouping Summary */}
      {Object.keys(groupedPatients).length > 1 && (
        <div className="card mt-6">
          <h3 className="text-lg font-semibold mb-4">Grouping Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(groupedPatients).map(([group, patients]) => (
              <div key={group} className="border border-gray-200 rounded-lg p-4">
                <div className="font-semibold text-gray-700">{group}</div>
                <div className="text-2xl font-bold text-primary-600 mt-2">{patients.length}</div>
                <div className="text-sm text-gray-500">patients</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
