"use client"

import { useRef, useEffect, useCallback } from "react"

const LetterGlitch = ({
  glitchColors = ["#2b4539", "#61dca3", "#61b3dc"],
  glitchSpeed = 50,
  centerVignette = false,
  outerVignette = true,
  smooth = true,
}: {
  glitchColors?: string[]
  glitchSpeed?: number
  centerVignette?: boolean
  outerVignette?: boolean
  smooth?: boolean
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const animationRef = useRef<number | null>(null)
  const letters = useRef<
    {
      char: string
      color: string
      targetColor: string
      colorProgress: number
    }[]
  >([])
  const grid = useRef({ columns: 0, rows: 0 })
  const context = useRef<CanvasRenderingContext2D | null>(null)
  const lastGlitchTime = useRef(Date.now())

  const fontSize = 16
  const charWidth = 10
  const charHeight = 20

  const getRandomColor = useCallback(() => {
    return glitchColors[Math.floor(Math.random() * glitchColors.length)]
  }, [glitchColors])

  const initLetters = (text: string) => {
    letters.current = []
    for (let i = 0; i < text.length; i++) {
      letters.current.push({
        char: text[i],
        color: getRandomColor(),
        targetColor: getRandomColor(),
        colorProgress: 0,
      })
    }
  }

  const glitch = useCallback(() => {
    if (Date.now() - lastGlitchTime.current < 100) return
    lastGlitchTime.current = Date.now()

    const glitchAmount = Math.floor(Math.random() * letters.current.length)

    for (let i = 0; i < glitchAmount; i++) {
      const randomIndex = Math.floor(Math.random() * letters.current.length)
      letters.current[randomIndex].targetColor = getRandomColor()
    }
  }, [getRandomColor])

  const draw = useCallback(() => {
    if (!context.current) return

    context.current.clearRect(0, 0, context.current.canvas.width, context.current.canvas.height)
    letters.current.forEach((letter, i) => {
      const x = (i % grid.current.columns) * charWidth
      const y = Math.floor(i / grid.current.columns) * charHeight

      // Smooth color transition
      letter.colorProgress += 0.025 * glitchSpeed
      if (letter.colorProgress > 1) {
        letter.colorProgress = 0
        letter.color = letter.targetColor
        letter.targetColor = getRandomColor()
      }

      const color = smooth ? lerpColor(letter.color, letter.targetColor, letter.colorProgress) : letter.color

      context.current.fillStyle = color
      context.current.fillText(letter.char, x, y)
    })
  }, [glitchSpeed, smooth, getRandomColor])

  const lerpColor = (a: string, b: string, amount: number) => {
    const ah = Number.parseInt(a.replace(/#/g, ""), 16)
    const ar = ah >> 16
    const ag = (ah >> 8) & 0xff
    const ab = ah & 0xff
    const bh = Number.parseInt(b.replace(/#/g, ""), 16)
    const br = bh >> 16
    const bg = (bh >> 8) & 0xff
    const bb = bh & 0xff
    const rr = ar + amount * (br - ar)
    const rg = ag + amount * (bg - ag)
    const rb = ab + amount * (bb - ab)

    return "#" + (((1 << 24) + (rr << 16) + (rg << 8) + rb) | 0).toString(16).slice(1)
  }

  const resizeCanvas = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const container = canvas.parentNode as HTMLElement

    canvas.width = container.offsetWidth
    canvas.height = container.offsetHeight

    grid.current.columns = Math.floor(canvas.width / charWidth)
    grid.current.rows = Math.floor(canvas.height / charHeight)

    if (context.current) {
      context.current.font = `${fontSize}px monospace`
      context.current.textBaseline = "top"

      const totalChars = grid.current.columns * grid.current.rows
      let text = ""
      for (let i = 0; i < totalChars; i++) {
        text += String.fromCharCode(33 + Math.floor(Math.random() * 94))
      }

      initLetters(text)
    }
  }, [initLetters])

  const animate = useCallback(() => {
    draw()
    glitch()
    animationRef.current = requestAnimationFrame(animate)
  }, [draw, glitch])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    context.current = canvas.getContext("2d")
    resizeCanvas()
    animate()

    let resizeTimeout: NodeJS.Timeout

    const handleResize = () => {
      clearTimeout(resizeTimeout)
      resizeTimeout = setTimeout(() => {
        cancelAnimationFrame(animationRef.current as number)
        resizeCanvas()
        animate()
      }, 500)
    }

    window.addEventListener("resize", handleResize)

    return () => {
      cancelAnimationFrame(animationRef.current!)
      window.removeEventListener("resize", handleResize)
    }
  }, [animate, resizeCanvas])

  return (
    <div className="relative w-full h-full bg-black overflow-hidden">
      <canvas ref={canvasRef} className="block w-full h-full" />
      {outerVignette && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none bg-[radial-gradient(circle,_rgba(0,0,0,0)_60%,_rgba(0,0,0,1)_100%)]"></div>
      )}
      {centerVignette && (
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none bg-[radial-gradient(circle,_rgba(0,0,0,0.8)_0%,_rgba(0,0,0,0)_60%)]"></div>
      )}
    </div>
  )
}

export default LetterGlitch

