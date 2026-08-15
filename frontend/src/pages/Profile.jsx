import React, { useEffect, useState } from 'react'
import { getProfile, updateProfile } from '../services/userService'
import LoadingButton from '../components/LoadingButton'
import ConfirmModal from '../components/ConfirmModal'

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const token = localStorage.getItem('access_token')

  useEffect(() => {
    let mounted = true
    if (!token) return
    setLoading(true)
    getProfile(token)
      .then(d => { if (mounted) setProfile(d) })
      .catch(e => setError(e))
      .finally(() => setLoading(false))
    return () => { mounted = false }
  }, [])

  const handleSave = async () => {
    setLoading(true)
    try {
      const updated = await updateProfile(token, profile)
      setProfile(updated)
      // success state: could be a toast
      alert('Profile saved')
    } catch (e) {
      alert('Error saving')
    } finally {
      setLoading(false)
    }
  }

  const handleSensitiveChange = () => {
    setConfirmOpen(true)
  }

  const confirmProceed = () => {
    setConfirmOpen(false)
    handleSave()
  }

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error loading profile</div>
  if (!profile) return <div>No profile</div>

  return (
    <div className="profile-page">
      <h2>Profile</h2>
      <div className="form-row">
        <label>First name</label>
        <input value={profile.first_name || ''} onChange={e => setProfile({ ...profile, first_name: e.target.value })} />
      </div>
      <div className="form-row">
        <label>Last name</label>
        <input value={profile.last_name || ''} onChange={e => setProfile({ ...profile, last_name: e.target.value })} />
      </div>
      <div className="form-row">
        <label>Phone</label>
        <input value={profile.phone || ''} onChange={e => setProfile({ ...profile, phone: e.target.value })} />
      </div>
      <div className="form-actions">
        <LoadingButton loading={loading} onClick={handleSave}>Save</LoadingButton>
        <button onClick={handleSensitiveChange}>Save sensitive changes</button>
      </div>

      {confirmOpen && (
        <ConfirmModal title="Confirm sensitive update" message="Are you sure you want to update sensitive profile fields?" onConfirm={confirmProceed} onCancel={() => setConfirmOpen(false)} />
      )}
    </div>
  )
}
