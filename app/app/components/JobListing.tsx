import type React from "react"
import { Calendar, Clock, User } from "lucide-react"

interface JobListingProps {
  job: {
    title: string
    subtitle: string
    date: string
    time: string
    description: string
  }
  isDarkMode: boolean
}

const JobListing: React.FC<JobListingProps> = ({ job, isDarkMode }) => {
  return (
    <div
      className={`${isDarkMode ? "bg-gray-800 text-white" : "bg-white text-gray-800"} p-4 rounded-lg shadow-lg transition-colors duration-200 flex-shrink-0 w-[280px]`}
    >
      <div className="w-full h-32 mb-3 rounded-md overflow-hidden">
        <img
          src="https://sjc.microlink.io/fAMl9PRNQRAg6f0sPmh3rcvS0VMVrDmcxypE-dQpPH_ysFSNzJs-S11Y_bn_TDJkN9aJoc824bnJ5EFCgXXbcQ.jpeg"
          alt="1-1-1 Hackathon"
          className="w-full h-full object-cover"
        />
      </div>
      <h2 className="text-lg font-bold mb-2">{job.title}</h2>
      <p className={`${isDarkMode ? "text-blue-400" : "text-blue-600"} text-sm mb-3`}>{job.subtitle}</p>
      <div className={`flex items-center ${isDarkMode ? "text-gray-300" : "text-gray-600"} text-sm mb-1`}>
        <Calendar className="w-3 h-3 mr-1" />
        <span>{job.date}</span>
      </div>
      <div className={`flex items-center ${isDarkMode ? "text-gray-300" : "text-gray-600"} text-sm mb-1`}>
        <Clock className="w-3 h-3 mr-1" />
        <span>{job.time}</span>
      </div>
      <div className={`flex items-center ${isDarkMode ? "text-gray-300" : "text-gray-600"} text-sm mb-2`}>
        <User className="w-3 h-3 mr-1" />
        <span>One Person</span>
      </div>
      <p className={`${isDarkMode ? "text-gray-400" : "text-gray-700"} text-sm mb-4 line-clamp-2`}>{job.description}</p>
      <button
        className={`w-full ${isDarkMode ? "bg-blue-600 hover:bg-blue-700" : "bg-blue-500 hover:bg-blue-600"} text-white px-3 py-1.5 rounded text-sm transition-colors`}
      >
        Join Hackathon
      </button>
    </div>
  )
}

export default JobListing

