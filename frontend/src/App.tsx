// src/App.tsx
// Root component: router, layout shell, and page routes.

import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'
import { Home } from '@/pages/Home'
import { HowItWorks } from '@/pages/HowItWorks'
import { Emotions } from '@/pages/Emotions'

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">
        <Header />
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/how-it-works" element={<HowItWorks />} />
            <Route path="/emotions" element={<Emotions />} />
          </Routes>
        </div>
        <Footer />
      </div>
    </BrowserRouter>
  )
}
