// complaints.js - Complaint modal inspection & status workflow

async function viewComplaintDetails(complaintId) {
  const modal = document.getElementById("detailModal");
  if (!modal) return;

  try {
    const res = await fetch(`/api/complaint/${complaintId}`);
    const data = await res.json();
    if (!data.success || !data.complaint) {
      alert("Complaint details could not be retrieved.");
      return;
    }

    const c = data.complaint;
    document.getElementById("modalComplaintId").textContent = `#${c.complaint_code}`;
    document.getElementById("modalTitle").textContent = c.title;
    document.getElementById("modalDescription").textContent = c.description;
    document.getElementById("modalStudent").textContent = `${c.student_name} (${c.student_id})`;
    document.getElementById("modalContact").textContent = `${c.student_phone || 'N/A'} • ${c.student_email || 'N/A'}`;
    document.getElementById("modalLocation").textContent = `${c.block} • Room ${c.room_number}`;
    document.getElementById("modalCategory").textContent = c.category;
    document.getElementById("modalSubmitted").textContent = c.created_at;
    document.getElementById("modalAssignee").textContent = c.assigned_to || "Unassigned";

    // Status Badge
    const statusEl = document.getElementById("modalStatusBadge");
    const statusClasses = {
      "Resolved": "badge-resolved",
      "Pending": "badge-pending",
      "In Progress": "badge-in-progress",
      "Rejected": "badge-rejected"
    };
    statusEl.className = `badge ${statusClasses[c.status] || 'badge-pending'}`;
    statusEl.innerHTML = `<span class="badge-dot"></span>${c.status}`;

    // Priority Tag
    const prioEl = document.getElementById("modalPriorityTag");
    const prioClasses = {
      "Critical": "priority-critical",
      "High": "priority-high",
      "Medium": "priority-medium",
      "Low": "priority-low"
    };
    prioEl.className = `priority-tag ${prioClasses[c.severity] || 'priority-medium'}`;
    prioEl.textContent = c.severity;

    // Resolution details
    const resSection = document.getElementById("modalResolutionSection");
    if (c.status === "Resolved" && c.resolved_at) {
      resSection.style.display = "block";
      document.getElementById("modalResolvedAt").textContent = `${c.resolved_at} (${c.resolution_time_days || '0'} days taken)`;
      document.getElementById("modalResolutionNotes").textContent = c.resolution_notes || "No additional notes.";
    } else {
      resSection.style.display = "none";
    }

    // Prepare quick action button in detail modal
    const updateBtn = document.getElementById("modalUpdateStatusBtn");
    if (updateBtn) {
      updateBtn.onclick = () => {
        closeModal("detailModal");
        openStatusModal(c.complaint_code, c.status, c.resolution_notes, c.assigned_to);
      };
    }

    modal.classList.add("active");
  } catch (err) {
    console.error("Error fetching complaint:", err);
  }
}

function openStatusModal(complaintCode, currentStatus, currentNotes = "", currentAssignee = "") {
  const modal = document.getElementById("statusModal");
  if (!modal) return;

  document.getElementById("statusModalCode").textContent = `#${complaintCode}`;
  document.getElementById("statusInputCode").value = complaintCode;
  document.getElementById("statusSelect").value = currentStatus || "Pending";
  document.getElementById("statusNotes").value = currentNotes || "";
  document.getElementById("statusAssignee").value = currentAssignee || "";

  toggleResolutionNotesField();
  modal.classList.add("active");
}

function toggleResolutionNotesField() {
  const statusSelect = document.getElementById("statusSelect");
  const notesContainer = document.getElementById("resolutionNotesContainer");
  if (!statusSelect || !notesContainer) return;

  if (statusSelect.value === "Resolved" || statusSelect.value === "Rejected") {
    notesContainer.style.display = "flex";
  } else {
    notesContainer.style.display = "flex"; // Keep accessible for audit notes
  }
}

async function submitStatusUpdate(e) {
  if (e) e.preventDefault();

  const code = document.getElementById("statusInputCode").value;
  const status = document.getElementById("statusSelect").value;
  const notes = document.getElementById("statusNotes").value;
  const assignee = document.getElementById("statusAssignee").value;

  try {
    const res = await fetch(`/api/complaint/${code}/update-status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        status: status,
        resolution_notes: notes,
        assigned_to: assignee
      })
    });

    const data = await res.json();
    if (data.success) {
      closeModal("statusModal");
      showToast(data.message, "success");
      // Reload page to reflect new status and metrics
      setTimeout(() => window.location.reload(), 600);
    } else {
      alert(data.message || "Failed to update complaint");
    }
  } catch (err) {
    console.error("Error updating status:", err);
    alert("Network error updating status.");
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("active");
  }
}

// Modal event listeners
document.addEventListener("DOMContentLoaded", () => {
  const overlays = document.querySelectorAll(".modal-overlay");
  overlays.forEach((overlay) => {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        overlay.classList.remove("active");
      }
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      overlays.forEach((o) => o.classList.remove("active"));
    }
  });

  const statusForm = document.getElementById("statusUpdateForm");
  if (statusForm) {
    statusForm.addEventListener("submit", submitStatusUpdate);
  }
});
