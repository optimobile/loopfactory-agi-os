import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import './App.css'
import { Button } from './components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './components/ui/card'
import { Input } from './components/ui/input'
import { Badge } from './components/ui/badge'
import { Search, Sparkles, Zap, TrendingUp, Star, ArrowRight } from 'lucide-react'

// API Base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Header />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/companies" element={<CompaniesPage />} />
        </Routes>
        <Footer />
      </div>
    </Router>
  )
}

function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        <Link to="/" className="flex items-center space-x-2">
          <Sparkles className="h-6 w-6 text-primary" />
          <span className="font-bold text-xl">Loop Factory AI</span>
        </Link>
        <nav className="ml-auto flex gap-6">
          <Link to="/agents" className="text-sm font-medium transition-colors hover:text-primary">
            Agents
          </Link>
          <Link to="/companies" className="text-sm font-medium transition-colors hover:text-primary">
            Companies
          </Link>
          <Button size="sm">Get Started</Button>
        </nav>
      </div>
    </header>
  )
}

function HomePage() {
  const [stats, setStats] = useState({ agents: 0, companies: 0, users: 0 })
  const [featuredAgents, setFeaturedAgents] = useState([])

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/stats`)
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error('Error fetching stats:', err))

    fetch(`${API_BASE_URL}/api/agents?featured=true&limit=6`)
      .then(res => res.json())
      .then(data => setFeaturedAgents(data))
      .catch(err => console.error('Error fetching featured agents:', err))
  }, [])

  return (
    <main>
      <section className="container py-24 space-y-8">
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <Badge className="mb-4" variant="secondary">
            <Sparkles className="h-3 w-3 mr-1" />
            Powered by AI
          </Badge>
          <h1 className="text-5xl font-bold tracking-tight sm:text-6xl">
            AI Agents for Every Industry
          </h1>
          <p className="text-xl text-muted-foreground">
            Discover, deploy, and automate with specialized AI agents across 11 industry-leading platforms.
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" className="gap-2" asChild>
              <Link to="/agents">
                Browse Agents
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link to="/companies">View Companies</Link>
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto pt-12">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-4xl font-bold">{stats.agents}+</CardTitle>
              <CardDescription>AI Agents</CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-4xl font-bold">{stats.companies}</CardTitle>
              <CardDescription>Industry Companies</CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-4xl font-bold">{stats.users}+</CardTitle>
              <CardDescription>Active Users</CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      <section className="container py-16 space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-bold">Featured AI Agents</h2>
          <p className="text-muted-foreground">Handpicked agents to supercharge your workflow</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featuredAgents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      </section>

      <section className="container py-16 space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card>
            <CardHeader>
              <Zap className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Instant Deployment</CardTitle>
              <CardDescription>Deploy AI agents in seconds. No coding required.</CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <TrendingUp className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Industry Specialized</CardTitle>
              <CardDescription>11 companies serving specific industries with tailored solutions.</CardDescription>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader>
              <Star className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Proven Results</CardTitle>
              <CardDescription>Join thousands of users automating their workflows.</CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>
    </main>
  )
}

function AgentsPage() {
  const [agents, setAgents] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    const url = searchQuery 
      ? `${API_BASE_URL}/api/search?q=${encodeURIComponent(searchQuery)}`
      : `${API_BASE_URL}/api/agents?limit=50`
    
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setAgents(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching agents:', err)
        setLoading(false)
      })
  }, [searchQuery])

  return (
    <main className="container py-12 space-y-8">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold">AI Agents Marketplace</h1>
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search agents..."
            className="pl-10"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Loading agents...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      )}
    </main>
  )
}

function CompaniesPage() {
  const [companies, setCompanies] = useState([])

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/companies`)
      .then(res => res.json())
      .then(data => setCompanies(data))
      .catch(err => console.error('Error fetching companies:', err))
  }, [])

  return (
    <main className="container py-12 space-y-8">
      <div className="space-y-4">
        <h1 className="text-4xl font-bold">Our Companies</h1>
        <p className="text-xl text-muted-foreground">11 specialized companies serving different industries</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {companies.map((company) => (
          <Card key={company.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle>{company.name}</CardTitle>
              <CardDescription>{company.industry}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{company.description}</p>
            </CardContent>
            <CardFooter>
              <Button variant="outline" className="w-full" asChild>
                <a href={`https://${company.domain}`} target="_blank" rel="noopener noreferrer">
                  Visit {company.domain}
                </a>
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </main>
  )
}

function AgentCard({ agent }) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle>{agent.name}</CardTitle>
            <CardDescription>{agent.category}</CardDescription>
          </div>
          {agent.is_featured && (
            <Badge variant="secondary">
              <Star className="h-3 w-3 mr-1" />
              Featured
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground line-clamp-3">
          {agent.description || 'No description available'}
        </p>
        <div className="flex items-center gap-2 mt-4">
          <div className="flex items-center">
            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
            <span className="text-sm ml-1">{agent.rating_average.toFixed(1)}</span>
          </div>
          <span className="text-sm text-muted-foreground">({agent.rating_count} reviews)</span>
        </div>
      </CardContent>
      <CardFooter className="flex justify-between items-center">
        <div className="text-2xl font-bold">
          ${agent.price_usd}
          <span className="text-sm font-normal text-muted-foreground">/mo</span>
        </div>
        <Button>Get Started</Button>
      </CardFooter>
    </Card>
  )
}

function Footer() {
  return (
    <footer className="border-t py-12 mt-24">
      <div className="container">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <span className="font-bold">Loop Factory AI</span>
            </div>
            <p className="text-sm text-muted-foreground">
              AI Agent Marketplace powering 11 industry-specific companies
            </p>
          </div>
          <div>
            <h3 className="font-semibold mb-3">Product</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link to="/agents" className="hover:text-foreground">Browse Agents</Link></li>
              <li><Link to="/companies" className="hover:text-foreground">Companies</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-3">Company</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-foreground">About</a></li>
              <li><a href="#" className="hover:text-foreground">Blog</a></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-3">Legal</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-foreground">Privacy</a></li>
              <li><a href="#" className="hover:text-foreground">Terms</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t mt-8 pt-8 text-center text-sm text-muted-foreground">
          © 2025 Loop Factory AI. All rights reserved.
        </div>
      </div>
    </footer>
  )
}

export default App

