import React, { ReactNode } from 'react'
import Head from 'next/head'
import Link from 'next/link'

type LayoutProps = {
  children: ReactNode
  title?: string
}

const Layout = ({ children, title = 'Resume AI Generator' }: LayoutProps) => {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content="Generate professional resumes with AI" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className="min-h-screen flex flex-col">
        <header className="bg-blue-600 text-white">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-xl font-bold">Resume AI Generator</h1>
            <nav>
              <ul className="flex space-x-4">
                <li><Link href="/" className="hover:underline">Home</Link></li>
                <li><Link href="/templates" className="hover:underline">Templates</Link></li>
                <li><Link href="/about" className="hover:underline">About</Link></li>
              </ul>
            </nav>
          </div>
        </header>
        <main className="flex-grow">
          {children}
        </main>
        <footer className="bg-gray-100 py-6">
          <div className="container mx-auto px-4 text-center text-gray-600">
            <p>© {new Date().getFullYear()} Resume AI Generator. All rights reserved.</p>
          </div>
        </footer>
      </div>
    </>
  )
}

export default Layout