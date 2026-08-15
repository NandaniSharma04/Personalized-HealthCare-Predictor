import React from 'react'

export default function LoadingButton({ children, loading, ...props }) {
  return (
    <button disabled={loading} {...props}>
      {loading ? 'Saving...' : children}
    </button>
  )
}
