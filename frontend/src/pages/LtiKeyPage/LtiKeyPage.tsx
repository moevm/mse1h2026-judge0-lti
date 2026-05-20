import { useEffect, useState } from 'react'
import api from '../../lib/api'

export default function LtiKeyPage() {
  const [key, setKey] = useState('')

  useEffect(() => {
    api.get('/lti/public-key').then(r => setKey(r.data))
  }, [])

  return (
    <div style={{ padding: 40 }}>
      <h2>Публичный ключ для Moodle</h2>
      <p>Скопируйте и вставьте в настройки LTI инструмента:</p>
      <textarea
        rows={10}
        cols={70}
        value={key}
        readOnly
        onClick={e => (e.target as HTMLTextAreaElement).select()}
      />
    </div>
  )
}