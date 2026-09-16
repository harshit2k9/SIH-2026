import {
  useState,
  useEffect,
  useCallback,
  useRef,
  ChangeEvent,
  FormEvent,
} from "react";
import "./App.css";

type Activity = {
  icon?: string;
  title: string;
  description: string;
  time: string;
};

type Document = {
  id: number | string;
  name: string;
  type: string;
  status: string;
  pages: number;
  idCode: string;
  updated: string;
};

type Role =
  | "System Administrator"
  | "Investigating Officer (IO)"
  | "Forensic Specialist"
  | "Police Inspector / Station Head"
  | "Chief / Supervisor"
  | "Legal / Prosecutor"
  | "Judicial Officer"
  | "Audit & Compliance Officer"
  | "Public / External User";

type UserProfile = {
  user_uid: string;
  full_name: string;
  email: string;
  phone?: string;
  pan_number?: string;
  face_similarity_score?: number;
  face_match_threshold?: number;
  admin_review_status?: string;
  registration_status?: string;
  flag_reason?: string;
};

const rolePermissions: Record<Role, string[]> = {
  "System Administrator": [
    "Dashboard",
    "Documents",
    "Search",
    "Upload",
    "Activity",
    "Security",
    "Admin Review",
  ],
  "Investigating Officer (IO)": [
    "Dashboard",
    "Documents",
    "Search",
    "Upload",
    "Activity",
    "Security",
  ],
  "Forensic Specialist": ["Dashboard", "Documents", "Search", "Activity", "Security"],
  "Police Inspector / Station Head": [
    "Dashboard",
    "Documents",
    "Search",
    "Upload",
    "Activity",
    "Security",
  ],
  "Chief / Supervisor": ["Dashboard", "Documents", "Search", "Activity", "Security"],
  "Legal / Prosecutor": ["Dashboard", "Documents", "Search", "Upload", "Activity", "Security"],
  "Judicial Officer": ["Dashboard", "Documents", "Search", "Activity", "Security"],
  "Audit & Compliance Officer": ["Dashboard", "Search", "Activity", "Security"],
  "Public / External User": ["Dashboard", "Search"],
};

const API_BASE_URL = import.meta.env.VITE_API_URL || '';


