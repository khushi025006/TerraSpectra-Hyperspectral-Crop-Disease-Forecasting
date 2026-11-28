import { useState, useEffect } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import {
  LayoutDashboard, ScanEye, Image, Activity, Leaf,
  Microscope, TrendingUp, FileText, Bell, Search,
  ChevronDown, ChevronLeft, ChevronRight, Menu,
  Sprout, Database, CalendarDays, Download,
  ArrowUpRight, CircleCheck, Clock3, AlertCircle,
  FlaskConical, X,
} from 'lucide-react'

import './App.css'

const navigation = [
  {
    title: 'COMMAND',
    items: [{ label: 'Dashboard Overview', icon: LayoutDashboard }],
  },
  {
    title: 'IMAGING LAB',
    items: [
      { label: 'Hyperspectral Analysis', icon: ScanEye },
      { label: 'RGB Image Analysis', icon: Image },
      { label: 'Symptom Analysis', icon: Microscope },
    ],
  },
  {
    title: 'FIELD INTELLIGENCE',
    items: [
      { label: 'Plant Monitoring', icon: Leaf },
      { label: 'Capture Conditions', icon: Activity },
      { label: 'Disease Forecasting', icon: TrendingUp },
    ],
  },
  {
    title: 'OUTPUT',
    items: [{ label: 'Reports', icon: FileText }],
  },
]

const metrics = [
  {
    label: 'MONITORED PLANTS',
    value: '11',
    description: 'Across 3 plant groups',
    icon: Sprout,
    color: '#10B981',
    background: '#ECFDF5',
  },
  {
    label: 'IMAGES CAPTURED',
    value: '247',
    description: 'Trial 4 dataset records',
    icon: Image,
    color: '#6366F1',
    background: '#EEF2FF',
  },
  {
    label: 'PLANT-DAY RECORDS',
    value: '71',
    description: 'Temporal observations',
    icon: CalendarDays,
    color: '#0891B2',
    background: '#ECFEFF',
  },
  {
    label: 'LEAF-PART RECORDS',
    value: '245',
    description: 'Daily aggregated records',
    icon: Database,
    color: '#D97706',
    background: '#FFFBEB',
  },
]

function Sidebar({ activePage, setActivePage, collapsed, setCollapsed }) {
  return (
    <aside className={`sidebar ${collapsed ? 'sidebar-collapsed' : ''}`}>
            <div className="brand">
        <div className="brand-icon">
          <Sprout size={25} />
        </div>

        {!collapsed && (
          <div>
            <h2>TerraSpectra</h2>
            <span>AI INTELLIGENCE</span>
          </div>
        )}

        <button
          className="collapse-button"
          onClick={() => setCollapsed(!collapsed)}
        >
          {collapsed ? <ChevronRight size={17} /> : <ChevronLeft size={17} />}
        </button>
      </div>
      <div className="sidebar-content">
        {navigation.map((group) => (
          <div className="nav-group" key={group.title}>
            {!collapsed && <p className="nav-heading">{group.title}</p>}

            {group.items.map((item) => {
              const Icon = item.icon
              const active = activePage === item.label

              return (
                <button
                  key={item.label}
                  title={collapsed ? item.label : ''}
                  className={`nav-item ${active ? 'nav-active' : ''}`}
                  onClick={() => setActivePage(item.label)}
                >
                  <Icon size={19} />
                  {!collapsed && <span>{item.label}</span>}
                  {active && !collapsed && <span className="active-indicator" />}
                </button>
              )
            })}
          </div>
        ))}
      </div>

      {!collapsed && (
        <div className="sidebar-footer">
          <div className="footer-icon"><FlaskConical size={19} /></div>
          <div>
            <strong>Research Workspace</strong>
            <span>TerraSpectra v1.0</span>
          </div>
        </div>
      )}
    </aside>
  )
}

