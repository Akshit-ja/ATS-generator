import Link from 'next/link'
import Layout from '../components/Layout'

export default function Home() {

  return (
    <Layout>
      <div className="container mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-center text-blue-600 mb-8">
          Resume AI Generator
        </h1>
        <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-md p-8">
          <p className="text-lg text-gray-700 mb-6">
            Create professional resumes tailored to your target job with the help of AI.
            Simply provide your information and let our system generate a polished resume.
          </p>
          <div className="flex flex-col gap-4">
            <Link
              href="/register"
              className="inline-block w-full py-4 px-6 bg-blue-500 text-white font-bold rounded-lg hover:bg-blue-600 transition-all duration-200 text-center transform hover:scale-105"
            >
              🚀 Get Started - Create Account
            </Link>
            <Link
              href="/login"
              className="inline-block w-full py-4 px-6 bg-green-500 text-white font-bold rounded-lg hover:bg-green-600 transition-all duration-200 text-center transform hover:scale-105"
            >
              🔐 Already have an account? Sign In
            </Link>
          </div>
        </div>
      </div>
    </Layout>
  )
}