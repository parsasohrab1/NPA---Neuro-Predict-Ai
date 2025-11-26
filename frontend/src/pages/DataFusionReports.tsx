import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { 
  FileText, 
  TrendingUp, 
  AlertCircle, 
  CheckCircle, 
  Brain, 
  Activity,
  Download,
  Sparkles
} from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8001';

interface FusionReport {
  id: number;
  patient_id: number;
  generated_at: string;
  fusion_scores: {
    cognitive: number;
    biomarker: number;
    imaging: number;
    integrated: number;
    confidence: string;
  };
  cross_modal: {
    consistency_score: number;
    correlations: {
      cognitive_biomarker: number;
      cognitive_imaging: number;
      biomarker_imaging: number;
    };
    has_conflicts: boolean;
  };
  disease_analysis: {
    alzheimer: {
      score: number;
      confidence: number;
    };
    parkinson: {
      score: number;
      confidence: number;
    };
  };
  interpretation: {
    overall: string;
    primary_concern: string;
    confidence: number;
  };
  report: {
    executive_summary: string;
    detailed_findings: string;
    risk_assessment: string;
    recommendations: string;
    follow_up_plan: string;
  };
  quality: {
    data_completeness: number;
    has_outliers: boolean;
  };
}

export default function DataFusionReports() {
  const [patientId, setPatientId] = useState('');
  const [selectedReport, setSelectedReport] = useState<FusionReport | null>(null);
  const queryClient = useQueryClient();

  // Fetch patient reports
  const { data: reports, isLoading } = useQuery<FusionReport[]>({
    queryKey: ['fusion-reports', patientId],
    queryFn: async () => {
      if (!patientId) return [];
      const response = await axios.get(`${API_BASE}/api/v1/data-fusion/patient/${patientId}`);
      return response.data;
    },
    enabled: !!patientId,
  });

  // Generate new report mutation
  const generateReport = useMutation({
    mutationFn: async (patId: number) => {
      const response = await axios.post(`${API_BASE}/api/v1/data-fusion/generate`, {
        patient_id: patId,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fusion-reports', patientId] });
    },
  });

  const getInterpretationColor = (interpretation: string) => {
    switch (interpretation) {
      case 'normal':
        return 'bg-green-500';
      case 'mild_concern':
        return 'bg-yellow-500';
      case 'moderate_concern':
        return 'bg-orange-500';
      case 'high_concern':
        return 'bg-red-500';
      case 'critical':
        return 'bg-red-700';
      default:
        return 'bg-gray-500';
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'very_high':
        return 'text-green-600';
      case 'high':
        return 'text-blue-600';
      case 'moderate':
        return 'text-yellow-600';
      case 'low':
        return 'text-orange-600';
      case 'very_low':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const downloadReport = (report: FusionReport) => {
    const content = `
PATENT-PENDING: MULTI-MODAL DATA FUSION REPORT
NeuroPredict-AI System

Report ID: ${report.id}
Generated: ${new Date(report.generated_at).toLocaleString()}
Patient ID: ${report.patient_id}

${report.report.executive_summary}

DETAILED FINDINGS:
${report.report.detailed_findings}

RISK ASSESSMENT:
${report.report.risk_assessment}

RECOMMENDATIONS:
${report.report.recommendations}

FOLLOW-UP PLAN:
${report.report.follow_up_plan}

---
This report was generated using our proprietary multi-modal data fusion algorithm.
Patent-pending technology. © 2024 NeuroPredict-AI
    `.trim();

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `DataFusionReport_Patient${report.patient_id}_${report.id}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-purple-500" />
            Data Fusion Reports
          </h1>
          <p className="text-gray-600 mt-1">
            PATENT-PENDING: Multi-Modal Medical Data Integration & Interpretation
          </p>
        </div>
      </div>

      {/* Patent Notice */}
      <Card className="border-purple-200 bg-purple-50">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <Sparkles className="h-6 w-6 text-purple-600 mt-1" />
            <div>
              <h3 className="font-semibold text-purple-900">Patent-Pending Innovation</h3>
              <p className="text-sm text-purple-700 mt-1">
                This system implements our proprietary <strong>Multi-Modal Data Fusion Algorithm</strong> that
                integrates cognitive assessments, biomarker profiles, and neuroimaging findings through
                confidence-weighted correlation analysis with automated conflict resolution and natural
                language report generation. This represents our key differentiator for intellectual property protection.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Search & Generate */}
      <Card>
        <CardHeader>
          <CardTitle>Generate or View Fusion Reports</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              type="number"
              placeholder="Enter Patient ID"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              className="flex-1"
            />
            <Button
              onClick={() => {
                if (patientId) {
                  generateReport.mutate(parseInt(patientId));
                }
              }}
              disabled={!patientId || generateReport.isPending}
              className="bg-purple-600 hover:bg-purple-700"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Generate Fusion Report
            </Button>
          </div>

          {generateReport.isPending && (
            <div className="text-sm text-gray-600 flex items-center gap-2">
              <Activity className="h-4 w-4 animate-spin" />
              Generating multi-modal fusion report...
            </div>
          )}

          {generateReport.isSuccess && (
            <div className="text-sm text-green-600 flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Fusion report generated successfully!
            </div>
          )}
        </CardContent>
      </Card>

      {/* Reports List */}
      {isLoading && (
        <div className="text-center py-8">
          <Activity className="h-8 w-8 animate-spin mx-auto text-purple-600" />
          <p className="text-gray-600 mt-2">Loading reports...</p>
        </div>
      )}

      {reports && reports.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {reports.map((report) => (
            <Card
              key={report.id}
              className="cursor-pointer hover:shadow-lg transition-shadow border-l-4 border-l-purple-500"
              onClick={() => setSelectedReport(report)}
            >
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">Report #{report.id}</CardTitle>
                    <p className="text-sm text-gray-600">
                      {new Date(report.generated_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Badge className={getInterpretationColor(report.interpretation.overall)}>
                    {report.interpretation.overall.replace('_', ' ').toUpperCase()}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {/* Fusion Score */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-semibold">Integrated Fusion Score</span>
                    <span className={getConfidenceColor(report.fusion_scores.confidence)}>
                      {report.fusion_scores.integrated.toFixed(1)}/100
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full"
                      style={{ width: `${report.fusion_scores.integrated}%` }}
                    />
                  </div>
                </div>

                {/* Primary Concern */}
                <div>
                  <p className="text-sm font-semibold">Primary Concern:</p>
                  <p className="text-sm text-gray-700">{report.interpretation.primary_concern}</p>
                </div>

                {/* Modality Scores */}
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <p className="text-gray-600">Cognitive</p>
                    <p className="font-semibold">{report.fusion_scores.cognitive.toFixed(0)}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Biomarker</p>
                    <p className="font-semibold">{report.fusion_scores.biomarker.toFixed(0)}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Imaging</p>
                    <p className="font-semibold">{report.fusion_scores.imaging.toFixed(0)}</p>
                  </div>
                </div>

                {/* Conflicts Warning */}
                {report.cross_modal.has_conflicts && (
                  <div className="flex items-center gap-2 text-xs text-orange-600 bg-orange-50 p-2 rounded">
                    <AlertCircle className="h-4 w-4" />
                    Cross-modal conflicts detected
                  </div>
                )}

                {/* Disease Analysis */}
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-blue-50 p-2 rounded">
                    <p className="text-gray-600">AD Risk</p>
                    <p className="font-semibold text-blue-700">
                      {report.disease_analysis.alzheimer.score.toFixed(0)}%
                    </p>
                  </div>
                  <div className="bg-green-50 p-2 rounded">
                    <p className="text-gray-600">PD Risk</p>
                    <p className="font-semibold text-green-700">
                      {report.disease_analysis.parkinson.score.toFixed(0)}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Detailed Report Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <CardHeader className="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-2xl flex items-center gap-2">
                    <Brain className="h-6 w-6" />
                    Data Fusion Report #{selectedReport.id}
                  </CardTitle>
                  <p className="text-purple-100 mt-1">
                    Patient ID: {selectedReport.patient_id} | 
                    Generated: {new Date(selectedReport.generated_at).toLocaleString()}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedReport(null)}
                  className="text-white hover:bg-purple-700"
                >
                  ✕
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6 pt-6">
              {/* Executive Summary */}
              <div>
                <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
                  <FileText className="h-5 w-5 text-purple-600" />
                  Executive Summary
                </h3>
                <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded">
                  {selectedReport.report.executive_summary}
                </pre>
              </div>

              {/* Detailed Findings */}
              <div>
                <h3 className="font-bold text-lg mb-2">Detailed Findings</h3>
                <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded">
                  {selectedReport.report.detailed_findings}
                </pre>
              </div>

              {/* Risk Assessment */}
              <div>
                <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-orange-600" />
                  Risk Assessment
                </h3>
                <pre className="whitespace-pre-wrap text-sm bg-orange-50 p-4 rounded">
                  {selectedReport.report.risk_assessment}
                </pre>
              </div>

              {/* Recommendations */}
              <div>
                <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Recommendations
                </h3>
                <pre className="whitespace-pre-wrap text-sm bg-green-50 p-4 rounded">
                  {selectedReport.report.recommendations}
                </pre>
              </div>

              {/* Follow-up Plan */}
              {selectedReport.report.follow_up_plan && (
                <div>
                  <h3 className="font-bold text-lg mb-2">Follow-up Plan</h3>
                  <pre className="whitespace-pre-wrap text-sm bg-blue-50 p-4 rounded">
                    {selectedReport.report.follow_up_plan}
                  </pre>
                </div>
              )}

              {/* Quality Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">Data Completeness</h4>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${selectedReport.quality.data_completeness}%` }}
                      />
                    </div>
                    <span className="text-sm">{selectedReport.quality.data_completeness.toFixed(0)}%</span>
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Confidence</h4>
                  <Badge className={getConfidenceColor(selectedReport.fusion_scores.confidence)}>
                    {selectedReport.fusion_scores.confidence.replace('_', ' ').toUpperCase()}
                  </Badge>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t">
                <Button
                  onClick={() => downloadReport(selectedReport)}
                  className="flex-1 bg-purple-600 hover:bg-purple-700"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Report
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setSelectedReport(null)}
                  className="flex-1"
                >
                  Close
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}

