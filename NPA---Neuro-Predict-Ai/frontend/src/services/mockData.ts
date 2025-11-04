/**
 * Mock Data Service - Uses static JSON files when backend is unavailable
 */

export interface MockPatient {
  id: number
  patient_id: string
  first_name: string
  last_name: string
  date_of_birth: string
  gender: 'male' | 'female' | 'other'
  email?: string
  phone?: string
  education_years?: number
  medical_history?: string
  family_history?: string
  created_at: string
}

// Generate mock predictions based on patients
function generateMockPredictions() {
  const predictions = []
  for (let i = 1; i <= 8; i++) {
    const numPreds = Math.floor(Math.random() * 3) + 1 // 1-3 predictions
    for (let j = 0; j < numPreds; j++) {
      const alzheimerRisk = Math.min(0.95, Math.max(0.1, 0.3 + Math.random() * 0.5))
      const parkinsonRisk = Math.min(0.95, Math.max(0.1, 0.25 + Math.random() * 0.5))
      
      const getRiskLevel = (score: number) => {
        if (score < 0.33) return 'low'
        if (score < 0.66) return 'medium'
        return 'high'
      }
      
      const diseaseType = alzheimerRisk > 0.5 && parkinsonRisk > 0.5 ? 'both' :
                         alzheimerRisk > parkinsonRisk ? 'alzheimer' : 'parkinson'
      
      predictions.push({
        id: predictions.length + 1,
        patient_id: i,
        created_by: 1,
        disease_type: diseaseType,
        alzheimer_risk_score: Math.round(alzheimerRisk * 1000) / 1000,
        alzheimer_risk_level: getRiskLevel(alzheimerRisk),
        alzheimer_confidence: Math.round((1.0 - 2.0 * Math.abs(alzheimerRisk - 0.5)) * 1000) / 1000,
        parkinson_risk_score: Math.round(parkinsonRisk * 1000) / 1000,
        parkinson_risk_level: getRiskLevel(parkinsonRisk),
        parkinson_confidence: Math.round((1.0 - 2.0 * Math.abs(parkinsonRisk - 0.5)) * 1000) / 1000,
        model_version: '1.0.0-mock',
        model_name: 'MockPredictionModel',
        created_at: new Date(Date.now() - Math.random() * 180 * 24 * 60 * 60 * 1000).toISOString(),
      })
    }
  }
  return predictions
}

