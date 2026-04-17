"""
Admin Panel for Type 1 Diabetes Prediction System
Provides centralized dashboard to view all user and patient records
Includes CSV export functionality
"""

import os
import csv
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from io import StringIO, BytesIO

# Use absolute paths
APP_DIR = Path(__file__).parent
USERS_FILE = APP_DIR / "users.xlsx"
PATIENT_RECORDS_FILE = APP_DIR / "patient_records.xlsx"
CSV_EXPORT_DIR = APP_DIR / "exports"

# Create exports directory if it doesn't exist
CSV_EXPORT_DIR.mkdir(exist_ok=True)


def load_users_data():
    """Load all user records from Excel"""
    try:
        if USERS_FILE.exists():
            df = pd.read_excel(USERS_FILE)
            return df.to_dict('records')
        return []
    except Exception as e:
        print(f"Error loading users: {e}")
        return []


def load_patient_records():
    """Load all patient records from Excel"""
    try:
        if PATIENT_RECORDS_FILE.exists():
            df = pd.read_excel(PATIENT_RECORDS_FILE)
            return df.to_dict('records')
        return []
    except Exception as e:
        print(f"Error loading patient records: {e}")
        return []


def export_to_csv(data, filename, file_type="records"):
    """Export data to CSV file"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{filename}_{timestamp}.csv"
        file_path = CSV_EXPORT_DIR / file_name
        
        # Convert to DataFrame and save
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        
        return {
            "success": True,
            "message": f"Exported {len(data)} {file_type} to {file_name}",
            "file_path": str(file_path),
            "file_name": file_name
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error exporting data: {str(e)}"
        }


def get_admin_stats():
    """Get statistics about users and records"""
    users = load_users_data()
    records = load_patient_records()
    
    return {
        "total_users": len(users),
        "total_records": len(records),
        "high_risk_count": len([r for r in records if r.get("risk_level") == "HIGH"]),
        "moderate_risk_count": len([r for r in records if r.get("risk_level") == "MODERATE"]),
        "low_risk_count": len([r for r in records if r.get("risk_level") == "LOW"]),
        "records_today": len([r for r in records if isinstance(r.get("date"), str) and datetime.now().strftime("%Y-%m-%d") in str(r.get("date", ""))])
    }


def create_admin_html():
    """Generate admin dashboard HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Dashboard - T1D Prediction System</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            .high-risk { background: #fee2e2; color: #991b1b; }
            .moderate-risk { background: #fef3c7; color: #92400e; }
            .low-risk { background: #dcfce7; color: #166534; }
        </style>
    </head>
    <body class="bg-gray-100">
        <div class="min-h-screen">
            <!-- Header -->
            <div class="bg-[#0F6C74] text-white p-6 shadow-lg">
                <div class="max-w-7xl mx-auto">
                    <h1 class="text-3xl font-bold">Admin Dashboard</h1>
                    <p class="text-blue-100 mt-1">Type 1 Diabetes Prediction System - Centralized Records</p>
                </div>
            </div>

            <!-- Main Content -->
            <div class="max-w-7xl mx-auto p-6">
                
                <!-- Statistics -->
                <div class="grid grid-cols-4 gap-4 mb-8">
                    <div class="bg-white rounded-lg shadow p-6">
                        <p class="text-gray-600 text-sm">Total Users</p>
                        <p class="text-3xl font-bold text-[#0F6C74]" id="total-users">0</p>
                    </div>
                    <div class="bg-white rounded-lg shadow p-6">
                        <p class="text-gray-600 text-sm">Total Records</p>
                        <p class="text-3xl font-bold text-blue-600" id="total-records">0</p>
                    </div>
                    <div class="bg-red-50 rounded-lg shadow p-6 high-risk">
                        <p class="text-sm font-semibold">High Risk Cases</p>
                        <p class="text-3xl font-bold" id="high-risk">0</p>
                    </div>
                    <div class="bg-yellow-50 rounded-lg shadow p-6 moderate-risk">
                        <p class="text-sm font-semibold">Moderate Risk Cases</p>
                        <p class="text-3xl font-bold" id="moderate-risk">0</p>
                    </div>
                </div>

                <!-- Tabs -->
                <div class="bg-white rounded-lg shadow mb-6">
                    <div class="flex border-b">
                        <button onclick="showTab('users')" class="px-6 py-4 font-semibold text-[#0F6C74] border-b-2 border-[#0F6C74]" id="users-tab">
                            Users
                        </button>
                        <button onclick="showTab('records')" class="px-6 py-4 font-semibold text-gray-600 border-b-2 border-transparent hover:text-[#0F6C74]" id="records-tab">
                            Patient Records
                        </button>
                    </div>

                    <!-- Users Tab -->
                    <div id="users-content" class="p-6">
                        <div class="flex justify-between items-center mb-4">
                            <h2 class="text-xl font-bold">All Registered Users</h2>
                            <button onclick="exportUsers()" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                                📥 Export to CSV
                            </button>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-sm">
                                <thead class="bg-gray-100">
                                    <tr>
                                        <th class="px-4 py-2 text-left">Email</th>
                                        <th class="px-4 py-2 text-left">Registered Date</th>
                                        <th class="px-4 py-2 text-left">Status</th>
                                    </tr>
                                </thead>
                                <tbody id="users-table">
                                    <tr><td colspan="3" class="px-4 py-2 text-center">Loading...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Records Tab -->
                    <div id="records-content" class="p-6 hidden">
                        <div class="flex justify-between items-center mb-4">
                            <h2 class="text-xl font-bold">Patient Screening Records</h2>
                            <button onclick="exportRecords()" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                                📥 Export to CSV
                            </button>
                        </div>
                        <div class="overflow-x-auto">
                            <table class="w-full text-sm">
                                <thead class="bg-gray-100">
                                    <tr>
                                        <th class="px-4 py-2 text-left">Record ID</th>
                                        <th class="px-4 py-2 text-left">User Email</th>
                                        <th class="px-4 py-2 text-left">Risk Level</th>
                                        <th class="px-4 py-2 text-left">Confidence</th>
                                        <th class="px-4 py-2 text-left">Date</th>
                                        <th class="px-4 py-2 text-left">Glucose</th>
                                        <th class="px-4 py-2 text-left">Ketones</th>
                                        <th class="px-4 py-2 text-left">BMI</th>
                                    </tr>
                                </thead>
                                <tbody id="records-table">
                                    <tr><td colspan="8" class="px-4 py-2 text-center">Loading...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- Export Status -->
                <div id="export-status" class="hidden bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4">
                    <span id="status-message"></span>
                </div>

            </div>
        </div>

        <script>
            function showTab(tab) {
                // Hide all tabs
                document.getElementById('users-content').classList.add('hidden');
                document.getElementById('records-content').classList.add('hidden');
                document.getElementById('users-tab').classList.remove('border-[#0F6C74]', 'border-b-2', 'text-[#0F6C74]');
                document.getElementById('records-tab').classList.remove('border-[#0F6C74]', 'border-b-2', 'text-[#0F6C74]');

                // Show selected tab
                document.getElementById(tab + '-content').classList.remove('hidden');
                document.getElementById(tab + '-tab').classList.add('border-[#0F6C74]', 'border-b-2', 'text-[#0F6C74]');

                // Load data
                if (tab === 'users') {
                    loadUsers();
                } else {
                    loadRecords();
                }
            }

            function loadStats() {
                fetch('/api/admin/stats')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('total-users').textContent = data.total_users;
                        document.getElementById('total-records').textContent = data.total_records;
                        document.getElementById('high-risk').textContent = data.high_risk_count;
                        document.getElementById('moderate-risk').textContent = data.moderate_risk_count;
                    });
            }

            function loadUsers() {
                fetch('/api/admin/users')
                    .then(r => r.json())
                    .then(data => {
                        let html = '';
                        data.forEach(user => {
                            html += `
                                <tr class="border-b hover:bg-gray-50">
                                    <td class="px-4 py-2">${user.username || 'N/A'}</td>
                                    <td class="px-4 py-2">${user.registration_date || 'N/A'}</td>
                                    <td class="px-4 py-2"><span class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">Active</span></td>
                                </tr>
                            `;
                        });
                        document.getElementById('users-table').innerHTML = html || '<tr><td colspan="3" class="px-4 py-2 text-center text-gray-500">No users found</td></tr>';
                    });
            }

            function loadRecords() {
                fetch('/api/admin/records')
                    .then(r => r.json())
                    .then(data => {
                        let html = '';
                        data.forEach((record, idx) => {
                            const riskClass = record.risk_level === 'HIGH' ? 'high-risk' : record.risk_level === 'MODERATE' ? 'moderate-risk' : 'low-risk';
                            html += `
                                <tr class="border-b hover:bg-gray-50">
                                    <td class="px-4 py-2">${record.Record_ID || idx}</td>
                                    <td class="px-4 py-2">${record.User_Email || 'N/A'}</td>
                                    <td class="px-4 py-2"><span class="${riskClass} px-2 py-1 rounded text-xs font-semibold">${record.risk_level || 'N/A'}</span></td>
                                    <td class="px-4 py-2">${record.Model_Confidence ? (record.Model_Confidence * 100).toFixed(1) + '%' : 'N/A'}</td>
                                    <td class="px-4 py-2">${record.Date_of_Screening || 'N/A'}</td>
                                    <td class="px-4 py-2">${record.glucose_class || 'N/A'}</td>
                                    <td class="px-4 py-2">${record.ketone_class || 'N/A'}</td>
                                    <td class="px-4 py-2">${record.bmi_class || 'N/A'}</td>
                                </tr>
                            `;
                        });
                        document.getElementById('records-table').innerHTML = html || '<tr><td colspan="8" class="px-4 py-2 text-center text-gray-500">No records found</td></tr>';
                    });
            }

            function exportUsers() {
                fetch('/api/admin/export/users')
                    .then(r => r.json())
                    .then(data => {
                        showStatus(data.message);
                    });
            }

            function exportRecords() {
                fetch('/api/admin/export/records')
                    .then(r => r.json())
                    .then(data => {
                        showStatus(data.message);
                    });
            }

            function showStatus(message) {
                document.getElementById('status-message').textContent = message;
                document.getElementById('export-status').classList.remove('hidden');
                setTimeout(() => {
                    document.getElementById('export-status').classList.add('hidden');
                }, 5000);
            }

            // Load on page load
            window.onload = () => {
                loadStats();
                loadUsers();
            };
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    print("Admin module loaded. Add these routes to your Flask app.")