function Header({ activePage, onMenu }) {
  return (
    <header className="topbar">
      <button className="mobile-menu" onClick={onMenu}>
        <Menu size={21} />
      </button>

      <div className="breadcrumb">
        <span>Workspace</span>
        <ChevronRight size={15} />
        <strong>{activePage}</strong>
      </div>

      <div className="topbar-actions">
        <label className="search-box">
          <Search size={17} />
          <input placeholder="Search plants, images..." />
          <kbd>⌘ K</kbd>
        </label>

        <button className="icon-button" aria-label="Notifications">
          <Bell size={19} />
          <span className="notification-dot" />
        </button>

        <div className="profile">
          <div className="avatar">TS</div>
          <div className="profile-info">
            <strong>Researcher</strong>
            <span>Administrator</span>
          </div>
          <ChevronDown size={15} />
        </div>
      </div>
    </header>
  )
}

function FilterBar() {
  return (
    <div className="filter-bar">
      <div className="filter-item">
        <span className="filter-label">DATASET</span>
        <button className="filter-select">
          <Database size={15} />
          Trial 4 Dataset
          <ChevronDown size={14} />
        </button>
      </div>

      <div className="filter-divider" />

      <div className="filter-item">
        <span className="filter-label">DATE RANGE</span>
        <button className="filter-select">
          <CalendarDays size={15} />
          All observation dates
          <ChevronDown size={14} />
        </button>
      </div>

      <div className="filter-divider" />

      <div className="filter-item">
        <span className="filter-label">PLANT GROUP</span>
        <button className="filter-select">
          All Groups
          <ChevronDown size={14} />
        </button>
      </div>

      <button className="export-button" onClick={() => window.print()}>
        <Download size={16} />
        Export Snapshot
      </button>
    </div>
  )
}

function MetricCard({ metric }) {
  const Icon = metric.icon

  return (
    <article className="metric-card">
      <div className="metric-top">
        <span>{metric.label}</span>
        <div
          className="metric-icon"
          style={{ color: metric.color, background: metric.background }}
        >
          <Icon size={20} />
        </div>
      </div>

      <div className="metric-value">{metric.value}</div>
      <div className="metric-description">{metric.description}</div>
    </article>
  )
}

function EmptyAnalysis({ icon: Icon, title, description }) {
  return (
    <div className="empty-analysis">
      <div className="empty-icon">
        <Icon size={25} />
      </div>
      <strong>{title}</strong>
      <p>{description}</p>
      <span className="data-status">
        <Clock3 size={13} /> Awaiting data integration
      </span>
    </div>
  )
}


