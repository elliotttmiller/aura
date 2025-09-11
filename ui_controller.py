"""
Aura V32 Ultimate Rhino-Native Environment - UI Controller
==========================================================

The definitive Eto-based UI controller that serves as the native Rhino 8 Plugin
interface for the V32 Ultimate system. This module provides the AI Chat sidebar
with real-time interaction and non-blocking operation.

Key Features:
- Eto.Forms.Panel-based interface native to Rhino 8
- AI Chat sidebar with scrollable text area and input controls
- Asynchronous threading for non-blocking UI operations
- Thread-safe UI updates using Rhino's main thread dispatcher
- Real-time feedback and viewport updates

Implements Protocol 10: The Native Rhino Imperative
Implements Protocol 11: The Eto Doctrine (Official UI Mandate)
Implements Protocol 12: Direct Kernel Execution (Real-Time Forge)
"""

import System
import Rhino
import Rhino.UI
import Eto.Forms as Forms
import Eto.Drawing as Drawing
import scriptcontext as sc
import rhinoscriptsyntax as rs
import threading
import json
import time
from System import EventHandler
from System.ComponentModel import BackgroundWorker, DoWorkEventArgs, ProgressChangedEventArgs

try:
    from orchestrator import RhinoOrchestrator
except ImportError:
    # Fallback for development
    RhinoOrchestrator = None


