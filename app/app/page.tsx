"use client"

import type React from "react"

import { useState, useEffect } from "react"
import LetterGlitch from "./components/LetterGlitch"
import LoadingSpinner from "./components/LoadingSpinner"
import Modal from "./components/Modal"
import JobListings from "./components/JobListings"

export default function Home() {
  const [inputText, setInputText] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [jobListings, setJobListings] = useState<any[]>([])
  const [isDarkMode, setIsDarkMode] = useState(false)

  useEffect(() => {
    const darkModeMediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
    setIsDarkMode(darkModeMediaQuery.matches)

    const handleChange = (e: MediaQueryListEvent) => setIsDarkMode(e.matches)
    darkModeMediaQuery.addEventListener("change", handleChange)

    return () => darkModeMediaQuery.removeEventListener("change", handleChange)
  }, [])

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!inputText.trim()) return

    setIsLoading(true)

    // Simulate an API call
    await new Promise((resolve) => setTimeout(resolve, 2000))

    const hackathonInfo = {
      title: "1-1-1 Hackathon",
      subtitle: "One Person, One Product, One Day",
      date: "February 24, 2024",
      time: "10:00 - 19:00",
      description:
        "Join our unique hackathon where individuals create complete products in just one day. Challenge yourself to build something amazing!",
    }

    setJobListings([hackathonInfo])
    setInputText("")
    setIsLoading(false)
    setShowModal(true)
  }

  return (
    <main className={`relative w-screen h-screen overflow-hidden ${isDarkMode ? "dark" : ""}`}>
      <LetterGlitch
        glitchColors={isDarkMode ? ["#1F2937", "#374151", "#4B5563"] : ["#2b4539", "#61dca3", "#61b3dc"]}
        glitchSpeed={50}
        centerVignette={false}
        outerVignette={true}
        smooth={true}
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <form onSubmit={handleSubmit} className="w-full max-w-lg">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="largeInput text-6xl font-bold text-white bg-transparent border-none outline-none text-center w-full"
            placeholder="Search events..."
          />
        </form>
      </div>
      {isLoading && <LoadingSpinner />}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)}>
        <JobListings jobs={jobListings} isDarkMode={isDarkMode} />
      </Modal>
    </main>
  )
}