function PlantGroupChart({ data }) {
  return (
    <div style={{ width: '100%', height: 230, marginTop: 20 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
         data={data}
          layout="vertical"
          margin={{ top: 5, right: 25, left: 5, bottom: 5 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            horizontal={false}
            stroke="#E2E8F0"
          />

          <XAxis
            type="number"
            allowDecimals={false}
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#94A3B8', fontSize: 10 }}
          />

          <YAxis
            type="category"
            dataKey="group"
            width={85}
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#475569', fontSize: 10 }}
          />

          <Tooltip
            formatter={(value) => [`${value} images`, 'Records']}
            contentStyle={{
              borderRadius: '8px',
              border: '1px solid #E2E8F0',
              fontSize: '11px',
            }}
          />

          <Bar
            dataKey="images"
            fill="#10B981"
            radius={[0, 6, 6, 0]}
            barSize={24}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function DatasetValidationSummary({ validation }) {
  const validationItems = [
    {
      label: 'Total observation sequences',
      value: validation.total_sequences,
      icon: Database,
      color: '#6366F1',
      background: '#EEF2FF',
    },
    {
      label: 'Image-count checks passed',
      value: `${validation.image_count_matches} / ${validation.total_sequences}`,
      icon: CircleCheck,
      color: '#059669',
      background: '#ECFDF5',
    },
    {
      label: 'Date-count checks passed',
      value: `${validation.date_count_matches} / ${validation.total_sequences}`,
      icon: CircleCheck,
      color: '#059669',
      background: '#ECFDF5',
    },
    {
      label: 'Repeated captures',
      value: validation.repeated_captures,
      icon: Clock3,
      color: '#D97706',
      background: '#FFFBEB',
    },
  ]

  return (
    <section className="dashboard-card validation-card">
      <div className="card-heading">
        <div>
          <div className="card-title">Dataset Validation Summary</div>
          <div className="card-subtitle">
            Quality checks across {validation.total_sequences} observation sequences
          </div>
        </div>

        <CircleCheck size={20} className="heading-icon" />
      </div>

      <div className="validation-grid">
        {validationItems.map((item) => {
          const Icon = item.icon

          return (
            <div className="validation-item" key={item.label}>
              <div
                className="validation-icon"
                style={{
                  color: item.color,
                  background: item.background,
                }}
              >
                <Icon size={19} />
              </div>

              <div>
                <div className="validation-value">{item.value}</div>
                <div className="validation-label">{item.label}</div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="validation-note">
        <AlertCircle size={15} />
        <span>
          {validation.image_count_mismatches} image-count mismatches and{' '}
          {validation.date_count_mismatches} date-count mismatches were found.
          {' '}{validation.repeated_captures} repeated captures were recorded during the audit.
        </span>
      </div>
    </section>
  )
}

function DashboardOverview({ dashboardData }) {

  const dynamicMetrics = [
    {
      ...metrics[0],
      value: dashboardData.dataset.monitored_plants,
      description: `Across ${dashboardData.dataset.plant_groups} plant groups`,
    },
    {
      ...metrics[1],
      value: dashboardData.dataset.total_images,
      description: `${dashboardData.dataset.name} records`,
    },
    {
      ...metrics[2],
      value: dashboardData.dataset.plant_day_records,
      description: 'Temporal observations',
    },
    {
      ...metrics[3],
      value: dashboardData.dataset.leaf_part_records,
      description: 'Daily aggregated records',
    },
  ]

  return (
    <>
      <section className="welcome-section">
        <div>
          <div className="eyebrow">
            <span className="status-dot" />
            AGRICULTURAL INTELLIGENCE PLATFORM
          </div>

          <h1>Dashboard Overview</h1>

          <p>
            Monitor crop health, explore spectral patterns and understand
            temporal plant behaviour.
          </p>
        </div>

        <div className="date-badge">
          <CalendarDays size={16} />
          Trial 4 · April – August 2025
        </div>
      </section>

      <section className="metrics-grid">
  {dynamicMetrics.map((metric) => (
    <MetricCard metric={metric} key={metric.label} />
  ))}
</section>

      <DatasetValidationSummary validation={dashboardData.validation} />

      <section className="analysis-grid">
        <article className="dashboard-card main-analysis">
          <div className="card-heading">
            <div>
              <div className="card-title">Plant Health Trajectory</div>
              <div className="card-subtitle">
                Temporal monitoring across plant groups
              </div>
            </div>

            <button className="more-button">
              View analysis <ArrowUpRight size={15} />
            </button>
          </div>

          <EmptyAnalysis
            icon={Activity}
            title="Temporal visualization"
            description="Plant-level daily summaries are available. The actual trend chart will be connected to project CSV data."
          />
        </article>

        <article className="dashboard-card severity-card">
          <div className="card-heading">
            <div>
              <div className="card-title">Plant Group Distribution</div>
              <div className="card-subtitle">Dataset composition</div>
            </div>
          </div>

         <PlantGroupChart data={dashboardData.plant_group_distribution} />
          <div className="group-total">
            <span>Total image records</span>
            <strong>{dashboardData?.dataset?.total_images || 247}</strong>
          </div>

          <div className="notice-box">
            <AlertCircle size={16} />
            <span>
              Group distribution represents dataset records, not disease severity.
            </span>
          </div>
        </article>
      </section>

      <section className="analysis-grid lower-grid">
        <article className="dashboard-card">
          <div className="card-heading">
            <div>
              <div className="card-title">Hyperspectral Intelligence</div>
              <div className="card-subtitle">Spectral signature exploration</div>
            </div>
            <ScanEye size={20} className="heading-icon" />
          </div>

          <EmptyAnalysis
            icon={ScanEye}
            title="Spectral analysis workspace"
            description="Explore 204-band hyperspectral cubes, spectral signatures and variable wavelength regions."
          />
        </article>

        <article className="dashboard-card">
          <div className="card-heading">
            <div>
              <div className="card-title">Recent Capture Sessions</div>
              <div className="card-subtitle">Dataset observation overview</div>
            </div>
          </div>

          <div className="capture-list">
            <div className="capture-row">
              <div className="capture-icon"><Image size={17} /></div>
              <div className="capture-info">
                <strong>Hyperspectral dataset</strong>
               <span>{dashboardData.dataset.total_images} metadata records</span>
              </div>
              <span className="capture-status validated">
                <CircleCheck size={13} /> Audited
              </span>
            </div>

            <div className="capture-row">
              <div className="capture-icon purple"><Activity size={17} /></div>
              <div className="capture-info">
                <strong>Plant-level analysis</strong>
               <span>{dashboardData.dataset.plant_day_records} daily records</span>
              </div>
              <span className="capture-status validated">
                <CircleCheck size={13} /> Complete
              </span>
            </div>

            <div className="capture-row">
              <div className="capture-icon amber"><FlaskConical size={17} /></div>
              <div className="capture-info">
                <strong>Symptom forecasting</strong>
                <span>Model validation pending</span>
              </div>
              <span className="capture-status pending">
                <Clock3 size={13} /> Pending
              </span>
            </div>
          </div>
        </article>
      </section>

      <footer className="dashboard-footer">
        <span>TerraSpectra AI · Agricultural Intelligence</span>
        <span>Research dataset · Trial 4</span>
      </footer>
    </>
  )
}
function App() {
  const [activePage, setActivePage] = useState('Dashboard Overview')
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  const [dashboardData, setDashboardData] = useState(null)
  const [dataError, setDataError] = useState('')

  useEffect(() => {
    fetch('/data/dashboard_summary.json')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Unable to load dashboard data.')
        }

        return response.json()
      })
      .then((data) => {
        setDashboardData(data)
        console.log('TerraSpectra dashboard data loaded:', data)
      })
      .catch((error) => {
        setDataError(error.message)
        console.error('Dashboard data error:', error)
      })
  }, [])
  return (
    <div className="app-layout">
      <div
        className={`mobile-overlay ${mobileOpen ? 'show' : ''}`}
        onClick={() => setMobileOpen(false)}
      />

      <div className={`sidebar-wrapper ${mobileOpen ? 'mobile-open' : ''}`}>
        <Sidebar
          activePage={activePage}
          setActivePage={(page) => {
            setActivePage(page)
            setMobileOpen(false)
          }}
          collapsed={collapsed}
          setCollapsed={setCollapsed}
        />

        <button className="mobile-close" onClick={() => setMobileOpen(false)}>
          <X size={20} />
        </button>
      </div>

      <main className="main-area">
        <Header
          activePage={activePage}
          onMenu={() => setMobileOpen(true)}
        />

        <div className="page-content">
          <FilterBar />
{activePage === 'Dashboard Overview' ? (
  !dashboardData ? (
    <section className="dashboard-card" style={{ padding: '30px', textAlign: 'center' }}>
      {dataError ? (
        <>
          <AlertCircle size={28} color="#DC2626" />
          <h3>Dashboard Data Error</h3>
          <p>{dataError}</p>
        </>
      ) : (
        <>
          <Clock3 size={28} color="#0891B2" />
          <h3>Loading TerraSpectra Data...</h3>
          <p>Please wait while dashboard statistics are loaded.</p>
        </>
      )}
    </section>
  ) : (
    <DashboardOverview dashboardData={dashboardData} />
  )
) : (
            <section className="coming-soon dashboard-card">
              <div className="empty-icon"><Sprout size={27} /></div>
              <h2>{activePage}</h2>
              <p>
                This workspace will be implemented and connected to
                the corresponding TerraSpectra research data.
              </p>
              <button onClick={() => setActivePage('Dashboard Overview')}>
                Return to Dashboard
              </button>
            </section>
          )}
        </div>
      </main>
    </div>
  )
}

export default App