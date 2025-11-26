import { useRef, useMemo, useState } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Html, Environment } from '@react-three/drei'
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
    <group position={region.position}>
      {/* Main region mesh - rounded/smooth shape */}
      <mesh
        ref={meshRef}
        onPointerOver={() => onHover(region)}
        onPointerOut={() => onHover(null)}
        castShadow
        receiveShadow
      >
        <sphereGeometry args={[Math.max(...region.size) / 2, 32, 32]} />
        <meshPhysicalMaterial
          color={color}
          transparent
          opacity={opacity}
          emissive={color}
          emissiveIntensity={isHighlighted ? 1.2 : 0.4}
          roughness={0.2}
          metalness={0.3}
          clearcoat={1}
          clearcoatRoughness={0.3}
        />
      </mesh>
      
      {/* Outer glow effect for highlighted regions */}
      {isHighlighted && (
        <mesh scale={1.3}>
          <sphereGeometry args={[Math.max(...region.size) / 2, 16, 16]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={0.2}
            side={THREE.BackSide}
          />
        </mesh>
      )}
      
      {/* Risk indicator marker */}
      {riskLevel !== 'normal' && (
        <mesh position={[0, Math.max(...region.size) / 2 + 0.2, 0]}>
          <sphereGeometry args={[0.1, 16, 16]} />
          <meshStandardMaterial
            color={riskLevel === 'high' ? '#ef4444' : riskLevel === 'medium' ? '#f59e0b' : '#22c55e'}
            emissive={riskLevel === 'high' ? '#ef4444' : riskLevel === 'medium' ? '#f59e0b' : '#22c55e'}
            emissiveIntensity={2}
          />
        </mesh>
      )}
      
      {/* Tooltip */}
      {isHighlighted && (
        <Html distanceFactor={8} position={[0, Math.max(...region.size) / 2 + 0.5, 0]}>
          <div className="bg-slate-900/95 backdrop-blur-md text-white px-4 py-3 rounded-xl border-2 border-slate-600 shadow-2xl max-w-xs transform -translate-x-1/2">
            <div className="font-bold text-base mb-1.5">{region.name}</div>
            <div className="text-sm text-slate-300 mb-2">{region.description}</div>
            <div className="flex items-center gap-2">
              <span
                className={`px-3 py-1 rounded-lg font-semibold text-xs ${
                  riskLevel === 'high'
                    ? 'bg-red-600 text-white'
                    : riskLevel === 'medium'
                    ? 'bg-orange-600 text-white'
                    : riskLevel === 'low'
                    ? 'bg-green-600 text-white'
                    : 'bg-emerald-600 text-white'
                }`}
              >
                {riskLevel === 'normal' ? '✓ Healthy' : `⚠ ${riskLevel.toUpperCase()} RISK`}
              </span>
            </div>
          </div>
        </Html>
      )}
    </group>
  )
}

