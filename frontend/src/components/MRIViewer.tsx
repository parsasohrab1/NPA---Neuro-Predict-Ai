import { useState, useRef, useEffect } from 'react'
import { imagingApi } from '../services/api'
import {
  MagnifyingGlassIcon,
  ArrowsPointingOutIcon,
  ArrowsPointingInIcon,
  ArrowPathIcon,
  PhotoIcon,
} from '@heroicons/react/24/outline'

interface MRIViewerProps {
  studyId: number
  initialSlice?: number
  onSliceChange?: (slice: number) => void
  showControls?: boolean
  enableMeasurement?: boolean
  enableOverlay?: boolean
  comparisonStudyId?: number
}

export default function MRIViewer({
  studyId,
  initialSlice = 0,
  onSliceChange,
  showControls = true,
  enableMeasurement = true,
  enableOverlay = false,
  comparisonStudyId,
}: MRIViewerProps) {
  const [currentSlice, setCurrentSlice] = useState(initialSlice)
  const [totalSlices, setTotalSlices] = useState(1)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [windowLevel, setWindowLevel] = useState({ window: 400, level: 50 })
  const [measurements, setMeasurements] = useState<Array<{ id: string; x1: number; y1: number; x2: number; y2: number; distance?: number }>>([])
  const [isMeasuring, setIsMeasuring] = useState(false)
  const [measureStart, setMeasureStart] = useState<{ x: number; y: number } | null>(null)
  const [showOverlay, setShowOverlay] = useState(false)
  const [overlayOpacity, setOverlayOpacity] = useState(0.5)
  const [highlight3D, setHighlight3D] = useState(false)

  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)

  // Fetch slice info
  useEffect(() => {
    imagingApi
      .getStudySlices(studyId)
      .then((info) => {
        setTotalSlices(info.total_slices)
        if (currentSlice >= info.total_slices) {
          setCurrentSlice(0)
        }
      })
      .catch((err) => {
        console.error('Failed to fetch slice info:', err)
      })
  }, [studyId])

  // Load image when slice changes
  useEffect(() => {
    if (imageRef.current) {
      imageRef.current.src = imagingApi.getStudySlice(studyId, currentSlice)
    }
    if (onSliceChange) {
      onSliceChange(currentSlice)
    }
  }, [studyId, currentSlice, onSliceChange])

  // Draw on canvas
  useEffect(() => {
    const canvas = canvasRef.current
    const image = imageRef.current
    if (!canvas || !image) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const draw = () => {
      if (!image.complete) {
        image.onload = draw
        return
      }

      canvas.width = image.width
      canvas.height = image.height

      // Apply window/level
      ctx.drawImage(image, 0, 0)

      // Apply window/level effect (simplified)
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      const data = imageData.data
      const { window: w, level: l } = windowLevel

      for (let i = 0; i < data.length; i += 4) {
        const gray = (data[i] + data[i + 1] + data[i + 2]) / 3
        const normalized = Math.max(0, Math.min(255, ((gray - (l - w / 2)) / w) * 255))
        data[i] = normalized
        data[i + 1] = normalized
        data[i + 2] = normalized
      }

      ctx.putImageData(imageData, 0, 0)

      // Draw measurements
      ctx.strokeStyle = '#00ff00'
      ctx.lineWidth = 2
      ctx.font = '14px Arial'
      ctx.fillStyle = '#00ff00'

      measurements.forEach((measure) => {
        ctx.beginPath()
        ctx.moveTo(measure.x1, measure.y1)
        ctx.lineTo(measure.x2, measure.y2)
        ctx.stroke()

        if (measure.distance) {
          const midX = (measure.x1 + measure.x2) / 2
          const midY = (measure.y1 + measure.y2) / 2
          ctx.fillText(`${measure.distance.toFixed(1)} mm`, midX + 5, midY - 5)
        }
      })

      // Draw 3D highlights if enabled
      if (highlight3D) {
        ctx.strokeStyle = '#ff00ff'
        ctx.lineWidth = 3
        ctx.setLineDash([5, 5])
        ctx.strokeRect(50, 50, canvas.width - 100, canvas.height - 100)
        ctx.setLineDash([])
      }
    }

    draw()
  }, [imageRef.current?.complete, windowLevel, measurements, highlight3D])

  const handleSliceChange = (newSlice: number) => {
    const clamped = Math.max(0, Math.min(totalSlices - 1, newSlice))
    setCurrentSlice(clamped)
  }

  const handleZoom = (delta: number) => {
    setZoom((prev) => Math.max(0.5, Math.min(5, prev + delta)))
  }

  const handleReset = () => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
    setWindowLevel({ window: 400, level: 50 })
    setMeasurements([])
  }

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (isMeasuring) {
      const rect = canvasRef.current?.getBoundingClientRect()
      if (rect) {
        const x = e.clientX - rect.left
        const y = e.clientY - rect.top
        if (!measureStart) {
          setMeasureStart({ x, y })
        } else {
          // Complete measurement
          const distance = Math.sqrt(
            Math.pow(x - measureStart.x, 2) + Math.pow(y - measureStart.y, 2)
          )
          setMeasurements([
            ...measurements,
            {
              id: Date.now().toString(),
              x1: measureStart.x,
              y1: measureStart.y,
              x2: x,
              y2: y,
              distance: distance * 0.1, // Convert pixels to mm (simplified)
            },
          ])
          setMeasureStart(null)
          setIsMeasuring(false)
        }
      }
    } else {
      setIsDragging(true)
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
    }
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      })
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  return (
    <div className="relative bg-black rounded-lg overflow-hidden" ref={containerRef}>
      {/* Toolbar */}
      {showControls && (
        <div className="absolute top-2 left-2 right-2 z-10 flex items-center gap-2 bg-black/70 backdrop-blur-sm rounded-lg p-2">
          <div className="flex items-center gap-2 flex-1">
            <button
              onClick={() => handleSliceChange(currentSlice - 1)}
              disabled={currentSlice === 0}
              className="px-2 py-1 bg-gray-700 text-white rounded disabled:opacity-50"
            >
              ←
            </button>
            <span className="text-white text-sm min-w-[100px] text-center">
              Slice {currentSlice + 1} / {totalSlices}
            </span>
            <button
              onClick={() => handleSliceChange(currentSlice + 1)}
              disabled={currentSlice >= totalSlices - 1}
              className="px-2 py-1 bg-gray-700 text-white rounded disabled:opacity-50"
            >
              →
            </button>
            <input
              type="range"
              min="0"
              max={totalSlices - 1}
              value={currentSlice}
              onChange={(e) => handleSliceChange(Number(e.target.value))}
              className="flex-1"
            />
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleZoom(0.1)}
              className="p-1 bg-gray-700 text-white rounded"
              title="Zoom In"
            >
              <ArrowsPointingOutIcon className="h-4 w-4" />
            </button>
            <button
              onClick={() => handleZoom(-0.1)}
              className="p-1 bg-gray-700 text-white rounded"
              title="Zoom Out"
            >
              <ArrowsPointingInIcon className="h-4 w-4" />
            </button>
            <button
              onClick={handleReset}
              className="p-1 bg-gray-700 text-white rounded"
              title="Reset"
            >
              <ArrowPathIcon className="h-4 w-4" />
            </button>
            {enableMeasurement && (
              <button
                onClick={() => setIsMeasuring(!isMeasuring)}
                className={`p-1 rounded ${isMeasuring ? 'bg-green-600' : 'bg-gray-700'} text-white`}
                title="Toggle Measurement"
              >
                <MagnifyingGlassIcon className="h-4 w-4" />
              </button>
            )}
            {enableOverlay && comparisonStudyId && (
              <button
                onClick={() => setShowOverlay(!showOverlay)}
                className={`p-1 rounded ${showOverlay ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
                title="Toggle Overlay"
              >
                <PhotoIcon className="h-4 w-4" />
              </button>
            )}
            <button
              onClick={() => setHighlight3D(!highlight3D)}
              className={`p-1 rounded ${highlight3D ? 'bg-purple-600' : 'bg-gray-700'} text-white`}
              title="3D Highlights"
            >
              3D
            </button>
          </div>
        </div>
      )}

      {/* Window/Level Controls */}
      {showControls && (
        <div className="absolute bottom-2 left-2 right-2 z-10 bg-black/70 backdrop-blur-sm rounded-lg p-2">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <label className="text-white text-xs mb-1 block">Window</label>
              <input
                type="range"
                min="100"
                max="2000"
                value={windowLevel.window}
                onChange={(e) => setWindowLevel({ ...windowLevel, window: Number(e.target.value) })}
                className="w-full"
              />
              <span className="text-white text-xs">{windowLevel.window}</span>
            </div>
            <div className="flex-1">
              <label className="text-white text-xs mb-1 block">Level</label>
              <input
                type="range"
                min="0"
                max="255"
                value={windowLevel.level}
                onChange={(e) => setWindowLevel({ ...windowLevel, level: Number(e.target.value) })}
                className="w-full"
              />
              <span className="text-white text-xs">{windowLevel.level}</span>
            </div>
            {showOverlay && comparisonStudyId && (
              <div className="flex-1">
                <label className="text-white text-xs mb-1 block">Overlay Opacity</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={overlayOpacity}
                  onChange={(e) => setOverlayOpacity(Number(e.target.value))}
                  className="w-full"
                />
                <span className="text-white text-xs">{(overlayOpacity * 100).toFixed(0)}%</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Canvas Container */}
      <div className="relative w-full h-full flex items-center justify-center overflow-hidden">
        <div
          style={{
            transform: `scale(${zoom}) translate(${pan.x / zoom}px, ${pan.y / zoom}px)`,
            transformOrigin: 'center center',
          }}
        >
          <img
            ref={imageRef}
            alt={`MRI Slice ${currentSlice}`}
            className="hidden"
            onLoad={() => {
              // Trigger redraw
              if (canvasRef.current) {
                const canvas = canvasRef.current
                const ctx = canvas.getContext('2d')
                if (ctx && imageRef.current) {
                  canvas.width = imageRef.current.width
                  canvas.height = imageRef.current.height
                  ctx.drawImage(imageRef.current, 0, 0)
                }
              }
            }}
          />
          <canvas
            ref={canvasRef}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            className="cursor-crosshair max-w-full max-h-[600px]"
            style={{ imageRendering: 'pixelated' }}
          />
        </div>

        {/* Overlay Image */}
        {showOverlay && comparisonStudyId && (
          <img
            src={imagingApi.getStudySlice(comparisonStudyId, currentSlice)}
            alt="Comparison Overlay"
            className="absolute inset-0 opacity-50 pointer-events-none"
            style={{ opacity: overlayOpacity }}
          />
        )}
      </div>

      {/* Measurement Info */}
      {measurements.length > 0 && (
        <div className="absolute top-16 right-2 bg-black/70 backdrop-blur-sm rounded-lg p-2 text-white text-xs max-h-32 overflow-y-auto">
          <div className="font-semibold mb-1">Measurements:</div>
          {measurements.map((m) => (
            <div key={m.id} className="mb-1">
              {m.distance?.toFixed(1)} mm
            </div>
          ))}
          <button
            onClick={() => setMeasurements([])}
            className="mt-2 px-2 py-1 bg-red-600 rounded text-xs"
          >
            Clear
          </button>
        </div>
      )}
    </div>
  )
}

