import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
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
  Calendar, CheckCircle, Clock, MessageSquare, BookOpen, FlaskConical, 
  Users, BarChart3, PlusCircle, Settings, LogOut, Upload, Star, 
  FileText, DollarSign, Award, Bell, Camera, Download, Eye,
  Building2, UserCheck, Banknote, TrendingUp, FileImage, User,
  MapPin, Phone, GraduationCap, CalendarDays, AlertTriangle,
  Edit, Trash2, BookMarked, FileBarChart
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
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-2">
            <Building2 className="h-6 w-6 text-blue-600" />
            Research Lab Manager
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
    </div>
  );
};

// Main Dashboard Component
const Dashboard = ({ user, logout, setUser }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [tasks, setTasks] = useState([]);
  const [researchLogs, setResearchLogs] = useState([]);
  const [students, setStudents] = useState([]);
  const [stats, setStats] = useState({});
  const [bulletins, setBulletins] = useState([]);
  const [grants, setGrants] = useState([]);
  const [publications, setPublications] = useState([]);
  const [labSettings, setLabSettings] = useState({});
  const [meetings, setMeetings] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [
        tasksRes, logsRes, statsRes, bulletinsRes, grantsRes, 
        pubsRes, labRes, meetingsRes, remindersRes, notesRes
      ] = await Promise.all([
        axios.get(`${API}/tasks`).catch(() => ({data: []})),
        axios.get(`${API}/research-logs`).catch(() => ({data: []})),
        axios.get(`${API}/dashboard/stats`).catch(() => ({data: {}})),
        axios.get(`${API}/bulletins`).catch(() => ({data: []})),
        axios.get(`${API}/grants`).catch(() => ({data: []})),
        axios.get(`${API}/publications`).catch(() => ({data: []})),
        axios.get(`${API}/lab/settings`).catch(() => ({data: {}})),
        axios.get(`${API}/meetings`).catch(() => ({data: []})),
        axios.get(`${API}/reminders`).catch(() => ({data: []})),
        axios.get(`${API}/notes`).catch(() => ({data: []}))
      ]);

      setTasks(tasksRes.data || []);
      setResearchLogs(logsRes.data || []);
      setStats(statsRes.data || {});
      setBulletins(bulletinsRes.data || []);
      setGrants(grantsRes.data || []);
      setPublications(pubsRes.data || []);
      setLabSettings(labRes.data || {});
      setMeetings(meetingsRes.data || []);
      setReminders(remindersRes.data || []);
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
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              {labSettings.lab_logo ? (
                <img src={labSettings.lab_logo} alt="Lab Logo" className="h-10 w-10 rounded-full mr-3" />
              ) : (
                <Building2 className="h-8 w-8 text-blue-600 mr-3" />
              )}
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  {labSettings.lab_name || user.lab_name || 'Research Lab'}
                </h1>
                <p className="text-xs text-gray-500">Advanced Research Management System</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <div className="relative">
                <Bell className="h-5 w-5 text-gray-600 cursor-pointer" onClick={() => setActiveTab('reminders')} />
                {reminders.filter(r => !r.is_completed).length > 0 && (
                  <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full text-xs text-white flex items-center justify-center">
                    {reminders.filter(r => !r.is_completed).length}
                  </span>
                )}
              </div>
              
              <Button variant="outline" size="sm" onClick={() => setActiveTab('profile')}>
                <Settings className="h-4 w-4 mr-2" />
                Profile
              </Button>
              <Avatar className="cursor-pointer" onClick={() => setActiveTab('profile')}>
                <AvatarFallback>
                  {user.profile_picture ? (
                    <img src={user.profile_picture} alt="Profile" className="w-full h-full rounded-full object-cover" />
                  ) : (
                    user.full_name.split(' ').map(n => n[0]).join('')
                  )}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm font-medium">{user.full_name}</p>
                <p className="text-xs text-gray-500 capitalize">{user.role.replace('_', ' ')}</p>
              </div>
              <Button variant="outline" size="sm" onClick={logout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-5 lg:grid-cols-10 w-full max-w-5xl mb-8 text-xs">
            <TabsTrigger value="dashboard" className="flex flex-col items-center p-2">
              <BarChart3 className="h-4 w-4" />
              <span className="hidden sm:inline">Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="tasks" className="flex flex-col items-center p-2">
              <CheckCircle className="h-4 w-4" />
              <span className="hidden sm:inline">Tasks</span>
            </TabsTrigger>
            <TabsTrigger value="research" className="flex flex-col items-center p-2">
              <FlaskConical className="h-4 w-4" />
              <span className="hidden sm:inline">Research</span>
            </TabsTrigger>
            <TabsTrigger value="meetings" className="flex flex-col items-center p-2">
              <Calendar className="h-4 w-4" />
              <span className="hidden sm:inline">Meetings</span>
            </TabsTrigger>
            <TabsTrigger value="bulletins" className="flex flex-col items-center p-2">
              <Bell className="h-4 w-4" />
              <span className="hidden sm:inline">News</span>
            </TabsTrigger>
            <TabsTrigger value="grants" className="flex flex-col items-center p-2">
              <DollarSign className="h-4 w-4" />
              <span className="hidden sm:inline">Grants</span>
            </TabsTrigger>
            <TabsTrigger value="publications" className="flex flex-col items-center p-2">
              <Award className="h-4 w-4" />
              <span className="hidden sm:inline">Publications</span>
            </TabsTrigger>
            {(user.role === 'supervisor' || user.role === 'lab_manager') && (
              <TabsTrigger value="students" className="flex flex-col items-center p-2">
                <Users className="h-4 w-4" />
                <span className="hidden sm:inline">Students</span>
              </TabsTrigger>
            )}
            <TabsTrigger value="profile" className="flex flex-col items-center p-2">
              <Settings className="h-4 w-4" />
              <span className="hidden sm:inline">Profile</span>
            </TabsTrigger>
            <TabsTrigger value="reminders" className="flex flex-col items-center p-2">
              <AlertTriangle className="h-4 w-4" />
              <span className="hidden sm:inline">Reminders</span>
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="mt-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {user.role === 'student' ? (
                <>
                  <StatCard icon={CheckCircle} title="Total Tasks" value={stats.total_tasks || 0} color="blue" />
                  <StatCard icon={Award} title="Completed" value={stats.completed_tasks || 0} color="green" />
                  <StatCard icon={Clock} title="In Progress" value={stats.in_progress_tasks || 0} color="yellow" />
                  <StatCard icon={FlaskConical} title="Research Logs" value={stats.total_research_logs || 0} color="purple" />
                </>
              ) : (
                <>
                  <StatCard icon={Users} title="Students" value={stats.total_students || 0} color="blue" />
                  <StatCard icon={CheckCircle} title="Tasks Assigned" value={stats.total_assigned_tasks || 0} color="purple" />
                  <StatCard icon={Award} title="Publications" value={stats.total_publications || 0} color="green" />
                  <StatCard icon={DollarSign} title="Active Grants" value={stats.active_grants || 0} color="yellow" />
                </>
              )}
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    Upcoming Meetings
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {meetings.slice(0, 3).map((meeting) => (
                    <div key={meeting.id} className="flex items-center justify-between py-2 border-b last:border-b-0">
                      <div>
                        <p className="font-medium text-sm">{meeting.agenda}</p>
                        <p className="text-xs text-gray-600">{new Date(meeting.meeting_date).toLocaleDateString()}</p>
                      </div>
                      <Badge className={getStatusColor(meeting.meeting_type)} size="sm">
                        {meeting.meeting_type.replace('_', ' ')}
                      </Badge>
                    </div>
                  ))}
                  {meetings.length === 0 && (
                    <p className="text-gray-500 text-sm">No upcoming meetings</p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5" />
                    Active Reminders
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {reminders.filter(r => !r.is_completed).slice(0, 3).map((reminder) => (
                    <div key={reminder.id} className="flex items-center justify-between py-2 border-b last:border-b-0">
                      <div>
                        <p className="font-medium text-sm">{reminder.title}</p>
                        <p className="text-xs text-gray-600">{new Date(reminder.reminder_date).toLocaleDateString()}</p>
                      </div>
                      <Badge className={getPriorityColor(reminder.priority)} size="sm">
                        {reminder.priority}
                      </Badge>
                    </div>
                  ))}
                  {reminders.filter(r => !r.is_completed).length === 0 && (
                    <p className="text-gray-500 text-sm">No active reminders</p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Bell className="h-5 w-5" />
                    Recent Announcements
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {bulletins.slice(0, 3).map((bulletin) => (
                    <div key={bulletin.id} className="flex items-start space-x-3 py-2 border-b last:border-b-0">
                      <Bell className="h-4 w-4 text-blue-600 mt-0.5" />
                      <div className="flex-1">
                        <h4 className="font-medium text-sm">{bulletin.title}</h4>
                        <p className="text-xs text-gray-600 mt-1">{bulletin.category}</p>
                        <Badge className={getStatusColor(bulletin.status)} size="sm">
                          {bulletin.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                  {bulletins.length === 0 && (
                    <p className="text-gray-500 text-sm">No recent announcements</p>
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
                <CreateTaskDialog students={students} onTaskCreated={fetchDashboardData} />
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

            <div className="grid gap-6">
              {researchLogs.map((log) => (
                <ResearchLogCard key={log.id} log={log} user={user} onLogUpdated={fetchDashboardData} />
              ))}
              {researchLogs.length === 0 && (
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
              <h2 className="text-2xl font-bold">Supervisor Meetings</h2>
              {(user.role === 'supervisor' || user.role === 'lab_manager') && (
                <CreateMeetingDialog students={students} onMeetingCreated={fetchDashboardData} />
              )}
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

            <AllPublicationsView user={user} students={students} publications={publications} />
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
              <CreateReminderDialog students={students} onReminderCreated={fetchDashboardData} />
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
              {bulletins.map((bulletin) => (
                <BulletinCard key={bulletin.id} bulletin={bulletin} user={user} onBulletinUpdated={fetchDashboardData} />
              ))}
            </div>
          </TabsContent>

          {/* Grants Tab */}
          <TabsContent value="grants" className="mt-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Grant Management</h2>
              {(user.role === 'supervisor' || user.role === 'lab_manager') && (
                <CreateGrantDialog students={students} onGrantCreated={fetchDashboardData} />
              )}
            </div>

            <div className="grid gap-6">
              {grants.map((grant) => (
                <GrantCard key={grant.id} grant={grant} user={user} onGrantUpdated={fetchDashboardData} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
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

// Comprehensive Student Profile Component
const ComprehensiveStudentProfile = ({ user, setUser, meetings, reminders, notes, labSettings, onDataUpdated }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchUserProfile();
  }, []);

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
      alert('Error updating profile');
    } finally {
      setLoading(false);
    }
  };

  const uploadProfilePicture = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/users/profile-picture`, formData);
      setUserProfile({ ...userProfile, profile_picture: response.data.file_path });
      setUser({ ...user, profile_picture: response.data.file_path });
      alert('Profile picture updated successfully!');
    } catch (error) {
      console.error('Error uploading picture:', error);
      alert('Error uploading picture');
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
                  {userProfile.profile_picture ? (
                    <img 
                      src={userProfile.profile_picture} 
                      alt="Profile" 
                      className="w-full h-full rounded-full object-cover" 
                    />
                  ) : (
                    <div className="bg-blue-500 text-white text-2xl font-bold">
                      {userProfile.full_name.split(' ').map(n => n[0]).join('')}
                    </div>
                  )}
                </AvatarFallback>
              </Avatar>
              <label className="absolute bottom-0 right-0 bg-blue-600 rounded-full p-1 cursor-pointer hover:bg-blue-700">
                <Camera className="h-4 w-4 text-white" />
                <input
                  type="file"
                  accept="image/*"
                  onChange={uploadProfilePicture}
                  className="hidden"
                />
              </label>
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

// Placeholder components for the remaining functionality
const ProfileEditForm = ({ formData, setFormData, loading, onSave, onCancel }) => (
  <div className="space-y-4">
    <p className="text-center text-gray-600">Profile editing form will be implemented here</p>
    <div className="flex justify-end gap-2">
      <Button variant="outline" onClick={onCancel}>Cancel</Button>
      <Button onClick={onSave} disabled={loading}>
        {loading ? 'Saving...' : 'Save Changes'}
      </Button>
    </div>
  </div>
);

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
const ResearchLogCard = ({ log, user, onLogUpdated }) => (
  <Card>
    <CardContent className="p-6">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-semibold text-lg">{log.title}</h3>
          <p className="text-sm text-gray-600">
            {new Date(log.date).toLocaleDateString()} • {log.activity_type.replace('_', ' ')}
            {log.duration_hours && ` • ${log.duration_hours}h`}
          </p>
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
    </CardContent>
  </Card>
);

// Placeholder components for dialogs and other functionality
const CreateTaskDialog = ({ students, onTaskCreated }) => (
  <Button>
    <PlusCircle className="h-4 w-4 mr-2" />
    Create Task
  </Button>
);

const CreateResearchLogDialog = ({ onLogCreated }) => (
  <Button>
    <PlusCircle className="h-4 w-4 mr-2" />
    Add Research Log
  </Button>
);

const CreateMeetingDialog = ({ students, onMeetingCreated }) => (
  <Button>
    <PlusCircle className="h-4 w-4 mr-2" />
    Schedule Meeting
  </Button>
);

const CreateReminderDialog = ({ students, onReminderCreated }) => (
  <Button>
    <PlusCircle className="h-4 w-4 mr-2" />
    Add Reminder
  </Button>
);

const CreateBulletinDialog = ({ onBulletinCreated }) => (
  <Button>
    <PlusCircle className="h-4 w-4 mr-2" />
    Post Announcement
  </Button>
);

const CreateGrantDialog = ({ students, onGrantCreated }) => (
  <Button>
    <PlusCircle className="h-4 w-4 mr-2" />
    Add Grant
  </Button>
);

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

const ReminderCard = ({ reminder, user, onReminderUpdated }) => (
  <Card>
    <CardContent className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold">{reminder.title}</h3>
          <p className="text-sm text-gray-600">{reminder.description}</p>
        </div>
        <Badge className={getPriorityColor(reminder.priority)}>
          {reminder.priority}
        </Badge>
      </div>
    </CardContent>
  </Card>
);

const BulletinCard = ({ bulletin, user, onBulletinUpdated }) => (
  <Card>
    <CardContent className="p-6">
      <h3 className="font-semibold">{bulletin.title}</h3>
      <p className="text-gray-600 mt-2">{bulletin.content}</p>
      <Badge className={getStatusColor(bulletin.status)} size="sm">
        {bulletin.status}
      </Badge>
    </CardContent>
  </Card>
);

const GrantCard = ({ grant, user, onGrantUpdated }) => (
  <Card>
    <CardContent className="p-6">
      <h3 className="font-semibold">{grant.title}</h3>
      <p className="text-sm text-gray-600">{grant.funding_agency}</p>
      <div className="flex items-center justify-between mt-4">
        <span>Budget: ${grant.total_amount}</span>
        <Badge className={getStatusColor(grant.status)}>
          {grant.status}
        </Badge>
      </div>
    </CardContent>
  </Card>
);

const StudentManagementCard = ({ student, user, onStudentUpdated }) => (
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
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <MessageSquare className="h-4 w-4 mr-2" />
            Message
          </Button>
          <Button variant="outline" size="sm">
            <UserCheck className="h-4 w-4 mr-2" />
            Promote
          </Button>
        </div>
      </div>
    </CardContent>
  </Card>
);

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