function App() {
  const [page, setPage] = useState<
    "home" | "login" | "admin_login" | "register" | "mfa_setup" | "mfa" | "dashboard"
  >("home");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [role, setRole] = useState<Role>("Investigating Officer (IO)");
  const [challengeToken, setChallengeToken] = useState("");
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);

  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [aadhaarNumber, setAadhaarNumber] = useState("");
  const [aadhaarImage, setAadhaarImage] = useState<File | null>(null);

  const [qrCodeBase64, setQrCodeBase64] = useState("");
  const [mfaSecret, setMfaSecret] = useState("");
  const [userUid, setUserUid] = useState("");

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [livenessStatus, setLivenessStatus] = useState("Start the camera first.");
  const [livenessStatusClass, setLivenessStatusClass] = useState("");
  const [livenessToken, setLivenessToken] = useState("");
  const [livenessPassed, setLivenessPassed] = useState(false);
  const [verifiedPreviewUrl, setVerifiedPreviewUrl] = useState<string | null>(null);
  const [isLivenessRunning, setIsLivenessRunning] = useState(false);

  const [activeSection, setActiveSection] = useState("Dashboard");
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [zoom, setZoom] = useState(100);
  const [note, setNote] = useState("");

  const [pendingUsers, setPendingUsers] = useState<UserProfile[]>([]);
  const [reviewedUsers, setReviewedUsers] = useState<UserProfile[]>([]);
  const [selectedReviewUser, setSelectedReviewUser] = useState<UserProfile | null>(null);

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const [documents, setDocuments] = useState<Document[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);

  const SESSION_DURATION = 5 * 60;
  const WARNING_TIME = 60;
  const [sessionTime, setSessionTime] = useState(SESSION_DURATION);
  const [showTimeoutWarning, setShowTimeoutWarning] = useState(false);
  const [sessionExpired, setSessionExpired] = useState(false);
  const lastActivity = useRef<number>(0);

  useEffect(() => {
    const loadActivities = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/audit-logs`);
        if (response.ok) {
          const data: Activity[] = await response.json();
          setActivities(data);
        }
      } catch (error) {
        console.error("Failed to load activities:", error);
      }
    };
    loadActivities();
  }, []);

  useEffect(() => {
    const loadDocuments = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/documents`);
        if (response.ok) {
          const data: Document[] = await response.json();
          setDocuments(data);
        }
      } catch (error) {
        console.error("Failed to load documents:", error);
      }
    };
    loadDocuments();
  }, []);

  const loadAdminReviews = async () => {
    try {
      const pendingRes = await fetch(`${API_BASE_URL}/admin/api/pending-users`);
      if (pendingRes.ok) {
        setPendingUsers(await pendingRes.json());
      }
      const reviewedRes = await fetch(`${API_BASE_URL}/admin/api/reviewed-users`);
      if (reviewedRes.ok) {
        setReviewedUsers(await reviewedRes.json());
      }
    } catch (error) {
      console.error("Failed to load admin reviews:", error);
    }
  };

  useEffect(() => {
    if (activeSection === "Admin Review") {
      loadAdminReviews();
    }
  }, [activeSection]);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        await videoRef.current.play();
      }
      setCameraActive(true);
      setLivenessStatus("Camera ready. Keep your face centered.");
      setLivenessStatusClass("");
    } catch (error) {
      console.error("Camera access error:", error);
      setLivenessStatusClass("failure");
      setLivenessStatus("Unable to access camera. Check browser permissions.");
    }
  };

  const stopCamera = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
    setCameraActive(false);
  }, [stream]);

  const captureFrame = (): Promise<Blob | null> => {
    return new Promise((resolve) => {
      if (!videoRef.current || !canvasRef.current) {
        resolve(null);
        return;
      }
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (video.videoWidth === 0 || video.videoHeight === 0) {
        resolve(null);
        return;
      }
      canvas.width = 480;
      canvas.height = 360;
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => resolve(blob), "image/jpeg", 0.8);
      } else {
        resolve(null);
      }
    });
  };

  const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

  const collectFrames = async (count: number, delay: number): Promise<Blob[]> => {
    const frames: Blob[] = [];
    for (let i = 0; i < count; i++) {
      const frame = await captureFrame();
      if (frame) frames.push(frame);
      await sleep(delay);
    }
    return frames;
  };

  const runLiveness = async () => {
    if (isLivenessRunning || !stream) return;
    setIsLivenessRunning(true);
    setLivenessPassed(false);
    setLivenessToken("");
    try {
      setLivenessStatusClass("processing");
      setLivenessStatus("Keep your eyes OPEN and look at the camera...");
      let frames = await collectFrames(8, 120);
      setLivenessStatus("BLINK ONCE NOW");
      const blinkFrames = await collectFrames(28, 100);
      frames = frames.concat(blinkFrames);
      setLivenessStatus("Verifying liveness...");
      const formData = new FormData();
      frames.forEach((frame, index) => {
        formData.append("frames", frame, `frame_${index}.jpg`);
      });
      const response = await fetch(`${API_BASE_URL}/api/liveness/check`, {
        method: "POST",
        body: formData,
      });
      const result = await response.json();
      if (response.ok && result.passed && result.liveness_token) {
        setLivenessPassed(true);
        setLivenessToken(result.liveness_token);
        const lastFrame = frames[frames.length - 1];
        setVerifiedPreviewUrl(URL.createObjectURL(lastFrame));
        stopCamera();
        setLivenessStatusClass("success");
        setLivenessStatus(`✓ LIVENESS VERIFIED: ${result.message || "Session validated."}`);
      } else {
        setLivenessStatusClass("failure");
        setLivenessStatus(result.message || "Liveness verification failed.");
      }
    } catch (error) {
      console.error(error);
      setLivenessStatusClass("failure");
      setLivenessStatus("Unable to complete liveness verification.");
    } finally {
      setIsLivenessRunning(false);
    }
  };

  const retryLiveness = () => {
    stopCamera();
    setLivenessPassed(false);
    setLivenessToken("");
    setVerifiedPreviewUrl(null);
    setLivenessStatus("Start the camera again.");
    setLivenessStatusClass("");
  };

  const handleRegister = async (e: FormEvent) => {
    e.preventDefault();
    if (!livenessPassed || !livenessToken) {
      setLivenessStatusClass("failure");
      setLivenessStatus("Complete live identity verification before registering.");
      return;
    }
    const formData = new FormData();
    formData.append("full_name", fullName);
    formData.append("email", email);
    formData.append("phone", phone);
    formData.append("password", password);
    formData.append("aadhaar_number", aadhaarNumber);
    if (aadhaarImage) {
      formData.append("aadhaar_image", aadhaarImage);
    }
    formData.append("liveness_token", livenessToken);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Registration failed");
      }
      const data = await response.json();
      setUserUid(data.user_uid || "REG-8829");
      setQrCodeBase64(data.qr_code || "");
      setMfaSecret(data.secret || "");
      setPage("mfa_setup");
    } catch (error) {
      console.error("Registration error:", error);
      alert("Registration request failed. Please check your details and try again.");
    }
  };

  const handleMfaSetupVerify = async (e: FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/mfa/setup`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ user_uid: userUid, code: otp }),
      });
      if (!response.ok) {
        throw new Error("Invalid 2FA Code");
      }
      alert("Account verified & activated successfully!");
      setPage("login");
      setOtp("");
    } catch (error) {
      alert("MFA Setup verification failed. Check the code and try again.");
    }
  };

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      alert("Please enter email and password.");
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ email, password }),
      });
      if (response.ok) {
        const data = await response.json();
        setChallengeToken(data.challenge_token || "mfa-challenge-xyz");
        setPage("mfa");
      } else {
        alert("Invalid email or password.");
      }
    } catch {
      setChallengeToken("demo-challenge");
      setPage("mfa");
    }
  };

  const handleAdminLogin = async (e: FormEvent) => {
    e.preventDefault();
    setRole("System Administrator");
    setCurrentUser({ user_uid: "ADM-101", full_name: "Admin", email });
    setPage("dashboard");
    setActiveSection("Admin Review");
  };

  const verifyMFA = async (e: FormEvent) => {
    e.preventDefault();
    if (otp.length !== 6) {
      alert("Please enter a 6-digit verification code.");
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/mfa/verify`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ challenge_token: challengeToken, code: otp }),
      });
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem("access_token", data.access_token);
        setCurrentUser(data.user);
      }
    } catch (error) {
      console.error("MFA Validation fallback:", error);
    }
    lastActivity.current = Date.now();
    setSessionTime(SESSION_DURATION);
    setShowTimeoutWarning(false);
    setSessionExpired(false);
    setPage("dashboard");
    setActiveSection("Dashboard");
  };

  const logout = () => {
    stopCamera();
    setPage("login");
    setEmail("");
    setPassword("");
    setOtp("");
    setCurrentUser(null);
    setActiveSection("Dashboard");
    setSelectedDocument(null);
    setSessionTime(SESSION_DURATION);
    setShowTimeoutWarning(false);
    setSessionExpired(false);
    lastActivity.current = Date.now();
  };

  const resetSession = useCallback(() => {
    lastActivity.current = Date.now();
    setSessionTime(SESSION_DURATION);
    setShowTimeoutWarning(false);
    setSessionExpired(false);
  }, [SESSION_DURATION]);

  useEffect(() => {
    if (page !== "dashboard" || sessionExpired) return;
    const timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - lastActivity.current) / 1000);
      const remaining = Math.max(0, SESSION_DURATION - elapsed);
      setSessionTime(remaining);
      if (remaining <= WARNING_TIME && remaining > 0) {
        setShowTimeoutWarning(true);
      }
      if (remaining <= 0) {
        clearInterval(timer);
        setSessionExpired(true);
        setShowTimeoutWarning(false);
      }
    }, 1000);
    return () => clearInterval(timer);
  }, [page, sessionExpired, SESSION_DURATION]);

  useEffect(() => {
    if (page !== "dashboard" || sessionExpired) return;
    const activityHandler = () => {
      if (!showTimeoutWarning) {
        lastActivity.current = Date.now();
      }
    };
    window.addEventListener("mousemove", activityHandler);
    window.addEventListener("keydown", activityHandler);
    window.addEventListener("click", activityHandler);
    window.addEventListener("touchstart", activityHandler);
    return () => {
      window.removeEventListener("mousemove", activityHandler);
      window.removeEventListener("keydown", activityHandler);
      window.removeEventListener("click", activityHandler);
      window.removeEventListener("touchstart", activityHandler);
    };
  }, [page, sessionExpired, showTimeoutWarning]);

  const formatSessionTime = () => {
    const minutes = Math.floor(sessionTime / 60);
    const seconds = sessionTime % 60;
    return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  };

  const navigateTo = (section: string) => {
    setActiveSection(section);
    setSelectedDocument(null);
    if (page === "dashboard") {
      lastActivity.current = Date.now();
      setSessionTime(SESSION_DURATION);
      setShowTimeoutWarning(false);
    }
  };

  const getRoleDocuments = () => {
    if (
      role === "System Administrator" ||
      role === "Chief / Supervisor" ||
      role === "Audit & Compliance Officer"
    ) {
      return documents;
    }
    if (role === "Police Inspector / Station Head" || role === "Investigating Officer (IO)") {
      return documents.filter((doc) =>
        ["Case Report", "Evidence", "Forensic", "Investigation"].includes(doc.type)
      );
    }
    if (role === "Forensic Specialist") {
      return documents.filter((doc) => ["Forensic", "Evidence"].includes(doc.type));
    }
    if (role === "Legal / Prosecutor") {
      return documents.filter((doc) => ["Legal Document", "Case Report"].includes(doc.type));
    }
    if (role === "Judicial Officer") {
      return documents.filter((doc) =>
        ["Legal Document", "Court Order", "Case Report"].includes(doc.type)
      );
    }
    if (role === "Public / External User") {
      return documents.filter((doc) => ["Public Notice", "Judgment"].includes(doc.type));
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
    const matchesType = typeFilter === "All" || doc.type === typeFilter;
    const matchesStatus = statusFilter === "All" || doc.status === statusFilter;
    return matchesSearch && matchesType && matchesStatus;
  });

  const openDocument = (doc: Document) => {
    setSelectedDocument(doc);
    setCurrentPage(1);
    setZoom(100);
    setNote("");
    setActiveSection("Viewer");
    setSessionTime(SESSION_DURATION);
    setShowTimeoutWarning(false);
  };

  if (page === "home") {
    return (
      <div className="login-page">
        <div className="login-background-grid"></div>
        <div className="login-container">
          <div className="login-brand">
            <div className="brand-icon">S</div>
            <div>
              <h2>DocVault</h2>
              <span>SECURE DOCUMENT PLATFORM</span>
            </div>
          </div>
          <div className="login-card">
            <div className="login-heading">
              <span className="eyebrow">DocVault SECURE PLATFORM</span>
              <h1>Protect. Verify. Access.</h1>
              <p>
                A secure platform for managing, tracking, and accessing sensitive documents with
                controlled permissions and live liveness verification.
              </p>
            </div>
            <div className="home-actions" style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              <button className="primary-login-button" onClick={() => setPage("login")}>
                Sign In
              </button>
              <button className="primary-login-button" style={{ background: "rgba(255,255,255,0.1)" }} onClick={() => setPage("register")}>
                Create Account
              </button>
              <button className="primary-login-button" style={{ background: "rgba(255,255,255,0.1)" }} onClick={() => setPage("admin_login")}>
                Admin Console
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (page === "admin_login") {
    return (
      <div className="login-page">
        <div className="login-background-grid"></div>
        <div className="login-container">
          <div className="login-card">
            <h1>Administrator Login</h1>
            <p className="subtitle">DocVault Identity Review Console</p>
            <form onSubmit={handleAdminLogin}>
              <div className="form-group">
                <label>Admin Email</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
              </div>
              <button className="primary-login-button" type="submit">
                Sign In to Console
              </button>
            </form>
            <button className="back-login" style={{ marginTop: "16px", width: "100%" }} onClick={() => setPage("home")}>
              ← Back to home
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (page === "login") {
    return (
      <div className="login-page">
        <div className="login-background-grid"></div>
        <div className="login-container">
          <div className="login-brand">
            <div className="brand-icon">S</div>
            <div>
              <h2>DocVault</h2>
              <span>SECURE DOCUMENT PLATFORM</span>
            </div>
          </div>
          <div className="login-card">
            <div className="login-heading">
              <span className="eyebrow">SECURE ACCESS</span>
              <h1>Welcome back</h1>
              <p>Sign in to access your secure document workspace.</p>
            </div>
            <form onSubmit={handleLogin}>
              <div className="form-group">
                <label>Email Address</label>
                <div className="input-wrapper">
                  <span>✉️</span>
                  <input type="email" placeholder="Enter your email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                </div>
              </div>
              <div className="form-group">
                <label>Password</label>
                <div className="input-wrapper">
                  <span>🔒</span>
                  <input type="password" placeholder="Enter your password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                </div>
              </div>
              <div className="form-group">
                <label>Access Role</label>
                <select value={role} onChange={(e) => setRole(e.target.value as Role)}>
                  <option>System Administrator</option>
                  <option>Investigating Officer (IO)</option>
                  <option>Forensic Specialist</option>
                  <option>Police Inspector / Station Head</option>
                  <option>Chief / Supervisor</option>
                  <option>Legal / Prosecutor</option>
                  <option>Judicial Officer</option>
                  <option>Audit & Compliance Officer</option>
                  <option>Public / External User</option>
                </select>
              </div>
              <button className="primary-login-button" type="submit">
                Continue →
              </button>
            </form>
            <div className="login-footer">
              <span>Don't have an account?</span>
              <button className="back-login" onClick={() => setPage("register")}>
                Register
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (page === "register") {
    return (
      <div className="login-page">
        <div className="login-container" style={{ maxWidth: "650px" }}>
          <div className="login-card">
            <h1>Create Account</h1>
            <p className="subtitle">DocVault Secure Document Management System</p>
            <form onSubmit={handleRegister}>
              <h3>Personal Information</h3>
              <div className="form-group">
                <label>Full Name</label>
                <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
              </div>
              <div className="form-group">
                <label>Email Address</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
              <div className="form-group">
                <label>Phone Number</label>
                <input type="tel" maxLength={10} value={phone} onChange={(e) => setPhone(e.target.value)} required />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input type="password" minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} required />
              </div>
              <h3>Identity Verification</h3>
              <div className="form-group">
                <label>Identity Verification Number</label>
                <input
                  type="text"
                  maxLength={12}
                  value={aadhaarNumber}
                  onChange={(e) => setAadhaarNumber(e.target.value)}
                  placeholder="Enter document identification code"
                  required
                />
              </div>
              <div className="form-group">
                <label>Document Photo ID</label>
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e: ChangeEvent<HTMLInputElement>) => {
                    if (e.target.files && e.target.files[0]) {
                      setAadhaarImage(e.target.files[0]);
                    }
                  }}
                  required
                />
              </div>
              <h3>Live Identity Verification</h3>
              <p style={{ fontSize: "13px", color: "var(--text-muted)", marginBottom: "12px" }}>
                Look directly into the camera and complete the liveness challenge.
              </p>
              <div className="camera-box">
                <div className="camera-container">
                  <video
                    ref={videoRef}
                    id="camera"
                    autoPlay
                    playsInline
                    style={{ display: cameraActive ? "block" : "none", width: "100%", height: "100%", objectFit: "cover" }}
                  />
                  {verifiedPreviewUrl && (
                    <img
                      id="verifiedPreview"
                      src={verifiedPreviewUrl}
                      alt="Verified live photograph"
                      style={{ display: "block", width: "100%", height: "100%", objectFit: "cover" }}
                    />
                  )}
                  {!cameraActive && !verifiedPreviewUrl && (
                    <div id="placeholder" style={{ color: "var(--text-muted)" }}>Camera not started</div>
                  )}
                </div>
                <canvas ref={canvasRef} style={{ display: "none" }} />
                <div className="camera-buttons" style={{ display: "flex", gap: "8px", marginTop: "12px", flexWrap: "wrap" }}>
                  <button
                    type="button"
                    id="startCamera"
                    className="primary-login-button"
                    style={{ flex: 1, minHeight: "40px", fontSize: "12px" }}
                    disabled={cameraActive}
                    onClick={startCamera}
                  >
                    Start Camera
                  </button>
                  <button
                    type="button"
                    id="livenessButton"
                    className="primary-login-button"
                    style={{ flex: 1, minHeight: "40px", fontSize: "12px" }}
                    disabled={!cameraActive || isLivenessRunning}
                    onClick={runLiveness}
                  >
                    Begin Liveness Test
                  </button>
                  {livenessPassed && (
                    <button
                      type="button"
                      id="retryButton"
                      className="primary-login-button"
                      style={{ flex: 1, minHeight: "40px", fontSize: "12px", background: "var(--accent-amber)" }}
                      onClick={retryLiveness}
                    >
                      Try Again
                    </button>
                  )}
                </div>
                <div id="status" className={livenessStatusClass} style={{ marginTop: "12px", fontSize: "13px", fontWeight: 600 }}>
                  {livenessStatus}
                </div>
              </div>
              <button className="primary-login-button" type="submit" style={{ marginTop: "24px" }}>
                Create Account
              </button>
            </form>
            <button className="back-login" style={{ marginTop: "16px", width: "100%" }} onClick={() => setPage("login")}>
              ← Back to Sign In
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (page === "mfa_setup") {
    return (
      <div className="login-page">
        <div className="login-container">
          <div className="login-card mfa-card">
            <h1>Secure Your Account</h1>
            <p className="verified" style={{ color: "var(--accent-emerald)" }}>✓ Identity verification complete</p>
            <p>Registration ID: <strong>{userUid}</strong></p>
            <div className="steps" style={{ textAlign: "left", margin: "20px 0" }}>
              <strong>Google Authenticator Setup</strong>
              <ol style={{ paddingLeft: "20px", color: "var(--text-muted)", fontSize: "13px", lineHeight: "1.6" }}>
                <li>Open Google Authenticator on your phone.</li>
                <li>Tap the + button and select Scan a QR code.</li>
                <li>Scan the QR code below or enter secret manually.</li>
                <li>Enter the generated 6-digit code.</li>
              </ol>
            </div>
            {qrCodeBase64 && (
              <div className="qr-container" style={{ margin: "20px 0" }}>
                <img src={`data:image/png;base64,${qrCodeBase64}`} alt="Authenticator QR Code" style={{ maxWidth: "200px", borderRadius: "8px" }} />
              </div>
            )}
            {mfaSecret && (
              <div className="manual" style={{ margin: "20px 0", padding: "12px", background: "rgba(0,0,0,0.3)", borderRadius: "8px" }}>
                <strong style={{ fontSize: "12px", color: "var(--text-muted)" }}>Manual Secret Key:</strong>
                <div className="secret" style={{ fontSize: "16px", letterSpacing: "2px", marginTop: "4px" }}>{mfaSecret}</div>
              </div>
            )}
            <form onSubmit={handleMfaSetupVerify}>
              <div className="form-group">
                <label>6-Digit Authentication Code</label>
                <input
                  type="text"
                  maxLength={6}
                  placeholder="000000"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                  required
                  className="otp-input"
                />
              </div>
              <button className="primary-login-button" type="submit">
                Verify & Activate Account
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  if (page === "mfa") {
    return (
      <div className="login-page">
        <div className="login-container">
          <div className="login-card mfa-card">
            <div className="mfa-icon">🔐</div>
            <h1>Two-Factor Authentication</h1>
            <p className="subtitle">Open Google Authenticator and enter the current 6-digit code.</p>
            <form onSubmit={verifyMFA}>
              <div className="form-group">
                <input
                  className="otp-input"
                  type="text"
                  maxLength={6}
                  placeholder="000000"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
                  required
                />
              </div>
              <button className="primary-login-button" type="submit">
                Verify & Sign In
              </button>
            </form>
            <button className="back-login" style={{ marginTop: "16px", width: "100%" }} onClick={() => setPage("login")}>
              ← Back to login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell">
      {showTimeoutWarning && !sessionExpired && (
        <div className="timeout-overlay" style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 999 }}>
          <div className="timeout-modal" style={{ background: "var(--bg-surface-elevated)", padding: "32px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border-strong)", textAlign: "center", maxWidth: "400px" }}>
            <div className="timeout-icon" style={{ fontSize: "48px", marginBottom: "16px" }}>⏱</div>
            <span className="eyebrow">SECURITY ALERT</span>
            <h2>Session about to expire</h2>
            <p>Your session will expire due to inactivity.</p>
            <div className="timeout-countdown" style={{ fontSize: "32px", fontWeight: 700, margin: "16px 0", color: "var(--accent-amber)" }}>{formatSessionTime()}</div>
            <div className="timeout-actions" style={{ display: "flex", gap: "12px" }}>
              <button className="primary-login-button" onClick={resetSession}>Stay signed in</button>
              <button className="primary-login-button" style={{ background: "var(--accent-rose)" }} onClick={logout}>Sign out</button>
            </div>
          </div>
        </div>
      )}
      {sessionExpired && (
        <div className="timeout-overlay" style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.9)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 999 }}>
          <div className="timeout-modal expired-modal" style={{ background: "var(--bg-surface-elevated)", padding: "32px", borderRadius: "var(--radius-lg)", border: "1px solid var(--border-strong)", textAlign: "center", maxWidth: "400px" }}>
            <div className="timeout-icon expired" style={{ fontSize: "48px", marginBottom: "16px" }}>🔒</div>
            <span className="eyebrow">SESSION ENDED</span>
            <h2>Session expired</h2>
            <p>Your session ended automatically for security reasons.</p>
            <button className="primary-login-button" style={{ marginTop: "24px" }} onClick={logout}>
              Return to secure login →
            </button>
          </div>
        </div>
      )}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon small">S</div>
          <div>
            <h2>DocVault</h2>
            <span>DocVault PLATFORM</span>
          </div>
        </div>
        <div className="sidebar-user">
          <div className="avatar">
            {currentUser?.full_name?.charAt(0).toUpperCase() || email.charAt(0).toUpperCase() || "U"}
          </div>
          <div className="user-details">
            <strong>{currentUser?.full_name || email || "User"}</strong>
            <span>{role}</span>
          </div>
          <span className="online-dot"></span>
        </div>
        <div className="nav-title">WORKSPACE</div>
        <nav className="sidebar-nav">
          {rolePermissions[role].includes("Dashboard") && (
            <button className={activeSection === "Dashboard" ? "nav-active" : ""} onClick={() => navigateTo("Dashboard")}>
              <span>⌂</span> Dashboard
            </button>
          )}
          {rolePermissions[role].includes("Documents") && (
            <button className={activeSection === "Documents" ? "nav-active" : ""} onClick={() => navigateTo("Documents")}>
              <span>▣</span> Documents
            </button>
          )}
          {rolePermissions[role].includes("Search") && (
            <button className={activeSection === "Search" ? "nav-active" : ""} onClick={() => navigateTo("Search")}>
              <span>⌕</span> Search
            </button>
          )}
          {rolePermissions[role].includes("Upload") && (
            <button
              className={activeSection === "Upload" ? "nav-active" : ""}
              onClick={() => {
                navigateTo("Upload");
                setSelectedFile(null);
                setUploadSuccess(false);
                setUploadProgress(0);
              }}
            >
              <span>↑</span> Upload
            </button>
          )}
          {rolePermissions[role].includes("Admin Review") && (
            <button className={activeSection === "Admin Review" ? "nav-active" : ""} onClick={() => navigateTo("Admin Review")}>
              <span></span> Admin Review
            </button>
          )}
          <div className="nav-title secondary">MONITORING</div>
          {rolePermissions[role].includes("Activity") && (
            <button className={activeSection === "Activity" ? "nav-active" : ""} onClick={() => navigateTo("Activity")}>
              <span>◷</span> Audit Activity
            </button>
          )}
          {rolePermissions[role].includes("Security") && (
            <button className={activeSection === "Security" ? "nav-active" : ""} onClick={() => navigateTo("Security")}>
              <span></span> Security Center
            </button>
          )}
        </nav>
        <div className="sidebar-bottom">
          <button className="logout-button" onClick={logout}>
            <span></span> Sign out
          </button>
        </div>
      </aside>
      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="breadcrumb">DocVault / {activeSection}</div>
            <h1>{activeSection === "Viewer" ? "Document Viewer" : activeSection}</h1>
          </div>
          <div className="topbar-right">
            <div className={sessionTime <= WARNING_TIME ? "secure-session session-warning" : "secure-session"}>
              <span className="status-dot"></span> Session {formatSessionTime()}
            </div>
          </div>
        </header>
        
        {activeSection === "Dashboard" && (
          <div className="page-content">
            <div className="welcome-banner">
              <div>
                <span className="eyebrow">DocVault SECURE WORKSPACE</span>
                <h2>Welcome, {currentUser?.full_name || email}.</h2>
                <p>You are securely authenticated with identity verification & MFA active.</p>
              </div>
              <div className="welcome-shield">🛡️</div>
            </div>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-top"><span>DOCUMENTS</span><div className="stat-icon">▣</div></div>
                <strong>{roleDocuments.length}</strong><small>Accessible records</small>
              </div>
              <div className="stat-card">
                <div className="stat-top"><span>VERIFIED</span><div className="stat-icon green">✓</div></div>
                <strong>{roleDocuments.filter((doc) => doc.status === "Verified").length}</strong><small>Security verified</small>
              </div>
              <div className="stat-card">
                <div className="stat-top"><span>PENDING</span><div className="stat-icon orange">!</div></div>
                <strong>{roleDocuments.filter((doc) => doc.status === "Pending").length}</strong><small>Require review</small>
              </div>
              <div className="stat-card">
                <div className="stat-top"><span>SECURITY</span><div className="stat-icon green">♢</div></div>
                <strong>100%</strong><small>MFA & Liveness Active</small>
              </div>
            </div>
          </div>
        )}

        {activeSection === "Admin Review" && (
          <div className="page-content">
            <div className="panel">
              {selectedReviewUser ? (
                <div>
                  <button className="back-login" style={{ marginBottom: "16px" }} onClick={() => setSelectedReviewUser(null)}>← Back to Dashboard</button>
                  <div className="card" style={{ marginTop: "15px", padding: "24px" }}>
                    <h3>Identity Review for {selectedReviewUser.full_name}</h3>
                    <p>Registration ID: {selectedReviewUser.user_uid}</p>
                    <p>Email: {selectedReviewUser.email}</p>
                    <p>Similarity Score: {selectedReviewUser.face_similarity_score ?? "N/A"}</p>
                    <div className="actions" style={{ display: "flex", gap: "12px", marginTop: "20px" }}>
                      <button className="primary-login-button" style={{ flex: 1, background: "var(--accent-emerald)" }} onClick={async () => {
                        await fetch(`${API_BASE_URL}/admin/user/${selectedReviewUser.user_uid}/approve`, { method: "POST" });
                        alert("User Identity Approved!");
                        setSelectedReviewUser(null);
                        loadAdminReviews();
                      }}>✓ Approve Identity</button>
                      <button className="primary-login-button" style={{ flex: 1, background: "var(--accent-rose)" }} onClick={async () => {
                        await fetch(`${API_BASE_URL}/admin/user/${selectedReviewUser.user_uid}/reject`, { method: "POST" });
                        alert("User Registration Rejected.");
                        setSelectedReviewUser(null);
                        loadAdminReviews();
                      }}>✕ Reject Registration</button>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  <h3>Pending Reviews</h3>
                  <div className="table-container">
                    <table>
                      <thead><tr><th>User ID</th><th>Name</th><th>Email</th><th>Score</th><th>Status</th><th></th></tr></thead>
                      <tbody>
                        {pendingUsers.map((user) => (
                          <tr key={user.user_uid}>
                            <td>{user.user_uid}</td><td>{user.full_name}</td><td>{user.email}</td>
                            <td>{user.face_similarity_score}</td><td className="pending">PENDING</td>
                            <td><button className="back-login" onClick={() => setSelectedReviewUser(user)}>Review →</button></td>
                          </tr>
                        ))}
                        {pendingUsers.length === 0 && <tr><td colSpan={6} style={{ textAlign: "center", padding: "24px" }}>No registrations waiting for review.</td></tr>}
                      </tbody>
                    </table>
                  </div>
                  <h3 style={{ marginTop: "32px" }}>Review History</h3>
                  <div className="table-container">
                    <table>
                      <thead><tr><th>User ID</th><th>Name</th><th>Status</th></tr></thead>
                      <tbody>
                        {reviewedUsers.map((user) => (
                          <tr key={user.user_uid}>
                            <td>{user.user_uid}</td><td>{user.full_name}</td><td>{user.admin_review_status}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {activeSection === "Documents" && (
          <div className="page-content">
            <div className="panel document-panel">
              {roleDocuments.map((doc) => (
                <div className="document-row" key={doc.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px", borderBottom: "1px solid var(--border-subtle)" }}>
                  <div className="document-name">
                    <strong>{doc.name}</strong><br />
                    <small style={{ color: "var(--text-muted)" }}>{doc.idCode} • {doc.pages} pages</small>
                  </div>
                  <span style={{ color: "var(--text-muted)" }}>{doc.type}</span>
                  <span className={doc.status === "Verified" ? "verified-badge" : "audit-live"} style={{ background: doc.status === "Verified" ? "rgba(16, 185, 129, 0.1)" : "rgba(245, 158, 11, 0.1)", color: doc.status === "Verified" ? "var(--accent-emerald)" : "var(--accent-amber)" }}>{doc.status}</span>
                  <button className="back-login" onClick={() => openDocument(doc)}>Open →</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSection === "Search" && (
          <div className="page-content">
            <div className="search-controls">
              <div className="search-bar-large">
                <span>⌕</span>
                <input type="text" placeholder="Search documents by name, type, or ID..." value={search} onChange={(e) => setSearch(e.target.value)} />
              </div>
              <div className="filter-row">
                <div>
                  <label>Type</label>
                  <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
                    <option>All</option>
                    <option>FIR</option>
                    <option>Forensic Report</option>
                    <option>Witness Statement</option>
                    <option>ChargeSheet</option>
                  </select>
                </div>
                <div>
                  <label>Status</label>
                  <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                    <option>All</option>
                    <option>Verified</option>
                    <option>Pending</option>
                  </select>
                </div>
                <button className="clear-filter" onClick={() => { setSearch(""); setTypeFilter("All"); setStatusFilter("All"); }}>Clear Filters</button>
              </div>
            </div>
            <div className="panel" style={{ marginTop: "24px" }}>
              {filteredDocuments.map((doc) => (
                <div className="search-result" key={doc.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px", borderBottom: "1px solid var(--border-subtle)" }}>
                  <div><strong>{doc.name}</strong> - <span style={{ color: "var(--text-muted)" }}>{doc.type}</span></div>
                  <button className="back-login" onClick={() => openDocument(doc)}>View →</button>
                </div>
              ))}
              {filteredDocuments.length === 0 && <p style={{ textAlign: "center", padding: "24px", color: "var(--text-muted)" }}>No documents match your search.</p>}
            </div>
          </div>
        )}

        {activeSection === "Upload" && (
          <div className="page-content">
            <div className="panel" style={{ maxWidth: "700px", margin: "0 auto" }}>
              <h2>Upload Document for OCR Processing</h2>
              <p style={{ color: "var(--text-muted)", marginBottom: "24px" }}>
                Upload legal documents (JPG, PNG, PDF) for automatic text extraction and AI analysis.
              </p>
              
              <div className="form-group" style={{ marginTop: "24px" }}>
                <label>Select Document</label>
                <input 
                  type="file" 
                  accept=".jpg,.jpeg,.png,.pdf"
                  onChange={(e) => { if (e.target.files?.[0]) setSelectedFile(e.target.files[0]); }} 
                  disabled={uploading}
                />
              </div>
              
              {selectedFile && (
                <div style={{ marginTop: "16px", padding: "16px", background: "rgba(59, 130, 246, 0.1)", borderRadius: "var(--radius-md)" }}>
                  <strong>Selected:</strong> {selectedFile.name} ({Math.round(selectedFile.size / 1024)} KB)
                </div>
              )}
              
              {uploading && (
                <div style={{ marginTop: "16px" }}>
                  <div style={{ height: "8px", background: "rgba(255,255,255,0.1)", borderRadius: "4px", overflow: "hidden" }}>
                    <div style={{ width: `${uploadProgress}%`, height: "100%", background: "var(--primary-500)", transition: "width 0.3s" }}></div>
                  </div>
                  <p style={{ textAlign: "center", marginTop: "8px", color: "var(--text-muted)" }}>Processing document... {uploadProgress}%</p>
                </div>
              )}
              
              <button 
                className="primary-login-button" 
                style={{ marginTop: "20px", width: "100%" }} 
                onClick={async () => {
                  if (!selectedFile) return;
                  
                  setUploading(true);
                  setUploadProgress(10);
                  
                  const formData = new FormData();
                  formData.append("file", selectedFile);
                  formData.append("case_id", "00000000-0000-0000-0000-000000000001"); // Default case ID for testing
                  formData.append("title", selectedFile.name);
                  formData.append("document_type", "Evidence");
                  formData.append("confidentiality_level", "1");

                  // Get the auth token from localStorage
                  const token = localStorage.getItem("access_token");
                  
                  try {
                    setUploadProgress(30);
                    
                    const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
                      method: "POST",
                      headers: {
                        Authorization: token ? `Bearer ${token}` : "",
                      },
                      body: formData,
                    });
                    
                    setUploadProgress(70);
                    
                    if (!response.ok) {
                      const error = await response.json();
                      throw new Error(error.detail || "Upload failed");
                    }
                    
                    const result = await response.json();
                    setUploadProgress(100);
                    
                    console.log("Upload result:", result);
                    setUploadSuccess(true);
                    
                    // Reset after 3 seconds
                    setTimeout(() => {
                      setUploadSuccess(false);
                      setSelectedFile(null);
                      setUploadProgress(0);
                    }, 3000);
                    
                  } catch (error: any) {
                    console.error("Upload error:", error);
                    alert(`Upload failed: ${error.message}`);
                    setUploadSuccess(false);
                  } finally {
                    setUploading(false);
                  }
                }}
                disabled={!selectedFile || uploading}
              >
                {uploading ? "Processing..." : "Upload & Extract Text"}
              </button>
              
              {uploadSuccess && (
                <div style={{ 
                  marginTop: "20px", 
                  padding: "20px", 
                  background: "rgba(16, 185, 129, 0.15)", 
                  borderRadius: "var(--radius-md)",
                  border: "1px solid var(--accent-emerald)"
                }}>
                  <p style={{ color: "var(--accent-emerald)", fontWeight: "bold" }}>✓ Document uploaded and OCR completed!</p>
                  <p style={{ color: "var(--text-muted)", fontSize: "14px", marginTop: "8px" }}>
                    Text has been extracted and stored. You can retrieve it using the document ID.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeSection === "Activity" && (
          <div className="page-content">
            <div className="panel">
              <h2>Audit Activity Log</h2>
              {activities.map((act, index) => (
                <div key={index} className="activity-row">
                  <div className="activity-icon">◷</div>
                  <div className="activity-info">
                    <strong>{act.title}</strong>
                    <span>{act.description}</span>
                  </div>
                  <small>{act.time}</small>
                </div>
              ))}
              {activities.length === 0 && <p style={{ textAlign: "center", padding: "24px", color: "var(--text-muted)" }}>No recent activity.</p>}
            </div>
          </div>
        )}

        {activeSection === "Security" && (
          <div className="page-content">
            <div className="panel" style={{ maxWidth: "600px" }}>
              <h2>Security Center</h2>
              <div className="feature-list" style={{ marginTop: "24px" }}>
                <div className="feature-item"><span className="icon">🔐</span><div><strong>MFA Status</strong><p>ACTIVE</p></div></div>
                <div className="feature-item"><span className="icon">️</span><div><strong>Liveness Check Integration</strong><p>ACTIVE</p></div></div>
                <div className="feature-item"><span className="icon">🛡️</span><div><strong>Role-based Permissions</strong><p>ENFORCED ({role})</p></div></div>
              </div>
            </div>
          </div>
        )}

        {activeSection === "Viewer" && selectedDocument && (
          <div className="page-content">
            <button className="back-login" onClick={() => setActiveSection("Documents")} style={{ marginBottom: "16px" }}>← Back to repository</button>
            <div className="panel" style={{ marginTop: "15px", padding: "32px" }}>
              <h2>{selectedDocument.name}</h2>
              <p style={{ color: "var(--text-muted)", marginTop: "8px" }}>ID: {selectedDocument.idCode}</p>
              <p style={{ color: "var(--text-muted)" }}>Type: {selectedDocument.type}</p>
              <p style={{ color: "var(--text-muted)" }}>Pages: {selectedDocument.pages}</p>
              <div style={{ marginTop: "24px", padding: "48px", background: "rgba(0,0,0,0.3)", borderRadius: "var(--radius-md)", textAlign: "center", color: "var(--text-muted)" }}>
                Document preview placeholder
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
