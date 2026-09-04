import {
  useState,
  useEffect,
  useCallback,
  useRef,
} from "react";
import "./App.css";

function App() {
  const [page, setPage] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [role, setRole] = useState("Police Officer");

  const [activeSection, setActiveSection] = useState("Dashboard");

  // =========================
  // SESSION TIMEOUT
  // =========================

const SESSION_DURATION = 20;
const WARNING_TIME = 10;

  const [sessionTime, setSessionTime] =
    useState(SESSION_DURATION);

  const [showTimeoutWarning, setShowTimeoutWarning] =
    useState(false);

  const [sessionExpired, setSessionExpired] =
    useState(false);

  const lastActivity = useRef(Date.now());

  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");

  const [selectedDocument, setSelectedDocument] =
    useState(null);

  const [currentPage, setCurrentPage] = useState(1);
  const [zoom, setZoom] = useState(100);
  const [note, setNote] = useState("");

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const [documents, setDocuments] = useState([
    {
      id: 1,
      name: "Case_Report_102.pdf",
      type: "Case Report",
      status: "Verified",
      pages: 5,
      idCode: "SD-2026-102",
      updated: "Today, 10:42 AM",
    },
    {
      id: 2,
      name: "Evidence_Record_45.pdf",
      type: "Evidence",
      status: "Verified",
      pages: 8,
      idCode: "SD-2026-045",
      updated: "Today, 09:18 AM",
    },
    {
      id: 3,
      name: "Investigation_File_21.pdf",
      type: "Investigation",
      status: "Pending",
      pages: 12,
      idCode: "SD-2026-021",
      updated: "Yesterday",
    },
    {
      id: 4,
      name: "Legal_Notice_77.pdf",
      type: "Legal Document",
      status: "Verified",
      pages: 4,
      idCode: "SD-2026-077",
      updated: "Yesterday",
    },
    {
      id: 5,
      name: "Forensic_Report_13.pdf",
      type: "Forensic",
      status: "Pending",
      pages: 9,
      idCode: "SD-2026-013",
      updated: "2 days ago",
    },
  ]);

  const activities = [
    {
      icon: "📄",
      title: "Case_Report_102.pdf opened",
      description: "Document viewed successfully",
      time: "10:42 AM",
    },
    {
      icon: "🔐",
      title: "Security verification completed",
      description: "MFA verification successful",
      time: "10:35 AM",
    },
    {
      icon: "🔎",
      title: "Document search performed",
      description: "Search activity recorded",
      time: "10:21 AM",
    },
    {
      icon: "👤",
      title: "New secure session created",
      description: `${role} authenticated`,
      time: "10:15 AM",
    },
  ];

  const rolePermissions = {
    "Police Officer": [
      "Dashboard",
      "Documents",
      "Search",
      "Upload",
      "Activity",
      "Security",
    ],

    Investigator: [
      "Dashboard",
      "Documents",
      "Search",
      "Upload",
      "Activity",
      "Security",
    ],

    "Legal Officer": [
      "Dashboard",
      "Documents",
      "Search",
      "Activity",
      "Security",
    ],

    Supervisor: [
      "Dashboard",
      "Documents",
      "Search",
      "Activity",
      "Security",
    ],

    Auditor: [
      "Dashboard",
      "Search",
      "Activity",
      "Security",
    ],

    Administrator: [
      "Dashboard",
      "Documents",
      "Search",
      "Upload",
      "Activity",
      "Security",
    ],
  };

  const getRoleDocuments = () => {
    if (
      role === "Administrator" ||
      role === "Supervisor" ||
      role === "Auditor"
    ) {
      return documents;
    }

    if (role === "Police Officer") {
      return documents.filter(
        (doc) =>
          doc.type === "Case Report" ||
          doc.type === "Evidence" ||
          doc.type === "Forensic"
      );
    }

    if (role === "Investigator") {
      return documents.filter(
        (doc) =>
          doc.type === "Investigation" ||
          doc.type === "Evidence" ||
          doc.type === "Forensic"
      );
    }

    if (role === "Legal Officer") {
      return documents.filter(
        (doc) =>
          doc.type === "Legal Document" ||
          doc.type === "Case Report"
      );
    }

    return documents;
  };

  const roleDocuments = getRoleDocuments();

  const filteredDocuments = roleDocuments.filter((doc) => {
    const searchText = search.toLowerCase();

    const matchesSearch =
      doc.name.toLowerCase().includes(searchText) ||
      doc.type.toLowerCase().includes(searchText) ||
      doc.idCode.toLowerCase().includes(searchText);

    const matchesType =
      typeFilter === "All" ||
      doc.type === typeFilter;

    const matchesStatus =
      statusFilter === "All" ||
      doc.status === statusFilter;

    return (
      matchesSearch &&
      matchesType &&
      matchesStatus
    );
  });

  // =========================
  // LOGIN
  // =========================

  const handleLogin = (e) => {
    e.preventDefault();

    if (!username || !password) {
      alert("Please enter username and password.");
      return;
    }

    setPage("mfa");
  };

  // =========================
  // MFA
  // =========================

  const verifyMFA = (e) => {
    e.preventDefault();

    if (otp.length !== 6) {
      alert("Please enter a 6-digit verification code.");
      return;
    }

    lastActivity.current = Date.now();

    setSessionTime(SESSION_DURATION);
    setShowTimeoutWarning(false);
    setSessionExpired(false);

    setPage("dashboard");
    setActiveSection("Dashboard");
  };

  // =========================
  // LOGOUT
  // =========================

  const logout = () => {
    setPage("login");
    setUsername("");
    setPassword("");
    setOtp("");

    setActiveSection("Dashboard");
    setSelectedDocument(null);

    setSessionTime(SESSION_DURATION);
    setShowTimeoutWarning(false);
    setSessionExpired(false);

    lastActivity.current = Date.now();
  };

  // =========================
  // RESET SESSION
  // =========================

  const resetSession = useCallback(() => {
    lastActivity.current = Date.now();

    setSessionTime(SESSION_DURATION);
    setShowTimeoutWarning(false);
    setSessionExpired(false);
  }, []);

  // =========================
  // SESSION TIMER
  // =========================

  useEffect(() => {
    if (
      page !== "dashboard" ||
      sessionExpired
    ) {
      return;
    }

    const timer = setInterval(() => {
      const elapsed = Math.floor(
        (Date.now() - lastActivity.current) / 1000
      );

      const remaining = Math.max(
        0,
        SESSION_DURATION - elapsed
      );

      setSessionTime(remaining);

      if (
        remaining <= WARNING_TIME &&
        remaining > 0
      ) {
        setShowTimeoutWarning(true);
      }

      if (remaining <= 0) {
        clearInterval(timer);

        setSessionExpired(true);
        setShowTimeoutWarning(false);
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [
    page,
    sessionExpired,
    SESSION_DURATION,
  ]);

  // =========================
  // USER ACTIVITY DETECTION
  // =========================

  useEffect(() => {
    if (
      page !== "dashboard" ||
      sessionExpired
    ) {
      return;
    }

    const activityHandler = () => {
      if (!showTimeoutWarning) {
        lastActivity.current = Date.now();
      }
    };

    window.addEventListener(
      "mousemove",
      activityHandler
    );

    window.addEventListener(
      "keydown",
      activityHandler
    );

    window.addEventListener(
      "click",
      activityHandler
    );

    window.addEventListener(
      "touchstart",
      activityHandler
    );

    return () => {
      window.removeEventListener(
        "mousemove",
        activityHandler
      );

      window.removeEventListener(
        "keydown",
        activityHandler
      );

      window.removeEventListener(
        "click",
        activityHandler
      );

      window.removeEventListener(
        "touchstart",
        activityHandler
      );
    };
  }, [
    page,
    sessionExpired,
    showTimeoutWarning,
  ]);

  // =========================
  // FORMAT TIMER
  // =========================

  const formatSessionTime = () => {
    const minutes = Math.floor(
      sessionTime / 60
    );

    const seconds = sessionTime % 60;

    return `${String(minutes).padStart(
      2,
      "0"
    )}:${String(seconds).padStart(2, "0")}`;
  };

  // =========================
  // NAVIGATION
  // =========================

  const navigateTo = (section) => {
    setActiveSection(section);
    setSelectedDocument(null);

    if (page === "dashboard") {
      lastActivity.current = Date.now();
      setSessionTime(SESSION_DURATION);
      setShowTimeoutWarning(false);
    }
  };

  // =========================
  // DOCUMENT VIEWER
  // =========================

  const openDocument = (doc) => {
    setSelectedDocument(doc);
    setCurrentPage(1);
    setZoom(100);
    setNote("");
    setActiveSection("Viewer");

    lastActivity.current = Date.now();
    setSessionTime(SESSION_DURATION);
    setShowTimeoutWarning(false);
  };

  const closeViewer = () => {
    setSelectedDocument(null);
    setActiveSection("Documents");
  };

  // =========================
  // LOGIN PAGE
  // =========================

  if (page === "login") {
    return (
      <div className="login-page">
        <div className="login-background-grid"></div>

        <div className="login-container">
          <div className="login-brand">
            <div className="brand-icon">S</div>

            <div>
              <h2>SecureDocs</h2>
              <span>
                SECURE DOCUMENT PLATFORM
              </span>
            </div>
          </div>

          <div className="login-card">
            <div className="login-heading">
              <span className="eyebrow">
                SECURE ACCESS
              </span>

              <h1>Welcome back</h1>

              <p>
                Sign in to access your secure
                document workspace.
              </p>
            </div>

            <form onSubmit={handleLogin}>
              <div className="form-group">
                <label>Username</label>

                <div className="input-wrapper">
                  <span>👤</span>

                  <input
                    type="text"
                    placeholder="Enter your username"
                    value={username}
                    onChange={(e) =>
                      setUsername(e.target.value)
                    }
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Password</label>

                <div className="input-wrapper">
                  <span>🔒</span>

                  <input
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) =>
                      setPassword(e.target.value)
                    }
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Access Role</label>

                <select
                  value={role}
                  onChange={(e) =>
                    setRole(e.target.value)
                  }
                >
                  <option>
                    Police Officer
                  </option>

                  <option>
                    Investigator
                  </option>

                  <option>
                    Legal Officer
                  </option>

                  <option>
                    Supervisor
                  </option>

                  <option>
                    Auditor
                  </option>

                  <option>
                    Administrator
                  </option>
                </select>
              </div>

              <button
                className="primary-login-button"
                type="submit"
              >
                Sign in securely
                <span>→</span>
              </button>
            </form>

            <div className="login-security">
              <span className="status-dot"></span>
              <span>
                Protected session • MFA enabled
              </span>
            </div>
          </div>

          <div className="login-footer">
            <span>
              🔐 End-to-end protected workspace
            </span>

            <span>
              © 2026 SecureDocs
            </span>
          </div>
        </div>
      </div>
    );
  }

  // =========================
  // MFA PAGE
  // =========================

  if (page === "mfa") {
    return (
      <div className="login-page">
        <div className="login-background-grid"></div>

        <div className="login-container">
          <div className="login-brand">
            <div className="brand-icon">S</div>

            <div>
              <h2>SecureDocs</h2>
              <span>
                SECURE DOCUMENT PLATFORM
              </span>
            </div>
          </div>

          <div className="login-card mfa-card">
            <div className="mfa-icon">🔐</div>

            <div className="login-heading">
              <span className="eyebrow">
                SECOND FACTOR
              </span>

              <h1>
                Verify your identity
              </h1>

              <p>
                Enter the six-digit verification
                code to continue.
              </p>
            </div>

            <form onSubmit={verifyMFA}>
              <div className="form-group">
                <label>
                  Verification code
                </label>

                <input
                  className="otp-input"
                  type="text"
                  maxLength="6"
                  placeholder="000000"
                  value={otp}
                  onChange={(e) =>
                    setOtp(
                      e.target.value.replace(
                        /\D/g,
                        ""
                      )
                    )
                  }
                />
              </div>

              <button
                className="primary-login-button"
                type="submit"
              >
                Verify & continue
                <span>→</span>
              </button>
            </form>

            <div className="login-security">
              <span className="status-dot"></span>

              <span>
                Multi-factor authentication active
              </span>
            </div>
          </div>

          <div className="login-footer">
            <span>
              🔒 Identity verification required
            </span>

            <button
              className="back-login"
              onClick={() => setPage("login")}
            >
              ← Back to login
            </button>
          </div>
        </div>
      </div>
    );
  }

  // =========================
  // MAIN APP
  // =========================

  return (
    <div className="app-shell">

      {/* SESSION WARNING */}

      {showTimeoutWarning &&
        !sessionExpired && (
          <div className="timeout-overlay">
            <div className="timeout-modal">

              <div className="timeout-icon">
                ⏱
              </div>

              <span className="eyebrow">
                SECURITY ALERT
              </span>

              <h2>
                Session about to expire
              </h2>

              <p>
                Your SecureDocs session will
                expire due to inactivity.
              </p>

              <div className="timeout-countdown">
                {formatSessionTime()}
              </div>

              <div className="timeout-actions">

                <button
                  className="stay-signed-button"
                  onClick={resetSession}
                >
                  Stay signed in
                </button>

                <button
                  className="timeout-logout"
                  onClick={logout}
                >
                  Sign out
                </button>

              </div>
            </div>
          </div>
        )}

      {/* SESSION EXPIRED */}

      {sessionExpired && (
        <div className="timeout-overlay">
          <div className="timeout-modal expired-modal">

            <div className="timeout-icon expired">
              🔒
            </div>

            <span className="eyebrow">
              SESSION ENDED
            </span>

            <h2>
              Session expired
            </h2>

            <p>
              Your SecureDocs session ended
              automatically for security reasons.
            </p>

            <button
              className="stay-signed-button"
              onClick={() => {
                setSessionExpired(false);
                setSessionTime(
                  SESSION_DURATION
                );
                setShowTimeoutWarning(false);

                setPage("login");
                setUsername("");
                setPassword("");
                setOtp("");
              }}
            >
              Return to secure login →
            </button>

          </div>
        </div>
      )}

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="sidebar-brand">

          <div className="brand-icon small">
            S
          </div>

          <div>
            <h2>SecureDocs</h2>

            <span>
              SECURE PLATFORM
            </span>
          </div>

        </div>

        <div className="sidebar-user">

          <div className="avatar">
            {username
              .charAt(0)
              .toUpperCase() || "U"}
          </div>

          <div className="user-details">

            <strong>
              {username}
            </strong>

            <span>
              {role}
            </span>

          </div>

          <span className="online-dot"></span>

        </div>

        <div className="nav-title">
          WORKSPACE
        </div>

        <nav className="sidebar-nav">

          {rolePermissions[role].includes(
            "Dashboard"
          ) && (
            <button
              className={
                activeSection === "Dashboard"
                  ? "nav-active"
                  : ""
              }
              onClick={() =>
                navigateTo("Dashboard")
              }
            >
              <span>⌂</span>
              Dashboard
            </button>
          )}

          {rolePermissions[role].includes(
            "Documents"
          ) && (
            <button
              className={
                activeSection === "Documents"
                  ? "nav-active"
                  : ""
              }
              onClick={() =>
                navigateTo("Documents")
              }
            >
              <span>▣</span>
              Documents
            </button>
          )}

          {rolePermissions[role].includes(
            "Search"
          ) && (
            <button
              className={
                activeSection === "Search"
                  ? "nav-active"
                  : ""
              }
              onClick={() =>
                navigateTo("Search")
              }
            >
              <span>⌕</span>
              Search
            </button>
          )}

          {rolePermissions[role].includes(
            "Upload"
          ) && (
            <button
              className={
                activeSection === "Upload"
                  ? "nav-active"
                  : ""
              }
              onClick={() => {
                navigateTo("Upload");

                setSelectedFile(null);
                setUploadSuccess(false);
                setUploadProgress(0);
              }}
            >
              <span>↑</span>
              Upload
            </button>
          )}

          <div className="nav-title secondary">
            MONITORING
          </div>

          {rolePermissions[role].includes(
            "Activity"
          ) && (
            <button
              className={
                activeSection === "Activity"
                  ? "nav-active"
                  : ""
              }
              onClick={() =>
                navigateTo("Activity")
              }
            >
              <span>◷</span>
              Audit Activity
            </button>
          )}

          {rolePermissions[role].includes(
            "Security"
          ) && (
            <button
              className={
                activeSection === "Security"
                  ? "nav-active"
                  : ""
              }
              onClick={() =>
                navigateTo("Security")
              }
            >
              <span>♢</span>
              Security Center
            </button>
          )}

        </nav>

        <div className="sidebar-bottom">

          <div className="secure-status">

            <span className="status-dot"></span>

            <div>
              <strong>
                System Secure
              </strong>

              <small>
                All services operational
              </small>
            </div>

          </div>

          <button
            className="logout-button"
            onClick={logout}
          >
            <span>↪</span>
            Sign out
          </button>

        </div>

      </aside>

      {/* MAIN CONTENT */}

      <main className="main-content">

        <header className="topbar">

          <div>

            <div className="breadcrumb">
              SecureDocs / {activeSection}
            </div>

            <h1>
              {activeSection === "Viewer"
                ? "Document Viewer"
                : activeSection}
            </h1>

          </div>

          <div className="topbar-right">

            {/* SESSION TIMER */}

            <div
              className={
                sessionTime <= WARNING_TIME
                  ? "secure-session session-warning"
                  : "secure-session"
              }
            >
              <span className="status-dot"></span>

              Session{" "}
              {formatSessionTime()}
            </div>

            <div className="topbar-user">

              <div className="avatar small-avatar">
                {username
                  .charAt(0)
                  .toUpperCase()}
              </div>

              <div>

                <strong>
                  {username}
                </strong>

                <span>
                  {role}
                </span>

              </div>

            </div>

          </div>

        </header>

        {/* DASHBOARD */}

        {activeSection === "Dashboard" && (
          <div className="page-content">

            <div className="welcome-banner">

              <div>

                <span className="eyebrow">
                  SECURE WORKSPACE
                </span>

                <h2>
                  Good to see you, {username}.
                </h2>

                <p>
                  Your secure document workspace
                  is ready. Access is controlled
                  by your assigned role.
                </p>

              </div>

              <div className="welcome-shield">
                ◇
              </div>

            </div>

            <div className="stats-grid">

              <div className="stat-card">

                <div className="stat-top">
                  <span>DOCUMENTS</span>

                  <div className="stat-icon">
                    ▣
                  </div>
                </div>

                <strong>
                  {roleDocuments.length}
                </strong>

                <small>
                  Accessible records
                </small>

              </div>

              <div className="stat-card">

                <div className="stat-top">
                  <span>VERIFIED</span>

                  <div className="stat-icon green">
                    ✓
                  </div>
                </div>

                <strong>
                  {
                    roleDocuments.filter(
                      (doc) =>
                        doc.status ===
                        "Verified"
                    ).length
                  }
                </strong>

                <small>
                  Security verified
                </small>

              </div>

              <div className="stat-card">

                <div className="stat-top">
                  <span>PENDING</span>

                  <div className="stat-icon orange">
                    !
                  </div>
                </div>

                <strong>
                  {
                    roleDocuments.filter(
                      (doc) =>
                        doc.status ===
                        "Pending"
                    ).length
                  }
                </strong>

                <small>
                  Require review
                </small>

              </div>

              <div className="stat-card">

                <div className="stat-top">
                  <span>SECURITY</span>

                  <div className="stat-icon green">
                    ♢
                  </div>
                </div>

                <strong>
                  100%
                </strong>

                <small>
                  Protection status
                </small>

              </div>

            </div>

            <div className="dashboard-grid">

              <div className="panel">

                <div className="panel-header">

                  <div>
                    <span className="eyebrow">
                      ACCESS CONTROL
                    </span>

                    <h2>
                      Role permissions
                    </h2>
                  </div>

                  <span className="verified-badge">
                    ACTIVE
                  </span>

                </div>

                <div className="role-display">

                  <div className="role-icon">
                    ♢
                  </div>

                  <div>

                    <strong>
                      {role}
                    </strong>

                    <p>
                      Access is automatically
                      restricted according to your
                      assigned security role.
                    </p>

                  </div>

                </div>

                <div className="permission-list">

                  {rolePermissions[role].map(
                    (permission) => (
                      <span
                        key={permission}
                      >
                        ✓ {permission}
                      </span>
                    )
                  )}

                </div>

              </div>

              <div className="panel">

                <div className="panel-header">

                  <div>
                    <span className="eyebrow">
                      QUICK ACCESS
                    </span>

                    <h2>
                      Actions
                    </h2>
                  </div>

                </div>

                <div className="action-grid">

                  {rolePermissions[role].includes(
                    "Documents"
                  ) && (
                    <button
                      onClick={() =>
                        navigateTo(
                          "Documents"
                        )
                      }
                    >
                      <span>▣</span>
                      <strong>
                        Documents
                      </strong>
                      <small>
                        Browse repository
                      </small>
                    </button>
                  )}

                  <button
                    onClick={() =>
                      navigateTo("Search")
                    }
                  >
                    <span>⌕</span>

                    <strong>
                      Search
                    </strong>

                    <small>
                      Find records
                    </small>
                  </button>

                  {rolePermissions[role].includes(
                    "Upload"
                  ) && (
                    <button
                      onClick={() =>
                        navigateTo("Upload")
                      }
                    >
                      <span>↑</span>

                      <strong>
                        Upload
                      </strong>

                      <small>
                        Add document
                      </small>
                    </button>
                  )}

                  <button
                    onClick={() =>
                      navigateTo(
                        "Security"
                      )
                    }
                  >
                    <span>♢</span>

                    <strong>
                      Security
                    </strong>

                    <small>
                      View protection
                    </small>
                  </button>

                </div>

              </div>

            </div>

            <div className="panel">

              <div className="panel-header">

                <div>

                  <span className="eyebrow">
                    RECENT EVENTS
                  </span>

                  <h2>
                    Latest activity
                  </h2>

                </div>

                <button
                  className="text-button"
                  onClick={() =>
                    navigateTo(
                      "Activity"
                    )
                  }
                >
                  View audit log →
                </button>

              </div>

              <div className="activity-table">

                {activities
                  .slice(0, 3)
                  .map(
                    (activity, index) => (
                      <div
                        className="activity-row"
                        key={index}
                      >

                        <div className="activity-icon">
                          {activity.icon}
                        </div>

                        <div className="activity-info">

                          <strong>
                            {activity.title}
                          </strong>

                          <span>
                            {activity.description}
                          </span>

                        </div>

                        <small>
                          {activity.time}
                        </small>

                      </div>
                    )
                  )}

              </div>

            </div>

          </div>
        )}

        {/* DOCUMENTS */}

        {activeSection === "Documents" && (
          <div className="page-content">

            <div className="section-intro">

              <div>

                <span className="eyebrow">
                  REPOSITORY
                </span>

                <h2>
                  Document repository
                </h2>

                <p>
                  Secure records accessible to
                  your {role} account.
                </p>

              </div>

              <div className="record-count">
                {roleDocuments.length} records
              </div>

            </div>

            <div className="panel document-panel">

              <div className="document-table-header">

                <span>
                  DOCUMENT
                </span>

                <span>
                  TYPE
                </span>

                <span>
                  STATUS
                </span>

                <span>
                  UPDATED
                </span>

                <span></span>

              </div>

              {roleDocuments.map(
                (doc) => (
                  <div
                    className="document-row"
                    key={doc.id}
                  >

                    <div className="document-name">

                      <div className="file-icon">
                        PDF
                      </div>

                      <div>

                        <strong>
                          {doc.name}
                        </strong>

                        <small>
                          {doc.idCode} •{" "}
                          {doc.pages} pages
                        </small>

                      </div>

                    </div>

                    <span>
                      {doc.type}
                    </span>

                    <span
                      className={
                        doc.status ===
                        "Verified"
                          ? "status verified"
                          : "status pending"
                      }
                    >
                      <i></i>
                      {doc.status}
                    </span>

                    <span className="muted">
                      {doc.updated}
                    </span>

                    <button
                      className="open-button"
                      onClick={() =>
                        openDocument(doc)
                      }
                    >
                      Open →
                    </button>

                  </div>
                )
              )}

              {roleDocuments.length ===
                0 && (
                <div className="empty-state">
                  <h3>
                    No accessible documents
                  </h3>

                  <p>
                    Your role currently has
                    no document records.
                  </p>
                </div>
              )}

            </div>

          </div>
        )}

        {/* SEARCH */}

        {activeSection === "Search" && (
          <div className="page-content">

            <div className="section-intro">

              <div>

                <span className="eyebrow">
                  DISCOVERY
                </span>

                <h2>
                  Search & filtering
                </h2>

                <p>
                  Find secure records using
                  multiple search parameters.
                </p>

              </div>

            </div>

            <div className="panel">

              <div className="search-bar-large">

                <span>⌕</span>

                <input
                  type="text"
                  placeholder="Search by document name, type or SecureDocs ID..."
                  value={search}
                  onChange={(e) =>
                    setSearch(
                      e.target.value
                    )
                  }
                />

              </div>

              <div className="filter-row">

                <div>

                  <label>
                    Document type
                  </label>

                  <select
                    value={typeFilter}
                    onChange={(e) =>
                      setTypeFilter(
                        e.target.value
                      )
                    }
                  >
                    <option value="All">
                      All document types
                    </option>

                    <option value="Case Report">
                      Case Report
                    </option>

                    <option value="Evidence">
                      Evidence
                    </option>

                    <option value="Investigation">
                      Investigation
                    </option>

                    <option value="Legal Document">
                      Legal Document
                    </option>

                    <option value="Forensic">
                      Forensic
                    </option>

                  </select>

                </div>

                <div>

                  <label>
                    Security status
                  </label>

                  <select
                    value={statusFilter}
                    onChange={(e) =>
                      setStatusFilter(
                        e.target.value
                      )
                    }
                  >

                    <option value="All">
                      All statuses
                    </option>

                    <option value="Verified">
                      Verified
                    </option>

                    <option value="Pending">
                      Pending
                    </option>

                  </select>

                </div>

                <button
                  className="clear-filter"
                  onClick={() => {
                    setSearch("");
                    setTypeFilter("All");
                    setStatusFilter(
                      "All"
                    );
                  }}
                >
                  Clear filters
                </button>

              </div>

              <div className="search-results-header">

                <strong>
                  {filteredDocuments.length} results
                </strong>

                <span>
                  Restricted to {role} access
                </span>

              </div>

              {filteredDocuments.map(
                (doc) => (
                  <div
                    className="search-result"
                    key={doc.id}
                  >

                    <div className="file-icon">
                      PDF
                    </div>

                    <div className="result-main">

                      <strong>
                        {doc.name}
                      </strong>

                      <span>
                        {doc.type} •{" "}
                        {doc.idCode} •{" "}
                        {doc.pages} pages
                      </span>

                    </div>

                    <span
                      className={
                        doc.status ===
                        "Verified"
                          ? "status verified"
                          : "status pending"
                      }
                    >
                      <i></i>
                      {doc.status}
                    </span>

                    <button
                      className="open-button"
                      onClick={() =>
                        openDocument(doc)
                      }
                    >
                      View →
                    </button>

                  </div>
                )
              )}

              {filteredDocuments.length ===
                0 && (
                <div className="empty-state">

                  <h3>
                    No matching records
                  </h3>

                  <p>
                    Try changing your search
                    terms or filters.
                  </p>

                </div>
              )}

            </div>

          </div>
        )}

        {/* UPLOAD */}

        {activeSection === "Upload" && (
          <div className="page-content">

            <div className="section-intro">

              <div>

                <span className="eyebrow">
                  SECURE INGESTION
                </span>

                <h2>
                  Upload document
                </h2>

                <p>
                  Add a new document to the
                  protected repository.
                </p>

              </div>

            </div>

            <div className="upload-layout">

              <div className="panel upload-main">

                <div
                  className="drop-zone"
                  onClick={() =>
                    document
                      .getElementById(
                        "fileInput"
                      )
                      .click()
                  }
                >

                  <div className="drop-icon">
                    ↑
                  </div>

                  <h3>
                    Select a secure document
                  </h3>

                  <p>
                    Click to browse your
                    computer and select a file.
                  </p>

                  <span>
                    PDF, DOC or DOCX • Maximum
                    demo size 25 MB
                  </span>

                  <input
                    id="fileInput"
                    type="file"
                    accept=".pdf,.doc,.docx"
                    hidden
                    onChange={(e) => {
                      const file =
                        e.target.files[0];

                      if (file) {
                        setSelectedFile(
                          file
                        );

                        setUploadSuccess(
                          false
                        );

                        setUploadProgress(
                          0
                        );
                      }
                    }}
                  />

                </div>

                {selectedFile && (
                  <div className="selected-file-card">

                    <div className="file-icon">
                      DOC
                    </div>

                    <div>

                      <strong>
                        {selectedFile.name}
                      </strong>

                      <span>
                        {(
                          selectedFile.size /
                          1024
                        ).toFixed(1)}{" "}
                        KB
                      </span>

                    </div>

                    <button
                      onClick={() => {
                        setSelectedFile(
                          null
                        );

                        setUploadProgress(
                          0
                        );

                        setUploadSuccess(
                          false
                        );
                      }}
                    >
                      ×
                    </button>

                  </div>
                )}

                {selectedFile &&
                  !uploadSuccess && (
                    <button
                      className="upload-submit"
                      disabled={uploading}
                      onClick={() => {
                        setUploading(true);
                        setUploadProgress(
                          0
                        );

                        let progress = 0;

                        const interval =
                          setInterval(
                            () => {
                              progress +=
                                10;

                              setUploadProgress(
                                progress
                              );

                              if (
                                progress >=
                                100
                              ) {
                                clearInterval(
                                  interval
                                );

                                const newDocument =
                                  {
                                    id:
                                      documents.length +
                                      1,

                                    name:
                                      selectedFile.name,

                                    type:
                                      "Uploaded Document",

                                    status:
                                      "Pending",

                                    pages: 1,

                                    idCode:
                                      `SD-2026-${String(
                                        documents.length +
                                          1
                                      ).padStart(
                                        3,
                                        "0"
                                      )}`,

                                    updated:
                                      "Just now",
                                  };

                                setDocuments(
                                  (prev) => [
                                    ...prev,
                                    newDocument,
                                  ]
                                );

                                setUploading(
                                  false
                                );

                                setUploadSuccess(
                                  true
                                );

                                lastActivity.current =
                                  Date.now();

                                setSessionTime(
                                  SESSION_DURATION
                                );
                              }
                            },
                            150
                          );
                      }}
                    >
                      {uploading
                        ? `Uploading securely... ${uploadProgress}%`
                        : "Upload securely →"}
                    </button>
                  )}

                {uploading && (
                  <div className="progress-wrapper">

                    <div className="progress-track">

                      <div
                        className="progress-fill"
                        style={{
                          width: `${uploadProgress}%`,
                        }}
                      ></div>

                    </div>

                  </div>
                )}

                {uploadSuccess && (
                  <div className="upload-success-card">

                    <div className="success-icon">
                      ✓
                    </div>

                    <div>

                      <strong>
                        Document uploaded
                        successfully
                      </strong>

                      <span>
                        The document has been
                        added to the secure
                        repository.
                      </span>

                    </div>

                    <button
                      onClick={() => {
                        setSelectedFile(
                          null
                        );

                        setUploadSuccess(
                          false
                        );

                        setUploadProgress(
                          0
                        );

                        setActiveSection(
                          "Documents"
                        );
                      }}
                    >
                      View repository →
                    </button>

                  </div>
                )}

              </div>

              <div className="panel security-upload-info">

                <span className="eyebrow">
                  PROTECTION
                </span>

                <h2>
                  Upload security
                </h2>

                <div className="upload-security-item">

                  <span>✓</span>

                  <div>

                    <strong>
                      Access controlled
                    </strong>

                    <small>
                      Role permissions enforced
                    </small>

                  </div>

                </div>

                <div className="upload-security-item">

                  <span>✓</span>

                  <div>

                    <strong>
                      Audit logged
                    </strong>

                    <small>
                      Upload activity is recorded
                    </small>

                  </div>

                </div>

                <div className="upload-security-item">

                  <span>✓</span>

                  <div>

                    <strong>
                      Verification
                    </strong>

                    <small>
                      Files enter pending review
                    </small>

                  </div>

                </div>

              </div>

            </div>

          </div>
        )}

        {/* ACTIVITY */}

        {activeSection === "Activity" && (
          <div className="page-content">

            <div className="section-intro">

              <div>

                <span className="eyebrow">
                  AUDIT TRAIL
                </span>

                <h2>
                  Activity & audit log
                </h2>

                <p>
                  Security events associated
                  with your current session.
                </p>

              </div>

              <div className="audit-live">

                <span className="status-dot"></span>

                LIVE MONITORING

              </div>

            </div>

            <div className="panel audit-panel">

              {activities.map(
                (activity, index) => (
                  <div
                    className="audit-row"
                    key={index}
                  >

                    <div className="audit-line">
                      <div className="audit-dot"></div>
                    </div>

                    <div className="activity-icon large">
                      {activity.icon}
                    </div>

                    <div className="audit-content">

                      <strong>
                        {activity.title}
                      </strong>

                      <span>
                        {activity.description}
                      </span>

                    </div>

                    <time>
                      {activity.time}
                    </time>

                    <span className="logged-badge">
                      LOGGED
                    </span>

                  </div>
                )
              )}

            </div>

          </div>
        )}

        {/* SECURITY */}

        {activeSection === "Security" && (
          <div className="page-content">

            <div className="section-intro">

              <div>

                <span className="eyebrow">
                  SECURITY OPERATIONS
                </span>

                <h2>
                  Security center
                </h2>

                <p>
                  Monitor authentication,
                  access and session protection.
                </p>

              </div>

            </div>

            <div className="security-grid">

              <div className="security-hero">

                <div className="security-ring">
                  100%
                </div>

                <div>

                  <span className="eyebrow">
                    SYSTEM STATUS
                  </span>

                  <h2>
                    Protected
                  </h2>

                  <p>
                    All configured security
                    controls are currently active.
                  </p>

                </div>

              </div>

              <div className="panel security-list">

                <div className="security-control">

                  <div className="control-icon">
                    🔐
                  </div>

                  <div>

                    <strong>
                      Multi-factor authentication
                    </strong>

                    <span>
                      Identity verification is enabled
                    </span>

                  </div>

                  <b>
                    ACTIVE
                  </b>

                </div>

                <div className="security-control">

                  <div className="control-icon">
                    ♢
                  </div>

                  <div>

                    <strong>
                      Role-based access
                    </strong>

                    <span>
                      {role} permissions are enforced
                    </span>

                  </div>

                  <b>
                    ACTIVE
                  </b>

                </div>

                <div className="security-control">

                  <div className="control-icon">
                    ◷
                  </div>

                  <div>

                    <strong>
                      Secure session
                    </strong>

                    <span>
                      Session expires after inactivity
                    </span>

                  </div>

                  <b>
                    ACTIVE
                  </b>

                </div>

                <div className="security-control">

                  <div className="control-icon">
                    ⌁
                  </div>

                  <div>

                    <strong>
                      Audit logging
                    </strong>

                    <span>
                      Security events are monitored
                    </span>

                  </div>

                  <b>
                    ACTIVE
                  </b>

                </div>

              </div>

            </div>

          </div>
        )}

        {/* DOCUMENT VIEWER */}

        {activeSection === "Viewer" &&
          selectedDocument && (
            <div className="page-content">

              <div className="viewer-top">

                <button
                  className="back-button"
                  onClick={closeViewer}
                >
                  ← Back to repository
                </button>

                <span className="viewer-security">

                  <span className="status-dot"></span>

                  Protected document

                </span>

              </div>

              <div className="viewer-layout">

                <div className="viewer-main panel">

                  <div className="viewer-toolbar">

                    <div className="viewer-file">

                      <div className="file-icon">
                        PDF
                      </div>

                      <div>

                        <strong>
                          {selectedDocument.name}
                        </strong>

                        <span>
                          {selectedDocument.idCode}
                        </span>

                      </div>

                    </div>

                    <div className="viewer-controls">

                      <button
                        onClick={() =>
                          setZoom(
                            Math.max(
                              50,
                              zoom - 10
                            )
                          )
                        }
                      >
                        −
                      </button>

                      <span>
                        {zoom}%
                      </span>

                      <button
                        onClick={() =>
                          setZoom(
                            Math.min(
                              150,
                              zoom + 10
                            )
                          )
                        }
                      >
                        +
                      </button>

                      <button
                        onClick={() =>
                          setCurrentPage(
                            Math.max(
                              1,
                              currentPage - 1
                            )
                          )
                        }
                      >
                        ‹
                      </button>

                      <span>
                        {currentPage} /{" "}
                        {selectedDocument.pages}
                      </span>

                      <button
                        onClick={() =>
                          setCurrentPage(
                            Math.min(
                              selectedDocument.pages,
                              currentPage + 1
                            )
                          )
                        }
                      >
                        ›
                      </button>

                    </div>

                  </div>

                  <div className="document-canvas">

                    <div
                      className="document-page"
                      style={{
                        transform:
                          `scale(${zoom / 100})`,
                      }}
                    >

                      <div className="document-watermark">
                        SECUREDOCS
                      </div>

                      <div className="document-page-header">

                        <span>
                          SECURE DOCUMENT
                        </span>

                        <span>
                          CONFIDENTIAL
                        </span>

                      </div>

                      <h1>
                        {selectedDocument.name}
                      </h1>

                      <p className="document-id">
                        Document ID:{" "}
                        {selectedDocument.idCode}
                      </p>

                      <hr />

                      <h3>
                        {selectedDocument.type}
                      </h3>

                      <p>
                        This secure document preview
                        represents protected digital
                        evidence within the SecureDocs
                        platform.
                      </p>

                      <div className="document-lines">

                        <span></span>
                        <span></span>
                        <span></span>
                        <span></span>
                        <span></span>
                        <span></span>

                      </div>

                      <div className="document-notice">
                        AUTHORIZED PERSONNEL ONLY
                      </div>

                      <div className="document-page-number">
                        Page {currentPage}
                      </div>

                    </div>

                  </div>

                </div>

                <div className="viewer-side panel">

                  <span className="eyebrow">
                    DOCUMENT DETAILS
                  </span>

                  <h2>
                    Information
                  </h2>

                  <div className="detail-item">

                    <span>
                      Name
                    </span>

                    <strong>
                      {selectedDocument.name}
                    </strong>

                  </div>

                  <div className="detail-item">

                    <span>
                      Type
                    </span>

                    <strong>
                      {selectedDocument.type}
                    </strong>

                  </div>

                  <div className="detail-item">

                    <span>
                      Status
                    </span>

                    <strong
                      className={
                        selectedDocument.status ===
                        "Verified"
                          ? "green-text"
                          : "orange-text"
                      }
                    >
                      {selectedDocument.status}
                    </strong>

                  </div>

                  <div className="detail-item">

                    <span>
                      Pages
                    </span>

                    <strong>
                      {selectedDocument.pages}
                    </strong>

                  </div>

                  <div className="detail-item">

                    <span>
                      Accessed by
                    </span>

                    <strong>
                      {role}
                    </strong>

                  </div>

                  <hr />

                  <label>
                    Annotation
                  </label>

                  <textarea
                    placeholder="Add a secure annotation..."
                    value={note}
                    onChange={(e) =>
                      setNote(
                        e.target.value
                      )
                    }
                  />

                  <button
                    className="annotation-button"
                    onClick={() =>
                      alert(
                        note
                          ? "Annotation saved successfully."
                          : "Please enter an annotation first."
                      )
                    }
                  >
                    Save annotation
                  </button>

                </div>

              </div>

            </div>
          )}

      </main>
    </div>
  );
}

export default App;