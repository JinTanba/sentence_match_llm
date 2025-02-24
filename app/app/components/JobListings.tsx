import type React from "react"
import JobListing from "./JobListing"

interface JobListingsProps {
  jobs: {
    title: string
    subtitle: string
    date: string
    time: string
    description: string
  }[]
  isDarkMode: boolean
}

const JobListings: React.FC<JobListingsProps> = ({ jobs, isDarkMode }) => {
  return (
    <div className="w-full overflow-x-auto">
      <div className="flex space-x-6 pb-4">
        {jobs.map((job, index) => (
          <JobListing key={index} job={job} isDarkMode={isDarkMode} />
        ))}
      </div>
    </div>
  )
}

export default JobListings