function BrainOutline() {
  const outlineRef = useRef<THREE.Group>(null)

  useFrame((state) => {
    if (outlineRef.current) {
      outlineRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.1) * 0.1
    }
  })

  return (
    <group ref={outlineRef}>
      {/* Main brain shape - more realistic ellipsoid */}
      <mesh scale={[1.5, 1.2, 1.3]} castShadow receiveShadow>
        <sphereGeometry args={[1.8, 64, 64]} />
        <meshPhysicalMaterial
          color="#1e293b"
          transparent
          opacity={0.08}
          roughness={0.8}
          metalness={0.1}
          transmission={0.1}
        />
      </mesh>
      
      {/* Cerebral hemispheres outline */}
      <mesh position={[-0.4, 0.2, 0]} scale={[0.8, 1, 1]}>
        <sphereGeometry args={[1.5, 32, 32]} />
        <meshBasicMaterial
          color="#475569"
          transparent
          opacity={0.05}
          wireframe
        />
      </mesh>
      <mesh position={[0.4, 0.2, 0]} scale={[0.8, 1, 1]}>
        <sphereGeometry args={[1.5, 32, 32]} />
        <meshBasicMaterial
          color="#475569"
          transparent
          opacity={0.05}
          wireframe
        />
      </mesh>
      
      {/* Subtle grid overlay for better depth perception */}
      <mesh scale={[1.5, 1.2, 1.3]}>
        <sphereGeometry args={[1.9, 24, 24]} />
        <meshBasicMaterial
          color="#64748b"
          transparent
          opacity={0.03}
          wireframe
        />
      </mesh>
    </group>
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
      {/* Legend - Enhanced */}
      <div className="absolute top-4 left-4 z-10 bg-slate-900/95 backdrop-blur-md rounded-2xl border-2 border-slate-700 shadow-2xl p-5 space-y-3 min-w-[260px]">
        <h3 className="text-base font-bold text-white mb-3 flex items-center gap-2">
          <span className="text-2xl">🧠</span>
          Brain Health Status
        </h3>
        <div className="space-y-2.5">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 rounded-lg bg-emerald-500 shadow-lg shadow-emerald-500/50"></div>
            <span className="text-sm font-medium text-slate-200">Normal / Healthy</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 rounded-lg bg-green-500 shadow-lg shadow-green-500/50"></div>
            <span className="text-sm font-medium text-slate-200">Low Risk</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 rounded-lg bg-orange-500 shadow-lg shadow-orange-500/50"></div>
            <span className="text-sm font-medium text-slate-200">Medium Risk</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 rounded-lg bg-red-500 shadow-lg shadow-red-500/50"></div>
            <span className="text-sm font-medium text-slate-200">High Risk</span>
          </div>
        </div>

        <div className="border-t-2 border-slate-700 pt-3 mt-3 space-y-2">
          <div className="text-sm">
            <span className="text-slate-400 font-medium">Alzheimer's:</span>
            <div
              className={`mt-1 px-3 py-1.5 rounded-lg font-bold text-sm inline-block ${
                alzheimerLevel === 'high'
                  ? 'bg-red-600 text-white'
                  : alzheimerLevel === 'medium'
                  ? 'bg-orange-600 text-white'
                  : 'bg-green-600 text-white'
              }`}
            >
              {(alzheimerRisk * 100).toFixed(1)}% - {alzheimerLevel.toUpperCase()}
            </div>
          </div>
          <div className="text-sm">
            <span className="text-slate-400 font-medium">Parkinson's:</span>
            <div
              className={`mt-1 px-3 py-1.5 rounded-lg font-bold text-sm inline-block ${
                parkinsonLevel === 'high'
                  ? 'bg-red-600 text-white'
                  : parkinsonLevel === 'medium'
                  ? 'bg-orange-600 text-white'
                  : 'bg-green-600 text-white'
              }`}
            >
              {(parkinsonRisk * 100).toFixed(1)}% - {parkinsonLevel.toUpperCase()}
            </div>
          </div>
        </div>
      </div>

      {/* Overall Status Indicator - Enhanced */}
      <div className="absolute top-4 right-4 z-10 bg-slate-900/95 backdrop-blur-md rounded-2xl border-2 border-slate-700 shadow-2xl p-6">
        <div className="text-center">
          <div
            className={`text-6xl mb-3 ${
              isHealthy ? 'text-emerald-400' : alzheimerRisk > 0.66 || parkinsonRisk > 0.66 ? 'text-red-400' : 'text-orange-400'
            }`}
          >
            {isHealthy ? '✓' : alzheimerRisk > 0.66 || parkinsonRisk > 0.66 ? '⚠' : '⚠'}
          </div>
          <div className={`text-sm font-bold mb-1 ${
              isHealthy ? 'text-emerald-300' : alzheimerRisk > 0.66 || parkinsonRisk > 0.66 ? 'text-red-300' : 'text-orange-300'
            }`}>
            {isHealthy ? 'Healthy Brain' : alzheimerRisk > 0.66 || parkinsonRisk > 0.66 ? 'High Risk' : 'Risk Detected'}
          </div>
          <div className="text-xs text-slate-400">
            {isHealthy ? 'No significant risks' : 'Review affected regions'}
          </div>
        </div>
      </div>

      {/* Instructions - Enhanced */}
      <div className="absolute bottom-4 left-4 z-10 bg-slate-900/95 backdrop-blur-md rounded-xl border-2 border-slate-700 shadow-2xl px-4 py-3">
        <p className="text-sm text-slate-300 flex items-center gap-2">
          <span className="text-lg">💡</span>
          <span>
            <span className="font-bold text-white">Interact:</span> Drag to rotate • Scroll to zoom • Hover for details
          </span>
        </p>
      </div>

      {/* 3D Canvas - High Quality */}
      <Canvas
        camera={{ position: [0, 0, 6], fov: 45 }}
        style={{ background: 'transparent' }}
        shadows
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: 'high-performance',
        }}
        dpr={[1, 2]} // Support high DPI displays
      >
        {/* Enhanced Lighting Setup for Better Visuals */}
        <ambientLight intensity={0.4} color="#94a3b8" />
        
        {/* Key light - main illumination */}
        <directionalLight
          position={[5, 8, 5]}
          intensity={1.2}
          castShadow
          shadow-mapSize-width={2048}
          shadow-mapSize-height={2048}
          shadow-camera-far={50}
          shadow-camera-left={-10}
          shadow-camera-right={10}
          shadow-camera-top={10}
          shadow-camera-bottom={-10}
          color="#ffffff"
        />
        
        {/* Fill light - soften shadows */}
        <directionalLight position={[-5, 3, -5]} intensity={0.5} color="#8b9dc3" />
        
        {/* Rim light - enhance edges */}
        <pointLight position={[0, 0, -8]} intensity={0.8} color="#6366f1" />
        
        {/* Top light for depth */}
        <pointLight position={[0, 10, 0]} intensity={0.6} color="#f8fafc" />
        
        {/* Bottom light for balance */}
        <pointLight position={[0, -10, 0]} intensity={0.3} color="#475569" />
        
        {/* Spot lights for highlights */}
        <spotLight
          position={[8, 8, 8]}
          angle={0.4}
          penumbra={1}
          intensity={0.8}
          castShadow
          color="#ffffff"
        />

        {/* Environment for reflections and ambient lighting */}
        <Environment preset="city" />
        
        {/* Fog for depth perception */}
        <fog attach="fog" args={['#0f172a', 8, 15]} />

        {/* Brain outline */}
        <BrainOutline />

        {/* Brain regions with improved materials */}
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
          enablePan={true}
          minDistance={4}
          maxDistance={10}
          enableDamping
          dampingFactor={0.03}
          rotateSpeed={0.5}
          autoRotate
          autoRotateSpeed={0.5}
        />
      </Canvas>
    </div>
  )
}

