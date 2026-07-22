import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { predictionsApi, patientsApi, USE_MOCK_DATA } from '../services/api'

export default function PredictionResultPage() {
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()
  const [reviewNotes, setReviewNotes] = useState('')
  const [riskAdjustment, setRiskAdjustment] = useState('')
  const [reviewMessage, setReviewMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const { data: prediction, isLoading } = useQuery({
    queryKey: ['prediction', id],
    queryFn: () => predictionsApi.getById(Number(id)),
    enabled: !!id,
  })

  const { data: patient } = useQuery({
    queryKey: ['patient', prediction?.patient_id],
    queryFn: () => patientsApi.getById(prediction!.patient_id),
    enabled: !!prediction?.patient_id,
  })

  const reviewMutation = useMutation({
    mutationFn: (approved: boolean) =>
      predictionsApi.review(Number(id), {
        review_notes: reviewNotes || (approved ? 'Approved' : 'Override / not approved'),
        approved,
        risk_adjustment: riskAdjustment || undefined,
      }),
    onSuccess: () => {
      setReviewMessage({ type: 'success', text: 'Review submitted and audited.' })
      queryClient.invalidateQueries({ queryKey: ['prediction', id] })
    },
    onError: (err: unknown) => {
      const ax = err as { response?: { data?: { detail?: string } }; message?: string }
      setReviewMessage({
        type: 'error',
        text: ax.response?.data?.detail || ax.message || 'Failed to submit review',
      })
    },
  })

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary-600 border-t-transparent"></div>
        <p className="mt-2 text-gray-600">Loading prediction results...</p>
      </div>
    )
  }

  if (!prediction) {
    return <div className="text-center py-12">Prediction not found</div>
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high': return 'danger'
      case 'medium': return 'yellow'
      case 'low': return 'success'
      default: return 'gray'
    }
  }

  return (
    <div>
      {/* IFU / Clinical decision support disclaimer */}
      <div
        className="mb-6 rounded-lg border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950"
        role="note"
        aria-label="Clinical decision support disclaimer"
      >
        <p className="font-semibold mb-1">Clinical Decision Support — Important Notice</p>
        <p>
          NeuroPredict-AI is a clinical decision support system (CDSS) intended to assist qualified
          clinicians. It is <strong>not</strong> a standalone diagnostic device and does not replace
          clinical judgment, examination, or established diagnostic criteria. Always interpret
          outputs in the full clinical context.
        </p>
        <p className="mt-2 text-amber-900/90">
          Model version:{' '}
          <span className="font-mono">
            {prediction.model_version || prediction.model_name || 'unknown'}
          </span>
          {USE_MOCK_DATA && (
            <span className="ml-2 inline-block rounded bg-amber-200 px-2 py-0.5 text-xs font-medium">
              Mock / unvalidated data
            </span>
          )}
          {!USE_MOCK_DATA && !prediction.model_version && !prediction.model_name && (
            <span className="ml-2 inline-block rounded bg-amber-200 px-2 py-0.5 text-xs font-medium">
              Version not reported — treat as unvalidated for clinical use
            </span>
          )}
        </p>
      </div>

      <div className="mb-8">
        <Link to={patient ? `/patients/${patient.id}` : '/patients'} className="text-primary-600 hover:text-primary-700 text-sm font-medium mb-4 inline-block">
          ← Back to Patient
        </Link>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Prediction Results</h1>
        <p className="text-gray-600">
          {patient && `${patient.first_name} ${patient.last_name} • `}
          {new Date(prediction.created_at).toLocaleString()}
          {prediction.is_reviewed && (
            <span className="ml-2 text-success-700 font-medium">• Reviewed</span>
          )}
        </p>
      </div>

      {/* Risk Assessment Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Alzheimer's Risk */}
        {prediction.alzheimer_prediction && (
          <div className={`card border-2 border-${getRiskColor(prediction.alzheimer_prediction.risk_level)}-300`}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">🧠 Alzheimer's Risk</h2>
              <span className={`px-3 py-1 rounded-full text-sm font-medium bg-${getRiskColor(prediction.alzheimer_prediction.risk_level)}-100 text-${getRiskColor(prediction.alzheimer_prediction.risk_level)}-700 capitalize`}>
                {prediction.alzheimer_prediction.risk_level} Risk
              </span>
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-end mb-2">
                <span className="text-sm text-gray-600">Risk Score</span>
                <span className={`text-3xl font-bold text-${getRiskColor(prediction.alzheimer_prediction.risk_level)}-600`}>
                  {(prediction.alzheimer_prediction.risk_score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`bg-${getRiskColor(prediction.alzheimer_prediction.risk_level)}-500 h-3 rounded-full transition-all`}
                  style={{ width: `${prediction.alzheimer_prediction.risk_score * 100}%` }}
                ></div>
              </div>
            </div>

            <div>
              <span className="text-sm text-gray-600">Confidence</span>
              <div className="flex items-center mt-1">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full"
                    style={{ width: `${prediction.alzheimer_prediction.confidence * 100}%` }}
                  ></div>
                </div>
                <span className="ml-3 text-sm font-medium">
                  {(prediction.alzheimer_prediction.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Parkinson's Risk */}
        {prediction.parkinson_prediction && (
          <div className={`card border-2 border-${getRiskColor(prediction.parkinson_prediction.risk_level)}-300`}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">🤝 Parkinson's Risk</h2>
              <span className={`px-3 py-1 rounded-full text-sm font-medium bg-${getRiskColor(prediction.parkinson_prediction.risk_level)}-100 text-${getRiskColor(prediction.parkinson_prediction.risk_level)}-700 capitalize`}>
                {prediction.parkinson_prediction.risk_level} Risk
              </span>
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-end mb-2">
                <span className="text-sm text-gray-600">Risk Score</span>
                <span className={`text-3xl font-bold text-${getRiskColor(prediction.parkinson_prediction.risk_level)}-600`}>
                  {(prediction.parkinson_prediction.risk_score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`bg-${getRiskColor(prediction.parkinson_prediction.risk_level)}-500 h-3 rounded-full transition-all`}
                  style={{ width: `${prediction.parkinson_prediction.risk_score * 100}%` }}
                ></div>
              </div>
            </div>

            <div>
              <span className="text-sm text-gray-600">Confidence</span>
              <div className="flex items-center mt-1">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full"
                    style={{ width: `${prediction.parkinson_prediction.confidence * 100}%` }}
                  ></div>
                </div>
                <span className="ml-3 text-sm font-medium">
                  {(prediction.parkinson_prediction.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Clinician review / override */}
      <div className="card mb-6">
        <h2 className="text-xl font-bold mb-2">Clinician Review</h2>
        <p className="text-sm text-gray-600 mb-4">
          Approve the model output or document an override. Submissions are sent to the prediction
          review API and recorded for audit.
        </p>

        {prediction.is_reviewed && prediction.review_notes && (
          <div className="mb-4 p-3 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-700">
            <p className="font-medium text-gray-900 mb-1">Previous review notes</p>
            <pre className="whitespace-pre-wrap font-sans">{prediction.review_notes}</pre>
          </div>
        )}

        <div className="space-y-3">
          <div>
            <label className="label" htmlFor="review-notes">Approve / override notes</label>
            <textarea
              id="review-notes"
              className="input min-h-[80px]"
              value={reviewNotes}
              onChange={(e) => setReviewNotes(e.target.value)}
              placeholder="Clinical rationale for approval or override..."
            />
          </div>
          <div>
            <label className="label" htmlFor="risk-adjustment">Risk adjustment (optional)</label>
            <input
              id="risk-adjustment"
              type="text"
              className="input"
              value={riskAdjustment}
              onChange={(e) => setRiskAdjustment(e.target.value)}
              placeholder="e.g. Clinician adjusts high → medium due to comorbidity profile"
            />
          </div>
          {reviewMessage && (
            <p className={`text-sm ${reviewMessage.type === 'success' ? 'text-green-700' : 'text-red-700'}`}>
              {reviewMessage.text}
            </p>
          )}
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              className="btn btn-primary"
              disabled={reviewMutation.isPending}
              onClick={() => reviewMutation.mutate(true)}
            >
              {reviewMutation.isPending ? 'Submitting...' : 'Approve'}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              disabled={reviewMutation.isPending}
              onClick={() => reviewMutation.mutate(false)}
            >
              Override / Do not approve
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recommendations */}
        <div className="lg:col-span-2 card">
          <h2 className="text-xl font-bold mb-4">📋 Clinical Recommendations</h2>
          <div className="prose prose-sm max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-sm text-gray-700 leading-relaxed">
              {prediction.recommendations || 'No recommendations available'}
            </pre>
          </div>
        </div>

        {/* Feature Importance (clinical labels when available) */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">🔍 Top Contributing Factors</h2>
          {prediction.clinical_explanation?.clinical_feature_importance?.length ? (
            <div className="space-y-3">
              {prediction.clinical_explanation.clinical_feature_importance.map((item) => (
                <div key={item.feature_key}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-700 font-medium" title={item.interpretation_en}>
                      {item.clinical_label_fa || item.clinical_label_en}
                    </span>
                    <span className="font-medium">{(item.importance * 100).toFixed(1)}%</span>
                  </div>
                  {item.interpretation_fa && (
                    <p className="text-xs text-gray-500 mb-1" dir="rtl">{item.interpretation_fa}</p>
                  )}
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-500 h-2 rounded-full"
                      style={{ width: `${item.importance * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : prediction.feature_importance ? (
            <div className="space-y-3">
              {Object.entries(prediction.feature_importance)
                .slice(0, 10)
                .map(([feature, importance]) => (
                  <div key={feature}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700 capitalize">{feature.replace(/_/g, ' ')}</span>
                      <span className="font-medium">{((importance as number) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-500 h-2 rounded-full"
                        style={{ width: `${(importance as number) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
            </div>
          ) : null}
        </div>
      </div>

      {/* Clinical Explainability: cohort comparison + progression */}
      {prediction.clinical_explanation && (
        <div className="mt-8 space-y-6">
          <h2 className="text-2xl font-bold text-gray-900 border-b border-gray-200 pb-2">
            📊 Explainability بالینی
          </h2>

          {/* Cohort comparison */}
          {prediction.clinical_explanation.cohort_comparison && prediction.clinical_explanation.cohort_comparison.cohort_size > 0 && (
            <div className="card">
              <h3 className="text-lg font-bold mb-3">مقایسه با همگروه مشابه</h3>
              <p className="text-sm text-gray-600 mb-4">
                {prediction.clinical_explanation.cohort_comparison.cohort_description_fa} (n={
                  prediction.clinical_explanation.cohort_comparison.cohort_size
                })
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {prediction.clinical_explanation.cohort_comparison.alzheimer && (
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <h4 className="font-semibold text-blue-800 mb-2">آلزایمر</h4>
                    {prediction.clinical_explanation.cohort_comparison.alzheimer.patient_percentile != null && (
                      <p className="text-sm text-gray-700 mb-1">
                        صدک بیمار: <strong>{prediction.clinical_explanation.cohort_comparison.alzheimer.patient_percentile.toFixed(0)}</strong>
                      </p>
                    )}
                    <p className="text-sm text-gray-600" dir="rtl">
                      {prediction.clinical_explanation.cohort_comparison.alzheimer.summary_fa}
                    </p>
                    {prediction.clinical_explanation.cohort_comparison.alzheimer.cohort_median != null && (
                      <p className="text-xs text-gray-500 mt-2">
                        میانه همگروه: {(prediction.clinical_explanation.cohort_comparison.alzheimer.cohort_median * 100).toFixed(1)}%
                      </p>
                    )}
                  </div>
                )}
                {prediction.clinical_explanation.cohort_comparison.parkinson && (
                  <div className="p-3 bg-amber-50 rounded-lg">
                    <h4 className="font-semibold text-amber-800 mb-2">پارکینسون</h4>
                    {prediction.clinical_explanation.cohort_comparison.parkinson.patient_percentile != null && (
                      <p className="text-sm text-gray-700 mb-1">
                        صدک بیمار: <strong>{prediction.clinical_explanation.cohort_comparison.parkinson.patient_percentile.toFixed(0)}</strong>
                      </p>
                    )}
                    <p className="text-sm text-gray-600" dir="rtl">
                      {prediction.clinical_explanation.cohort_comparison.parkinson.summary_fa}
                    </p>
                    {prediction.clinical_explanation.cohort_comparison.parkinson.cohort_median != null && (
                      <p className="text-xs text-gray-500 mt-2">
                        میانه همگروه: {(prediction.clinical_explanation.cohort_comparison.parkinson.cohort_median * 100).toFixed(1)}%
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Progression visualization */}
          {prediction.clinical_explanation.progression_visualization && (
            <div className="card">
              <h3 className="text-lg font-bold mb-3">پیشرفت عصبی و پیگیری</h3>
              <p className="text-sm text-gray-700 mb-2" dir="rtl">
                {prediction.clinical_explanation.progression_visualization.trajectory_summary_fa}
              </p>
              <p className="text-sm text-gray-600">
                توصیه پیگیری: هر{' '}
                <strong>{prediction.clinical_explanation.progression_visualization.recommended_follow_up_months}</strong>{' '}
                ماه
              </p>
              {prediction.clinical_explanation.progression_visualization.has_longitudinal_data &&
                prediction.clinical_explanation.progression_visualization.trend_data?.visit_dates?.length && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs text-gray-500 mb-2">داده‌های طولی موجود است؛ روند در گزارش longitudinal قابل مشاهده است.</p>
                  </div>
                )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
