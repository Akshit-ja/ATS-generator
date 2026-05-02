import Link from 'next/link'

export default function TestPage() {
  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <h1>Test Page - Working!</h1>
      <div style={{ marginTop: '30px' }}>
        <Link href="/register" style={{ 
          display: 'inline-block',
          padding: '15px 30px',
          backgroundColor: '#3b82f6',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '8px',
          margin: '10px'
        }}>
          Go to Register
        </Link>
        <Link href="/login" style={{ 
          display: 'inline-block',
          padding: '15px 30px',
          backgroundColor: '#6b7280',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '8px',
          margin: '10px'
        }}>
          Go to Login
        </Link>
      </div>
    </div>
  )
}