import { useState, useEffect, useRef } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import useWebSocket from "./hooks/useWebSocket";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Avatar, AvatarFallback } from "./components/ui/avatar";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { Label } from "./components/ui/label";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { 
  Calendar, CheckCircle, CheckSquare, Clock, MessageSquare, BookOpen, FlaskConical, 
  Users, BarChart3, PlusCircle, Settings, LogOut, Upload, Star, 
  FileText, DollarSign, Award, Bell, Camera, Download, Eye,
  Building2, UserCheck, UserMinus, Banknote, TrendingUp, FileImage, User, ClipboardCheck,
  MapPin, Phone, GraduationCap, CalendarDays, AlertTriangle,
  Edit, Trash2, BookMarked, FileBarChart, X, Check, Plus, Target
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Utility Functions
const getStatusColor = (status) => {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    overdue: 'bg-red-100 text-red-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    active: 'bg-green-100 text-green-800',
    closed: 'bg-gray-100 text-gray-800',
    deferred: 'bg-orange-100 text-orange-800',
    on_leave: 'bg-purple-100 text-purple-800',
    graduated: 'bg-blue-100 text-blue-800'
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
};

const getPriorityColor = (priority) => {
  const colors = {
    low: 'bg-gray-100 text-gray-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    urgent: 'bg-red-100 text-red-800'
  };
  return colors[priority] || 'bg-gray-100 text-gray-800';
};

const formatProgramType = (programType) => {
  const types = {
    msc_research: 'MSc (Research)',
    msc_coursework: 'MSc (Coursework)',
    phd_research: 'PhD (Research)',
    phd_coursework: 'PhD (Coursework)'
  };
  return types[programType] || programType;
};

const formatStudyStatus = (status) => {
  const statuses = {
    active: 'Active',
    deferred: 'Deferred',
    on_leave: 'On Leave',
    graduated: 'Graduated'
  };
  return statuses[status] || status;
};

// Auth Context
const AuthContext = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('userData');
    if (token && userData) {
      setUser(JSON.parse(userData));
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    setLoading(false);
  }, []);

  const login = (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('userData', JSON.stringify(userData));
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userData');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="animate-pulse text-xl">Loading...</div>
    </div>;
  }

  return (
    <div>
      {user ? (
        <Dashboard user={user} logout={logout} setUser={setUser} />
      ) : (
        <Auth login={login} />
      )}
    </div>
  );
};

