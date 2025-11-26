import { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'
import * as THREE from 'three'

// Brain region definitions with their positions and sizes
interface BrainRegion {
  name: string
  position: [number, number, number]
  size: [number, number, number]
  diseaseType: 'alzheimer' | 'parkinson' | 'both' | 'general'
  description: string
}

const BRAIN_REGIONS: BrainRegion[] = [
  // Alzheimer's related regions
  {
    name: 'Hippocampus (L)',
    position: [-0.8, -0.3, 0],
    size: [0.4, 0.3, 0.5],
    diseaseType: 'alzheimer',
    description: 'Memory formation & consolidation',
  },
  {
    name: 'Hippocampus (R)',
    position: [0.8, -0.3, 0],
    size: [0.4, 0.3, 0.5],
    diseaseType: 'alzheimer',
    description: 'Memory formation & consolidation',
  },
  {
    name: 'Temporal Lobe (L)',
    position: [-1.2, 0, 0],
    size: [0.5, 0.8, 0.8],
    diseaseType: 'alzheimer',
    description: 'Language & memory processing',
  },
  {
    name: 'Temporal Lobe (R)',
    position: [1.2, 0, 0],
    size: [0.5, 0.8, 0.8],
    diseaseType: 'alzheimer',
    description: 'Language & memory processing',
  },
  {
    name: 'Entorhinal Cortex',
    position: [0, -0.5, 0.3],
    size: [0.6, 0.3, 0.4],
    diseaseType: 'alzheimer',
    description: 'Memory & navigation hub',
  },
  {
    name: 'Parietal Lobe',
    position: [0, 0.5, -0.5],
    size: [1.2, 0.6, 0.5],
    diseaseType: 'alzheimer',
    description: 'Spatial awareness & attention',
  },

  // Parkinson's related regions
  {
    name: 'Substantia Nigra',
    position: [0, -0.8, -0.3],
    size: [0.3, 0.2, 0.3],
    diseaseType: 'parkinson',
    description: 'Dopamine production',
  },
  {
    name: 'Basal Ganglia (L)',
    position: [-0.5, -0.2, -0.2],
    size: [0.3, 0.4, 0.3],
    diseaseType: 'parkinson',
    description: 'Movement control',
  },
  {
    name: 'Basal Ganglia (R)',
    position: [0.5, -0.2, -0.2],
    size: [0.3, 0.4, 0.3],
    diseaseType: 'parkinson',
    description: 'Movement control',
  },
  {
    name: 'Motor Cortex',
    position: [0, 1.0, 0],
    size: [1.0, 0.3, 0.6],
    diseaseType: 'parkinson',
    description: 'Voluntary movement execution',
  },

  // General brain structures
  {
    name: 'Frontal Lobe',
    position: [0, 0.6, 0.8],
    size: [1.2, 0.8, 0.6],
    diseaseType: 'general',
    description: 'Executive functions & decision making',
  },
  {
    name: 'Cerebellum',
    position: [0, -1.0, -0.8],
    size: [1.0, 0.5, 0.5],
    diseaseType: 'general',
    description: 'Coordination & balance',
  },
  {
    name: 'Brainstem',
    position: [0, -1.2, 0],
    size: [0.3, 0.5, 0.3],
    diseaseType: 'general',
    description: 'Vital functions control',
  },
]

interface BrainRegionMeshProps {
  region: BrainRegion
  riskLevel: 'low' | 'medium' | 'high' | 'normal'
  isHighlighted: boolean
  onHover: (region: BrainRegion | null) => void
}

function BrainRegionMesh({ region, riskLevel, isHighlighted, onHover }: BrainRegionMeshProps) {
  const meshRef = useRef<THREE.Mesh>(null)

  // Determine color based on risk level and disease type
  const color = useMemo(() => {
    if (riskLevel === 'normal') return '#10b981' // Green for normal
    if (riskLevel === 'high') return '#ef4444' // Red for high risk
    if (riskLevel === 'medium') return '#f59e0b' // Orange for medium risk
    return '#22c55e' // Light green for low risk
  }, [riskLevel])

  // Animation
  useFrame((state) => {
    if (meshRef.current && isHighlighted) {
      const scale = 1 + Math.sin(state.clock.elapsedTime * 3) * 0.1
      meshRef.current.scale.setScalar(scale)
    } else if (meshRef.current) {
      meshRef.current.scale.setScalar(1)
    }
  })

  const opacity = riskLevel === 'normal' ? 0.3 : 0.7

  return (
    <mesh
      ref={meshRef}
      position={region.position}
      onPointerOver={() => onHover(region)}
      onPointerOut={() => onHover(null)}
    >
      <boxGeometry args={region.size} />
      <meshStandardMaterial
        color={color}
        transparent
        opacity={opacity}
        emissive={color}
        emissiveIntensity={isHighlighted ? 0.8 : 0.3}
        roughness={0.3}
        metalness={0.2}
      />
      {isHighlighted && (
        <Html distanceFactor={10}>
          <div className="bg-slate-900/95 text-white px-3 py-2 rounded-lg border border-slate-700 shadow-lg max-w-xs">
            <div className="font-bold text-sm mb-1">{region.name}</div>
            <div className="text-xs text-slate-300">{region.description}</div>
            <div className="text-xs mt-1">
              <span
                className={`px-2 py-0.5 rounded ${
                  riskLevel === 'high'
                    ? 'bg-red-600'
                    : riskLevel === 'medium'
                    ? 'bg-orange-600'
                    : riskLevel === 'low'
                    ? 'bg-green-600'
                    : 'bg-emerald-600'
                }`}
              >
                {riskLevel === 'normal' ? 'Healthy' : `${riskLevel.toUpperCase()} RISK`}
              </span>
            </div>
          </div>
        </Html>
      )}
    </mesh>
  )
}

function BrainOutline() {
  const outlineRef = useRef<THREE.Mesh>(null)

  useFrame((state) => {
    if (outlineRef.current) {
      outlineRef.current.rotation.y += 0.001
    }
  })

  return (
    <mesh ref={outlineRef}>
      <sphereGeometry args={[2.2, 32, 32, 0, Math.PI * 2, 0, Math.PI * 0.7]} />
      <meshStandardMaterial
        color="#1e293b"
        transparent
        opacity={0.1}
        wireframe
        emissive="#475569"
        emissiveIntensity={0.2}
      />
    </mesh>
  )
}

interface BrainVisualization3DProps {
  alzheimerRisk: number // 0-1
  parkinsonRisk: number // 0-1
  className?: string
}

export default function BrainVisualization3D({
  alzheimerRisk,
  parkinsonRisk,
  className = '',
}: BrainVisualization3DProps) {
  const [hoveredRegion, setHoveredRegion] = useState<BrainRegion | null>(null)

  // Determine risk level from score
  const getRiskLevel = (score: number): 'low' | 'medium' | 'high' | 'normal' => {
    if (score >= 0.66) return 'high'
    if (score >= 0.33) return 'medium'
    if (score > 0) return 'low'
    return 'normal'
  }

  const alzheimerLevel = getRiskLevel(alzheimerRisk)
  const parkinsonLevel = getRiskLevel(parkinsonRisk)

  // Determine if the overall brain is healthy
  const isHealthy = alzheimerRisk < 0.33 && parkinsonRisk < 0.33

  return (
    <div className={`relative ${className}`}>
      {/* Legend */}
      <div className="absolute top-4 left-4 z-10 bg-slate-900/90 backdrop-blur-sm rounded-xl border border-slate-700 p-4 space-y-2">
        <h3 className="text-sm font-bold text-white mb-2">Brain Health Status</h3>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-emerald-500"></div>
            <span className="text-xs text-slate-300">Normal / Healthy</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-500"></div>
            <span className="text-xs text-slate-300">Low Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-orange-500"></div>
            <span className="text-xs text-slate-300">Medium Risk</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-red-500"></div>
            <span className="text-xs text-slate-300">High Risk</span>
          </div>
        </div>

        <div className="border-t border-slate-700 pt-2 mt-2 space-y-1">
          <div className="text-xs">
            <span className="text-slate-400">Alzheimer's Risk:</span>
            <span
              className={`ml-2 font-bold ${
                alzheimerLevel === 'high'
                  ? 'text-red-400'
                  : alzheimerLevel === 'medium'
                  ? 'text-orange-400'
                  : 'text-green-400'
              }`}
            >
              {(alzheimerRisk * 100).toFixed(1)}% ({alzheimerLevel.toUpperCase()})
            </span>
          </div>
          <div className="text-xs">
            <span className="text-slate-400">Parkinson's Risk:</span>
            <span
              className={`ml-2 font-bold ${
                parkinsonLevel === 'high'
                  ? 'text-red-400'
                  : parkinsonLevel === 'medium'
                  ? 'text-orange-400'
                  : 'text-green-400'
              }`}
            >
              {(parkinsonRisk * 100).toFixed(1)}% ({parkinsonLevel.toUpperCase()})
            </span>
          </div>
        </div>
      </div>

      {/* Overall Status Indicator */}
      <div className="absolute top-4 right-4 z-10 bg-slate-900/90 backdrop-blur-sm rounded-xl border border-slate-700 p-4">
        <div className="text-center">
          <div
            className={`text-4xl mb-2 ${
              isHealthy ? 'text-emerald-400' : 'text-orange-400'
            }`}
          >
            {isHealthy ? '✓' : '⚠'}
          </div>
          <div className="text-xs font-bold text-white">
            {isHealthy ? 'Healthy Brain' : 'Risk Detected'}
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="absolute bottom-4 left-4 z-10 bg-slate-900/90 backdrop-blur-sm rounded-xl border border-slate-700 px-3 py-2">
        <p className="text-xs text-slate-400">
          🖱️ Click and drag to rotate • Scroll to zoom • Hover over regions for details
        </p>
      </div>

      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [0, 0, 5], fov: 50 }}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <pointLight position={[-10, -10, -10]} intensity={0.5} />
        <spotLight position={[0, 10, 0]} angle={0.3} intensity={0.5} />

        {/* Brain outline */}
        <BrainOutline />

        {/* Brain regions */}
        {BRAIN_REGIONS.map((region) => {
          let regionRiskLevel: 'low' | 'medium' | 'high' | 'normal' = 'normal'

          if (region.diseaseType === 'alzheimer') {
            regionRiskLevel = alzheimerLevel
          } else if (region.diseaseType === 'parkinson') {
            regionRiskLevel = parkinsonLevel
          } else if (region.diseaseType === 'both') {
            // Use the higher risk
            const maxRisk = Math.max(alzheimerRisk, parkinsonRisk)
            regionRiskLevel = getRiskLevel(maxRisk)
          } else {
            // General regions remain normal unless there's very high overall risk
            if (alzheimerRisk > 0.8 || parkinsonRisk > 0.8) {
              regionRiskLevel = 'low'
            }
          }

          return (
            <BrainRegionMesh
              key={region.name}
              region={region}
              riskLevel={regionRiskLevel}
              isHighlighted={hoveredRegion?.name === region.name}
              onHover={setHoveredRegion}
            />
          )
        })}

        <OrbitControls
          enablePan={false}
          minDistance={3}
          maxDistance={8}
          enableDamping
          dampingFactor={0.05}
        />
      </Canvas>
    </div>
  )
}

