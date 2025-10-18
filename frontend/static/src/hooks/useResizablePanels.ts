import { useCallback, useEffect, useRef, useState } from 'react'

interface UseResizablePanelsProps {
  leftMinWidth: number
  leftMaxWidth: number
  leftDefaultWidth: number
  rightMinWidth: number
  rightMaxWidth: number
  rightDefaultWidth: number
  isLeftOpen: boolean
  isRightOpen: boolean
}

interface UseResizablePanelsReturn {
  leftWidth: number
  rightWidth: number
  handleLeftResize: (event: React.MouseEvent) => void
  handleRightResize: (event: React.MouseEvent) => void
  isResizing: boolean
}

export function useResizablePanels({
  leftMinWidth,
  leftMaxWidth,
  leftDefaultWidth,
  rightMinWidth,
  rightMaxWidth,
  rightDefaultWidth,
  isLeftOpen,
  isRightOpen
}: UseResizablePanelsProps): UseResizablePanelsReturn {
  const [leftWidth, setLeftWidth] = useState(leftDefaultWidth)
  const [rightWidth, setRightWidth] = useState(rightDefaultWidth)
  const [isResizing, setIsResizing] = useState(false)
  const resizeRef = useRef<{
    isResizing: boolean
    panel: 'left' | 'right' | null
    startX: number
    startWidth: number
  }>({
    isResizing: false,
    panel: null,
    startX: 0,
    startWidth: 0
  })

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!resizeRef.current.isResizing || !resizeRef.current.panel) return

    const deltaX = e.clientX - resizeRef.current.startX
    
    if (resizeRef.current.panel === 'left') {
      const newWidth = Math.max(
        leftMinWidth,
        Math.min(leftMaxWidth, resizeRef.current.startWidth + deltaX)
      )
      setLeftWidth(newWidth)
      
      // Update CSS variable for smooth transition
      document.documentElement.style.setProperty('--left-width', `${newWidth}px`)
    } else if (resizeRef.current.panel === 'right') {
      const newWidth = Math.max(
        rightMinWidth,
        Math.min(rightMaxWidth, resizeRef.current.startWidth - deltaX)
      )
      setRightWidth(newWidth)
      
      // Update CSS variable for smooth transition
      document.documentElement.style.setProperty('--right-width', `${newWidth}px`)
    }
  }, [leftMinWidth, leftMaxWidth, rightMinWidth, rightMaxWidth])

  const handleMouseUp = useCallback(() => {
    if (resizeRef.current.isResizing) {
      setIsResizing(false)
      resizeRef.current.isResizing = false
      resizeRef.current.panel = null
      document.body.classList.remove('resizing')
      
      // Save to localStorage for persistence
      localStorage.setItem('aura-left-width', leftWidth.toString())
      localStorage.setItem('aura-right-width', rightWidth.toString())
    }
  }, [leftWidth, rightWidth])

  const handleLeftResize = useCallback((event: React.MouseEvent) => {
    if (!isLeftOpen) return
    
    event.preventDefault()
    // eslint-disable-next-line no-console
    console.log('🔧 Starting left sidebar resize')
    setIsResizing(true)
    resizeRef.current.isResizing = true
    resizeRef.current.panel = 'left'
    resizeRef.current.startX = event.clientX
    resizeRef.current.startWidth = leftWidth
    document.body.classList.add('resizing')
  }, [isLeftOpen, leftWidth])

  const handleRightResize = useCallback((event: React.MouseEvent) => {
    if (!isRightOpen) return
    
    event.preventDefault()
    // eslint-disable-next-line no-console
    console.log('🔧 Starting right sidebar resize')
    setIsResizing(true)
    resizeRef.current.isResizing = true
    resizeRef.current.panel = 'right'
    resizeRef.current.startX = event.clientX
    resizeRef.current.startWidth = rightWidth
    document.body.classList.add('resizing')
  }, [isRightOpen, rightWidth])

  // Setup global mouse events
  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [handleMouseMove, handleMouseUp])

  // Load saved widths from localStorage
  useEffect(() => {
    const savedLeftWidth = localStorage.getItem('aura-left-width')
    const savedRightWidth = localStorage.getItem('aura-right-width')
    
    if (savedLeftWidth) {
      const width = parseInt(savedLeftWidth, 10)
      if (width >= leftMinWidth && width <= leftMaxWidth) {
        setLeftWidth(width)
      }
    }
    
    if (savedRightWidth) {
      const width = parseInt(savedRightWidth, 10)
      if (width >= rightMinWidth && width <= rightMaxWidth) {
        setRightWidth(width)
      }
    }
  }, [leftMinWidth, leftMaxWidth, rightMinWidth, rightMaxWidth])

  // Set initial CSS variables on mount and when widths change from localStorage
  useEffect(() => {
    document.documentElement.style.setProperty('--left-width', `${leftWidth}px`)
    document.documentElement.style.setProperty('--right-width', `${rightWidth}px`)
  }, [leftWidth, rightWidth]) // Run when widths change (including initial mount)

  return {
    leftWidth,
    rightWidth,
    handleLeftResize,
    handleRightResize,
    isResizing
  }
}