// Inline patient data
const PATIENTS_DATA: MockPatient[] = [
  {
    id: 1,
    patient_id: "PT-2024-001",
    first_name: "احمد",
    last_name: "محمدی",
    date_of_birth: "1955-03-15",
    gender: "male",
    email: "ahmad.mohammadi@example.com",
    phone: "09123456789",
    education_years: 12,
    medical_history: "فشار خون بالا، دیابت نوع 2",
    family_history: "سابقه آلزایمر در مادر",
    created_at: "2024-01-15T10:00:00Z"
  },
  {
    id: 2,
    patient_id: "PT-2024-002",
    first_name: "فاطمه",
    last_name: "حسینی",
    date_of_birth: "1948-07-22",
    gender: "female",
    email: "fateme.hosseini@example.com",
    phone: "09123456790",
    education_years: 16,
    medical_history: "پوکی استخوان",
    family_history: "سابقه پارکینسون در پدر",
    created_at: "2024-01-20T10:00:00Z"
  },
  {
    id: 3,
    patient_id: "PT-2024-003",
    first_name: "محمد",
    last_name: "کریمی",
    date_of_birth: "1960-11-08",
    gender: "male",
    email: "mohammad.karimi@example.com",
    phone: "09123456791",
    education_years: 14,
    medical_history: "بیماری قلبی",
    family_history: "بدون سابقه",
    created_at: "2024-02-01T10:00:00Z"
  },
  {
    id: 4,
    patient_id: "PT-2024-004",
    first_name: "زهرا",
    last_name: "احمدی",
    date_of_birth: "1952-05-30",
    gender: "female",
    email: "zahra.ahmadi@example.com",
    phone: "09123456792",
    education_years: 10,
    medical_history: "کم‌خونی",
    family_history: "سابقه آلزایمر در خواهر",
    created_at: "2024-02-15T10:00:00Z"
  },
  {
    id: 5,
    patient_id: "PT-2024-005",
    first_name: "علی",
    last_name: "نوری",
    date_of_birth: "1958-09-12",
    gender: "male",
    email: "ali.nouri@example.com",
    phone: "09123456793",
    education_years: 18,
    medical_history: "آرتریت",
    family_history: "بدون سابقه",
    created_at: "2024-03-01T10:00:00Z"
  },
  {
    id: 6,
    patient_id: "PT-2024-006",
    first_name: "مریم",
    last_name: "صادقی",
    date_of_birth: "1945-12-03",
    gender: "female",
    email: "maryam.sadeghi@example.com",
    phone: "09123456794",
    education_years: 8,
    medical_history: "دیابت، فشار خون",
    family_history: "سابقه پارکینسون در مادر",
    created_at: "2024-03-15T10:00:00Z"
  },
  {
    id: 7,
    patient_id: "PT-2024-007",
    first_name: "حسن",
    last_name: "رضایی",
    date_of_birth: "1962-02-18",
    gender: "male",
    email: "hasan.rezaei@example.com",
    phone: "09123456795",
    education_years: 15,
    medical_history: "بدون سابقه",
    family_history: "بدون سابقه",
    created_at: "2024-03-22T10:00:00Z"
  },
  {
    id: 8,
    patient_id: "PT-2024-008",
    first_name: "سمیه",
    last_name: "موسوی",
    date_of_birth: "1950-08-25",
    gender: "female",
    email: "somayeh.mousavi@example.com",
    phone: "09123456796",
    education_years: 12,
    medical_history: "مشکلات تیروئید",
    family_history: "سابقه آلزایمر در مادربزرگ",
    created_at: "2024-03-26T10:00:00Z"
  }
]

