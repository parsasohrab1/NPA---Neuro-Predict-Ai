import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { patientsApi } from '../services/api'

const SEARCH_DEBOUNCE_MS = 300
const PAGE_SIZE_OPTIONS = [10, 20, 50] as const
const DEFAULT_PAGE_SIZE = 20

export default function PatientsPage() {
  const [searchInput, setSearchInput] = useState('')
  const [searchDebounced, setSearchDebounced] = useState('')
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE)

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearchDebounced(searchInput)
    }, SEARCH_DEBOUNCE_MS)
    return () => window.clearTimeout(timer)
  }, [searchInput])

  useEffect(() => {
    setPage(0)
  }, [searchDebounced, pageSize])

  const skip = page * pageSize
  const { data: patients = [], isLoading } = useQuery({
    queryKey: ['patients', searchDebounced, skip, pageSize],
    queryFn: () => patientsApi.getAll(skip, pageSize, searchDebounced || undefined),
  })

  const hasNextPage = patients.length >= pageSize
  const hasPrevPage = page > 0

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Patients</h1>
        <p className="text-gray-600">Manage patient records and medical data</p>
      </div>

      {/* Search, pagination size, and Actions */}
      <div className="card mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex-1 min-w-[200px] max-w-md">
            <input
              type="text"
              placeholder="Search patients by name or ID..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="input"
            />
          </div>
          <div className="flex items-center gap-3">
            <label className="text-sm text-gray-600">Per page:</label>
            <select
              value={pageSize}
              onChange={(e) => setPageSize(Number(e.target.value))}
              className="input w-20 py-2"
            >
              {PAGE_SIZE_OPTIONS.map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary">
            + Add Patient
          </button>
        </div>
      </div>

      {/* Patients Table */}
      <div className="card">
        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary-600 border-t-transparent"></div>
            <p className="mt-2 text-gray-600">Loading patients...</p>
          </div>
        ) : patients.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No patients found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Patient ID</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Name</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Gender</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Date of Birth</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Contact</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((patient) => (
                  <tr key={patient.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <span className="font-mono text-sm">{patient.patient_id}</span>
                    </td>
                    <td className="py-3 px-4">
                      <p className="font-medium">{patient.first_name} {patient.last_name}</p>
                    </td>
                    <td className="py-3 px-4">
                      <span className="capitalize">{patient.gender}</span>
                    </td>
                    <td className="py-3 px-4">
                      {new Date(patient.date_of_birth).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      <div>{patient.email || '-'}</div>
                      <div>{patient.phone || '-'}</div>
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
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Server-side pagination controls */}
        {(patients.length > 0 || hasPrevPage) && (
          <div className="flex items-center justify-between border-t border-gray-200 px-4 py-3">
            <p className="text-sm text-gray-600">
              Page {page + 1}
              {patients.length > 0 && ` · Showing ${skip + 1}–${skip + patients.length}`}
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={!hasPrevPage || isLoading}
                className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                type="button"
                onClick={() => setPage((p) => p + 1)}
                disabled={!hasNextPage || isLoading}
                className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