class AuraAiChatPanel(Forms.Panel):
    """
    Aura V32 AI Chat Panel - Native Eto Implementation
    
    The core UI component providing the AI chat interface within Rhino 8.
    Uses Eto framework for cross-platform native UI experience.
    """
    
    def __init__(self):
        super(AuraAiChatPanel, self).__init__()
        self.orchestrator = None
        self.background_worker = None
        
        # Initialize UI components
        self._create_ui()
        self._initialize_orchestrator()
        
        # Thread-safe message queue for UI updates
        self.message_queue = []
        self.update_timer = None
        
        print("🔮 Aura V32 AI Chat Panel initialized - Native Rhino UI ready")
    
    def _create_ui(self):
        """Create the Eto-based UI layout."""
        
        # Main layout container
        layout = Forms.DynamicLayout()
        layout.Spacing = Drawing.Size(5, 5)
        layout.Padding = Drawing.Padding(10)
        
        # Header section
        header_layout = Forms.DynamicLayout()
        header_layout.AddRow(self._create_header_controls())
        
        # Chat history display (scrollable text area)
        self.chat_display = Forms.TextArea()
        self.chat_display.ReadOnly = True
        self.chat_display.Wrap = True
        self.chat_display.Size = Drawing.Size(400, 300)
        self.chat_display.BackgroundColor = Drawing.Colors.White
        self.chat_display.Text = "🎨 Aura V32 AI Chat Ready\n\nEnter your jewelry design request below and click Generate to begin AI-driven creation.\n\nExample: 'Create a sleek, modern 18k white gold tension-set ring, size 6.5, holding a 1.25 carat princess-cut diamond with perfectly flat top profile and 1.8mm thickness.'\n"
        
        # Input section
        input_layout = Forms.DynamicLayout()
        
        # User prompt input
        self.prompt_input = Forms.TextArea()
        self.prompt_input.Size = Drawing.Size(400, 80)
        self.prompt_input.Wrap = True
        self.prompt_input.PlaceholderText = "Describe your jewelry design..."
        
        # Control buttons
        button_layout = Forms.DynamicLayout()
        button_layout.BeginHorizontal()
        
        self.generate_button = Forms.Button()
        self.generate_button.Text = "🔥 Generate Design"
        self.generate_button.Size = Drawing.Size(140, 30)
        self.generate_button.Click += self.on_generate_click
        
        self.clear_button = Forms.Button()
        self.clear_button.Text = "🔄 Clear Chat"
        self.clear_button.Size = Drawing.Size(100, 30)
        self.clear_button.Click += self.on_clear_click
        
        button_layout.Add(self.generate_button)
        button_layout.Add(self.clear_button)
        button_layout.EndHorizontal()
        
        # Add components to input layout
        input_layout.AddRow(Forms.Label() + "Design Request:")
        input_layout.AddRow(self.prompt_input)
        input_layout.AddRow(button_layout)
        
        # Assemble main layout
        layout.AddRow(header_layout)
        layout.AddRow(Forms.Label() + "AI Chat History:")
        layout.AddRow(self.chat_display)
        layout.AddRow(input_layout)
        
        # Set the panel content
        self.Content = layout
        
        print("✅ Eto UI layout created successfully")
    
    def _create_header_controls(self):
        """Create header controls and status indicators."""
        
        header_layout = Forms.DynamicLayout()
        header_layout.BeginHorizontal()
        
        # Aura V32 title
        title_label = Forms.Label()
        title_label.Text = "🔮 Aura V32 Ultimate"
        title_label.Font = Forms.Font(title_label.Font.FamilyName, 14, Drawing.FontStyle.Bold)
        
        # Status indicator
        self.status_label = Forms.Label()
        self.status_label.Text = "✅ Ready"
        self.status_label.TextColor = Drawing.Colors.Green
        
        header_layout.Add(title_label)
        header_layout.Add(None) # Spacer
        header_layout.Add(self.status_label)
        header_layout.EndHorizontal()
        
        return header_layout
    
    def _initialize_orchestrator(self):
        """Initialize the Rhino orchestrator for direct execution."""
        try:
            if RhinoOrchestrator:
                self.orchestrator = RhinoOrchestrator()
                self._append_to_chat("🏭 Rhino Orchestrator initialized - Direct kernel execution ready", "system")
            else:
                self._append_to_chat("⚠️ Orchestrator not available - Running in UI-only mode", "system")
        except Exception as e:
            self._append_to_chat(f"❌ Failed to initialize orchestrator: {str(e)}", "error")
    
    def on_generate_click(self, sender, e):
        """Handle the Generate button click event."""
        user_prompt = self.prompt_input.Text.strip()
        
        if not user_prompt:
            self._append_to_chat("⚠️ Please enter a design request", "warning")
            return
        
        if not self.orchestrator:
            self._append_to_chat("❌ Orchestrator not available - Cannot generate design", "error")
            return
        
        # Disable button to prevent multiple simultaneous requests
        self.generate_button.Enabled = False
        self.status_label.Text = "🔄 Processing..."
        self.status_label.TextColor = Drawing.Colors.Orange
        
        # Add user message to chat
        self._append_to_chat(f"👤 User: {user_prompt}", "user")
        
        # Clear the input
        self.prompt_input.Text = ""
        
        # Start background processing
        self._start_background_processing(user_prompt)
    
    def _start_background_processing(self, user_prompt):
        """Start AI processing in background thread using BackgroundWorker."""
        
        if self.background_worker and self.background_worker.IsBusy:
            self._append_to_chat("⚠️ Already processing a request", "warning")
            return
        
        # Create and configure background worker
        self.background_worker = BackgroundWorker()
        self.background_worker.WorkerReportsProgress = True
        self.background_worker.DoWork += EventHandler[DoWorkEventArgs](self._background_worker_do_work)
        self.background_worker.ProgressChanged += EventHandler[ProgressChangedEventArgs](self._background_worker_progress_changed)
        self.background_worker.RunWorkerCompleted += self._background_worker_completed
        
        # Start the work
        self.background_worker.RunWorkerAsync(user_prompt)
        
        print(f"🚀 Background processing started for: {user_prompt}")
    
    def _background_worker_do_work(self, sender, e):
        """Background worker thread - Execute AI orchestration."""
        user_prompt = e.Argument
        worker = sender
        
        try:
            # Phase 1: Analysis
            worker.ReportProgress(10, "🧠 AI Master Planner analyzing request...")
            
            # Phase 2: Construction Planning  
            worker.ReportProgress(25, "📐 Generating construction blueprint...")
            
            # Phase 3: Direct Rhino Execution
            worker.ReportProgress(50, "🏭 Executing directly in Rhino document...")
            
            # Execute the orchestrator
            if self.orchestrator:
                result = self.orchestrator.create_jewelry_design(user_prompt)
                e.Result = result
            else:
                # Simulate processing for UI testing
                time.sleep(2)
                e.Result = {
                    "success": True,
                    "message": "Design created successfully (simulation mode)",
                    "execution_time": 2.0
                }
            
            worker.ReportProgress(90, "✨ Finalizing and updating viewport...")
            worker.ReportProgress(100, "✅ Design generation complete!")
            
        except Exception as ex:
            e.Result = {
                "success": False,
                "error": str(ex)
            }
    
    def _background_worker_progress_changed(self, sender, e):
        """Handle progress updates from background worker."""
        progress_message = e.UserState
        if progress_message:
            # Update chat with progress
            self._append_to_chat(progress_message, "progress")
    
    def _background_worker_completed(self, sender, e):
        """Handle completion of background processing."""
        
        # Re-enable the generate button
        self.generate_button.Enabled = True
        self.status_label.Text = "✅ Ready"
        self.status_label.TextColor = Drawing.Colors.Green
        
        # Process the result
        if e.Error:
            self._append_to_chat(f"❌ Error during processing: {str(e.Error)}", "error")
        elif e.Result:
            result = e.Result
            if result.get("success", False):
                message = result.get("message", "Design created successfully")
                execution_time = result.get("execution_time", 0)
                self._append_to_chat(f"✅ {message}", "success")
                if execution_time > 0:
                    self._append_to_chat(f"⚡ Completed in {execution_time:.1f} seconds", "info")
                
                # Trigger viewport redraw
                sc.doc.Views.Redraw()
            else:
                error_msg = result.get("error", "Unknown error")
                self._append_to_chat(f"❌ Generation failed: {error_msg}", "error")
        else:
            self._append_to_chat("❌ No result returned from processing", "error")
        
        print("🏁 Background processing completed")
    
    def on_clear_click(self, sender, e):
        """Handle the Clear Chat button click event."""
        self.chat_display.Text = "🔮 Aura V32 AI Chat - Cleared\n\nReady for new design requests.\n"
        print("🔄 Chat history cleared")
    
    def _append_to_chat(self, message, message_type="info"):
        """
        Thread-safe method to append messages to chat display.
        
        Args:
            message: The message to display
            message_type: Type of message (info, user, progress, success, error, warning, system)
        """
        # Format timestamp
        timestamp = time.strftime("%H:%M:%S")
        
        # Format message based on type
        if message_type == "user":
            formatted_message = f"[{timestamp}] {message}\n"
        elif message_type == "progress":
            formatted_message = f"[{timestamp}] {message}\n"
        elif message_type == "success":
            formatted_message = f"[{timestamp}] {message}\n"
        elif message_type == "error":
            formatted_message = f"[{timestamp}] {message}\n"
        elif message_type == "warning":
            formatted_message = f"[{timestamp}] {message}\n"
        elif message_type == "system":
            formatted_message = f"[{timestamp}] {message}\n"
        else:
            formatted_message = f"[{timestamp}] {message}\n"
        
        # Thread-safe UI update using Invoke if needed
        try:
            if self.chat_display.InvokeRequired:
                self.chat_display.Invoke(lambda: self._append_to_chat_direct(formatted_message))
            else:
                self._append_to_chat_direct(formatted_message)
        except:
            # Fallback for direct update
            self._append_to_chat_direct(formatted_message)
    
    def _append_to_chat_direct(self, formatted_message):
        """Directly append message to chat display."""
        self.chat_display.Text += formatted_message
        
        # Auto-scroll to bottom
        self.chat_display.CaretIndex = len(self.chat_display.Text)


