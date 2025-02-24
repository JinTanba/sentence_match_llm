"use client"

import type { ReactNode } from "react"
import { motion, AnimatePresence } from "framer-motion"

interface ModalProps {
  children: ReactNode
  onClose: () => void
  isOpen: boolean
}

const Modal = ({ children, onClose, isOpen }: ModalProps) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ type: "spring", damping: 15 }}
            className="bg-white dark:bg-gray-800 p-8 rounded-lg w-auto max-w-3xl max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={onClose}
              className="float-right text-gray-500 dark:text-gray-300 hover:text-gray-700 dark:hover:text-gray-100"
            >
              ×
            </button>
            <div className="mt-4 overflow-x-auto">{children}</div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

export default Modal

