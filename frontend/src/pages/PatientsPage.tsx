import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { patientsApi, type Patient } from '../services/api'

const SEARCH_DEBOUNCE_MS = 300
const PAGE_SIZE_OPTIONS = [10, 20, 50] as const
const DEFAULT_PAGE_SIZE = 20

const emptyForm = {
  patient_id: '',
  first_name: '',
  last_name: '',
  date_of_birth: '',
  gender: 'male' as Patient['gender'],
  email: '',
  phone: '',
  education_years: '',
}

export default function PatientsPage() {
  const [searchInput, setSearchInput] = useState('')
  const [searchDebounced, setSearchDebounced] = useState('')
  const [page, setPage] = useState(0)
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE)
  const [showModal, setShowModal] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [formError, setFormError] = useState('')
  const queryClient = useQueryClient()

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

  const createMutation = useMutation({
    mutationFn: () =>
      patientsApi.create({
        patient_id: form.patient_id.trim(),
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        date_of_birth: form.date_of_birth,
        gender: form.gender,
        email: form.email.trim() || undefined,
        phone: form.phone.trim() || undefined,
        education_years: form.education_years ? Number(form.education_years) : undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients'] })
      setShowModal(false)
      setForm(emptyForm)
      setFormError('')
    },
    onError: (err: unknown) => {
      const ax = err as { response?: { data?: { detail?: string } }; message?: string }
      const detail = ax.response?.data?.detail
      setFormError(
        typeof detail === 'string'
          ? detail
          : ax.message || 'Failed to create patient'
      )
    },
  })

  const hasNextPage = patients.length >= pageSize
  const hasPrevPage = page > 0

  const openModal = () => {
    setForm(emptyForm)
    setFormError('')
    setShowModal(true)
  }

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    setFormError('')
    createMutation.mutate()
  }

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
          <button type="button" className="btn btn-primary" onClick={openModal}>
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

      {showModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="add-patient-title"
        >
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6">
            <h2 id="add-patient-title" className="text-xl font-bold text-gray-900 mb-4">
              Add Patient
            </h2>
            <form onSubmit={handleCreate} className="space-y-3">
              <div>
                <label className="label" htmlFor="patient_id">Patient ID</label>
                <input
                  id="patient_id"
                  className="input"
                  required
                  value={form.patient_id}
                  onChange={(e) => setForm((f) => ({ ...f, patient_id: e.target.value }))}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="label" htmlFor="first_name">First name</label>
                  <input
                    id="first_name"
                    className="input"
                    required
                    value={form.first_name}
                    onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="label" htmlFor="last_name">Last name</label>
                  <input
                    id="last_name"
                    className="input"
                    required
                    value={form.last_name}
                    onChange={(e) => setForm((f) => ({ ...f, last_name: e.target.value }))}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="label" htmlFor="date_of_birth">Date of birth</label>
                  <input
                    id="date_of_birth"
                    type="date"
                    className="input"
                    required
                    value={form.date_of_birth}
                    onChange={(e) => setForm((f) => ({ ...f, date_of_birth: e.target.value }))}
                  />
                </div>
                <div>
                  <label className="label" htmlFor="gender">Gender</label>
                  <select
                    id="gender"
                    className="input"
                    value={form.gender}
                    onChange={(e) =>
                      setForm((f) => ({ ...f, gender: e.target.value as Patient['gender'] }))
                    }
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="label" htmlFor="email">Email (optional)</label>
                <input
                  id="email"
                  type="email"
                  className="input"
                  value={form.email}
                  onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                />
              </div>
              <div>
                <label className="label" htmlFor="phone">Phone (optional)</label>
                <input
                  id="phone"
                  className="input"
                  value={form.phone}
                  onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
                />
              </div>
              {formError && (
                <p className="text-sm text-red-700">{formError}</p>
              )}
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}
                  disabled={createMutation.isPending}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={createMutation.isPending}
                >
                  {createMutation.isPending ? 'Saving...' : 'Create Patient'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