class AuraRhinoPanel(Rhino.UI.Panels.Panel):
    """
    Aura V32 Rhino Panel - Native Rhino Plugin Panel
    
    This is the main panel that gets registered with Rhino's panel system.
    It hosts the AuraAiChatPanel as its content.
    """
    
    def __init__(self):
        super(AuraRhinoPanel, self).__init__(System.Guid("12345678-1234-1234-1234-123456789ABC"))
        
        # Create the main chat panel
        self.chat_panel = AuraAiChatPanel()
        
        print("🔮 Aura V32 Rhino Panel initialized")
    
    @property 
    def Icon(self):
        """Panel icon."""
        # Return a small icon for the panel tab
        return None
    
    @property
    def PanelTitle(self):
        """Panel title displayed in Rhino."""
        return "Aura V32 AI"
    
    @property
    def PanelContent(self):
        """Panel content - returns our Eto chat panel."""
        return self.chat_panel


def show_aura_panel():
    """
    Show the Aura V32 AI Chat panel in Rhino.
    This function should be called from a Rhino command.
    """
    panel_id = System.Guid("12345678-1234-1234-1234-123456789ABC")
    
    # Check if panel is already open
    if Rhino.UI.Panels.IsPanelVisible(panel_id):
        print("Aura V32 panel is already open")
        return True
    
    # Open the panel
    success = Rhino.UI.Panels.OpenPanel(panel_id)
    
    if success:
        print("✅ Aura V32 AI Chat panel opened successfully")
    else:
        print("❌ Failed to open Aura V32 panel")
    
    return success


# Panel registration for Rhino plugin system
def register_panel():
    """Register the Aura V32 panel with Rhino."""
    panel_id = System.Guid("12345678-1234-1234-1234-123456789ABC")
    
    # Register the panel type
    Rhino.UI.Panels.RegisterPanel(
        Rhino.PlugIns.PlugIn.IdFromName("Aura"),  # Plugin ID (needs to match plugin)
        type(AuraRhinoPanel),                      # Panel class
        "Aura V32 AI",                            # Panel caption
        None                                       # Panel icon
    )
    
    print("✅ Aura V32 panel registered with Rhino")


def unregister_panel():
    """Unregister the Aura V32 panel from Rhino."""
    panel_id = System.Guid("12345678-1234-1234-1234-123456789ABC")
    
    # Close panel if open
    if Rhino.UI.Panels.IsPanelVisible(panel_id):
        Rhino.UI.Panels.ClosePanel(panel_id)
    
    print("✅ Aura V32 panel unregistered")


# Test function for development
def test_ui():
    """Test function to show the panel."""
    show_aura_panel()


if __name__ == "__main__":
    # Development test
    test_ui()