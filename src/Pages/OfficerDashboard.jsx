import React, { useState, useEffect } from "react";
import {
  FileText,
  Layers,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Send,
  Upload,
  MessageSquare,
  AlertCircle as AlertIcon,
  Eye,
  PlayCircle,
  PauseCircle,
  RefreshCw,
  Image as ImageIcon,
} from "lucide-react";
import { officerAPI } from "../services/api";

export default function OfficerDashboard() {
  // State
  const [tickets, setTickets] = useState([]);
  const [resolvedTickets, setResolvedTickets] = useState([]);
  const [ticketCounts, setTicketCounts] = useState({
    assigned: 0,
    in_progress: 0,
    completed: 0,
    clarifications: 0,
  });
  const [loading, setLoading] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [clarifications, setClarifications] = useState([]);

  // Modals
  const [showResolveModal, setShowResolveModal] = useState(false);
  const [showClarificationModal, setShowClarificationModal] = useState(false);
  const [showResolvedDetailsModal, setShowResolvedDetailsModal] =
    useState(false);

  // Forms
  const [resolveForm, setResolveForm] = useState({
    action_taken: "",
    closing_remark: "",
    resolution_photos: [],
  });
  const [clarificationForm, setClarificationForm] = useState({
    message: "",
  });

  // Loading states
  const [resolveLoading, setResolveLoading] = useState(false);
  const [clarificationLoading, setClarificationLoading] = useState(false);
  const [statusUpdateLoading, setStatusUpdateLoading] = useState(false);

  // Errors
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Fetch dashboard data
  useEffect(() => {
    fetchDashboard();
    fetchResolvedTickets();
    fetchTicketCounts();
    fetchClarifications();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await officerAPI.getDashboard();
      console.log("Dashboard API Response:", response.data);

      // Check if response is array or has a tickets property
      const ticketsData = Array.isArray(response.data)
        ? response.data
        : response.data?.tickets || [];
      setTickets(ticketsData);
      console.log("Tickets loaded:", ticketsData.length);
    } catch (error) {
      console.error("Failed to fetch dashboard:", error);
      console.error("Error details:", error.response?.data);

      let errorMsg = "Failed to load tickets";
      if (error.response?.status === 403) {
        errorMsg = "Access denied. Please login as an officer.";
      } else if (error.response?.status === 404) {
        errorMsg = "Officer dashboard endpoint not found.";
      } else if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      }
      setError(errorMsg);
    }
    setLoading(false);
  };

  const fetchResolvedTickets = async () => {
    try {
      const response = await officerAPI.getResolvedTickets();
      console.log("Resolved Tickets API Response:", response.data);
      const resolvedData = Array.isArray(response.data) ? response.data : [];
      setResolvedTickets(resolvedData);
      console.log("Resolved tickets loaded:", resolvedData.length);
    } catch (error) {
      console.error("Failed to fetch resolved tickets:", error);
    }
  };

  const fetchTicketCounts = async () => {
    try {
      const response = await officerAPI.getTicketCounts();
      console.log("Ticket Counts API Response:", response.data);
      setTicketCounts(response.data);
    } catch (error) {
      console.error("Failed to fetch ticket counts:", error);
    }
  };

  const fetchClarifications = async () => {
    try {
      const response = await officerAPI.getClarifications();
      setClarifications(response.data.clarifications || []);
    } catch (error) {
      console.error("Failed to fetch clarifications:", error);
    }
  };

  const handleStatusUpdate = async (
    grievanceId,
    newStatus,
    progressNote = ""
  ) => {
    setStatusUpdateLoading(true);
    setError("");
    try {
      await officerAPI.updateStatus({
        grievance_id: grievanceId,
        new_status: newStatus,
        progress_note: progressNote,
      });
      setSuccess(`Ticket status updated to ${newStatus}`);
      fetchDashboard();
      setTimeout(() => setSuccess(""), 3000);
    } catch (error) {
      setError(error.response?.data?.detail || "Failed to update status");
    }
    setStatusUpdateLoading(false);
  };

  const openResolveModal = (ticket) => {
    setSelectedTicket(ticket);
    setShowResolveModal(true);
    setResolveForm({
      action_taken: "",
      closing_remark: "",
      resolution_photos: [],
    });
  };

  const handleFileChange = (e) => {
    setResolveForm({
      ...resolveForm,
      resolution_photos: Array.from(e.target.files),
    });
  };

  const handleResolveTicket = async (e) => {
    e.preventDefault();
    setResolveLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("grievance_id", selectedTicket.ticket.grievance_id);
      formData.append("action_taken", resolveForm.action_taken);
      formData.append("closing_remark", resolveForm.closing_remark);

      resolveForm.resolution_photos.forEach((photo) => {
        formData.append("resolution_photos", photo);
      });

      const response = await officerAPI.resolveTicket(formData);
      setSuccess(
        `Ticket resolved successfully! Time: ${response.data.completion_time_hours}hrs`
      );
      setShowResolveModal(false);
      fetchDashboard();
      setTimeout(() => setSuccess(""), 5000);
    } catch (error) {
      setError(error.response?.data?.detail || "Failed to resolve ticket");
    }
    setResolveLoading(false);
  };

  const openClarificationModal = (ticket) => {
    setSelectedTicket(ticket);
    setShowClarificationModal(true);
    setClarificationForm({ message: "" });
  };

  const handleRequestClarification = async (e) => {
    e.preventDefault();
    setClarificationLoading(true);
    setError("");

    try {
      await officerAPI.requestClarification({
        grievance_id: selectedTicket.ticket.grievance_id,
        message: clarificationForm.message,
      });
      setSuccess("Clarification request sent to citizen");
      setShowClarificationModal(false);
      fetchClarifications();
      setTimeout(() => setSuccess(""), 3000);
    } catch (error) {
      setError(error.response?.data?.detail || "Failed to send clarification");
    }
    setClarificationLoading(false);
  };

  const viewTicketDetails = async (ticket) => {
    // For resolved tickets, show the resolved details modal
    setSelectedTicket(ticket);
    setShowResolvedDetailsModal(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "assigned":
        return "bg-blue-100 text-blue-700";
      case "in_progress":
        return "bg-yellow-100 text-yellow-700";
      case "resolved":
        return "bg-green-100 text-green-700";
      case "clarification_requested":
        return "bg-orange-100 text-orange-700";
      default:
        return "bg-slate-100 text-slate-700";
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "low":
        return "text-green-600";
      case "medium":
        return "text-yellow-600";
      case "high":
        return "text-orange-600";
      case "critical":
        return "text-red-600";
      default:
        return "text-slate-600";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200">
      {/* Officer Navbar */}
      <nav className="bg-gradient-to-r from-blue-900 to-blue-800 text-white p-4 sticky top-0 z-50 shadow-xl">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <FileText size={22} />
            </div>
            <span className="font-bold text-xl tracking-wide">
              OFFICER DASHBOARD
            </span>
          </div>
          <button
            onClick={fetchDashboard}
            className="p-2 hover:bg-blue-700 rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
          </button>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto p-8">
        {/* Success/Error Messages */}
        {success && (
          <div className="mb-4 p-4 bg-green-50 border-l-4 border-green-500 rounded-lg text-green-700 flex items-center gap-3 animate-fade-in-up">
            <CheckCircle size={20} />
            <div>{success}</div>
          </div>
        )}

        {error && (
          <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg text-red-700 flex items-center gap-3 animate-shake">
            <AlertIcon size={20} />
            <div>{error}</div>
          </div>
        )}

        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800">
            Active Grievances
          </h1>
          <p className="text-slate-500 mt-1">
            Manage and resolve assigned tickets
          </p>
        </header>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-2xl shadow-md border border-slate-200">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600">
                <FileText size={24} />
              </div>
              <div>
                <div className="text-3xl font-bold text-slate-800">
                  {ticketCounts.assigned}
                </div>
                <div className="text-sm text-slate-500">Assigned</div>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-md border border-slate-200">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center text-yellow-600">
                <Clock size={24} />
              </div>
              <div>
                <div className="text-3xl font-bold text-slate-800">
                  {ticketCounts.in_progress}
                </div>
                <div className="text-sm text-slate-500">In Progress</div>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-md border border-slate-200">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center text-green-600">
                <CheckCircle size={24} />
              </div>
              <div>
                <div className="text-3xl font-bold text-slate-800">
                  {ticketCounts.completed}
                </div>
                <div className="text-sm text-slate-500">Completed</div>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-2xl shadow-md border border-slate-200">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center text-orange-600">
                <MessageSquare size={24} />
              </div>
              <div>
                <div className="text-3xl font-bold text-slate-800">
                  {ticketCounts.clarifications}
                </div>
                <div className="text-sm text-slate-500">Clarifications</div>
              </div>
            </div>
          </div>
        </div>

        {/* Resolved Tickets Section */}
        {resolvedTickets.length > 0 && (
          <div className="mb-8 bg-white rounded-2xl shadow-md border border-slate-200 overflow-hidden">
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-slate-200 p-6">
              <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                <CheckCircle className="text-green-600" size={24} />
                Resolved Tickets ({resolvedTickets.length})
              </h2>
              <p className="text-slate-600 text-sm mt-1">
                Recently completed and resolved grievances
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase">
                      Ticket ID
                    </th>
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase">
                      Priority
                    </th>
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase">
                      Resolved At
                    </th>
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase">
                      Duration
                    </th>
                    <th className="p-4 text-xs font-bold text-slate-500 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {resolvedTickets.map((item) => (
                    <tr
                      key={item.ticket.grievance_id}
                      className="hover:bg-green-50 transition-colors"
                    >
                      <td className="p-4 font-mono text-sm font-bold text-slate-800">
                        {item.ticket.grievance_id}
                      </td>
                      <td className="p-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-bold ${getPriorityColor(
                            item.ticket.priority_level
                          )}`}
                        >
                          {item.ticket.priority_level?.toUpperCase()}
                        </span>
                      </td>
                      <td className="p-4 text-sm text-slate-600">
                        {item.ticket.resolved_at
                          ? new Date(item.ticket.resolved_at).toLocaleString()
                          : "-"}
                      </td>
                      <td className="p-4 text-sm text-slate-600">
                        {item.ticket.assigned_at && item.ticket.resolved_at
                          ? `${Math.round(
                              (new Date(item.ticket.resolved_at) -
                                new Date(item.ticket.assigned_at)) /
                                (1000 * 60 * 60)
                            )}h`
                          : "-"}
                      </td>
                      <td className="p-4">
                        <button
                          onClick={() => viewTicketDetails(item)}
                          className="p-2 text-green-600 hover:bg-green-100 rounded-lg transition-colors"
                          title="View Details"
                        >
                          <Eye size={18} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tickets Table */}
        <div className="bg-white rounded-2xl shadow-md border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="bg-gradient-to-r from-slate-50 to-slate-100 border-b border-slate-200">
                <tr>
                  <th className="p-4 text-xs font-bold text-slate-500 uppercase">
                    Ticket ID
                  </th>
                  <th className="p-4 text-xs font-bold text-slate-500 uppercase">
                    Priority
                  </th>
                  <th className="p-4 text-xs font-bold text-slate-500 uppercase">
                    Status
                  </th>
                  <th className="p-4 text-xs font-bold text-slate-500 uppercase">
                    Assigned At
                  </th>
                  <th className="p-4 text-xs font-bold text-slate-500 uppercase">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan="5" className="p-8 text-center">
                      <div className="flex items-center justify-center gap-3">
                        <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-600 border-t-transparent"></div>
                        <span className="text-slate-500">
                          Loading tickets...
                        </span>
                      </div>
                    </td>
                  </tr>
                ) : tickets.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="p-8 text-center text-slate-500">
                      No tickets assigned yet.
                    </td>
                  </tr>
                ) : (
                  tickets.map((item) => (
                    <tr
                      key={item.ticket.grievance_id}
                      className="hover:bg-blue-50 transition-colors"
                    >
                      <td className="p-4 font-mono text-sm font-bold text-slate-800">
                        {item.ticket.grievance_id}
                      </td>
                      <td className="p-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-bold ${getPriorityColor(
                            item.ticket.priority_level
                          )}`}
                        >
                          {item.ticket.priority_level?.toUpperCase()}
                        </span>
                      </td>
                      <td className="p-4">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusColor(
                            item.ticket.status
                          )}`}
                        >
                          {item.ticket.status?.replace("_", " ").toUpperCase()}
                        </span>
                      </td>
                      <td className="p-4 text-sm text-slate-600">
                        {new Date(item.ticket.assigned_at).toLocaleString()}
                      </td>
                      <td className="p-4">
                        <div className="flex gap-2">
                          <button
                            onClick={() => viewTicketDetails(item)}
                            className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
                            title="View Details"
                          >
                            <Eye size={18} />
                          </button>
                          {item.ticket.status === "assigned" && (
                            <button
                              onClick={() =>
                                handleStatusUpdate(
                                  item.ticket.grievance_id,
                                  "in_progress"
                                )
                              }
                              disabled={statusUpdateLoading}
                              className="p-2 text-green-600 hover:bg-green-100 rounded-lg transition-colors"
                              title="Start Work"
                            >
                              <PlayCircle size={18} />
                            </button>
                          )}
                          {item.ticket.status === "in_progress" && (
                            <>
                              <button
                                onClick={() => openClarificationModal(item)}
                                className="p-2 text-orange-600 hover:bg-orange-100 rounded-lg transition-colors"
                                title="Request Clarification"
                              >
                                <MessageSquare size={18} />
                              </button>
                              <button
                                onClick={() => openResolveModal(item)}
                                className="p-2 text-green-600 hover:bg-green-100 rounded-lg transition-colors"
                                title="Resolve Ticket"
                              >
                                <CheckCircle size={18} />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Ticket Details Panel */}
        {selectedTicket && !showResolveModal && !showClarificationModal && (
          <div className="mt-6 bg-white rounded-2xl shadow-lg border border-slate-200 p-6 animate-fade-in-up">
            <div className="flex justify-between items-start mb-6">
              <h3 className="text-xl font-bold text-slate-800">
                Ticket Details
              </h3>
              <button
                onClick={() => setSelectedTicket(null)}
                className="text-slate-400 hover:text-red-500 text-2xl"
              >
                ×
              </button>
            </div>

            {selectedTicket.urgency_banner && (
              <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertTriangle
                    className="text-red-600 flex-shrink-0"
                    size={20}
                  />
                  <div className="text-red-700 font-medium">
                    {selectedTicket.urgency_banner}
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div className="space-y-4">
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-xs text-slate-500 uppercase font-bold mb-1">
                    Grievance ID
                  </div>
                  <div className="font-mono text-slate-800">
                    {selectedTicket.ticket.grievance_id}
                  </div>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-xs text-slate-500 uppercase font-bold mb-1">
                    Priority
                  </div>
                  <div
                    className={`font-bold ${getPriorityColor(
                      selectedTicket.ticket.priority_level
                    )}`}
                  >
                    {selectedTicket.ticket.priority_level?.toUpperCase()}
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-xs text-slate-500 uppercase font-bold mb-1">
                    Status
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusColor(
                      selectedTicket.ticket.status
                    )}`}
                  >
                    {selectedTicket.ticket.status
                      ?.replace("_", " ")
                      .toUpperCase()}
                  </span>
                </div>
                <div className="p-4 bg-slate-50 rounded-lg">
                  <div className="text-xs text-slate-500 uppercase font-bold mb-1">
                    Assigned At
                  </div>
                  <div className="text-slate-800">
                    {new Date(
                      selectedTicket.ticket.assigned_at
                    ).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>

            {selectedTicket.context_panel && (
              <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="text-xs font-bold text-blue-500 uppercase mb-2">
                  Context
                </div>
                <div className="text-blue-900">
                  {selectedTicket.context_panel}
                </div>
              </div>
            )}

            {selectedTicket.cluster_summary && (
              <div className="mb-6 p-4 bg-purple-50 rounded-lg border border-purple-200">
                <div className="text-xs font-bold text-purple-500 uppercase mb-2 flex items-center gap-2">
                  <Layers size={14} /> Cluster Summary
                </div>
                <div className="text-purple-900">
                  {selectedTicket.cluster_summary}
                </div>
              </div>
            )}

            {selectedTicket.media_gallery &&
              selectedTicket.media_gallery.length > 0 && (
                <div className="mb-6">
                  <div className="text-xs font-bold text-slate-500 uppercase mb-3 flex items-center gap-2">
                    <ImageIcon size={14} /> Evidence Gallery
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {selectedTicket.media_gallery.map((url, idx) => (
                      <div
                        key={idx}
                        className="aspect-square bg-slate-100 rounded-lg overflow-hidden"
                      >
                        <img
                          src={url}
                          alt={`Evidence ${idx + 1}`}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}

            {selectedTicket.ticket.priority_reasoning && (
              <div className="p-4 bg-slate-50 rounded-lg">
                <div className="text-xs font-bold text-slate-500 uppercase mb-2">
                  AI Priority Reasoning
                </div>
                <div className="text-slate-700">
                  {selectedTicket.ticket.priority_reasoning}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* RESOLVE TICKET MODAL */}
      {showResolveModal && selectedTicket && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in-up">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden">
            <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-6 flex justify-between items-center">
              <h3 className="font-bold text-xl flex items-center gap-3">
                <CheckCircle size={24} /> Resolve Ticket
              </h3>
              <button
                onClick={() => setShowResolveModal(false)}
                className="hover:bg-white/20 p-2 rounded-lg transition-colors"
              >
                <XCircle size={24} />
              </button>
            </div>

            <form onSubmit={handleResolveTicket} className="p-6 space-y-6">
              <div className="p-4 bg-slate-50 rounded-lg">
                <div className="text-sm text-slate-500">Resolving ticket:</div>
                <div className="font-mono font-bold text-slate-800">
                  {selectedTicket.ticket.grievance_id}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                  Action Taken *
                </label>
                <textarea
                  value={resolveForm.action_taken}
                  onChange={(e) =>
                    setResolveForm({
                      ...resolveForm,
                      action_taken: e.target.value,
                    })
                  }
                  placeholder="Describe the action taken to resolve this issue..."
                  required
                  rows={4}
                  className="w-full p-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 bg-slate-50"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                  Closing Remark *
                </label>
                <textarea
                  value={resolveForm.closing_remark}
                  onChange={(e) =>
                    setResolveForm({
                      ...resolveForm,
                      closing_remark: e.target.value,
                    })
                  }
                  placeholder="Final remarks and resolution summary..."
                  required
                  rows={3}
                  className="w-full p-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 bg-slate-50"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                  Resolution Photos (Proof) *
                </label>
                <div className="border-2 border-dashed border-slate-200 rounded-lg p-6 text-center hover:border-green-500 transition-colors">
                  <Upload className="mx-auto text-slate-400 mb-2" size={32} />
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={handleFileChange}
                    required
                    className="w-full"
                  />
                  <p className="text-sm text-slate-500 mt-2">
                    Upload photos showing the resolved issue
                  </p>
                  {resolveForm.resolution_photos.length > 0 && (
                    <div className="mt-3 text-sm font-bold text-green-600">
                      {resolveForm.resolution_photos.length} file(s) selected
                    </div>
                  )}
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={resolveLoading}
                  className="flex-1 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white py-3 rounded-xl font-bold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {resolveLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                      Resolving...
                    </>
                  ) : (
                    <>
                      <CheckCircle size={20} /> Resolve Ticket
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => setShowResolveModal(false)}
                  className="px-6 py-3 border-2 border-slate-200 text-slate-700 rounded-xl font-bold hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* RESOLVED TICKET DETAILS MODAL */}
      {showResolvedDetailsModal && selectedTicket && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in-up overflow-y-auto">
          <div className="bg-gradient-to-br from-slate-50 to-green-50 rounded-2xl shadow-2xl w-full max-w-5xl my-8 overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white p-6 flex justify-between items-center sticky top-0 z-10">
              <div>
                <h3 className="font-bold text-2xl flex items-center gap-3">
                  <CheckCircle size={28} /> Resolved Ticket Details
                </h3>
                <p className="text-green-100 text-sm mt-1">
                  Complete information about resolved grievance
                </p>
              </div>
              <button
                onClick={() => setShowResolvedDetailsModal(false)}
                className="hover:bg-white/20 p-2 rounded-lg transition-colors"
              >
                <XCircle size={28} />
              </button>
            </div>

            <div className="p-6 space-y-6 max-h-[80vh] overflow-y-auto">
              {/* Ticket ID & Status */}
              <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-600">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-slate-500 uppercase font-bold mb-2 flex items-center gap-2">
                      <FileText size={14} /> Ticket ID
                    </div>
                    <div className="font-mono text-2xl font-bold text-slate-800 bg-slate-50 p-3 rounded-lg">
                      {selectedTicket.ticket.grievance_id}
                    </div>
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 uppercase font-bold mb-2">
                      Status
                    </div>
                    <span
                      className={`inline-flex px-4 py-2 rounded-full text-sm font-bold ${getStatusColor(
                        selectedTicket.ticket.status
                      )}`}
                    >
                      {selectedTicket.ticket.status
                        ?.replace("_", " ")
                        .toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Urgency Banner */}
              {selectedTicket.urgency_banner && (
                <div className="bg-gradient-to-r from-red-50 to-orange-50 border-l-4 border-red-500 rounded-xl p-6 shadow-md">
                  <div className="flex items-start gap-3">
                    <AlertTriangle
                      className="text-red-600 flex-shrink-0"
                      size={24}
                    />
                    <div>
                      <div className="text-xs font-bold text-red-500 uppercase mb-2">
                        Urgency Alert
                      </div>
                      <div className="text-red-900 font-medium text-lg">
                        {selectedTicket.urgency_banner}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Priority & Timeline Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white rounded-xl shadow-md p-5 border-t-4 border-blue-500">
                  <div className="text-xs text-slate-500 uppercase font-bold mb-2 flex items-center gap-2">
                    <AlertIcon size={14} /> Priority Level
                  </div>
                  <div
                    className={`text-2xl font-bold ${getPriorityColor(
                      selectedTicket.ticket.priority_level
                    )}`}
                  >
                    {selectedTicket.ticket.priority_level?.toUpperCase()}
                  </div>
                  {selectedTicket.ticket.priority_reasoning && (
                    <div className="mt-3 p-3 bg-slate-50 rounded-lg text-sm text-slate-700">
                      {selectedTicket.ticket.priority_reasoning}
                    </div>
                  )}
                </div>

                <div className="bg-white rounded-xl shadow-md p-5 border-t-4 border-green-500">
                  <div className="text-xs text-slate-500 uppercase font-bold mb-3 flex items-center gap-2">
                    <Clock size={14} /> Timeline
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between items-center p-2 bg-blue-50 rounded">
                      <span className="text-slate-600">Assigned:</span>
                      <span className="font-bold text-slate-800">
                        {new Date(
                          selectedTicket.ticket.assigned_at
                        ).toLocaleString()}
                      </span>
                    </div>
                    {selectedTicket.ticket.started_at && (
                      <div className="flex justify-between items-center p-2 bg-yellow-50 rounded">
                        <span className="text-slate-600">Started:</span>
                        <span className="font-bold text-slate-800">
                          {new Date(
                            selectedTicket.ticket.started_at
                          ).toLocaleString()}
                        </span>
                      </div>
                    )}
                    {selectedTicket.ticket.resolved_at && (
                      <div className="flex justify-between items-center p-2 bg-green-50 rounded">
                        <span className="text-slate-600">Resolved:</span>
                        <span className="font-bold text-slate-800">
                          {new Date(
                            selectedTicket.ticket.resolved_at
                          ).toLocaleString()}
                        </span>
                      </div>
                    )}
                    {selectedTicket.ticket.assigned_at &&
                      selectedTicket.ticket.resolved_at && (
                        <div className="mt-3 p-3 bg-gradient-to-r from-green-100 to-emerald-100 rounded-lg border border-green-300">
                          <div className="text-xs text-green-700 font-bold uppercase mb-1">
                            Total Duration
                          </div>
                          <div className="text-2xl font-bold text-green-800">
                            {Math.round(
                              (new Date(selectedTicket.ticket.resolved_at) -
                                new Date(selectedTicket.ticket.assigned_at)) /
                                (1000 * 60 * 60)
                            )}{" "}
                            hours
                          </div>
                        </div>
                      )}
                  </div>
                </div>
              </div>

              {/* Context Panel */}
              {selectedTicket.context_panel && (
                <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
                  <div className="text-xs font-bold text-blue-600 uppercase mb-3 flex items-center gap-2">
                    <FileText size={16} /> Context Information
                  </div>
                  <div className="text-slate-800 leading-relaxed text-lg bg-blue-50 p-4 rounded-lg">
                    {selectedTicket.context_panel}
                  </div>
                </div>
              )}

              {/* Cluster Summary */}
              {selectedTicket.cluster_summary && (
                <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-500">
                  <div className="text-xs font-bold text-purple-600 uppercase mb-3 flex items-center gap-2">
                    <Layers size={16} /> Cluster Analysis
                  </div>
                  <div className="text-slate-800 leading-relaxed text-lg bg-purple-50 p-4 rounded-lg">
                    {selectedTicket.cluster_summary}
                  </div>
                </div>
              )}

              {/* Cluster Info */}
              {selectedTicket.ticket.cluster_info &&
                Object.keys(selectedTicket.ticket.cluster_info).length > 0 && (
                  <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-indigo-500">
                    <div className="text-xs font-bold text-indigo-600 uppercase mb-3 flex items-center gap-2">
                      <Layers size={16} /> Cluster Details
                    </div>
                    <div className="bg-indigo-50 p-4 rounded-lg">
                      <pre className="text-sm text-slate-800 overflow-x-auto">
                        {JSON.stringify(
                          selectedTicket.ticket.cluster_info,
                          null,
                          2
                        )}
                      </pre>
                    </div>
                  </div>
                )}

              {/* Media Gallery */}
              {selectedTicket.media_gallery &&
                selectedTicket.media_gallery.length > 0 && (
                  <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-pink-500">
                    <div className="text-xs font-bold text-pink-600 uppercase mb-4 flex items-center gap-2">
                      <ImageIcon size={16} /> Evidence Gallery (
                      {selectedTicket.media_gallery.length} items)
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                      {selectedTicket.media_gallery.map((url, idx) => (
                        <div
                          key={idx}
                          className="group relative aspect-square bg-slate-100 rounded-lg overflow-hidden shadow-md hover:shadow-xl transition-all cursor-pointer"
                        >
                          <img
                            src={url}
                            alt={`Evidence ${idx + 1}`}
                            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                            onClick={() => window.open(url, "_blank")}
                          />
                          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all flex items-center justify-center">
                            <Eye
                              className="text-white opacity-0 group-hover:opacity-100 transition-opacity"
                              size={24}
                            />
                          </div>
                          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-2">
                            <span className="text-white text-xs font-bold">
                              Image {idx + 1}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              {/* Original Documents */}
              {selectedTicket.ticket.original_documents &&
                selectedTicket.ticket.original_documents.length > 0 && (
                  <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-teal-500">
                    <div className="text-xs font-bold text-teal-600 uppercase mb-4 flex items-center gap-2">
                      <FileText size={16} /> Original Documents (
                      {selectedTicket.ticket.original_documents.length})
                    </div>
                    <div className="space-y-2">
                      {selectedTicket.ticket.original_documents.map(
                        (doc, idx) => (
                          <div
                            key={idx}
                            className="flex items-center gap-3 p-3 bg-teal-50 rounded-lg hover:bg-teal-100 transition-colors"
                          >
                            <FileText className="text-teal-600" size={20} />
                            <span className="text-slate-800 flex-1">
                              Document {idx + 1}
                            </span>
                            <button className="px-4 py-2 bg-teal-600 text-white rounded-lg text-sm font-bold hover:bg-teal-700 transition-colors">
                              View
                            </button>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

              {/* Close Button */}
              <div className="flex justify-end pt-4">
                <button
                  onClick={() => setShowResolvedDetailsModal(false)}
                  className="px-8 py-3 bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-700 hover:to-slate-800 text-white rounded-xl font-bold shadow-lg hover:shadow-xl transition-all"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* REQUEST CLARIFICATION MODAL */}
      {showClarificationModal && selectedTicket && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in-up">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
            <div className="bg-gradient-to-r from-orange-600 to-orange-700 text-white p-6 flex justify-between items-center">
              <h3 className="font-bold text-xl flex items-center gap-3">
                <MessageSquare size={24} /> Request Clarification
              </h3>
              <button
                onClick={() => setShowClarificationModal(false)}
                className="hover:bg-white/20 p-2 rounded-lg transition-colors"
              >
                <XCircle size={24} />
              </button>
            </div>

            <form
              onSubmit={handleRequestClarification}
              className="p-6 space-y-6"
            >
              <div className="p-4 bg-slate-50 rounded-lg">
                <div className="text-sm text-slate-500">
                  Requesting clarification for:
                </div>
                <div className="font-mono font-bold text-slate-800">
                  {selectedTicket.ticket.grievance_id}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
                  Message to Citizen *
                </label>
                <textarea
                  value={clarificationForm.message}
                  onChange={(e) =>
                    setClarificationForm({
                      ...clarificationForm,
                      message: e.target.value,
                    })
                  }
                  placeholder="What additional information do you need from the citizen?"
                  required
                  rows={5}
                  className="w-full p-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 bg-slate-50"
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={clarificationLoading}
                  className="flex-1 bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 text-white py-3 rounded-xl font-bold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {clarificationLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send size={20} /> Send Request
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => setShowClarificationModal(false)}
                  className="px-6 py-3 border-2 border-slate-200 text-slate-700 rounded-xl font-bold hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