export const mockDataService = {
  async getPatients(): Promise<MockPatient[]> {
    return Promise.resolve(PATIENTS_DATA)
  },

  async getPredictions(patientId?: number) {
    const predictions = generateMockPredictions()
    if (patientId) {
      return predictions.filter(p => p.patient_id === patientId)
    }
    return predictions
  },

  async getReportSummary() {
    const patients = await this.getPatients()
    const predictions = await this.getPredictions()
    const highRisk = predictions.filter(p => 
      p.alzheimer_risk_level === 'high' || p.parkinson_risk_level === 'high'
    ).length

    return {
      report_type: 'clinical',
      period: {
        start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        end: new Date().toISOString()
      },
      statistics: {
        total_patients: patients.length,
        total_predictions: predictions.length,
        high_risk_cases: highRisk,
        low_risk_cases: predictions.length - highRisk
      }
    }
  },

  async getPredictionsTrend(days: number = 7) {
    const predictions = await this.getPredictions()
    const trendData = []
    for (let i = 0; i < days; i++) {
      const date = new Date(Date.now() - (days - i - 1) * 24 * 60 * 60 * 1000)
      const dateStr = date.toISOString().split('T')[0]
      const count = predictions.filter(p => p.created_at.startsWith(dateStr)).length
      trendData.push({
        date: dateStr,
        count: count > 0 ? count : Math.floor(Math.random() * 3)
      })
    }
    return { period_days: days, data: trendData }
  },

  async getRiskDistribution() {
    const predictions = await this.getPredictions()
    const low = predictions.filter(p => 
      p.alzheimer_risk_level === 'low' && p.parkinson_risk_level === 'low'
    ).length
    const medium = predictions.filter(p => 
      p.alzheimer_risk_level === 'medium' || p.parkinson_risk_level === 'medium'
    ).length
    const high = predictions.filter(p => 
      p.alzheimer_risk_level === 'high' || p.parkinson_risk_level === 'high'
    ).length

    return {
      distribution: { low, medium, high },
      total: predictions.length
    }
  },

  async getAgeDistribution() {
    const patients = await this.getPatients()
    const ageGroups: Record<string, number> = { "40-50": 0, "50-60": 0, "60-70": 0, "70-80": 0, "80+": 0 }
    
    patients.forEach(patient => {
      const age = (Date.now() - new Date(patient.date_of_birth).getTime()) / (365.25 * 24 * 60 * 60 * 1000)
      if (age >= 40 && age < 50) ageGroups["40-50"]++
      else if (age >= 50 && age < 60) ageGroups["50-60"]++
      else if (age >= 60 && age < 70) ageGroups["60-70"]++
      else if (age >= 70 && age < 80) ageGroups["70-80"]++
      else if (age >= 80) ageGroups["80+"]++
    })

    return {
      distribution: Object.entries(ageGroups).map(([age_group, count]) => ({ age_group, count }))
    }
  },

  async getGenderDistribution() {
    const patients = await this.getPatients()
    const male = patients.filter(p => p.gender === 'male').length
    const female = patients.filter(p => p.gender === 'female').length
    const total = patients.length

    return {
      distribution: [
        { gender: 'Male', value: male, count: male, percentage: Math.round(male / total * 1000) / 10 },
        { gender: 'Female', value: female, count: female, percentage: Math.round(female / total * 1000) / 10 }
      ]
    }
  },

  async getPopulationStatistics() {
    const patients = await this.getPatients()
    const predictions = await this.getPredictions()
    const highRisk = predictions.filter(p => 
      p.alzheimer_risk_level === 'high' || p.parkinson_risk_level === 'high'
    ).length
    
    const totalAge = patients.reduce((sum, p) => {
      const age = (Date.now() - new Date(p.date_of_birth).getTime()) / (365.25 * 24 * 60 * 60 * 1000)
      return sum + age
    }, 0)

    return {
      total_patients: patients.length,
      total_predictions: predictions.length,
      high_risk_cases: highRisk,
      prevalence_percentage: Math.round(highRisk / patients.length * 10000) / 100,
      average_age: Math.round(totalAge / patients.length * 10) / 10,
      predictions_per_patient: Math.round(predictions.length / patients.length * 10) / 10
    }
  },

  async getLongitudinalData(patientId: number) {
    const predictions = await this.getPredictions(patientId)
    const timeline = predictions.map(pred => ({
      date: pred.created_at,
      prediction_id: pred.id,
      alzheimer_risk_score: pred.alzheimer_risk_score,
      parkinson_risk_score: pred.parkinson_risk_score,
    }))

    timeline.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

    return {
      patient_id: patientId,
      total_predictions: predictions.length,
      timeline
    }
  },

  async getModels() {
    return {
      models: [
        {
          id: 'alzheimer-v1.0',
          name: 'Alzheimer Prediction Model',
          version: '1.0.0',
          status: 'active',
          disease_type: 'alzheimer',
          accuracy: 0.95,
          precision: 0.93,
          recall: 0.94,
          f1_score: 0.935,
        },
        {
          id: 'parkinson-v1.0',
          name: 'Parkinson Prediction Model',
          version: '1.0.0',
          status: 'active',
          disease_type: 'parkinson',
          accuracy: 0.92,
          precision: 0.91,
          recall: 0.90,
          f1_score: 0.905,
        }
      ],
      total: 2
    }
  },

  async getUsers() {
    return [
      {
        id: 1,
        email: 'doctor@neuropredict.ai',
        username: 'doctor',
        full_name: 'دکتر نمونه',
        role: 'doctor',
        is_active: true
      },
      {
        id: 2,
        email: 'admin@neuropredict.ai',
        username: 'admin',
        full_name: 'مدیر سیستم',
        role: 'admin',
        is_active: true
      }
    ]
  }
}