// Enhanced Authentication Component with comprehensive fields
const Auth = ({ login }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    role: 'student',
    
    // Enhanced Student Information
    student_id: '',
    contact_number: '',
    nationality: '',
    citizenship: '',
    program_type: 'msc_research',
    field_of_study: '',
    department: '',
    faculty: '',
    institute: '',
    enrollment_date: '',
    expected_graduation_date: '',
    
    // Existing fields
    research_area: '',
    supervisor_email: '',
    lab_name: '',
    scopus_id: '',
    orcid_id: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : formData;

      const response = await axios.post(`${API}${endpoint}`, payload);
      login(response.data.access_token, response.data.user_data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="relative">
          {/* Logo positioned at top right corner */}
          <div className="absolute top-4 right-4 z-10">
            <img 
              src="https://customer-assets.emergentagent.com/job_gradtrack/artifacts/hsqx7kb3_H2O%20BLUE%20TRANS%202%202.png" 
              alt="H2O Hydrochemistry Lab" 
              className="h-12 w-auto" 
            />
          </div>
          
          <CardHeader className="text-center pt-16">
            <CardTitle className="text-2xl font-bold text-gray-900">
              Hydrochemistry Laboratory Management
            </CardTitle>
            <p className="text-gray-600 mt-2">
              {isLogin ? 'Sign in to your lab account' : 'Create your comprehensive lab profile'}
            </p>
          </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Basic Authentication Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                />
              </div>
              <div>
                <Label htmlFor="password">Password *</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                />
              </div>
            </div>
            
            {!isLogin && (
              <>
                {/* Personal Information */}
                <div className="border-t pt-4">
                  <h3 className="text-lg font-medium mb-4">Personal Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="full_name">Full Name *</Label>
                      <Input
                        id="full_name"
                        value={formData.full_name}
                        onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="role">Role *</Label>
                      <Select value={formData.role} onValueChange={(value) => setFormData({...formData, role: value})}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="student">Graduate Student</SelectItem>
                          <SelectItem value="supervisor">Supervisor</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>

                {formData.role === 'student' && (
                  <>
                    {/* Student Specific Information */}
                    <div className="border-t pt-4">
                      <h3 className="text-lg font-medium mb-4">Student Information</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="student_id">Student ID / Matric Number</Label>
                          <Input
                            id="student_id"
                            value={formData.student_id}
                            onChange={(e) => setFormData({...formData, student_id: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="contact_number">Contact Number</Label>
                          <Input
                            id="contact_number"
                            value={formData.contact_number}
                            onChange={(e) => setFormData({...formData, contact_number: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="nationality">Nationality</Label>
                          <Input
                            id="nationality"
                            value={formData.nationality}
                            onChange={(e) => setFormData({...formData, nationality: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="citizenship">Citizenship</Label>
                          <Input
                            id="citizenship"
                            value={formData.citizenship}
                            onChange={(e) => setFormData({...formData, citizenship: e.target.value})}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Academic Information */}
                    <div className="border-t pt-4">
                      <h3 className="text-lg font-medium mb-4">Academic Information</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="program_type">Program Type</Label>
                          <Select value={formData.program_type} onValueChange={(value) => setFormData({...formData, program_type: value})}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="msc_research">MSc (Research)</SelectItem>
                              <SelectItem value="msc_coursework">MSc (Coursework)</SelectItem>
                              <SelectItem value="phd_research">PhD (Research)</SelectItem>
                              <SelectItem value="phd_coursework">PhD (Coursework)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="field_of_study">Field of Study / Research Area</Label>
                          <Input
                            id="field_of_study"
                            value={formData.field_of_study}
                            onChange={(e) => setFormData({...formData, field_of_study: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="department">Department</Label>
                          <Input
                            id="department"
                            value={formData.department}
                            onChange={(e) => setFormData({...formData, department: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="faculty">Faculty</Label>
                          <Input
                            id="faculty"
                            value={formData.faculty}
                            onChange={(e) => setFormData({...formData, faculty: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="institute">Institute</Label>
                          <Input
                            id="institute"
                            value={formData.institute}
                            onChange={(e) => setFormData({...formData, institute: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="research_area">Research Area</Label>
                          <Input
                            id="research_area"
                            value={formData.research_area}
                            onChange={(e) => setFormData({...formData, research_area: e.target.value})}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Dates */}
                    <div className="border-t pt-4">
                      <h3 className="text-lg font-medium mb-4">Academic Timeline</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="enrollment_date">Enrollment Date</Label>
                          <Input
                            id="enrollment_date"
                            type="date"
                            value={formData.enrollment_date}
                            onChange={(e) => setFormData({...formData, enrollment_date: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="expected_graduation_date">Expected Graduation Date</Label>
                          <Input
                            id="expected_graduation_date"
                            type="date"
                            value={formData.expected_graduation_date}
                            onChange={(e) => setFormData({...formData, expected_graduation_date: e.target.value})}
                          />
                        </div>
                      </div>
                    </div>

                    {/* Supervisor Information */}
                    <div className="border-t pt-4">
                      <h3 className="text-lg font-medium mb-4">Supervisor Information</h3>
                      <div>
                        <Label htmlFor="supervisor_email">Supervisor Email</Label>
                        <Input
                          id="supervisor_email"
                          type="email"
                          value={formData.supervisor_email}
                          onChange={(e) => setFormData({...formData, supervisor_email: e.target.value})}
                        />
                      </div>
                    </div>
                  </>
                )}

                {formData.role === 'supervisor' && (
                  <>
                    {/* Supervisor Lab Information */}
                    <div className="border-t pt-4">
                      <h3 className="text-lg font-medium mb-4">Lab Information</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="lab_name">Lab Name</Label>
                          <Input
                            id="lab_name"
                            value={formData.lab_name}
                            onChange={(e) => setFormData({...formData, lab_name: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="department">Department</Label>
                          <Input
                            id="department"
                            value={formData.department}
                            onChange={(e) => setFormData({...formData, department: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="research_area">Research Area</Label>
                          <Input
                            id="research_area"
                            value={formData.research_area}
                            onChange={(e) => setFormData({...formData, research_area: e.target.value})}
                          />
                        </div>
                        <div>
                          <Label htmlFor="scopus_id">Scopus Author ID</Label>
                          <Input
                            id="scopus_id"
                            value={formData.scopus_id}
                            onChange={(e) => setFormData({...formData, scopus_id: e.target.value})}
                            placeholder="e.g., 22133247800"
                          />
                        </div>
                        <div>
                          <Label htmlFor="orcid_id">ORCID ID</Label>
                          <Input
                            id="orcid_id"
                            value={formData.orcid_id}
                            onChange={(e) => setFormData({...formData, orcid_id: e.target.value})}
                            placeholder="e.g., 0000-0000-0000-0000"
                          />
                        </div>
                      </div>
                    </div>
                  </>
                )}
              </>
            )}

            {error && <p className="text-red-500 text-sm">{error}</p>}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
            </Button>

            <p className="text-center text-sm">
              {isLogin ? "Don't have an account? " : 'Already have an account? '}
              <button
                type="button"
                className="text-blue-600 hover:underline"
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError('');
                }}
              >
                {isLogin ? 'Sign up' : 'Sign in'}
              </button>
            </p>
          </form>
        </CardContent>
        </Card>
        
        {/* Copyright Footer */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            © 2025 Research Lab Management System. All rights reserved.<br />
            Professor Dr Ahmad Zaharin Aris
          </p>
        </div>
      </div>
    </div>
  );
};

// Main Dashboard Component
const Dashboard = ({ user, logout, setUser }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [tasks, setTasks] = useState([]);
  const [researchLogs, setResearchLogs] = useState([]);
  const [studentLogStatus, setStudentLogStatus] = useState([]); // New state for student log status tracking
  const [activeGrants, setActiveGrants] = useState([]); // New state for active grants
  const [students, setStudents] = useState([]);
  const [stats, setStats] = useState({});
  const [bulletins, setBulletins] = useState([]);
  const [grants, setGrants] = useState([]);
  const [publications, setPublications] = useState([]);
  const [labSettings, setLabSettings] = useState({});
  const [meetings, setMeetings] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [milestones, setMilestones] = useState([]);
  const [menuSettings, setMenuSettings] = useState({
    tasks: true,
    research: true,
    meetings: true,
    publications: true,
    milestones: true,
    reminders: true,
    news: true,
    grants: true,
    students: true,
    admin: true
  });
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);

  // WebSocket for real-time updates
  const handleWebSocketMessage = (data) => {
    console.log('Received real-time update:', data);
    
    switch (data.type) {
      case 'research_log_updated':
        fetchResearchLogs();
        if (user.role === 'student') {
          fetchStudentLogStatus();
        }
        showNotification(data.data.action, `Research log ${data.data.action} by ${data.data.user_name || data.data.supervisor_name}`);
        break;
      case 'meeting_updated':
        fetchMeetings();
        showNotification('Meeting Update', `Meeting ${data.data.action}`);
        break;
      case 'milestone_updated':
        fetchMilestones();
        showNotification('Milestone Update', `Milestone ${data.data.action}`);
        break;
      case 'grant_updated':
        fetchGrants();
        fetchActiveGrants();
        showNotification('Grant Update', `Grant ${data.data.action}`);
        break;
      case 'publication_updated':
        fetchPublications();
        showNotification('Publications', `Publications synchronized (${data.data.publications_count} total)`);
        break;
      case 'user_updated':
        if (data.data.action === 'avatar_updated') {
          if (data.data.user_id === user.id) {
            setUser({ ...user, avatar_emoji: data.data.avatar_emoji });
          }
          showNotification('Avatar Updated', `${data.data.user_name} updated their avatar`);
        }
        break;
      case 'bulletin_updated':
        fetchBulletins();
        showNotification('Announcement', `Announcement ${data.data.action}`);
        break;
      case 'notification_created':
        setNotifications(prev => [data.data, ...prev]);
        showNotification(data.data.title, data.data.message);
        break;
      default:
        console.log('Unknown event type:', data.type);
    }
  };

  const { isConnected } = useWebSocket(user?.id, handleWebSocketMessage);

  const showNotification = (title, message) => {
    // Simple notification system - you can enhance this with toast libraries
    if (Notification.permission === 'granted') {
      new Notification(title, { body: message });
    }
  };

  // Request notification permission
  useEffect(() => {
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Individual fetch functions for real-time updates
  const fetchResearchLogs = async () => {
    try {
      const response = await axios.get(`${API}/research-logs`);
      setResearchLogs(response.data || []);
    } catch (error) {
      console.error('Error fetching research logs:', error);
    }
  };

  const fetchStudentLogStatus = async () => {
    if (user.role !== 'student') return;
    try {
      const response = await axios.get(`${API}/research-logs/student/status`);
      setStudentLogStatus(response.data?.logs || []);
    } catch (error) {
      console.error('Error fetching student log status:', error);
    }
  };

  const fetchGrants = async () => {
    try {
      const response = await axios.get(`${API}/grants`);
      setGrants(response.data || []);
    } catch (error) {
      console.error('Error fetching grants:', error);
    }
  };

  const fetchActiveGrants = async () => {
    try {
      const response = await axios.get(`${API}/grants/active`);
      setActiveGrants(response.data?.active_grants || []);
    } catch (error) {
      console.error('Error fetching active grants:', error);
    }
  };

  const fetchPublications = async () => {
    try {
      const response = await axios.get(`${API}/publications`);
      setPublications(response.data || []);
    } catch (error) {
      console.error('Error fetching publications:', error);
    }
  };

  const fetchBulletins = async () => {
    try {
      const response = await axios.get(`${API}/bulletins`);
      setBulletins(response.data || []);
    } catch (error) {
      console.error('Error fetching bulletins:', error);
    }
  };

  const fetchMeetings = async () => {
    try {
      const response = await axios.get(`${API}/meetings`);
      const filteredMeetings = (response.data || []).filter(meeting => {
        const meetingDate = new Date(meeting.meeting_date);
        const now = new Date();
        const diffDays = (now - meetingDate) / (1000 * 60 * 60 * 24);
        return diffDays < 7;
      });
      setMeetings(filteredMeetings);
    } catch (error) {
      console.error('Error fetching meetings:', error);
    }
  };

  const fetchMilestones = async () => {
    try {
      const response = await axios.get(`${API}/milestones`);
      setMilestones(response.data || []);
    } catch (error) {
      console.error('Error fetching milestones:', error);
    }
  };
    try {
      const apiCalls = [
        axios.get(`${API}/tasks`).catch(() => ({data: []})),
        axios.get(`${API}/research-logs`).catch(() => ({data: []})),
        axios.get(`${API}/dashboard/stats`).catch(() => ({data: {}})),
        axios.get(`${API}/bulletins`).catch(() => ({data: []})),
        axios.get(`${API}/grants`).catch(() => ({data: []})),
        axios.get(`${API}/publications`).catch(() => ({data: []})),
        axios.get(`${API}/lab/settings`).catch(() => ({data: {}})),
        axios.get(`${API}/meetings`).catch(() => ({data: []})),
        axios.get(`${API}/reminders`).catch(() => ({data: []})),
        axios.get(`${API}/milestones`).catch(() => ({data: []})),
        axios.get(`${API}/notes`).catch(() => ({data: []})),
        axios.get(`${API}/grants/active`).catch(() => ({data: {active_grants: [], cumulative_balance: 0}}))
      ];

      // Add student-specific API call for research log status tracking
      if (user.role === 'student') {
        apiCalls.push(axios.get(`${API}/research-logs/student/status`).catch(() => ({data: {logs: []}})));
      }

      const [
        tasksRes, logsRes, statsRes, bulletinsRes, grantsRes, 
        pubsRes, labRes, meetingsRes, remindersRes, milestonesRes, notesRes, activeGrantsRes, studentLogStatusRes
      ] = await Promise.all(apiCalls);

      setTasks(tasksRes.data || []);
      setResearchLogs(logsRes.data || []);
      setStats(statsRes.data || {});
      setBulletins(bulletinsRes.data || []);
      setGrants(grantsRes.data || []);
      setPublications(pubsRes.data || []);
      setLabSettings(labRes.data || {});
      setMilestones(milestonesRes.data || []);
      setActiveGrants(activeGrantsRes.data?.active_grants || []);
      
      // Set student log status if user is a student
      if (user.role === 'student' && studentLogStatusRes) {
        setStudentLogStatus(studentLogStatusRes.data?.logs || []);
      }
      
      // Auto-cleanup completed/past items
      const now = new Date();
      
      const filteredMeetings = (meetingsRes.data || []).filter(meeting => {
        const meetingDate = new Date(meeting.meeting_date);
        // Show upcoming meetings and meetings from the last 7 days
        const diffDays = (now - meetingDate) / (1000 * 60 * 60 * 24);
        return diffDays < 7; // Show meetings from last 7 days and future meetings
      });
      
      const filteredReminders = (remindersRes.data || []).filter(reminder => {
        if (reminder.is_completed) return false;
        const reminderDate = new Date(reminder.reminder_date);
        return reminderDate >= now;
      });
      
      const filteredTasks = (tasksRes.data || []).filter(task => {
        return task.status !== 'completed';
      });

      setMeetings(filteredMeetings);
      setReminders(filteredReminders);
      setTasks(filteredTasks);
      setNotes(notesRes.data || []);

      if (user.role === 'supervisor' || user.role === 'lab_manager') {
        const studentsRes = await axios.get(`${API}/students`);
        setStudents(studentsRes.data || []);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Helper functions
  async function syncScopusPublications() {
    try {
      const response = await axios.post(`${API}/publications/sync-scopus`);
      alert(response.data.message);
      fetchDashboardData();
    } catch (error) {
      alert('Error syncing publications: ' + (error.response?.data?.detail || error.message));
    }
  }

  async function generateReport(type) {
    try {
      const response = await axios.get(`${API}/reports/generate/${type}`);
      alert('PDF report generated successfully!');
      console.log('Report data:', response.data);
    } catch (error) {
      alert('Error generating report: ' + (error.response?.data?.detail || error.message));
    }
  }

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="animate-pulse text-xl">Loading dashboard...</div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Enhanced Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center min-w-0 flex-1">
              {labSettings.lab_logo ? (
                <img src={labSettings.lab_logo} alt="Lab Logo" className="h-8 w-8 sm:h-10 sm:w-10 rounded-full mr-2 sm:mr-3 flex-shrink-0" />
              ) : (
                <img 
                  src="https://customer-assets.emergentagent.com/job_gradtrack/artifacts/hsqx7kb3_H2O%20BLUE%20TRANS%202%202.png" 
                  alt="H2O Hydrochemistry Lab" 
                  className="h-8 w-auto sm:h-10 mr-2 sm:mr-3 flex-shrink-0" 
                />
              )}
              <div className="min-w-0 flex-1">
                <h1 className="text-sm sm:text-xl font-bold text-gray-900 truncate">
                  {labSettings.lab_name || user.lab_name || 'Hydrochemistry Laboratory'}
                </h1>
                <p className="text-xs text-gray-500 hidden sm:block">Advanced Research Management System</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 sm:space-x-4 flex-shrink-0">
              {/* Notifications */}
              <div className="relative">
                <Bell className="h-5 w-5 text-gray-600 cursor-pointer" onClick={() => setActiveTab('reminders')} />
                {reminders.filter(r => !r.is_completed).length > 0 && (
                  <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full text-xs text-white flex items-center justify-center">
                    {reminders.filter(r => !r.is_completed).length}
                  </span>
                )}
              </div>
              
              <Button variant="outline" size="sm" onClick={() => setActiveTab('profile')} className="hidden sm:flex">
                <User className="h-4 w-4" />
              </Button>
              <Avatar className="h-8 w-8 sm:h-10 sm:w-10 cursor-pointer flex-shrink-0" onClick={() => setActiveTab('profile')}>
                <AvatarFallback>
                  {user.full_name.split(' ').map(n => n[0]).join('')}
                </AvatarFallback>
              </Avatar>
              <div className="hidden sm:block">
                <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
                <p className="text-xs text-gray-500">
                  {user.role.replace('_', ' ').toUpperCase()}
                </p>
              </div>
              {(user.role === 'supervisor' || user.role === 'lab_manager' || user.role === 'admin') && (
                <Button 
                  onClick={() => setActiveTab('admin')}
                  className="bg-white text-black border border-gray-300 hover:bg-gray-100 hover:text-black px-3 py-2 rounded-md text-sm font-medium"
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Admin
                </Button>
              )}
              <Button 
                onClick={logout}
                className="bg-white text-black border border-gray-300 hover:bg-gray-100 hover:text-black px-3 py-2 rounded-md text-sm font-medium"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="flex justify-center w-full mb-6 sm:mb-8">
          <TabsList className="inline-flex h-12 items-center justify-center rounded-xl bg-white border border-gray-200 shadow-sm p-1 text-sm font-medium overflow-x-auto scrollbar-hide w-full max-w-7xl">
            <TabsTrigger value="dashboard" className="inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-2 text-sm ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-sm min-w-fit">
              <BarChart3 className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Dashboard</span>
            </TabsTrigger>
{menuSettings.tasks && <TabsTrigger value="tasks" className="inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-2 text-sm ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-sm min-w-fit">
              <CheckSquare className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Tasks</span>
            </TabsTrigger>}
{menuSettings.research && <TabsTrigger value="research" className="inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-2 text-sm ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-sm min-w-fit">
              <FlaskConical className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Research</span>
            </TabsTrigger>}
{menuSettings.meetings && <TabsTrigger value="meetings" className="inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-2 text-sm ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-sm min-w-fit">
              <Calendar className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Meetings</span>
            </TabsTrigger>}
{(user.role === 'supervisor' || user.role === 'lab_manager') && menuSettings.students && (
              <TabsTrigger value="students" className="inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-2 text-sm ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-sm min-w-fit">
                <Users className="h-4 w-4 sm:mr-2" />
                <span className="hidden sm:inline">Students</span>
              </TabsTrigger>
            )}
{menuSettings.publications && <TabsTrigger value="publications" className="inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-2 text-sm ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-sm min-w-fit">
              <BookOpen className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Publications</span>
            </TabsTrigger>}
{menuSettings.milestones && <TabsTrigger value="milestones" className="inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-2 text-sm ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-sm min-w-fit">
              <BookOpen className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Milestones</span>
            </TabsTrigger>}
{menuSettings.reminders && <TabsTrigger value="reminders" className="inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-2 text-sm ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-sm min-w-fit">
              <AlertTriangle className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Reminders</span>
            </TabsTrigger>}
{menuSettings.news && <TabsTrigger value="bulletins" className="inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-2 text-sm ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-sm min-w-fit">
              <Bell className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">News</span>
            </TabsTrigger>}
{menuSettings.grants && <TabsTrigger value="grants" className="inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-2 text-sm ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-sm min-w-fit">
              <DollarSign className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Grants</span>
            </TabsTrigger>}
            <TabsTrigger value="profile" className="inline-flex items-center justify-center whitespace-nowrap rounded-lg px-3 py-2 text-sm ring-offset-white transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-950 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[state=active]:bg-blue-600 data-[state=active]:text-white data-[state=active]:shadow-sm min-w-fit">
              <Settings className="h-4 w-4 sm:mr-2" />
              <span className="hidden sm:inline">Profile</span>
            </TabsTrigger>
          </TabsList>
        </div>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="mt-6">
            {/* Statistics Overview */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              {user.role === 'student' ? (
                <>
                  <StatCard icon={CheckCircle} title="Tasks" value={stats.total_tasks || 0} color="blue" />
                  <StatCard icon={Award} title="Completed" value={stats.completed_tasks || 0} color="green" />
                  <StatCard icon={Clock} title="Research Logs" value={stats.total_research_logs || 0} color="yellow" />
                  <StatCard 
                    icon={DollarSign} 
                    title="Active Grants Balance" 
                    value={`$${(stats.active_grants_balance || 0).toLocaleString()}`} 
                    color="purple" 
                  />
                </>
              ) : (
                <>
                  <StatCard icon={Users} title="Students" value={stats.total_students || 0} color="blue" />
                  <StatCard icon={CheckCircle} title="Tasks" value={stats.total_assigned_tasks || 0} color="purple" />
                  <StatCard icon={Award} title="Publications" value={stats.total_publications || 0} color="green" />
                  <StatCard 
                    icon={DollarSign} 
                    title="Active Grants Balance" 
                    value={`$${(stats.active_grants_balance || 0).toLocaleString()}`} 
                    color="yellow" 
                  />
                </>
              )}
            </div>

            {/* Student Notifications */}
            {user.role === 'student' && (
              <div className="mb-6">
                <Card className="border-l-4 border-l-blue-500">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Bell className="h-5 w-5" />
                      Notifications
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {/* Research Log Review Notifications */}
                      {researchLogs
                        .filter(log => log.student_id === user.id && log.review_status)
                        .slice(0, 3)
                        .map((log) => (
                          <div key={log.id} className={`p-3 rounded-lg ${
                            log.review_status === 'accepted' ? 'bg-green-50 border-green-200' :
                            log.review_status === 'revision' ? 'bg-yellow-50 border-yellow-200' :
                            'bg-red-50 border-red-200'
                          } border`}>
                            <div className="flex items-start gap-2">
                              {log.review_status === 'accepted' && <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />}
                              {log.review_status === 'revision' && <Clock className="h-4 w-4 text-yellow-600 mt-0.5" />}
                              {log.review_status === 'rejected' && <X className="h-4 w-4 text-red-600 mt-0.5" />}
                              <div className="flex-1">
                                <p className="font-medium text-sm">
                                  Research Log Review: "{log.title}"
                                </p>
                                <p className="text-xs text-gray-600 mb-1">
                                  {log.review_status === 'accepted' ? 'Your research log has been accepted!' :
                                   log.review_status === 'revision' ? 'Your research log needs revision' :
                                   'Your research log was not accepted'}
                                </p>
                                {log.review_feedback && (
                                  <p className="text-xs text-gray-700 bg-white/50 p-2 rounded">
                                    <strong>Feedback:</strong> {log.review_feedback}
                                  </p>
                                )}
                                <p className="text-xs text-gray-500 mt-1">
                                  Reviewed on {new Date(log.reviewed_at).toLocaleDateString()}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      
                      {/* Upcoming Reminders */}
                      {reminders
                        .filter(r => !r.is_completed && r.user_id === user.id)
                        .slice(0, 2)
                        .map((reminder) => (
                          <div key={reminder.id} className="p-3 rounded-lg bg-blue-50 border border-blue-200">
                            <div className="flex items-start gap-2">
                              <AlertTriangle className="h-4 w-4 text-blue-600 mt-0.5" />
                              <div className="flex-1">
                                <p className="font-medium text-sm">{reminder.title}</p>
                                <p className="text-xs text-gray-600">
                                  Due: {new Date(reminder.reminder_date).toLocaleDateString()}
                                </p>
                                {reminder.description && (
                                  <p className="text-xs text-gray-700 mt-1">{reminder.description}</p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      
                      {/* No notifications message */}
                      {researchLogs.filter(log => log.student_id === user.id && log.review_status).length === 0 &&
                       reminders.filter(r => !r.is_completed && r.user_id === user.id).length === 0 && (
                        <div className="text-center py-4">
                          <Bell className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                          <p className="text-gray-500 text-sm">No new notifications</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Student Research Log Status Tracking */}
            {user.role === 'student' && (
              <div className="mb-6">
                <Card className="border-l-4 border-l-green-500">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <ClipboardCheck className="h-5 w-5" />
                      My Research Log Submissions Status
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {studentLogStatus.length > 0 ? (
                        studentLogStatus.slice(0, 5).map((log) => (
                          <div key={log.id} className={`p-3 rounded-lg border ${
                            log.status === 'approved' ? 'bg-green-50 border-green-200' :
                            log.status === 'needs revision' ? 'bg-yellow-50 border-yellow-200' :
                            log.status === 'not accepted' ? 'bg-red-50 border-red-200' :
                            'bg-gray-50 border-gray-200'
                          }`}>
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-2">
                                  {log.status === 'approved' && <CheckCircle className="h-4 w-4 text-green-600" />}
                                  {log.status === 'needs revision' && <Clock className="h-4 w-4 text-yellow-600" />}
                                  {log.status === 'not accepted' && <X className="h-4 w-4 text-red-600" />}
                                  {log.status === 'pending' && <Clock className="h-4 w-4 text-gray-600" />}
                                  <p className="font-medium text-sm">{log.title}</p>
                                </div>
                                <div className="text-xs text-gray-600 mb-1">
                                  <span className="inline-block mr-3">Activity: {log.activity_type}</span>
                                  <span className="inline-block mr-3">
                                    Submitted: {new Date(log.submission_date).toLocaleDateString()}
                                  </span>
                                </div>
                                {log.review_feedback && (
                                  <p className="text-xs text-gray-700 bg-white/50 p-2 rounded mb-1">
                                    <strong>Feedback:</strong> {log.review_feedback}
                                  </p>
                                )}
                                {log.reviewed_at && (
                                  <p className="text-xs text-gray-500">
                                    Reviewed by {log.reviewer_name} on {new Date(log.reviewed_at).toLocaleDateString()}
                                  </p>
                                )}
                              </div>
                              <Badge className={
                                log.status === 'approved' ? 'bg-green-100 text-green-800' :
                                log.status === 'needs revision' ? 'bg-yellow-100 text-yellow-800' :
                                log.status === 'not accepted' ? 'bg-red-100 text-red-800' :
                                'bg-gray-100 text-gray-800'
                              }>
                                {log.status.charAt(0).toUpperCase() + log.status.slice(1)}
                              </Badge>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-4">
                          <ClipboardCheck className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                          <p className="text-gray-500 text-sm">No research logs submitted yet</p>
                        </div>
                      )}
                      {studentLogStatus.length > 5 && (
                        <div className="text-center pt-2 border-t">
                          <p className="text-xs text-gray-500">
                            Showing 5 of {studentLogStatus.length} research logs
                          </p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5" />
                    Latest Publications
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {publications.slice(0, 1).map((publication) => (
                    <div key={publication.id} className="py-2">
                      <div>
                        <p className="font-medium text-sm line-clamp-2">{publication.title}</p>
                        <p className="text-xs text-gray-600 mt-1">
                          {Array.isArray(publication.authors) ? publication.authors.join(', ') : publication.authors} • {publication.journal || publication.conference}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {publication.publication_year || new Date(publication.created_at).getFullYear()}
                        </p>
                        {publication.doi && (
                          <p className="text-xs text-blue-600 mt-1 truncate">
                            DOI: {publication.doi}
                          </p>
                        )}
                        {publication.scopus_id && (
                          <p className="text-xs text-purple-600 mt-1 truncate">
                            Scopus ID: {publication.scopus_id}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                  {publications.length === 0 && (
                    <p className="text-gray-500 text-sm">No publications yet</p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <DollarSign className="h-5 w-5" />
                    Active Grants
                    <Badge variant="outline" className="ml-auto">
                      {activeGrants.length} Active
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {/* Cumulative Balance Summary */}
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-green-800">Total Active Balance</p>
                        <p className="text-xs text-green-600">Remaining funds across all active grants</p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-green-800">
                          ${activeGrants.reduce((sum, grant) => sum + (grant.remaining_balance || 0), 0).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Active Grants List */}
                  {activeGrants.slice(0, 3).map((grant) => (
                    <div key={grant.id} className="py-2 border-b last:border-b-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-sm line-clamp-2">{grant.title}</p>
                          <p className="text-xs text-gray-600 mt-1">
                            {grant.funding_agency} • {grant.grant_type || 'Research Grant'}
                          </p>
                          <div className="flex items-center gap-4 mt-1">
                            <p className="text-xs text-green-600 font-medium">
                              Balance: ${(grant.remaining_balance || 0).toLocaleString()}
                            </p>
                            {grant.person_in_charge && (
                              <p className="text-xs text-blue-600">
                                PIC: {grant.person_in_charge}
                              </p>
                            )}
                          </div>
                        </div>
                        <Badge className="bg-green-100 text-green-800 ml-2" size="sm">
                          Active
                        </Badge>
                      </div>
                    </div>
                  ))}
                  {activeGrants.length === 0 && (
                    <div className="text-center py-4">
                      <DollarSign className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                      <p className="text-gray-500 text-sm">No active grants</p>
                    </div>
                  )}
                  {activeGrants.length > 3 && (
                    <div className="text-center pt-2 mt-2 border-t">
                      <p className="text-xs text-gray-500">
                        +{activeGrants.length - 3} more grants
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bell className="h-5 w-5" />
                    Recent Announcements
                    <Badge variant="outline" className="ml-auto">
                      {bulletins.filter(b => b.status === 'approved').length} Active
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  {bulletins
                    .filter(bulletin => bulletin.status === 'approved') // Only show approved announcements
                    .slice(0, 3)
                    .map((bulletin, index) => (
                    <div key={bulletin.id} className={`
                      flex items-start space-x-3 p-4 
                      ${index < bulletins.length - 1 ? 'border-b' : ''}
                      ${bulletin.is_highlight ? 'bg-yellow-50 border-l-4 border-yellow-400' : 'hover:bg-gray-50'}
                      transition-colors
                    `}>
                      {bulletin.is_highlight ? (
                        <Star className="h-4 w-4 text-yellow-500 mt-0.5 fill-current" />
                      ) : (
                        <Bell className="h-4 w-4 text-gray-600 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className={`font-medium text-sm ${bulletin.is_highlight ? 'text-yellow-900' : 'text-gray-900'}`}>
                              {bulletin.is_highlight && <span className="text-yellow-600">🌟 </span>}
                              {bulletin.title}
                            </h4>
                            <p className="text-xs text-gray-600 mt-1">{bulletin.category}</p>
                            {bulletin.is_highlight && (
                              <p className="text-xs text-yellow-700 mt-1 font-medium">Priority Announcement</p>
                            )}
                          </div>
                          <div className="flex flex-col items-end gap-1">
                            <Badge 
                              className={`${getStatusColor(bulletin.status)} text-xs`} 
                              size="sm"
                            >
                              {bulletin.status}
                            </Badge>
                            {bulletin.is_highlight && (
                              <Badge variant="secondary" size="sm" className="text-xs bg-yellow-100 text-yellow-800">
                                Highlight
                              </Badge>
                            )}
                          </div>
                        </div>
                        {bulletin.description && (
                          <p className="text-xs text-gray-600 mt-2 line-clamp-2">{bulletin.description.slice(0, 100)}...</p>
                        )}
                      </div>
                    </div>
                  ))}
                  {bulletins.filter(b => b.status === 'approved').length === 0 && (
                    <div className="p-4 text-center">
                      <Bell className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                      <p className="text-gray-500 text-sm">No approved announcements</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Tasks Tab */}
          <TabsContent value="tasks" className="mt-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Tasks Management</h2>
              {(user.role === 'supervisor' || user.role === 'lab_manager') && (
                <CreateTaskDialog students={students} onTaskCreated={fetchDashboardData} user={user} />
              )}
            </div>

            <div className="grid gap-6">
              {tasks.map((task) => (
                <TaskCard key={task.id} task={task} user={user} onTaskUpdated={fetchDashboardData} />
              ))}
              {tasks.length === 0 && (
                <Card>
                  <CardContent className="text-center py-12">
                    <CheckCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">
                      {user.role === 'student' 
                        ? 'No tasks assigned yet. Your supervisor will assign tasks soon.' 
                        : 'No tasks created yet. Create your first task to get started.'}
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Research Log Tab */}
          <TabsContent value="research" className="mt-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Research Activities</h2>
              {user.role === 'student' && (
                <CreateResearchLogDialog onLogCreated={fetchDashboardData} />
              )}
            </div>

            {/* Student Submission Status Tracking */}
            {user.role === 'student' && (
              <Card className="mb-6">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ClipboardCheck className="h-5 w-5" />
                    My Research Log Submissions Status
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {researchLogs
                      .filter(log => log.user_id === user.id || log.student_id === user.id)
                      .map((log) => (
                        <div key={log.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                          <div className="flex-1">
                            <h4 className="font-medium text-sm">{log.title}</h4>
                            <p className="text-xs text-gray-600">
                              Submitted: {new Date(log.date || log.created_at).toLocaleDateString()} • 
                              Type: {log.activity_type.replace('_', ' ')}
                            </p>
                          </div>
                          <div className="flex items-center gap-3">
                            {log.review_status ? (
                              <>
                                <Badge className={`${
                                  log.review_status === 'accepted' ? 'bg-green-100 text-green-800' :
                                  log.review_status === 'revision' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {log.review_status === 'accepted' ? '✓ Approved' :
                                   log.review_status === 'revision' ? '↻ Needs Revision' :
                                   '✗ Not Accepted'}
                                </Badge>
                                {log.review_feedback && (
                                  <div className="text-xs text-gray-500 max-w-xs truncate">
                                    "{log.review_feedback}"
                                  </div>
                                )}
                              </>
                            ) : (
                              <Badge className="bg-gray-100 text-gray-600">
                                ⏳ Pending Review
                              </Badge>
                            )}
                          </div>
                        </div>
                      ))}
                    {researchLogs.filter(log => log.user_id === user.id || log.student_id === user.id).length === 0 && (
                      <div className="text-center py-8">
                        <ClipboardCheck className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                        <p className="text-gray-500 text-sm">No research logs submitted yet</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="grid gap-6">
              {researchLogs
                .filter(log => {
                  // Students see only their own logs
                  if (user.role === 'student') {
                    return log.student_id === user.id;
                  }
                  // Supervisors, lab managers, and admins see all logs
                  return true;
                })
                .map((log) => (
                  <ResearchLogCard key={log.id} log={log} user={user} onLogUpdated={fetchDashboardData} />
                ))}
              {researchLogs.filter(log => user.role === 'student' ? log.student_id === user.id : true).length === 0 && (
                <Card>
                  <CardContent className="text-center py-12">
                    <FlaskConical className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">
                      {user.role === 'student' 
                        ? 'No research logs yet. Start documenting your research activities.' 
                        : 'No research logs from students yet.'}
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Meetings Tab */}
          <TabsContent value="meetings" className="mt-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Meetings & Schedule</h2>
              <CreateMeetingDialog students={students} onMeetingCreated={fetchDashboardData} user={user} />
            </div>

            <div className="grid gap-6">
              {meetings.map((meeting) => (
                <MeetingCard key={meeting.id} meeting={meeting} user={user} onMeetingUpdated={fetchDashboardData} />
              ))}
              {meetings.length === 0 && (
                <Card>
                  <CardContent className="text-center py-12">
                    <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No meetings scheduled yet.</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Publications Tab */}
          <TabsContent value="publications" className="mt-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Lab Publications</h2>
              <div className="flex gap-2">
                {user.role === 'supervisor' && user.scopus_id && (
                  <Button onClick={syncScopusPublications} variant="outline">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Sync Scopus
                  </Button>
                )}
                <Button onClick={() => generateReport('publications')} variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Export PDF
                </Button>
              </div>
            </div>

            <div className="space-y-6">
              {/* Scopus Publications Integration */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BookOpen className="h-5 w-5 text-blue-600" />
                    Hydrochemistry Laboratory Publications
                  </CardTitle>
                  <p className="text-sm text-gray-600">Live publications from Scopus database</p>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="w-full rounded-lg overflow-hidden bg-transparent">
                    <iframe 
                      src="https://hydrochemistry.github.io/scopus-publications/" 
                      width="100%" 
                      height="600px" 
                      style={{border:'none', background: 'transparent'}} 
                      allowTransparency="true"
                      className="w-full rounded-lg"
                    >
                    </iframe>
                  </div>
                </CardContent>
              </Card>
              
              {/* Local Publications Management */}
              <AllPublicationsView user={user} students={students} publications={publications} />
            </div>
          </TabsContent>

          {/* Milestones Tab */}
          <TabsContent value="milestones" className="mt-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Project Milestones</h2>
              {user.role === 'student' && (
                <CreateMilestoneDialog onMilestoneCreated={fetchDashboardData} />
              )}
            </div>

            <div className="grid gap-6">
              {milestones.map((milestone) => (
                <MilestoneCard key={milestone.id} milestone={milestone} user={user} onMilestoneUpdated={fetchDashboardData} />
              ))}
              {milestones.length === 0 && (
                <Card>
                  <CardContent className="text-center py-12">
                    <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">
                      {user.role === 'student' 
                        ? 'No milestones created yet. Start tracking your project progress.' 
                        : 'No student milestones to review yet.'}
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Students Tab */}
          {(user.role === 'supervisor' || user.role === 'lab_manager') && (
            <TabsContent value="students" className="mt-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Students Management</h2>
              </div>

              <div className="grid gap-6">
                {students.map((student) => (
                  <StudentManagementCard key={student.id} student={student} user={user} onStudentUpdated={fetchDashboardData} />
                ))}
                {students.length === 0 && (
                  <Card>
                    <CardContent className="text-center py-12">
                      <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No students assigned yet. Students can connect with you using your email during registration.</p>
                    </CardContent>
                  </Card>
                )}
              </div>
            </TabsContent>
          )}

          {/* Profile Tab - Comprehensive Student Profile */}
          <TabsContent value="profile" className="mt-6">
            <ComprehensiveStudentProfile 
              user={user} 
              setUser={setUser}
              meetings={meetings}
              reminders={reminders}
              notes={notes}
              labSettings={labSettings}
              onDataUpdated={fetchDashboardData}
            />
          </TabsContent>

          {/* Reminders Tab */}
          <TabsContent value="reminders" className="mt-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Reminders & Alerts</h2>
              <CreateReminderDialog students={students} onReminderCreated={fetchDashboardData} user={user} />
            </div>

            <div className="grid gap-6">
              {reminders.filter(r => !r.is_completed).map((reminder) => (
                <ReminderCard key={reminder.id} reminder={reminder} user={user} onReminderUpdated={fetchDashboardData} />
              ))}
              {reminders.filter(r => !r.is_completed).length === 0 && (
                <Card>
                  <CardContent className="text-center py-12">
                    <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No active reminders.</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Bulletins Tab */}
          <TabsContent value="bulletins" className="mt-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Lab News & Announcements</h2>
              <CreateBulletinDialog onBulletinCreated={fetchDashboardData} />
            </div>

            <div className="grid gap-6">
              {bulletins
                .filter(bulletin => {
                  // Students only see approved bulletins
                  if (user.role === 'student') {
                    return bulletin.status === 'approved';
                  }
                  // Supervisors, lab_managers, and admins see all bulletins
                  return true;
                })
                .map((bulletin) => (
                  <BulletinCard key={bulletin.id} bulletin={bulletin} user={user} onBulletinUpdated={fetchDashboardData} />
                ))}
                
              {/* Empty state for students when no approved bulletins */}
              {user.role === 'student' && bulletins.filter(b => b.status === 'approved').length === 0 && (
                <Card>
                  <CardContent className="text-center py-12">
                    <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500">No approved announcements available</p>
                    <p className="text-sm text-gray-400 mt-2">Check back later for new updates</p>
                  </CardContent>
                </Card>
              )}
              
              {/* Empty state for supervisors when no bulletins exist */}
              {user.role !== 'student' && bulletins.length === 0 && (
                <Card>
                  <CardContent className="text-center py-12">
                    <Bell className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500">No announcements posted yet</p>
                    <p className="text-sm text-gray-400 mt-2">Create your first announcement using the button above</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Grants Tab */}
          <TabsContent value="grants" className="mt-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Grant Management</h2>
              <div className="flex gap-2">
                {/* Grants Dashboard Summary */}
                <div className="flex gap-4 mr-6">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{grants.filter(g => g.status === 'active').length}</p>
                    <p className="text-xs text-gray-500">Active Grants</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">
                      ${grants.filter(g => g.status === 'active').reduce((sum, g) => sum + (g.total_amount || 0), 0).toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500">Active Value</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-orange-600">
                      ${grants.filter(g => g.status === 'active').reduce((sum, g) => sum + (g.remaining_balance || g.current_balance || 0), 0).toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500">Active Balance</p>
                  </div>
                </div>
                {(user.role === 'supervisor' || user.role === 'lab_manager' || user.role === 'admin') && (
                  <CreateGrantDialog students={students} onGrantCreated={fetchDashboardData} />
                )}
              </div>
            </div>

            {/* Active Grants Section - Priority Display */}
            {grants.filter(g => g.status === 'active').length > 0 && (
              <Card className="mb-6 border-l-4 border-l-green-500">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-700">
                    <TrendingUp className="h-5 w-5" />
                    Active Grants ({grants.filter(g => g.status === 'active').length})
                  </CardTitle>
                  <p className="text-sm text-gray-600">
                    Currently active grants available for all lab members to view and participate in
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4">
                    {grants
                      .filter(g => g.status === 'active')
                      .map((grant) => (
                        <GrantCard key={grant.id} grant={grant} user={user} onGrantUpdated={fetchDashboardData} />
                      ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* All Grants Section */}
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">All Grants</h3>
            </div>

            <div className="grid gap-6">
              {grants.length > 0 ? (
                grants.map((grant) => (
                  <GrantCard key={grant.id} grant={grant} user={user} onGrantUpdated={fetchDashboardData} />
                ))
              ) : (
                <Card className="text-center py-12">
                  <CardContent>
                    <DollarSign className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Grants Found</h3>
                    <p className="text-gray-500 mb-4">
                      No grants are currently available. Check back later for funding opportunities.
                    </p>
                    {(user.role === 'supervisor' || user.role === 'lab_manager' || user.role === 'admin') && (
                      <CreateGrantDialog students={students} onGrantCreated={fetchDashboardData} />
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Administrator Tab */}
          {(user.role === 'supervisor' || user.role === 'lab_manager' || user.role === 'admin') && (
            <TabsContent value="admin" className="mt-6">
              <AdminPanel user={user} labSettings={labSettings} onSettingsUpdated={fetchDashboardData} menuSettings={menuSettings} onMenuSettingsUpdated={setMenuSettings} />
            </TabsContent>
          )}
        </Tabs>
      </div>
      
      {/* Copyright Footer */}
      <div className="mt-12 pt-6 border-t border-gray-200">
        <p className="text-center text-sm text-gray-500">
          © 2025 Research Lab Management System. All rights reserved.<br />Professor Dr Ahmad Zaharin Aris
        </p>
      </div>
    </div>
  );
};

// Utility Components
const StatCard = ({ icon: Icon, title, value, color }) => (
  <Card>
    <CardContent className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className={`text-2xl font-bold text-${color}-600`}>{value}</p>
        </div>
        <Icon className={`h-8 w-8 text-${color}-600`} />
      </div>
    </CardContent>
  </Card>
);

// Password Change Form Component
const PasswordChangeForm = () => {
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [loading, setLoading] = useState(false);

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_password) {
      alert('New password and confirmation do not match');
      return;
    }
    
    setLoading(true);
    try {
      await axios.post(`${API}/auth/change-password`, {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      alert('Password changed successfully!');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      console.error('Error changing password:', error);
      alert(error.response?.data?.detail || 'Error changing password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
      <div>
        <Label htmlFor="current_password">Current Password *</Label>
        <Input
          id="current_password"
          type="password"
          value={passwordData.current_password}
          onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
          placeholder="Enter current password"
          required
        />
      </div>
      <div>
        <Label htmlFor="new_password">New Password *</Label>
        <Input
          id="new_password"
          type="password"
          value={passwordData.new_password}
          onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
          placeholder="Enter new password"
          required
        />
      </div>
      <div>
        <Label htmlFor="confirm_password">Confirm New Password *</Label>
        <Input
          id="confirm_password"
          type="password"
          value={passwordData.confirm_password}
          onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
          placeholder="Confirm new password"
          required
        />
      </div>
      <Button 
        type="submit" 
        disabled={loading || !passwordData.current_password || !passwordData.new_password}
        className="w-full"
      >
        {loading ? 'Changing...' : 'Change Password'}
      </Button>
    </form>
  );
};

// Comprehensive Student Profile Component
const ComprehensiveStudentProfile = ({ user, setUser, meetings, reminders, notes, labSettings, onDataUpdated }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchUserProfile();
  }, []);

  useEffect(() => {
    if (userProfile) {
      setFormData({
        full_name: userProfile.full_name || '',
        contact_number: userProfile.contact_number || '',
        student_id: userProfile.student_id || '',
        program_type: userProfile.program_type || '',
        study_status: userProfile.study_status || '',
        field_of_study: userProfile.field_of_study || '',
        department: userProfile.department || '',
        faculty: userProfile.faculty || '',
        institute: userProfile.institute || '',
        enrollment_date: userProfile.enrollment_date ? userProfile.enrollment_date.split('T')[0] : '',
        expected_graduation_date: userProfile.expected_graduation_date ? userProfile.expected_graduation_date.split('T')[0] : '',
        nationality: userProfile.nationality || '',
        citizenship: userProfile.citizenship || '',
        research_area: userProfile.research_area || '',
        lab_name: userProfile.lab_name || '',
        scopus_id: userProfile.scopus_id || '',
        orcid_id: userProfile.orcid_id || ''
      });
    }
  }, [userProfile]);

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get(`${API}/users/profile`);
      setUserProfile(response.data);
      setFormData(response.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
      setUserProfile(user);
      setFormData(user);
    }
  };

  const updateProfile = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/users/profile`, formData);
      setUserProfile(formData);
      setUser({ ...user, ...formData });
      setIsEditing(false);
      onDataUpdated();
      alert('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Error updating profile: ' + (typeof error.response?.data?.detail === 'string' ? error.response.data.detail : JSON.stringify(error.response?.data?.detail || error.message || 'Unknown error occurred')));
    } finally {
      setLoading(false);
    }
  };

  if (!userProfile) {
    return <div className="flex items-center justify-center p-8">
      <div className="animate-pulse">Loading profile...</div>
    </div>;
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Profile Header */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Avatar className="h-20 w-20">
                <AvatarFallback>
                  {userProfile.full_name.split(' ').map(n => n[0]).join('')}
                </AvatarFallback>
              </Avatar>
            </div>
            <div>
              <h1 className="text-2xl font-bold">{userProfile.full_name}</h1>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span className="flex items-center gap-1">
                  <User className="h-4 w-4" />
                  {userProfile.role.replace('_', ' ').toUpperCase()}
                </span>
                {userProfile.student_id && (
                  <span className="flex items-center gap-1">
                    <BookMarked className="h-4 w-4" />
                    {userProfile.student_id}
                  </span>
                )}
                {userProfile.study_status && (
                  <Badge className={getStatusColor(userProfile.study_status)}>
                    {formatStudyStatus(userProfile.study_status)}
                  </Badge>
                )}
              </div>
            </div>
          </div>
          <Button onClick={() => setIsEditing(!isEditing)}>
            <Edit className="h-4 w-4 mr-2" />
            {isEditing ? 'Cancel' : 'Edit Profile'}
          </Button>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <ProfileEditForm 
              formData={formData} 
              setFormData={setFormData} 
              loading={loading}
              onSave={updateProfile}
              onCancel={() => setIsEditing(false)}
              user={user}
              setUser={setUser}
            />
          ) : (
            <ProfileDisplayView userProfile={userProfile} />
          )}
        </CardContent>
      </Card>

      {/* Student Role Specific Content */}
      {userProfile.role === 'student' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Academic Progress */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GraduationCap className="h-5 w-5" />
                Academic Progress
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {userProfile.enrollment_date && userProfile.expected_graduation_date && (
                <div>
                  <Label>Program Timeline</Label>
                  <div className="flex items-center justify-between text-sm">
                    <span>Enrolled: {new Date(userProfile.enrollment_date).toLocaleDateString()}</span>
                    <span>Expected: {new Date(userProfile.expected_graduation_date).toLocaleDateString()}</span>
                  </div>
                  <Progress value={calculateProgressPercentage(userProfile.enrollment_date, userProfile.expected_graduation_date)} className="mt-2" />
                </div>
              )}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <Label>Program Type</Label>
                  <p className="text-gray-700">{formatProgramType(userProfile.program_type)}</p>
                </div>
                <div>
                  <Label>Field of Study</Label>
                  <p className="text-gray-700">{userProfile.field_of_study || 'Not specified'}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Supervisor Notes */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookMarked className="h-5 w-5" />
                Supervisor Notes
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {notes.filter(note => !note.is_private || userProfile.role !== 'student').map((note) => (
                  <div key={note.id} className="border-l-4 border-blue-500 pl-3 py-2">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-sm">{note.title}</h4>
                      <Badge variant="outline">{note.note_type.replace('_', ' ')}</Badge>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{note.content}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(note.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
                {notes.length === 0 && (
                  <p className="text-gray-500 text-sm">No supervisor notes yet.</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Meeting History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Meeting History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {meetings.slice(0, 10).map((meeting) => (
              <div key={meeting.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{meeting.agenda}</h4>
                  <div className="flex items-center gap-2">
                    <Badge className={getStatusColor(meeting.meeting_type)}>
                      {meeting.meeting_type.replace('_', ' ')}
                    </Badge>
                    <span className="text-sm text-gray-600">
                      {new Date(meeting.meeting_date).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                {meeting.meeting_notes && (
                  <p className="text-sm text-gray-700 mb-2">{meeting.meeting_notes}</p>
                )}
                {meeting.action_items && meeting.action_items.length > 0 && (
                  <div>
                    <Label className="text-xs">Action Items:</Label>
                    <ul className="list-disc list-inside text-sm text-gray-600">
                      {meeting.action_items.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
            {meetings.length === 0 && (
              <p className="text-gray-500 text-sm">No meetings recorded yet.</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Password Change Section - Available to All Users */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Change Password
          </CardTitle>
          <p className="text-sm text-gray-600">Update your account password for security</p>
        </CardHeader>
        <CardContent>
          <PasswordChangeForm />
        </CardContent>
      </Card>
      
      {/* Copyright Footer */}
      <div className="mt-8 pt-4 border-t border-gray-200">
        <p className="text-center text-sm text-gray-500">
          © 2025 Research Lab Management System. All rights reserved.<br />Professor Dr Ahmad Zaharin Aris
        </p>
      </div>
    </div>
  );
};

// Helper function to calculate progress percentage
const calculateProgressPercentage = (enrollmentDate, expectedGraduationDate) => {
  if (!enrollmentDate || !expectedGraduationDate) return 0;
  
  const start = new Date(enrollmentDate);
  const end = new Date(expectedGraduationDate);
  const now = new Date();
  
  const totalDuration = end.getTime() - start.getTime();
  const elapsed = now.getTime() - start.getTime();
  
  const percentage = Math.max(0, Math.min(100, (elapsed / totalDuration) * 100));
  return Math.round(percentage);
};

// Profile Display View Component
const ProfileDisplayView = ({ userProfile }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {/* Basic Information */}
    <div className="space-y-4">
      <h3 className="font-semibold text-lg border-b pb-2">Basic Information</h3>
      <div className="space-y-3">
        <div>
          <Label>Full Name</Label>
          <p className="text-gray-700">{userProfile.full_name}</p>
        </div>
        <div>
          <Label>Email</Label>
          <p className="text-gray-700">{userProfile.email}</p>
        </div>
        {userProfile.contact_number && (
          <div>
            <Label>Contact Number</Label>
            <p className="text-gray-700 flex items-center gap-1">
              <Phone className="h-4 w-4" />
              {userProfile.contact_number}
            </p>
          </div>
        )}
        {userProfile.nationality && (
          <div>
            <Label>Nationality</Label>
            <p className="text-gray-700 flex items-center gap-1">
              <MapPin className="h-4 w-4" />
              {userProfile.nationality}
            </p>
          </div>
        )}
        {userProfile.citizenship && (
          <div>
            <Label>Citizenship</Label>
            <p className="text-gray-700">{userProfile.citizenship}</p>
          </div>
        )}
      </div>
    </div>

    {/* Academic Information */}
    <div className="space-y-4">
      <h3 className="font-semibold text-lg border-b pb-2">Academic Information</h3>
      <div className="space-y-3">
        {userProfile.program_type && (
          <div>
            <Label>Program Type</Label>
            <p className="text-gray-700">{formatProgramType(userProfile.program_type)}</p>
          </div>
        )}
        <div>
          <Label>Department</Label>
          <p className="text-gray-700">{userProfile.department || 'Not specified'}</p>
        </div>
        {userProfile.faculty && (
          <div>
            <Label>Faculty</Label>
            <p className="text-gray-700">{userProfile.faculty}</p>
          </div>
        )}
        {userProfile.institute && (
          <div>
            <Label>Institute</Label>
            <p className="text-gray-700">{userProfile.institute}</p>
          </div>
        )}
        {userProfile.field_of_study && (
          <div>
            <Label>Field of Study</Label>
            <p className="text-gray-700">{userProfile.field_of_study}</p>
          </div>
        )}
        {userProfile.research_area && (
          <div>
            <Label>Research Area</Label>
            <p className="text-gray-700">{userProfile.research_area}</p>
          </div>
        )}
      </div>
    </div>

    {/* Timeline & Status */}
    <div className="space-y-4">
      <h3 className="font-semibold text-lg border-b pb-2">Timeline & Status</h3>
      <div className="space-y-3">
        {userProfile.enrollment_date && (
          <div>
            <Label>Enrollment Date</Label>
            <p className="text-gray-700 flex items-center gap-1">
              <CalendarDays className="h-4 w-4" />
              {new Date(userProfile.enrollment_date).toLocaleDateString()}
            </p>
          </div>
        )}
        {userProfile.expected_graduation_date && (
          <div>
            <Label>Expected Graduation</Label>
            <p className="text-gray-700 flex items-center gap-1">
              <GraduationCap className="h-4 w-4" />
              {new Date(userProfile.expected_graduation_date).toLocaleDateString()}
            </p>
          </div>
        )}
        <div>
          <Label>Study Status</Label>
          <div className="flex items-center gap-2">
            <Badge className={getStatusColor(userProfile.study_status)}>
              {formatStudyStatus(userProfile.study_status)}
            </Badge>
          </div>
        </div>
        {userProfile.scopus_id && (
          <div>
            <Label>Scopus ID</Label>
            <p className="text-gray-700">{userProfile.scopus_id}</p>
          </div>
        )}
        {userProfile.orcid_id && (
          <div>
            <Label>ORCID ID</Label>
            <p className="text-gray-700">{userProfile.orcid_id}</p>
          </div>
        )}
      </div>
    </div>
  </div>
);

// Profile Edit Form Component
const ProfileEditForm = ({ formData, setFormData, loading, onSave, onCancel, user, setUser }) => {
  return (
    <div className="space-y-6">
      {/* Basic Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="full_name">Full Name *</Label>
          <Input
            id="full_name"
            value={formData.full_name || ''}
            onChange={(e) => setFormData({...formData, full_name: e.target.value})}
            required
          />
        </div>
        <div>
          <Label htmlFor="contact_number">Contact Number</Label>
          <Input
            id="contact_number"
            type="tel"
            value={formData.contact_number || ''}
            onChange={(e) => setFormData({...formData, contact_number: e.target.value})}
          />
        </div>
      </div>

      {/* Supervisor Profile - Only Salutation */}
      {user?.role === 'supervisor' ? (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Supervisor Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="salutation">Salutation</Label>
              <Select value={formData.salutation || ''} onValueChange={(value) => setFormData({...formData, salutation: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select salutation" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="professor_dr">Professor Dr.</SelectItem>
                  <SelectItem value="dr">Dr.</SelectItem>
                  <SelectItem value="prof">Prof.</SelectItem>
                  <SelectItem value="assoc_prof_dr">Associate Professor Dr.</SelectItem>
                  <SelectItem value="asst_prof_dr">Assistant Professor Dr.</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      ) : (
        <>
        {/* Academic Information - Only for Students */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Academic Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="student_id">Student ID</Label>
              <Input
                id="student_id"
                value={formData.student_id || ''}
                onChange={(e) => setFormData({...formData, student_id: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="program_type">Program Type</Label>
              <Select value={formData.program_type || ''} onValueChange={(value) => setFormData({...formData, program_type: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select program" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="msc_research">MSc (Research)</SelectItem>
                  <SelectItem value="msc_coursework">MSc (Coursework)</SelectItem>
                  <SelectItem value="phd_research">PhD (Research)</SelectItem>
                  <SelectItem value="phd_coursework">PhD (Coursework)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="study_status">Study Status</Label>
              <Select value={formData.study_status || ''} onValueChange={(value) => setFormData({...formData, study_status: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="deferred">Deferred</SelectItem>
                  <SelectItem value="on_leave">On Leave</SelectItem>
                  <SelectItem value="graduated">Graduated</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="field_of_study">Field of Study</Label>
              <Input
                id="field_of_study"
                value={formData.field_of_study || ''}
                onChange={(e) => setFormData({...formData, field_of_study: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="department">Department</Label>
              <Input
                id="department"
                value={formData.department || ''}
                onChange={(e) => setFormData({...formData, department: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="faculty">Faculty</Label>
              <Input
                id="faculty"
                value={formData.faculty || ''}
                onChange={(e) => setFormData({...formData, faculty: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="institute">Institute</Label>
              <Input
                id="institute"
                value={formData.institute || ''}
                onChange={(e) => setFormData({...formData, institute: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="enrollment_date">Enrollment Date</Label>
              <Input
                id="enrollment_date"
                type="date"
                value={formData.enrollment_date ? formData.enrollment_date.split('T')[0] : ''}
                onChange={(e) => setFormData({...formData, enrollment_date: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="expected_graduation_date">Expected Graduation Date</Label>
              <Input
                id="expected_graduation_date"
                type="date"
                value={formData.expected_graduation_date ? formData.expected_graduation_date.split('T')[0] : ''}
                onChange={(e) => setFormData({...formData, expected_graduation_date: e.target.value})}
              />
            </div>
          </div>
        </div>

        {/* Personal Information - Only for Students */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Personal Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="nationality">Nationality</Label>
              <Input
                id="nationality"
                value={formData.nationality || ''}
                onChange={(e) => setFormData({...formData, nationality: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="citizenship">Citizenship</Label>
              <Input
                id="citizenship"
                value={formData.citizenship || ''}
                onChange={(e) => setFormData({...formData, citizenship: e.target.value})}
              />
            </div>
          </div>
        </div>

        {/* Research Information - Only for Students */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">Research Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="research_area">Research Area</Label>
              <Textarea
                id="research_area"
                value={formData.research_area || ''}
                onChange={(e) => setFormData({...formData, research_area: e.target.value})}
                rows={3}
              />
            </div>
            <div>
              <Label htmlFor="lab_name">Lab Name</Label>
              <Input
                id="lab_name"
                value={formData.lab_name || ''}
                onChange={(e) => setFormData({...formData, lab_name: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="scopus_id">Scopus ID</Label>
              <Input
                id="scopus_id"
                value={formData.scopus_id || ''}
                onChange={(e) => setFormData({...formData, scopus_id: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="orcid_id">ORCID ID</Label>
              <Input
                id="orcid_id"
                value={formData.orcid_id || ''}
                onChange={(e) => setFormData({...formData, orcid_id: e.target.value})}
              />
            </div>
          </div>
        </div>
        </>
      )}

    {/* Action Buttons */}
    <div className="flex justify-end gap-2 pt-4 border-t">
      <Button variant="outline" onClick={onCancel} disabled={loading}>
        Cancel
      </Button>
      <Button onClick={onSave} disabled={loading}>
        {loading ? 'Saving...' : 'Save Changes'}
      </Button>
    </div>
  </div>
);
}

const AllPublicationsView = ({ user, students, publications }) => (
  <div className="space-y-4">
    <h3 className="text-xl font-bold mb-4">All Lab Publications</h3>
    {publications.length === 0 ? (
      <Card>
        <CardContent className="text-center py-12">
          <Award className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No publications found. Sync with Scopus to import publications.</p>
        </CardContent>
      </Card>
    ) : (
      <div className="grid gap-4">
        {publications.map((pub, index) => (
          <Card key={index}>
            <CardContent className="p-4">
              <h4 className="font-semibold">{pub.title}</h4>
              <p className="text-sm text-gray-600">{pub.journal} • {pub.year}</p>
              <p className="text-sm text-gray-500">{pub.authors?.join(', ')}</p>
              {pub.doi && <p className="text-xs text-blue-600">DOI: {pub.doi}</p>}
              <div className="flex items-center justify-between mt-2">
                <span className="text-xs text-gray-500">Citations: {pub.citation_count || 0}</span>
                {pub.student_contributor_names && pub.student_contributor_names.length > 0 && (
                  <div className="flex gap-1">
                    {pub.student_contributor_names.map((name, i) => (
                      <Badge key={i} variant="outline" size="sm">{name}</Badge>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    )}
  </div>
);

// Task Card Component
const TaskCard = ({ task, user, onTaskUpdated }) => (
  <Card>
    <CardContent className="p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-semibold text-lg">{task.title}</h3>
          <p className="text-gray-600 mt-1">{task.description}</p>
          <p className="text-sm text-gray-500 mt-2">
            Due: {new Date(task.due_date).toLocaleDateString()}
          </p>
        </div>
        <div className="flex flex-col gap-2">
          <Badge className={getStatusColor(task.status)}>
            {task.status.replace('_', ' ')}
          </Badge>
          <Badge className={getPriorityColor(task.priority)}>
            {task.priority}
          </Badge>
        </div>
      </div>
      
      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span>Progress</span>
            <span>{task.progress_percentage}%</span>
          </div>
          <Progress value={task.progress_percentage} />
        </div>
        
        {task.supervisor_rating && (
          <div className="bg-green-50 p-3 rounded-lg">
            <div className="flex items-center gap-2">
              <Star className="h-4 w-4 text-yellow-500" />
              <span className="font-medium">Rating: {task.supervisor_rating}/5</span>
            </div>
            {task.supervisor_feedback && (
              <p className="text-sm text-gray-700 mt-2">{task.supervisor_feedback}</p>
            )}
          </div>
        )}
      </div>
    </CardContent>
  </Card>
);

// Research Log Card Component
const ResearchLogCard = ({ log, user, onLogUpdated }) => {
  const [showAttachments, setShowAttachments] = useState(false);
  const [reviewState, setReviewState] = useState('none'); // 'none', 'revision', 'rejection'
  const [reviewLoading, setReviewLoading] = useState(false);
  const [reviewFeedback, setReviewFeedback] = useState('');

  const handleReviewAction = async (action, feedback = '') => {
    setReviewLoading(true);
    try {
      const reviewData = {
        action: action, // 'accepted', 'revision', 'rejected'
        feedback: feedback,
        reviewed_by: user.id,
        reviewed_at: new Date().toISOString()
      };

      await axios.post(`${API}/research-logs/${log.id}/review`, reviewData);
      alert(`Research log ${action} successfully!`);
      onLogUpdated();
    } catch (error) {
      alert(`Error ${action}ing research log: ${error.response?.data?.detail || error.message}`);
    } finally {
      setReviewLoading(false);
      setReviewState('none');
      setReviewFeedback('');
    }
  };
  
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="font-semibold text-lg">{log.title}</h3>
            <div className="text-sm text-gray-600">
              <p>
                {new Date(log.date || log.created_at).toLocaleDateString()} • {log.activity_type.replace('_', ' ')}
                {log.duration_hours && ` • ${log.duration_hours}h`}
              </p>
              {/* Show student info for supervisors */}
              {user.role !== 'student' && (
                <div className="mt-1">
                  <p className="text-blue-600 font-medium">
                    <User className="h-4 w-4 inline mr-1" />
                    {log.student_name || 'Unknown Student'} 
                    <span className="text-gray-500 ml-2">ID: {log.student_id}</span>
                  </p>
                  {log.student_email && (
                    <p className="text-gray-500 text-xs">
                      {log.student_email}
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
          <Badge>{log.activity_type.replace('_', ' ')}</Badge>
        </div>
        
        <p className="text-gray-700 mb-4">{log.description}</p>
        
        {log.findings && (
          <div className="mb-3">
            <h4 className="font-medium text-green-700 mb-1">Key Findings:</h4>
            <p className="text-sm text-gray-700">{log.findings}</p>
          </div>
        )}
        
        {log.challenges && (
          <div className="mb-3">
            <h4 className="font-medium text-orange-700 mb-1">Challenges:</h4>
            <p className="text-sm text-gray-700">{log.challenges}</p>
          </div>
        )}
        
        {log.next_steps && (
          <div className="mb-3">
            <h4 className="font-medium text-blue-700 mb-1">Next Steps:</h4>
            <p className="text-sm text-gray-700">{log.next_steps}</p>
          </div>
        )}
        
        {log.tags && log.tags.length > 0 && (
          <div className="mb-3">
            <div className="flex flex-wrap gap-2">
              {log.tags.map((tag, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  #{tag}
                </Badge>
              ))}
            </div>
          </div>
        )}
        
        {/* Attachments Section */}
        {log.attachments && log.attachments.length > 0 && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-700">Attachments ({log.attachments.length})</h4>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setShowAttachments(!showAttachments)}
              >
                <Paperclip className="h-4 w-4 mr-1" />
                {showAttachments ? 'Hide' : 'Show'}
              </Button>
            </div>
            {showAttachments && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {log.attachments.map((attachment, index) => (
                  <div key={index} className="flex items-center gap-2 p-2 bg-white rounded border">
                    <FileText className="h-4 w-4 text-gray-500" />
                    <span className="text-sm truncate">{attachment.filename}</span>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => window.open(attachment.url, '_blank')}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        
        {/* Supervisor Review Status */}
        {log.review_status && (
          <div className={`p-3 rounded-lg mb-4 ${
            log.review_status === 'accepted' ? 'bg-green-50' : 
            log.review_status === 'revision' ? 'bg-yellow-50' : 
            'bg-red-50'
          }`}>
            <div className="flex items-center gap-2">
              {log.review_status === 'accepted' && <CheckCircle className="h-4 w-4 text-green-600" />}
              {log.review_status === 'revision' && <Clock className="h-4 w-4 text-yellow-600" />}
              {log.review_status === 'rejected' && <X className="h-4 w-4 text-red-600" />}
              <span className="font-medium">
                Status: {log.review_status === 'accepted' ? 'Accepted' : 
                         log.review_status === 'revision' ? 'Needs Revision' : 
                         'Not Accepted'}
              </span>
            </div>
            {log.review_feedback && (
              <p className="text-sm text-gray-700 mt-2">
                <strong>Feedback:</strong> {log.review_feedback}
              </p>
            )}
            {log.reviewed_by && log.reviewed_at && (
              <p className="text-xs text-gray-500 mt-1">
                Reviewed by {log.reviewer_name || 'Supervisor'} on {new Date(log.reviewed_at).toLocaleDateString()}
              </p>
            )}
          </div>
        )}
        
        {/* Supervisor Review Actions */}
        {(user.role === 'supervisor' || user.role === 'lab_manager' || user.role === 'admin') && 
         user.id !== log.student_id && !log.review_status && (
          <div className="border-t pt-4 mb-4">
            <h4 className="font-medium text-gray-700 mb-3">Supervisor Review</h4>
            {reviewState === 'none' ? (
              <div className="flex gap-2">
                <Button
                  onClick={() => handleReviewAction('accepted')}
                  disabled={reviewLoading}
                  className="bg-green-600 hover:bg-green-700 text-white"
                  size="sm"
                >
                  <Check className="h-4 w-4 mr-1" />
                  Accept
                </Button>
                <Button
                  onClick={() => setReviewState('revision')}
                  disabled={reviewLoading}
                  variant="outline"
                  size="sm"
                >
                  <Clock className="h-4 w-4 mr-1" />
                  Return for Revision
                </Button>
                <Button
                  onClick={() => setReviewState('rejection')}
                  disabled={reviewLoading}
                  variant="destructive"
                  size="sm"
                >
                  <X className="h-4 w-4 mr-1" />
                  Not Accept
                </Button>
              </div>
            ) : reviewState === 'revision' ? (
              <div className="space-y-3">
                <Textarea
                  placeholder="Provide feedback for revision..."
                  rows={3}
                  value={reviewFeedback}
                  onChange={(e) => setReviewFeedback(e.target.value)}
                />
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleReviewAction('revision', reviewFeedback)}
                    disabled={reviewLoading || !reviewFeedback.trim()}
                    size="sm"
                  >
                    {reviewLoading ? 'Submitting...' : 'Submit Revision Request'}
                  </Button>
                  <Button
                    onClick={() => setReviewState('none')}
                    disabled={reviewLoading}
                    variant="outline"
                    size="sm"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <Textarea
                  placeholder="Provide reason for not accepting this research log..."
                  rows={3}
                  value={reviewFeedback}
                  onChange={(e) => setReviewFeedback(e.target.value)}
                />
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleReviewAction('rejected', reviewFeedback)}
                    disabled={reviewLoading || !reviewFeedback.trim()}
                    variant="destructive"
                    size="sm"
                  >
                    {reviewLoading ? 'Submitting...' : 'Submit Rejection'}
                  </Button>
                  <Button
                    onClick={() => setReviewState('none')}
                    disabled={reviewLoading}
                    variant="outline"
                    size="sm"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
        
        {log.supervisor_endorsement !== null && (
          <div className={`p-3 rounded-lg ${log.supervisor_endorsement ? 'bg-green-50' : 'bg-red-50'}`}>
            <div className="flex items-center gap-2">
              <UserCheck className={`h-4 w-4 ${log.supervisor_endorsement ? 'text-green-600' : 'text-red-600'}`} />
              <span className="font-medium">
                {log.supervisor_endorsement ? 'Endorsed' : 'Needs Revision'}
                {log.supervisor_rating && ` (${log.supervisor_rating}/5)`}
              </span>
            </div>
          </div>
        )}
        
        {/* PDF Download Button */}
        <div className="flex justify-end mt-4 pt-4 border-t">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => window.open(`${API}/research-logs/${log.id}/pdf`, '_blank')}
          >
            <FileText className="h-4 w-4 mr-2" />
            Download PDF
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// Placeholder components for dialogs and other functionality
const CreateTaskDialog = ({ students, onTaskCreated, user }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    assigned_to: '',
    priority: 'medium',
    due_date: '',
    status: 'pending'
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/tasks`, {
        title: formData.title,
        description: formData.description,
        assigned_to: formData.assigned_to || user.id, // Use selected student or current user
        priority: formData.priority,
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : new Date(Date.now() + 7*24*60*60*1000).toISOString(), // Default to 7 days from now if not set
        tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()) : []
      });
      
      alert('Task created successfully!');
      setFormData({
        title: '',
        description: '',
        assigned_to: '',
        priority: 'medium',
        due_date: '',
        status: 'pending'
      });
      setIsOpen(false);
      onTaskCreated();
    } catch (error) {
      console.error('Error creating task:', error);
      alert('Error creating task: ' + (error.response?.data?.detail || error.message || 'Unknown error occurred'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <PlusCircle className="h-4 w-4 mr-2" />
          Create Task
        </Button>
      </DialogTrigger>
      <DialogContent className="w-[95vw] max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Task</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="title">Task Title *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              placeholder="Enter task title"
              required
            />
          </div>
          
          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Task description"
              rows={3}
            />
          </div>
          
          <div>
            <Label htmlFor="assigned_to">Assign To</Label>
            <Select value={formData.assigned_to} onValueChange={(value) => setFormData({...formData, assigned_to: value})}>
              <SelectTrigger>
                <SelectValue placeholder="Select student" />
              </SelectTrigger>
              <SelectContent>
                {students.map((student) => (
                  <SelectItem key={student.id} value={student.id}>
                    {student.full_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label htmlFor="priority">Priority</Label>
            <Select value={formData.priority} onValueChange={(value) => setFormData({...formData, priority: value})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label htmlFor="due_date">Due Date</Label>
            <Input
              id="due_date"
              type="date"
              value={formData.due_date}
              onChange={(e) => setFormData({...formData, due_date: e.target.value})}
            />
          </div>
          
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Task'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

const CreateResearchLogDialog = ({ onLogCreated }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    activity_type: 'experiment',
    description: '',
    findings: '',
    challenges: '',
    next_steps: '',
    duration_hours: '',
    tags: '',
    log_date: new Date().toISOString().split('T')[0],
    log_time: '09:00'
  });
  const [attachments, setAttachments] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    const validFiles = files.filter(file => {
      if (file.size > maxSize) {
        alert(`File ${file.name} is too large. Maximum size is 10MB.`);
        return false;
      }
      if (!allowedTypes.includes(file.type)) {
        alert(`File ${file.name} type not allowed. Allowed: images, PDF, text, Word documents.`);
        return false;
      }
      return true;
    });

    setAttachments(prev => [...prev, ...validFiles]);
  };

  const removeAttachment = (index) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Prepare the data for submission
      const submitData = {
        title: formData.title,
        activity_type: formData.activity_type,
        description: formData.description,
        findings: formData.findings,
        challenges: formData.challenges,
        next_steps: formData.next_steps,
        duration_hours: formData.duration_hours ? parseFloat(formData.duration_hours) : null,
        tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()) : [],
        log_date: formData.log_date,
        log_time: formData.log_time
      };
      
      // First create the research log
      const logResponse = await axios.post(`${API}/research-logs`, submitData);

      // Then upload attachments if any
      if (attachments.length > 0) {
        const uploadPromises = attachments.map(async (file) => {
          const fileFormData = new FormData();
          fileFormData.append('file', file);
          fileFormData.append('research_log_id', logResponse.data.id);
          
          return axios.post(`${API}/research-logs/attachments`, fileFormData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
        });

        await Promise.all(uploadPromises);
      }
      
      alert('Research log created successfully!');
      setFormData({
        title: '',
        activity_type: 'experiment',
        description: '',
        findings: '',
        challenges: '',
        next_steps: '',
        duration_hours: '',
        tags: '',
        log_date: new Date().toISOString().split('T')[0],
        log_time: '09:00'
      });
      setAttachments([]);
      setIsOpen(false);
      onLogCreated();
    } catch (error) {
      console.error('❌ Error creating research log:', error);
      console.error('❌ Error response:', error.response?.data);
      console.error('❌ Error message:', error.message);
      console.error('❌ Error code:', error.code);
      
      let errorMessage = 'Error creating research log: ';
      
      if (error.code === 'ERR_NETWORK') {
        errorMessage += 'Network connection failed. Please check your internet connection and try again.';
      } else if (error.response?.status === 401) {
        errorMessage += 'Authentication failed. Please log out and log back in.';
      } else if (error.response?.status === 403) {
        errorMessage += 'Permission denied. You may not have access to create research logs.';
      } else if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage += error.response.data.detail;
        } else {
          errorMessage += JSON.stringify(error.response.data.detail);
        }
      } else if (error.message) {
        errorMessage += error.message;
      } else {
        errorMessage += 'Unknown error occurred. Please try again.';
      }
      
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <PlusCircle className="h-4 w-4 mr-2" />
          Add Research Log
        </Button>
      </DialogTrigger>
      <DialogContent className="w-[95vw] max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create Research Log</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                placeholder="Research activity title"
              />
            </div>
            
            <div>
              <Label htmlFor="activity_type">Activity Type</Label>
              <Select value={formData.activity_type} onValueChange={(value) => setFormData({...formData, activity_type: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="experiment">Experiment</SelectItem>
                  <SelectItem value="literature_review">Literature Review</SelectItem>
                  <SelectItem value="data_collection">Data Collection</SelectItem>
                  <SelectItem value="meeting">Meeting</SelectItem>
                  <SelectItem value="writing">Writing</SelectItem>
                  <SelectItem value="analysis">Analysis</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div>
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Describe the research activity"
              rows={3}
            />
          </div>
          
          <div>
            <Label htmlFor="findings">Key Findings</Label>
            <Textarea
              id="findings"
              value={formData.findings}
              onChange={(e) => setFormData({...formData, findings: e.target.value})}
              placeholder="What did you discover or learn?"
              rows={2}
            />
          </div>
          
          <div>
            <Label htmlFor="challenges">Challenges Faced</Label>
            <Textarea
              id="challenges"
              value={formData.challenges}
              onChange={(e) => setFormData({...formData, challenges: e.target.value})}
              placeholder="Any difficulties or obstacles encountered"
              rows={2}
            />
          </div>
          
          <div>
            <Label htmlFor="next_steps">Next Steps</Label>
            <Textarea
              id="next_steps"
              value={formData.next_steps}
              onChange={(e) => setFormData({...formData, next_steps: e.target.value})}
              placeholder="What are the planned next actions?"
              rows={2}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="duration_hours">Duration (hours)</Label>
              <Input
                id="duration_hours"
                type="number"
                step="0.5"
                value={formData.duration_hours}
                onChange={(e) => setFormData({...formData, duration_hours: e.target.value})}
                placeholder="Time spent"
              />
            </div>
            
            <div>
              <Label htmlFor="log_date">Log Date *</Label>
              <Input
                id="log_date"
                type="date"
                value={formData.log_date}
                onChange={(e) => setFormData({...formData, log_date: e.target.value})}
              />
            </div>
            
            <div>
              <Label htmlFor="log_time">Log Time *</Label>
              <Select value={formData.log_time} onValueChange={(value) => setFormData({...formData, log_time: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select time" />
                </SelectTrigger>
                <SelectContent className="max-h-60 overflow-y-auto">
                  <SelectItem value="06:00">06:00</SelectItem>
                  <SelectItem value="06:30">06:30</SelectItem>
                  <SelectItem value="07:00">07:00</SelectItem>
                  <SelectItem value="07:30">07:30</SelectItem>
                  <SelectItem value="08:00">08:00</SelectItem>
                  <SelectItem value="08:30">08:30</SelectItem>
                  <SelectItem value="09:00">09:00</SelectItem>
                  <SelectItem value="09:30">09:30</SelectItem>
                  <SelectItem value="10:00">10:00</SelectItem>
                  <SelectItem value="10:30">10:30</SelectItem>
                  <SelectItem value="11:00">11:00</SelectItem>
                  <SelectItem value="11:30">11:30</SelectItem>
                  <SelectItem value="12:00">12:00</SelectItem>
                  <SelectItem value="12:30">12:30</SelectItem>
                  <SelectItem value="13:00">13:00</SelectItem>
                  <SelectItem value="13:30">13:30</SelectItem>
                  <SelectItem value="14:00">14:00</SelectItem>
                  <SelectItem value="14:30">14:30</SelectItem>
                  <SelectItem value="15:00">15:00</SelectItem>
                  <SelectItem value="15:30">15:30</SelectItem>
                  <SelectItem value="16:00">16:00</SelectItem>
                  <SelectItem value="16:30">16:30</SelectItem>
                  <SelectItem value="17:00">17:00</SelectItem>
                  <SelectItem value="17:30">17:30</SelectItem>
                  <SelectItem value="18:00">18:00</SelectItem>
                  <SelectItem value="18:30">18:30</SelectItem>
                  <SelectItem value="19:00">19:00</SelectItem>
                  <SelectItem value="19:30">19:30</SelectItem>
                  <SelectItem value="20:00">20:00</SelectItem>
                  <SelectItem value="20:30">20:30</SelectItem>
                  <SelectItem value="21:00">21:00</SelectItem>
                  <SelectItem value="21:30">21:30</SelectItem>
                  <SelectItem value="22:00">22:00</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div>
            <Label htmlFor="tags">Tags (comma-separated)</Label>
            <Input
              id="tags"
              value={formData.tags}
              onChange={(e) => setFormData({...formData, tags: e.target.value})}
              placeholder="machine learning, neural networks"
            />
          </div>
          
          {/* File Attachments Section */}
          <div className="space-y-4 border-t pt-4">
            <div>
              <Label>Research Attachments</Label>
              <p className="text-xs text-gray-500 mb-2">Upload images, documents, data files (Max 10MB each)</p>
              <div className="flex items-center gap-2">
                <input
                  type="file"
                  multiple
                  accept="image/*,.pdf,.txt,.doc,.docx"
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                />
                <button
                  type="button"
                  onClick={() => document.getElementById('file-upload').click()}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Add Files
                </button>
                <span className="text-xs text-gray-500">
                  Images, PDF, Word documents
                </span>
              </div>
            </div>
            
            {/* Display selected files */}
            {attachments.length > 0 && (
              <div className="space-y-2">
                <Label>Selected Files ({attachments.length})</Label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-32 overflow-y-auto">
                  {attachments.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded border">
                      <div className="flex items-center gap-2 min-w-0">
                        {file.type.startsWith('image/') ? (
                          <FileImage className="h-4 w-4 text-blue-600 flex-shrink-0" />
                        ) : (
                          <FileText className="h-4 w-4 text-gray-600 flex-shrink-0" />
                        )}
                        <div className="min-w-0">
                          <p className="text-sm font-medium truncate">{file.name}</p>
                          <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                        </div>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeAttachment(index)}
                        className="text-red-600 hover:text-red-800 flex-shrink-0"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Log'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

const CreateMeetingDialog = ({ students, onMeetingCreated, user }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    agenda: '',
    meeting_date: '',
    meeting_time: '09:00', // Default to 9:00 AM
    meeting_type: 'supervision',
    attendees: [],
    location: '',
    notes: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      
      // Create proper ISO datetime string
      const meetingDateTime = new Date(`${formData.meeting_date}T${formData.meeting_time}:00`);
      
      // Validate the date is valid
      if (isNaN(meetingDateTime.getTime())) {
        alert('Invalid date or time format. Please check your inputs.');
        setLoading(false);
        return;
      }
      
      await axios.post(`${API}/meetings`, {
        student_id: user.id,
        meeting_type: formData.meeting_type,
        meeting_date: meetingDateTime.toISOString(),
        agenda: formData.agenda,
        meeting_notes: formData.notes || undefined,
        duration_minutes: 60,
        location: formData.location || undefined
      });
      
      alert('Meeting scheduled successfully!');
      setFormData({
        agenda: '',
        meeting_date: '',
        meeting_time: '09:00',
        meeting_type: 'supervision',
        attendees: [],
        location: '',
        notes: ''
      });
      setIsOpen(false);
      onMeetingCreated();
    } catch (error) {
      console.error('Error scheduling meeting:', error);
      let errorMessage = 'Error scheduling meeting: ';
      
      if (error.response?.data?.detail) {
        errorMessage += error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage += error.response.data.message;
      } else if (error.message) {
        errorMessage += error.message;
      } else if (typeof error === 'string') {
        errorMessage += error;
      } else {
        errorMessage += 'Unknown error occurred. Please check all required fields.';
      }
      
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <PlusCircle className="h-4 w-4 mr-2" />
          Schedule Meeting
        </Button>
      </DialogTrigger>
      <DialogContent className="w-[95vw] max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Schedule New Meeting</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="agenda">Meeting Agenda *</Label>
            <Input
              id="agenda"
              value={formData.agenda}
              onChange={(e) => setFormData({...formData, agenda: e.target.value})}
              placeholder="Enter meeting agenda"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="meeting_date">Date *</Label>
              <Input
                id="meeting_date"
                type="date"
                value={formData.meeting_date}
                onChange={(e) => setFormData({...formData, meeting_date: e.target.value})}
                required
              />
            </div>
            <div>
              <Label htmlFor="meeting_time">Time *</Label>
              <Select value={formData.meeting_time} onValueChange={(value) => setFormData({...formData, meeting_time: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select time" />
                </SelectTrigger>
                <SelectContent className="max-h-60 overflow-y-auto">
                  <SelectItem value="06:00">06:00</SelectItem>
                  <SelectItem value="06:30">06:30</SelectItem>
                  <SelectItem value="07:00">07:00</SelectItem>
                  <SelectItem value="07:30">07:30</SelectItem>
                  <SelectItem value="08:00">08:00</SelectItem>
                  <SelectItem value="08:30">08:30</SelectItem>
                  <SelectItem value="09:00">09:00</SelectItem>
                  <SelectItem value="09:30">09:30</SelectItem>
                  <SelectItem value="10:00">10:00</SelectItem>
                  <SelectItem value="10:30">10:30</SelectItem>
                  <SelectItem value="11:00">11:00</SelectItem>
                  <SelectItem value="11:30">11:30</SelectItem>
                  <SelectItem value="12:00">12:00</SelectItem>
                  <SelectItem value="12:30">12:30</SelectItem>
                  <SelectItem value="13:00">13:00</SelectItem>
                  <SelectItem value="13:30">13:30</SelectItem>
                  <SelectItem value="14:00">14:00</SelectItem>
                  <SelectItem value="14:30">14:30</SelectItem>
                  <SelectItem value="15:00">15:00</SelectItem>
                  <SelectItem value="15:30">15:30</SelectItem>
                  <SelectItem value="16:00">16:00</SelectItem>
                  <SelectItem value="16:30">16:30</SelectItem>
                  <SelectItem value="17:00">17:00</SelectItem>
                  <SelectItem value="17:30">17:30</SelectItem>
                  <SelectItem value="18:00">18:00</SelectItem>
                  <SelectItem value="18:30">18:30</SelectItem>
                  <SelectItem value="19:00">19:00</SelectItem>
                  <SelectItem value="19:30">19:30</SelectItem>
                  <SelectItem value="20:00">20:00</SelectItem>
                  <SelectItem value="20:30">20:30</SelectItem>
                  <SelectItem value="21:00">21:00</SelectItem>
                  <SelectItem value="21:30">21:30</SelectItem>
                  <SelectItem value="22:00">22:00</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div>
            <Label htmlFor="meeting_type">Meeting Type</Label>
            <Select value={formData.meeting_type} onValueChange={(value) => setFormData({...formData, meeting_type: value})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="supervision">Supervision</SelectItem>
                <SelectItem value="progress_review">Progress Review</SelectItem>
                <SelectItem value="thesis_discussion">Thesis Discussion</SelectItem>
                <SelectItem value="general">General</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label htmlFor="location">Location</Label>
            <Input
              id="location"
              value={formData.location}
              onChange={(e) => setFormData({...formData, location: e.target.value})}
              placeholder="Meeting location or online link"
            />
          </div>
          
          <div>
            <Label htmlFor="notes">Additional Notes</Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              placeholder="Any additional information"
              rows={2}
            />
          </div>
          
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Scheduling...' : 'Schedule Meeting'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

const CreateReminderDialog = ({ students, onReminderCreated, user }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    reminder_date: '',
    reminder_time: '09:00', // Default to 9:00 AM
    priority: 'medium',
    assigned_to: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      
      // Create proper ISO datetime string with default values if needed
      const reminderDate = formData.reminder_date || new Date().toISOString().split('T')[0];
      const reminderTime = formData.reminder_time || '09:00';
      const reminderDateTime = new Date(`${reminderDate}T${reminderTime}:00`);
      
      await axios.post(`${API}/reminders`, {
        user_id: user.id,
        title: formData.title,
        description: formData.description || '',
        reminder_date: reminderDateTime.toISOString(),
        priority: formData.priority,
        reminder_type: 'general'
      });
      
      alert('Reminder added successfully!');
      setFormData({
        title: '',
        description: '',
        reminder_date: '',
        reminder_time: '09:00',
        priority: 'medium',
        assigned_to: ''
      });
      setIsOpen(false);
      onReminderCreated();
    } catch (error) {
      console.error('Error creating reminder:', error);
      let errorMessage = 'Error creating reminder: ';
      
      if (error.response?.data?.detail) {
        errorMessage += error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage += error.response.data.message;
      } else if (error.message) {
        errorMessage += error.message;
      } else if (typeof error === 'string') {
        errorMessage += error;
      } else {
        errorMessage += 'Unknown error occurred. Please check all required fields.';
      }
      
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <PlusCircle className="h-4 w-4 mr-2" />
          Add Reminder
        </Button>
      </DialogTrigger>
      <DialogContent className="w-[95vw] max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create Reminder</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="title">Reminder Title *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              placeholder="Enter reminder title"
            />
          </div>
          
          <div>
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Reminder details"
              rows={2}
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="reminder_date">Date *</Label>
              <Input
                id="reminder_date"
                type="date"
                value={formData.reminder_date}
                onChange={(e) => setFormData({...formData, reminder_date: e.target.value})}
                required
              />
            </div>
            <div>
              <Label htmlFor="reminder_time">Time *</Label>
              <Select value={formData.reminder_time} onValueChange={(value) => setFormData({...formData, reminder_time: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select time" />
                </SelectTrigger>
                <SelectContent className="max-h-60 overflow-y-auto">
                  <SelectItem value="06:00">06:00</SelectItem>
                  <SelectItem value="06:30">06:30</SelectItem>
                  <SelectItem value="07:00">07:00</SelectItem>
                  <SelectItem value="07:30">07:30</SelectItem>
                  <SelectItem value="08:00">08:00</SelectItem>
                  <SelectItem value="08:30">08:30</SelectItem>
                  <SelectItem value="09:00">09:00</SelectItem>
                  <SelectItem value="09:30">09:30</SelectItem>
                  <SelectItem value="10:00">10:00</SelectItem>
                  <SelectItem value="10:30">10:30</SelectItem>
                  <SelectItem value="11:00">11:00</SelectItem>
                  <SelectItem value="11:30">11:30</SelectItem>
                  <SelectItem value="12:00">12:00</SelectItem>
                  <SelectItem value="12:30">12:30</SelectItem>
                  <SelectItem value="13:00">13:00</SelectItem>
                  <SelectItem value="13:30">13:30</SelectItem>
                  <SelectItem value="14:00">14:00</SelectItem>
                  <SelectItem value="14:30">14:30</SelectItem>
                  <SelectItem value="15:00">15:00</SelectItem>
                  <SelectItem value="15:30">15:30</SelectItem>
                  <SelectItem value="16:00">16:00</SelectItem>
                  <SelectItem value="16:30">16:30</SelectItem>
                  <SelectItem value="17:00">17:00</SelectItem>
                  <SelectItem value="17:30">17:30</SelectItem>
                  <SelectItem value="18:00">18:00</SelectItem>
                  <SelectItem value="18:30">18:30</SelectItem>
                  <SelectItem value="19:00">19:00</SelectItem>
                  <SelectItem value="19:30">19:30</SelectItem>
                  <SelectItem value="20:00">20:00</SelectItem>
                  <SelectItem value="20:30">20:30</SelectItem>
                  <SelectItem value="21:00">21:00</SelectItem>
                  <SelectItem value="21:30">21:30</SelectItem>
                  <SelectItem value="22:00">22:00</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div>
            <Label htmlFor="priority">Priority</Label>
            <Select value={formData.priority} onValueChange={(value) => setFormData({...formData, priority: value})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <Label htmlFor="assigned_to">Assign To (Optional)</Label>
            <Select value={formData.assigned_to} onValueChange={(value) => setFormData({...formData, assigned_to: value})}>
              <SelectTrigger>
                <SelectValue placeholder="Select student (optional)" />
              </SelectTrigger>
              <SelectContent>
                {students.map((student) => (
                  <SelectItem key={student.id} value={student.id}>
                    {student.full_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Reminder'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

const CreateBulletinDialog = ({ onBulletinCreated }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: 'announcement',
    is_highlight: false
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/bulletins`, formData);
      
      alert('Announcement posted successfully!');
      setFormData({
        title: '',
        content: '',
        category: 'announcement',
        is_highlight: false
      });
      setIsOpen(false);
      onBulletinCreated();
    } catch (error) {
      console.error('Error creating bulletin:', error);
      let errorMessage = 'Error posting announcement: ';
      
      if (error.code === 'ERR_NETWORK') {
        errorMessage += 'Network connection failed. Please check your internet connection and try again.';
      } else if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage += error.response.data.detail;
        } else {
          errorMessage += JSON.stringify(error.response.data.detail);
        }
      } else if (error.response?.data?.message) {
        errorMessage += error.response.data.message;
      } else if (error.message) {
        errorMessage += error.message;
      } else {
        errorMessage += 'Unknown error occurred. Please try again.';
      }
      
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <PlusCircle className="h-4 w-4 mr-2" />
          Post Announcement
        </Button>
      </DialogTrigger>
      <DialogContent className="w-[95vw] max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create Announcement</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              placeholder="Announcement title"
            />
          </div>
          
          <div>
            <Label htmlFor="content">Content *</Label>
            <Textarea
              id="content"
              value={formData.content}
              onChange={(e) => setFormData({...formData, content: e.target.value})}
              placeholder="Write your announcement..."
              rows={4}
            />
          </div>
          
          <div>
            <Label htmlFor="category">Category</Label>
            <Select value={formData.category} onValueChange={(value) => setFormData({...formData, category: value})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="announcement">Announcement</SelectItem>
                <SelectItem value="event">Event</SelectItem>
                <SelectItem value="deadline">Deadline</SelectItem>
                <SelectItem value="news">News</SelectItem>
                <SelectItem value="update">Update</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is_highlight"
              checked={formData.is_highlight}
              onChange={(e) => setFormData({...formData, is_highlight: e.target.checked})}
              className="rounded"
            />
            <Label htmlFor="is_highlight" className="text-sm">
              Mark as priority highlight (⭐ Featured on dashboard)
            </Label>
          </div>
          
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Publishing...' : 'Post Announcement'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

const CreateGrantDialog = ({ students, onGrantCreated }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    funding_agency: '',
    total_amount: '',
    duration_months: '',
    grant_type: 'research',
    description: '',
    start_date: '',
    end_date: '',
    status: 'active',
    person_in_charge: '',
    grant_vote_number: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/grants`, {
        ...formData,
        total_amount: parseFloat(formData.total_amount) || 0,
        duration_months: parseInt(formData.duration_months) || 0,
        remaining_balance: parseFloat(formData.total_amount) || 0,
        start_date: formData.start_date ? new Date(formData.start_date).toISOString() : null,
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null
      });
      
      alert('Grant created successfully!');
      setFormData({
        title: '',
        funding_agency: '',
        total_amount: '',
        duration_months: '',
        grant_type: 'research',
        description: '',
        start_date: '',
        end_date: '',
        status: 'active',
        person_in_charge: '',
        grant_vote_number: ''
      });
      setIsOpen(false);
      onGrantCreated();
    } catch (error) {
      console.error('Error creating grant:', error);
      alert('Error creating grant: ' + (error.response?.data?.detail || error.message || 'Unknown error occurred'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <PlusCircle className="h-4 w-4 mr-2" />
          Add Grant
        </Button>
      </DialogTrigger>
      <DialogContent className="w-[95vw] max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Grant</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="title">Grant Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                placeholder="Enter grant title"
              />
            </div>
            
            <div>
              <Label htmlFor="funding_agency">Funding Agency *</Label>
              <Input
                id="funding_agency"
                value={formData.funding_agency}
                onChange={(e) => setFormData({...formData, funding_agency: e.target.value})}
                placeholder="e.g., NSF, NIH, University Research Board"
                required
              />
            </div>
          </div>
          
          {/* Financial Information */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="total_amount">Total Amount ($) *</Label>
              <Input
                id="total_amount"
                type="number"
                step="0.01"
                min="0"
                value={formData.total_amount}
                onChange={(e) => setFormData({...formData, total_amount: e.target.value})}
                placeholder="0.00"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="duration_months">Duration (Months) *</Label>
              <Input
                id="duration_months"
                type="number"
                min="1"
                value={formData.duration_months}
                onChange={(e) => setFormData({...formData, duration_months: e.target.value})}
                placeholder="12"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="grant_type">Grant Type</Label>
              <Select value={formData.grant_type} onValueChange={(value) => setFormData({...formData, grant_type: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="research">Research Grant</SelectItem>
                  <SelectItem value="equipment">Equipment Grant</SelectItem>
                  <SelectItem value="travel">Travel Grant</SelectItem>
                  <SelectItem value="conference">Conference Grant</SelectItem>
                  <SelectItem value="fellowship">Fellowship</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          {/* Timeline */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="start_date">Start Date *</Label>
              <Input
                id="start_date"
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                required
              />
            </div>
            
            <div>
              <Label htmlFor="end_date">End Date *</Label>
              <Input
                id="end_date"
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData({...formData, end_date: e.target.value})}
                required
              />
            </div>
          </div>
          
          {/* Description */}
          <div>
            <Label htmlFor="description">Grant Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Describe the grant objectives, scope, and expected outcomes..."
              rows={4}
            />
          </div>
          
          {/* Status */}
          <div>
            <Label htmlFor="status">Initial Status</Label>
            <Select value={formData.status} onValueChange={(value) => setFormData({...formData, status: value})}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="pending">Pending Approval</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="suspended">Suspended</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          {/* Management Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="person_in_charge">Person in Charge (PIC)</Label>
              <Select value={formData.person_in_charge} onValueChange={(value) => setFormData({...formData, person_in_charge: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a student as PIC" />
                </SelectTrigger>
                <SelectContent>
                  {students.map((student) => (
                    <SelectItem key={student.id} value={student.id}>
                      {student.full_name} - {student.email}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="grant_vote_number">Grant Vote Number</Label>
              <Input
                id="grant_vote_number"
                value={formData.grant_vote_number}
                onChange={(e) => setFormData({...formData, grant_vote_number: e.target.value})}
                placeholder="e.g., GV-2024-001"
              />
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" variant="outline" onClick={() => setIsOpen(false)} disabled={loading}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Grant'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

const EditGrantDialog = ({ grant, onGrantUpdated, isPIC = false }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: grant.title || '',
    funding_agency: grant.funding_agency || '',
    total_amount: grant.total_amount || '',
    current_balance: grant.current_balance || grant.total_amount || '',
    duration_months: grant.duration_months || '',
    grant_type: grant.grant_type || 'research',
    status: grant.status || 'active',
    person_in_charge: grant.person_in_charge || '',
    grant_vote_number: grant.grant_vote_number || '',
    start_date: grant.start_date ? grant.start_date.split('T')[0] : '',
    end_date: grant.end_date ? grant.end_date.split('T')[0] : '',
    description: grant.description || ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      console.log('🔍 Updating grant with data:', formData);
      
      const updateData = {
        ...formData,
        total_amount: parseFloat(formData.total_amount) || 0,
        current_balance: parseFloat(formData.current_balance) || 0,
        duration_months: parseInt(formData.duration_months) || 0,
        start_date: formData.start_date ? new Date(formData.start_date).toISOString() : null,
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null
      };
      
      await axios.put(`${API}/grants/${grant.id}`, updateData);
      
      alert('Grant updated successfully!');
      setIsOpen(false);
      onGrantUpdated();
    } catch (error) {
      console.error('Error updating grant:', error);
      let errorMessage = 'Error updating grant: ';
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage += error.response.data.detail;
        } else {
          errorMessage += JSON.stringify(error.response.data.detail);
        }
      } else if (error.message) {
        errorMessage += error.message;
      } else {
        errorMessage += 'Unknown error occurred';
      }
      
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Edit className="h-4 w-4 mr-2" />
          {isPIC ? 'Update Status' : 'Edit Grant'}
        </Button>
      </DialogTrigger>
      <DialogContent className="w-[95vw] max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {isPIC ? `Update Grant Status: ${grant.title}` : `Edit Grant: ${grant.title}`}
          </DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          
          {/* PIC Mode - Limited Fields */}
          {isPIC ? (
            <>
              <div>
                <Label htmlFor="status">Grant Status *</Label>
                <Select 
                  value={formData.status} 
                  onValueChange={(value) => setFormData({...formData, status: value})}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="on_hold">On Hold</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="current_balance">Current Balance *</Label>
                <Input
                  id="current_balance"
                  type="number"
                  step="0.01"
                  value={formData.current_balance}
                  onChange={(e) => setFormData({...formData, current_balance: e.target.value})}
                  placeholder="Enter current remaining balance"
                />
              </div>

              <div>
                <Label htmlFor="description">Progress Notes</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  placeholder="Update progress notes and status details..."
                  rows={4}
                />
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Updating...' : 'Update Grant Status'}
              </Button>
            </>
          ) : (
            <>
          {/* Full Edit Mode - All Fields */}
          <div>
            <Label htmlFor="title">Grant Title *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              placeholder="Enter grant title"
            />
          </div>
          
          <div>
            <Label htmlFor="funding_agency">Funding Agency *</Label>
            <Input
              id="funding_agency"
              value={formData.funding_agency}
              onChange={(e) => setFormData({...formData, funding_agency: e.target.value})}
              placeholder="e.g., NSF, NIH, DARPA"
              required
            />
          </div>
          
          {/* Financial Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="total_amount">Total Amount ($) *</Label>
              <Input
                id="total_amount"
                type="number"
                step="0.01"
                min="0"
                value={formData.total_amount}
                onChange={(e) => setFormData({...formData, total_amount: e.target.value})}
                placeholder="0.00"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="current_balance">Current Balance ($) *</Label>
              <Input
                id="current_balance"
                type="number"
                step="0.01"
                min="0"
                max={formData.total_amount}
                value={formData.current_balance}
                onChange={(e) => setFormData({...formData, current_balance: e.target.value})}
                placeholder="Current remaining balance"
                required
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="duration_months">Duration (Months) *</Label>
              <Input
                id="duration_months"
                type="number"
                min="1"
                value={formData.duration_months}
                onChange={(e) => setFormData({...formData, duration_months: e.target.value})}
                placeholder="12"
                required
              />
            </div>
            
            <div>
              <Label htmlFor="grant_type">Grant Type</Label>
              <Select value={formData.grant_type} onValueChange={(value) => setFormData({...formData, grant_type: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="research">Research Grant</SelectItem>
                  <SelectItem value="equipment">Equipment Grant</SelectItem>
                  <SelectItem value="travel">Travel Grant</SelectItem>
                  <SelectItem value="conference">Conference Grant</SelectItem>
                  <SelectItem value="fellowship">Fellowship</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="status">Status</Label>
              <Select value={formData.status} onValueChange={(value) => setFormData({...formData, status: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="pending">Pending Approval</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="suspended">Suspended</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          {/* Timeline */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="start_date">Start Date</Label>
              <Input
                id="start_date"
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({...formData, start_date: e.target.value})}
              />
            </div>
            
            <div>
              <Label htmlFor="end_date">End Date</Label>
              <Input
                id="end_date"
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData({...formData, end_date: e.target.value})}
              />
            </div>
          </div>
          
          {/* Description */}
          <div>
            <Label htmlFor="description">Grant Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Describe the grant objectives, scope, and expected outcomes..."
              rows={4}
            />
          </div>
          
          {/* Management Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="person_in_charge">Person in Charge (PIC)</Label>
              <Input
                id="person_in_charge"
                value={formData.person_in_charge}
                onChange={(e) => setFormData({...formData, person_in_charge: e.target.value})}
                placeholder="Name of responsible person"
              />
            </div>
            
            <div>
              <Label htmlFor="grant_vote_number">Grant Vote Number</Label>
              <Input
                id="grant_vote_number"
                value={formData.grant_vote_number}
                onChange={(e) => setFormData({...formData, grant_vote_number: e.target.value})}
                placeholder="e.g., GV-2024-001"
              />
            </div>
          </div>
          
          {/* Action Buttons */}
          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" variant="outline" onClick={() => setIsOpen(false)} disabled={loading}>
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={loading || !formData.title || !formData.funding_agency}
            >
              {loading ? 'Updating...' : 'Update Grant'}
            </Button>
          </div>
          </>
          )}
        </form>
      </DialogContent>
    </Dialog>
  );
}

// Scopus Publication Dialog Component
const ScopusPublicationDialog = ({ onPublicationAdded }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [scopusId, setScopusId] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!scopusId.trim()) {
      alert('Please enter a Scopus ID');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/publications/scopus`, {
        scopus_id: scopusId.trim()
      });
      
      alert('Publication added successfully from Scopus!');
      setScopusId('');
      setIsOpen(false);
      onPublicationAdded();
    } catch (error) {
      console.error('Error adding publication:', error);
      alert('Error adding publication: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="w-full">
          <Plus className="h-3 w-3 mr-1" />
          Add from Scopus
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Publication from Scopus</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="scopus_id">Scopus ID</Label>
            <Input
              id="scopus_id"
              value={scopusId}
              onChange={(e) => setScopusId(e.target.value)}
              placeholder="Enter Scopus ID (e.g., 2-s2.0-85123456789)"
            />
            <p className="text-xs text-gray-500 mt-1">
              Enter the Scopus ID to automatically fetch publication details
            </p>
          </div>
          <div className="flex gap-2 justify-end">
            <Button type="button" variant="outline" onClick={() => setIsOpen(false)} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading || !scopusId.trim()}>
              {loading ? 'Adding...' : 'Add Publication'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

const MeetingCard = ({ meeting, user, onMeetingUpdated }) => (
  <Card>
    <CardContent className="p-6">
      <h3 className="font-semibold">{meeting.agenda}</h3>
      <p className="text-sm text-gray-600">
        {new Date(meeting.meeting_date).toLocaleDateString()} • {meeting.meeting_type.replace('_', ' ')}
      </p>
    </CardContent>
  </Card>
);

const ReminderCard = ({ reminder, user, onReminderUpdated }) => {
  const [isSnoozing, setIsSnoozing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [editFormData, setEditFormData] = useState({
    title: reminder.title || '',
    description: reminder.description || '',
    reminder_date: reminder.reminder_date ? reminder.reminder_date.split('T')[0] : '',
    reminder_time: reminder.reminder_time || '09:00',
    priority: reminder.priority || 'medium'
  });

  const handleSnooze = async (hours = 24) => {
    setIsSnoozing(true);
    try {
      const newDate = new Date(reminder.reminder_date);
      newDate.setHours(newDate.getHours() + hours);
      
      await axios.put(`${API}/reminders/${reminder.id}`, {
        reminder_date: newDate.toISOString()
      });
      alert(`Reminder snoozed for ${hours} hours`);
      onReminderUpdated();
    } catch (error) {
      alert('Error snoozing reminder: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsSnoozing(false);
    }
  };

  const handleEdit = async () => {
    try {
      const reminderDateTime = new Date(`${editFormData.reminder_date}T${editFormData.reminder_time}:00`);
      
      await axios.put(`${API}/reminders/${reminder.id}`, {
        title: editFormData.title,
        description: editFormData.description,
        reminder_date: reminderDateTime.toISOString(),
        priority: editFormData.priority
      });
      alert('Reminder updated successfully!');
      setShowEditDialog(false);
      onReminderUpdated();
    } catch (error) {
      alert('Error updating reminder: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this reminder?')) return;
    
    setIsDeleting(true);
    try {
      await axios.delete(`${API}/reminders/${reminder.id}`);
      alert('Reminder deleted successfully!');
      onReminderUpdated();
    } catch (error) {
      alert('Error deleting reminder: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="font-semibold">{reminder.title}</h3>
              <p className="text-sm text-gray-600 mb-2">{reminder.description}</p>
              <p className="text-xs text-gray-500">
                Due: {new Date(reminder.reminder_date).toLocaleString()}
              </p>
            </div>
            <Badge className={getPriorityColor(reminder.priority)}>
              {reminder.priority}
            </Badge>
          </div>
          
          {/* Action Buttons */}
          <div className="flex gap-2 mt-4 pt-3 border-t">
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleSnooze(24)}
              disabled={isSnoozing}
              className="text-blue-600 border-blue-600 hover:bg-blue-50"
            >
              <Clock className="h-3 w-3 mr-1" />
              {isSnoozing ? 'Snoozing...' : 'Snooze 24h'}
            </Button>
            
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowEditDialog(true)}
              className="text-green-600 border-green-600 hover:bg-green-50"
            >
              <Edit className="h-3 w-3 mr-1" />
              Edit
            </Button>
            
            <Button
              size="sm"
              variant="outline"
              onClick={handleDelete}
              disabled={isDeleting}
              className="text-red-600 border-red-600 hover:bg-red-50"
            >
              <Trash2 className="h-3 w-3 mr-1" />
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Reminder</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>Title</Label>
              <Input
                value={editFormData.title}
                onChange={(e) => setEditFormData({...editFormData, title: e.target.value})}
                placeholder="Reminder title"
              />
            </div>
            <div>
              <Label>Description</Label>
              <Textarea
                value={editFormData.description}
                onChange={(e) => setEditFormData({...editFormData, description: e.target.value})}
                placeholder="Reminder description"
                rows={3}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Date</Label>
                <Input
                  type="date"
                  value={editFormData.reminder_date}
                  onChange={(e) => setEditFormData({...editFormData, reminder_date: e.target.value})}
                />
              </div>
              <div>
                <Label>Time</Label>
                <Input
                  type="time"
                  value={editFormData.reminder_time}
                  onChange={(e) => setEditFormData({...editFormData, reminder_time: e.target.value})}
                />
              </div>
            </div>
            <div>
              <Label>Priority</Label>
              <Select value={editFormData.priority} onValueChange={(value) => setEditFormData({...editFormData, priority: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-2 justify-end">
              <Button variant="outline" onClick={() => setShowEditDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleEdit}>
                Update Reminder
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
};

const BulletinCard = ({ bulletin, user, onBulletinUpdated }) => {
  const [isApproving, setIsApproving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  
  const handleApprove = async (approved) => {
    setIsApproving(true);
    try {
      await axios.post(`${API}/bulletins/${bulletin.id}/approve`, { 
        bulletin_id: bulletin.id,
        approved 
      });
      alert(`Bulletin ${approved ? 'approved' : 'rejected'} successfully!`);
      onBulletinUpdated();
    } catch (error) {
      console.error('Error updating bulletin status:', error);
      let errorMessage = 'Error updating bulletin status: ';
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage += error.response.data.detail;
        } else {
          errorMessage += JSON.stringify(error.response.data.detail);
        }
      } else if (error.response?.data?.message) {
        errorMessage += error.response.data.message;
      } else if (error.message) {
        errorMessage += error.message;
      } else {
        errorMessage += 'Unknown error occurred';
      }
      
      alert(errorMessage);
    } finally {
      setIsApproving(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this announcement? This action cannot be undone.')) {
      return;
    }
    
    setIsDeleting(true);
    try {
      await axios.delete(`${API}/bulletins/${bulletin.id}`);
      alert('Announcement deleted successfully!');
      onBulletinUpdated();
    } catch (error) {
      console.error('Error deleting bulletin:', error);
      let errorMessage = 'Error deleting announcement: ';
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage += error.response.data.detail;
        } else {
          errorMessage += JSON.stringify(error.response.data.detail);
        }
      } else if (error.response?.data?.message) {
        errorMessage += error.response.data.message;
      } else if (error.message) {
        errorMessage += error.message;
      } else {
        errorMessage += 'Unknown error occurred';
      }
      
      alert(errorMessage);
    } finally {
      setIsDeleting(false);
    }
  };

  const canApprove = user.role === 'supervisor' || user.role === 'lab_manager' || user.role === 'admin';
  const canDelete = user.role === 'supervisor' || user.role === 'lab_manager' || user.role === 'admin' || bulletin.author_id === user.id;
  const isPending = bulletin.status === 'pending';

  return (
    <Card className={`${bulletin.is_highlight && bulletin.status === 'approved' ? 'border-yellow-400 bg-yellow-50' : ''}`}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            {bulletin.is_highlight && bulletin.status === 'approved' && (
              <div className="flex items-center mb-2">
                <Star className="h-4 w-4 text-yellow-500 mr-1" />
                <Badge className="bg-yellow-100 text-yellow-800 text-xs">Highlight</Badge>
              </div>
            )}
            <h3 className="font-semibold text-lg">{bulletin.title}</h3>
            <p className="text-gray-600 mt-2">{bulletin.content}</p>
            <p className="text-xs text-gray-500 mt-2">
              Category: {bulletin.category} | Posted by: {bulletin.author_name || 'Unknown'}
            </p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <Badge className={getStatusColor(bulletin.status)} size="sm">
              {bulletin.status}
            </Badge>
            <div className="flex flex-wrap gap-2">
              {canApprove && isPending && (
                <>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-green-600 border-green-600 hover:bg-green-50"
                    onClick={() => handleApprove(true)}
                    disabled={isApproving || isDeleting}
                  >
                    <Check className="h-3 w-3 mr-1" />
                    Approve
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-red-600 border-red-600 hover:bg-red-50"
                    onClick={() => handleApprove(false)}
                    disabled={isApproving || isDeleting}
                  >
                    <X className="h-3 w-3 mr-1" />
                    Reject
                  </Button>
                </>
              )}
              {canDelete && (
                <Button
                  size="sm"
                  variant="outline"
                  className="text-red-600 border-red-600 hover:bg-red-50"
                  onClick={handleDelete}
                  disabled={isApproving || isDeleting}
                >
                  <Trash2 className="h-3 w-3 mr-1" />
                  {isDeleting ? 'Deleting...' : 'Delete'}
                </Button>
              )}
            </div>
          </div>
        </div>
        
        {bulletin.status === 'approved' && (
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-green-600 font-medium">
              ✅ This announcement is live and visible to all users
            </p>
          </div>
        )}
        {bulletin.status === 'rejected' && (
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-red-600 font-medium">
              ❌ This announcement has been rejected and is not visible to users
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const GrantCard = ({ grant, user, onGrantUpdated }) => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  
  const handleRegisterForGrant = async () => {
    setIsRegistering(true);
    try {
      const response = await axios.post(`${API}/grants/${grant.id}/register`);
      alert('Successfully registered for grant!');
      onGrantUpdated();
    } catch (error) {
      console.error('Error registering for grant:', error);
      alert(error.response?.data?.detail || 'Error registering for grant');
    } finally {
      setIsRegistering(false);
    }
  };

  const handleDeleteGrant = async () => {
    if (!window.confirm(`Are you sure you want to delete the grant "${grant.title}"? This action cannot be undone.`)) {
      return;
    }

    setIsDeleting(true);
    try {
      await axios.delete(`${API}/grants/${grant.id}`);
      alert('Grant deleted successfully!');
      onGrantUpdated();
    } catch (error) {
      console.error('Error deleting grant:', error);
      alert(error.response?.data?.detail || 'Error deleting grant');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-lg">{grant.title}</h3>
            <p className="text-sm text-gray-600 mt-1">
              <Building2 className="h-4 w-4 inline mr-1" />
              {grant.funding_agency}
            </p>
            {grant.description && (
              <p className="text-sm text-gray-700 mt-2">
                {showDetails ? grant.description : `${grant.description.slice(0, 100)}...`}
                <Button 
                  variant="link" 
                  size="sm" 
                  onClick={() => setShowDetails(!showDetails)}
                  className="p-0 h-auto text-blue-600"
                >
                  {showDetails ? 'Show less' : 'Show more'}
                </Button>
              </p>
            )}
          </div>
          <Badge className={getStatusColor(grant.status)} size="sm">
            {grant.status.replace('_', ' ')}
          </Badge>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-4 pt-4 border-t">
          <div>
            <p className="text-xs text-gray-500">Total Amount</p>
            <p className="font-semibold text-green-600">${grant.total_amount?.toLocaleString() || 'N/A'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Duration</p>
            <p className="font-medium">{grant.duration_months || 'N/A'} months</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Type</p>
            <p className="font-medium">{grant.grant_type?.replace('_', ' ') || 'N/A'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Vote Number</p>
            <p className="font-medium text-purple-600">{grant.grant_vote_number || 'N/A'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Remaining Balance</p>
            <p className="font-semibold text-blue-600">${grant.remaining_balance?.toLocaleString() || 'N/A'}</p>
          </div>
        </div>

        {/* Person in Charge Information */}
        {grant.person_in_charge && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2">
              <UserCheck className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium text-gray-900">Person in Charge (PIC)</span>
            </div>
            <p className="text-sm text-gray-700 mt-1">{grant.person_in_charge_name || 'Loading...'}</p>
          </div>
        )}

        {grant.start_date && (
          <div className="flex items-center gap-4 mt-3 pt-3 border-t text-sm text-gray-600">
            <span>
              <CalendarDays className="h-4 w-4 inline mr-1" />
              Start: {new Date(grant.start_date).toLocaleDateString()}
            </span>
            {grant.end_date && (
              <span>
                End: {new Date(grant.end_date).toLocaleDateString()}
              </span>
            )}
          </div>
        )}

        {/* PIC Edit Section for Students */}
        {user.role === 'student' && grant.person_in_charge === user.id && (
          <div className="mt-4 pt-4 border-t">
            <div className="bg-blue-50 p-3 rounded-lg">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-sm font-medium text-blue-900">Grant Management (PIC)</p>
                  <p className="text-xs text-blue-700">You are the Person in Charge for this grant</p>
                </div>
                <Badge className="bg-blue-100 text-blue-800">PIC Access</Badge>
              </div>
              <EditGrantDialog grant={grant} onGrantUpdated={onGrantUpdated} isPIC={true} />
            </div>
          </div>
        )}

        {/* Registration Section for Students */}
        {user.role === 'student' && grant.status === 'active' && (
          <div className="mt-4 pt-4 border-t">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">Grant Registration</p>
                <p className="text-xs text-gray-600">Apply to participate in this grant</p>
              </div>
              <Button 
                onClick={handleRegisterForGrant}
                disabled={isRegistering}
                size="sm"
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isRegistering ? (
                  <>
                    <div className="animate-spin h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full" />
                    Registering...
                  </>
                ) : (
                  <>
                    <Award className="h-4 w-4 mr-2" />
                    Register for Grant
                  </>
                )}
              </Button>
            </div>
          </div>
        )}

        {/* Additional Actions for Supervisors */}
        {(user.role === 'supervisor' || user.role === 'lab_manager' || user.role === 'admin') && (
          <div className="mt-4 pt-4 border-t">
            <div className="flex flex-wrap gap-2">
              {grant.status === 'pending' && (
                <>
                  <Button variant="default" size="sm" className="bg-green-600 hover:bg-green-700">
                    <Check className="h-4 w-4 mr-2" />
                    Approve Grant
                  </Button>
                  <Button variant="outline" size="sm" className="text-red-600 border-red-600 hover:bg-red-50">
                    <X className="h-4 w-4 mr-2" />
                    Reject
                  </Button>
                </>
              )}
              <Button variant="outline" size="sm" onClick={() => alert('View Registrations functionality - Coming Soon!')}>
                <Eye className="h-4 w-4 mr-2" />
                View Registrations
              </Button>
              <EditGrantDialog grant={grant} onGrantUpdated={onGrantUpdated} />
              {grant.status === 'active' && (
                <Button variant="outline" size="sm" onClick={() => alert('Generate Report functionality - Coming Soon!')}>
                  <FileBarChart className="h-4 w-4 mr-2" />
                  Generate Report
                </Button>
              )}
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleDeleteGrant}
                disabled={isDeleting}
                className="text-red-600 border-red-600 hover:bg-red-50"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                {isDeleting ? 'Deleting...' : 'Delete Grant'}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const StudentManagementCard = ({ student, user, onStudentUpdated }) => {
  const [isMessageOpen, setIsMessageOpen] = useState(false);
  const [isPromoteOpen, setIsPromoteOpen] = useState(false);
  const [isDemoteOpen, setIsDemoteOpen] = useState(false);
  const [messageData, setMessageData] = useState({ subject: '', content: '' });
  const [promoteData, setPromoteData] = useState({ new_role: 'lab_manager' });
  const [loading, setLoading] = useState(false);
  
  // New state for additional user management actions
  const [isRevoking, setIsRevoking] = useState(false);
  const [isFreezing, setIsFreezing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/messages`, {
        recipient_id: student.id,
        subject: messageData.subject,
        content: messageData.content
      });
      
      alert('Message sent successfully!');
      setMessageData({ subject: '', content: '' });
      setIsMessageOpen(false);
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error sending message: ' + (error.response?.data?.detail || error.message || 'Unknown error occurred'));
    } finally {
      setLoading(false);
    }
  };

  const handlePromoteUser = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.put(`${API}/users/${student.id}/promote`, {
        new_role: promoteData.new_role
      });
      
      alert(`User promoted to ${promoteData.new_role.replace('_', ' ')} successfully!`);
      setIsPromoteOpen(false);
      onStudentUpdated();
    } catch (error) {
      console.error('Error promoting user:', error);
      alert('Error promoting user: ' + (error.response?.data?.detail || error.message || 'Unknown error occurred'));
    } finally {
      setLoading(false);
    }
  };

  const handleDemoteUser = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.put(`${API}/users/${student.id}/promote`, {
        new_role: 'student'
      });
      
      alert(`User demoted to student successfully!`);
      setIsDemoteOpen(false);
      onStudentUpdated();
    } catch (error) {
      console.error('Error demoting user:', error);
      alert('Error demoting user: ' + (error.response?.data?.detail || error.message || 'Unknown error occurred'));
    } finally {
      setLoading(false);
    }
  };

  // New handler functions for user management
  const handleRevokeAccess = async () => {
    if (!window.confirm(`Are you sure you want to revoke access for ${student.full_name}? This will prevent them from logging into the system.`)) {
      return;
    }

    setIsRevoking(true);
    try {
      await axios.post(`${API}/users/${student.id}/freeze`);
      alert('User access revoked successfully!');
      onStudentUpdated();
    } catch (error) {
      console.error('Error revoking access:', error);
      alert('Error revoking access: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsRevoking(false);
    }
  };

  const handleFreezeAccess = async () => {
    const isCurrentlyFrozen = student.study_status === 'suspended' || !student.is_active;
    const action = isCurrentlyFrozen ? 'unfreeze' : 'freeze';
    const actionText = isCurrentlyFrozen ? 'restore' : 'freeze';
    
    if (!window.confirm(`Are you sure you want to ${actionText} access for ${student.full_name}?`)) {
      return;
    }

    setIsFreezing(true);
    try {
      await axios.post(`${API}/users/${student.id}/${action}`);
      alert(`User access ${actionText}d successfully!`);
      onStudentUpdated();
    } catch (error) {
      console.error(`Error ${actionText}ing access:`, error);
      alert(`Error ${actionText}ing access: ` + (error.response?.data?.detail || error.message));
    } finally {
      setIsFreezing(false);
    }
  };

  const handleDeleteProfile = async () => {
    if (!window.confirm(`⚠️ PERMANENT DELETE: Are you sure you want to completely delete ${student.full_name}'s profile? This will permanently remove all their data including research logs, reminders, and cannot be undone.`)) {
      return;
    }

    if (!window.confirm(`FINAL CONFIRMATION: Type "DELETE" to confirm you want to permanently delete ${student.full_name}'s profile and all associated data.`)) {
      return;
    }

    setIsDeleting(true);
    try {
      await axios.delete(`${API}/users/${student.id}`);
      alert('User profile and all associated data deleted successfully!');
      onStudentUpdated();
    } catch (error) {
      console.error('Error deleting profile:', error);
      alert('Error deleting profile: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Avatar>
              <AvatarFallback>{student.full_name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
            </Avatar>
            <div>
              <h3 className="font-semibold">{student.full_name}</h3>
              <p className="text-sm text-gray-600">{student.email}</p>
              <p className="text-xs text-gray-500">{student.role.replace('_', ' ')}</p>
            </div>
          </div>
          <div className="flex gap-2">
            {/* Message Dialog */}
            <Dialog open={isMessageOpen} onOpenChange={setIsMessageOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" size="sm">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Message
                </Button>
              </DialogTrigger>
              <DialogContent className="w-[95vw] max-w-md mx-4 max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Send Message to {student.full_name}</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSendMessage} className="space-y-4">
                  <div>
                    <Label htmlFor="subject">Subject *</Label>
                    <Input
                      id="subject"
                      value={messageData.subject}
                      onChange={(e) => setMessageData({...messageData, subject: e.target.value})}
                      placeholder="Message subject"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="content">Message *</Label>
                    <Textarea
                      id="content"
                      value={messageData.content}
                      onChange={(e) => setMessageData({...messageData, content: e.target.value})}
                      placeholder="Type your message here..."
                      rows={4}
                      required
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="outline" onClick={() => setIsMessageOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit" disabled={loading || !messageData.subject || !messageData.content}>
                      {loading ? 'Sending...' : 'Send Message'}
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>

            {/* Promote Dialog */}
            <Dialog open={isPromoteOpen} onOpenChange={setIsPromoteOpen}>
              <DialogTrigger asChild>
                <Button variant="outline" size="sm">
                  <UserCheck className="h-4 w-4 mr-2" />
                  Promote
                </Button>
              </DialogTrigger>
              <DialogContent className="w-[95vw] max-w-md mx-4 max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Promote {student.full_name}</DialogTitle>
                </DialogHeader>
                <form onSubmit={handlePromoteUser} className="space-y-4">
                  <div>
                    <Label>Current Role</Label>
                    <p className="text-sm text-gray-600 capitalize">{student.role.replace('_', ' ')}</p>
                  </div>
                  <div>
                    <Label htmlFor="new_role">Promote to *</Label>
                    <Select value={promoteData.new_role} onValueChange={(value) => setPromoteData({new_role: value})}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="lab_manager">Lab Manager</SelectItem>
                        <SelectItem value="supervisor">Supervisor</SelectItem>
                        <SelectItem value="admin">Administrator</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="text-sm text-gray-500">
                    <p>⚠️ This action will change the user's role and permissions permanently.</p>
                  </div>
                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="outline" onClick={() => setIsPromoteOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit" disabled={loading}>
                      {loading ? 'Promoting...' : 'Promote User'}
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>

            {/* Revoke Access Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={handleRevokeAccess}
              disabled={isRevoking}
              className="text-red-600 border-red-600 hover:bg-red-50"
            >
              <X className="h-4 w-4 mr-2" />
              {isRevoking ? 'Revoking...' : 'Revoke'}
            </Button>

            {/* Freeze/Unfreeze Access Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={handleFreezeAccess}
              disabled={isFreezing}
              className={`${
                student.study_status === 'suspended' || !student.is_active
                  ? 'text-blue-600 border-blue-600 hover:bg-blue-50'
                  : 'text-yellow-600 border-yellow-600 hover:bg-yellow-50'
              }`}
            >
              <Clock className="h-4 w-4 mr-2" />
              {isFreezing ? 'Processing...' : (
                student.study_status === 'suspended' || !student.is_active ? 'Unfreeze' : 'Freeze'
              )}
            </Button>

            {/* Delete Profile Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={handleDeleteProfile}
              disabled={isDeleting}
              className="text-red-700 border-red-700 hover:bg-red-100"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>

            {/* Demote Dialog */}
            {student.role !== 'student' && (
              <Dialog open={isDemoteOpen} onOpenChange={setIsDemoteOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" size="sm" className="text-orange-600 border-orange-600 hover:bg-orange-50">
                    <UserMinus className="h-4 w-4 mr-2" />
                    Demote
                  </Button>
                </DialogTrigger>
                <DialogContent className="w-[95vw] max-w-md mx-4 max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Demote {student.full_name}</DialogTitle>
                  </DialogHeader>
                  <form onSubmit={handleDemoteUser} className="space-y-4">
                    <div>
                      <Label>Current Role</Label>
                      <p className="text-sm text-gray-600 capitalize">{student.role.replace('_', ' ')}</p>
                    </div>
                    <div>
                      <Label>Demote to</Label>
                      <p className="text-sm font-medium text-orange-600">Student (Normal User)</p>
                    </div>
                    <div className="text-sm text-orange-600 bg-orange-50 p-3 rounded">
                      <p>⚠️ This action will remove all elevated privileges and demote the user to a normal student account.</p>
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button type="button" variant="outline" onClick={() => setIsDemoteOpen(false)}>
                        Cancel
                      </Button>
                      <Button type="submit" disabled={loading} className="bg-orange-600 hover:bg-orange-700">
                        {loading ? 'Demoting...' : 'Demote to Student'}
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Admin Panel Component
const AdminPanel = ({ user, labSettings, onSettingsUpdated, menuSettings, onMenuSettingsUpdated }) => {
  const [activeAdminTab, setActiveAdminTab] = useState('lab-settings');
  const [labData, setLabData] = useState({
    lab_name: labSettings?.lab_name || '',
    lab_logo: labSettings?.lab_logo || '',
    description: labSettings?.description || '',
    contact_email: labSettings?.contact_email || '',
    website: labSettings?.website || '',
    address: labSettings?.address || '',
    lab_scopus_id: labSettings?.lab_scopus_id || ''
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [loading, setLoading] = useState(false);

  // Update labData when labSettings prop changes
  useEffect(() => {
    setLabData({
      lab_name: labSettings?.lab_name || '',
      lab_logo: labSettings?.lab_logo || '',
      description: labSettings?.description || '',
      contact_email: labSettings?.contact_email || '',
      website: labSettings?.website || '',
      address: labSettings?.address || '',
      lab_scopus_id: labSettings?.lab_scopus_id || ''
    });
  }, [labSettings]);

  const handleLabSettingsUpdate = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/lab/settings`, labData);
      alert('Lab settings updated successfully!');
      onSettingsUpdated();
    } catch (error) {
      console.error('Error updating lab settings:', error);
      alert('Error updating lab settings: ' + (error.response?.data?.detail || error.message || 'Unknown error occurred'));
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      alert('New password and confirmation do not match');
      return;
    }
    
    setLoading(true);
    try {
      await axios.post(`${API}/auth/change-password`, {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      alert('Password changed successfully!');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (error) {
      console.error('Error changing password:', error);
      alert(error.response?.data?.detail || 'Error changing password');
    } finally {
      setLoading(false);
    }
  };

  const handleLogoUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const response = await axios.post(`${API}/lab/logo`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setLabData({ ...labData, lab_logo: response.data.file_path });
      alert('Logo uploaded successfully!');
    } catch (error) {
      console.error('Error uploading logo:', error);
      alert('Error uploading logo: ' + (error.response?.data?.detail || error.message || 'Unknown error occurred'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Administration Panel</h2>
        <Badge variant="outline" className="bg-blue-50 text-blue-700">
          {user.role.replace('_', ' ').toUpperCase()}
        </Badge>
      </div>

      <Tabs value={activeAdminTab} onValueChange={setActiveAdminTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="lab-settings">Lab Settings</TabsTrigger>
          <TabsTrigger value="user-management">User Management</TabsTrigger>
          <TabsTrigger value="menu-settings">Menu Settings</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        {/* Lab Settings Tab */}
        <TabsContent value="lab-settings" className="mt-6">
          {user.role === 'supervisor' ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Laboratory Information
                </CardTitle>
                <p className="text-sm text-gray-600">Configure your lab's basic information and branding</p>
              </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="lab_name">Lab Name *</Label>
                    <Input
                      id="lab_name"
                      value={labData.lab_name}
                      onChange={(e) => setLabData({...labData, lab_name: e.target.value})}
                      placeholder="Enter lab name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="contact_email">Contact Email</Label>
                    <Input
                      id="contact_email"
                      type="email"
                      value={labData.contact_email}
                      onChange={(e) => setLabData({...labData, contact_email: e.target.value})}
                      placeholder="lab@university.edu"
                    />
                  </div>
                  <div>
                    <Label htmlFor="website">Website</Label>
                    <Input
                      id="website"
                      type="url"
                      value={labData.website}
                      onChange={(e) => setLabData({...labData, website: e.target.value})}
                      placeholder="https://lab.university.edu"
                    />
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="description">Lab Description</Label>
                    <Textarea
                      id="description"
                      value={labData.description}
                      onChange={(e) => setLabData({...labData, description: e.target.value})}
                      placeholder="Describe your lab's research focus and mission"
                      rows={4}
                    />
                  </div>
                  <div>
                    <Label htmlFor="address">Address</Label>
                    <Textarea
                      id="address"
                      value={labData.address}
                      onChange={(e) => setLabData({...labData, address: e.target.value})}
                      placeholder="Lab physical address"
                      rows={3}
                    />
                  </div>
                </div>
              </div>

              {/* Lab Scopus ID Section - Critical for Publications Sync */}
              <div className="border-t pt-6">
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="lab_scopus_id" className="text-base font-semibold">Lab Scopus ID</Label>
                    <p className="text-sm text-gray-600 mb-2">
                      Enter your lab's Scopus ID to automatically sync and display publications across all users
                    </p>
                    <Input
                      id="lab_scopus_id"
                      value={labData.lab_scopus_id || ''}
                      onChange={(e) => setLabData({...labData, lab_scopus_id: e.target.value})}
                      placeholder="e.g., 55208373700, 7004212771"
                    />
                    <p className="text-xs text-blue-600 mt-1">
                      ⚠️ When updated, this will sync ALL lab publications from Scopus and make them visible to all users
                    </p>
                  </div>
                </div>
              </div>

              <div className="border-t pt-6">
                <Label>Lab Logo</Label>
                <div className="flex items-center space-x-4 mt-2">
                  {labData.lab_logo && (
                    <div className="w-16 h-16 rounded-lg border overflow-hidden">
                      <img 
                        src={`${BACKEND_URL}${labData.lab_logo}`} 
                        alt="Lab logo" 
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}
                  <div>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleLogoUpload}
                      className="hidden"
                      id="logo-upload"
                    />
                    <label htmlFor="logo-upload">
                      <Button type="button" variant="outline" disabled={loading}>
                        <Upload className="h-4 w-4 mr-2" />
                        {labData.lab_logo ? 'Change Logo' : 'Upload Logo'}
                      </Button>
                    </label>
                  </div>
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <Button onClick={handleLabSettingsUpdate} disabled={loading}>
                  {loading ? 'Updating...' : 'Save Lab Settings'}
                </Button>
              </div>
            </CardContent>
          </Card>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Access Restricted</h3>
                <p className="text-gray-500">Only supervisors can access lab settings.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* User Management Tab */}
        <TabsContent value="user-management" className="mt-6">
          {user.role === 'supervisor' ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  User Management
                </CardTitle>
                <p className="text-sm text-gray-600">Manage user roles and permissions</p>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <Users className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">User management features coming soon</p>
                  <p className="text-sm text-gray-400 mt-1">This will include role management, user promotion, and access control</p>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Access Restricted</h3>
                <p className="text-gray-500">Only supervisors can access user management.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Menu Settings Tab */}
        <TabsContent value="menu-settings" className="mt-6">
          {user.role === 'supervisor' ? (
            <Card>
              <CardHeader>
                <CardTitle>Menu Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">Enable or disable menu tabs for all users</p>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(menuSettings).map(([key, value]) => (
                      <div key={key} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id={key}
                          checked={value}
                          onChange={(e) => onMenuSettingsUpdated({
                            ...menuSettings,
                            [key]: e.target.checked
                          })}
                          className="rounded border-gray-300"
                        />
                        <Label htmlFor={key} className="text-sm font-medium capitalize">
                          {key.replace('_', ' ')}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Access Restricted</h3>
                <p className="text-gray-500">Only supervisors can access menu settings.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Security Settings
              </CardTitle>
              <p className="text-sm text-gray-600">Change your password and security preferences</p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div>
                  <Label htmlFor="current_password">Current Password *</Label>
                  <Input
                    id="current_password"
                    type="password"
                    value={passwordData.current_password}
                    onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                    placeholder="Enter current password"
                  />
                </div>
                <div>
                  <Label htmlFor="new_password">New Password *</Label>
                  <Input
                    id="new_password"
                    type="password"
                    value={passwordData.new_password}
                    onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                    placeholder="Enter new password"
                  />
                </div>
                <div>
                  <Label htmlFor="confirm_password">Confirm New Password *</Label>
                  <Input
                    id="confirm_password"
                    type="password"
                    value={passwordData.confirm_password}
                    onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
                    placeholder="Confirm new password"
                  />
                </div>
              </div>

              <div className="flex justify-end pt-4">
                <Button 
                  onClick={handlePasswordChange} 
                  disabled={loading || !passwordData.current_password || !passwordData.new_password}
                >
                  {loading ? 'Changing...' : 'Change Password'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

const CreateMilestoneDialog = ({ onMilestoneCreated }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [formData, setFormData] = useState({
    project_title: '',
    milestone_title: '',
    description: '',
    start_date: new Date().toISOString().split('T')[0],
    target_end_date: '',
    progress_percentage: 0,
    deliverables: '',
    challenges: '',
    next_steps: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const submitData = {
        ...formData,
        deliverables: formData.deliverables ? formData.deliverables.split(',').map(d => d.trim()) : [],
        start_date: new Date(formData.start_date).toISOString(),
        target_end_date: new Date(formData.target_end_date).toISOString()
      };
      
      await axios.post(`${API}/milestones`, submitData);
      
      alert('Milestone created successfully!');
      setFormData({
        project_title: '',
        milestone_title: '',
        description: '',
        start_date: new Date().toISOString().split('T')[0],
        target_end_date: '',
        progress_percentage: 0,
        deliverables: '',
        challenges: '',
        next_steps: ''
      });
      setIsOpen(false);
      onMilestoneCreated();
    } catch (error) {
      console.error('Error creating milestone:', error);
      alert('Error creating milestone: ' + (error.response?.data?.detail || error.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Milestone
        </Button>
      </DialogTrigger>
      <DialogContent className="w-[95vw] max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Milestone</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="project_title">Project Title *</Label>
            <Input
              id="project_title"
              value={formData.project_title}
              onChange={(e) => setFormData({...formData, project_title: e.target.value})}
              placeholder="Enter project name"
            />
          </div>
          
          <div>
            <Label htmlFor="milestone_title">Milestone Title *</Label>
            <Input
              id="milestone_title"
              value={formData.milestone_title}
              onChange={(e) => setFormData({...formData, milestone_title: e.target.value})}
              placeholder="Enter milestone name"
            />
          </div>
          
          <div>
            <Label htmlFor="description">Description *</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              placeholder="Describe the milestone objectives and scope"
              required
              rows={3}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="start_date">Start Date *</Label>
              <Input
                id="start_date"
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({...formData, start_date: e.target.value})}
                required
              />
            </div>
            
            <div>
              <Label htmlFor="target_end_date">Target End Date *</Label>
              <Input
                id="target_end_date"
                type="date"
                value={formData.target_end_date}
                onChange={(e) => setFormData({...formData, target_end_date: e.target.value})}
                required
              />
            </div>
          </div>
          
          <div>
            <Label htmlFor="deliverables">Expected Deliverables</Label>
            <Input
              id="deliverables"
              value={formData.deliverables}
              onChange={(e) => setFormData({...formData, deliverables: e.target.value})}
              placeholder="Deliverable 1, Deliverable 2, Deliverable 3"
            />
            <p className="text-xs text-gray-500 mt-1">Separate multiple deliverables with commas</p>
          </div>
          
          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button type="button" variant="outline" onClick={() => setIsOpen(false)} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Milestone'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

const MilestoneCard = ({ milestone, user, onMilestoneUpdated }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [progress, setProgress] = useState(milestone.progress_percentage || 0);

  const updateProgress = async () => {
    try {
      await axios.put(`${API}/milestones/${milestone.id}`, {
        progress_percentage: progress,
        status: progress >= 100 ? 'completed' : 'in_progress'
      });
      alert('Progress updated successfully!');
      setIsEditing(false);
      onMilestoneUpdated();
    } catch (error) {
      alert('Error updating progress: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="font-semibold text-lg">{milestone.milestone_title}</h3>
            <p className="text-blue-600 font-medium">{milestone.project_title}</p>
            <p className="text-sm text-gray-600">
              {new Date(milestone.start_date).toLocaleDateString()} - {new Date(milestone.target_end_date).toLocaleDateString()}
            </p>
            {user.role !== 'student' && milestone.student_name && (
              <p className="text-sm text-purple-600">Student: {milestone.student_name}</p>
            )}
          </div>
          <Badge className={milestone.status === 'completed' ? 'bg-green-100 text-green-800' : milestone.status === 'delayed' ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'}>
            {milestone.status.replace('_', ' ')}
          </Badge>
        </div>
        
        <p className="text-gray-700 mb-4">{milestone.description}</p>
        
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Progress</span>
            <span className="text-sm text-gray-600">{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
              style={{width: `${progress}%`}}
            ></div>
          </div>
        </div>
        
        {milestone.deliverables && milestone.deliverables.length > 0 && (
          <div className="mb-4">
            <h4 className="font-medium text-sm mb-2">Deliverables:</h4>
            <div className="flex flex-wrap gap-2">
              {milestone.deliverables.map((deliverable, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {deliverable}
                </Badge>
              ))}
            </div>
          </div>
        )}
        
        {user.role === 'student' && milestone.student_id === user.id && (
          <div className="flex justify-end gap-2 pt-4 border-t">
            {isEditing ? (
              <>
                <input 
                  type="range" 
                  min="0" 
                  max="100" 
                  value={progress}
                  onChange={(e) => setProgress(parseInt(e.target.value))}
                  className="flex-1"
                />
                <Button size="sm" onClick={updateProgress}>Save</Button>
                <Button size="sm" variant="outline" onClick={() => setIsEditing(false)}>Cancel</Button>
              </>
            ) : (
              <Button size="sm" onClick={() => setIsEditing(true)}>
                Update Progress
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/*" element={<AuthContext />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;